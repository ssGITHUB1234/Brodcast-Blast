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
- 2024-11-25: Initial project setup

## User Preferences
- Priority broadcast system (no admin approval needed)
- Payment only for exclusive broadcast slots, not per broadcast
- Auto-queue management when priority slots are active

## Environment Variables Needed
- TELEGRAM_BOT_TOKEN
- SUPABASE_URL
- SUPABASE_KEY
- OPENAI_API_KEY (already available)
- STARS_API_KEY
- CRYPTOPAY_API_KEY
- XROCKET_API_KEY
- MONETAG_SDK_KEY
