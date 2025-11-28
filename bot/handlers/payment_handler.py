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
        from bot.handlers.menu_handler import handle_menu
        # Create a fake message object from callback
        class FakeMessage:
            def __init__(self, callback):
                self.from_user = callback.from_user
                self.chat = callback.message.chat
                self.message_id = callback.message.message_id
        
        msg = FakeMessage(call)
        handle_menu(bot, msg)
        bot.answer_callback_query(call.id, "Payment cancelled")
    except Exception as e:
        print(f"Error cancelling payment: {e}")
        bot.answer_callback_query(call.id, "Cancelled")
