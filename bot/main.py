import telebot
from telebot import types
import time
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

from config.settings import TELEGRAM_BOT_TOKEN
from config.database import initialize_database, get_supabase_client
from bot.handlers import registration, broadcast_handlers, priority_handlers, menu_handler, analytics_handlers
from bot.services.broadcast_service import BroadcastService
from bot.services.priority_service import PrioritySlotService
from bot.services.user_service import UserService
from bot.services.ai_service import generate_broadcast_template

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None

broadcast_service = BroadcastService()
priority_service = PrioritySlotService()
user_service = UserService()

@bot.message_handler(commands=['start'])
def start_command(message):
    registration.handle_start(bot, message)

@bot.message_handler(commands=['menu'])
def menu_command(message):
    menu_handler.handle_menu(bot, message)

@bot.message_handler(commands=['create'])
def create_broadcast_command(message):
    broadcast_handlers.handle_create_broadcast(bot, message)

@bot.message_handler(commands=['priority'])
def priority_command(message):
    priority_handlers.handle_priority_slots(bot, message)

@bot.message_handler(commands=['mybroadcasts'])
def my_broadcasts_command(message):
    menu_handler.handle_my_broadcasts(bot, message)

@bot.message_handler(commands=['stats'])
def stats_command(message):
    menu_handler.handle_stats(bot, message)

@bot.message_handler(commands=['mystats'])
def mystats_command(message):
    """View detailed broadcast analytics"""
    analytics_handlers.handle_broadcast_analytics(bot, message)

@bot.message_handler(commands=['settings'])
def settings_command(message):
    menu_handler.handle_settings(bot, message)

@bot.message_handler(commands=['help'])
def help_command(message):
    menu_handler.handle_help(bot, message)

@bot.message_handler(commands=['ai_template'])
def ai_template_command(message):
    """Generate AI broadcast template"""
    user_id = message.from_user.id
    
    try:
        user = user_service.get_user(user_id)
    except:
        user = None
    
    if user and user.get('blocked'):
        bot.reply_to(message, "Access denied.")
        return
    
    bot.reply_to(message, "Generating AI template... Please wait.")
    
    topic = None
    country = None
    if user:
        cats = user.get('categories', user.get('category'))
        if isinstance(cats, list) and cats:
            topic = cats[0]
        else:
            topic = cats
        country = user.get('country')
    
    template = generate_broadcast_template(
        topic=topic,
        target_audience=f"{country} users" if country else None
    )
    
    if template:
        bot.send_message(message.chat.id,
            f"AI-Generated Template:\n\n{template}\n\n"
            f"Feel free to customize this template for your broadcast!")
    else:
        bot.send_message(message.chat.id, 
            "AI service is currently unavailable. Please try again later.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('country_'))
def country_callback(call):
    registration.handle_country_selection(bot, call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('cat_'))
def category_callback(call):
    registration.handle_category_selection(bot, call)

@bot.callback_query_handler(func=lambda call: call.data == 'broadcast_skip_media')
def skip_media_callback(call):
    broadcast_handlers.handle_broadcast_skip_media(bot, call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('target_'))
def target_callback(call):
    broadcast_handlers.handle_target_selection(bot, call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('targetc_'))
def target_country_callback(call):
    broadcast_handlers.handle_country_target(bot, call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('targetcat_'))
def target_category_callback(call):
    broadcast_handlers.handle_category_target(bot, call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('priority_'))
def priority_slot_callback(call):
    priority_handlers.handle_priority_slot_selection(bot, call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('analytics_'))
def analytics_callback(call):
    """Handle analytics callbacks"""
    if call.data.startswith('analytics_prev_') or call.data.startswith('analytics_next_'):
        analytics_handlers.handle_analytics_navigation(bot, call)
    elif call.data == 'analytics_close':
        analytics_handlers.handle_analytics_close(bot, call)
    else:
        bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'noop')
def noop_callback(call):
    """No-op callback for disabled buttons"""
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_'))
def payment_callback(call):
    priority_handlers.handle_payment_gateway_selection(bot, call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('menu_'))
def menu_callback(call):
    menu_action = call.data.replace('menu_', '')
    if menu_action == 'create':
        broadcast_handlers.handle_create_broadcast(bot, call.message)
    elif menu_action == 'priority':
        priority_handlers.handle_priority_slots(bot, call.message)
    elif menu_action == 'mybroadcasts':
        menu_handler.handle_my_broadcasts(bot, call.message)
    elif menu_action == 'stats':
        menu_handler.handle_stats(bot, call.message)
    elif menu_action == 'settings':
        menu_handler.handle_settings(bot, call.message)
    elif menu_action == 'help':
        menu_handler.handle_help(bot, call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('settings_'))
def settings_callback(call):
    setting = call.data.replace('settings_', '')
    user_id = call.from_user.id
    if setting == 'country':
        registration.show_country_selection(bot, call.message.chat.id)
    elif setting == 'category':
        registration.user_categories[user_id] = []
        registration.show_category_selection(bot, call.message.chat.id, user_id)

