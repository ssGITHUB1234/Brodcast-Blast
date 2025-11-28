"""Payment handling for priority slots"""
from telebot import types

def handle_payment_cancel(bot, call):
    """Cancel payment and return to menu"""
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
