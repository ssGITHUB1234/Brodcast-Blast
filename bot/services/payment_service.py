import hmac
import hashlib
import json
from datetime import datetime, timedelta
from config.database import get_supabase_client
from config.settings import CRYPTOPAY_API_KEY, XROCKET_API_KEY

INVOICE_EXPIRY_MINUTES = 5

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
    
    def get_expired_pending_payments(self):
        """Get pending payments older than 5 minutes"""
        try:
            expiry_time = datetime.utcnow() - timedelta(minutes=INVOICE_EXPIRY_MINUTES)
            expiry_str = expiry_time.isoformat()
            
            response = self.db.table('payments').select('*').eq('status', 'pending').lt('timestamp', expiry_str).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting expired payments: {e}")
            return []
    
    def expire_pending_payment(self, payment_id):
        """Mark a payment as expired and delete associated slot"""
        try:
            response = self.db.table('payments').update({'status': 'expired'}).eq('payment_id', payment_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error expiring payment: {e}")
            return None
    
    def delete_pending_slot(self, slot_id):
        """Delete a pending (unpaid) priority slot"""
        try:
            self.db.table('priority_slots').delete().eq('slot_id', slot_id).eq('payment_status', 'pending').execute()
            return True
        except Exception as e:
            print(f"Error deleting pending slot: {e}")
            return False
    
    def cleanup_expired_invoices(self):
        """Cleanup expired pending payments and their slots"""
        try:
            expired_payments = self.get_expired_pending_payments()
            cleaned_count = 0
            
            for payment in expired_payments:
                slot_id = payment.get('slot_id')
                payment_id = payment.get('payment_id')
                
                self.expire_pending_payment(payment_id)
                
                if slot_id:
                    self.delete_pending_slot(slot_id)
                
                cleaned_count += 1
                print(f"Expired invoice cleaned: payment_id={payment_id}, slot_id={slot_id}")
            
            if cleaned_count > 0:
                print(f"Cleaned up {cleaned_count} expired invoice(s)")
            
            return cleaned_count
        except Exception as e:
            print(f"Error cleaning up expired invoices: {e}")
            return 0
