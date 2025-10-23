

import sys
import os
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)
from scrapers.instagram import scrap

if __name__ == "__main__":
    url = input("URL de publicación de Instagram: ").strip()
    result = scrap(url)
    print("Resultado:")
    for k, v in result.items():
        print(f"{k}: {v}")
