from datetime import datetime

def normalize_date(date_str):
    """
    Convierte una fecha en string a formato 'YYYY-MM-DD'.
    Soporta:
    - ISO 8601 (2025-03-25T13:37:26Z)
    - YYYYMMDD (20250427)
    - YYYY-MM-DD
    - Otros formatos comunes
    Si no puede convertir, retorna None.
    """
    if not date_str or not isinstance(date_str, str):
        return None
    date_str = date_str.strip()
    # ISO 8601
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
    except Exception:
        pass
    # YYYYMMDD
    try:
        if len(date_str) == 8 and date_str.isdigit():
            dt = datetime.strptime(date_str, '%Y%m%d')
            return dt.strftime('%Y-%m-%d')
    except Exception:
        pass
    # YYYY-MM-DD
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%Y-%m-%d')
    except Exception:
        pass
    # Otros formatos comunes
    for fmt in ('%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d'):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except Exception:
            pass
    return date_str
