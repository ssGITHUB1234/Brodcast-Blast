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
- 2024-11-27: **Payment Integration Complete** - Integrated 4 payment methods
  - ⭐ Telegram Stars (XTR currency) - sendInvoice via Bot API
  - 💳 CryptoPay (USDT, TON, BTC, ETH, LTC, BNB, TRX, USDC) - REST API + webhooks
  - 💰 Telegram Wallet (USD fiat) - Native Telegram wallet payment
  - 🚀 xRocket (graceful fallback with error handling)
  - Pre-checkout query handling for all methods
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
- MONETAG_SDK_KEY - For ad integration (coming soon)
