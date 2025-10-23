def scrap(url, config=None):
    import requests
    from bs4 import BeautifulSoup
    try:
        resp = requests.get(url)
        if resp.status_code != 200:
            return {}
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Buscar metadatos en el HTML
        author = None
        date = None
        likes = None
        comments = None
        caption = None
        # Extraer datos de los meta tags
        for tag in soup.find_all('meta'):
            if tag.get('property') == 'og:description':
                caption = tag.get('content')
            if tag.get('property') == 'og:title':
                author = tag.get('content')
            if tag.get('property') == 'og:published_time':
                date = tag.get('content')
        # Likes y comentarios pueden estar en el caption
        if caption:
            import re
            likes_match = re.search(r'(\d+) Me gusta', caption)
            comments_match = re.search(r'(\d+) comentarios', caption)
            if likes_match:
                likes = int(likes_match.group(1))
            if comments_match:
                comments = int(comments_match.group(1))
        return {
            'author': author,
            'date': date,
            'likes': likes,
            'comments': comments,
            'shares': None,
            'views': None,
            'caption': caption,
        }
    except Exception:
        return {}
