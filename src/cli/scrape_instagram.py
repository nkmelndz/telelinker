import csv
import os
import re
import json
from src.services.telegram_service import TelegramService
from src.scrapers.instagram import scrap

def run(args):
    # Leer configuracion desde la carpeta del usuario
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
    group = args.group
    out_file = args.out
    limit = args.limit if hasattr(args, 'limit') and args.limit else None
    client = TelegramService(session_file, api_id, api_hash)
    insta_url_pattern = re.compile(r"https?://(www\.)?instagram.com/p/[A-Za-z0-9_-]+/?")
    rows = []
    count = 0
    for msg in client.iter_group_messages(group):
        if limit and count >= limit:
            break
        if msg.message:
            urls = insta_url_pattern.findall(msg.message)
            for url in urls:
                meta = scrap(url)
                row = {
                    'url': url,
                    'author': meta.get('author'),
                    'date': meta.get('date'),
                    'likes': meta.get('likes'),
                    'comments': meta.get('comments'),
                    'shares': meta.get('shares'),
                    'views': meta.get('views'),
                    'caption': meta.get('caption'),
                }
                rows.append(row)
        count += 1
    client.disconnect()
    with open(out_file, "w", encoding="utf-8", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['url','author','date','likes','comments','shares','views','caption'])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"✅ Guardados {len(rows)} posts de Instagram en {out_file}")
