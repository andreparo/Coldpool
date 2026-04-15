from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Disk:
    """A physical storage disk available for artifact copy placement."""

    id: int
    name: str
    total_capacity_bytes: int
    free_space_bytes: int
    health_score: float
    location: str | None = None
    state: str = "offline"

    def __post_init__(self) -> None:
        """Validate Disk field values after initialization."""
        raise NotImplementedError

    def can_store_size(self, size_bytes: int) -> bool:
        """Return whether the disk can store a payload of the given size."""
        raise NotImplementedError

    def get_used_space_bytes(self) -> int:
        """Return the currently used space on the disk."""
        raise NotImplementedError

    def is_online(self) -> bool:
        """Return whether the disk is currently online."""
        raise NotImplementedError

    def is_retired(self) -> bool:
        """Return whether the disk is retired and should not receive new copies."""
        raise NotImplementedError
