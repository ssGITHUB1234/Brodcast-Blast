from telebot import types
from bot.services.user_service import UserService
from bot.services.broadcast_service import BroadcastService
from bot.services.priority_service import PrioritySlotService
from bot.utils.state_manager import set_user_state, get_user_message_id
from bot.utils.nav_helpers import add_navigation_buttons, edit_or_send
from config import ads_state

user_service = UserService()
broadcast_service = BroadcastService()
priority_service = PrioritySlotService()

def handle_menu(bot, message):
    """Show main menu"""
    user_id = message.from_user.id
    message_id = getattr(message, 'message_id', None)
    
    user = None
    try:
        user = user_service.get_user(user_id)
        if not user:
            print(f"❌ User {user_id} not found in database")
        else:
            print(f"✅ User {user_id} retrieved: country={user.get('country')}, categories={user.get('categories')}")
    except Exception as e:
        print(f"❌ Error retrieving user {user_id}: {e}")
    
    if user and user.get('blocked'):
        bot.reply_to(message, "Access denied. You have been blocked.")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Create Broadcast", callback_data="menu_create"),
        types.InlineKeyboardButton("Priority Slots", callback_data="menu_priority"),
        types.InlineKeyboardButton("My Broadcasts", callback_data="menu_mybroadcasts"),
        types.InlineKeyboardButton("My Stats", callback_data="menu_stats"),
        types.InlineKeyboardButton("💰 Earn Rewards", callback_data="menu_ads"),
        types.InlineKeyboardButton("Settings", callback_data="menu_settings"),
        types.InlineKeyboardButton("Help", callback_data="menu_help")
    )
    add_navigation_buttons(markup, go_back=False, go_menu=False)
    
    slot_msg = ""
    try:
        active_slot = priority_service.get_active_priority_slot()
        if active_slot and active_slot.get('user_id') == user_id:
            slot_msg = "\n\n✨ Your priority slot is ACTIVE!"
    except:
        pass
    
    first_name = message.from_user.first_name
    country = "Not set"
    categories = "Not set"
    points = 0
    
    if user:
        first_name = user.get('first_name', first_name)
        country = user.get('country') or 'Not set'
        points = user.get('points', 0) or 0
        # Handle both 'categories' (array) and 'category' (old format)
        cats = user.get('categories') or user.get('category')
        if isinstance(cats, list):
            categories = ', '.join(filter(None, cats)) if cats else 'Not set'
        elif cats:
            categories = str(cats)
        else:
            categories = 'Not set'
    
    # Get points required for broadcast
    points_required = ads_state.settings.get('points_required', 30)
    points_status = "✅ Can broadcast!" if points >= points_required else f"❌ Need {points_required - points} more"
    
    text = f"Main Menu{slot_msg}\n\n" \
           f"Welcome, {first_name}!\n" \
           f"💰 Points: {points}/{points_required} ({points_status})\n" \
           f"📍 Country: {country}\n" \
           f"📂 Interests: {categories}\n\n" \
           f"Select an option:"
    
    result = edit_or_send(bot, message.chat.id, text, message_id, markup)
    if result:
        set_user_state(user_id, result.message_id, 'menu')
    else:
        set_user_state(user_id, message_id, 'menu')

