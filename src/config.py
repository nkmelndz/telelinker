# ...existing code...
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID: int | None
    API_HASH: str | None
    SESSION_NAME: str
    GROUP_USERNAME: str | int

    DB_HOST: str | None
    DB_NAME: str | None
    DB_USER: str | None
    DB_PASSWORD: str | None

    def __init__(self):
        api_id_raw = os.getenv('API_ID')
        self.API_ID = int(api_id_raw) if api_id_raw and api_id_raw.isdigit() else None
        self.API_HASH = os.getenv('API_HASH')
        self.SESSION_NAME = os.getenv('SESSION_NAME', 'session')
        g = os.getenv('GROUP_USERNAME')
        self.GROUP_USERNAME = int(g) 
        self.DB_HOST = os.getenv('DB_HOST')
        self.DB_NAME = os.getenv('DB_NAME')
        self.DB_USER = os.getenv('DB_USER')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD')

    def validate(self):
        missing = []
        if not self.API_ID or not self.API_HASH:
            missing.append('API_ID/API_HASH')
        if not self.GROUP_USERNAME:
            missing.append('GROUP_USERNAME')
        if missing:
            raise RuntimeError(f"Variables obligatorias faltantes: {', '.join(missing)}")

def get_config() -> Config:
    cfg = Config()
    cfg.validate()
    return cfg
# ...existing code...