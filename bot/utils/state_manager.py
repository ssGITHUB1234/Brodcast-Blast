"""User state management for navigation tracking"""

# Store user context: {user_id: {'message_id': int, 'context': str, 'previous_context': str}}
user_state = {}

def set_user_state(user_id, message_id, context, extra_data=None):
    """Track user's current context and message ID"""
    if user_id not in user_state:
        user_state[user_id] = {}
    user_state[user_id]['message_id'] = message_id
    user_state[user_id]['context'] = context
    if extra_data:
        user_state[user_id]['extra_data'] = extra_data

def get_user_state(user_id):
    """Get user's current state"""
    return user_state.get(user_id, {})

def get_user_message_id(user_id):
    """Get user's last message ID"""
    return user_state.get(user_id, {}).get('message_id')

def get_user_context(user_id):
    """Get user's current context"""
    return user_state.get(user_id, {}).get('context')

def get_previous_context(user_id):
    """Get user's previous context"""
    return user_state.get(user_id, {}).get('previous_context')

def clear_user_state(user_id):
    """Clear user state"""
    if user_id in user_state:
        del user_state[user_id]
