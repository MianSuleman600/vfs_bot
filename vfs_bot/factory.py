import importlib
from utils.config_reader import load_country_config, load_global_settings
from notification.notification_factory import NotificationFactory


class VFSBotFactory:
    @staticmethod
    def get_bot(country_code: str):
        # Load global and country-specific configs
        global_cfg = load_global_settings()
        country_cfg = load_country_config(country_code)

        # Set up the Telegram notification channel using .env values
        telegram = NotificationFactory.get_channel(
            'telegram',
            token=global_cfg['telegram_token'],
            admin_chat_id=global_cfg['admin_chat_id']
        )

        # Dynamically import the country-specific bot class
        module_name = f"vfs_bot.bots.{country_code.lower()}"
        class_name = f"VFSBot{country_code.upper()}"

        try:
            mod = importlib.import_module(module_name)
            BotClass = getattr(mod, class_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Could not import bot class '{class_name}' from '{module_name}': {e}")

        # Instantiate the bot with its configuration and dependencies
        bot = BotClass(
        config=country_cfg,
        telegram_token=global_cfg['telegram_token'],  # pass token string, not client
        user_agent=global_cfg['user_agent'],
        headless=global_cfg['headless']
    )

        return bot
