-- Telegram Broadcast Bot Database Schema
-- Run this in your Supabase SQL Editor

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    country TEXT,
    categories TEXT[],
    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE,
    blocked BOOLEAN DEFAULT FALSE,
    can_view_analytics BOOLEAN DEFAULT FALSE
);

-- Broadcasts Table
CREATE TABLE IF NOT EXISTS broadcasts (
    broadcast_id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    text TEXT NOT NULL,
    media_url TEXT,
    media_type TEXT,
    target_country TEXT,
    target_category TEXT,
    status TEXT DEFAULT 'queued',
    views INT DEFAULT 0,
    sent_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP
);

-- Priority Slots Table
CREATE TABLE IF NOT EXISTS priority_slots (
    slot_id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    slot_type TEXT NOT NULL,
    duration_hours INT,
    message_count INT,
    messages_sent INT DEFAULT 0,
    price NUMERIC(10, 2) NOT NULL,
    payment_status TEXT DEFAULT 'pending',
    payment_gateway TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analytics Table
CREATE TABLE IF NOT EXISTS analytics (
    id SERIAL PRIMARY KEY,
    broadcast_id INT REFERENCES broadcasts(broadcast_id),
    user_id BIGINT REFERENCES users(user_id),
    viewed BOOLEAN DEFAULT FALSE,
    reaction TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Payments Table
CREATE TABLE IF NOT EXISTS payments (
    payment_id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    slot_id INT REFERENCES priority_slots(slot_id),
    amount NUMERIC(10, 2) NOT NULL,
    gateway TEXT NOT NULL,
    transaction_id TEXT,
    status TEXT DEFAULT 'pending',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admin Logs Table
CREATE TABLE IF NOT EXISTS admin_logs (
    log_id SERIAL PRIMARY KEY,
    admin_id BIGINT,
    action TEXT NOT NULL,
    target_user_id BIGINT,
    broadcast_id INT,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- IMPORTANT: Disable Row Level Security for bot access
-- Run these commands to allow the bot to read/write data
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE broadcasts DISABLE ROW LEVEL SECURITY;
ALTER TABLE priority_slots DISABLE ROW LEVEL SECURITY;
ALTER TABLE analytics DISABLE ROW LEVEL SECURITY;
ALTER TABLE payments DISABLE ROW LEVEL SECURITY;
ALTER TABLE admin_logs DISABLE ROW LEVEL SECURITY;

-- Also drop any existing RLS policies if they exist
DROP POLICY IF EXISTS "Enable all access" ON users;
DROP POLICY IF EXISTS "Enable all access" ON broadcasts;
DROP POLICY IF EXISTS "Enable all access" ON priority_slots;
DROP POLICY IF EXISTS "Enable all access" ON analytics;
DROP POLICY IF EXISTS "Enable all access" ON payments;
DROP POLICY IF EXISTS "Enable all access" ON admin_logs;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_broadcasts_status ON broadcasts(status);
CREATE INDEX IF NOT EXISTS idx_broadcasts_user ON broadcasts(user_id);
CREATE INDEX IF NOT EXISTS idx_priority_slots_active ON priority_slots(active);
CREATE INDEX IF NOT EXISTS idx_analytics_broadcast ON analytics(broadcast_id);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(active);
