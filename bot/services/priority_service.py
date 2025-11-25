from datetime import datetime, timedelta
from config.database import get_supabase_client

class PrioritySlotService:
    def __init__(self):
        self.db = get_supabase_client()
    
    def create_priority_slot(self, user_id, slot_type, price, duration_hours=None, message_count=None, payment_gateway=None):
        """Create a new priority slot"""
        try:
            data = {
                'user_id': user_id,
                'slot_type': slot_type,
                'duration_hours': duration_hours,
                'message_count': message_count,
                'price': price,
                'payment_status': 'pending',
                'payment_gateway': payment_gateway,
                'active': False
            }
            response = self.db.table('priority_slots').insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating priority slot: {e}")
            return None
    
    def activate_priority_slot(self, slot_id):
        """Activate a priority slot after payment"""
        try:
            slot = self.get_priority_slot(slot_id)
            if not slot:
                return None
            
            start_time = datetime.utcnow()
            end_time = None
            
            if slot['slot_type'] == 'time' and slot['duration_hours']:
                end_time = start_time + timedelta(hours=slot['duration_hours'])
            
            update_data = {
                'active': True,
                'payment_status': 'completed',
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat() if end_time else None
            }
            
            response = self.db.table('priority_slots').update(update_data).eq('slot_id', slot_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error activating priority slot: {e}")
            return None
    
    def get_priority_slot(self, slot_id):
        """Get priority slot by ID"""
        try:
            response = self.db.table('priority_slots').select('*').eq('slot_id', slot_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting priority slot: {e}")
            return None
    
    def get_active_priority_slot(self):
        """Get currently active priority slot"""
        try:
            response = self.db.table('priority_slots').select('*').eq('active', True).order('start_time', desc=True).limit(1).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting active priority slot: {e}")
            return None
    
    def check_and_expire_slots(self):
        """Check and expire time-based priority slots"""
        try:
            active_slot = self.get_active_priority_slot()
            if not active_slot:
                return None
            
            if active_slot['slot_type'] == 'time' and active_slot['end_time']:
                end_time = datetime.fromisoformat(active_slot['end_time'].replace('Z', '+00:00'))
                if datetime.utcnow() > end_time.replace(tzinfo=None):
                    self.deactivate_priority_slot(active_slot['slot_id'])
                    return True
            
            elif active_slot['slot_type'] == 'count':
                if active_slot['messages_sent'] >= active_slot['message_count']:
                    self.deactivate_priority_slot(active_slot['slot_id'])
                    return True
            
            return False
        except Exception as e:
            print(f"Error checking slot expiration: {e}")
            return False
    
    def deactivate_priority_slot(self, slot_id):
        """Deactivate a priority slot"""
        try:
            response = self.db.table('priority_slots').update({'active': False}).eq('slot_id', slot_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error deactivating priority slot: {e}")
            return None
    
    def increment_slot_message_count(self, slot_id):
        """Increment message count for count-based slots"""
        try:
            slot = self.get_priority_slot(slot_id)
            if slot:
                new_count = slot.get('messages_sent', 0) + 1
                response = self.db.table('priority_slots').update({'messages_sent': new_count}).eq('slot_id', slot_id).execute()
                return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error incrementing slot message count: {e}")
            return None
    
    def get_user_priority_slots(self, user_id):
        """Get user's priority slots"""
        try:
            response = self.db.table('priority_slots').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting user priority slots: {e}")
            return []
