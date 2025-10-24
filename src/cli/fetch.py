
import csv
import json
import os
import re
from src.services.telegram_service import TelegramService
from src.scrapers import SCRAPERS


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


def load_config():
    """Carga la configuración desde el archivo de configuración del usuario."""
    config_dir = os.path.join(os.path.expanduser("~"), ".telelinker")
    config_path = os.path.join(config_dir, "config.json")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"❌ Config file not found. Run 'telelinker setup' first. Esperado en: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    
    return cfg, config_dir


def validate_session(config_dir, session_name):
    """Valida que el archivo de sesión exista."""
    session_file = os.path.join(config_dir, f"{session_name}.session")
    
    if not os.path.exists(session_file):
        raise FileNotFoundError(f"❌ Session not found. Run 'telelinker login' to authenticate. Esperado en: {session_file}")
    
    return session_file


def load_groups_from_args(args):
    """Carga la lista de grupos desde los argumentos o archivo."""
    groups = []
    
    if getattr(args, "groups_file", None):
        with open(args.groups_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split(",")
                    group_id = parts[0].strip()
                    groups.append(group_id)
    else:
        groups = [args.group]
    
    return groups


def get_output_file(args, formato):
    """Determina el archivo de salida basado en los argumentos y formato."""
    out_file = getattr(args, "out", None)
    
    if not out_file:
        out_file = os.path.abspath("posts.csv" if formato == "csv" else "posts.sql")
    else:
        if not os.path.isabs(out_file):
            out_file = os.path.abspath(out_file)
    
    return out_file


def process_message_urls(msg, limit, enlace_count):
    """Procesa las URLs encontradas en un mensaje de Telegram."""
    if not msg.message:
        return [], enlace_count
    
    urls = re.findall(r'(https?://[^\s]+)', msg.message)
    processed_data = []
    
    for url in urls:
        if limit is not None and enlace_count >= int(limit):
            break
            
        plataforma, fn = pick_scraper(url)
        if not fn:
            continue
            
        datos = fn(url)
        datos['url'] = url
        datos['plataforma'] = plataforma
        
        if all(datos.get(k) is not None for k in ('autor_contenido', 'likes', 'comentarios', 'fecha_publicacion')):
            processed_data.append(datos)
            enlace_count += 1
    
    return processed_data, enlace_count


def format_data_for_csv(datos):
    """Formatea los datos para exportación CSV."""
    return {
        'url': datos.get('url'),
        'platform': datos.get('plataforma'),
        'content_type': datos.get('tipo_contenido'),
        'author': datos.get('autor_contenido'),
        'date': datos.get('fecha_publicacion'),
        'likes': datos.get('likes'),
        'comments': datos.get('comentarios'),
        'shared': datos.get('compartidos', None),
        'visit': datos.get('visitas', None)
    }


def sql_str(val):
    """Convierte un valor a formato SQL string."""
    if val is None:
        return "NULL"
    if isinstance(val, str):
        return "'{}'".format(val.replace("'", "''"))
    return str(val)


def format_data_for_sql(datos, table_name):
    """Formatea los datos para exportación SQL."""
    values = [
        sql_str(datos.get('url')),
        sql_str(datos.get('plataforma')),
        sql_str(datos.get('tipo_contenido')),
        sql_str(datos.get('autor_contenido')),
        sql_str(datos.get('fecha_publicacion')),
        sql_str(datos.get('likes')),
        sql_str(datos.get('comentarios')),
        sql_str(datos.get('compartidos')),
        sql_str(datos.get('visitas'))
    ]
    return f"INSERT INTO {table_name} (url, platform, content_type, author, date, likes, comments, shared, visit) VALUES ({', '.join(values)});\n"


def export_to_csv(groups, tg_service, limit, out_file):
    """Exporta los datos a formato CSV."""
    total_posts = 0
    enlace_count = 0
    
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        
        for group in groups:
            print_fetch_message(group, limit)
            
            for msg in tg_service.iter_group_messages(int(group)):
                processed_data, enlace_count = process_message_urls(msg, limit, enlace_count)
                
                for datos in processed_data:
                    row = format_data_for_csv(datos)
                    writer.writerow(row)
                    total_posts += 1
                    print_progress(total_posts)
    
    return total_posts


def export_to_postgresql(groups, tg_service, limit, out_file):
    """Exporta los datos a formato PostgreSQL."""
    create_table_stmt = (
        "CREATE TABLE posts (\n"
        "    id SERIAL PRIMARY KEY,\n"
        "    url TEXT NOT NULL,\n"
        "    platform VARCHAR(50) NOT NULL,\n"
        "    content_type VARCHAR(50),\n"
        "    author VARCHAR(100),\n"
        "    date TIMESTAMP,\n"
        "    likes INT,\n"
        "    comments INT,\n"
        "    shared INT,\n"
        "    visit INT\n"
        ");\n\n"
    )
    
    total_posts = 0
    file_exists = os.path.exists(out_file)
    table_name = "posts"
    
    with open(out_file, "w" if not file_exists else "a", encoding="utf-8") as f:
        if not file_exists:
            f.write(create_table_stmt)
        
        for group in groups:
            print_fetch_message(group, limit)
            enlace_count = 0
            
            for msg in tg_service.iter_group_messages(int(group)):
                processed_data, enlace_count = process_message_urls(msg, limit, enlace_count)
                
                for datos in processed_data:
                    sql_statement = format_data_for_sql(datos, table_name)
                    f.write(sql_statement)
                    total_posts += 1
                    print_progress(total_posts)
    
    return total_posts


def print_fetch_message(group, limit):
    """Imprime el mensaje de inicio de fetch para un grupo."""
    if limit is not None:
        print(f"📡 Fetching up to {limit} posts from group {group}...")
    else:
        print(f"📡 Fetching all posts from group {group}...")


def print_progress(total_posts):
    """Imprime el progreso de la operación."""
    print(f"\r[{'=' * (total_posts % 10)}{' ' * (10 - (total_posts % 10))}] Insertando... {total_posts}", end='')


def run(args):
    """Función principal que ejecuta el comando fetch."""
    try:
        # Cargar configuración
        cfg, config_dir = load_config()
        api_id = cfg["API_ID"]
        api_hash = cfg["API_HASH"]
        session_name = cfg["SESSION_NAME"]
        
        # Validar sesión
        session_file = validate_session(config_dir, session_name)
        
        # Procesar argumentos
        limit = getattr(args, "limit", None)
        formato = args.format
        groups = load_groups_from_args(args)
        out_file = get_output_file(args, formato)
        
        # Inicializar servicio de Telegram
        tg_service = TelegramService(session_file, api_id, api_hash)
        
        try:
            # Exportar según el formato
            if formato == "csv":
                total_posts = export_to_csv(groups, tg_service, limit, out_file)
                print(f"\n✅ Export complete: {total_posts} posts saved to {out_file}")
            elif formato == "postgresql":
                total_posts = export_to_postgresql(groups, tg_service, limit, out_file)
                print(f"\n✅ Export complete: {total_posts} posts saved to {out_file} (PostgreSQL)")
            else:
                print("Format not supported.")
        finally:
            tg_service.disconnect()
            
    except FileNotFoundError as e:
        print(str(e))
    except Exception as e:
        print(f"❌ Error: {str(e)}")