import os
from ..handlers.config import load_config, get_config_values
from ..handlers.session import validate_session


def run(args):
    # Cargar configuración y reutilizar utilidades compartidas
    cfg, config_dir = load_config()
    values = get_config_values(cfg)
    api_id = values['api_id']
    api_hash = values['api_hash']
    session_name = values['session_name']

    # Validar que la sesión exista usando el validador centralizado
    try:
        session_path = validate_session(config_dir, session_name)
    except FileNotFoundError as e:
        print(str(e))
        return

    # Intentar desconectar explícitamente la sesión de Telethon
    try:
        from src.services.telegram_service import TelegramService
        tg_service = TelegramService(session_path, api_id, api_hash)
        tg_service.disconnect()
    except Exception as e:
        print(f"Advertencia: no se pudo desconectar explícitamente la sesión: {e}")

    # Eliminar el archivo de sesión
    try:
        os.remove(session_path)
        print(f"Sesión de Telegram eliminada: {session_path}")
    except PermissionError:
        print(f"Error eliminando la sesión: el archivo está en uso por otro proceso: '{session_path}'")
    except Exception as e:
        print(f"Error eliminando la sesión: {e}")