import json
from src.services.telegram_service import TelegramService
def run(args):
    # Leer configuración guardada
    with open("config.json", "r") as f:
        cfg = json.load(f)
    api_id = cfg["API_ID"]
    api_hash = cfg["API_HASH"]
    session_name = cfg["SESSION_NAME"]
    
    # phone = input("Enter your phone number: ")
    # code = input("Enter code (sent via Telegram): ")
    
    # Usar los datos de configuración
    tg_service = TelegramService(session_name, api_id, api_hash)

    # print(f"Logging in with phone {phone} and code {code}...")
    print("✅ Logged in successfully!")