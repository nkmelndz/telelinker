import json
import os
from src.services.telegram_service import TelegramService


def load_config():
    """Carga la configuración desde el archivo de configuración del usuario."""
    config_dir = os.path.join(os.path.expanduser("~"), ".telelinker")
    config_path = os.path.join(config_dir, "config.json")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"❌ Config file not found. Run 'telelinker setup' first. Esperado en: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    
    return cfg, config_dir


def validate_session(config_dir, session_name):
    """Valida que el archivo de sesión exista."""
    session_file = os.path.join(config_dir, f"{session_name}.session")
    
    if not os.path.exists(session_file):
        raise FileNotFoundError(f"❌ Session not found. Run 'telelinker login' to authenticate. Esperado en: {session_file}")
    
    return session_file


def get_output_file(args):
    """Determina el archivo de salida basado en los argumentos."""
    export_file = getattr(args, "out", None)
    export_format = getattr(args, "format", "csv")
    
    if not export_file:
        export_file = os.path.abspath("groups.csv" if export_format == "csv" else "groups.json")
    else:
        if not os.path.isabs(export_file):
            export_file = os.path.abspath(export_file)
    
    return export_file, export_format


def collect_groups(client):
    """Recolecta todos los grupos del usuario."""
    grupos = []
    
    for dialog in client.iter_user_dialogs():
        if dialog.is_group:
            grupos.append({"id": dialog.id, "name": dialog.name})
    
    return grupos


def export_groups_to_json(grupos, export_file):
    """Exporta los grupos a formato JSON."""
    with open(export_file, "w", encoding="utf-8") as f:
        json.dump(grupos, f, ensure_ascii=False, indent=2)


def export_groups_to_csv(grupos, export_file):
    """Exporta los grupos a formato CSV."""
    with open(export_file, "w", encoding="utf-8") as f:
        for grupo in grupos:
            f.write(f"{grupo['id']},{grupo['name']}\n")


def print_groups_table(grupos):
    """Imprime los grupos en formato tabla."""
    print("Groups and subgroups you are a member of:")
    print("{:<20} {:<40}".format("ID", "Name"))
    print("-" * 60)
    
    for grupo in grupos:
        print("{:<20} {:<40}".format(str(grupo["id"]), grupo["name"]))
    
    print(f"📋 Found {len(grupos)} groups.")


def export_groups(grupos, export_file, export_format):
    """Exporta los grupos según el formato especificado."""
    if export_format == "json":
        export_groups_to_json(grupos, export_file)
    else:
        export_groups_to_csv(grupos, export_file)
    
    print(f"📋 Exported {len(grupos)} groups to {export_file} as {export_format}")


def run(args):
    """Función principal que ejecuta el comando groups."""
    try:
        # Cargar configuración
        cfg, config_dir = load_config()
        api_id = cfg["API_ID"]
        api_hash = cfg["API_HASH"]
        session_name = cfg["SESSION_NAME"]
        
        # Validar sesión
        session_file = validate_session(config_dir, session_name)
        
        # Procesar argumentos
        export_file, export_format = get_output_file(args)
        
        # Inicializar servicio de Telegram
        client = TelegramService(session_file, api_id, api_hash)
        
        try:
            # Recolectar grupos
            grupos = collect_groups(client)
            
            # Exportar o mostrar grupos
            if getattr(args, "out", None) or export_format != "csv":
                export_groups(grupos, export_file, export_format)
            else:
                print_groups_table(grupos)
                
        finally:
            client.disconnect()
            
    except FileNotFoundError as e:
        print(str(e))
    except Exception as e:
        print(f"❌ Error: {str(e)}")