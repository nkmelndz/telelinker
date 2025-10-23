from telethon.sync import TelegramClient

class TelegramService:
    def __init__(self, session_name, api_id, api_hash):
        self.client = TelegramClient(session_name, api_id, api_hash)
        self.client.start()

    def iter_group_messages(self, group_username):
        return self.client.iter_messages(group_username)
    
    def iter_user_dialogs(self, ):
        return self.client.iter_dialogs()

    def disconnect(self):
        self.client.disconnect()
