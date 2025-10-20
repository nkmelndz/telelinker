"""
Programa base para identificar y listar todos los enlaces compartidos en un grupo de Telegram.
docker build -t telegram-links-app .
docker run -it telegram-links-app
"""

from telethon.sync import TelegramClient
import re
import requests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import psycopg2
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (si existe)
load_dotenv()

# --- Configuración ---
# Variables sensibles cargadas desde entorno (.env)
api_id_raw = os.getenv('API_ID')
try:
    api_id = int(api_id_raw)
except Exception:
    api_id = api_id_raw
api_hash = os.getenv('API_HASH')
session_name = os.getenv('SESSION_NAME')

# Grupo (puede ser username público o ID numérico). Intentar convertir a int si es posible.
group_raw = os.getenv('GROUP_USERNAME')
try:
    group_username = int(group_raw)
except Exception:
    group_username = group_raw

# --- Conexión ---
client = TelegramClient(session_name, api_id, api_hash)
client.start()

# --- Configuración de PostgreSQL ---
db_config = {
    'host': os.getenv('DB_HOST'),      # Cambia si usas Docker Compose con servicio de base de datos
    'dbname': os.getenv('DB_NAME'),   # Cambia por el nombre de tu base de datos
    'user': os.getenv('DB_USER'),       # Cambia por tu usuario
    'password': os.getenv('DB_PASSWORD')    # Cambia por tu contraseña
}

try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    print("Conexión a PostgreSQL exitosa.")
except Exception as e:
    print(f"Error al conectar a PostgreSQL: {e}")
    conn = None
    cursor = None

# --- Extracción de enlaces ---
print(f"Extrayendo enlaces del grupo: {group_username}")

enlaces = []
for message in client.iter_messages(group_username):
    if message.message:
        urls = re.findall(r'(https?://[^\s]+)', message.message)
        if urls:
            enlaces.extend(urls)

redes = {
    'LinkedIn': ['linkedin.com'],
    'Dev.to': ['dev.to'],
    'YouTube': ['youtube.com', 'youtu.be'],
    'Medium': ['medium.com'],
    'Instagram': ['instagram.com'],
    'TikTok': ['tiktok.com'],
}

conteo_redes = {}
for url in enlaces:
    encontrada = False
    for nombre, dominios in redes.items():
        if any(dominio in url for dominio in dominios):
            conteo_redes[nombre] = conteo_redes.get(nombre, 0) + 1
            encontrada = True
            break
    if not encontrada:
        conteo_redes['Otra'] = conteo_redes.get('Otra', 0) + 1

# --- Listado de enlaces ---
print(f"Total de enlaces encontrados: {len(enlaces)}")
print("\nRedes sociales extraídas y concurrencia:")
for nombre, cantidad in sorted(conteo_redes.items(), key=lambda x: x[1], reverse=True):
    print(f"{nombre}: {cantidad}")

def _parse_count(value: str | None) -> int | None:
    if not value:
        return None
    txt = value.strip().replace('\xa0', ' ')
    m = re.search(r'([\d\.,]+)\s*([KkMm])?', txt)
    if not m:
        # a veces viene directamente en atributo (p.ej. "2")
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

def scrap_linkedin(url):
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

    # Autor: <a ... data-tracking-control-name="public_post_feed-actor-name">Nombre</a>
    autor_tag = soup.select_one('a[data-tracking-control-name="public_post_feed-actor-name"]')
    if not autor_tag:
        # Fallback genérico: cualquier <a> cuyo atributo termine en actor-name
        autor_tag = next((a for a in soup.find_all('a')
                          if a.get('data-tracking-control-name', '').endswith('actor-name')), None)
    autor_contenido = autor_tag.get_text(strip=True) if autor_tag else None

    # Likes: <span data-test-id="social-actions__reaction-count">N</span>
    likes_tag = soup.select_one('span[data-test-id="social-actions__reaction-count"]')
    likes = _parse_count(likes_tag.get_text(strip=True)) if likes_tag else 0

    # Comentarios: desde atributo data-num-comments (fallback a texto visible)
    cm_a = soup.select_one('a[data-test-id="social-actions__comments"]')
    comentarios = 0
    if cm_a:
        raw_attr = cm_a.get('data-num-comments') or cm_a.get('data-enum-comments')
        comentarios = _parse_count(raw_attr) if raw_attr else _parse_count(cm_a.get_text())

    # Fecha exacta desde JSON-LD (datePublished)
    fecha_publicacion = None
    for script in soup.find_all('script', attrs={'type': 'application/ld+json'}):
        txt = script.string or script.get_text(strip=True)
        if not txt:
            continue
        found = False
        try:
            data = json.loads(txt)
        except Exception:
            m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', txt)
            if m:
                fecha_publicacion = m.group(1)
                break
            continue

        def find_date(obj) -> bool:
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

    return {
        'autor_contenido': autor_contenido,
        'likes': likes,
        'comentarios': comentarios,
        'compartidos': None,
        'visitas': None,
        'fecha_publicacion': fecha_publicacion,
        'tipo_contenido': None,
    }

