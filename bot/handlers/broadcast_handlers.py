from telebot import types
from bot.services.broadcast_service import BroadcastService
from bot.services.user_service import UserService
from bot.services.priority_service import PrioritySlotService
from bot.services.monetag_service import MonetgService
from config.settings import COUNTRIES, CATEGORIES, APP_DOMAIN, ADMIN_USER_IDS
from config import ads_state
import os
import secrets
import traceback

broadcast_service = BroadcastService()
user_service = UserService()
priority_service = PrioritySlotService()
monetag_service = MonetgService()

user_broadcast_state = {}
users_ads_watched = set()

def is_admin(user_id):
    """Check if user is admin"""
    return user_id in ADMIN_USER_IDS

def handle_create_broadcast(bot, message):
    """Start broadcast creation process - check points or show ad"""
    from bot.utils.nav_helpers import edit_or_send
    import secrets
    import traceback
    
    user_id = message.from_user.id
    message_id = getattr(message, 'message_id', None)
    chat_id = message.chat.id
    
    print(f"[CREATE_BROADCAST] User {user_id} triggered create broadcast (message_id={message_id}, chat_id={chat_id})")
    
    try:
        print(f"[CREATE_BROADCAST] Getting user {user_id}...")
        user = user_service.get_user(user_id)
        
        # Auto-register user if they don't exist
        if not user:
            print(f"[CREATE_BROADCAST] User {user_id} not found, auto-registering...")
            try:
                user_service.create_user(
                    user_id,
                    message.from_user.username,
                    message.from_user.first_name,
                    message.from_user.last_name
                )
                edit_or_send(bot, chat_id, f"Welcome! Quick registration:\n\nPlease use /start to select your country & interests.\n\nThen come back to /create", message_id)
                return
            except Exception as e:
                print(f"❌ Auto-register error: {e}")
                traceback.print_exc()
                edit_or_send(bot, chat_id, "❌ Registration failed. Please try /start", message_id)
                return
        
        # Check if user is blocked
        if user.get('blocked'):
            print(f"[CREATE_BROADCAST] User {user_id} is blocked")
            edit_or_send(bot, chat_id, "⛔ You have been blocked and cannot create broadcasts.", message_id)
            return
        
        # Admin bypass - admins don't need points
        if is_admin(user_id):
            print(f"[CREATE_BROADCAST] User {user_id} is ADMIN - bypassing points check")
            start_broadcast_creation(bot, message, user_id)
            return
        
        # Check if ads/points are required (admin setting)
        ads_required = ads_state.settings.get('ads_required', True)
        if not ads_required:
            print(f"[CREATE_BROADCAST] Ads not required (admin setting) - allowing broadcast for user {user_id}")
            start_broadcast_creation(bot, message, user_id)
            return
        
        # Get points settings
        points_required = ads_state.settings.get('points_required', 30)
        points_per_ad = ads_state.settings.get('points_per_ad', 10)
        current_points = user_service.get_user_points(user_id)
        
        print(f"[CREATE_BROADCAST] User {user_id} points: {current_points}/{points_required}")
        
        # Check if user has enough points
        if current_points >= points_required:
            # User has enough points - start broadcast creation
            print(f"[CREATE_BROADCAST] User {user_id} has enough points - starting broadcast creation")
            start_broadcast_creation(bot, message, user_id)
        else:
            # Not enough points - show ad button
            points_needed = points_required - current_points
            ads_needed = -(-points_needed // points_per_ad)  # Ceiling division
            
            print(f"[CREATE_BROADCAST] User {user_id} needs {points_needed} more points ({ads_needed} ads)")
            
            # Generate unique session token for this ad session
            session_token = secrets.token_urlsafe(32)
            
            # Use APP_DOMAIN from config (auto-detects Render, Replit, or fallback)
            base_url = APP_DOMAIN
            print(f"[CREATE_BROADCAST] Using domain: {base_url}")
            
            # Create WebApp URL with session token
            ad_viewer_url = f"{base_url}/ad-viewer?user_id={user_id}&token={session_token}"
            print(f"[CREATE_BROADCAST] Ad viewer URL: {ad_viewer_url}")
            
            # Use WebApp button instead of URL button (more reliable in Telegram)
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("▶️ Watch Ad (+10 points)", web_app=types.WebAppInfo(url=ad_viewer_url))
            )
            edit_or_send(bot, chat_id,
                f"📊 Points Required to Broadcast\n\n"
                f"💰 Your balance: {current_points} points\n"
                f"📋 Required: {points_required} points\n"
                f"❌ Needed: {points_needed} more points\n\n"
                f"🎬 Watch {ads_needed} ad(s) to earn enough points!\n"
                f"Each ad = +{points_per_ad} points",
                message_id, markup)
            print(f"[CREATE_BROADCAST] Ad button sent to user {user_id}")
            return
    except Exception as e:
        print(f"❌ handle_create_broadcast error for user {user_id}: {e}")
        traceback.print_exc()
        try:
            edit_or_send(bot, chat_id, f"❌ Error in broadcast creation: {str(e)[:80]}", message_id)
        except Exception as send_error:
            print(f"❌ Could not send error message: {send_error}")
            try:
                bot.send_message(chat_id, f"❌ Broadcast creation failed. Please try again.\n\nError: {str(e)[:50]}")
            except:
                pass

