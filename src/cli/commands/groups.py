from src.services.telegram_service import TelegramService
from ..handlers.config import load_config, get_config_values
from ..handlers.session import validate_session
from ..handlers.output import get_groups_output_file
from ..formatters.csv_formatter import export_groups_to_csv
from ..formatters.json_formatter import export_groups_to_json
import os
from InquirerPy import inquirer



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
        
        # Inicializar servicio de Telegram y asegurar que está iniciado
        client = TelegramService(session_file, config_values['api_id'], config_values['api_hash'])
        success = client.start()
        
        if not success:
            print("❌ Authentication failed. Please run 'telelinker login' first.")
            return
        
        try:
            # Recolectar grupos
            grupos = collect_groups(client)
            
            # Exportar o mostrar grupos
            if getattr(args, "interactive", None):
                # Modo interactivo con InquirerPy
                choices = [{"name": f"{g['name']} ({g['id']})", "value": g} for g in grupos]
                # Selección con reintento si no se elige ningún grupo
                while True:
                    selected = inquirer.checkbox(
                        message="Select groups (space to mark, enter to confirm)",
                        choices=choices,
                        instruction="↑/↓ navigate, space to select"
                    ).execute()
                    if selected:
                        break
                    print("⚠ You must select at least one group.")

                fmt = inquirer.select(
                    message="Formato de salida",
                    choices=["csv", "json"],
                    default="csv"
                ).execute()

                default_out = os.path.abspath(f"groups.{fmt}")
                out_input = inquirer.text(
                    message="Nombre del archivo de exportación",
                    default=default_out
                ).execute()

                out_file = os.path.abspath(out_input.strip()) if out_input else default_out
                ext = ".csv" if fmt == "csv" else ".json"
                if not out_file.lower().endswith(ext):
                    out_file += ext

                export_groups(selected, out_file, fmt)
            else:
                # Si el usuario especifica --format o --out, exportar; si no, mostrar tabla
                if getattr(args, "out", None) or getattr(args, "format", None):
                    export_groups(grupos, export_file, export_format)
                else:
                    print_groups_table(grupos)
                
        finally:
            client.disconnect()
            
    except FileNotFoundError as e:
        print(str(e))
    except Exception as e:
        print(f"❌ Error: {str(e)}")