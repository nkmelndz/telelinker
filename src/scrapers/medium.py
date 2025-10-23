from src.utils.normalize_date import normalize_date
import re
import json
import requests
from bs4 import BeautifulSoup

def scrap(url, config=None):
    """Scrapea datos clave de un artículo de Medium usando window.__APOLLO_STATE__"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; scraper/1.0; +https://example.com)'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
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
    apollo_json = None
    for script in soup.find_all('script'):
        if script.string and 'window.__APOLLO_STATE__' in script.string:
            m = re.search(r'window\.__APOLLO_STATE__\s*=\s*(\{.*?\});?\s*$', script.string, re.DOTALL)
            if m:
                try:
                    apollo_json = json.loads(m.group(1))
                except Exception:
                    pass
            break

    autor = None
    likes = None
    comentarios = None
    fecha_publicacion = None

    if apollo_json:
        # Buscar el primer objeto tipo "User" para el autor
        for k, v in apollo_json.items():
            if isinstance(v, dict) and v.get('__typename') == 'User' and v.get('name'):
                autor = v.get('name')
                break
        # Buscar el primer objeto tipo "Post" para likes, comentarios, fecha
        for k, v in apollo_json.items():
            if isinstance(v, dict) and v.get('__typename') == 'Post':
                likes = v.get('clapCount')
                fecha_publicacion = v.get('dateModified')
                post_responses = v.get('postResponses')
                if isinstance(post_responses, dict):
                    comentarios = post_responses.get('count')
                break

    # Si no se encontró la fecha, buscar en <script type="application/ld+json">
    if not fecha_publicacion:
        for script in soup.find_all('script', attrs={'type': 'application/ld+json'}):
            try:
                data = json.loads(script.string or script.get_text())
                if isinstance(data, dict) and 'datePublished' in data:
                    fecha_publicacion = data['datePublished']
                    break
            except Exception:
                continue

    return {
        'autor_contenido': autor,
        'likes': likes,
        'comentarios': comentarios,
        'compartidos': None,
        'visitas': None,
        'fecha_publicacion': normalize_date(fecha_publicacion),
        'tipo_contenido': 'artículo',
    }
