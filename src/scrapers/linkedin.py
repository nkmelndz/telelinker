import requests
from bs4 import BeautifulSoup
import json
import re
from src.utils.parse_count import _parse_count
from src.utils.normalize_date import normalize_date

def scrap(url, config=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    }
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
    except Exception:
        return {
            'autor_contenido': None,
            'likes': None,
            'comentarios': None,
            'compartidos': None,
            'visitas': None,
            'fecha_publicacion': None,
            'tipo_contenido': None,
        }
    soup = BeautifulSoup(resp.text, 'html.parser')
    autor_tag = soup.select_one('a[data-tracking-control-name="public_post_feed-actor-name"]')
    if not autor_tag:
        autor_tag = next((a for a in soup.find_all('a') if a.get('data-tracking-control-name', '').endswith('actor-name')), None)
    autor_contenido = autor_tag.get_text(strip=True) if autor_tag else None
    likes_tag = soup.select_one('span[data-test-id="social-actions__reaction-count"]')
    likes = _parse_count(likes_tag.get_text(strip=True)) if likes_tag else 0
    cm_a = soup.select_one('a[data-test-id="social-actions__comments"]')
    comentarios = 0
    if cm_a:
        raw_attr = cm_a.get('data-num-comments') or cm_a.get('data-enum-comments')
        comentarios = _parse_count(raw_attr) if raw_attr else _parse_count(cm_a.get_text())
    fecha_publicacion = None
    for script in soup.find_all('script', attrs={'type': 'application/ld+json'}):
        txt = script.string or script.get_text(strip=True)
        if not txt:
            continue
        try:
            data = json.loads(txt)
        except Exception:
            m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', txt)
            if m:
                fecha_publicacion = m.group(1)
                break
            continue
        def find_date(obj):
            nonlocal fecha_publicacion
            if isinstance(obj, dict):
                if obj.get('@type') in ('DiscussionForumPosting', 'SocialMediaPosting'):
                    if 'datePublished' in obj:
                        fecha_publicacion = obj['datePublished']
                        return True
                for v in obj.values():
                    if find_date(v):
                        return True
            elif isinstance(obj, list):
                for it in obj:
                    if find_date(it):
                        return True
            return False
        if find_date(data):
            break
    fecha_publicacion = normalize_date(fecha_publicacion)
    return {
        'autor_contenido': autor_contenido,
        'likes': likes,
        'comentarios': comentarios,
        'compartidos': None,
        'visitas': None,
        'fecha_publicacion': fecha_publicacion,
        'tipo_contenido': None,
    }
