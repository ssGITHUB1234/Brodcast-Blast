from telebot import types
from bot.services.user_service import UserService
from bot.services.broadcast_service import BroadcastService
from bot.services.priority_service import PrioritySlotService

user_service = UserService()
broadcast_service = BroadcastService()
priority_service = PrioritySlotService()

def handle_menu(bot, message):
    """Show main menu"""
    user_id = message.from_user.id
    
    try:
        user = user_service.get_user(user_id)
    except:
        user = None
    
    if user and user.get('blocked'):
        bot.reply_to(message, "Access denied. You have been blocked.")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Create Broadcast", callback_data="menu_create"),
        types.InlineKeyboardButton("Priority Slots", callback_data="menu_priority"),
        types.InlineKeyboardButton("My Broadcasts", callback_data="menu_mybroadcasts"),
        types.InlineKeyboardButton("My Stats", callback_data="menu_stats"),
        types.InlineKeyboardButton("Settings", callback_data="menu_settings"),
        types.InlineKeyboardButton("Help", callback_data="menu_help")
    )
    
    slot_msg = ""
    try:
        active_slot = priority_service.get_active_priority_slot()
        if active_slot and active_slot.get('user_id') == user_id:
            slot_msg = "\n\nYour priority slot is ACTIVE!"
    except:
        pass
    
    first_name = message.from_user.first_name
    country = "Not set"
    categories = "Not set"
    
    if user:
        first_name = user.get('first_name', first_name)
        country = user.get('country', 'Not set')
        cats = user.get('categories', user.get('category', 'Not set'))
        if isinstance(cats, list):
            categories = ', '.join(cats)
        else:
            categories = cats if cats else 'Not set'
    
    bot.send_message(message.chat.id,
        f"Main Menu{slot_msg}\n\n"
        f"Welcome, {first_name}!\n"
        f"Country: {country}\n"
        f"Interests: {categories}\n\n"
        f"Select an option:",
        reply_markup=markup)

def handle_my_broadcasts(bot, message):
    """Show user's broadcasts"""
    user_id = message.from_user.id
    
    try:
        broadcasts = broadcast_service.get_user_broadcasts(user_id, limit=10)
    except:
        broadcasts = []
    
    if not broadcasts:
        bot.reply_to(message, "You haven't created any broadcasts yet.\n\nUse /create to send your first broadcast!")
        return
    
    response = "Your Recent Broadcasts:\n\n"
    for bc in broadcasts:
        status_emoji = "[SENT]" if bc['status'] == 'sent' else "[QUEUED]" if bc['status'] == 'queued' else "[DRAFT]"
        response += f"{status_emoji} #{bc['broadcast_id']}\n"
        response += f"   {bc.get('views', 0)} views | {bc.get('sent_count', 0)} sent\n"
        text = bc.get('text', '')[:50]
        response += f"   {text}...\n\n"
    
    bot.reply_to(message, response)

def handle_stats(bot, message):
    """Show user statistics"""
    user_id = message.from_user.id
    
    try:
        broadcasts = broadcast_service.get_user_broadcasts(user_id, limit=100)
    except:
        broadcasts = []
    
    try:
        priority_slots = priority_service.get_user_priority_slots(user_id)
    except:
        priority_slots = []
    
    total_views = sum(bc.get('views', 0) for bc in broadcasts)
    total_sent = sum(bc.get('sent_count', 0) for bc in broadcasts)
    total_broadcasts = len(broadcasts)
    active_slots = sum(1 for slot in priority_slots if slot.get('active', False))
    
    bot.reply_to(message,
        f"Your Statistics\n\n"
        f"Total Broadcasts: {total_broadcasts}\n"
        f"Total Views: {total_views}\n"
        f"Total Recipients: {total_sent}\n"
        f"Priority Slots Used: {len(priority_slots)}\n"
        f"Active Slots: {active_slots}\n\n"
        f"Keep broadcasting to reach more users!")

def handle_settings(bot, message):
    """Show settings"""
    user_id = message.from_user.id
    
    try:
        user = user_service.get_user(user_id)
    except:
        user = None
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("Change Country", callback_data="settings_country"),
        types.InlineKeyboardButton("Change Categories", callback_data="settings_category")
    )
    
    country = user.get('country', 'Not set') if user else 'Not set'
    cats = user.get('categories', user.get('category', 'Not set')) if user else 'Not set'
    if isinstance(cats, list):
        cats = ', '.join(cats)
    
    bot.send_message(message.chat.id,
        f"Settings\n\n"
        f"Current settings:\n"
        f"Country: {country}\n"
        f"Categories: {cats}\n\n"
        f"Select what you want to change:",
        reply_markup=markup)

def handle_help(bot, message):
    """Show help information"""
    help_text = """
Help & Information

What is this bot?
This is a broadcast bot that allows you to send messages to targeted audiences.

Free Broadcasts:
- Create broadcasts with text and media
- Target by country, category, or all users
- Broadcasts are queued and sent automatically

Priority Slots:
Want your broadcasts sent immediately?
- Purchase a priority slot
- Your broadcasts bypass the queue
- Other broadcasts are paused during your slot
- Available as time-based or count-based

Commands:
/start - Register or restart
/menu - Main menu
/create - Create a broadcast
/priority - View priority slot options
/mybroadcasts - View your broadcasts
/stats - View your statistics
/settings - Change your settings
/help - Show this help message

Need assistance?
Contact our admin team for support!
"""
    bot.reply_to(message, help_text)
