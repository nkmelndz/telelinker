
from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import SessionRevokedError, AuthKeyUnregisteredError


class TelegramService:
    def __init__(self, session_path, api_id, api_hash):
        try:
            # No iniciar sesión automáticamente; solo crear el cliente
            self.client = TelegramClient(session_path, api_id, api_hash)
        except (SessionRevokedError, AuthKeyUnregisteredError):
            pass  # Silenciar completamente el error

    def start(self):
        try:
            self.client.start()
        except (SessionRevokedError, AuthKeyUnregisteredError):
            pass  # Silenciar completamente el error

    def iter_group_messages(self, group_username):
        try:
            return self.client.iter_messages(group_username)
        except (SessionRevokedError, AuthKeyUnregisteredError):
            return []  # Silenciar completamente el error
    
    def iter_user_dialogs(self, ):
        try:
            return self.client.iter_dialogs()
        except (SessionRevokedError, AuthKeyUnregisteredError):
            return []  # Silenciar completamente el error

    def disconnect(self):
        try:
            self.client.disconnect()
        except Exception:
            pass
