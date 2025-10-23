from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
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

    autor = None
    try:
        # El nombre de usuario aparece en el enlace del perfil
        autor_elem = driver.find_element(By.XPATH, '//a[contains(@href, "/@")]')
        autor = autor_elem.get_attribute('href').split('/@')[-1].split('/')[0]
    except Exception:
        autor = None

    # Puedes agregar aquí la extracción de likes, comentarios, visitas, fecha_publicacion si lo necesitas

    driver.quit()

    return {
        'url': url,
        'autor_contenido': autor,
        'likes': None,
        'comentarios': None,
        'compartidos': None,
        'visitas': None,
        'fecha_publicacion': None,
        'tipo_contenido': 'video',
    }