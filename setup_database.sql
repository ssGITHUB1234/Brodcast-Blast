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

-- Priority Slot Types Table (for admin management)
CREATE TABLE IF NOT EXISTS priority_slot_types (
    id SERIAL PRIMARY KEY,
    slot_key TEXT NOT NULL UNIQUE,
    slot_category TEXT NOT NULL CHECK (slot_category IN ('time', 'count')),
    display_name TEXT NOT NULL,
    description TEXT,
    duration_hours INT,
    message_count INT,
    price NUMERIC(10, 2) NOT NULL DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default slot types
INSERT INTO priority_slot_types (slot_key, slot_category, display_name, description, duration_hours, message_count, price, active)
VALUES 
    ('time_1h', 'time', '1 Hour Priority', 'Your broadcast stays at top for 1 hour', 1, NULL, 5.00, true),
    ('time_6h', 'time', '6 Hours Priority', 'Your broadcast stays at top for 6 hours', 6, NULL, 25.00, true),
    ('time_12h', 'time', '12 Hours Priority', 'Your broadcast stays at top for 12 hours', 12, NULL, 45.00, true),
    ('time_24h', 'time', '24 Hours Priority', 'Your broadcast stays at top for 24 hours', 24, NULL, 80.00, true),
    ('count_5', 'count', '5 Broadcasts', 'Next 5 broadcasts will be priority', NULL, 5, 10.00, true),
    ('count_10', 'count', '10 Broadcasts', 'Next 10 broadcasts will be priority', NULL, 10, 18.00, true),
    ('count_25', 'count', '25 Broadcasts', 'Next 25 broadcasts will be priority', NULL, 25, 40.00, true),
    ('count_50', 'count', '50 Broadcasts', 'Next 50 broadcasts will be priority', NULL, 50, 70.00, true)
ON CONFLICT (slot_key) DO NOTHING;

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
ALTER TABLE priority_slot_types DISABLE ROW LEVEL SECURITY;
ALTER TABLE analytics DISABLE ROW LEVEL SECURITY;
ALTER TABLE payments DISABLE ROW LEVEL SECURITY;
ALTER TABLE admin_logs DISABLE ROW LEVEL SECURITY;

-- Also drop any existing RLS policies if they exist
DROP POLICY IF EXISTS "Enable all access" ON users;
DROP POLICY IF EXISTS "Enable all access" ON broadcasts;
DROP POLICY IF EXISTS "Enable all access" ON priority_slots;
DROP POLICY IF EXISTS "Enable all access" ON priority_slot_types;
DROP POLICY IF EXISTS "Enable all access" ON analytics;
DROP POLICY IF EXISTS "Enable all access" ON payments;
DROP POLICY IF EXISTS "Enable all access" ON admin_logs;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_broadcasts_status ON broadcasts(status);
CREATE INDEX IF NOT EXISTS idx_broadcasts_user ON broadcasts(user_id);
CREATE INDEX IF NOT EXISTS idx_priority_slots_active ON priority_slots(active);
CREATE INDEX IF NOT EXISTS idx_priority_slot_types_category ON priority_slot_types(slot_category);
CREATE INDEX IF NOT EXISTS idx_priority_slot_types_active ON priority_slot_types(active);
CREATE INDEX IF NOT EXISTS idx_analytics_broadcast ON analytics(broadcast_id);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(active);

-- =====================================================
-- RPC Functions for Priority Slot Types Management
-- These bypass Supabase schema cache issues
-- =====================================================

-- Get all slot types
CREATE OR REPLACE FUNCTION get_all_slot_types(p_active_only BOOLEAN DEFAULT FALSE)
RETURNS SETOF priority_slot_types AS $$
BEGIN
    IF p_active_only THEN
        RETURN QUERY SELECT * FROM priority_slot_types WHERE active = TRUE ORDER BY slot_category, price;
    ELSE
        RETURN QUERY SELECT * FROM priority_slot_types ORDER BY slot_category, price;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a new slot type
CREATE OR REPLACE FUNCTION create_slot_type(
    p_slot_key TEXT,
    p_slot_category TEXT,
    p_display_name TEXT,
    p_price NUMERIC,
    p_description TEXT DEFAULT NULL,
    p_duration_hours INT DEFAULT NULL,
    p_message_count INT DEFAULT NULL
)
RETURNS priority_slot_types AS $$
DECLARE
    new_slot priority_slot_types;
BEGIN
    INSERT INTO priority_slot_types (slot_key, slot_category, display_name, description, duration_hours, message_count, price, active)
    VALUES (p_slot_key, p_slot_category, p_display_name, p_description, p_duration_hours, p_message_count, p_price, TRUE)
    RETURNING * INTO new_slot;
    RETURN new_slot;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Update a slot type
CREATE OR REPLACE FUNCTION update_slot_type(
    p_id INT,
    p_price NUMERIC DEFAULT NULL,
    p_active BOOLEAN DEFAULT NULL,
    p_display_name TEXT DEFAULT NULL
)
RETURNS priority_slot_types AS $$
DECLARE
    updated_slot priority_slot_types;
BEGIN
    UPDATE priority_slot_types
    SET 
        price = COALESCE(p_price, price),
        active = COALESCE(p_active, active),
        display_name = COALESCE(p_display_name, display_name)
    WHERE id = p_id
    RETURNING * INTO updated_slot;
    RETURN updated_slot;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Delete a slot type
CREATE OR REPLACE FUNCTION delete_slot_type(p_id INT)
RETURNS BOOLEAN AS $$
BEGIN
    DELETE FROM priority_slot_types WHERE id = p_id;
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
