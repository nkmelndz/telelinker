def run(args):
    api_id = input("Enter your Telegram API ID: ")
    api_hash = input("Enter your Telegram API HASH: ")
    # Guardar configuración (ejemplo simple)
    with open("config.json", "w") as f:
        import json
        json.dump({"API_ID": api_id, "API_HASH": api_hash}, f)
    print("✅ Configuration saved!")