def scrap_youtube(url):
    import yt_dlp
    try:
        ydl_opts = {
            'extract_flat': False,
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            autor = info.get('uploader')
            likes = info.get('like_count', 0)
            comentarios = info.get('comment_count', 0)
            visitas = info.get('view_count', 0)
            fecha_publicacion = info.get('upload_date')
            return {
                'autor_contenido': autor,
                'likes': likes,
                'comentarios': comentarios,
                'compartidos': None,
                'visitas': visitas,
                'fecha_publicacion': fecha_publicacion,
                'tipo_contenido': 'video',
            }
    except Exception:
        return {
            'autor_contenido': None,
            'likes': None,
            'comentarios': None,
            'compartidos': None,
            'visitas': None,
            'fecha_publicacion': None,
            'tipo_contenido': 'video',
        }

def scrap_tiktok(url):
    # Aquí iría el scraping específico para TikTok
    return {}

def scrap_instagram(url):
    # Aquí iría el scraping específico para Instagram
    return {}

def scrap_medium(url):
    # Aquí iría el scraping específico para Medium
    return {}

def scrap_devto(url):
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

    # 1) JSON-LD: BlogPosting
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
            # Autor
            author_node = node.get('author')
            if isinstance(author_node, dict):
                autor = author_node.get('name') or autor
            elif isinstance(author_node, list) and author_node:
                a0 = author_node[0]
                if isinstance(a0, dict):
                    autor = a0.get('name') or autor
            # Fecha
            fecha_publicacion = node.get('datePublished') or node.get('dateCreated') or fecha_publicacion
            # Comentarios (si existiera en JSON-LD)
            if comentarios is None:
                comentarios = node.get('commentCount')
            break

    # 2) Fallback: __NEXT_DATA__ (contiene post.public_reactions_count, comments_count, published_at, user)
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
                    # Autor
                    if autor is None:
                        user = post.get('user') or {}
                        autor = user.get('name') or user.get('username') or autor
                    # Fecha
                    if fecha_publicacion is None:
                        fecha_publicacion = post.get('published_at') or post.get('published_timestamp') or fecha_publicacion
                    # Reacciones (likes)
                    if likes is None:
                        likes = post.get('public_reactions_count')
                    # Comentarios
                    if comentarios is None:
                        comentarios = post.get('comments_count')
                    # Vistas (si está disponible públicamente)
                    if visitas is None:
                        visitas = post.get('page_views_count')
            except Exception:
                pass

    # 3) Fallback directo a spans de la UI (ids: reaction_total_count, reaction-number-comment)
    if comentarios is None:
        span_comments = soup.find('span', id='reaction-number-comment') or soup.select_one('#reaction-number-comment')
        if span_comments:
            raw = span_comments.get('data-count') or span_comments.get_text(strip=True)
            comentarios = _parse_count(raw)

    # Si likes sigue siendo None, usar Selenium para obtener el valor renderizado
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

    # Normalización de números
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

scrapers = {
    'LinkedIn': scrap_linkedin,
    'Dev.to': scrap_devto,
    'YouTube': scrap_youtube,
    'Medium': scrap_medium,
    'Instagram': scrap_instagram,
    'TikTok': scrap_tiktok,
}

def insertar_enlace_pg(datos):
    if not cursor or not conn:
        print("No hay conexión a la base de datos.")
        return False
    # Verificar campos obligatorios
    requeridos = ['autor_contenido', 'likes', 'comentarios', 'fecha_publicacion']
    if not all(datos.get(campo) is not None for campo in requeridos):
        print(f"\nDatos incompletos, se omite: {datos.get('url')}")
        return False
    try:
        cursor.execute('''
            INSERT INTO enlaces (url, plataforma, tipo_contenido, autor_contenido, fecha_publicacion, likes, comentarios, compartidos, visitas)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            datos.get('url'),
            datos.get('plataforma'),
            datos.get('tipo_contenido'),
            datos.get('autor_contenido'),
            datos.get('fecha_publicacion'),
            datos.get('likes'),
            datos.get('comentarios'),
            datos.get('compartidos'),
            datos.get('visitas')
        ))
        conn.commit()
        print(f"\n\nEnlace insertado: {datos.get('url')}")
        return True
    except Exception as e:
        print(f"Error al insertar: {e}")
        conn.rollback()
        return False

# Procesar cada enlace y aplicar el scraper correspondiente
for url in enlaces:
    for nombre, dominios in redes.items():
        if any(dominio in url for dominio in dominios):
            datos = scrapers[nombre](url)
            datos['url'] = url
            datos['plataforma'] = nombre
            insertar_enlace_pg(datos)
            print(f"\nDatos extraídos de {nombre} para el enlace:")
            print(datos)
            break

client.disconnect()
