# ⚠️ Important: Supabase API Key Issue

## Problem
You're currently using a **service_role** key, but you need the **anon/public** key.

## Solution: Get the Correct Key

1. Go to your Supabase project dashboard
2. Click on **Settings** (⚙️ icon in the left sidebar)
3. Click on **API**
4. Look for the section **Project API keys**
5. You'll see TWO keys:
   - ✅ **anon** / **public** - This is what you need! (starts with `eyJ`)
   - ❌ **service_role** - DO NOT use this one (starts with `sb_secret_`)

6. Copy the **anon public** key (the long one starting with `eyJ`)
7. Update your SUPABASE_KEY secret with this new key

## How to Update in Replit

1. Click the 🔒 **Secrets** icon (or Tools → Secrets)
2. Find `SUPABASE_KEY`
3. Click **Edit**
4. Replace with the **anon/public** key from Supabase
5. Save

After updating, the bot will automatically restart and connect properly!

---

**Why the difference?**
- **anon/public key**: Safe for client-side use, used by the bot
- **service_role key**: Full database access, should never be exposed
