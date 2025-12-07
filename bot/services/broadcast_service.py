from datetime import datetime, timedelta
from config.database import get_supabase_client

MAX_BROADCASTS_PER_USER = 3

class BroadcastService:
    def __init__(self):
        self._db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_supabase_client()
        return self._db
    
    def create_broadcast(self, user_id, text, media_url=None, media_type=None, 
                        target_country=None, target_category=None):
        """Create a new broadcast"""
        try:
            data = {
                'user_id': user_id,
                'text': text,
                'media_url': media_url,
                'media_type': media_type,
                'target_country': target_country,
                'target_category': target_category,
                'status': 'queued'
            }
            response = self.db.table('broadcasts').insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating broadcast: {e}")
            return None
    
    def get_broadcast(self, broadcast_id):
        """Get broadcast by ID"""
        try:
            response = self.db.table('broadcasts').select('*').eq('broadcast_id', broadcast_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting broadcast: {e}")
            return None
    
    def get_queued_broadcasts(self):
        """Get all queued broadcasts"""
        try:
            response = self.db.table('broadcasts').select('*').eq('status', 'queued').order('created_at').execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting queued broadcasts: {e}")
            return []
    
    def update_broadcast_status(self, broadcast_id, status):
        """Update broadcast status"""
        try:
            update_data = {'status': status}
            if status == 'sent':
                update_data['sent_at'] = datetime.utcnow().isoformat()
            
            response = self.db.table('broadcasts').update(update_data).eq('broadcast_id', broadcast_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating broadcast status: {e}")
            return None
    
    def increment_broadcast_stats(self, broadcast_id, sent_count=0, views=0):
        """Increment broadcast statistics"""
        try:
            broadcast = self.get_broadcast(broadcast_id)
            if broadcast:
                update_data = {
                    'sent_count': broadcast.get('sent_count', 0) + sent_count,
                    'views': broadcast.get('views', 0) + views
                }
                response = self.db.table('broadcasts').update(update_data).eq('broadcast_id', broadcast_id).execute()
                return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error incrementing broadcast stats: {e}")
            return None
    
    def get_user_broadcasts(self, user_id, limit=10):
        """Get user's broadcasts"""
        try:
            response = self.db.table('broadcasts').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting user broadcasts: {e}")
            return []
    
    def delete_broadcast(self, broadcast_id):
        """Delete a broadcast by ID"""
        try:
            response = self.db.table('broadcasts').delete().eq('broadcast_id', broadcast_id).execute()
            print(f"✓ Deleted broadcast #{broadcast_id}")
            return True
        except Exception as e:
            print(f"Error deleting broadcast {broadcast_id}: {e}")
            return False
    
    def enforce_user_broadcast_limit(self, user_id):
        """Keep only the last 3 broadcasts per user, delete older ones"""
        try:
            response = self.db.table('broadcasts').select('broadcast_id').eq('user_id', user_id).order('created_at', desc=True).execute()
            broadcasts = response.data if response.data else []
            
            if len(broadcasts) > MAX_BROADCASTS_PER_USER:
                broadcasts_to_delete = broadcasts[MAX_BROADCASTS_PER_USER:]
                for bc in broadcasts_to_delete:
                    self.delete_broadcast(bc['broadcast_id'])
                print(f"✓ Enforced limit for user {user_id}: deleted {len(broadcasts_to_delete)} old broadcasts")
            return True
        except Exception as e:
            print(f"Error enforcing broadcast limit for user {user_id}: {e}")
            return False
    
    def delete_expired_broadcasts(self, hours=1):
        """Delete non-priority broadcasts older than specified hours"""
        try:
            cutoff_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
            
            response = self.db.table('broadcasts').select('broadcast_id, user_id, created_at, is_priority').lt('created_at', cutoff_time).execute()
            
            deleted_count = 0
            if response.data:
                for bc in response.data:
                    if not bc.get('is_priority', False):
                        self.delete_broadcast(bc['broadcast_id'])
                        deleted_count += 1
            
            if deleted_count > 0:
                print(f"✓ Deleted {deleted_count} expired broadcasts (older than {hours}h)")
            return deleted_count
        except Exception as e:
            print(f"Error deleting expired broadcasts: {e}")
            return 0
