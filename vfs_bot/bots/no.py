from vfs_bot.base import VFSBot
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class VFSBotNO(VFSBot):
    def pre_login_steps(self):
        # Dismiss cookie banner if shown
        try:
            btn = self.driver.find_element(By.ID, 'onetrust-reject-all-handler')
            btn.click()
        except:
            pass

    def login(self):
        sel = self.cfg['selectors']
        creds = self.cfg['credentials']

        WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located((By.ID, sel['email']))
        ).send_keys(creds['email'])
        
        self.driver.find_element(By.ID, sel['password']).send_keys(creds['password'])
        self.driver.find_element(By.XPATH, sel['sign_in_button']).click()

    def post_login_steps(self):
        # Click "Start New Booking"
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, self.cfg['selectors']['start_new_booking']))
        ).click()

    def check_for_appointment(self, parameters: dict) -> list:
        sel = self.cfg['selectors']

        # Select dropdowns
        for key, dropdown_id in (
            ('visa_center', sel['visa_centre_dropdown']),
            ('visa_category', sel['visa_category_dropdown']),
            ('visa_sub_category', sel['visa_subcategory_dropdown']),
        ):
            self.driver.find_element(By.ID, dropdown_id).click()
            xpath = f"//mat-option[.//span[text()='{parameters[key]}']]"
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            ).click()

        # Wait for calendar and collect available dates
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, sel['calendar_selector']))
        )
        cal = self.driver.find_element(By.CSS_SELECTOR, sel['calendar_selector'])
        dates = [el.text for el in cal.find_elements(By.CSS_SELECTOR, sel['available_date_selector'])]
        return dates
