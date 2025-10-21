import re
from typing import Optional

def _parse_count(value: str | None) -> int | None:
    if not value:
        return None
    txt = value.strip().replace('\xa0', ' ')
    m = re.search(r'([\d\.,]+)\s*([KkMm])?', txt)
    if not m:
        digits = re.sub(r'[^\d]', '', txt)
        return int(digits) if digits else None
    num = m.group(1).replace('.', '').replace(',', '')
    try:
        n = float(num)
    except ValueError:
        return None
    suf = m.group(2)
    if suf:
        if suf.upper() == 'K':
            n *= 1_000
        elif suf.upper() == 'M':
            n *= 1_000_000
    return int(n)