def handle_my_broadcasts(bot, message, page=0):
    """Show user's broadcasts with pagination (1 per page, max 3 broadcasts)"""
    user_id = message.from_user.id
    message_id = getattr(message, 'message_id', None)
    
    try:
        # Limit to last 3 broadcasts to save storage
        broadcasts = broadcast_service.get_user_broadcasts(user_id, limit=3)
    except:
        broadcasts = []
    
    if not broadcasts:
        markup = types.InlineKeyboardMarkup()
        add_navigation_buttons(markup, go_back=False, go_menu=True)
        text = "You haven't created any broadcasts yet.\n\nUse /create to send your first broadcast!"
        result = edit_or_send(bot, message.chat.id, text, message_id, markup)
        if result:
            set_user_state(user_id, result.message_id, 'mybroadcasts')
        else:
            set_user_state(user_id, message_id, 'mybroadcasts')
        return
    
    # Get current broadcast
    if page >= len(broadcasts):
        page = len(broadcasts) - 1
    if page < 0:
        page = 0
    
    bc = broadcasts[page]
    status_emoji = "✅" if bc['status'] == 'sent' else "⏳" if bc['status'] == 'queued' else "📝"
    
    # Format broadcast details
    text_preview = bc.get('text', '')[:100]
    response = f"📢 Broadcast {page + 1}/{len(broadcasts)}\n\n"
    response += f"{status_emoji} Status: {bc['status'].upper()}\n"
    response += f"📝 Text:\n{text_preview}\n\n"
    response += f"👁️ Views: {bc.get('views', 0)}\n"
    response += f"📤 Recipients: {bc.get('sent_count', 0)}\n"
    response += f"⏰ Created: {bc.get('created_at', 'N/A')}"
    
    # Pagination buttons
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Add prev/next buttons
    if page > 0:
        markup.add(types.InlineKeyboardButton("⬅️ Previous", callback_data=f"bc_prev_{page}"))
    else:
        markup.add(types.InlineKeyboardButton("⬅️", callback_data="noop"))
    
    if page < len(broadcasts) - 1:
        markup.add(types.InlineKeyboardButton("Next ➡️", callback_data=f"bc_next_{page}"))
    else:
        markup.add(types.InlineKeyboardButton("➡️", callback_data="noop"))
    
    # Menu button
    add_navigation_buttons(markup, go_back=False, go_menu=True)
    
    result = edit_or_send(bot, message.chat.id, response, message_id, markup)
    if result:
        set_user_state(user_id, result.message_id, 'mybroadcasts', {'page': page, 'total': len(broadcasts)})
    else:
        set_user_state(user_id, message_id, 'mybroadcasts', {'page': page, 'total': len(broadcasts)})

def handle_stats(bot, message):
    """Show user statistics"""
    user_id = message.from_user.id
    message_id = getattr(message, 'message_id', None)
    
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
    
    text = f"📊 Your Statistics\n\n" \
           f"📢 Total Broadcasts: {total_broadcasts}\n" \
           f"👁️ Total Views: {total_views}\n" \
           f"📤 Total Recipients: {total_sent}\n" \
           f"🎯 Priority Slots Used: {len(priority_slots)}\n" \
           f"✨ Active Slots: {active_slots}\n\n" \
           f"Keep broadcasting to reach more users!"
    
    markup = types.InlineKeyboardMarkup()
    add_navigation_buttons(markup, go_back=False, go_menu=True)
    result = edit_or_send(bot, message.chat.id, text, message_id, markup)
    if result:
        set_user_state(user_id, result.message_id, 'stats')
    else:
        set_user_state(user_id, message_id, 'stats')

def handle_settings(bot, message):
    """Show settings"""
    user_id = message.from_user.id
    message_id = getattr(message, 'message_id', None)
    
    try:
        user = user_service.get_user(user_id)
    except:
        user = None
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("Change Country", callback_data="settings_country"),
        types.InlineKeyboardButton("Change Categories", callback_data="settings_category")
    )
    add_navigation_buttons(markup, go_back=False, go_menu=True)
    
    country = user.get('country', 'Not set') if user else 'Not set'
    cats = user.get('categories', user.get('category', 'Not set')) if user else 'Not set'
    if isinstance(cats, list):
        cats = ', '.join(cats)
    
    text = f"⚙️ Settings\n\n" \
           f"Current settings:\n" \
           f"📍 Country: {country}\n" \
           f"📂 Categories: {cats}\n\n" \
           f"Select what you want to change:"
    
    result = edit_or_send(bot, message.chat.id, text, message_id, markup)
    if result:
        set_user_state(user_id, result.message_id, 'settings')
    else:
        set_user_state(user_id, message_id, 'settings')

