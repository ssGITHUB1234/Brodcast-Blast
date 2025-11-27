"""Crypto Pay Bot Integration"""
import requests
import json
from config.settings import CRYPTOPAY_API_KEY
from config.database import get_supabase_client

class CryptoPayService:
    """Handle CryptoPay Bot payments"""
    
    def __init__(self):
        self._db = None
        self.api_key = CRYPTOPAY_API_KEY
        self.api_url = "https://pay.crypt.bot/api"
        self.testnet_url = "https://testnet-pay.crypt.bot/api"  # For testing
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_supabase_client()
        return self._db
    
    def get_headers(self):
        """Get request headers with API token"""
        return {
            'Crypto-Pay-API-Token': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def test_connection(self):
        """Test API connection"""
        try:
            url = f"{self.api_url}/getMe"
            response = requests.get(url, headers=self.get_headers())
            result = response.json()
            return result.get('ok', False)
        except Exception as e:
            print(f"Error testing CryptoPay connection: {e}")
            return False
    
    def create_invoice(self, amount, description, slot_id, asset='USDT', currency_type='crypto'):
        """
        Create invoice for priority slot
        
        Args:
            amount: Amount in crypto or fiat
            description: Invoice description
            slot_id: Priority slot ID
            asset: Cryptocurrency (USDT, TON, BTC, ETH, LTC, BNB, TRX, USDC)
            currency_type: 'crypto' or 'fiat'
        """
        try:
            url = f"{self.api_url}/createInvoice"
            
            data = {
                'amount': str(amount),
                'description': description[:1024],
                'payload': f"slot_{slot_id}",
                'allow_comments': False,
                'allow_anonymous': True,
                'expires_in': 3600,  # 1 hour expiration
            }
            
            if currency_type == 'crypto':
                data['asset'] = asset
            else:
                data['fiat'] = asset
            
            response = requests.post(url, json=data, headers=self.get_headers())
            result = response.json()
            
            if result.get('ok'):
                invoice = result.get('result', {})
                return {
                    'invoice_id': invoice.get('invoice_id'),
                    'bot_invoice_url': invoice.get('bot_invoice_url'),
                    'web_app_invoice_url': invoice.get('web_app_invoice_url'),
                    'mini_app_invoice_url': invoice.get('mini_app_invoice_url'),
                }
            else:
                print(f"Error creating CryptoPay invoice: {result.get('error')}")
                return None
        except Exception as e:
            print(f"Error creating CryptoPay invoice: {e}")
            return None
    
    def get_invoice(self, invoice_id):
        """Get invoice details"""
        try:
            url = f"{self.api_url}/getInvoices"
            params = {'invoice_ids': str(invoice_id)}
            
            response = requests.get(url, params=params, headers=self.get_headers())
            result = response.json()
            
            if result.get('ok'):
                invoices = result.get('result', [])
                return invoices[0] if invoices else None
            return None
        except Exception as e:
            print(f"Error getting CryptoPay invoice: {e}")
            return None
    
    def get_balance(self):
        """Get app balance"""
        try:
            url = f"{self.api_url}/getBalance"
            response = requests.get(url, headers=self.get_headers())
            result = response.json()
            
            if result.get('ok'):
                return result.get('result', [])
            return None
        except Exception as e:
            print(f"Error getting CryptoPay balance: {e}")
            return None
    
    def get_exchange_rates(self):
        """Get exchange rates"""
        try:
            url = f"{self.api_url}/getExchangeRates"
            response = requests.get(url, headers=self.get_headers())
            result = response.json()
            
            if result.get('ok'):
                return result.get('result', [])
            return None
        except Exception as e:
            print(f"Error getting exchange rates: {e}")
            return None
