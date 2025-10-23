import json
import os
from src.services.telegram_service import TelegramService


def run(args):
    
    # Leer configuración guardada igual que login.py
    if not os.path.exists("config.json"):
        print("❌ Configuración no encontrada. Ejecuta primero 'telelinker setup'.")
        return
    with open("config.json", "r") as f:
        cfg = json.load(f)
    api_id = cfg["API_ID"]
    api_hash = cfg["API_HASH"]
    session_name = cfg["SESSION_NAME"]
    
    session_file = f"{session_name}.session"
    if not os.path.exists(session_file):
        print(f"❌ Sesión no encontrada. Ejecuta primero 'telelinker login' para autenticarte.")
        return
    
    client = TelegramService(session_name, api_id, api_hash)
    
    grupos = []
    

    export_file = getattr(args, "out", None) or getattr(args, "save", None)
    export_format = getattr(args, "format", "csv")
    if export_file:
        for dialog in client.iter_user_dialogs():
            if dialog.is_group:
                grupos.append({"id": dialog.id, "name": dialog.name})
        client.disconnect()
        if export_format == "json":
            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(grupos, f, ensure_ascii=False, indent=2)
        else:
            with open(export_file, "w", encoding="utf-8") as f:
                for grupo in grupos:
                    f.write(f"{grupo['id']},{grupo['name']}\n")
        print(f"📋 Exportados {len(grupos)} grupos a {export_file} en formato {export_format}")
    else:
        for dialog in client.iter_user_dialogs():
            if dialog.is_group:
                grupos.append({"id": dialog.id, "name": dialog.name})
        client.disconnect()
        print("Grupos y subgrupos donde eres miembro:")
        print("{:<20} {:<40}".format("ID", "Nombre"))
        print("-"*60)
        for grupo in grupos:
            print("{:<20} {:<40}".format(str(grupo["id"]), grupo["name"]))
        print(f"📋 Found {len(grupos)} groups.")