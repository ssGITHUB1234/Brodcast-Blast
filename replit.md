# Telegram Broadcast Bot with Priority Slots

## Overview
A comprehensive Telegram broadcast bot that allows users to send broadcasts to targeted audiences. The unique feature is a **priority broadcast slot system** where users can pay to temporarily block other broadcasts and ensure exclusive delivery for a specific time period or number of messages.

## Features
- **User Registration**: Country and interest category selection via inline buttons
- **Free Broadcasts**: Users can create and queue broadcasts with text and media
- **Priority Slot System**: 
  - Time-based (e.g., 24 hours exclusive)
  - Count-based (e.g., next 10 broadcasts only)
- **Multi-Gateway Payments**: Stars, CryptoPay, X Rocket, Telegram Wallet
- **Admin Dashboard**: Monitor users, broadcasts, revenue, and analytics
- **Analytics**: Track views, engagement, and delivery success
- **AI Features**: OpenAI-powered broadcast template generation
- **Monetag Ads**: Optional ad integration for revenue

## Tech Stack
- **Bot**: Python with pyTelegramBotAPI
- **Backend**: Flask
- **Frontend**: React with Vite
- **Database**: Supabase (PostgreSQL)
- **AI**: OpenAI API
- **Deployment**: Render-ready

## Project Structure
```
/
├── bot/                    # Telegram bot
│   ├── main.py            # Bot entry point
│   ├── handlers/          # Command and callback handlers
│   ├── services/          # Business logic
│   └── utils/             # Helper functions
├── backend/               # Flask API
│   ├── app.py            # Flask app
│   ├── routes/           # API endpoints
│   └── models/           # Data models
├── frontend/              # React dashboard
│   └── src/
├── config/               # Configuration files
└── requirements.txt      # Python dependencies
```

## Database Schema
- **users**: User registration and status
- **broadcasts**: Broadcast messages and metadata
- **priority_slots**: Priority broadcast reservations
- **analytics**: View and engagement tracking
- **payments**: Payment transaction logs
- **admin_logs**: Administrative action logs

## Recent Changes
- 2024-11-27: **Admin Monetag Ad Links Management Complete** - Direct links from Monetag
  - ✅ Admin pastes direct Monetag links (from Monetag Direct Links page)
  - ✅ Add, edit, delete ad links
  - ✅ Optional friendly names for each link
  - ✅ Full link validation before adding
  - ✅ UI in dashboard "Ad Settings" tab - "Monetag Ad Links" section
  - ✅ Works with any Monetag link (Dreamy, Perfect, Lovely, etc.)
- 2024-11-27: **Mandatory Ads Before Broadcast Complete** - Full ad requirement system
  - ✅ Users must watch ad before creating broadcasts
  - ✅ Admin can toggle ads requirement on/off
  - ✅ Ad status tracked per user session
  - ✅ Broadcast creation blocked until ad viewed
  - ✅ Admin Dashboard "Ad Settings" tab for control
- 2024-11-27: **Monetag Ads System Complete** - Full ad integration
  - ✅ `/ads` command for users to watch ads
  - ✅ Two ad formats: Rewarded Interstitial & Popup
  - ✅ Main menu button for easy access
  - ✅ Admin dashboard SDK loaded
  - ✅ Monetag Zone: 10243712
- 2024-11-27: **Chat Analysis Dashboard Complete** - Added pie/bar charts for analytics
  - 📊 Top Paying Users as Bar Chart - shows revenue by user
  - 📊 Top Broadcasting Users as Pie Chart - shows broadcast distribution
  - Ban/Unban controls for each user with instant status updates
  - Chart.js integration for interactive visualizations
- 2024-11-27: **Broadcast Pagination Complete** - 1 broadcast per page with nav buttons
- 2024-11-27: **Message Editing System Complete** - Fixed duplicate messages on button clicks
  - All button interactions now UPDATE existing messages instead of creating new ones ✅
  - Implemented `edit_or_send` helper function with fallback to new messages if edit fails
  - Fixed priority slot handler duplicate message bug (was sending 2 messages)
  - Message ID tracking through all callback handlers for smooth navigation
  - No more message spam in user chats - cleaner UX
- 2024-11-27: **Navigation System Complete** - Full menu + back buttons on all screens
  - Main menu button on all interactive messages
  - Back button for payment pages
  - State tracking via state_manager.py for user context
- 2024-11-27: **Payment Integration Complete** - Integrated 2 payment methods
  - ⭐ Telegram Stars (XTR currency) - sendInvoice via Bot API ✅
  - 💳 CryptoPay (USDT, TON, BTC, ETH, LTC, BNB, TRX, USDC) - REST API + webhooks ✅
  - Pre-checkout query handling for Telegram payments
  - Webhook handlers for payment confirmation and auto-activation
  - Payment recording and status tracking in database
- 2024-11-27: Fixed Row Level Security (RLS) blocking data persistence - disabled RLS on all tables
- 2024-11-27: Updated database schema to support categories as TEXT[] array for multi-category selection
- 2024-11-27: Improved error handling across all handlers for graceful database operation
- 2024-11-27: Added Sri Lanka and 7 additional countries to country list
- 2024-11-27: Added Crypto, Marketing, Real Estate, Automotive categories
- 2024-11-25: Initial project setup

## User Preferences
- Priority broadcast system (no admin approval needed)
- Payment only for exclusive broadcast slots, not per broadcast
- Auto-queue management when priority slots are active

## Environment Variables & Secrets Configured
✅ **TELEGRAM_BOT_TOKEN** - Bot authentication
✅ **SUPABASE_URL** - Database connection
✅ **SUPABASE_KEY** - Database authentication
✅ **OPENAI_API_KEY** - AI template generation
✅ **CRYPTOPAY_API_KEY** - CryptoPay integration
✅ **XROCKET_API_KEY** - xRocket payment integration
✅ **SESSION_SECRET** - Session management

## Optional/Future Variables
- STARS_API_KEY - For Telegram Stars (handled via bot API)
- MONETAG_SDK_KEY - For Monetag ad integration (zone: 10243712)
