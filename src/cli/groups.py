import json
import os
from src.services.telegram_service import TelegramService


def run(args):
    
    # Leer configuración guardada igual que login.py
    if not os.path.exists("config.json"):
        print("❌ Configuración no encontrada. Ejecuta primero 'social-scraper setup'.")
        return
    with open("config.json", "r") as f:
        cfg = json.load(f)
    api_id = cfg["API_ID"]
    api_hash = cfg["API_HASH"]
    session_name = cfg.get("SESSION_NAME", "telelinker")
    
    client = TelegramService(session_name, api_id, api_hash)
    
    grupos = []
    
    client.start()

    print("Grupos y subgrupos donde eres miembro:")
    for dialog in client.iter_dialogs():
        if dialog.is_group:
            grupos.append({"id": dialog.id, "name": dialog.name})
            print(f"Nombre: {dialog.name} | ID: {dialog.id}")

    client.disconnect()
    
    print(f"📋 Found {len(grupos)} groups.")
    if hasattr(args, "save") and args.save:
        with open(args.save, "w") as f:
            for grupo in grupos:
                f.write(f"{grupo['id']},{grupo['name']}\n")
        print(f"Saved to {args.save}")