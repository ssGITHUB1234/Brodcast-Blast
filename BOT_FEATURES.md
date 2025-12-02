# Telegram Broadcast Bot - Complete Features List

## 🚀 User Features

### 1. User Registration & Personalization
- **Country Selection**: Users select their country from a dropdown list during `/start`
- **Interest Categories**: Multi-select interest categories (Crypto, Marketing, Real Estate, Automotive, etc.)
- **Profile Persistence**: All preferences saved to database and persist across sessions
- **Auto-Registration**: New users auto-registered on first command

### 2. Free Broadcast Creation
- **Text Broadcasts**: Send text-only messages to targeted audiences
- **Media Support**: Attach images, videos, or documents to broadcasts
- **Target Filtering**: 
  - Send to all users
  - Filter by country
  - Filter by interest category
  - Combine multiple filters
- **Broadcast Queue**: Messages queued and sent in order
- **Delivery Confirmation**: Track broadcast delivery status

### 3. Monetag Ad System
- **Auto-Starting Ads**: Watch advertisement automatically starts on ad page load
- **30-Second Timer**: Countdown display with auto-close
- **Zero Clicks After Ad**: Timer completes → auto-returns to bot → broadcast form appears
- **Ad Recency Tracking**: Skip ads if watched within 60 seconds (no repeated ads for rapid creations)
- **WebApp Integration**: Seamless Telegram WebApp experience
- **Admin Control**: Admins can toggle ads on/off via dashboard
- **Mandatory Before Each Broadcast**: Users watch ad before creating each broadcast

### 4. Priority Broadcast Slots (Paid Feature)
- **Time-Based Slots**:
  - 1-hour exclusive delivery ($5)
  - 6-hour exclusive delivery ($25)
  - 12-hour exclusive delivery ($45)
  - 24-hour exclusive delivery ($80)
- **Count-Based Slots**:
  - Next 5 broadcasts exclusive ($10)
  - Next 10 broadcasts exclusive ($18)
  - Next 25 broadcasts exclusive ($40)
  - Next 50 broadcasts exclusive ($70)
- **Priority Queue**: Broadcasts with active slots sent before free broadcasts
- **Automatic Expiration**: Slots expire based on time or message count
- **Real-Time Status**: Users see remaining slot time/broadcasts

### 5. Payment Integration
- **Telegram Stars**: Native Telegram payment (100 XTR = $1 USD)
- **CryptoPay Integration**: Support for USDT, TON, BTC, ETH, LTC, BNB, TRX, USDC
- **xRocket Integration**: Additional crypto payment option
- **Payment Status Tracking**: View all payments and transactions
- **Webhook Confirmation**: Automatic payment verification
- **Invoice Generation**: Auto-generated payment invoices

### 6. Broadcast Analytics
- **View Count**: Track how many users viewed each broadcast
- **Engagement Metrics**: Click rates and interaction tracking
- **User Statistics**: See who sent broadcasts and how many
- **Revenue Tracking**: Monitor income from priority slots
- **My Broadcasts Pagination**: View 1 broadcast per page with navigation
- **Detailed Stats**: `/mystats` command for personal analytics

### 7. Navigation & Menu System
- **Main Menu**: `/menu` shows all available options
- **Back Buttons**: Easy navigation between screens
- **Message Editing**: Buttons update existing messages (no spam)
- **Context Tracking**: Bot remembers user state/location
- **Command Shortcuts**:
  - `/start` - Register or view profile
  - `/create` - Start broadcast creation
  - `/mybroadcasts` - View your sent broadcasts
  - `/priority` - Check priority slot options
  - `/mystats` - View your analytics
  - `/settings` - Update preferences
  - `/help` - See help information
  - `/menu` - Main menu

---

## 👨‍💼 Admin Dashboard Features

### 1. User Management
- **User List**: View all registered users
- **User Status**: Active/Blocked status
- **Block/Unban Controls**: Instant user control
- **User Analytics**: See user registration dates and activity
- **Multi-Status Toggle**: Ban/unban users instantly

### 2. Broadcast Monitoring
- **Broadcast History**: View all broadcasts sent
- **Broadcast Pagination**: Navigate through broadcasts (1 per page)
- **Delivery Status**: See sent/queued/failed status
- **Content Preview**: View broadcast text and media
- **Target Details**: See which audience segment received broadcast

### 3. Analytics Dashboard
- **Total Users**: Real-time user count
- **Total Broadcasts**: Cumulative broadcasts sent
- **Active Priority Slots**: Currently active paid slots
- **Revenue Stats**: Total income from priority slots
- **Top Paying Users**: Bar chart of user revenue
- **Top Broadcasting Users**: Pie chart of broadcast distribution
- **Chart.js Integration**: Interactive data visualization

### 4. Payment Management
- **Payment History**: Complete transaction log
- **Payment Methods**: Filter by payment gateway
- **Transaction Details**: User, amount, status, timestamp
- **Revenue Tracking**: Total revenue by period
- **Failed Payments**: Identify incomplete transactions

