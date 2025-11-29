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

## Recent Changes (Nov 29, 2025)
- ✅ **CRITICAL FIX: Registration Now Saves Correctly** 🔧
  - Fixed Supabase update query order in user_service.py
  - Changed: `.update(kwargs).eq('user_id', user_id)` → `.eq('user_id', user_id).update(kwargs)`
  - Users can now complete registration (country + categories)
  - Can now create broadcasts after registration ✅
- ✅ **RENDER DEPLOYMENT COMPLETE** 🚀
  - Bot running on Render: https://brodcast-blast.onrender.com
  - Webhook configured: /api/webhook/telegram
  - 14 message handlers registered and active
  - Polling disabled on Render (webhook-only mode)
  - Local dev dashboard-only mode (SKIP_BOT_POLLING=true)
  - Admin dashboard available at: https://brodcast-blast.onrender.com
- ✅ **Production Configuration**
  - run.py now detects RENDER env var for webhook mode
  - Webhook handler processes all Telegram updates
  - Bot handlers in bot/main.py process via webhook
  - Local Replit dev: Dashboard only (no polling conflicts)
- 2024-11-27: **Admin Monetag Ad Links Management Complete** - Direct links from Monetag
  - ✅ Admin pastes direct Monetag links (from Monetag Direct Links page)
  - ✅ Add, edit, delete ad links
  - ✅ Optional friendly names for each link
  - ✅ Full link validation before adding
  - ✅ UI in dashboard "Ad Settings" tab - "Monetag Ad Links" section
  - ✅ Works with any Monetag link (Dreamy, Perfect, Lovely, etc.)
- 2024-11-27: **Embedded Ad Viewer with Auto-Timer Completion - FIXED & LIVE** 🎬⏱️✅
  - ✅ **FIX**: Ads now check `ads_required` backend flag (not SDK key)
  - ✅ User: `/create` → Shows "Watch Ad Now" button
  - ✅ User: Clicks button → Opens embedded ad viewer
  - ✅ Ads load IN-APP with 30-second countdown timer
  - ✅ Timer shows at top (like native Monetag ads: 00:30 → 00:00)
  - ✅ When timer reaches 0 → Shows "✅ Ad Complete - Return to Telegram" button
  - ✅ User clicks button → Returns to Telegram
  - ✅ Bot auto-marks user as watched and starts broadcast creation
  - ✅ NO SKIP option - Ads mandatory before each broadcast
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
✅ **OPENAI_API_KEY** - AI template generation (optional)
✅ **CRYPTOPAY_API_KEY** - CryptoPay integration
✅ **XROCKET_API_KEY** - xRocket payment integration
✅ **SESSION_SECRET** - Session management
✅ **MONETAG_SDK_KEY** - For Monetag ad integration (zone: 10243712)

## Optional/Future Variables
- STARS_API_KEY - For Telegram Stars (handled via bot API)

## CRITICAL: Database Schema Update Required
⚠️ **The users table MUST have these columns for full functionality:**
```sql
-- Update existing 'category' column to 'categories' TEXT[] array:
ALTER TABLE users DROP COLUMN category;
ALTER TABLE users ADD COLUMN categories TEXT[] DEFAULT ARRAY[]::TEXT[];
```
- This allows saving multiple interest categories per user
- Without this, registration will fail silently

## Recent Bug Fixes (Nov 28, 2025)
- 🔧 Fixed: Registration details not saving (update_user now properly updates database)
- 🔧 Fixed: users_ads_watched undefined error (added set definition)
- 🔧 Fixed: Payment callback routing (correct gateway selection)
- 🔧 Fixed: Back navigation (routes to main menu)
