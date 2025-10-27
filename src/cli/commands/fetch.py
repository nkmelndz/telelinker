import re
import os
import json
from src.services.telegram_service import TelegramService
from src.scrapers import SCRAPERS
from ..handlers.config import load_config, get_config_values
from ..handlers.session import validate_session
from ..handlers.output import get_fetch_output_file
from ..formatters.csv_formatter import open_posts_csv_writer
from ..formatters.sql_formatter import open_sql_inserter
from ..formatters.json_formatter import open_posts_json_writer
from src.utils.normalize_date import normalize_date
from src.utils.parse_count import _parse_count as parse_count
from contextlib import contextmanager
from InquirerPy import inquirer

@contextmanager
def group_progress(limit, group):
    if limit is not None:
        with Progress(
            SpinnerColumn(),
            TextColumn("Processing urls in group {task.fields[group_name]} [{task.fields[group_id]}]"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total} urls"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            transient=True,
        ) as progress:
            task_id = progress.add_task(
                "fetch", total=limit, group_name=group['name'], group_id=group['id']
            )
            yield progress, task_id
    else:
        with Progress(
            SpinnerColumn(),
            TextColumn("Processing urls in group {task.fields[group_name]} [{task.fields[group_id]}]: {task.completed} urls"),
            transient=True,
        ) as progress:
            task_id = progress.add_task(
                "fetch", total=None, group_name=group['name'], group_id=group['id']
            )
            yield progress, task_id
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn

# Detección básica de plataforma según dominio
DOMAIN_TO_PLATFORM = {
    'linkedin.com': 'LinkedIn',
    'dev.to': 'Dev.to',
    'youtube.com': 'YouTube',
    'youtu.be': 'YouTube',
    'medium.com': 'Medium',
    'instagram.com': 'Instagram',
    'tiktok.com': 'TikTok',
}

URL_REGEX = re.compile(r"https?://[^\s]+", re.IGNORECASE)


def pick_scraper(url: str):
    """Selecciona el scraper apropiado basado en la URL."""
    for domain, platform in DOMAIN_TO_PLATFORM.items():
        if domain in url:
            fn = SCRAPERS.get(platform)
            if fn:
                return platform, fn
    return None, None


def extract_urls(text: str):
    if not text:
        return []
    return URL_REGEX.findall(text)


def process_message_urls(msg, limit, enlace_count):
    """Extrae URLs del mensaje, detecta plataforma y ejecuta el scraper.
    Devuelve solo URLs de plataformas soportadas con 'url', 'platform', 'data'.
    El límite cuenta únicamente enlaces soportados.
    """
    urls = extract_urls(getattr(msg, 'message', '') or '')
    processed = []
    for url in urls:
        platform, scraper = pick_scraper(url)
        if not scraper:
            # Saltar URLs de plataformas no soportadas
            continue
        scraped = None
        try:
            scraped = scraper(url)
        except Exception:
            scraped = None
        processed.append({'url': url, 'platform': platform, 'data': scraped})
        enlace_count[0] += 1
        if limit is not None and enlace_count[0] >= limit:
            break
    return processed


def build_row(group_id: str, url: str, platform: str | None, data: dict) -> dict:
    """Construye una fila normalizada para CSV/SQL a partir de los datos de scraping."""
    fecha = data.get("fecha_publicacion")
    likes = data.get("likes")
    comentarios = data.get("comentarios")
    compartidos = data.get("compartidos")
    visitas = data.get("visitas")
    return {
        "group_id": group_id,
        "url": url,
        "plataforma": platform,
        "tipo_contenido": data.get("tipo_contenido"),
        "autor_contenido": data.get("autor_contenido"),
        "fecha_publicacion": normalize_date(fecha) if fecha else None,
        "likes": parse_count(str(likes)) if likes is not None else None,
        "comentarios": parse_count(str(comentarios)) if comentarios is not None else None,
        "compartidos": parse_count(str(compartidos)) if compartidos is not None else None,
        "visitas": parse_count(str(visitas)) if visitas is not None else None,
    }


