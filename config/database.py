from supabase import create_client
from config.settings import SUPABASE_URL, SUPABASE_KEY

supabase = None

def get_supabase_client():
    global supabase
    if supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise Exception("Supabase credentials not configured")
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            print(f"Error connecting to Supabase: {e}")
            print(f"Please verify your SUPABASE_URL and SUPABASE_KEY are correct")
            print(f"Make sure you're using the 'anon/public' key, not the service_role key")
            raise
    return supabase

SCHEMA_SQL = """
-- Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    country TEXT,
    category TEXT,
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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_broadcasts_status ON broadcasts(status);
CREATE INDEX IF NOT EXISTS idx_broadcasts_user ON broadcasts(user_id);
CREATE INDEX IF NOT EXISTS idx_priority_slots_active ON priority_slots(active);
CREATE INDEX IF NOT EXISTS idx_analytics_broadcast ON analytics(broadcast_id);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(active);
"""

def initialize_database():
    """Initialize database schema"""
    try:
        db = get_supabase_client()
        print("✓ Connected to Supabase")
        print("Note: Run the SQL schema in your Supabase dashboard SQL editor")
        print("Schema available in config/database.py")
        return True
    except Exception as e:
        print(f"✗ Database connection error: {e}")
        return False
