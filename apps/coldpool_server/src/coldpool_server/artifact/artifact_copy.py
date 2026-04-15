from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ArtifactCopy:
    """A physical stored copy of one artifact version on one disk."""

    id: int
    artifact_version_id: int
    copy_index: int
    disk_id: int
    disk_path: str
    is_present: bool = True
    status: str = "verified"

    VALID_STATUSES = ("verified", "stale", "missing")

    def __post_init__(self) -> None:
        """Validate ArtifactCopy field values after initialization."""
        raise NotImplementedError

    def is_missing(self) -> bool:
        """Return whether this copy is currently missing."""
        raise NotImplementedError

    def is_verified(self) -> bool:
        """Return whether this copy is currently verified."""
        raise NotImplementedError

    def is_stale(self) -> bool:
        """Return whether this copy is currently stale."""
        raise NotImplementedError