def process_group_stream(group: dict, tg_service, limit: int | None, on_row) -> int:
    """Procesa un grupo en streaming llamando on_row(row) por cada URL y devuelve el conteo."""
    group_count = [0]
    print_fetch_message(group, limit)
    try:
        with group_progress(limit, group) as (progress, task_id):
            for msg in tg_service.iter_group_messages(group["id"]):
                processed_urls = process_message_urls(msg, limit, group_count)
                progress.advance(task_id, len(processed_urls) if processed_urls else 0)
                if processed_urls:
                    for u in processed_urls:
                        data = u.get("data") or {}
                        row = build_row(group.get("id"), u.get("url"), u.get("platform"), data)
                        on_row(row)
                if limit is not None and group_count[0] >= limit:
                    break
    except Exception as e:
        print(f"⚠️ Could not iterate messages for group {group['id']}: {e}")
        return group_count[0]
    print(f"✔ Group {group['name']} [{group['id']}] processed {group_count[0]} urls")
    return group_count[0]



def print_fetch_message(group, limit):
    lim_txt = f" (limit {limit})" if limit is not None else " (no limit)"
    print(f"🔎 Fetching from group {group['name']} [{group['id']}]" + lim_txt)




def collect_groups(client):
    """Recolecta todos los grupos del usuario."""
    grupos = []
    for dialog in client.iter_user_dialogs():
        if dialog.is_group:
            grupos.append({"id": dialog.id, "name": dialog.name})
    return grupos

def load_groups_from_args(args):
    """Carga los grupos desde los argumentos (archivo o grupo individual).
    Soporta archivos CSV y JSON. En JSON acepta una lista de objetos
    o un objeto con clave 'groups'. Cada objeto debe tener al menos 'id' y opcionalmente 'name'.
    """
    groups = []
    if hasattr(args, 'groups_file') and args.groups_file:
        path = args.groups_file
        if not os.path.exists(path):
            raise FileNotFoundError(f"❌ Groups file not found: {path}")
        ext = os.path.splitext(path)[1].lower()
        if ext == '.json':
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            items = data.get('groups') if isinstance(data, dict) else data
            if not isinstance(items, list):
                raise ValueError("❌ Invalid JSON format: expected list or {groups: []}")
            for item in items:
                if isinstance(item, dict):
                    gid = item.get("id") or item.get("group_id") or item.get("channel_id")
                    name = item.get("name") or item.get("group_name") or item.get("title")
                    if gid is None:
                        continue
                    try:
                        gid_int = int(gid)
                        groups.append({"id": gid_int, "name": str(name or gid_int)})
                    except Exception:
                        groups.append({"id": gid, "name": str(name or gid)})
                elif isinstance(item, (list, tuple)) and len(item) >= 2:
                    id_val, name_val = item[0], item[1]
                    try:
                        gid_int = int(id_val)
                        groups.append({"id": gid_int, "name": str(name_val)})
                    except Exception:
                        groups.append({"id": id_val, "name": str(name_val)})
                elif isinstance(item, (int, str)):
                    try:
                        gid_int = int(item)
                        groups.append({"id": gid_int, "name": str(gid_int)})
                    except Exception:
                        groups.append({"id": item, "name": str(item)})
        else:
            # CSV: admite cabecera opcional 'id,name' en la primera línea
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            start_index = 1 if lines and lines[0].strip().lower().startswith(('id', 'group_id')) else 0
            for line in lines[start_index:]:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) >= 2:
                        id_raw, name_raw = parts[0], parts[1]
                        try:
                            groups.append({"id": int(id_raw), "name": name_raw})
                        except Exception:
                            groups.append({"id": id_raw, "name": name_raw})
    elif hasattr(args, 'group') and args.group:
        # Grupo individual
        gid = args.group
        try:
            gid_int = int(gid)
            groups.append({"id": gid_int, "name": str(gid_int)})
        except Exception:
            groups.append({"id": gid, "name": gid})
    return groups


def export_to_csv(groups, tg_service, limit, out_file):
    """Exporta en CSV escribiendo filas en streaming mientras se scrapea."""
    total_count = 0
    with open_posts_csv_writer(out_file) as write_row:
        for group in groups:
            count = process_group_stream(group, tg_service, limit, on_row=write_row)
            total_count += count
    return total_count


def export_to_json(groups, tg_service, limit, out_file):
    """Exporta a JSON escribiendo elementos en streaming mientras se scrapea."""
    total_count = 0
    with open_posts_json_writer(out_file) as write_row:
        for group in groups:
            count = process_group_stream(group, tg_service, limit, on_row=write_row)
            total_count += count
    return total_count


def export_to_postgresql(groups, tg_service, limit, out_file):
    """Exporta a SQL escribiendo INSERTs en streaming mientras se scrapea."""
    total_count = 0
    with open_sql_inserter(out_file) as write_row:
        for group in groups:
            count = process_group_stream(group, tg_service, limit, on_row=write_row)
            total_count += count
    return total_count


