"""
Shared ad state between bot and backend
"""
import time

# Track users who watched ads in current session
users_watched_ads = {}  # {user_id: True}

# Track when users watched ads (timestamps) - for skipping ad on immediate next interaction
ad_watched_timestamps = {}  # {user_id: timestamp}

# Track ad statistics
ad_stats = {
    'views_completed': 0,
    'views_uncompleted': 0
}

# Admin settings - shared between backend and bot
settings = {
    'ads_required': True  # Admin can toggle via dashboard
}

def mark_ad_watched(user_id):
    """Mark that user watched an ad with timestamp"""
    users_watched_ads[user_id] = True
    ad_watched_timestamps[user_id] = time.time()  # Store timestamp
    ad_stats['views_completed'] += 1

def user_watched_ad_recently(user_id, timeout_seconds=60):
    """Check if user watched ad recently (within timeout)"""
    if user_id not in ad_watched_timestamps:
        return False
    time_since_watch = time.time() - ad_watched_timestamps[user_id]
    return time_since_watch < timeout_seconds

def mark_ad_started(user_id):
    """Track that user started watching ad"""
    ad_stats['views_uncompleted'] += 1

def user_watched_ad(user_id):
    """Check if user watched ad in current session"""
    return user_id in users_watched_ads

def clear_watched(user_id):
    """Clear ad watched status for user"""
    if user_id in users_watched_ads:
        del users_watched_ads[user_id]

def get_stats():
    """Get ad statistics"""
    return {
        'views_completed': ad_stats['views_completed'],
        'views_uncompleted': ad_stats['views_uncompleted'],
        'total_views': ad_stats['views_completed'] + ad_stats['views_uncompleted']
    }
