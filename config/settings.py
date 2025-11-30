import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Domain detection - priority: WEBHOOK_URL (Render) > RENDER_EXTERNAL_URL > REPLIT_DOMAINS > fallback
def _get_app_domain():
    webhook = os.getenv('WEBHOOK_URL', '').strip()
    if webhook:
        return webhook.rstrip('/')
    
    render_url = os.getenv('RENDER_EXTERNAL_URL', '').strip()
    if render_url:
        return render_url.rstrip('/')
    
    replit_domains = os.getenv('REPLIT_DOMAINS', '').strip()
    if replit_domains:
        domain = replit_domains.split(',')[0].strip()
        return f'https://{domain}'
    
    return 'https://localhost:5000'  # Fallback - Telegram requires HTTPS

APP_DOMAIN = _get_app_domain()

STARS_API_KEY = os.getenv('STARS_API_KEY', '')
CRYPTOPAY_API_KEY = os.getenv('CRYPTOPAY_API_KEY', '')
XROCKET_API_KEY = os.getenv('XROCKET_API_KEY', '')
MONETAG_SDK_KEY = os.getenv('MONETAG_SDK_KEY', '')
MONETAG_ZONE = '10243712'  # Zone ID from SDK
MONETAG_SDK_FUNC = 'show_10243712'  # SDK function name

COUNTRIES = [
    'Sri Lanka', 'United States', 'United Kingdom', 'Canada', 'Australia', 'Germany',
    'France', 'Spain', 'Italy', 'Brazil', 'India', 'China', 'Japan',
    'Russia', 'Mexico', 'South Korea', 'Indonesia', 'Netherlands',
    'Turkey', 'Saudi Arabia', 'Switzerland', 'Pakistan', 'Bangladesh',
    'Philippines', 'Vietnam', 'Thailand', 'Malaysia', 'Singapore', 'Other'
]

CATEGORIES = [
    'Technology', 'Business', 'Entertainment', 'Sports', 'Education',
    'Health', 'Finance', 'Travel', 'Food', 'Fashion', 'Gaming',
    'News', 'Music', 'Art', 'Science', 'Lifestyle', 'Crypto',
    'Marketing', 'Real Estate', 'Automotive'
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
