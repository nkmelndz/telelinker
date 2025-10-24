"""
Formatter especializado para exportación CSV.
"""
import csv
from ..handlers.output import ensure_directory_exists


def export_groups_to_csv(grupos, export_file):
    """Exporta los grupos a formato CSV."""
    ensure_directory_exists(export_file)
    
    with open(export_file, "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name"])  # Header
        for grupo in grupos:
            writer.writerow([grupo['id'], grupo['name']])


def export_posts_to_csv(posts, export_file):
    """Exporta los posts a formato CSV."""
    ensure_directory_exists(export_file)
    
    with open(export_file, "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        # Header
        writer.writerow(["group_id", "group_name", "message_id", "date", "message", "urls"])
        
        for post in posts:
            writer.writerow([
                post.get('group_id', ''),
                post.get('group_name', ''),
                post.get('message_id', ''),
                post.get('date', ''),
                post.get('message', ''),
                post.get('urls', '')
            ])


def format_data_for_csv(data):
    """Formatea los datos para exportación CSV."""
    if isinstance(data, list):
        return '; '.join(str(item) for item in data)
    return str(data) if data is not None else ''