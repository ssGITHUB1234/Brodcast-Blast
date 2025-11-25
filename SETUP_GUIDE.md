# 🚀 Quick Setup Guide

Follow these steps to get your Telegram Broadcast Bot running:

## Step 1: Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the **Bot Token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Step 2: Set Up Supabase Database

1. Go to [supabase.com](https://supabase.com) and create a free account
2. Create a new project
3. Wait for the project to be ready (~2 minutes)
4. Go to **Settings** → **API**
5. Copy:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon/public key** (the long key under "Project API keys")
6. Go to **SQL Editor** (left sidebar)
7. Click **New Query**
8. Copy and paste the entire contents of `setup_database.sql`
9. Click **Run** to execute

## Step 3: Get Your Telegram User ID (For Admin Access)

1. Open Telegram and search for **@userinfobot**
2. Start the bot
3. It will show you your User ID (a number like `123456789`)
4. Copy this number

## Step 4: Configure Environment Variables

In Replit, go to the **Secrets** tab (🔒 icon in left sidebar) and add:

### Required:
- `TELEGRAM_BOT_TOKEN` - Your bot token from @BotFather
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon key

### Optional (but recommended):
- `OPENAI_API_KEY` - For AI features (get from openai.com)
- `ADMIN_USER_ID` - Your Telegram user ID for admin access

## Step 5: Test Your Bot

Once you've set up the environment variables, I'll start the bot for you!

You can then:
1. Open Telegram
2. Search for your bot (the username you created with @BotFather)
3. Send `/start` to begin

---

## 📊 What's Included

✅ User registration with country & category selection
✅ Broadcast creation with media support
✅ Priority slot system (time & count based)
✅ Payment gateway integration (demo mode)
✅ Admin dashboard API
✅ AI-powered templates (if OpenAI key provided)
✅ Analytics tracking
✅ Auto-queue management

---

## 🔗 Useful Links

- Telegram Bot API: https://core.telegram.org/bots
- Supabase Docs: https://supabase.com/docs
- OpenAI API: https://platform.openai.com/api-keys

---

## ❓ Need Help?

Check the main README.md for detailed documentation!
