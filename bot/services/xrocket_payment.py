"""xRocket Payment Integration"""
import requests
import json
from config.settings import XROCKET_API_KEY
from config.database import get_supabase_client

class XRocketPaymentService:
    """Handle xRocket payments for crypto transactions"""
    
    def __init__(self):
        self._db = None
        self.api_key = XROCKET_API_KEY
        self.api_url = "https://pay.xrocket.tg"
        self.testnet_url = "https://dev-pay.xrocket.tg"
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_supabase_client()
        return self._db
    
    def get_headers(self):
        """Get request headers with API token"""
        return {
            'Rocket-Pay-Key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def test_connection(self):
        """Test API connection"""
        try:
            url = f"{self.api_url}/app/info"
            response = requests.get(url, headers=self.get_headers())
            result = response.json()
            return result.get('success', False)
        except Exception as e:
            print(f"Error testing xRocket connection: {e}")
            return False
    
    def create_invoice(self, amount, description, slot_id, currency='USDT', num_payments=1):
        """
        Create invoice for priority slot
        
        Args:
            amount: Amount to charge
            description: Invoice description
            slot_id: Priority slot ID
            currency: Cryptocurrency (TONCOIN, USDT, BTC, etc.)
            num_payments: Number of times invoice can be paid
        """
        try:
            url = f"{self.api_url}/tg-invoices"
            
            data = {
                'amount': float(amount),
                'currency': currency,
                'description': description[:200],
                'hiddenMessage': f"slot_{slot_id}",
                'callbackUrl': None,
                'payload': f"slot_{slot_id}",
                'numPayments': num_payments,
                'expiredIn': 3600
            }
            
            response = requests.post(url, json=data, headers=self.get_headers())
            result = response.json()
            
            if result.get('success'):
                invoice_data = result.get('data', {})
                return {
                    'invoice_id': str(invoice_data.get('id')),
                    'invoice_url': invoice_data.get('link'),
                    'amount': invoice_data.get('amount'),
                    'currency': invoice_data.get('currency'),
                    'status': invoice_data.get('status')
                }
            else:
                print(f"Error creating xRocket invoice: {result.get('message')}")
                return None
        except Exception as e:
            print(f"Error creating xRocket invoice: {e}")
            return None
    
    def get_invoice(self, invoice_id):
        """Get invoice details"""
        try:
            url = f"{self.api_url}/tg-invoices/{invoice_id}"
            response = requests.get(url, headers=self.get_headers())
            result = response.json()
            
            if result.get('success'):
                return result.get('data')
            return None
        except Exception as e:
            print(f"Error getting xRocket invoice: {e}")
            return None
    
    def get_currencies(self):
        """Get available currencies"""
        try:
            url = f"{self.api_url}/currencies/available"
            response = requests.get(url, headers=self.get_headers())
            result = response.json()
            
            if result.get('success'):
                return result.get('data', [])
            return None
        except Exception as e:
            print(f"Error getting xRocket currencies: {e}")
            return None
    
    def get_app_info(self):
        """Get app info and balance"""
        try:
            url = f"{self.api_url}/app/info"
            response = requests.get(url, headers=self.get_headers())
            result = response.json()
            
            if result.get('success'):
                return result.get('data')
            return None
        except Exception as e:
            print(f"Error getting xRocket app info: {e}")
            return None
    
    def delete_invoice(self, invoice_id):
        """Delete/cancel an invoice"""
        try:
            url = f"{self.api_url}/tg-invoices/{invoice_id}"
            response = requests.delete(url, headers=self.get_headers())
            result = response.json()
            return result.get('success', False)
        except Exception as e:
            print(f"Error deleting xRocket invoice: {e}")
            return False
