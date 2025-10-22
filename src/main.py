import re
from src.services.telegram_service import TelegramService
from src.scrapers import SCRAPERS
from src.config import get_config
from src.db import DB

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

def run():
    cfg = get_config()
    db = DB(cfg)
    tg_service = TelegramService(cfg.SESSION_NAME, cfg.API_ID, cfg.API_HASH)

    for msg in tg_service.iter_group_messages(cfg.GROUP_USERNAME):
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
                db.insert_enlace(datos)
                print(f"\nEnlace insertado: {datos['url']} ({datos['plataforma']})")
    
    tg_service.disconnect()

import argparse

def main():
    parser = argparse.ArgumentParser(prog="social-scraper")
    subparsers = parser.add_subparsers(dest="command")

    # setup
    subparsers.add_parser("setup")

    # login
    subparsers.add_parser("login")

    # groups
    groups_parser = subparsers.add_parser("groups")
    groups_parser.add_argument("--save", type=str, help="Archivo donde guardar los grupos")

    # fetch
    fetch_parser = subparsers.add_parser("fetch")
    fetch_parser.add_argument("--groups-file", type=str, required=False, help="Archivo con los grupos")
    fetch_parser.add_argument("--group", type=str, required=True, help="ID o username del grupo")
    fetch_parser.add_argument("--format", type=str, choices=["csv"], default="csv", help="Formato de exportación")
    fetch_parser.add_argument("--limit", type=str, required=True, help="Numero máximo de posts a fetch")
    fetch_parser.add_argument("--out", type=str, required=False, help="Archivo de salida")

    args = parser.parse_args()

    if args.command == "setup":
        from cli import setup
        setup.run(args)
    elif args.command == "login":
        from cli import login
        login.run(args)
    elif args.command == "groups":
        from cli import groups
        groups.run(args)
    elif args.command == "fetch":
        from cli import fetch
        fetch.run(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()


