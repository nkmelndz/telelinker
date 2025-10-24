from src.services.telegram_service import TelegramService
from ..handlers.config import load_config, get_config_values
from ..handlers.session import validate_session
from ..handlers.output import get_groups_output_file
from ..formatters.csv_formatter import export_groups_to_csv
from ..formatters.json_formatter import export_groups_to_json


def collect_groups(client):
    """Recolecta todos los grupos del usuario."""
    grupos = []
    
    for dialog in client.iter_user_dialogs():
        if dialog.is_group:
            grupos.append({"id": dialog.id, "name": dialog.name})
    
    return grupos


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
        config_values = get_config_values(cfg)
        
        # Validar sesión
        session_file = validate_session(config_dir, config_values['session_name'])
        
        # Procesar argumentos
        export_file, export_format = get_groups_output_file(args)
        
        # Inicializar servicio de Telegram
        client = TelegramService(session_file, config_values['api_id'], config_values['api_hash'])
        
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