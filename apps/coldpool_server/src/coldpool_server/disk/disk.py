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

    VALID_STATES = ("online", "offline", "offsite", "retired")

    def __post_init__(self) -> None:
        """Validate Disk field values after initialization."""
        if self.id <= 0:
            raise ValueError("Disk id must be > 0.")

        if not self.name.strip():
            raise ValueError("Disk name must not be empty.")

        if self.total_capacity_bytes < 0:
            raise ValueError("Disk total_capacity_bytes must be >= 0.")

        if self.free_space_bytes < 0:
            raise ValueError("Disk free_space_bytes must be >= 0.")

        if self.free_space_bytes > self.total_capacity_bytes:
            raise ValueError("Disk free_space_bytes must be <= total_capacity_bytes.")

        if not 0.0 <= self.health_score <= 1.0:
            raise ValueError("Disk health_score must be between 0.0 and 1.0.")

        if self.location is not None and not self.location.strip():
            raise ValueError("Disk location must not be empty if provided.")

        if self.state not in self.VALID_STATES:
            raise ValueError("Disk state must be one of: online, offline, offsite, retired.")

    def can_store_size(self, size_bytes: int) -> bool:
        """Return whether the disk can store a payload of the given size."""
        if size_bytes < 0:
            raise ValueError("size_bytes must be >= 0.")
        return size_bytes <= self.free_space_bytes

    def get_used_space_bytes(self) -> int:
        """Return the currently used space on the disk."""
        return self.total_capacity_bytes - self.free_space_bytes

    def is_online(self) -> bool:
        """Return whether the disk is currently online."""
        return self.state == "online"

    def is_retired(self) -> bool:
        """Return whether the disk is retired and should not receive new copies."""
        return self.state == "retired"
