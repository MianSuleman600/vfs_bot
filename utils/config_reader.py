import os
import yaml
from dotenv import load_dotenv
from typing import Dict, Any

# Calculate BASE_DIR relative to current file (assuming this script is inside a subdir)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env
load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

def load_global_settings() -> Dict[str, Any]:
    """Load global settings from environment variables."""
    try:
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
    except ValueError:
        smtp_port = 587

    return {
        'telegram_token': os.getenv('TELEGRAM_TOKEN'),
        'admin_chat_id': os.getenv('ADMIN_CHAT_ID'),
        'user_agent': os.getenv('USER_AGENT'),
        'headless': os.getenv('HEADLESS', 'False').lower() == 'true',
        'use_proxy': os.getenv('USE_PROXY', 'False').lower() == 'true',
        'proxy_url': os.getenv('PROXY_URL'),
        'smtp': {
            'host': os.getenv('SMTP_HOST'),
            'port': smtp_port,
            'user': os.getenv('SMTP_USER'),
            'password': os.getenv('SMTP_PASSWORD'),
        }
    }

def load_country_config(country_code: str) -> Dict[str, Any]:
    """Load country-specific configuration from YAML file."""
    config_path = os.path.join(BASE_DIR, 'config', 'countries.yml')

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at path: {config_path}")

    with open(config_path, 'r') as f:
        all_configs = yaml.safe_load(f)

    country_code = country_code.upper()
    if country_code not in all_configs:
        raise ValueError(f"No configuration found for country code: {country_code}")

    return all_configs[country_code]
