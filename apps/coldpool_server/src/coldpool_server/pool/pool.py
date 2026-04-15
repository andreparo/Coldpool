from __future__ import annotations

from dataclasses import dataclass, field

from coldpool_server.disk.disk import Disk


@dataclass(slots=True)
class Pool:
    """A collection of disks managed together by Coldpool."""

    disks: list[Disk] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate Pool field values after initialization."""
        raise NotImplementedError

    def get_total_capacity_bytes(self) -> int:
        """Return the total capacity across all disks in the pool."""
        raise NotImplementedError

    def get_total_used_space_bytes(self) -> int:
        """Return the total used space across all disks in the pool."""
        raise NotImplementedError

    def get_total_free_space_bytes(self) -> int:
        """Return the total free space across all disks in the pool."""
        raise NotImplementedError
