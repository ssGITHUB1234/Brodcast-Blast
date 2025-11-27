"""Navigation helpers for consistent UI"""
from telebot import types

def add_navigation_buttons(markup, go_back=True, go_menu=True):
    """Add navigation buttons to keyboard"""
    nav_row = []
    if go_back:
        nav_row.append(types.InlineKeyboardButton("← Back", callback_data="nav_back"))
    if go_menu:
        nav_row.append(types.InlineKeyboardButton("🏠 Menu", callback_data="nav_menu"))
    
    if nav_row:
        markup.add(*nav_row)
    return markup

def edit_or_send(bot, chat_id, text, message_id=None, reply_markup=None):
    """Edit message if message_id exists, otherwise send new"""
    try:
        if message_id:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=reply_markup)
        else:
            return bot.send_message(chat_id, text, reply_markup=reply_markup)
    except Exception as e:
        print(f"Message operation error: {e}")
        # Fallback to send if edit fails
        if message_id:
            return bot.send_message(chat_id, text, reply_markup=reply_markup)
