"""Telegram Wallet Payment Integration"""
import requests
from config.settings import TELEGRAM_BOT_TOKEN
from config.database import get_supabase_client

class TelegramWalletService:
    """Handle Telegram Wallet payments via bot API"""
    
    def __init__(self):
        self._db = None
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_supabase_client()
        return self._db
    
    def send_invoice(self, user_id, slot_id, title, description, amount, payload=None):
        """
        Send invoice to user for priority slot purchase via Telegram Wallet
        Amount is in cents (smallest currency unit)
        """
        try:
            if payload is None:
                payload = f"slot_{slot_id}"
            
            url = f"{self.api_url}/sendInvoice"
            
            # Convert dollar amount to cents
            amount_cents = int(amount * 100)
            
            data = {
                'chat_id': user_id,
                'title': title,
                'description': description,
                'payload': payload,
                'currency': 'USD',  # Telegram Wallet uses USD
                'prices': [{'label': title, 'amount': amount_cents}],
                'provider_token': '',  # Empty for Telegram Wallet (uses native wallet)
            }
            
            response = requests.post(url, json=data)
            result = response.json()
            
            if result.get('ok'):
                print(f"Telegram Wallet invoice sent successfully to user {user_id}")
                return result.get('result')
            else:
                print(f"Error sending Telegram Wallet invoice: {result.get('description')}")
                return None
        except Exception as e:
            print(f"Error sending Telegram Wallet invoice: {e}")
            return None
    
    def handle_pre_checkout_query(self, bot, pre_checkout_query_id, ok=True, error_message=None):
        """
        Approve or decline pre-checkout query
        Called when user taps Pay button
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
        """
        try:
            payment_data = {
                'user_id': user_id,
                'gateway': 'telegram_wallet',
                'transaction_id': successful_payment.get('telegram_payment_charge_id'),
                'amount': successful_payment.get('total_amount') / 100,  # Convert from cents
                'currency': successful_payment.get('currency', 'USD'),
                'status': 'completed',
                'payload': successful_payment.get('invoice_payload')
            }
            return payment_data
        except Exception as e:
            print(f"Error processing successful Telegram Wallet payment: {e}")
            return None
