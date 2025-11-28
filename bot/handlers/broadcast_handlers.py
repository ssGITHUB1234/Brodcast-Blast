from telebot import types
from bot.services.broadcast_service import BroadcastService
from bot.services.user_service import UserService
from bot.services.priority_service import PrioritySlotService
from bot.services.monetag_service import MonetgService
from config.settings import COUNTRIES, CATEGORIES
from config import ads_state
import os

broadcast_service = BroadcastService()
user_service = UserService()
priority_service = PrioritySlotService()
monetag_service = MonetgService()

user_broadcast_state = {}
users_ads_watched = set()

def handle_create_broadcast(bot, message):
    """Start broadcast creation process - show ad if required"""
    user_id = message.from_user.id
    user = user_service.get_user(user_id)
    
    # Auto-register user if they don't exist
    if not user:
        try:
            user_service.create_user(
                user_id,
                message.from_user.username,
                message.from_user.first_name,
                message.from_user.last_name
            )
            bot.reply_to(message, f"Welcome! Quick registration:\n\nPlease use /start to select your country & interests.\n\nThen come back to /create")
            return
        except Exception as e:
            print(f"Auto-register error: {e}")
            bot.reply_to(message, "❌ Registration failed. Please try /start")
            return
    
    # Check if user is blocked
    if user.get('blocked'):
        bot.reply_to(message, "⛔ You have been blocked and cannot create broadcasts.")
        return
    
    # Check if user already watched ad in this session
    already_watched = ads_state.user_watched_ad(user_id)
    
    # Always require ads
    if not already_watched:
        domain = os.environ.get('REPLIT_DOMAIN', '').strip()
        
        # Only show ad button if we have a valid domain (not localhost)
        if domain and 'localhost' not in domain and domain != '':
            try:
                from backend.app import monetag_links
                if monetag_links and len(monetag_links) > 0:
                    link = monetag_links[0].get('link', '')
                    # URL encode to avoid & becoming &amp;
                    import urllib.parse
                    ad_viewer_url = f"https://{domain}/ad-viewer?user_id={user_id}&link={urllib.parse.quote(link, safe='')}"
                    
                    markup = types.InlineKeyboardMarkup()
                    markup.add(
                        types.InlineKeyboardButton("🎬 Watch Ad Now", url=ad_viewer_url)
                    )
                    bot.send_message(message.chat.id,
                        "🎬 Watch Ad to Unlock Broadcast\n\n"
                        "Click to watch - timer auto-completes!\n"
                        "⏱️ 30 seconds total\n\n"
                        "After watching, return here and click /create again.",
                        reply_markup=markup)
                    return
            except ImportError as e:
                print(f"[INFO] Backend monetag_links not available: {e}, allowing broadcast")
            except Exception as e:
                print(f"[ERROR] Error showing ad button: {e}")
        
        # No valid domain or ad failed - mark as watched and proceed
        users_ads_watched.add(user_id)
    
    # User watched ad or system failed - allow broadcast
    start_broadcast_creation(bot, message, user_id)

def start_broadcast_creation(bot, message, user_id):
    """Start the actual broadcast creation flow"""
    user_broadcast_state[user_id] = {'step': 'text'}
    bot.reply_to(message, 
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
        
        show_targeting_options(bot, message.chat.id)

def show_targeting_options(bot, chat_id, message_id=None):
    """Show targeting options"""
    from bot.utils.nav_helpers import edit_or_send
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🌍 All Users", callback_data="target_all"),
        types.InlineKeyboardButton("📍 By Country", callback_data="target_country"),
        types.InlineKeyboardButton("📂 By Category", callback_data="target_category")
    )
    
    text = "Step 3: Select your target audience:"
    edit_or_send(bot, chat_id, text, message_id, markup)

def handle_broadcast_skip_media(bot, call):
    """Handle skip media callback"""
    user_id = call.from_user.id
    
    if user_id in user_broadcast_state:
        user_broadcast_state[user_id]['media_url'] = None
        user_broadcast_state[user_id]['media_type'] = None
        user_broadcast_state[user_id]['step'] = 'targeting'
        
        bot.answer_callback_query(call.id, "Media skipped")
        show_targeting_options(bot, call.message.chat.id, call.message.message_id)

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
               f"📊 Status: {broadcast['status']}{queue_status}\n\n" \
               f"Your broadcast will be sent to users based on the queue."
        
        markup = types.InlineKeyboardMarkup()
        from bot.utils.nav_helpers import add_navigation_buttons
        add_navigation_buttons(markup, go_back=False, go_menu=True)
        
        edit_or_send(bot, chat_id, text, message_id, markup)
        
        del user_broadcast_state[user_id]
    else:
        bot.send_message(chat_id, "❌ Error creating broadcast. Please try again.")
