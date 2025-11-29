from config.database import get_supabase_client

class UserService:
    def __init__(self):
        self._db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_supabase_client()
        return self._db
    
    def get_user(self, user_id):
        """Get user by ID"""
        try:
            response = self.db.table('users').select('*').eq('user_id', user_id).execute()
            if response.data:
                user = response.data[0]
                print(f"✅ Retrieved user {user_id}: country={user.get('country')}, categories={user.get('categories')}")
                return user
            else:
                print(f"❌ User {user_id} not found in database")
                return None
        except Exception as e:
            print(f"❌ Database error getting user {user_id}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_user(self, user_id, username, first_name, last_name):
        """Create new user"""
        try:
            data = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name
            }
            response = self.db.table('users').insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def update_user(self, user_id, **kwargs):
        """Update user details"""
        try:
            response = self.db.table('users').eq('user_id', user_id).update(kwargs).execute()
            print(f"✅ Updated user {user_id}: {kwargs}")
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Error updating user {user_id}: {e}")
            return None
    
    def is_user_blocked(self, user_id):
        """Check if user is blocked"""
        user = self.get_user(user_id)
        return user.get('blocked', False) if user else False
    
    def get_all_users(self, active_only=True, target_country=None, target_category=None):
        """Get users based on filters"""
        try:
            query = self.db.table('users').select('*')
            
            if active_only:
                query = query.eq('active', True).eq('blocked', False)
            
            if target_country:
                query = query.eq('country', target_country)
            
            if target_category:
                query = query.eq('category', target_category)
            
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def get_user_count(self):
        """Get total user count"""
        try:
            response = self.db.table('users').select('user_id', count='exact').execute()
            return response.count if response.count else 0
        except Exception as e:
            print(f"Error getting user count: {e}")
            return 0
