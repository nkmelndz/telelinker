def scrap(url, config=None):
    autor_contenido = None
    fecha_publicacion = None
    likes = None
    comentarios = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")

        # --- autor_contenido ---
        try:
            autor_contenido = page.locator('h3[data-e2e="video-author-uniqueid"]').inner_text()
        except:
            try:
                autor_contenido = page.locator('span[data-e2e="browse-username"]').inner_text()
            except:
                autor_contenido = None

        # --- fecha_publicacion ---
        try:
            # Busca el último span dentro del contenedor que tiene la fecha
            fecha_publicacion = page.locator(
                'span[data-e2e="browser-nickname"] > span:last-child'
            ).inner_text()
        except:
            fecha_publicacion = None

        # --- likes ---
        try:
            likes = page.locator('strong[data-e2e="like-count"]').inner_text()
        except:
            likes = None

        # --- comentarios ---
        try:
            comentarios = page.locator('strong[data-e2e="comment-count"]').inner_text()
        except:
            comentarios = None

        browser.close()

    return {
        'autor_contenido': autor_contenido,
        'likes': likes,
        'comentarios': comentarios,
        'compartidos': None,
        'visitas': None,
        'fecha_publicacion': fecha_publicacion,
        'tipo_contenido': None,
    }

