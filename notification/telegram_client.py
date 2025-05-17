from telegram import Bot

class TelegramClient:
    def __init__(self, token: str, admin_chat_id: str):
        self.bot = Bot(token)
        self.admin_id = admin_chat_id

    def send(self, chat_id: str, text: str):
        self.bot.send_message(chat_id=chat_id, text=text)

    def notify_admin(self, text: str):
        self.send(self.admin_id, text)