from telebot import types
from config.settings import COUNTRIES, CATEGORIES
from bot.services.user_service import UserService

user_service = UserService()

def handle_start(bot, message):
    """Handle /start command"""
    user_id = message.from_user.id
    user = user_service.get_user(user_id)
    
    if user:
        if user.get('blocked'):
            bot.reply_to(message, "⛔ You have been blocked by an administrator.")
            return
        
        if user.get('country') and user.get('category'):
            bot.reply_to(message, 
                f"Welcome back, {message.from_user.first_name}! 👋\n\n"
                f"Your profile:\n"
                f"🌍 Country: {user['country']}\n"
                f"📂 Interest: {user['category']}\n\n"
                f"Use /menu to see all options.")
            return
    else:
        user_service.create_user(
            user_id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name
        )
    
    bot.reply_to(message,
        f"Welcome to the Broadcast Bot, {message.from_user.first_name}! 🎉\n\n"
        "Let's get you registered. First, please select your country:")
    
    show_country_selection(bot, message.chat.id)

def show_country_selection(bot, chat_id):
    """Show country selection keyboard"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    
    for country in COUNTRIES:
        buttons.append(types.InlineKeyboardButton(country, callback_data=f"country_{country}"))
    
    markup.add(*buttons)
    bot.send_message(chat_id, "🌍 Select your country:", reply_markup=markup)

def handle_country_selection(bot, call):
    """Handle country selection callback"""
    country = call.data.replace('country_', '')
    user_id = call.from_user.id
    
    user_service.update_user(user_id, country=country)
    
    bot.edit_message_text(
        f"✅ Country set to: {country}\n\nNow, select your interest category:",
        call.message.chat.id,
        call.message.message_id
    )
    
    show_category_selection(bot, call.message.chat.id)

def show_category_selection(bot, chat_id):
    """Show category selection keyboard"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    
    for category in CATEGORIES:
        buttons.append(types.InlineKeyboardButton(category, callback_data=f"category_{category}"))
    
    markup.add(*buttons)
    bot.send_message(chat_id, "📂 Select your interest category:", reply_markup=markup)

def handle_category_selection(bot, call):
    """Handle category selection callback"""
    category = call.data.replace('category_', '')
    user_id = call.from_user.id
    
    user_service.update_user(user_id, category=category)
    
    bot.edit_message_text(
        f"✅ Category set to: {category}\n\n"
        f"🎊 Registration complete! You can now use all features.\n\n"
        f"Use /menu to see available options.",
        call.message.chat.id,
        call.message.message_id
    )
