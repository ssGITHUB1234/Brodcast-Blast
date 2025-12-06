"""Force Join Channel Service"""
from config.database import get_supabase_client
from config.settings import TELEGRAM_BOT_TOKEN
import requests

class ForceJoinService:
    """Handle force join channel operations"""
    
    def __init__(self):
        self._db = None
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_supabase_client()
        return self._db
    
    def get_all_channels(self):
        """Get all force join channels"""
        try:
            response = self.db.table('force_join_channels').select('*').order('created_at', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting force join channels: {e}")
            return []
    
    def get_active_channels(self):
        """Get only active force join channels"""
        try:
            response = self.db.table('force_join_channels').select('*').eq('active', True).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting active channels: {e}")
            return []
    
    def add_channel(self, channel_id, channel_name, channel_username=None):
        """Add a new force join channel"""
        try:
            data = {
                'channel_id': str(channel_id),
                'channel_name': channel_name,
                'channel_username': channel_username,
                'active': True
            }
            response = self.db.table('force_join_channels').insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error adding force join channel: {e}")
            return None
    
    def update_channel(self, id, **kwargs):
        """Update a force join channel"""
        try:
            response = self.db.table('force_join_channels').update(kwargs).eq('id', id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating force join channel: {e}")
            return None
    
    def delete_channel(self, id):
        """Delete a force join channel"""
        try:
            self.db.table('force_join_channels').delete().eq('id', id).execute()
            return True
        except Exception as e:
            print(f"Error deleting force join channel: {e}")
            return False
    
    def check_user_membership(self, user_id, channel_id):
        """Check if user is a member of a channel"""
        try:
            url = f"{self.api_url}/getChatMember"
            
            # Ensure channel_id has proper format for channels (should start with -100)
            chat_id = channel_id
            if isinstance(channel_id, str):
                # If it's a username, use as-is
                if not channel_id.startswith('@') and not channel_id.startswith('-'):
                    # Try as username first
                    chat_id = f"@{channel_id}"
                elif channel_id.lstrip('-').isdigit():
                    # It's a numeric ID - ensure it's properly formatted
                    chat_id = channel_id
            
            data = {
                'chat_id': chat_id,
                'user_id': user_id
            }
            response = requests.post(url, json=data)
            result = response.json()
            
            if result.get('ok'):
                status = result.get('result', {}).get('status')
                # Include 'restricted' status - restricted users are still channel members
                return status in ['member', 'administrator', 'creator', 'restricted']
            else:
                # Log the error for debugging
                error_desc = result.get('description', 'Unknown error')
                print(f"Telegram API error checking membership: {error_desc} (channel: {chat_id}, user: {user_id})")
            return False
        except Exception as e:
            print(f"Error checking membership for user {user_id} in channel {channel_id}: {e}")
            return False
    
    def check_all_channels(self, user_id):
        """Check if user has joined all required channels"""
        channels = self.get_active_channels()
        if not channels:
            return True, []
        
        not_joined = []
        for channel in channels:
            channel_id = channel.get('channel_id')
            if not self.check_user_membership(user_id, channel_id):
                not_joined.append(channel)
        
        return len(not_joined) == 0, not_joined
    
    def get_channel_info(self, channel_input):
        """Get channel info from Telegram"""
        try:
            url = f"{self.api_url}/getChat"
            
            # Handle different input formats
            chat_id = channel_input.strip()
            if not chat_id.startswith('@') and not chat_id.startswith('-'):
                # If it's just a username without @, add it
                if not chat_id.lstrip('-').isdigit():
                    chat_id = f"@{chat_id}"
            
            data = {'chat_id': chat_id}
            response = requests.post(url, json=data)
            result = response.json()
            
            if result.get('ok'):
                chat = result.get('result', {})
                return {
                    'id': chat.get('id'),
                    'title': chat.get('title'),
                    'username': chat.get('username'),
                    'type': chat.get('type')
                }
            else:
                error_desc = result.get('description', 'Unknown error')
                print(f"Failed to get channel info for {chat_id}: {error_desc}")
            return None
        except Exception as e:
            print(f"Error getting channel info: {e}")
            return None
