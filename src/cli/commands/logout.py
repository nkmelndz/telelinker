import os
import json
from ..handlers.config import load_config, get_config_values

def run(args):
    
    # Cargar configuración y reutilizar utilidades compartidas
    cfg, config_dir = load_config()
    values = get_config_values(cfg)
    api_id = values['api_id']
    api_hash = values['api_hash']
    session_name = values['session_name']

    # Construir la ruta del archivo de sesión
    session_path = os.path.join(config_dir, f"{session_name}.session")

    # Si no existe sesión, mostrar error y salir sin pedir login
    if not os.path.exists(session_path):
        print("❌ No hay sesión activa. Ejecuta 'telelinker login' primero.")
        return

    # Intentar desconectar explícitamente la sesión de Telethon
    try:
        from src.services.telegram_service import TelegramService
        # Instanciar el servicio con los valores reales (constructor de 3 parámetros)
        tg_service = TelegramService(session_path, api_id, api_hash)
        tg_service.disconnect()
    except Exception as e:
        print(f"Advertencia: no se pudo desconectar explícitamente la sesión: {e}")

    # Eliminar el archivo de sesión
    try:
        os.remove(session_path)
        print(f"Sesión de Telegram eliminada: {session_path}")
    except Exception as e:
        print(f"Error eliminando la sesión: {e}")