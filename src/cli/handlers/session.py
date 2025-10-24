"""
Módulo para manejo y validación de sesiones de Telegram.
"""
import os


def validate_session(config_dir, session_name):
    """Valida que el archivo de sesión exista."""
    session_file = os.path.join(config_dir, f"{session_name}.session")
    
    if not os.path.exists(session_file):
        raise FileNotFoundError(f"❌ Session not found. Run 'telelinker login' to authenticate. Esperado en: {session_file}")
    
    return session_file


def get_session_path(config_dir, session_name):
    """Obtiene la ruta del archivo de sesión."""
    return os.path.join(config_dir, f"{session_name}.session")