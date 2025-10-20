import requests
from bs4 import BeautifulSoup
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from utils import _parse_count

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
            'tipo_contenido': 'artículo',
        }
    soup = BeautifulSoup(resp.text, 'html.parser')
    autor = None
    fecha_publicacion = None
    likes = None
    comentarios = None
    visitas = None
    def _find_blog_node(obj):
        if isinstance(obj, dict):
            if obj.get('@type') in ('BlogPosting', 'Article', 'SocialMediaPosting'):
                return obj
            for v in obj.values():
                found = _find_blog_node(v)
                if found:
                    return found
        elif isinstance(obj, list):
            for it in obj:
                found = _find_blog_node(it)
                if found:
                    return found
        return None
    for script in soup.find_all('script', attrs={'type': 'application/ld+json'}):
        txt = script.string or script.get_text(strip=True)
        if not txt:
            continue
        try:
            data = json.loads(txt)
        except Exception:
            continue
        node = _find_blog_node(data)
        if node:
            author_node = node.get('author')
            if isinstance(author_node, dict):
                autor = author_node.get('name') or autor
            elif isinstance(author_node, list) and author_node:
                a0 = author_node[0]
                if isinstance(a0, dict):
                    autor = a0.get('name') or autor
            fecha_publicacion = node.get('datePublished') or node.get('dateCreated') or fecha_publicacion
            if comentarios is None:
                comentarios = node.get('commentCount')
            break
    if any(v is None for v in [autor, fecha_publicacion, likes, comentarios, visitas]):
        next_data = soup.find('script', id='__NEXT_DATA__')
        if next_data and (next_data.string or next_data.get_text()):
            try:
                nd = json.loads(next_data.string or next_data.get_text())
                obj = nd
                for k in ('props', 'pageProps'):
                    if isinstance(obj, dict) and k in obj:
                        obj = obj[k]
                post = obj.get('post') if isinstance(obj, dict) else None
                if isinstance(post, dict):
                    if autor is None:
                        user = post.get('user') or {}
                        autor = user.get('name') or user.get('username') or autor
                    if fecha_publicacion is None:
                        fecha_publicacion = post.get('published_at') or post.get('published_timestamp') or fecha_publicacion
                    if likes is None:
                        likes = post.get('public_reactions_count')
                    if comentarios is None:
                        comentarios = post.get('comments_count')
                    if visitas is None:
                        visitas = post.get('page_views_count')
            except Exception:
                pass
    if comentarios is None:
        span_comments = soup.find('span', id='reaction-number-comment') or soup.select_one('#reaction-number-comment')
        if span_comments:
            raw = span_comments.get('data-count') or span_comments.get_text(strip=True)
            comentarios = _parse_count(raw)
    if likes is None:
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=' + headers['User-Agent'])
            chrome_options.binary_location = "/usr/bin/chromium"
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            elem = driver.find_element(By.ID, 'reaction_total_count')
            likes_text = elem.text.strip()
            likes = _parse_count(likes_text)
            driver.quit()
        except Exception:
            likes = None
    likes = (int(likes) if isinstance(likes, (int, float)) else _parse_count(str(likes)) if likes is not None else None)
    comentarios = (int(comentarios) if isinstance(comentarios, (int, float)) else _parse_count(str(comentarios)) if comentarios is not None else None)
    visitas = (int(visitas) if isinstance(visitas, (int, float)) else _parse_count(str(visitas)) if visitas is not None else None)
    return {
        'url': url,
        'autor_contenido': autor,
        'likes': likes,
        'comentarios': comentarios,
        'compartidos': None,
        'visitas': visitas,
        'fecha_publicacion': fecha_publicacion,
        'tipo_contenido': 'artículo',
    }
