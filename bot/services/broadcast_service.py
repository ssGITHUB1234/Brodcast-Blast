from datetime import datetime
from config.database import get_supabase_client

class BroadcastService:
    def __init__(self):
        self.db = get_supabase_client()
    
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
