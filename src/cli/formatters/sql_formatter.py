import os
from typing import List, Dict, Any
from contextlib import contextmanager


def ensure_directory_exists(file_path: str) -> None:
    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)


def _escape(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value).replace("'", "''")
    return f"'{s}'"




@contextmanager
def open_sql_inserter(file_path: str):
    """Context manager que abre un SQL, crea la tabla y devuelve write_row(row).
    Cada llamada a write_row escribe un INSERT y hace flush para escritura en streaming.
    """
    ensure_directory_exists(file_path)

    f = open(file_path, mode="w", encoding="utf-8")
    f.write("-- Export enlaces_redes_sociales\n\n")
    f.write(
        "CREATE TABLE IF NOT EXISTS enlaces_redes_sociales (\n"
        "    group_id TEXT,\n"
        "    url TEXT,\n"
        "    plataforma TEXT,\n"
        "    tipo_contenido TEXT,\n"
        "    autor_contenido TEXT,\n"
        "    fecha_publicacion TEXT,\n"
        "    likes INTEGER,\n"
        "    comentarios INTEGER,\n"
        "    compartidos INTEGER,\n"
        "    visitas INTEGER\n"
        ");\n\n"
    )
    try:
        def write_row(r: Dict[str, Any]):
            f.write(
                "INSERT INTO enlaces_redes_sociales (group_id, url, plataforma, tipo_contenido, autor_contenido, fecha_publicacion, likes, comentarios, compartidos, visitas) VALUES ("
                f"{_escape(r.get('group_id'))}, "
                f"{_escape(r.get('url'))}, "
                f"{_escape(r.get('plataforma'))}, "
                f"{_escape(r.get('tipo_contenido'))}, "
                f"{_escape(r.get('autor_contenido'))}, "
                f"{_escape(r.get('fecha_publicacion'))}, "
                f"{_escape(r.get('likes'))}, "
                f"{_escape(r.get('comentarios'))}, "
                f"{_escape(r.get('compartidos'))}, "
                f"{_escape(r.get('visitas'))}"
                ");\n"
            )
            f.flush()
        yield write_row
    finally:
        f.close()