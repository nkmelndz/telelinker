def run(args):
    import os
    import json
    api_id = input("Enter your Telegram API ID: ")
    api_hash = input("Enter your Telegram API HASH: ")
    # Definir ruta segura en la carpeta del usuario
    config_dir = os.path.join(os.path.expanduser("~"), ".telelinker")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "config.json")
    # Guardar configuración
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump({"API_ID": api_id, "API_HASH": api_hash, "SESSION_NAME": "telelinker"}, f, indent=2)
    print(f"✅ Configuration saved at {config_path}!")