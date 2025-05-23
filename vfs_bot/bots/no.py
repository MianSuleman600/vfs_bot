import os
import time
import logging
import re
from dotenv import load_dotenv

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from captcha_solver.two_captcha import TwoCaptchaSolver
from vfs_bot.base import VFSBot

logger = logging.getLogger(__name__)
load_dotenv()

class VFSBotNO(VFSBot):

    def pre_login_steps(self):
        """Handle cookie banner by clicking 'Accept Only Necessary' if present."""
        try:
            WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.ID, 'onetrust-reject-all-handler'))
            ).click()
            logger.info("Clicked 'Accept Only Necessary' for cookies.")
        except TimeoutException:
            logger.info("No cookie consent banner appeared.")

    def solve_captcha(self):
        """Solve Cloudflare Turnstile CAPTCHA using 2Captcha."""
        api_key = os.getenv("API_KEY")
        sitekey = os.getenv("SITEKEY")
        page_url = os.getenv("PAGE_URL")
        poll_interval = int(os.getenv("POLL_INTERVAL", 5))

        if not all([api_key, sitekey, page_url]):
            raise Exception("Missing .env values: API_KEY, SITEKEY, or PAGE_URL")

        logger.info("Solving CAPTCHA...")
        solver = TwoCaptchaSolver(api_key, poll_interval)
        token = solver.solve(sitekey, page_url)
        logger.info("CAPTCHA solved successfully.")

        self.driver.execute_script("""
            const textarea = document.querySelector('textarea[name="cf-turnstile-response"]');
            if (textarea) {
                textarea.value = arguments[0];
                const event = new Event('input', { bubbles: true });
                textarea.dispatchEvent(event);
            }
        """, token)
        time.sleep(2)

    def login(self):
        """Perform login using selectors and credentials from config with CAPTCHA solved first."""
        sel = self.cfg['selectors']
        creds = self.cfg['credentials']
        max_retries = 3

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Login attempt {attempt}...")
                WebDriverWait(self.driver, 40).until(
                    EC.presence_of_element_located((By.TAG_NAME, "form"))
                )
                self.solve_captcha()

                WebDriverWait(self.driver, 20).until(
                    EC.visibility_of_element_located((By.ID, sel['email']))
                ).send_keys(creds['email'])
                logger.info("Email entered.")

                WebDriverWait(self.driver, 20).until(
                    EC.visibility_of_element_located((By.ID, sel['password']))
                ).send_keys(creds['password'])
                logger.info("Password entered.")

                WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, sel['sign_in_button']))
                ).click()
                logger.info("Clicked sign-in button.")
                return

            except TimeoutException:
                logger.warning(f"Attempt {attempt} failed due to timeout.")

                if attempt == max_retries:
                    logger.error("Max login attempts reached. Login failed.")
                    raise
                else:
                    self.driver.refresh()
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )

    def post_login_steps(self):
        """Click the 'Start New Booking' button after logging in."""
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, self.cfg['selectors']['start_new_booking']))
        ).click()

    def check_for_appointment(self, parameters: dict) -> dict:
        """Check the calendar for available appointments and scrape the earliest slot date."""
        sel = self.cfg['selectors']
        dropdowns = [
            ('visa_center', sel['visa_centre_dropdown']),
            ('visa_category', sel['visa_category_dropdown']),
            ('visa_sub_category', sel['visa_subcategory_dropdown']),
        ]

        for i, (key, dropdown_id) in enumerate(dropdowns):
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, dropdown_id))
            ).click()

            option_xpath = f"//mat-option[.//span[text()='{parameters[key]}']]"
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, option_xpath))
            ).click()

            if i + 1 < len(dropdowns):
                next_dropdown_id = dropdowns[i + 1][1]
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, next_dropdown_id))
                )
            else:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, sel['calendar_selector']))
                )

        # Grab available dates from calendar
        cal = self.driver.find_element(By.CSS_SELECTOR, sel['calendar_selector'])
        dates = [el.text for el in cal.find_elements(By.CSS_SELECTOR, sel['available_date_selector'])]

        # Try to grab earliest slot from alert box
        try:
            earliest_alert = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.alert-info-blue.alert-info"))
            )
            alert_text = earliest_alert.text.strip()
            match = re.search(r"(\d{2}-\d{2}-\d{4})", alert_text)
            earliest_date = match.group(1) if match else None
        except TimeoutException:
            earliest_date = None

        return {
            "available_dates": dates,
            "earliest_date": earliest_date
        }
