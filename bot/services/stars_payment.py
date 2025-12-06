"""Telegram Stars Payment Integration"""
import requests
from config.settings import TELEGRAM_BOT_TOKEN
from config.database import get_supabase_client

# Telegram Stars exchange rate: 100 XTR = $1.30 USD
# So 1 USD = 100/1.30 ≈ 76.92 stars
STARS_PER_USD = 77  # 100 stars / $1.30

class StarsPaymentService:
    """Handle Telegram Stars payments via bot API"""
    
    def __init__(self):
        self._db = None
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_supabase_client()
        return self._db
    
    def send_invoice(self, user_id, slot_id, title, description, amount_usd, payload=None):
        """
        Send invoice to user for priority slot purchase
        amount_usd: Price in USD (will be converted to Stars)
        """
        try:
            if payload is None:
                payload = f"slot_{slot_id}"
            
            # Convert USD to Telegram Stars (100 XTR ≈ $1 USD)
            amount_stars = int(amount_usd * STARS_PER_USD)
            
            url = f"{self.api_url}/sendInvoice"
            
            data = {
                'chat_id': user_id,
                'title': title,
                'description': description,
                'payload': payload,
                'currency': 'XTR',
                'prices': [{'label': title, 'amount': amount_stars}],
                'provider_token': '',  # Empty for digital goods with Telegram Stars
            }
            
            response = requests.post(url, json=data)
            result = response.json()
            
            if result.get('ok'):
                return result.get('result')
            else:
                print(f"Error sending invoice: {result.get('description')}")
                return None
        except Exception as e:
            print(f"Error sending Stars invoice: {e}")
            return None
    
    def handle_pre_checkout_query(self, bot, pre_checkout_query_id, ok=True, error_message=None):
        """
        Approve or decline pre-checkout query
        This is called when user taps Pay button
        """
        try:
            url = f"{self.api_url}/answerPreCheckoutQuery"
            
            data = {
                'pre_checkout_query_id': pre_checkout_query_id,
                'ok': ok,
            }
            
            if not ok and error_message:
                data['error_message'] = error_message
            
            response = requests.post(url, json=data)
            return response.json().get('ok', False)
        except Exception as e:
            print(f"Error handling pre-checkout query: {e}")
            return False
    
    def process_successful_payment(self, user_id, successful_payment):
        """
        Process successful payment update
        Called when user successfully pays invoice
        successful_payment contains: telegram_payment_charge_id, provider_payment_charge_id, currency, total_amount, invoice_payload
        """
        try:
            payment_data = {
                'user_id': user_id,
                'gateway': 'telegram_stars',
                'transaction_id': successful_payment.get('telegram_payment_charge_id'),
                'amount': successful_payment.get('total_amount') / 100,  # Convert to proper units
                'currency': successful_payment.get('currency'),
                'status': 'completed',
                'payload': successful_payment.get('invoice_payload')
            }
            return payment_data
        except Exception as e:
            print(f"Error processing successful Stars payment: {e}")
            return None
