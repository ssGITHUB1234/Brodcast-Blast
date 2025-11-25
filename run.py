#!/usr/bin/env python3
"""
Main entry point for the Telegram Broadcast Bot
Runs both the bot and Flask admin dashboard
"""

import os
import sys
from multiprocessing import Process

def run_bot():
    """Run the Telegram bot"""
    from bot.main import main
    main()

def run_flask():
    """Run the Flask admin dashboard"""
    from backend.app import app
    from config.settings import FLASK_HOST, FLASK_PORT
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False, use_reloader=False)

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 TELEGRAM BROADCAST BOT - PRIORITY SLOT SYSTEM")
    print("=" * 60)
    print()
    
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    supabase_url = os.getenv('SUPABASE_URL', '')
    
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
    print()
    print("📊 Admin Dashboard will be available at:")
    print("   http://localhost:5000")
    print()
    print("🤖 Telegram Bot Status:")
    print("   Starting...")
    print()
    print("=" * 60)
    print()
    
    flask_process = Process(target=run_flask)
    flask_process.start()
    
    try:
        run_bot()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        flask_process.terminate()
        flask_process.join()
        print("✓ Stopped")
