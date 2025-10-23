import os
import json

def run(args):
    config_dir = os.path.join(os.path.expanduser("~"), ".telelinker")
    config_path = os.path.join(config_dir, "config.json")
    if not os.path.exists(config_path):
        print(f"No se encontró el archivo de configuración en {config_path}")
        return
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    session_name = cfg.get("SESSION_NAME")
    if not session_name:
        print("No se encontró SESSION_NAME en la configuración.")
        return
    session_path = os.path.join(config_dir, f"{session_name}.session")
    # Intentar desconectar explícitamente la sesión de Telethon
    try:
        from src.services.telegram_service import TelegramService
        # Usar valores dummy para api_id y api_hash, solo para desconectar
        # No se realiza ninguna operación, solo desconexión si existe
        api_id = cfg.get("API_ID", 1)
        api_hash = cfg.get("API_HASH", "dummy")
        tg_service = TelegramService(session_path, api_id, api_hash, connect_only=True)
        tg_service.disconnect()
    except Exception as e:
        print(f"Advertencia: no se pudo desconectar explícitamente la sesión: {e}")
    if os.path.exists(session_path):
        try:
            os.remove(session_path)
            print(f"Sesión de Telegram eliminada: {session_path}")
        except Exception as e:
            print(f"Error eliminando la sesión: {e}")
    else:
        print("No existe ningún archivo de sesión para eliminar.")