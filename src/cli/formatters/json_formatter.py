from __future__ import annotations

import json
from contextlib import contextmanager
from typing import Callable, Iterable, Mapping, Any

from ..handlers.output import ensure_directory_exists


@contextmanager
def open_posts_json_writer(file_path: str, *, indent: int | None = 2) -> Iterable[Callable[[Mapping[str, Any]], None]]:
    """
    Context manager that writes a JSON array of post rows in a streaming manner.

    - Writes '[' on enter, appends items separated by commas, and closes with ']'.
    - Each row should be a plain mapping (dict-like) with JSON-serializable values.
    - Ensures the output directory exists before writing.

    Usage:
        with open_posts_json_writer("posts.json") as write_row:
            write_row({"id": 1, "text": "hello"})
            write_row({"id": 2, "text": "world"})
    """
    ensure_directory_exists(file_path)

    f = open(file_path, "w", encoding="utf-8")
    try:
        f.write("[\n")
        first = True

        def write_row(row: Mapping[str, Any]) -> None:
            nonlocal first
            if not first:
                f.write(",\n")
            else:
                first = False
            # Use json.dumps to serialize with utf-8 and optional indentation for readability
            if indent is not None:
                f.write(json.dumps(row, ensure_ascii=False, indent=indent))
            else:
                f.write(json.dumps(row, ensure_ascii=False))

        yield write_row
    finally:
        f.write("\n]\n")
        f.flush()
        f.close()