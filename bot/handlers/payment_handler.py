"""Payment handling for priority slots"""
from telebot import types
from bot.services.payment_service import PaymentService
from bot.services.stars_payment import StarsPaymentService
from bot.services.cryptopay import CryptoPayService
from bot.services.priority_service import PrioritySlotService

payment_service = PaymentService()
stars_service = StarsPaymentService()
cryptopay_service = CryptoPayService()
priority_service = PrioritySlotService()

def handle_priority_payment(bot, call):
    """Handle priority slot purchase button click"""
    user_id = call.from_user.id
    data_parts = call.data.split('_')
    
    if len(data_parts) < 3:
        bot.answer_callback_query(call.id, "Invalid selection")
        return
    
    slot_type = data_parts[1]
    duration = data_parts[2]
    slot_key = f"{slot_type}_{duration}"
    
    price = PRIORITY_SLOT_PRICES.get(slot_key)
    if not price:
        bot.answer_callback_query(call.id, "Invalid slot type")
        return
    
    try:
        # Create priority slot record
        if slot_type == 'time':
            duration_hours = int(duration)
            slot = priority_service.create_priority_slot(
                user_id,
                'time',
                price,
                duration_hours=duration_hours,
                payment_gateway='pending'
            )
        else:  # count
            message_count = int(duration)
            slot = priority_service.create_priority_slot(
                user_id,
                'count',
                price,
                message_count=message_count,
                payment_gateway='pending'
            )
        
        if not slot:
            bot.answer_callback_query(call.id, "Error creating slot")
            return
        
        slot_id = slot['slot_id']
        
        # Show payment method selection
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("⭐ Telegram Stars", callback_data=f"pay_stars_{slot_id}"),
            types.InlineKeyboardButton("🪙 CryptoPay", callback_data=f"pay_crypto_{slot_id}"),
            types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_payment")
        )
        
        bot.edit_message_text(
            f"Select payment method:\n\n"
            f"Amount: ${price}\n"
            f"Slot Type: {slot_type.capitalize()} - {duration}\n\n"
            f"Choose your preferred payment gateway:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Error handling priority payment: {e}")
        bot.answer_callback_query(call.id, "Error processing request")


def handle_stars_payment(bot, call):
    """Initiate Telegram Stars payment"""
    user_id = call.from_user.id
    slot_id = int(call.data.split('_')[2])
    
    try:
        slot = priority_service.get_priority_slot(slot_id)
        if not slot:
            bot.answer_callback_query(call.id, "Slot not found")
            return
        
        title = f"{slot['slot_type'].capitalize()} Slot"
        if slot['slot_type'] == 'time':
            description = f"Priority broadcast for {slot['duration_hours']} hours"
        else:
            description = f"Priority broadcast for {slot['message_count']} messages"
        
        # Send invoice (amount in USD, will be converted to Stars)
        stars_service.send_invoice(
            user_id,
            slot_id,
            title,
            description,
            amount_usd=float(slot['price']),
            payload=f"slot_{slot_id}"
        )
        
        bot.edit_message_text(
            "📱 Check your Telegram app for the payment invoice.\n\n"
            "Click the Pay button to complete your purchase!",
            call.message.chat.id,
            call.message.message_id
        )
        
        payment_service.record_payment(
            user_id,
            slot_id,
            slot['price'],
            'telegram_stars',
            f"stars_pending_{slot_id}",
            'pending'
        )
    except Exception as e:
        print(f"Error initiating Stars payment: {e}")
        bot.answer_callback_query(call.id, "Error sending invoice")


def handle_cryptopay_payment(bot, call):
    """Initiate CryptoPay payment"""
    user_id = call.from_user.id
    slot_id = int(call.data.split('_')[2])
    
    try:
        slot = priority_service.get_priority_slot(slot_id)
        if not slot:
            bot.answer_callback_query(call.id, "Slot not found")
            return
        
        description = f"Priority Slot #{slot_id}"
        
        # Create invoice
        invoice = cryptopay_service.create_invoice(
            slot['price'],
            description,
            slot_id,
            asset='USDT'
        )
        
        if not invoice:
            bot.answer_callback_query(call.id, "Error creating invoice")
            return
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            "💳 Pay with Crypto",
            url=invoice['bot_invoice_url']
        ))
        
        bot.edit_message_text(
            f"CryptoPay Invoice\n\n"
            f"Amount: ${slot['price']}\n"
            f"Invoice ID: {invoice['invoice_id']}\n\n"
            f"Click the button below to pay:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
        
        payment_service.record_payment(
            user_id,
            slot_id,
            slot['price'],
            'cryptopay',
            str(invoice['invoice_id']),
            'pending'
        )
    except Exception as e:
        print(f"Error initiating CryptoPay payment: {e}")
        bot.answer_callback_query(call.id, "Error creating invoice")




def handle_payment_cancel(bot, call):
    """Cancel payment"""
    try:
        bot.edit_message_text(
            "❌ Payment cancelled.\n\n"
            "Use /menu to return to main menu.",
            call.message.chat.id,
            call.message.message_id
        )
    except:
        pass
