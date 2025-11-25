# 🚀 Telegram Broadcast Bot with Priority Slot System

A comprehensive Telegram broadcast bot that allows users to send broadcasts to targeted audiences with an innovative **priority slot system**. Users can pay to temporarily block other broadcasts and ensure exclusive delivery for a specific time period or number of messages.

## ✨ Features

### Core Features
- **User Registration**: Interactive registration with country and interest category selection
- **Free Broadcasts**: Create and queue broadcasts with text and media (images, videos, documents)
- **Targeting Options**: Send to all users, specific countries, or interest categories
- **Priority Slot System**: 
  - ⏱️ Time-based slots (1h, 6h, 12h, 24h)
  - 📊 Count-based slots (5, 10, 25, 50 broadcasts)
- **Auto-Queue Management**: Broadcasts are queued when priority slots are active
- **Analytics**: Track views, delivery success, and engagement
- **AI Features**: OpenAI-powered broadcast template generation

### Admin Features
- **Dashboard**: Monitor users, broadcasts, revenue, and analytics
- **User Management**: Block/unblock users, view user statistics
- **Broadcast Control**: View all broadcasts and their status
- **Priority Slot Monitoring**: Track active slots and revenue
- **Payment Tracking**: Monitor all transactions

### Payment Integration
- Telegram Stars
- CryptoPay
- X Rocket
- Telegram Wallet
- *Note: Payment gateways are in demo mode - production integration required*

## 🛠️ Tech Stack

- **Bot**: Python with pyTelegramBotAPI
- **Backend API**: Flask with Flask-CORS
- **Database**: Supabase (PostgreSQL)
- **AI**: OpenAI GPT-3.5
- **Scheduler**: APScheduler for background tasks
- **Deployment**: Render-ready

## 📦 Installation

### Prerequisites
- Python 3.11+
- Telegram Bot Token (from @BotFather)
- Supabase account (free tier)
- OpenAI API key (optional, for AI features)

### Setup Steps

1. **Clone or access the project**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` and fill in your values:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
OPENAI_API_KEY=your_openai_api_key
ADMIN_USER_ID=your_telegram_user_id
```

4. **Set up Supabase Database**

Go to your Supabase project's SQL Editor and run the schema from `config/database.py` (SCHEMA_SQL constant).

5. **Run the bot**
```bash
python run.py
```

The bot and admin dashboard will start:
- 🤖 Telegram Bot: Running and polling
- 📊 Admin Dashboard: http://localhost:5000

## 📱 Bot Commands

- `/start` - Register or restart the bot
- `/menu` - Show main menu with all options
- `/create` - Create a new broadcast
- `/priority` - View and purchase priority slots
- `/mybroadcasts` - View your broadcast history
- `/stats` - View your statistics
- `/settings` - Change country or category
- `/help` - Show help information
- `/ai_template` - Generate AI broadcast template

## 🎯 How Priority Slots Work

### What are Priority Slots?
Priority slots give you exclusive broadcast rights for a specific period or number of messages.

### When you have an active priority slot:
1. ✅ Your broadcasts are sent immediately
2. ⏸️ Other users' broadcasts are queued
3. 🚀 No competition for user attention
4. 📈 Higher engagement rates

### Two Types Available:

**Time-Based Slots**
- 1 Hour - $5.00
- 6 Hours - $25.00
- 12 Hours - $45.00
- 24 Hours - $80.00

**Count-Based Slots**
- 5 Broadcasts - $10.00
- 10 Broadcasts - $18.00
- 25 Broadcasts - $40.00
- 50 Broadcasts - $70.00

## 🔐 Admin Dashboard API

### Available Endpoints

```
GET  /api/health              - Health check
GET  /api/stats               - Overall statistics
GET  /api/users               - List all users
GET  /api/users/:id           - Get specific user
POST /api/users/:id/block     - Block/unblock user
GET  /api/broadcasts          - List all broadcasts
GET  /api/broadcasts/:id      - Get specific broadcast
GET  /api/priority-slots      - List all priority slots
GET  /api/priority-slots/active - Get active slot
GET  /api/analytics/broadcasts - Get broadcast analytics
GET  /api/payments            - List all payments
GET  /api/admin/logs          - Get admin logs
```

## 📊 Database Schema

### Users Table
- User registration and profile information
- Country and interest category
- Active/blocked status

### Broadcasts Table
- Broadcast messages and metadata
- Targeting information
- Status tracking (queued, sent)
- View and delivery statistics

### Priority Slots Table
- Slot type (time/count)
- Duration or message count
- Payment status and gateway
- Active status and timestamps

### Analytics Table
- Broadcast views and engagement
- User interactions
- Timestamp tracking

### Payments Table
- Transaction records
- Payment gateway information
- Status tracking

### Admin Logs Table
- Administrative actions
- User and broadcast references
- Audit trail

## 🚀 Deployment (Render)

### Prepare for Deployment

1. **Create `render.yaml`**
```yaml
services:
  - type: web
    name: telegram-broadcast-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python run.py
    envVars:
      - key: TELEGRAM_BOT_TOKEN
        sync: false
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false
```

2. **Push to Git repository**
3. **Connect to Render**
4. **Set environment variables in Render dashboard**
5. **Deploy**

## 🔧 Configuration

### Priority Slot Pricing
Edit `config/settings.py` to adjust pricing:
```python
PRIORITY_SLOT_PRICES = {
    'time_1h': 5.0,
    'time_6h': 25.0,
    # ... adjust as needed
}
```

### Countries and Categories
Customize available options in `config/settings.py`:
```python
COUNTRIES = ['United States', 'United Kingdom', ...]
CATEGORIES = ['Technology', 'Business', ...]
```

### Broadcast Queue Processing
The queue is processed every 30 seconds by default. Adjust in `bot/main.py`:
```python
scheduler.add_job(process_broadcast_queue, 'interval', seconds=30)
```

## 🤖 AI Features

The bot includes OpenAI integration for:
- Automatic broadcast template generation
- Message optimization suggestions
- Engagement prediction

Enable by setting `OPENAI_API_KEY` in your environment.

## 🐛 Troubleshooting

### Bot not responding?
- Check your `TELEGRAM_BOT_TOKEN` is correct
- Ensure the bot is running (`python run.py`)
- Check console logs for errors

### Database errors?
- Verify Supabase credentials
- Run the schema SQL in Supabase dashboard
- Check network connectivity

### Broadcasts not sending?
- Verify users exist in database
- Check broadcast status in admin dashboard
- Review console logs for errors

## 📝 License

This project is provided as-is for educational and commercial use.

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- React admin dashboard frontend
- Additional payment gateway integrations
- Enhanced analytics and reporting
- Monetag Ads SDK integration
- Scheduled broadcasts feature
- Multi-admin role system

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review console logs
3. Verify environment variables
4. Check Supabase database setup

---

**Made with ❤️ using Python, Telegram Bot API, and Supabase**
