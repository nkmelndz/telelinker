"""
Módulo para manejo de configuración común.
"""
import json
import os


def load_config():
    """Carga la configuración desde el archivo de configuración del usuario."""
    config_dir = os.path.join(os.path.expanduser("~"), ".telelinker")
    config_path = os.path.join(config_dir, "config.json")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"❌ Config file not found. Run 'telelinker setup' first. Esperado en: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    
    return cfg, config_dir


def get_config_values(cfg):
    """Extrae los valores principales de configuración."""
    return {
        'api_id': cfg["API_ID"],
        'api_hash': cfg["API_HASH"],
        'session_name': cfg["SESSION_NAME"]
    }