"""
Módulo para manejo de archivos de salida.
"""
import os


def get_output_file(args, default_filename="output", default_format="csv"):
    """Determina el archivo de salida basado en los argumentos."""
    export_file = getattr(args, "out", None)
    export_format = getattr(args, "format", default_format)
    
    if not export_file:
        extension = "csv" if export_format == "csv" else export_format
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