def handle_help(bot, message):
    """Show help information"""
    user_id = message.from_user.id
    message_id = getattr(message, 'message_id', None)
    help_text = """❓ Help & Information

📖 What is this bot?
This is a broadcast bot that allows you to send messages to targeted audiences.

📢 Free Broadcasts:
• Create broadcasts with text and media
• Target by country, category, or all users
• Broadcasts are queued and sent automatically

💰 Points System:
• Watch ads to earn points
• Use points to create broadcasts
• Check /points for your balance

🌟 Priority Slots:
Want your broadcasts sent immediately?
• Purchase a priority slot
• Your broadcasts bypass the queue
• Other broadcasts are paused during your slot
• Available as time-based or count-based

⌨️ Commands:
/start - Register or restart
/menu - Main menu
/create - Create a broadcast
/points - Check your points balance
/priority - View priority slot options
/mystats - View detailed broadcast analytics
/settings - Change your settings
/help - Show this help message

Need assistance?
Contact our admin team for support!"""
    
    markup = types.InlineKeyboardMarkup()
    add_navigation_buttons(markup, go_back=False, go_menu=True)
    result = edit_or_send(bot, message.chat.id, help_text, message_id, markup)
    if result:
        set_user_state(user_id, result.message_id, 'help')
    else:
        set_user_state(user_id, message_id, 'help')

def handle_points(bot, message):
    """Show user's points balance and earn options"""
    from config.settings import APP_DOMAIN, ADMIN_USER_IDS
    import secrets
    
    user_id = message.from_user.id
    message_id = getattr(message, 'message_id', None)
    
    try:
        user = user_service.get_user(user_id)
    except:
        user = None
    
    current_points = user.get('points', 0) or 0 if user else 0
    points_per_ad = ads_state.settings.get('points_per_ad', 10)
    points_required = ads_state.settings.get('points_required', 30)
    
    # Check if admin
    is_admin = user_id in ADMIN_USER_IDS
    
    if is_admin:
        text = f"💰 Points Balance\n\n" \
               f"🔒 You are an ADMIN\n" \
               f"✅ You can broadcast without points!\n\n" \
               f"📊 Current balance: {current_points} points\n" \
               f"(For reference only - admins bypass points check)"
        
        markup = types.InlineKeyboardMarkup()
        add_navigation_buttons(markup, go_back=False, go_menu=True)
    else:
        points_needed = max(0, points_required - current_points)
        ads_needed = -(-points_needed // points_per_ad) if points_needed > 0 else 0
        
        can_broadcast = current_points >= points_required
        status = "✅ Ready to broadcast!" if can_broadcast else f"❌ Need {points_needed} more points"
        
        text = f"💰 Points Balance\n\n" \
               f"📊 Your balance: {current_points} points\n" \
               f"📋 Required to broadcast: {points_required} points\n" \
               f"📌 Status: {status}\n\n"
        
        if can_broadcast:
            text += f"🎉 You have enough points!\n" \
                    f"Use /create to send a broadcast."
        else:
            text += f"🎬 Watch {ads_needed} ad(s) to earn enough points!\n" \
                    f"Each ad = +{points_per_ad} points"
        
        markup = types.InlineKeyboardMarkup()
        
        if not can_broadcast:
            # Add watch ad button
            session_token = secrets.token_urlsafe(32)
            ad_viewer_url = f"{APP_DOMAIN}/ad-viewer?user_id={user_id}&token={session_token}"
            markup.add(
                types.InlineKeyboardButton(f"▶️ Watch Ad (+{points_per_ad} points)", web_app=types.WebAppInfo(url=ad_viewer_url))
            )
        else:
            markup.add(
                types.InlineKeyboardButton("📢 Create Broadcast", callback_data="menu_create")
            )
        
        add_navigation_buttons(markup, go_back=False, go_menu=True)
    
    result = edit_or_send(bot, message.chat.id, text, message_id, markup)
    if result:
        set_user_state(user_id, result.message_id, 'points')
    else:
        set_user_state(user_id, message_id, 'points')
