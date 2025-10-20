import yt_dlp

def get_video_info(url):
    ydl_opts = {
        'extract_flat': False,  # Necesario para obtener metadata completa
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        return {
            'titulo': info.get('title'),
            'canal': info.get('uploader'),
            'vistas': info.get('view_count', 0),
            'likes': info.get('like_count', 0),
            'comentarios': info.get('comment_count', 0),  # ← Cantidad de comentarios
            'fecha_publicacion': info.get('upload_date'),
            'duracion': info.get('duration', 0)
        }

if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=fDxWDVqJFn8"
    resultado = get_video_info(url)
    print("\nResultado:")
    for k, v in resultado.items():
        print(f"{k}: {v}")

