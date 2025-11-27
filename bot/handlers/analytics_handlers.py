"""Broadcast analytics handlers"""
from telebot import types
from bot.services.broadcast_service import BroadcastService
from bot.services.user_service import UserService

broadcast_service = BroadcastService()
user_service = UserService()

# Store user's current broadcast index for pagination
user_analytics_index = {}

def handle_broadcast_analytics(bot, message):
    """Show broadcast analytics with pagination"""
    user_id = message.from_user.id
    
    try:
        user = user_service.get_user(user_id)
        if user and user.get('blocked'):
            bot.reply_to(message, "Access denied.")
            return
        
        broadcasts = broadcast_service.get_user_broadcasts(user_id, limit=10)
        if not broadcasts:
            bot.reply_to(message, "You haven't created any broadcasts yet.\n\nUse /create to send your first broadcast!")
            return
        
        user_analytics_index[user_id] = 0
        show_broadcast_analytics(bot, message.chat.id, user_id, broadcasts, 0)
    except Exception as e:
        print(f"Error handling broadcast analytics: {e}")
        bot.reply_to(message, "Error loading analytics")

def show_broadcast_analytics(bot, chat_id, user_id, broadcasts, index):
    """Show single broadcast analytics with navigation"""
    if index < 0 or index >= len(broadcasts):
        return
    
    bc = broadcasts[index]
    total = len(broadcasts)
    
    # Calculate engagement
    engagement_rate = 0
    if bc.get('sent_count', 0) > 0:
        engagement_rate = (bc.get('views', 0) / bc.get('sent_count', 1)) * 100
    
    # Status emoji
    status_emoji = "✅" if bc['status'] == 'sent' else "⏳" if bc['status'] == 'queued' else "📝"
    
    # Message content
    text = bc.get('text', '(No text)')[:100]
    if len(bc.get('text', '')) > 100:
        text += "..."
    
    message_text = f"""📊 Broadcast Analytics ({index + 1}/{total})

{status_emoji} Status: {bc['status'].upper()}

📄 Message: {text}

📈 Statistics:
  • Views: {bc.get('views', 0)}
  • Recipients: {bc.get('sent_count', 0)}
  • Engagement: {engagement_rate:.1f}%

🎯 Target:
  • Country: {bc.get('target_country', 'All')}
  • Category: {bc.get('target_category', 'All')}

📅 Created: {bc.get('created_at', 'N/A')[:10]}
"""
    
    # Navigation buttons
    markup = types.InlineKeyboardMarkup(row_width=3)
    
    # Previous, info, next buttons
    prev_btn = types.InlineKeyboardButton("⬅️ Prev", callback_data=f"analytics_prev_{user_id}_{index}") if index > 0 else types.InlineKeyboardButton("⬅️", callback_data="dummy")
    next_btn = types.InlineKeyboardButton("Next ➡️", callback_data=f"analytics_next_{user_id}_{index}") if index < total - 1 else types.InlineKeyboardButton("➡️", callback_data="dummy")
    info_btn = types.InlineKeyboardButton(f"📋 {index + 1}/{total}", callback_data="dummy")
    
    markup.add(prev_btn, info_btn, next_btn)
    markup.add(types.InlineKeyboardButton("Close", callback_data="analytics_close"))
    
    try:
        bot.send_message(chat_id, message_text, reply_markup=markup)
    except:
        bot.send_message(chat_id, message_text)

def handle_analytics_navigation(bot, call):
    """Handle analytics navigation buttons"""
    data = call.data.split('_')
    action = data[1]
    
    try:
        user_id = int(data[2])
        current_index = int(data[3])
        
        broadcasts = broadcast_service.get_user_broadcasts(user_id, limit=10)
        
        if action == 'prev':
            new_index = max(0, current_index - 1)
        elif action == 'next':
            new_index = min(len(broadcasts) - 1, current_index + 1)
        else:
            return
        
        user_analytics_index[user_id] = new_index
        
        # Delete old message
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        
        # Show new analytics
        show_broadcast_analytics(bot, call.message.chat.id, user_id, broadcasts, new_index)
        
    except Exception as e:
        print(f"Error handling analytics navigation: {e}")

def handle_analytics_close(bot, call):
    """Close analytics view"""
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Analytics closed. Use /stats to view again.")
    except:
        pass
