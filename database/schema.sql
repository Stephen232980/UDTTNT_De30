-- Mạch Đỏ SQLite schema: reflects fresh initialize_database() DDL.
-- Connection setup also runs PRAGMA foreign_keys=ON and journal_mode=WAL.
-- Existing migrated databases may have legacy defaults for donors.created_at.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS donors (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT DEFAULT '',
    blood_group TEXT DEFAULT 'Chưa cập nhật',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    birth_date TEXT,
    address TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    venue TEXT NOT NULL,
    campaign_date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    description TEXT DEFAULT '',
    status TEXT DEFAULT 'Đang mở'
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    display_name TEXT,
    role TEXT,
    password TEXT,
    donor_id INTEGER REFERENCES donors(id),
    phone TEXT NOT NULL DEFAULT '',
    blood_group TEXT NOT NULL DEFAULT 'Chưa cập nhật',
    birth_date TEXT,
    address TEXT NOT NULL DEFAULT '',
    organization TEXT NOT NULL DEFAULT '',
    job_title TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    full_name TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'locked')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS slots (
    id INTEGER PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id),
    start_at TEXT,
    end_at TEXT,
    capacity INTEGER,
    UNIQUE (campaign_id, start_at)
);

CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY,
    donor_id INTEGER REFERENCES donors(id),
    slot_id INTEGER REFERENCES slots(id),
    status TEXT DEFAULT 'Đã đăng ký',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (donor_id, slot_id)
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title TEXT NOT NULL DEFAULT '',
    message TEXT NOT NULL DEFAULT '',
    type TEXT NOT NULL DEFAULT 'system',
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    appointment_id INTEGER REFERENCES appointments(id),
    donor_id INTEGER REFERENCES donors(id),
    campaign_id INTEGER REFERENCES campaigns(id),
    sent_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS procedures (
    id INTEGER PRIMARY KEY,
    title TEXT,
    content TEXT
);

-- UNIQUE constraints above create SQLite autoindexes for users.username,
-- slots(campaign_id, start_at), and appointments(donor_id, slot_id).
CREATE INDEX IF NOT EXISTS idx_notifications_user_created
    ON notifications(user_id, created_at DESC);

CREATE UNIQUE INDEX IF NOT EXISTS idx_notifications_reminder_appointment
    ON notifications(user_id, appointment_id)
    WHERE type = 'reminder' AND appointment_id IS NOT NULL;

-- No CHECK constraints exist in current code.
