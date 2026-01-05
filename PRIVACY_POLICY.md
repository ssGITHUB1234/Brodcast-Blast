# Brodcast Blast — Privacy Policy

Last updated: 2026-01-05

Summary
- This Mini App uses the TON blockchain exclusively.
- Wallet interactions are performed via the TON Connect SDK. We never request or store private keys or seed phrases.
- We collect only minimal data required to operate the service (connected wallet address, session ID, and transaction metadata).

Data handling
- Wallet connection: We receive the public wallet address and a session token from TON Connect. These are used to authorize user actions.
- Transaction metadata: tx hash, timestamp, and amounts may be logged for support and reconciliation.
- Logs: Server logs are retained for debugging and security for a limited retention period.

Storage & retention
- Wallet addresses and transaction metadata are stored for a limited period (configurable).
- No private keys or sensitive wallet credentials are stored.

Third‑party services
- TON Connect SDK (wallet connectivity). See: https://docs.ton.org/v3/guidelines/ton-connect/overview
- Telegram Mini Apps Analytics SDK (event analytics). See: https://github.com/Telegram-Mini-Apps/analytics
- Hosting/CDN providers as required (Render).

Security
- All service endpoints use HTTPS.
- Bot tokens and other sensitive keys are stored as environment variables and are never committed.

Contact
- For privacy questions, contact: your-email@example.com