@bot.pre_checkout_query_handler(func=lambda query: True)
def handle_pre_checkout_query(pre_checkout_query):
    """Handle pre-checkout query for Telegram payments (Stars, Wallet, etc)"""
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def handle_successful_payment(message):
    """Handle successful Telegram Stars payment"""
    from bot.services.payment_service import PaymentService
    from bot.services.priority_service import PrioritySlotService
    user_id = message.from_user.id
    successful_payment = message.successful_payment
    payment_service = PaymentService()
    priority_service = PrioritySlotService()
    
    try:
        payload = successful_payment.invoice_payload
        if payload.startswith('slot_'):
            slot_id = int(payload.split('_')[1])
            transaction_id = successful_payment.telegram_payment_charge_id
            
            payment_service.update_payment_status(f"stars_pending_{slot_id}", 'completed')
            priority_service.activate_priority_slot(slot_id)
            
            bot.send_message(user_id,
                "✅ Payment Successful!\n\n"
                "Your priority slot is now ACTIVE.\n"
                "Use /create to send broadcasts that will be delivered immediately!")
    except Exception as e:
        print(f"Error handling successful payment: {e}")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id
    if user_id in broadcast_handlers.user_broadcast_state:
        if broadcast_handlers.user_broadcast_state[user_id]['step'] == 'text':
            broadcast_handlers.handle_broadcast_text_input(bot, message)
        else:
            bot.reply_to(message, "Please complete your current broadcast creation or use /menu to cancel.")
    else:
        bot.reply_to(message, "Use /menu to see available options.")

@bot.message_handler(content_types=['photo', 'video', 'document'])
def handle_media(message):
    user_id = message.from_user.id
    if user_id in broadcast_handlers.user_broadcast_state and broadcast_handlers.user_broadcast_state[user_id]['step'] == 'media':
        broadcast_handlers.handle_broadcast_media_input(bot, message)
    else:
        bot.reply_to(message, "Use /create to start a new broadcast.")

def process_broadcast_queue():
    """Background job to process broadcast queue"""
    try:
        priority_service.check_and_expire_slots()
        
        active_slot = priority_service.get_active_priority_slot()
        
        if active_slot:
            user_broadcasts = broadcast_service.get_queued_broadcasts()
            priority_user_broadcasts = [b for b in user_broadcasts if b['user_id'] == active_slot['user_id']]
            
            for broadcast in priority_user_broadcasts[:1]:
                send_broadcast(broadcast)
                
                if active_slot['slot_type'] == 'count':
                    priority_service.increment_slot_message_count(active_slot['slot_id'])
                    priority_service.check_and_expire_slots()
        else:
            queued_broadcasts = broadcast_service.get_queued_broadcasts()
            if queued_broadcasts:
                send_broadcast(queued_broadcasts[0])
    
    except Exception as e:
        print(f"Queue processing error: {e}")

def send_broadcast(broadcast):
    """Send a broadcast to targeted users"""
    try:
        target_users = user_service.get_all_users(
            active_only=True,
            target_country=broadcast.get('target_country'),
            target_category=broadcast.get('target_category')
        )
        
        sent_count = 0
        for user in target_users:
            try:
                if broadcast.get('media_url') and broadcast.get('media_type'):
                    if broadcast['media_type'] == 'photo':
                        bot.send_photo(user['user_id'], broadcast['media_url'], caption=broadcast['text'])
                    elif broadcast['media_type'] == 'video':
                        bot.send_video(user['user_id'], broadcast['media_url'], caption=broadcast['text'])
                    elif broadcast['media_type'] == 'document':
                        bot.send_document(user['user_id'], broadcast['media_url'], caption=broadcast['text'])
                else:
                    bot.send_message(user['user_id'], broadcast['text'])
                
                sent_count += 1
            except Exception as e:
                print(f"Error sending to user {user['user_id']}: {e}")
        
        broadcast_service.update_broadcast_status(broadcast['broadcast_id'], 'sent')
        broadcast_service.increment_broadcast_stats(broadcast['broadcast_id'], sent_count=sent_count, views=sent_count)
        
        print(f"✓ Broadcast #{broadcast['broadcast_id']} sent to {sent_count} users")
    
    except Exception as e:
        print(f"Broadcast sending error: {e}")

def main():
    """Main bot function"""
    if not bot:
        print("❌ Error: TELEGRAM_BOT_TOKEN not set")
        print("Please set up your environment variables:")
        print("- TELEGRAM_BOT_TOKEN")
        print("- SUPABASE_URL")
        print("- SUPABASE_KEY")
        return
    
    print("🤖 Telegram Broadcast Bot Starting...")
    
    if initialize_database():
        print("✓ Database initialized")
    else:
        print("⚠️  Database initialization skipped - configure Supabase first")
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(process_broadcast_queue, 'interval', seconds=30)
    scheduler.start()
    print("✓ Broadcast queue processor started")
    
    print("✓ Bot is running... Press Ctrl+C to stop")
    bot.infinity_polling()

if __name__ == '__main__':
    main()
