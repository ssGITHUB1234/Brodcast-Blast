import hmac
import hashlib
import json
from config.database import get_supabase_client
from config.settings import CRYPTOPAY_API_KEY, XROCKET_API_KEY

class PaymentService:
    """Base payment service for handling all payment operations"""
    
    def __init__(self):
        self._db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_supabase_client()
        return self._db
    
    def record_payment(self, user_id, slot_id, amount, gateway, transaction_id, status='pending'):
        """Record a payment in the database"""
        try:
            data = {
                'user_id': user_id,
                'slot_id': slot_id,
                'amount': amount,
                'gateway': gateway,
                'transaction_id': transaction_id,
                'status': status
            }
            response = self.db.table('payments').insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error recording payment: {e}")
            return None
    
    def update_payment_status(self, transaction_id, status):
        """Update payment status"""
        try:
            response = self.db.table('payments').update({'status': status}).eq('transaction_id', transaction_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating payment status: {e}")
            return None
    
    def get_payment_by_transaction(self, transaction_id):
        """Get payment by transaction ID"""
        try:
            response = self.db.table('payments').select('*').eq('transaction_id', transaction_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting payment: {e}")
            return None
    
    def verify_cryptopay_webhook(self, body, signature):
        """Verify CryptoPay webhook signature"""
        try:
            secret = hashlib.sha256(CRYPTOPAY_API_KEY.encode()).digest()
            expected_signature = hmac.new(
                secret, 
                body.encode() if isinstance(body, str) else body, 
                hashlib.sha256
            ).hexdigest()
            return expected_signature == signature
        except Exception as e:
            print(f"Error verifying CryptoPay webhook: {e}")
            return False
    
    def verify_xrocket_webhook(self, body, signature):
        """Verify xRocket webhook signature"""
        try:
            secret = hashlib.sha256(XROCKET_API_KEY.encode()).digest()
            expected_signature = hmac.new(
                secret, 
                body.encode() if isinstance(body, str) else body, 
                hashlib.sha256
            ).hexdigest()
            return expected_signature == signature
        except Exception as e:
            print(f"Error verifying xRocket webhook: {e}")
            return False
