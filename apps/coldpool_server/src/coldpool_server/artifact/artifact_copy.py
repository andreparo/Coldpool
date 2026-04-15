from __future__ import annotations

from dataclasses import dataclass

from coldpool_server.artifact.artifact_version import ArtifactVersion
from coldpool_server.artifact.artifact import Artifact


@dataclass(slots=True)
class ArtifactCopy:
    """A physical stored copy of one artifact version on one disk."""

    id: int
    artifact_version: ArtifactVersion
    copy_index: int
    disk_id: int
    disk_path: str
    is_present: bool = True
    status: str = "verified"

    VALID_STATUSES = ("verified", "stale", "missing")

    def __post_init__(self) -> None:
        """Validate ArtifactCopy field values after initialization."""
        if self.id <= 0:
            raise ValueError("ArtifactCopy id must be > 0.")

        if self.copy_index < 1:
            raise ValueError("ArtifactCopy copy_index must be >= 1.")

        if self.disk_id <= 0:
            raise ValueError("ArtifactCopy disk_id must be > 0.")

        if not self.disk_path.strip():
            raise ValueError("ArtifactCopy disk_path must not be empty.")

        if self.status not in self.VALID_STATUSES:
            raise ValueError("ArtifactCopy status must be one of: verified, stale, missing.")

    @property
    def size_bytes(self) -> int:
        """Return the size of this copy derived from its artifact version."""
        return self.artifact_version.size_bytes

    @property
    def artifact(self) -> Artifact:
        """Return the logical artifact that owns this copy through its version."""
        return self.artifact_version.artifact

    def is_missing(self) -> bool:
        """Return whether this copy is currently missing."""
        return self.status == "missing"

    def is_verified(self) -> bool:
        """Return whether this copy is currently verified."""
        return self.status == "verified"

    def is_stale(self) -> bool:
        """Return whether this copy is currently stale."""
        return self.status == "stale"
