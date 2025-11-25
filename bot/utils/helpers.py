from datetime import datetime, timedelta
import re

def is_valid_media_url(url):
    """Check if URL is valid"""
    pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is None or pattern.match(url) is not None

def format_price(amount):
    """Format price with currency"""
    return f"${amount:.2f}"

def calculate_priority_slot_end_time(start_time, slot_type, duration_hours=None):
    """Calculate when priority slot should end"""
    if duration_hours:
        return start_time + timedelta(hours=duration_hours)
    return None

def get_slot_description(slot_type, duration_hours=None, message_count=None):
    """Get human-readable slot description"""
    if slot_type == 'time':
        return f"{duration_hours} hours exclusive broadcast"
    elif slot_type == 'count':
        return f"{message_count} broadcasts exclusive"
    return "Priority slot"

def format_datetime(dt):
    """Format datetime for display"""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
