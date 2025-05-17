from abc import ABC, abstractmethod
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update

class VFSBot(ABC):
    def __init__(self, config: dict, telegram_token: str, user_agent: str, headless: bool):
        self.cfg = config
        self.user_agent = user_agent
        self.headless = headless
        self.driver = None

        # Telegram application setup
        self.application = Application.builder().token(telegram_token).build()

        # Parameters for appointment search, can be set externally before run
        self.params = {}

    async def setup_driver(self):
        opts = uc.ChromeOptions()
        
        # Use --headless=new if headless is enabled (recommended for Chrome 109+)
        if self.headless:
            opts.add_argument('--headless=new')

        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument(f'--user-agent={self.user_agent}')
        
        # Do NOT use deprecated options:
        # opts.add_experimental_option('excludeSwitches', ['enable-automation'])
        # opts.add_experimental_option('useAutomationExtension', False)

        # Start undetected_chromedriver with options
        self.driver = uc.Chrome(options=opts)

        # Optional: Hide 'webdriver' property for stealth
        self.driver.execute_cdp_cmd(
            'Page.addScriptToEvaluateOnNewDocument',
            {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'}
        )


    def quit_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    async def handle_cloudflare(self):
        try:
            WebDriverWait(self.driver, 30).until_not(
                EC.presence_of_element_located((By.ID, 'cf-challenge-running'))
            )
        except:
            pass

    async def notify_admin(self, message: str):
        admin_chat_id = self.cfg.get('admin_chat_id')
        if admin_chat_id:
            await self.application.bot.send_message(chat_id=admin_chat_id, text=message)

    def run(self):
        self.add_handlers()
        self.application.run_polling(stop_signals=None)

    def add_handlers(self):
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(CommandHandler('check', self.command_check))
        # Add more handlers if needed

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Hello! Bot started. Use /check to look for appointments.")

    async def command_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Checking for appointment slots...")
        try:
            await self.setup_driver()
            self.login_flow()
            dates = self.check_for_appointment(self.params)
            if dates:
                await update.message.reply_text(f"Slots available: {dates}")
            else:
                await update.message.reply_text("No slots found.")
        except Exception as e:
            await update.message.reply_text(f"Error occurred: {e}")
        finally:
            self.quit_driver()

    def login_flow(self):
        self.driver.get(self.cfg['login_url'])
        self.handle_cloudflare()
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
