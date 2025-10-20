from .linkedin import scrap as scrap_linkedin
from .devto import scrap as scrap_devto
from .youtube import scrap as scrap_youtube
from .medium import scrap as scrap_medium
from .instagram import scrap as scrap_instagram
from .tiktok import scrap as scrap_tiktok

SCRAPERS = {
    'LinkedIn': scrap_linkedin,
    'Dev.to': scrap_devto,
    'YouTube': scrap_youtube,
    'Medium': scrap_medium,
    'Instagram': scrap_instagram,
    'TikTok': scrap_tiktok,
}