def start_broadcast_creation(bot, message, user_id):
    """Start the actual broadcast creation flow"""
    user_broadcast_state[user_id] = {'step': 'text'}
    chat_id = message.chat.id
    bot.send_message(chat_id,
        "📝 Send your broadcast message.\n\n"
        "Text only or with media (image/video/document).")

def handle_broadcast_text_input(bot, message):
    """Handle text input for broadcast"""
    user_id = message.from_user.id
    
    if user_id in user_broadcast_state and user_broadcast_state[user_id]['step'] == 'text':
        user_broadcast_state[user_id]['text'] = message.text
        user_broadcast_state[user_id]['step'] = 'media'
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Skip Media", callback_data="broadcast_skip_media"))
        
        bot.reply_to(message, 
            "✅ Text saved!\n\n"
            "Step 2: Send me an image, video, or document (optional).\n"
            "Or click 'Skip Media' to continue.",
            reply_markup=markup)

def handle_broadcast_media_input(bot, message):
    """Handle media input for broadcast"""
    user_id = message.from_user.id
    
    if user_id in user_broadcast_state and user_broadcast_state[user_id]['step'] == 'media':
        if message.photo:
            media_url = message.photo[-1].file_id
            media_type = 'photo'
        elif message.video:
            media_url = message.video.file_id
            media_type = 'video'
        elif message.document:
            media_url = message.document.file_id
            media_type = 'document'
        else:
            bot.reply_to(message, "Please send a photo, video, or document, or click 'Skip Media'.")
            return
        
        user_broadcast_state[user_id]['media_url'] = media_url
        user_broadcast_state[user_id]['media_type'] = media_type
        user_broadcast_state[user_id]['step'] = 'targeting'
        
        show_targeting_options(bot, message.chat.id, user_id=user_id)

def show_targeting_options(bot, chat_id, message_id=None, user_id=None):
    """Show targeting options - All Users only available for priority broadcasts"""
    from bot.utils.nav_helpers import edit_or_send
    from config.settings import ADMIN_USER_IDS
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # Check if user has active priority slot or is admin
    has_priority = False
    if user_id:
        active_slot = priority_service.get_active_priority_slot()
        if active_slot and active_slot.get('user_id') == user_id:
            has_priority = True
        if user_id in ADMIN_USER_IDS:
            has_priority = True
    
    # Only show "All Users" for priority broadcasts or admins
    if has_priority:
        markup.add(
            types.InlineKeyboardButton("🌍 All Users", callback_data="target_all"),
            types.InlineKeyboardButton("📍 By Country", callback_data="target_country"),
            types.InlineKeyboardButton("📂 By Category", callback_data="target_category")
        )
        text = "Step 3: Select your target audience:"
    else:
        markup.add(
            types.InlineKeyboardButton("📍 By Country", callback_data="target_country"),
            types.InlineKeyboardButton("📂 By Category", callback_data="target_category")
        )
        text = "Step 3: Select your target audience:\n\n💡 Tip: Purchase a priority slot to broadcast to all users!"
    
    edit_or_send(bot, chat_id, text, message_id, markup)

def handle_broadcast_skip_media(bot, call):
    """Handle skip media callback"""
    user_id = call.from_user.id
    
    if user_id in user_broadcast_state:
        user_broadcast_state[user_id]['media_url'] = None
        user_broadcast_state[user_id]['media_type'] = None
        user_broadcast_state[user_id]['step'] = 'targeting'
        
        bot.answer_callback_query(call.id, "Media skipped")
        show_targeting_options(bot, call.message.chat.id, call.message.message_id, user_id=user_id)

