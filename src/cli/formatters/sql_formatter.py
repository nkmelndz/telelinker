import os
from typing import List, Dict, Any


def ensure_directory_exists(file_path: str) -> None:
    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)


def _escape(val: Any) -> str:
    if val is None:
        return "NULL"
    if isinstance(val, (int, float)):
        return str(val)
    s = str(val)
    s = s.replace("'", "''")
    return f"'{s}'"


def generate_sql_file(rows: List[Dict[str, Any]], file_path: str) -> str:
    """
    Genera un archivo SQL con la tabla enlaces_redes_sociales y
    sentencias INSERT por cada URL procesada.
    Incluye group_id y las columnas requeridas.
    """
    ensure_directory_exists(file_path)

    columns = [
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

    create_table = (
        "CREATE TABLE IF NOT EXISTS enlaces_redes_sociales (\n"
        "  id SERIAL PRIMARY KEY,\n"
        "  group_id BIGINT NOT NULL,\n"
        "  url TEXT NOT NULL,\n"
        "  plataforma VARCHAR(50) NOT NULL,\n"
        "  tipo_contenido VARCHAR(50),\n"
        "  autor_contenido VARCHAR(100),\n"
        "  fecha_publicacion TIMESTAMP,\n"
        "  likes INT,\n"
        "  comentarios INT,\n"
        "  compartidos INT,\n"
        "  visitas INT\n"
        ");\n\n"
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("-- Export enlaces_redes_sociales\n")
        f.write(create_table)
        for r in rows:
            values = [
                _escape(r.get("group_id")),
                _escape(r.get("url")),
                _escape(r.get("plataforma")),
                _escape(r.get("tipo_contenido")),
                _escape(r.get("autor_contenido")),
                _escape(r.get("fecha_publicacion")),
                _escape(r.get("likes")),
                _escape(r.get("comentarios")),
                _escape(r.get("compartidos")),
                _escape(r.get("visitas")),
            ]
            insert_stmt = (
                f"INSERT INTO enlaces_redes_sociales ({', '.join(columns)}) VALUES ("
                + ", ".join(values) + ");\n"
            )
            f.write(insert_stmt)

    return file_path