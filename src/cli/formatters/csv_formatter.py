import csv
import os
from typing import List, Dict, Any
from contextlib import contextmanager


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




@contextmanager
def open_posts_csv_writer(file_path: str):
    """Context manager que abre un CSV, escribe cabecera y devuelve write_row(row).
    Cad a llamada a write_row escribe una fila y hace flush para escritura en streaming.
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

    f = open(file_path, mode="w", newline="", encoding="utf-8")
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    try:
        def write_row(r: Dict[str, Any]):
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
            f.flush()
        yield write_row
    finally:
        f.close()