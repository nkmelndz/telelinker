import csv
import json
import os
import re
from src.services.telegram_service import TelegramService
from src.scrapers import SCRAPERS
from ..handlers.config import load_config, get_config_values
from ..handlers.session import validate_session
from ..handlers.output import get_fetch_output_file
from ..formatters.csv_formatter import export_posts_to_csv, format_data_for_csv
from ..formatters.sql_formatter import export_posts_to_postgresql, format_data_for_sql, generate_sql_file


DOMAIN_TO_PLATFORM = {
    'linkedin.com': 'LinkedIn',
    'dev.to': 'Dev.to',
    'youtube.com': 'YouTube',
    'youtu.be': 'YouTube',
    'medium.com': 'Medium',
    'instagram.com': 'Instagram',
    'tiktok.com': 'TikTok',
}

FIELDNAMES = [
    "url",
    "platform",
    "content_type",
    "author",
    "date",
    "likes",
    "comments",
    "shared",
    "visit"
]


def pick_scraper(url: str):
    """Selecciona el scraper apropiado basado en la URL."""
    for domain, platform in DOMAIN_TO_PLATFORM.items():
        if domain in url:
            fn = SCRAPERS.get(platform)
            if fn:
                return platform, fn
    return None, None


def load_groups_from_args(args):
    """Carga los grupos desde los argumentos (archivo o grupo individual)."""
    groups = []
    
    if hasattr(args, 'groups_file') and args.groups_file:
        # Cargar desde archivo
        if not os.path.exists(args.groups_file):
            raise FileNotFoundError(f"❌ Groups file not found: {args.groups_file}")
        
        with open(args.groups_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split(",")
                    if len(parts) >= 2:
                        groups.append({"id": int(parts[0]), "name": parts[1]})
    
    elif hasattr(args, 'group') and args.group:
        # Grupo individual
        groups.append({"id": args.group, "name": args.group})
    
    return groups


def process_message_urls(msg, limit, enlace_count):
    """Procesa las URLs encontradas en un mensaje."""
    urls = re.findall(r'https?://[^\s]+', msg.message)
    processed_urls = []
    
    for url in urls:
        if enlace_count[0] >= limit:
            break
            
        platform, scraper_fn = pick_scraper(url)
        if platform and scraper_fn:
            try:
                datos = scraper_fn(url)
                if datos:
                    processed_urls.append({
                        'url': url,
                        'platform': platform,
                        'data': datos
                    })
                    enlace_count[0] += 1
            except Exception as e:
                print(f"⚠️  Error scraping {url}: {str(e)}")
    
    return processed_urls


def export_to_csv(groups, tg_service, limit, out_file):
    """Exporta los datos a formato CSV."""
    posts = []
    enlace_count = [0]
    
    for group in groups:
        print_fetch_message(group, limit)
        
        for msg in tg_service.get_messages(group["id"], limit=limit):
            if enlace_count[0] >= limit:
                break
                
            processed_urls = process_message_urls(msg, limit, enlace_count)
            
            for url_data in processed_urls:
                post_data = {
                    'group_id': group["id"],
                    'group_name': group["name"],
                    'message_id': msg.id,
                    'date': msg.date.strftime("%Y-%m-%d %H:%M:%S"),
                    'message': msg.message,
                    'urls': url_data['url']
                }
                posts.append(post_data)
        
        print_progress(enlace_count[0])
    
    export_posts_to_csv(posts, out_file)
    return enlace_count[0]


def export_to_postgresql(groups, tg_service, limit, out_file):
    """Exporta los datos a PostgreSQL o genera archivo SQL."""
    posts = []
    enlace_count = [0]
    
    for group in groups:
        print_fetch_message(group, limit)
        
        for msg in tg_service.get_messages(group["id"], limit=limit):
            if enlace_count[0] >= limit:
                break
                
            processed_urls = process_message_urls(msg, limit, enlace_count)
            
            for url_data in processed_urls:
                post_data = {
                    'group_id': group["id"],
                    'group_name': group["name"],
                    'message_id': msg.id,
                    'date': msg.date.strftime("%Y-%m-%d %H:%M:%S"),
                    'message': msg.message,
                    'urls': [url_data['url']]
                }
                posts.append(post_data)
        
        print_progress(enlace_count[0])
    
    # Generar archivo SQL
    generate_sql_file(posts, out_file)
    return enlace_count[0]


def print_fetch_message(group, limit):
    """Imprime mensaje de inicio de fetch para un grupo."""
    print(f"🔍 Fetching from group: {group['name']} (limit: {limit})")


def print_progress(total_posts):
    """Imprime el progreso actual."""
    print(f"📊 Processed {total_posts} posts so far...")


def run(args):
    """Función principal que ejecuta el comando fetch."""
    try:
        # Cargar configuración
        cfg, config_dir = load_config()
        config_values = get_config_values(cfg)
        
        # Validar sesión
        session_file = validate_session(config_dir, config_values['session_name'])
        
        # Cargar grupos
        groups = load_groups_from_args(args)
        if not groups:
            raise ValueError("❌ No groups specified. Use --group or --groups-file")
        
        # Procesar argumentos
        export_file, export_format = get_fetch_output_file(args)
        limit = int(getattr(args, "limit", 100))
        
        # Inicializar servicio de Telegram
        tg_service = TelegramService(session_file, config_values['api_id'], config_values['api_hash'])
        
        try:
            # Exportar según formato
            if export_format == "postgresql":
                total_posts = export_to_postgresql(groups, tg_service, limit, export_file)
                print(f"📋 Exported {total_posts} posts to {export_file} as SQL")
            else:
                total_posts = export_to_csv(groups, tg_service, limit, export_file)
                print(f"📋 Exported {total_posts} posts to {export_file} as CSV")
                
        finally:
            tg_service.disconnect()
            
    except FileNotFoundError as e:
        print(str(e))
    except Exception as e:
        print(f"❌ Error: {str(e)}")