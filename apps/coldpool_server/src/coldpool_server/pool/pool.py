from __future__ import annotations

from dataclasses import dataclass, field

from coldpool_server.disk.disk import Disk


@dataclass(slots=True)
class Pool:
    """A collection of disks managed together by Coldpool."""

    disks: list[Disk] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate Pool field values after initialization."""
        self._validate_unique_disk_ids()
        self._validate_unique_disk_names()

    def _validate_unique_disk_ids(self) -> None:
        """Validate that disk ids are unique within the pool."""
        seen_disk_ids: set[int] = set()

        for disk in self.disks:
            if disk.id in seen_disk_ids:
                raise ValueError("Pool disks must not contain duplicate ids.")
            seen_disk_ids.add(disk.id)

    def _validate_unique_disk_names(self) -> None:
        """Validate that disk names are unique within the pool."""
        seen_disk_names: set[str] = set()

        for disk in self.disks:
            if disk.name in seen_disk_names:
                raise ValueError("Pool disks must not contain duplicate names.")
            seen_disk_names.add(disk.name)

    def get_total_capacity_bytes(self) -> int:
        """Return the total capacity across all disks in the pool."""
        return sum(disk.total_capacity_bytes for disk in self.disks)

    def get_total_used_space_bytes(self) -> int:
        """Return the total used space across all disks in the pool."""
        return sum(disk.get_used_space_bytes() for disk in self.disks)

    def get_total_free_space_bytes(self) -> int:
        """Return the total free space across all disks in the pool."""
        return sum(disk.free_space_bytes for disk in self.disks)
