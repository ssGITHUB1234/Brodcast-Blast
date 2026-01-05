# Integration Guide — TON Connect & Telegram Mini Apps Analytics (example)

These are example snippets. Replace placeholders with real package names/keys and adapt to your framework.

1) TON Connect (example, plain JavaScript front-end)
```html
<!-- miniapp/index.html will include the example implementation used by reviewers -->
```

2) Telegram Mini Apps Analytics (example)
- See official repo: https://github.com/Telegram-Mini-Apps/analytics
- Initialize analytics in the Mini App and track key events: miniapp_open, wallet_connect, tx_sent, error.

3) Server-side: verify and sign (backend)
- Do not accept private keys.
- Validate wallet address ownership via signed messages (if your flows require authorization).
- For transactions, prefer the user to sign in their wallet via TON Connect and submit tx to the network; only store tx hash and status.

Test plan for reviewers
1. Visit https://YOUR_RENDER_URL/ and open the Mini App in Incognito.
2. Connect a TON wallet via TON Connect and confirm connection (testnet recommended).
3. Send a test transaction on testnet (if configured) and confirm Telegram Analytics events are emitted (or check console/logs).
4. Verify manifest is reachable at /miniapp/manifest.json and privacy policy is reachable.

Links
- TON Connect overview: https://docs.ton.org/v3/guidelines/ton-connect/overview
- Telegram Mini Apps Analytics: https://github.com/Telegram-Mini-Apps/analytics
- Telegram Apps Center Terms & Conditions: https://telegra.ph/Telegram-Apps-Center-Terms-and-Conditions-01-29
