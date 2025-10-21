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


if __name__ == '__main__':
    run()


