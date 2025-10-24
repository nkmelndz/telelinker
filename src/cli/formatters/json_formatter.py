"""
Formatter especializado para exportación JSON.
"""
import json
from ..handlers.output import ensure_directory_exists


def export_groups_to_json(grupos, export_file):
    """Exporta los grupos a formato JSON."""
    ensure_directory_exists(export_file)
    
    with open(export_file, "w", encoding="utf-8") as f:
        json.dump(grupos, f, ensure_ascii=False, indent=2)


def export_posts_to_json(posts, export_file):
    """Exporta los posts a formato JSON."""
    ensure_directory_exists(export_file)
    
    with open(export_file, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)


def format_data_for_json(data):
    """Formatea los datos para exportación JSON."""
    return data  # JSON mantiene los tipos de datos nativos