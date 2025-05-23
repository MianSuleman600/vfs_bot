import importlib
import logging
from utils.config_reader import load_country_config, load_global_settings

logger = logging.getLogger(__name__)

class VFSBotFactory:
    @staticmethod
    def get_bot(country_code: str):
        """
        Factory method to initialize the appropriate VFSBot subclass
        for the given country code.
        """
        logger.info(f"Initializing VFS bot for country: {country_code}")

        # Load global and country-specific configurations
        global_cfg = load_global_settings()
        country_cfg = load_country_config(country_code)

        if not country_cfg:
            raise ValueError(f"No configuration found for country code: '{country_code}'")

        # Optional user agent (can be None for random)
        user_agent = global_cfg.get('user_agent')

        # Convert headless to bool (default to True)
        headless_raw = global_cfg.get('headless', 'true')
        headless = str(headless_raw).strip().lower() in ['1', 'true', 'yes']

        # Telegram token (must be present)
        telegram_token = global_cfg.get('telegram_token')
        if not telegram_token:
            raise ValueError("Missing 'telegram_token' in global configuration.")

        # Dynamically import the correct bot class
        module_name = f"vfs_bot.bots.{country_code.lower()}"
        class_name = f"VFSBot{country_code.upper()}"

        try:
            mod = importlib.import_module(module_name)
            BotClass = getattr(mod, class_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(
                f"Could not import bot class '{class_name}' from module '{module_name}': {e}"
            )

        # Instantiate and return the bot
        try:
            bot = BotClass(
                config=country_cfg,
                telegram_token=telegram_token,
                user_agent=user_agent,
                headless=headless
            )
        except TypeError as e:
            raise TypeError(
                f"Error initializing bot class '{class_name}': {e}. "
                f"Check if the constructor supports all required arguments."
            )

        logger.info(f"Bot '{class_name}' initialized successfully.")
        return bot
