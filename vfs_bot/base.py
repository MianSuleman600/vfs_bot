from abc import ABC, abstractmethod
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
from fake_useragent import UserAgent
from telegram.request import HTTPXRequest
import logging
import sys

# Setup logging to console with DEBUG level
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

class VFSBot(ABC):
    def __init__(self, config: dict, telegram_token: str, user_agent: str, headless: True):
        if config is None:
            raise ValueError("Config cannot be None.")
        self.cfg = config
        logger.debug(f"Config keys: {list(self.cfg.keys())}")
        self.user_agent = user_agent
        self.headless = headless
        self.driver = None

        request = None
        try:
            if self.cfg.get("use_proxy") and self.cfg.get("proxy_url"):
                proxy_url = self.cfg.get("proxy_url")
                logger.debug(f"Attempting to use SOCKS5 proxy: {proxy_url}")
                request = HTTPXRequest(proxy=proxy_url)
                logger.debug("HTTPXRequest with proxy successfully created.")
            else:
                logger.debug("Proxy not enabled or proxy_url missing, not using proxy.")
        except Exception as e:
            logger.error(f"Exception while creating HTTPXRequest with proxy: {e}", exc_info=True)

        try:
            builder = ApplicationBuilder().token(telegram_token)
            if request:
                builder = builder.request(request)
            self.application = builder.build()
            logger.debug("Telegram Application successfully built.")
        except Exception as e:
            logger.error(f"Exception while building Telegram Application: {e}", exc_info=True)
            raise

        self.params = {}

    async def setup_driver(self):
        self.user_agent = UserAgent().random
        opts = uc.ChromeOptions()

        if self.headless:
            opts.add_argument('--headless=new')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument('--window-size=1920,1080')
        opts.add_argument(f'--user-agent={self.user_agent}')

        try:
            self.driver = uc.Chrome(options=opts)
            self.driver.execute_cdp_cmd(
                'Page.addScriptToEvaluateOnNewDocument',
                {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'}
            )
            logger.debug("Chrome WebDriver successfully initialized.")
        except Exception as e:
            self.driver = None
            logger.error(f"Error launching Chrome: {e}", exc_info=True)

    def quit_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.debug("Chrome WebDriver closed.")

    async def notify_admin(self, message: str):
        admin_chat_id = self.cfg.get('admin_chat_id')
        if admin_chat_id:
            try:
                await self.application.bot.send_message(chat_id=admin_chat_id, text=message)
                logger.debug(f"Notification sent to admin: {message}")
            except Exception as e:
                logger.error(f"Failed to send notification to admin: {e}", exc_info=True)

    def run(self):
        self.add_handlers()
        logger.debug("Starting bot polling...")
        self.application.run_polling(stop_signals=None)

    def add_handlers(self):
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(CommandHandler('check', self.command_check))
        logger.debug("Telegram command handlers added.")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("✅ Bot started. Use /check to look for appointments.")

    async def command_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🔍 Checking for appointment slots...")
        try:
            await self.setup_driver()

            if not self.driver:
                await update.message.reply_text("❌ Failed to launch browser. Try again later.")
                return

            self.login_flow()
            dates = self.check_for_appointment(self.params)
            if dates:
                await update.message.reply_text(f"✅ Slots available: {dates}")
            else:
                await update.message.reply_text("❌ No slots found.")
        except Exception as e:
            logger.error(f"Error during /check command execution: {e}", exc_info=True)
            await update.message.reply_text(f"⚠️ Error occurred: {e}")
        finally:
            self.quit_driver()

    def login_flow(self):
        login_url = self.cfg.get('login_url')
        if not login_url:
            raise ValueError("Missing 'login_url' in country configuration.")

        self.driver.get(login_url)

        try:
            WebDriverWait(self.driver, 30).until_not(
                EC.presence_of_element_located((By.ID, 'cf-challenge-running'))
            )
            logger.debug("Cloudflare challenge passed or not detected.")
        except Exception as e:
            logger.warning(f"Cloudflare challenge wait timed out or failed: {e}")

        self.pre_login_steps()
        self.login()
        self.post_login_steps()

    @abstractmethod
    def pre_login_steps(self):
        pass

    @abstractmethod
    def login(self):
        pass

    @abstractmethod
    def post_login_steps(self):
        pass

    @abstractmethod
    def check_for_appointment(self, parameters: dict) -> list:
        pass
