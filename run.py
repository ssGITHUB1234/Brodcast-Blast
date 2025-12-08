#!/usr/bin/env python3
"""
Main entry point for the Telegram Broadcast Bot
Runs both the bot and Flask admin dashboard
"""

import os
import sys
import threading

def run_bot():
    """Run the Telegram bot in background"""
    from bot.main import main
    try:
        main()
    except Exception as e:
        print(f"❌ Bot error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 TELEGRAM BROADCAST BOT - PRIORITY SLOT SYSTEM")
    print("=" * 60)
    print()
    
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    supabase_url = os.getenv('SUPABASE_URL', '')
    supabase_key = os.getenv('SUPABASE_KEY', '')
    is_production = bool(os.getenv('RENDER', False))
    
    dashboard_only_mode = False
    
    if not telegram_token or not supabase_url or not supabase_key:
        print("⚠️ DASHBOARD-ONLY MODE")
        print()
        print("Some environment variables are missing.")
        print("Starting dashboard without bot functionality.")
        print()
        print("Missing:")
        if not telegram_token:
            print("  - TELEGRAM_BOT_TOKEN")
        if not supabase_url:
            print("  - SUPABASE_URL")
        if not supabase_key:
            print("  - SUPABASE_KEY")
        print()
        print("The dashboard will start, but bot features won't work.")
        print("Set these in the Secrets tab to enable full functionality.")
        print()
        dashboard_only_mode = True
    
    print("✓ Configuration loaded")
    print(f"✓ Environment: {'PRODUCTION (Render)' if is_production else 'LOCAL DEV'}")
    print()
    print("📊 Admin Dashboard will be available at:")
    print("   http://localhost:5000")
    print()
    print("🤖 Telegram Bot Status:")
    skip_bot_polling = os.getenv('SKIP_BOT_POLLING', '').lower() == 'true'
    if is_production:
        print("   ✓ Webhook mode enabled (Render)")
        print("   ✓ Bot ready for Telegram webhook updates")
    elif skip_bot_polling:
        print("   ✓ Polling disabled (dashboard-only mode)")
    else:
        print("   ✓ Starting polling mode (local dev)...")
    print()
    print("=" * 60)
    print()
    
    # Only start bot thread on local dev (polling mode) if not explicitly disabled
    # On Render (webhook mode), Flask webhook handler receives updates
    if not dashboard_only_mode and not is_production and not skip_bot_polling:
        bot_thread = threading.Thread(target=run_bot, daemon=False)
        bot_thread.start()
    elif dashboard_only_mode:
        print("   ⚠️ Bot not started (dashboard-only mode)")
    
    # Register Telegram webhook and start scheduler for production (Render)
    if is_production and not dashboard_only_mode:
        try:
            import telebot
            bot = telebot.TeleBot(telegram_token)
            
            # Get Render external URL (automatically provided by Render)
            render_url = os.getenv('RENDER_EXTERNAL_URL', '')
            webhook_url_env = os.getenv('WEBHOOK_URL', '')
            
            # Use WEBHOOK_URL if set, otherwise construct from RENDER_EXTERNAL_URL
            if webhook_url_env:
                webhook_url = webhook_url_env.rstrip('/') + '/api/webhook/telegram'
            elif render_url:
                webhook_url = render_url.rstrip('/') + '/api/webhook/telegram'
            else:
                print("   ⚠️ No RENDER_EXTERNAL_URL or WEBHOOK_URL found - webhook not set")
                webhook_url = None
            
            if webhook_url:
                # Delete any existing webhook first
                bot.delete_webhook()
                # Set the new webhook
                result = bot.set_webhook(
                    url=webhook_url,
                    allowed_updates=["message", "callback_query"]
                )
                if result:
                    print(f"   ✓ Webhook registered: {webhook_url}")
                else:
                    print(f"   ⚠️ Failed to register webhook: {webhook_url}")
        except Exception as e:
            print(f"   ⚠️ Webhook registration error: {e}")
        
        # Start the background scheduler for broadcast processing on Render
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from bot.main import process_broadcast_queue, cleanup_expired_invoices, cleanup_expired_broadcasts
            
            scheduler = BackgroundScheduler()
            scheduler.add_job(process_broadcast_queue, 'interval', seconds=30)
            scheduler.add_job(cleanup_expired_invoices, 'interval', seconds=60)
            scheduler.add_job(cleanup_expired_broadcasts, 'interval', minutes=5)
            scheduler.start()
            print("   ✓ Broadcast queue processor started")
            print("   ✓ Background scheduler running")
        except Exception as e:
            print(f"   ⚠️ Scheduler error: {e}")
            import traceback
            traceback.print_exc()
    
    # Run Flask as main app
    from backend.app import app
    from config.settings import FLASK_HOST, FLASK_PORT
    
    port = int(os.getenv('PORT', FLASK_PORT))
    print(f"✓ Starting Flask server on {FLASK_HOST}:{port}")
    try:
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        print("✓ Stopped")
