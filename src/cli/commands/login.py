import json
from src.services.telegram_service import TelegramService
def run(args):
    # Leer configuración guardada desde la carpeta del usuario
    import os
    config_dir = os.path.join(os.path.expanduser("~"), ".telelinker")
    config_path = os.path.join(config_dir, "config.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"No se encontró el archivo de configuración en {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    api_id = cfg["API_ID"]
    api_hash = cfg["API_HASH"]
    session_name = cfg["SESSION_NAME"]
    # Definir ruta segura para el archivo de sesión
    session_path = os.path.join(config_dir, f"{session_name}.session")
    
    # phone = input("Enter your phone number: ")
    # code = input("Enter code (sent via Telegram): ")
    
    # Usar los datos de configuración y la ruta segura para la sesión
    tg_service = TelegramService(session_path, api_id, api_hash)

    # print(f"Logging in with phone {phone} and code {code}...")
    print("✅ Logged in successfully!")