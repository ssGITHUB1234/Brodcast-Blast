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
        """Get all slot types using RPC"""
        try:
            response = self.db.rpc('get_all_slot_types', {'p_active_only': active_only}).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting slot types: {e}")
            return []
    
    def get_slot_type(self, slot_type_id):
        """Get a single slot type by ID"""
        try:
            all_slots = self.get_all_slot_types(active_only=False)
            for slot in all_slots:
                if slot['id'] == slot_type_id:
                    return slot
            return None
        except Exception as e:
            print(f"Error getting slot type: {e}")
            return None
    
    def get_slot_type_by_key(self, slot_key):
        """Get a slot type by its key"""
        try:
            all_slots = self.get_all_slot_types(active_only=False)
            for slot in all_slots:
                if slot['slot_key'] == slot_key:
                    return slot
            return None
        except Exception as e:
            print(f"Error getting slot type by key: {e}")
            return None
    
    def create_slot_type(self, slot_key, slot_category, display_name, price, description=None, duration_hours=None, message_count=None):
        """Create a new slot type using RPC"""
        try:
            response = self.db.rpc('create_slot_type', {
                'p_slot_key': slot_key,
                'p_slot_category': slot_category,
                'p_display_name': display_name,
                'p_price': float(price),
                'p_description': description,
                'p_duration_hours': duration_hours,
                'p_message_count': message_count
            }).execute()
            return response.data if response.data else None
        except Exception as e:
            print(f"Error creating slot type: {e}")
            return None
    
    def update_slot_type(self, slot_type_id, **kwargs):
        """Update a slot type using RPC"""
        try:
            allowed_fields = ['slot_key', 'slot_category', 'display_name', 'description', 
                            'duration_hours', 'message_count', 'price', 'active']
            update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            if not update_data:
                return None
            
            price = float(update_data.get('price', 0)) if 'price' in update_data else None
            active = update_data.get('active')
            display_name = update_data.get('display_name')
            
            response = self.db.rpc('update_slot_type', {
                'p_id': slot_type_id,
                'p_price': price,
                'p_active': active,
                'p_display_name': display_name
            }).execute()
            return response.data if response.data else None
        except Exception as e:
            print(f"Error updating slot type: {e}")
            return None
    
    def delete_slot_type(self, slot_type_id):
        """Delete (soft delete by deactivating) a slot type"""
        try:
            return self.update_slot_type(slot_type_id, active=False)
        except Exception as e:
            print(f"Error deleting slot type: {e}")
            return None
    
    def hard_delete_slot_type(self, slot_type_id):
        """Permanently delete a slot type using RPC"""
        try:
            response = self.db.rpc('delete_slot_type', {'p_id': slot_type_id}).execute()
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
            all_slots = self.get_all_slot_types(active_only=active_only)
            time_slots = [s for s in all_slots if s.get('slot_category') == 'time']
            return sorted(time_slots, key=lambda x: x.get('duration_hours') or 0)
        except Exception as e:
            print(f"Error getting time slots: {e}")
            return []
    
    def get_count_slots(self, active_only=True):
        """Get all count-based slot types"""
        try:
            all_slots = self.get_all_slot_types(active_only=active_only)
            count_slots = [s for s in all_slots if s.get('slot_category') == 'count']
            return sorted(count_slots, key=lambda x: x.get('message_count') or 0)
        except Exception as e:
            print(f"Error getting count slots: {e}")
            return []