def run(args):
    """Función principal que ejecuta el comando fetch."""
    try:
        # Cargar configuración
        cfg, config_dir = load_config()
        config_values = get_config_values(cfg)
        # Validar sesión
        session_file = validate_session(config_dir, config_values['session_name'])
        # Inicializar servicio de Telegram y asegurar que está iniciado
        tg_service = TelegramService(session_file, config_values['api_id'], config_values['api_hash'])
        success = tg_service.start()
        
        if not success:
            print("❌ Authentication failed. Please run 'telelinker login' first.")
            return
        try:
            # Si se pidió modo interactivo explícito o no hay argumentos de grupo, iniciar InquirerPy
            no_group_args = not getattr(args, 'groups_file', None) and not getattr(args, 'group', None)
            if getattr(args, 'interactive', None) or no_group_args:
                # 1) Listar grupos para seleccionar
                grupos_disponibles = collect_groups(tg_service)
                if not grupos_disponibles:
                    raise ValueError("❌ No groups found in your account")
                choices = [{"name": f"{g['name']} ({g['id']})", "value": g} for g in grupos_disponibles]
                selected = []
                while not selected:
                    selected = inquirer.checkbox(
                        message="Select groups (space to mark, enter to confirm)",
                        choices=choices,
                        instruction="↑/↓ navigate, space to select"
                    ).execute()
                    if not selected:
                        print("⚠ You must select at least one group.")
                # 2) Cantidad de enlaces por grupo
                while True:
                    limit_input = inquirer.text(
                        message="Cantidad de enlaces por grupo (vacío=sin límite)",
                        default=""
                    ).execute()
                    if not limit_input:
                        limit = None
                        break
                    try:
                        limit = int(limit_input)
                        if limit < 0:
                            print("⚠ Ingresa un número válido (>= 0)")
                            continue
                        break
                    except Exception:
                        print("⚠ Ingresa un número válido o deja vacío")
                # 3) Formato de exportación
                fmt = inquirer.select(
                    message="Formato de exportación",
                    choices=["csv", "postgresql", "json"],
                    default="csv"
                ).execute()
                ext_map = {"csv": "csv", "postgresql": "sql", "json": "json"}
                default_out = os.path.abspath(f"posts.{ext_map[fmt]}")
                # 4) Nombre del archivo
                out_input = inquirer.text(
                    message="Nombre del archivo de exportación",
                    default=default_out
                ).execute()
                out_file = os.path.abspath(out_input.strip()) if out_input else default_out
                # Asegurar extensión correcta
                ext = "." + ext_map[fmt]
                if not out_file.lower().endswith(ext):
                    out_file += ext
                # Ejecutar exportación según formato
                if fmt == "postgresql":
                    total = export_to_postgresql(selected, tg_service, limit, out_file)
                    print(f"📋 Exported {total} urls to {out_file} as SQL")
                elif fmt == "json":
                    total = export_to_json(selected, tg_service, limit, out_file)
                    print(f"📋 Exported {total} urls to {out_file} as JSON")
                else:
                    total = export_to_csv(selected, tg_service, limit, out_file)
                    print(f"📋 Exported {total} urls to {out_file} as CSV")
            else:
                # Modo no interactivo: usar argumentos
                groups = load_groups_from_args(args)
                if not groups:
                    raise ValueError("❌ No groups specified. Use --group or --groups-file")
                export_file, export_format = get_fetch_output_file(args)
                raw_limit = getattr(args, "limit", None)
                limit = int(raw_limit) if raw_limit is not None else None
                # Exportar según formato
                if export_format == "postgresql":
                    total = export_to_postgresql(groups, tg_service, limit, export_file)
                    print(f"📋 Exported {total} urls to {export_file} as SQL")
                elif export_format == "json":
                    total = export_to_json(groups, tg_service, limit, export_file)
                    print(f"📋 Exported {total} urls to {export_file} as JSON")
                else:
                    total = export_to_csv(groups, tg_service, limit, export_file)
                    print(f"📋 Exported {total} urls to {export_file} as CSV")
        finally:
            tg_service.disconnect()
    except FileNotFoundError as e:
        print(str(e))
    except Exception as e:
        msg = str(e).lower()
        if "database is locked" in msg or "locked" in msg:
            print("❌ Error: database is locked")
            print("Close other Python/Telelinker processes using the same session.")
            print("If it persists, run 'python -m src.main logout' and then 'python -m src.main login' to recreate the session.")
        else:
            print(f"❌ Error: {str(e)}")
