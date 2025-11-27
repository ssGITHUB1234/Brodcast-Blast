from telebot import types
from config.settings import COUNTRIES, CATEGORIES
from bot.services.user_service import UserService

user_service = UserService()

user_categories = {}

def handle_start(bot, message):
    """Handle /start command"""
    user_id = message.from_user.id
    
    try:
        user = user_service.get_user(user_id)
    except:
        user = None
    
    if user:
        if user.get('blocked'):
            bot.reply_to(message, "You have been blocked by an administrator.")
            return
        
        if user.get('country') and user.get('categories'):
            cats = user['categories'] if isinstance(user['categories'], list) else [user['categories']]
            bot.reply_to(message, 
                f"Welcome back, {message.from_user.first_name}!\n\n"
                f"Your profile:\n"
                f"Country: {user['country']}\n"
                f"Interests: {', '.join(cats)}\n\n"
                f"Use /menu to see all options.")
            return
    
    try:
        user_service.create_user(
            user_id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name
        )
    except Exception as e:
        print(f"Could not create user in database: {e}")
    
    bot.reply_to(message,
        f"Welcome to the Broadcast Bot, {message.from_user.first_name}!\n\n"
        "Let's get you registered. First, please select your country:")
    
    show_country_selection(bot, message.chat.id)

def show_country_selection(bot, chat_id):
    """Show country selection keyboard"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    
    for country in COUNTRIES:
        buttons.append(types.InlineKeyboardButton(country, callback_data=f"country_{country[:20]}"))
    
    markup.add(*buttons)
    bot.send_message(chat_id, "Select your country:", reply_markup=markup)

def handle_country_selection(bot, call):
    """Handle country selection callback"""
    country = call.data.replace('country_', '')
    user_id = call.from_user.id
    
    for c in COUNTRIES:
        if c.startswith(country):
            country = c
            break
    
    try:
        user_service.update_user(user_id, country=country)
    except Exception as e:
        print(f"Could not update user country: {e}")
    
    bot.edit_message_text(
        f"Country set to: {country}\n\nNow, select your interest categories (you can select multiple):",
        call.message.chat.id,
        call.message.message_id
    )
    
    user_categories[user_id] = []
    show_category_selection(bot, call.message.chat.id, user_id)

def show_category_selection(bot, chat_id, user_id=None):
    """Show category selection keyboard with multi-select"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    
    selected = user_categories.get(user_id, []) if user_id else []
    
    for category in CATEGORIES:
        prefix = "✅ " if category in selected else ""
        buttons.append(types.InlineKeyboardButton(
            f"{prefix}{category}", 
            callback_data=f"cat_{category[:15]}"
        ))
    
    markup.add(*buttons)
    
    if selected:
        markup.add(types.InlineKeyboardButton(
            f"Done - Save {len(selected)} categories", 
            callback_data="cat_done"
        ))
    
    bot.send_message(chat_id, 
        f"Select your interest categories:\n"
        f"Selected: {len(selected)} categories\n"
        f"(Tap to select/deselect, then tap Done)",
        reply_markup=markup)

def handle_category_selection(bot, call):
    """Handle category selection callback"""
    user_id = call.from_user.id
    data = call.data.replace('cat_', '')
    
    if data == 'done':
        selected = user_categories.get(user_id, [])
        if not selected:
            bot.answer_callback_query(call.id, "Please select at least one category!")
            return
        
        try:
            user_service.update_user(user_id, categories=selected)
        except Exception as e:
            print(f"Could not update user categories: {e}")
        
        bot.edit_message_text(
            f"Categories set to: {', '.join(selected)}\n\n"
            f"Registration complete! You can now use all features.\n\n"
            f"Use /menu to see available options.",
            call.message.chat.id,
            call.message.message_id
        )
        
        if user_id in user_categories:
            del user_categories[user_id]
        return
    
    for cat in CATEGORIES:
        if cat.startswith(data) or cat[:15] == data:
            data = cat
            break
    
    if user_id not in user_categories:
        user_categories[user_id] = []
    
    if data in user_categories[user_id]:
        user_categories[user_id].remove(data)
        bot.answer_callback_query(call.id, f"Removed: {data}")
    else:
        user_categories[user_id].append(data)
        bot.answer_callback_query(call.id, f"Added: {data}")
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    selected = user_categories[user_id]
    
    for category in CATEGORIES:
        prefix = "✅ " if category in selected else ""
        buttons.append(types.InlineKeyboardButton(
            f"{prefix}{category}", 
            callback_data=f"cat_{category[:15]}"
        ))
    
    markup.add(*buttons)
    
    if selected:
        markup.add(types.InlineKeyboardButton(
            f"Done - Save {len(selected)} categories", 
            callback_data="cat_done"
        ))
    
    try:
        bot.edit_message_text(
            f"Select your interest categories:\n"
            f"Selected: {len(selected)} - {', '.join(selected)}\n"
            f"(Tap to select/deselect, then tap Done)",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    except:
        pass
