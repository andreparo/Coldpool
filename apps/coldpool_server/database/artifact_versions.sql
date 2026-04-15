CREATE TABLE artifact_versions (
    id INTEGER PRIMARY KEY,
    artifact_id INTEGER NOT NULL,
    version_label TEXT,
    created_at TEXT NOT NULL,
    size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
    checksum TEXT,
    expires_at TEXT,
    FOREIGN KEY (artifact_id) REFERENCES artifacts(id) ON DELETE CASCADE,
    UNIQUE (artifact_id, version_label)
);