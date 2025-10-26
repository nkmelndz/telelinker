from src.services.telegram_service import TelegramService
from ..handlers.config import load_config, get_config_values

def run(args):
    import os
    # Cargar configuración y reutilizar utilidades compartidas
    cfg, config_dir = load_config()
    values = get_config_values(cfg)
    api_id = values['api_id']
    api_hash = values['api_hash']
    session_name = values['session_name']

    # Construir la ruta del archivo de sesión
    session_path = os.path.join(config_dir, f"{session_name}.session")

    if not os.path.exists(config_dir):
        print("❌ No hay configuracion activa. Ejecuta 'telelinker setup' primero.")
        return
    
    # Iniciar sesión usando TelegramService
    tg_service = TelegramService(session_path, api_id, api_hash)
    success = tg_service.start()
    
    if success:
        print("✅ Logged in successfully!")
    else:
        print("❌ Login failed. Please try again.")
        return