### 5. Ad Settings & Management
- **Monetag Ad Links**: Add/edit/delete direct Monetag links
- **Ad Status Toggle**: Enable/disable ads system-wide
- **Ad Statistics**: Views completed, uncompleted
- **Friendly Names**: Label ad links for identification
- **Link Validation**: Verify Monetag links before saving
- **Zone Configuration**: Zone 10243712 setup

### 6. Pricing Controls
- **Flexible Pricing**: Set custom prices for each slot type
- **Real-Time Updates**: Change prices instantly
- **Price Categories**:
  - Time-based (1h, 6h, 12h, 24h)
  - Count-based (5, 10, 25, 50 broadcasts)
- **Save Mechanism**: Prices persist to backend

### 7. Dashboard Statistics
- **Real-Time Data**: Live updates
- **Export-Ready Stats**: Data available for reports
- **Date Filters**: View by time period
- **User Segmentation**: Analyze by country/category

---

## 🔧 Technical Features

### 1. Database System
- **Supabase PostgreSQL**: Cloud-backed database
- **Tables**:
  - `users`: User profiles and preferences
  - `broadcasts`: Broadcast messages and metadata
  - `priority_slots`: Slot reservations and status
  - `analytics`: View tracking and engagement
  - `payments`: Transaction history
  - `admin_logs`: Administrative action logging
- **Row-Level Security**: Disabled for simplicity

### 2. Webhook Integration
- **Telegram Webhook**: Real-time message handling
- **Payment Webhooks**: CryptoPay confirmation
- **WebApp Callbacks**: Ad completion signals
- **Web App Data Handler**: Auto-broadcast creation trigger

### 3. Background Processing
- **Broadcast Queue Processor**: 30-second interval processing
- **Priority Slot Expiration**: Automatic slot cleanup
- **APScheduler**: Background job scheduling
- **Message Delivery**: Async sending to all targets

### 4. Security
- **Session Tokens**: Unique tokens for ad sessions
- **Admin-Only Routes**: Protected dashboard endpoints
- **User Validation**: Verify user before operations
- **Rate Limiting**: Prevent abuse

### 5. API Endpoints
- `GET /` - Admin dashboard
- `GET /ad-viewer` - Ad viewer page
- `GET /api/health` - Health check
- `GET /api/stats` - Overall statistics
- `GET /api/payments` - Payment history
- `GET /api/pricing` - Current pricing
- `POST /api/pricing/<slot>` - Update pricing
- `GET /api/ads/links` - Monetag ad links
- `POST /api/ads/links` - Add new ad link
- `DELETE /api/ads/links/<id>` - Remove ad link
- `GET /api/ads/settings` - Ad system settings
- `POST /api/ads/settings` - Toggle ads on/off
- `POST /api/ads/watched/<user_id>` - Mark ad watched
- `GET /api/ads/check/<user_id>` - Check ad status
- `GET /api/ads/stats` - Ad statistics

### 6. Configuration
- **Environment Variables**: Secure secret management
- **Domain Detection**: Auto-detect HTTPS URLs for WebApp
- **Settings File**: Centralized configuration
- **State Management**: Track user broadcast state

---

## 📱 User Flow Example

### Creating a Broadcast with Priority
1. User clicks `/create`
2. Bot shows "Watch Ad & Unlock" button
3. User clicks button → WebApp opens with ad
4. Ad auto-starts (30-second timer begins)
5. Timer counts down automatically
6. At 0 seconds → WebApp closes and bot receives signal
7. **Bot auto-shows**: "📝 Send your broadcast message..."
8. User types broadcast text
9. User skips or adds media
10. User selects target country/category
11. Broadcast created and queued
12. User offered priority slot purchase
13. If purchased → broadcast sent immediately
14. If free → broadcast queued behind other broadcasts
15. Analytics updated in real-time

---

## 🌍 Supported Countries
- USA, UK, Canada, India, Australia, Germany, France, Italy, Spain, Sri Lanka, and 30+ more

## 🏷️ Supported Categories
- Crypto, Marketing, Real Estate, Automotive, Business, Entertainment, Tech, Sports, and more

## 💰 Payment Options
- Telegram Stars (XTR) - 100 XTR = $1 USD
- CryptoPay (USDT, TON, BTC, ETH, LTC, BNB, TRX, USDC)
- xRocket
- Telegram Wallet

---

## 🚀 Deployment
- **Production**: Render (https://brodcast-blast.onrender.com)
- **Environment**: Webhook-based (polling disabled)
- **Database**: Supabase PostgreSQL
- **Hosting**: 24/7 availability

---

## 📊 Key Statistics
- **Message Handlers**: 14+ registered
- **API Endpoints**: 15+ routes
- **Database Tables**: 6 main tables
- **Supported Currencies**: 8+ crypto options
- **Price Tiers**: 8 different slot options
- **Target Segments**: By country + category

