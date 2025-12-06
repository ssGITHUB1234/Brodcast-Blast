from config.database import get_supabase_client

class SlotTypeService:
    def __init__(self):
        self._db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_supabase_client()
        return self._db
    
    def get_all_slot_types(self, active_only=False):
        """Get all slot types"""
        try:
            query = self.db.table('priority_slot_types').select('*')
            if active_only:
                query = query.eq('active', True)
            response = query.order('slot_category').order('price').execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting slot types: {e}")
            return []
    
    def get_slot_type(self, slot_type_id):
        """Get a single slot type by ID"""
        try:
            response = self.db.table('priority_slot_types').select('*').eq('id', slot_type_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting slot type: {e}")
            return None
    
    def get_slot_type_by_key(self, slot_key):
        """Get a slot type by its key"""
        try:
            response = self.db.table('priority_slot_types').select('*').eq('slot_key', slot_key).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting slot type by key: {e}")
            return None
    
    def create_slot_type(self, slot_key, slot_category, display_name, price, description=None, duration_hours=None, message_count=None):
        """Create a new slot type"""
        try:
            data = {
                'slot_key': slot_key,
                'slot_category': slot_category,
                'display_name': display_name,
                'description': description,
                'duration_hours': duration_hours,
                'message_count': message_count,
                'price': float(price),
                'active': True
            }
            response = self.db.table('priority_slot_types').insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating slot type: {e}")
            return None
    
    def update_slot_type(self, slot_type_id, **kwargs):
        """Update a slot type"""
        try:
            allowed_fields = ['slot_key', 'slot_category', 'display_name', 'description', 
                            'duration_hours', 'message_count', 'price', 'active']
            update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            if 'price' in update_data:
                update_data['price'] = float(update_data['price'])
            
            if not update_data:
                return None
            
            response = self.db.table('priority_slot_types').update(update_data).eq('id', slot_type_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating slot type: {e}")
            return None
    
    def delete_slot_type(self, slot_type_id):
        """Delete (soft delete by deactivating) a slot type"""
        try:
            response = self.db.table('priority_slot_types').update({'active': False}).eq('id', slot_type_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error deleting slot type: {e}")
            return None
    
    def hard_delete_slot_type(self, slot_type_id):
        """Permanently delete a slot type"""
        try:
            response = self.db.table('priority_slot_types').delete().eq('id', slot_type_id).execute()
            return True
        except Exception as e:
            print(f"Error hard deleting slot type: {e}")
            return False
    
    def get_pricing_dict(self):
        """Get pricing as a dictionary (compatible with legacy pricing_cache format)"""
        try:
            slot_types = self.get_all_slot_types(active_only=True)
            pricing = {}
            for slot in slot_types:
                pricing[slot['slot_key']] = float(slot['price'])
            return pricing
        except Exception as e:
            print(f"Error getting pricing dict: {e}")
            return {}
    
    def get_time_slots(self, active_only=True):
        """Get all time-based slot types"""
        try:
            query = self.db.table('priority_slot_types').select('*').eq('slot_category', 'time')
            if active_only:
                query = query.eq('active', True)
            response = query.order('duration_hours').execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting time slots: {e}")
            return []
    
    def get_count_slots(self, active_only=True):
        """Get all count-based slot types"""
        try:
            query = self.db.table('priority_slot_types').select('*').eq('slot_category', 'count')
            if active_only:
                query = query.eq('active', True)
            response = query.order('message_count').execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting count slots: {e}")
            return []