def handle_target_selection(bot, call):
    """Handle target audience selection"""
    user_id = call.from_user.id
    target_type = call.data.replace('target_', '')
    
    if target_type == 'all':
        user_broadcast_state[user_id]['target_country'] = None
        user_broadcast_state[user_id]['target_category'] = None
        finalize_broadcast(bot, call.message.chat.id, user_id)
    elif target_type == 'country':
        user_broadcast_state[user_id]['target_type'] = 'country'
        show_country_targets(bot, call.message.chat.id, call.message.message_id)
    elif target_type == 'category':
        user_broadcast_state[user_id]['target_type'] = 'category'
        show_category_targets(bot, call.message.chat.id, call.message.message_id)
    
    bot.answer_callback_query(call.id)

def show_country_targets(bot, chat_id, message_id=None):
    """Show country targeting options"""
    from bot.utils.nav_helpers import edit_or_send
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    
    for country in COUNTRIES:
        buttons.append(types.InlineKeyboardButton(country, callback_data=f"targetc_{country}"))
    
    markup.add(*buttons)
    edit_or_send(bot, chat_id, "Select target country:", message_id, markup)

def show_category_targets(bot, chat_id, message_id=None):
    """Show category targeting options"""
    from bot.utils.nav_helpers import edit_or_send
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    
    for category in CATEGORIES:
        buttons.append(types.InlineKeyboardButton(category, callback_data=f"targetcat_{category}"))
    
    markup.add(*buttons)
    edit_or_send(bot, chat_id, "Select target category:", message_id, markup)

def handle_country_target(bot, call):
    """Handle country target selection"""
    user_id = call.from_user.id
    country = call.data.replace('targetc_', '')
    
    user_broadcast_state[user_id]['target_country'] = country
    user_broadcast_state[user_id]['target_category'] = None
    
    bot.answer_callback_query(call.id, f"✅ Targeting: {country}")
    finalize_broadcast(bot, call.message.chat.id, user_id, call.message.message_id)

def handle_category_target(bot, call):
    """Handle category target selection"""
    user_id = call.from_user.id
    category = call.data.replace('targetcat_', '')
    
    user_broadcast_state[user_id]['target_country'] = None
    user_broadcast_state[user_id]['target_category'] = category
    
    bot.answer_callback_query(call.id, f"✅ Targeting: {category}")
    finalize_broadcast(bot, call.message.chat.id, user_id, call.message.message_id)

def finalize_broadcast(bot, chat_id, user_id, message_id=None):
    """Finalize and save broadcast"""
    from bot.utils.nav_helpers import edit_or_send
    state = user_broadcast_state.get(user_id, {})
    
    broadcast = broadcast_service.create_broadcast(
        user_id=user_id,
        text=state.get('text'),
        media_url=state.get('media_url'),
        media_type=state.get('media_type'),
        target_country=state.get('target_country'),
        target_category=state.get('target_category')
    )
    
    if broadcast:
        broadcast_service.enforce_user_broadcast_limit(user_id)
        # Deduct points for non-admin users
        points_info = ""
        if not is_admin(user_id):
            points_required = ads_state.settings.get('points_required', 30)
            new_balance = user_service.deduct_points(user_id, points_required)
            if new_balance is not None:
                points_info = f"\n💰 Points deducted: -{points_required}\n💳 New balance: {new_balance} points"
                print(f"[BROADCAST] Deducted {points_required} points from user {user_id}. New balance: {new_balance}")
        
        target_desc = "All Users"
        if state.get('target_country'):
            target_desc = f"Country: {state['target_country']}"
        elif state.get('target_category'):
            target_desc = f"Category: {state['target_category']}"
        
        active_slot = priority_service.get_active_priority_slot()
        queue_status = ""
        if active_slot and active_slot['user_id'] != user_id:
            queue_status = "\n\n⏳ Note: Another user has an active priority slot. Your broadcast will be queued."
        
        text = f"✅ Broadcast created successfully!\n\n" \
               f"📝 ID: #{broadcast['broadcast_id']}\n" \
               f"🎯 Target: {target_desc}\n" \
               f"📊 Status: {broadcast['status']}{points_info}{queue_status}\n\n" \
               f"Your broadcast will be sent to users based on the queue."
        
        markup = types.InlineKeyboardMarkup()
        from bot.utils.nav_helpers import add_navigation_buttons
        add_navigation_buttons(markup, go_back=False, go_menu=True)
        
        edit_or_send(bot, chat_id, text, message_id, markup)
        
        del user_broadcast_state[user_id]
    else:
        bot.send_message(chat_id, "❌ Error creating broadcast. Please try again.")
