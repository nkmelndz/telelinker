import json
import os
from src.services.telegram_service import TelegramService


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
    
    client = TelegramService(session_file, api_id, api_hash)
    
    grupos = []
    

    exports_dir = os.path.join(config_dir, "exports")
    os.makedirs(exports_dir, exist_ok=True)
    export_file = getattr(args, "out", None)
    if not export_file:
        export_file = os.path.join(exports_dir, "groups.csv" if export_format=="csv" else "groups.json")
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
        print(f"📋 Exported {len(grupos)} groups to {export_file} as {export_format}")
    else:
        for dialog in client.iter_user_dialogs():
            if dialog.is_group:
                grupos.append({"id": dialog.id, "name": dialog.name})
        client.disconnect()
        print("Groups and subgroups you are a member of:")
        print("{:<20} {:<40}".format("ID", "Name"))
        print("-"*60)
        for grupo in grupos:
            print("{:<20} {:<40}".format(str(grupo["id"]), grupo["name"]))
        print(f"📋 Found {len(grupos)} groups.")