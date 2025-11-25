import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

STARS_API_KEY = os.getenv('STARS_API_KEY', '')
CRYPTOPAY_API_KEY = os.getenv('CRYPTOPAY_API_KEY', '')
XROCKET_API_KEY = os.getenv('XROCKET_API_KEY', '')
MONETAG_SDK_KEY = os.getenv('MONETAG_SDK_KEY', '')

COUNTRIES = [
    'United States', 'United Kingdom', 'Canada', 'Australia', 'Germany',
    'France', 'Spain', 'Italy', 'Brazil', 'India', 'China', 'Japan',
    'Russia', 'Mexico', 'South Korea', 'Indonesia', 'Netherlands',
    'Turkey', 'Saudi Arabia', 'Switzerland', 'Other'
]

CATEGORIES = [
    'Technology', 'Business', 'Entertainment', 'Sports', 'Education',
    'Health', 'Finance', 'Travel', 'Food', 'Fashion', 'Gaming',
    'News', 'Music', 'Art', 'Science', 'Lifestyle'
]

PRIORITY_SLOT_PRICES = {
    'time_1h': 5.0,
    'time_6h': 25.0,
    'time_12h': 45.0,
    'time_24h': 80.0,
    'count_5': 10.0,
    'count_10': 18.0,
    'count_25': 40.0,
    'count_50': 70.0,
}

ADMIN_USER_IDS = [int(os.getenv('ADMIN_USER_ID', '0'))] if os.getenv('ADMIN_USER_ID') else []

FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000
