import os
import yaml
from dotenv import load_dotenv

# Load from .env file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

def load_global_settings():
    return {
        'telegram_token': os.getenv('TELEGRAM_TOKEN'),
        'admin_chat_id': os.getenv('ADMIN_CHAT_ID'),
        'user_agent': os.getenv('USER_AGENT'),
        'headless': os.getenv('HEADLESS', 'False').lower() == 'true',
        'smtp': {
            'host': os.getenv('SMTP_HOST'),
            'port': int(os.getenv('SMTP_PORT')),
            'user': os.getenv('SMTP_USER'),
            'password': os.getenv('SMTP_PASSWORD'),
        }
    }

def load_country_config(country_code: str) -> dict:
    config_path = os.path.join(BASE_DIR, 'config', 'countries.yml')
    
    with open(config_path, 'r') as f:
        all_configs = yaml.safe_load(f)

    country_code = country_code.upper()
    if country_code not in all_configs:
        raise ValueError(f"No configuration found for country code: {country_code}")
    return all_configs[country_code]
