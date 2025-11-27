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
            try:
                bot.edit_message_text(text, chat_id, message_id, reply_markup=reply_markup)
                return None
            except Exception as edit_error:
                # If edit fails (e.g., message too old), send new message
                if "message to edit not found" in str(edit_error).lower() or "message not modified" in str(edit_error).lower():
                    return bot.send_message(chat_id, text, reply_markup=reply_markup)
                raise
        else:
            return bot.send_message(chat_id, text, reply_markup=reply_markup)
    except Exception as e:
        print(f"Message operation error: {e}")
        if not message_id:
            return bot.send_message(chat_id, text, reply_markup=reply_markup)
