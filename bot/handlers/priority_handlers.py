from telebot import types
from bot.services.priority_service import PrioritySlotService
from bot.services.user_service import UserService
from bot.services.payment_service import PaymentService
from bot.services.stars_payment import StarsPaymentService
from bot.services.cryptopay import CryptoPayService
from bot.services.slot_type_service import SlotTypeService
from bot.utils.helpers import format_price, get_slot_description
from bot.utils.state_manager import set_user_state, get_user_message_id
from bot.utils.nav_helpers import add_navigation_buttons, edit_or_send

priority_service = PrioritySlotService()
user_service = UserService()
payment_service = PaymentService()
stars_service = StarsPaymentService()
cryptopay_service = CryptoPayService()
slot_type_service = SlotTypeService()

# Get dynamic pricing from backend
def get_priority_slot_prices():
    """Get pricing from backend (shared pricing_cache)"""
    try:
        from backend.app import pricing_cache
        return pricing_cache
    except ImportError:
        # Fallback to static pricing if backend not available
        from config.settings import PRIORITY_SLOT_PRICES
        return PRIORITY_SLOT_PRICES

def handle_priority_slots(bot, message):
    """Show priority slot options"""
    user_id = message.from_user.id
    
    try:
        user = user_service.get_user(user_id)
    except:
        user = None
    
    # Check if user is explicitly blocked
    if user and user.get('blocked'):
        bot.reply_to(message, "⛔ You don't have permission to use this feature.")
        return
    
    # Create user if doesn't exist
    if not user:
        try:
            user_service.create_user(
                user_id,
                message.from_user.username,
                message.from_user.first_name,
                message.from_user.last_name
            )
        except:
            pass
    
    active_slot = priority_service.get_active_priority_slot()
    
    if active_slot and active_slot['user_id'] == user_id:
        show_active_slot_info(bot, message.chat.id, user_id, active_slot, message.message_id)
    else:
        show_priority_slot_packages(bot, message.chat.id, user_id, active_slot, message.message_id)

def show_priority_slot_packages(bot, chat_id, user_id, active_slot=None, message_id=None):
    """Show available priority slot packages - only shows active/enabled slots"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    active_msg = ""
    if active_slot:
        active_msg = "\n⚠️ Note: Another user currently has an active priority slot.\n\n"
    
    # Get active time slots from database
    time_slots = slot_type_service.get_time_slots(active_only=True)
    for slot in time_slots:
        hours = slot.get('duration_hours', 0)
        price = float(slot.get('price', 0))
        display_name = slot.get('display_name', f"{hours} Hour{'s' if hours > 1 else ''}")
        markup.add(
            types.InlineKeyboardButton(
                f"⏱️ {display_name} - {format_price(price)}",
                callback_data=f"priority_time_{hours}h"
            )
        )
    
    # Get active count slots from database
    count_slots = slot_type_service.get_count_slots(active_only=True)
    for slot in count_slots:
        count = slot.get('message_count', 0)
        price = float(slot.get('price', 0))
        display_name = slot.get('display_name', f"{count} Broadcasts")
        markup.add(
            types.InlineKeyboardButton(
                f"📊 {display_name} - {format_price(price)}",
                callback_data=f"priority_count_{count}"
            )
        )
    
    add_navigation_buttons(markup, go_back=False, go_menu=True)
    
    # Check if there are any active slots
    if not time_slots and not count_slots:
        text = f"🌟 Priority Broadcast Slots\n\n" \
               f"No priority slots are currently available.\n" \
               f"Please check back later."
    else:
        text = f"🌟 Priority Broadcast Slots\n\n" \
               f"{active_msg}" \
               f"Get exclusive broadcast rights!\n" \
               f"When you have an active priority slot, all other broadcasts are paused and only your messages are sent.\n\n" \
               f"Choose your package:"
    
    result = edit_or_send(bot, chat_id, text, message_id, markup)
    if result:  # New message was sent
        set_user_state(user_id, result.message_id, 'priority')
    else:  # Message was edited
        set_user_state(user_id, message_id, 'priority')

def show_active_slot_info(bot, chat_id, user_id, slot, message_id=None):
    """Show active slot information"""
    if slot['slot_type'] == 'time':
        remaining = "Check /mystats for details"
        desc = get_slot_description('time', duration_hours=slot['duration_hours'])
    else:
        remaining_count = slot['message_count'] - slot['messages_sent']
        remaining = f"{remaining_count} broadcasts remaining"
        desc = get_slot_description('count', message_count=slot['message_count'])
    
    markup = types.InlineKeyboardMarkup()
    add_navigation_buttons(markup, go_back=False, go_menu=True)
    
    text = f"✨ Your Priority Slot is Active!\n\n" \
           f"📦 Package: {desc}\n" \
           f"📊 {remaining}\n\n" \
           f"All your broadcasts will be sent immediately, and other users' broadcasts are queued."
    
    result = edit_or_send(bot, chat_id, text, message_id, markup)
    if result:
        set_user_state(user_id, result.message_id, 'priority_active')
    else:
        set_user_state(user_id, message_id, 'priority_active')

def handle_priority_slot_selection(bot, call):
    """Handle priority slot package selection"""
    user_id = call.from_user.id
    slot_data = call.data.replace('priority_', '')
    
    active_slot = priority_service.get_active_priority_slot()
    if active_slot and active_slot['user_id'] != user_id:
        bot.answer_callback_query(call.id, 
            "⚠️ Another user has an active slot. You can still purchase for later use.",
            show_alert=True)
    
    PRICES = get_priority_slot_prices()
    if slot_data.startswith('time_'):
        hours = int(slot_data.split('_')[1].replace('h', ''))
        price = PRICES[slot_data]
        show_payment_options(bot, call.message.chat.id, user_id, 'time', price, duration_hours=hours, message_id=call.message.message_id)
    elif slot_data.startswith('count_'):
        count = int(slot_data.split('_')[1])
        price = PRICES[f'count_{count}']
        show_payment_options(bot, call.message.chat.id, user_id, 'count', price, message_count=count, message_id=call.message.message_id)
    
    bot.answer_callback_query(call.id)

def show_payment_options(bot, chat_id, user_id, slot_type, price, duration_hours=None, message_count=None, message_id=None):
    """Show payment gateway options"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    slot_desc = get_slot_description(slot_type, duration_hours, message_count)
    slot_data = f"{slot_type}_{duration_hours if duration_hours else message_count}"
    
    markup.add(
        types.InlineKeyboardButton("⭐ Telegram Stars", callback_data=f"pay_stars_{slot_data}"),
        types.InlineKeyboardButton("💳 CryptoPay", callback_data=f"pay_crypto_{slot_data}")
    )
    add_navigation_buttons(markup, go_back=True, go_menu=True)
    
    text = f"💰 Payment Required\n\n" \
           f"Package: {slot_desc}\n" \
           f"Price: {format_price(price)}\n\n" \
           f"Select your payment method:"
    
    result = edit_or_send(bot, chat_id, text, message_id, markup)
    if result:  # Only update state if new message was created
        set_user_state(user_id, result.message_id, 'payment')
    else:  # Edit happened
        set_user_state(user_id, message_id, 'payment')

