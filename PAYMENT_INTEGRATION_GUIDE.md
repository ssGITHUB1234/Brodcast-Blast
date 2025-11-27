# Payment Integration Guide

## Overview
Your Telegram Broadcast Bot now supports three payment gateways for priority slot purchases:
1. **Telegram Stars** - Native Telegram payment system (XTR currency)
2. **CryptoPay** - Cryptocurrency payments (USDT, TON, BTC, ETH, LTC, BNB, TRX, USDC)
3. **xRocket** - Fast payment processing

## How Payment Flow Works

### User Journey
1. User selects `/priority` command
2. Chooses a priority slot package (time-based or count-based)
3. Selects payment method (Stars, Crypto, xRocket)
4. Gets redirected to payment interface
5. After payment, priority slot is activated automatically

### Payment Processing

#### Telegram Stars
- **File:** `bot/services/stars_payment.py`
- **Process:**
  - Invoice sent via Telegram Bot API
  - User clicks "Pay" in Telegram app
  - Pre-checkout query handled and approved
  - Successful payment triggers slot activation
- **Handler:** `bot/main.py` - `handle_successful_payment()`
- **Webhook:** Not needed (uses Telegram API updates)

#### CryptoPay
- **File:** `bot/services/cryptopay.py`
- **Supported Assets:** USDT, TON, BTC, ETH, LTC, BNB, TRX, USDC
- **Process:**
  - Invoice created via CryptoPay API
  - User sent to bot_invoice_url
  - Payment confirmed via webhook
  - Webhook endpoint: `/api/webhook/cryptopay`
- **Webhook Handler:** `backend/app.py` - `cryptopay_webhook()`
- **Features:**
  - Automatic verification via HMAC-SHA256 signature
  - Exchange rates available via API
  - Supports both crypto and fiat pricing

#### xRocket
- **File:** `bot/services/xrocket_payment.py`
- **Process:**
  - Invoice created via xRocket API
  - User sent to invoice_url
  - Payment confirmed via webhook
  - Webhook endpoint: `/api/webhook/xrocket`
- **Webhook Handler:** `backend/app.py` - `xrocket_webhook()`
- **Features:**
  - Multi-invoice support
  - Flexible payment options
  - Real-time status updates

## Database Schema

### payments Table
```sql
CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    slot_id INT REFERENCES priority_slots(slot_id),
    amount NUMERIC(10, 2) NOT NULL,
    gateway TEXT NOT NULL,
    transaction_id TEXT,
    status TEXT DEFAULT 'pending', -- pending, completed, failed, refunded
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### priority_slots Updates
- Added `payment_gateway` field to track which service processed payment
- Payment status tracked: 'pending', 'completed'
- Auto-activation on payment confirmation

## Configuration

### API Keys Required
Get these from respective payment services:

**CryptoPay:**
1. Open @CryptoBot or @CryptoTestnetBot (for testing)
2. Go to "Crypto Pay" → "Create App"
3. Copy API Token to `CRYPTOPAY_API_KEY`

**xRocket:**
1. Open @xRocket (or @xrocket_testnet_bot for testing)
2. Go to "Rocket Pay" → "Create App"
3. Copy API Token to `XROCKET_API_KEY`

**Telegram Stars:**
- Handled natively via Telegram Bot API
- No additional API key needed
- Uses TELEGRAM_BOT_TOKEN

## Price Configuration

Edit `config/settings.py`:
```python
PRIORITY_SLOT_PRICES = {
    'time_1h': 5.0,
    'time_6h': 25.0,
    'time_12h': 45.0,
    'time_24h': 80.0,
    'count_5': 10.0,
    'count_10': 18.0,
    'count_25': 40.0,
    'count_50': 70.0,
}
```

All prices in USD equivalent (or your local currency).

## Testing

### Test Mode
- CryptoPay: Use @CryptoTestnetBot with testnet API
- xRocket: Use @xrocket_testnet_bot for testing
- Telegram Stars: Use test invoices (no real payment)

### Production Mode
- Switch to production API URLs
- Enable webhook verification
- Monitor payment logs in `/api/payments`

## API Endpoints

### Admin Dashboard
- `GET /api/stats` - Overall statistics including total_revenue
- `GET /api/payments` - All payment transactions
- `GET /api/payments/{id}` - Specific payment details

### Webhooks (Must be configured in payment provider dashboard)
- `POST /api/webhook/cryptopay` - CryptoPay payment confirmation
- `POST /api/webhook/xrocket` - xRocket payment confirmation

## Webhook Setup Instructions

### CryptoPay Webhook
1. Go to @CryptoBot → "My Apps"
2. Select your app
3. Under "Webhooks" section, enable it
4. Set URL: `https://your-domain.com/api/webhook/cryptopay`
5. Signature verification is automatic (HMAC-SHA256)

### xRocket Webhook
1. Go to @xRocket → App Management
2. Select your app
3. Enable "Webhooks"
4. Set URL: `https://your-domain.com/api/webhook/xrocket`
5. Signature verification is automatic (HMAC-SHA256)

## Error Handling

### Payment Verification
- All webhook signatures verified with HMAC-SHA256
- Invalid signatures rejected (401 Unauthorized)
- Failed payments marked as 'failed' in database

### Slot Activation
- Only activated after payment status is 'completed'
- Automatic expiration based on slot type:
  - Time-based: expires after duration
  - Count-based: expires after message limit

## Troubleshooting

### Payment Not Showing in Database
- Verify webhook is enabled in payment provider dashboard
- Check signature verification is passing
- View logs: `GET /api/admin/logs`

### Invoice Creation Fails
- Verify API keys in environment variables
- Check API connection (test endpoints available)
- Ensure pricing is set in `config/settings.py`

### Webhook Not Triggered
- Confirm webhook URL is accessible
- Check webhook is enabled in payment provider dashboard
- Verify firewall/routing isn't blocking requests
- Check server logs for incoming requests

## Revenue Tracking

Total revenue calculated in admin stats:
```python
total_revenue = SUM(payments.amount WHERE status = 'completed')
```

View dashboard at: `http://localhost:5000` (local) or your deployed domain

## Next Steps

1. **Deploy:** Publish your bot to get production URL
2. **Configure Webhooks:** Set webhook URLs in payment providers
3. **Test Payments:** Verify payment flow end-to-end
4. **Monitor:** Track payments via admin dashboard
5. **Expand:** Consider adding:
   - Refund processing
   - Payment method statistics
   - Currency conversion tracking
   - Customer invoicing/receipts
