"""xRocket Pay API Integration"""
import requests
import json
from config.settings import XROCKET_API_KEY
from config.database import get_supabase_client

class XRocketPayService:
    """Handle xRocket payment processing"""
    
    def __init__(self):
        self._db = None
        self.api_key = XROCKET_API_KEY
        self.api_url = "https://pay.xrocket.tg"
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_supabase_client()
        return self._db
    
    def get_headers(self):
        """Get request headers with API key"""
        if not self.api_key:
            print("WARNING: xRocket API key not configured")
        return {
            'Rocket-Pay-Key': self.api_key if self.api_key else '',
            'Content-Type': 'application/json'
        }
    
    def get_version(self):
        """Get API version"""
        try:
            url = f"{self.api_url}/version"
            response = requests.get(url)
            return response.json().get('version')
        except Exception as e:
            print(f"Error getting xRocket version: {e}")
            return None
    
    def get_app_info(self):
        """Get application info"""
        try:
            url = f"{self.api_url}/app/info"
            response = requests.get(url, headers=self.get_headers())
            return response.json()
        except Exception as e:
            print(f"Error getting app info: {e}")
            return None
    
    def create_invoice(self, amount, description, slot_id, num_payments=1):
        """
        Create Telegram invoice via xRocket
        
        Args:
            amount: Amount in USD or other currency
            description: Invoice description
            slot_id: Priority slot ID
            num_payments: Number of payments allowed (default 1)
        """
        try:
            url = f"{self.api_url}/tg-invoices"
            
            data = {
                'amount': float(amount),
                'description': description[:1024],
                'numPayments': num_payments,
            }
            
            headers = self.get_headers()
            
            print(f"xRocket: Creating invoice with URL: {url}")
            print(f"xRocket: Headers: {headers}")
            print(f"xRocket: Data: {data}")
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            
            print(f"xRocket: Response status: {response.status_code}")
            print(f"xRocket: Response text: {response.text}")
            
            result = response.json()
            
            print(f"xRocket: Parsed result: {result}")
            
            # Handle different response formats
            if result.get('status') == 'success':
                invoice = result.get('data', {})
                return {
                    'invoice_id': invoice.get('id'),
                    'invoice_url': invoice.get('url'),
                    'amount': invoice.get('amount'),
                    'status': invoice.get('status'),
                }
            elif isinstance(result, dict) and 'id' in result:
                # Direct invoice object response
                return {
                    'invoice_id': result.get('id'),
                    'invoice_url': result.get('url'),
                    'amount': result.get('amount'),
                    'status': result.get('status', 'active'),
                }
            else:
                print(f"Error creating xRocket invoice - unexpected response format: {result}")
                return None
        except Exception as e:
            print(f"Error creating xRocket invoice: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_invoice(self, invoice_id):
        """Get invoice details"""
        try:
            url = f"{self.api_url}/tg-invoices/{invoice_id}"
            response = requests.get(url, headers=self.get_headers())
            result = response.json()
            
            if result.get('status') == 'success':
                return result.get('data')
            return None
        except Exception as e:
            print(f"Error getting xRocket invoice: {e}")
            return None
    
    def get_invoices(self, status=None, limit=100):
        """Get list of invoices"""
        try:
            url = f"{self.api_url}/tg-invoices"
            params = {'limit': limit}
            if status:
                params['status'] = status
            
            response = requests.get(url, params=params, headers=self.get_headers())
            result = response.json()
            
            if result.get('status') == 'success':
                return result.get('data', [])
            return None
        except Exception as e:
            print(f"Error getting xRocket invoices: {e}")
            return None
    
    def delete_invoice(self, invoice_id):
        """Delete invoice"""
        try:
            url = f"{self.api_url}/tg-invoices/{invoice_id}"
            response = requests.delete(url, headers=self.get_headers())
            result = response.json()
            return result.get('status') == 'success'
        except Exception as e:
            print(f"Error deleting xRocket invoice: {e}")
            return False
