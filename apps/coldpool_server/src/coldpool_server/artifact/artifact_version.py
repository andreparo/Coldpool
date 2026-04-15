from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ArtifactVersion:
    """A concrete stored version of one logical artifact."""

    id: int
    artifact_id: int
    created_at: datetime
    size_bytes: int
    version_label: str | None = None
    checksum: str | None = None
    expires_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate ArtifactVersion field values after initialization."""
        if self.id <= 0:
            raise ValueError("ArtifactVersion id must be > 0.")

        if self.artifact_id <= 0:
            raise ValueError("ArtifactVersion artifact_id must be > 0.")

        if self.size_bytes < 0:
            raise ValueError("ArtifactVersion size_bytes must be >= 0.")

        if self.version_label is not None and not self.version_label.strip():
            raise ValueError("ArtifactVersion version_label must not be empty if provided.")

        if self.checksum is not None and not self.checksum.strip():
            raise ValueError("ArtifactVersion checksum must not be empty if provided.")

        if self.expires_at is not None and self.expires_at < self.created_at:
            raise ValueError("ArtifactVersion expires_at must be >= created_at.")
