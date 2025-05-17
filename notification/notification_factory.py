from .email_client import EmailClient
from .telegram_client import TelegramClient

class NotificationFactory:
    @staticmethod
    def get_channel(name: str, **kwargs):
        if name == 'email':
            return EmailClient(**kwargs)
        elif name == 'telegram':
            return TelegramClient(**kwargs)
        else:
            raise ValueError(f"Unknown notification channel: {name}")