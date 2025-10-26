"""
Módulo para manejo de archivos de salida.
"""
import os


def get_output_file(args, default_filename="output", default_format="csv"):
    """Determina el archivo de salida basado en los argumentos."""
    export_file = getattr(args, "out", None)
    # Si el argumento format no fue proporcionado, usa el default
    export_format = getattr(args, "format", None) or default_format
    
    if not export_file:
        # Mapear formatos a extensiones de archivo deseadas
        extension_map = {
            "postgresql": "sql",
            "csv": "csv",
            "json": "json",
        }
        extension = extension_map.get(export_format, export_format)
        export_file = os.path.abspath(f"{default_filename}.{extension}")
    else:
        if not os.path.isabs(export_file):
            export_file = os.path.abspath(export_file)
    
    return export_file, export_format


def get_groups_output_file(args):
    """Determina el archivo de salida específico para el comando groups."""
    return get_output_file(args, default_filename="groups", default_format="csv")


def get_fetch_output_file(args):
    """Determina el archivo de salida específico para el comando fetch."""
    return get_output_file(args, default_filename="posts", default_format="csv")


def ensure_directory_exists(file_path):
    """Asegura que el directorio del archivo exista."""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)