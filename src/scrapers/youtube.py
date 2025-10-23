from src.utils.normalize_date import normalize_date

def scrap(url, config=None):
    import yt_dlp
    import contextlib, os, sys
    try:
        ydl_opts = {
            'extract_flat': False,
            'quiet': True,
        }
        with contextlib.redirect_stderr(open(os.devnull, 'w')):
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
            'fecha_publicacion': normalize_date(fecha_publicacion),
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
