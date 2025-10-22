
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
    group = args.group
    limit = args.limit
    formato = args.format

    print(f"📡 Fetching {limit} posts from group {group}...")

    # Leer configuración guardada igual que login.py
    if not os.path.exists("config.json"):
        print("❌ Configuración no encontrada. Ejecuta primero 'social-scraper setup'.")
        return
    with open("config.json", "r") as f:
        cfg = json.load(f)
    api_id = cfg["API_ID"]
    api_hash = cfg["API_HASH"]
    session_name = cfg.get("SESSION_NAME", "telelinker")

    session_file = f"{session_name}.session"
    if not os.path.exists(session_file):
        print(f"❌ Sesión no encontrada. Ejecuta primero 'social-scraper login' para autenticarte.")
        return

    tg_service = TelegramService(session_name, api_id, api_hash)

    posts = []
    for i, msg in enumerate(tg_service.iter_group_messages(int(group))):
        if i >= int(limit):
            break
        
        if not msg.message:
            continue
        urls = re.findall(r'(https?://[^\s]+)', msg.message)
        
        for url in urls:
            plataforma, fn = pick_scraper(url)
            if not fn:
                continue
            datos = fn(url)
            datos['url'] = url
            datos['plataforma'] = plataforma
            # validar campos obligatorios antes de persistir
            if all(datos.get(k) is not None for k in ('autor_contenido','likes','comentarios','fecha_publicacion')):
                posts.append({'autor_contenido': datos['autor_contenido'],
                    'likes': datos['likes'],
                    'comentarios': datos['comentarios'],
                    'compartidos': datos.get('compartidos', None),
                    'visitas': datos.get('visitas', None),
                    'fecha_publicacion': datos['fecha_publicacion'],
                    'tipo_contenido': datos.get('tipo_contenido', None)
                })
                print(f"\nEnlace insertado: {datos['url']} ({datos['plataforma']})")
        
    tg_service.disconnect()

    if formato == "csv":
        out_file = f"{group}_posts.csv"
        with open(out_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["group_id", "post_id", "content"])
            writer.writeheader()
            writer.writerows(posts)
        print(f"✅ Export complete: {len(posts)} posts saved to {out_file}")
    else:
        print("Formato no soportado.")