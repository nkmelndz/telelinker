
def get_video_info(url):
    with yt_dlp.YoutubeDL() as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            'titulo': info['title'],
            'canal': info['uploader'],
            'vistas': info.get('view_count', 0),
            'likes': info.get('like_count', 0),
            'fecha_publicacion': info['upload_date'],
            'duracion': info['duration']
        }

if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=jegJEDH_eWU"
    resultado = get_video_info(url)
    print("\nResultado:")
    for k, v in resultado.items():
        print(f"{k}: {v}")

