from telebot import types
from bot.services.priority_service import PrioritySlotService
from bot.services.user_service import UserService
from config.settings import PRIORITY_SLOT_PRICES
from bot.utils.helpers import format_price, get_slot_description

priority_service = PrioritySlotService()
user_service = UserService()

def handle_priority_slots(bot, message):
    """Show priority slot options"""
    user_id = message.from_user.id
    user = user_service.get_user(user_id)
    
    if not user or user.get('blocked'):
        bot.reply_to(message, "⛔ You don't have permission to use this feature.")
        return
    
    active_slot = priority_service.get_active_priority_slot()
    
    if active_slot and active_slot['user_id'] == user_id:
        show_active_slot_info(bot, message.chat.id, active_slot)
    else:
        show_priority_slot_packages(bot, message.chat.id, active_slot)

def show_priority_slot_packages(bot, chat_id, active_slot=None):
    """Show available priority slot packages"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    active_msg = ""
    if active_slot:
        active_msg = "\n⚠️ Note: Another user currently has an active priority slot.\n\n"
    
    markup.add(
        types.InlineKeyboardButton(
            f"⏱️ 1 Hour - {format_price(PRIORITY_SLOT_PRICES['time_1h'])}",
            callback_data="priority_time_1h"
        ),
        types.InlineKeyboardButton(
            f"⏱️ 6 Hours - {format_price(PRIORITY_SLOT_PRICES['time_6h'])}",
            callback_data="priority_time_6h"
        ),
        types.InlineKeyboardButton(
            f"⏱️ 12 Hours - {format_price(PRIORITY_SLOT_PRICES['time_12h'])}",
            callback_data="priority_time_12h"
        ),
        types.InlineKeyboardButton(
            f"⏱️ 24 Hours - {format_price(PRIORITY_SLOT_PRICES['time_24h'])}",
            callback_data="priority_time_24h"
        ),
        types.InlineKeyboardButton(
            f"📊 5 Broadcasts - {format_price(PRIORITY_SLOT_PRICES['count_5'])}",
            callback_data="priority_count_5"
        ),
        types.InlineKeyboardButton(
            f"📊 10 Broadcasts - {format_price(PRIORITY_SLOT_PRICES['count_10'])}",
            callback_data="priority_count_10"
        ),
        types.InlineKeyboardButton(
            f"📊 25 Broadcasts - {format_price(PRIORITY_SLOT_PRICES['count_25'])}",
            callback_data="priority_count_25"
        ),
        types.InlineKeyboardButton(
            f"📊 50 Broadcasts - {format_price(PRIORITY_SLOT_PRICES['count_50'])}",
            callback_data="priority_count_50"
        )
    )
    
    bot.send_message(chat_id,
        f"🌟 Priority Broadcast Slots\n\n"
        f"{active_msg}"
        f"Get exclusive broadcast rights!\n"
        f"When you have an active priority slot, all other broadcasts are paused and only your messages are sent.\n\n"
        f"Choose your package:",
        reply_markup=markup)

def show_active_slot_info(bot, chat_id, slot):
    """Show active slot information"""
    if slot['slot_type'] == 'time':
        remaining = "Check /mystatus for details"
        desc = get_slot_description('time', duration_hours=slot['duration_hours'])
    else:
        remaining_count = slot['message_count'] - slot['messages_sent']
        remaining = f"{remaining_count} broadcasts remaining"
        desc = get_slot_description('count', message_count=slot['message_count'])
    
    bot.send_message(chat_id,
        f"✨ Your Priority Slot is Active!\n\n"
        f"📦 Package: {desc}\n"
        f"📊 {remaining}\n\n"
        f"All your broadcasts will be sent immediately, and other users' broadcasts are queued.")

def handle_priority_slot_selection(bot, call):
    """Handle priority slot package selection"""
    user_id = call.from_user.id
    slot_data = call.data.replace('priority_', '')
    
    active_slot = priority_service.get_active_priority_slot()
    if active_slot and active_slot['user_id'] != user_id:
        bot.answer_callback_query(call.id, 
            "⚠️ Another user has an active slot. You can still purchase for later use.",
            show_alert=True)
    
    if slot_data.startswith('time_'):
        hours = int(slot_data.split('_')[1].replace('h', ''))
        price = PRIORITY_SLOT_PRICES[slot_data]
        show_payment_options(bot, call.message.chat.id, user_id, 'time', price, duration_hours=hours)
    elif slot_data.startswith('count_'):
        count = int(slot_data.split('_')[1])
        price = PRIORITY_SLOT_PRICES[slot_data]
        show_payment_options(bot, call.message.chat.id, user_id, 'count', price, message_count=count)

def show_payment_options(bot, chat_id, user_id, slot_type, price, duration_hours=None, message_count=None):
    """Show payment gateway options"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    slot_desc = get_slot_description(slot_type, duration_hours, message_count)
    
    slot_data = f"{slot_type}_{duration_hours if duration_hours else message_count}"
    
    markup.add(
        types.InlineKeyboardButton("⭐ Telegram Stars", callback_data=f"pay_stars_{slot_data}"),
        types.InlineKeyboardButton("💳 CryptoPay", callback_data=f"pay_crypto_{slot_data}"),
        types.InlineKeyboardButton("🚀 X Rocket", callback_data=f"pay_xrocket_{slot_data}"),
        types.InlineKeyboardButton("💰 Telegram Wallet", callback_data=f"pay_wallet_{slot_data}")
    )
    
    bot.send_message(chat_id,
        f"💰 Payment Required\n\n"
        f"Package: {slot_desc}\n"
        f"Price: {format_price(price)}\n\n"
        f"Select your payment method:",
        reply_markup=markup)

def handle_payment_gateway_selection(bot, call):
    """Handle payment gateway selection"""
    user_id = call.from_user.id
    payment_data = call.data.replace('pay_', '')
    
    gateway, slot_info = payment_data.split('_', 1)
    slot_parts = slot_info.split('_')
    slot_type = slot_parts[0]
    value = int(slot_parts[1])
    
    if slot_type == 'time':
        duration_hours = value
        message_count = None
        price = PRIORITY_SLOT_PRICES[f'time_{value}h']
    else:
        duration_hours = None
        message_count = value
        price = PRIORITY_SLOT_PRICES[f'count_{value}']
    
    slot = priority_service.create_priority_slot(
        user_id=user_id,
        slot_type=slot_type,
        price=price,
        duration_hours=duration_hours,
        message_count=message_count,
        payment_gateway=gateway
    )
    
    if slot:
        bot.answer_callback_query(call.id, "Processing payment...")
        
        bot.send_message(call.message.chat.id,
            f"💳 Payment Gateway: {gateway.upper()}\n\n"
            f"⚠️ DEMO MODE: Payment integration is being processed.\n\n"
            f"In production, you would be redirected to {gateway} payment page.\n\n"
            f"For demonstration, I'll activate your priority slot now...")
        
        priority_service.activate_priority_slot(slot['slot_id'])
        
        bot.send_message(call.message.chat.id,
            f"✅ Priority Slot Activated!\n\n"
            f"Your exclusive broadcast window is now active.\n"
            f"Use /create to send broadcasts that will be delivered immediately!")
    else:
        bot.answer_callback_query(call.id, "❌ Error processing request", show_alert=True)
