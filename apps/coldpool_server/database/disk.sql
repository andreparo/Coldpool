CREATE TABLE disks (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    total_capacity_bytes INTEGER NOT NULL CHECK (total_capacity_bytes >= 0),
    health_score REAL NOT NULL CHECK (health_score >= 0.0 AND health_score <= 1.0),
    location TEXT,
    state TEXT NOT NULL DEFAULT 'offline' CHECK (
        state IN ('online', 'offline', 'offsite', 'retired')
    )
);