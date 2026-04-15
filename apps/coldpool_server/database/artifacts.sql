CREATE TABLE artifacts (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    priority_score INTEGER NOT NULL CHECK (priority_score >= 0),
    desired_copy_count INTEGER NOT NULL CHECK (desired_copy_count >= 0),
    artifact_type TEXT,
    shelf_life_days INTEGER CHECK (shelf_life_days IS NULL OR shelf_life_days >= 0)
);