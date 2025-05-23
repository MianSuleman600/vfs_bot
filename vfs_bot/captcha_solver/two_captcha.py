# captcha_solver/two_captcha.py

import time
import requests
from dotenv import load_dotenv
import os

from captcha_solver.base import CaptchaSolver

load_dotenv()  # Load .env variables

class TwoCaptchaSolver(CaptchaSolver):
    def __init__(self):
        self.api_key = os.getenv('API_KEY')
        self.poll_interval = int(os.getenv('POLL_INTERVAL', 5))

    def solve(self, sitekey: str, page_url: str) -> str:
        data = {
            'key': self.api_key,
            'method': 'turnstile',
            'sitekey': sitekey,
            'pageurl': page_url,
            'json': 1
        }
        response = requests.post('http://2captcha.com/in.php', data=data).json()
        if response.get('status') != 1:
            raise Exception(f"2Captcha submit error: {response.get('request')}")

        captcha_id = response['request']
        fetch_url = 'http://2captcha.com/res.php'
        params = {
            'key': self.api_key,
            'action': 'get',
            'id': captcha_id,
            'json': 1
        }

        while True:
            time.sleep(self.poll_interval)
            result = requests.get(fetch_url, params=params).json()
            if result.get('status') == 1:
                return result['request']
            if result.get('request') != 'CAPCHA_NOT_READY':
                raise Exception(f"2Captcha polling error: {result.get('request')}")
