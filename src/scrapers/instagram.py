
import json
import re
from datetime import datetime, timezone
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from src.utils.parse_count import _parse_count
from src.utils.normalize_date import normalize_date


def scrap(url, config=None):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--lang=es-ES')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(3)

    likes = None
    comentarios = None
    
    try:
        # Extraer el primer span para likes
        spans = driver.find_elements(By.XPATH, '//span[contains(@class, "xdj266r") and contains(@class, "x14z9mp") and contains(@class, "xat24cr")]')
        if len(spans) > 0:
            likes = spans[0].text.strip()
        if len(spans) > 1:
            comentarios = spans[1].text.strip()
    except Exception:
        likes = None
        comentarios = None
        
    try:
        span_user = driver.find_element(By.XPATH, '//span[contains(@class, "x1lliihq") and contains(@class, "x1plvlek") and contains(@class, "xryxfnj") and contains(@class, "x1n2onr6") and contains(@class, "xyejjpt") and contains(@class, "x15dsfln") and contains(@class, "x193iq5w") and contains(@class, "xeuugli") and contains(@class, "x1fj9vlw") and contains(@class, "x13faqbe") and contains(@class, "x1vvkbs") and contains(@class, "x1s928wv") and contains(@class, "xhkezso") and contains(@class, "x1gmr53x") and contains(@class, "x1cpjm7i") and contains(@class, "x1fgarty") and contains(@class, "x1943h6x") and contains(@class, "x1i0vuye") and contains(@class, "xvs91rp") and contains(@class, "x1s688f") and contains(@class, "x5n08af") and contains(@class, "x10wh9bi") and contains(@class, "xpm28yp") and contains(@class, "x8viiok") and contains(@class, "x1o7cslx")]')
        username = span_user.text.strip()
    except Exception:
        username = None
        
    fecha_publicacion = None
    try:
        time_elem = driver.find_element(By.XPATH, '//time[@class="x1p4m5qa"]')
        fecha_publicacion = time_elem.get_attribute('datetime')
    except Exception:
        fecha_publicacion = None

    driver.quit()

    likes = (int(likes) if isinstance(likes, (int, float)) else _parse_count(str(likes)) if likes is not None else None)
    comentarios = (int(comentarios) if isinstance(comentarios, (int, float)) else _parse_count(str(comentarios)) if comentarios is not None else None)
    
    return {
        'autor_contenido': username,
        'likes': likes,
        'comentarios': comentarios,
        'compartidos': None,
        'visitas': None,
        'fecha_publicacion': normalize_date(fecha_publicacion),
        'tipo_contenido': 'foto/video',
    }