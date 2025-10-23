
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

def pick_scraper(url: str):
    for domain, platform in DOMAIN_TO_PLATFORM.items():
        if domain in url:
            fn = SCRAPERS.get(platform)
            if fn:
                return platform, fn
    return None, None

def run(args):
    
    # Leer configuración desde la carpeta del usuario
    config_dir = os.path.join(os.path.expanduser("~"), ".telelinker")
    config_path = os.path.join(config_dir, "config.json")
    if not os.path.exists(config_path):
        print(f"❌ Config file not found. Run 'telelinker setup' first. Esperado en: {config_path}")
        return
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    api_id = cfg["API_ID"]
    api_hash = cfg["API_HASH"]
    session_name = cfg["SESSION_NAME"]

    session_file = os.path.join(config_dir, f"{session_name}.session")
    if not os.path.exists(session_file):
        print(f"❌ Session not found. Run 'telelinker login' to authenticate. Esperado en: {session_file}")
        return
    
    limit = getattr(args, "limit", None)
    formato = args.format
    groups = []
    if getattr(args, "groups_file", None):
        # Read groups from file
        with open(args.groups_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Allow format: id,name
                    parts = line.split(",")
                    group_id = parts[0].strip()
                    groups.append(group_id)
    else:
        groups = [args.group]

    try:
        tg_service = TelegramService(session_file, api_id, api_hash)
    except SilentException:
        print("⚠️  Error temporal de sesión de Telegram. Intenta reiniciar sesión si el problema persiste.")
        return

    out_file = getattr(args, "out", None)
    if not out_file:
        out_file = os.path.abspath("posts.csv" if formato=="csv" else "posts.sql")
    else:
        if not os.path.isabs(out_file):
            out_file = os.path.abspath(out_file)
    fieldnames = [
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
    total_posts = 0
    enlace_count = 0

    if formato == "csv":
        with open(out_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for group in groups:
                if limit is not None:
                    print(f"📡 Fetching up to {limit} posts from group {group}...")
                else:
                    print(f"📡 Fetching all posts from group {group}...")
                for msg in tg_service.iter_group_messages(int(group)):
                    if not msg.message:
                        continue
                    urls = re.findall(r'(https?://[^\s]+)', msg.message)
                    for url in urls:
                        if limit is not None and enlace_count >= int(limit):
                            break
                        plataforma, fn = pick_scraper(url)
                        if not fn:
                            continue
                        datos = fn(url)
                        datos['url'] = url
                        datos['plataforma'] = plataforma
                        if all(datos.get(k) is not None for k in ('autor_contenido','likes','comentarios','fecha_publicacion')):
                            row = {
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
                            writer.writerow(row)
                            total_posts += 1
                            enlace_count += 1
                            print(f"\r[{'=' * (total_posts % 10)}{' ' * (10 - (total_posts % 10))}] Insertando... {total_posts}", end='')
        tg_service.disconnect()
        print(f"\n✅ Export complete: {total_posts} posts saved to {out_file}")
    elif formato == "postgresql":
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
        file_exists = os.path.exists(out_file)
        with open(out_file, "w" if not file_exists else "a", encoding="utf-8") as f:
            if not file_exists:
                f.write(create_table_stmt)
            table_name = "posts"
            for group in groups:
                if limit is not None:
                    print(f"📡 Fetching up to {limit} posts from group {group}...")
                else:
                    print(f"📡 Fetching all posts from group {group}...")
                enlace_count = 0
                for msg in tg_service.iter_group_messages(int(group)):
                    if not msg.message:
                        continue
                    urls = re.findall(r'(https?://[^\s]+)', msg.message)
                    for url in urls:
                        if limit is not None and enlace_count >= int(limit):
                            break
                        plataforma, fn = pick_scraper(url)
                        if not fn:
                            continue
                        datos = fn(url)
                        datos['url'] = url
                        datos['plataforma'] = plataforma
                        if all(datos.get(k) is not None for k in ('autor_contenido','likes','comentarios','fecha_publicacion')):
                            # Mapear los datos al formato de la tabla
                            def sql_str(val):
                                if val is None:
                                    return "NULL"
                                if isinstance(val, str):
                                    return "'{}'".format(val.replace("'", "''"))
                                return str(val)

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
                            f.write(f"INSERT INTO {table_name} (url, platform, content_type, author, date, likes, comments, shared, visit) VALUES ({', '.join(values)});\n")
                            total_posts += 1
                            enlace_count += 1
                            print(f"\r[{'=' * (total_posts % 10)}{' ' * (10 - (total_posts % 10))}] Insertando... {total_posts}", end='')
        tg_service.disconnect()
        print(f"\n ✅ Export complete: {total_posts} posts saved to {out_file} (PostgreSQL)")
    else:
        tg_service.disconnect()
        print("Format not supported.")