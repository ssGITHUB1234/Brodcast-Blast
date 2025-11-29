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
    is_production = bool(os.getenv('RENDER', False))
    
    if not telegram_token or not supabase_url:
        print("❌ CONFIGURATION ERROR")
        print()
        print("Required environment variables are missing!")
        print()
        print("Please set the following:")
        print("  - TELEGRAM_BOT_TOKEN: Get from @BotFather on Telegram")
        print("  - SUPABASE_URL: Your Supabase project URL")
        print("  - SUPABASE_KEY: Your Supabase anon key")
        print()
        print("Optional (but recommended):")
        print("  - OPENAI_API_KEY: For AI-powered features")
        print("  - ADMIN_USER_ID: Your Telegram user ID for admin access")
        print()
        print("Copy .env.example to .env and fill in your values.")
        print()
        sys.exit(1)
    
    print("✓ Configuration loaded")
    print(f"✓ Environment: {'PRODUCTION (Render)' if is_production else 'LOCAL DEV'}")
    print()
    print("📊 Admin Dashboard will be available at:")
    print("   http://localhost:5000")
    print()
    print("🤖 Telegram Bot Status:")
    if is_production:
        print("   ✓ Webhook mode enabled (Render)")
        print("   ✓ Bot ready for Telegram webhook updates")
    else:
        print("   ✓ Starting polling mode (local dev)...")
    print()
    print("=" * 60)
    print()
    
    # Only start bot thread on local dev (polling mode)
    # On Render (webhook mode), Flask webhook handler receives updates
    if not is_production:
        bot_thread = threading.Thread(target=run_bot, daemon=False)
        bot_thread.start()
    
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
