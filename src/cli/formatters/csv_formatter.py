import csv
import os
from typing import List, Dict, Any


def ensure_directory_exists(file_path: str) -> None:
    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)


def export_groups_to_csv(groups: List[Dict[str, Any]], file_path: str) -> str:
    ensure_directory_exists(file_path)

    headers = ["id", "name"]

    with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for group in groups:
            writer.writerow({
                "id": group.get("id"),
                "name": group.get("name"),
            })

    return file_path


def export_posts_to_csv(rows: List[Dict[str, Any]], file_path: str) -> str:
    """
    Exporta las columnas requeridas incluyendo group_id:
    group_id, url, plataforma, tipo_contenido, autor_contenido, fecha_publicacion,
    likes, comentarios, compartidos, visitas.
    """
    ensure_directory_exists(file_path)

    headers = [
        "group_id",
        "url",
        "plataforma",
        "tipo_contenido",
        "autor_contenido",
        "fecha_publicacion",
        "likes",
        "comentarios",
        "compartidos",
        "visitas",
    ]

    with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for r in rows:
            writer.writerow({
                "group_id": r.get("group_id"),
                "url": r.get("url"),
                "plataforma": r.get("plataforma"),
                "tipo_contenido": r.get("tipo_contenido"),
                "autor_contenido": r.get("autor_contenido"),
                "fecha_publicacion": r.get("fecha_publicacion"),
                "likes": r.get("likes"),
                "comentarios": r.get("comentarios"),
                "compartidos": r.get("compartidos"),
                "visitas": r.get("visitas"),
            })

    return file_path