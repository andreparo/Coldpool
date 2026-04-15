CREATE TABLE copies (
    id INTEGER PRIMARY KEY,
    artifact_version_id INTEGER NOT NULL,
    copy_index INTEGER NOT NULL CHECK (copy_index >= 1),
    disk_id INTEGER NOT NULL,
    disk_path TEXT NOT NULL,
    is_present INTEGER NOT NULL DEFAULT 1 CHECK (is_present IN (0, 1)),
    status TEXT NOT NULL DEFAULT 'verified' CHECK (
        status IN ('verified', 'stale', 'missing')
    ),
    FOREIGN KEY (artifact_version_id) REFERENCES artifact_versions(id) ON DELETE CASCADE,
    FOREIGN KEY (disk_id) REFERENCES disks(id) ON DELETE CASCADE,
    UNIQUE (artifact_version_id, copy_index),
    UNIQUE (artifact_version_id, disk_id)
);