def handle_payment_gateway_selection(bot, call):
    """Handle payment gateway selection"""
    user_id = call.from_user.id
    payment_data = call.data.replace('pay_', '')
    PRICES = get_priority_slot_prices()
    
    gateway, slot_info = payment_data.split('_', 1)
    slot_parts = slot_info.split('_')
    slot_type = slot_parts[0]
    value = int(slot_parts[1])
    
    if slot_type == 'time':
        duration_hours = value
        message_count = None
        price = PRICES[f'time_{value}h']
    else:
        duration_hours = None
        message_count = value
        price = PRICES[f'count_{value}']
    
    slot = priority_service.create_priority_slot(
        user_id=user_id,
        slot_type=slot_type,
        price=price,
        duration_hours=duration_hours,
        message_count=message_count,
        payment_gateway=gateway
    )
    
    if not slot:
        bot.answer_callback_query(call.id, "❌ Error processing request", show_alert=True)
        return
    
    slot_id = slot['slot_id']
    
    if gateway == 'stars':
        handle_stars_payment_init(bot, call, slot_id, slot, user_id)
    elif gateway == 'crypto':
        handle_cryptopay_init(bot, call, slot_id, slot, user_id)
    
    bot.answer_callback_query(call.id)


def handle_stars_payment_init(bot, call, slot_id, slot, user_id):
    """Initialize Telegram Stars payment"""
    try:
        title = f"{slot['slot_type'].capitalize()} Slot"
        if slot['slot_type'] == 'time':
            description = f"Priority broadcast for {slot['duration_hours']} hours"
        else:
            description = f"Priority broadcast for {slot['message_count']} messages"
        
        invoice = stars_service.send_invoice(
            user_id,
            slot_id,
            title,
            description,
            amount_usd=float(slot['price']),
            payload=f"slot_{slot_id}"
        )
        
        if invoice:
            bot.edit_message_text(
                "⭐ Check your Telegram app for the payment invoice.\n\n"
                "Click the Pay button to complete your purchase!",
                call.message.chat.id,
                call.message.message_id
            )
            payment_service.record_payment(user_id, slot_id, slot['price'], 'telegram_stars', f"stars_pending_{slot_id}", 'pending')
        else:
            bot.answer_callback_query(call.id, "Error sending invoice")
    except Exception as e:
        print(f"Error initiating Stars payment: {e}")
        bot.answer_callback_query(call.id, "Error processing payment")


def handle_cryptopay_init(bot, call, slot_id, slot, user_id):
    """Initialize CryptoPay payment"""
    try:
        description = f"Priority Slot #{slot_id}"
        invoice = cryptopay_service.create_invoice(slot['price'], description, slot_id, asset='USDT')
        
        if invoice:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("💳 Pay with Crypto", url=invoice['bot_invoice_url']))
            
            bot.edit_message_text(
                f"💳 CryptoPay Invoice\n\n"
                f"Amount: ${slot['price']}\n"
                f"Invoice ID: {invoice['invoice_id']}\n\n"
                f"Click the button below to pay:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup
            )
            payment_service.record_payment(user_id, slot_id, slot['price'], 'cryptopay', str(invoice['invoice_id']), 'pending')
        else:
            bot.answer_callback_query(call.id, "Error creating invoice")
    except Exception as e:
        print(f"Error initiating CryptoPay: {e}")
        bot.answer_callback_query(call.id, "Error processing payment")


