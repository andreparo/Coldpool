from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from coldpool_server.artifact.artifact_copy import ArtifactCopy


@dataclass(slots=True)
class Disk:
    """A physical storage disk available for artifact copy placement."""

    id: int
    name: str
    total_capacity_bytes: int
    health_score: float
    location: str | None = None
    state: str = "offline"
    copies: list[ArtifactCopy] = field(default_factory=list)

    VALID_STATES = ("online", "offline", "offsite", "retired")

    def __post_init__(self) -> None:
        """Validate Disk field values after initialization."""
        if self.id <= 0:
            raise ValueError("Disk id must be > 0.")

        if not self.name.strip():
            raise ValueError("Disk name must not be empty.")

        if self.total_capacity_bytes < 0:
            raise ValueError("Disk total_capacity_bytes must be >= 0.")

        if not 0.0 <= self.health_score <= 1.0:
            raise ValueError("Disk health_score must be between 0.0 and 1.0.")

        if self.location is not None and not self.location.strip():
            raise ValueError("Disk location must not be empty if provided.")

        if self.state not in self.VALID_STATES:
            raise ValueError("Disk state must be one of: online, offline, offsite, retired.")

        self._validate_initial_copies()

    @property
    def free_space_bytes(self) -> int:
        """Return the remaining free space derived from stored copies."""
        return self.total_capacity_bytes - self.get_used_space_bytes()

    def _validate_initial_copies(self) -> None:
        """Validate all copies provided at initialization."""
        seen_copy_ids: set[int] = set()
        seen_slots: set[tuple[int, int]] = set()
        seen_versions: set[int] = set()

        for artifact_copy in self.copies:
            if artifact_copy.disk is not self:
                raise ValueError("ArtifactCopy disk does not match Disk.")

            if artifact_copy.id in seen_copy_ids:
                raise ValueError(f"ArtifactCopy with id={artifact_copy.id} already exists in this disk.")
            seen_copy_ids.add(artifact_copy.id)

            slot = (artifact_copy.artifact_version.id, artifact_copy.copy_index)
            if slot in seen_slots:
                raise ValueError(f"ArtifactCopy with copy_index={artifact_copy.copy_index} already exists in this disk.")
            seen_slots.add(slot)

            version_id = artifact_copy.artifact_version.id
            if version_id in seen_versions:
                raise ValueError("Disk must not contain more than one copy of the same artifact version.")
            seen_versions.add(version_id)

        if self.get_used_space_bytes() > self.total_capacity_bytes:
            raise ValueError("Disk copies exceed total capacity.")

    def add_copy(self, artifact_copy: ArtifactCopy) -> None:
        """Add a new copy to this disk."""
        if artifact_copy.disk is not self:
            raise ValueError("ArtifactCopy disk does not match Disk.")

        if any(existing_copy.id == artifact_copy.id for existing_copy in self.copies):
            raise ValueError(f"ArtifactCopy with id={artifact_copy.id} already exists in this disk.")

        if any(
            existing_copy.artifact_version.id == artifact_copy.artifact_version.id
            and existing_copy.copy_index == artifact_copy.copy_index
            for existing_copy in self.copies
        ):
            raise ValueError(f"ArtifactCopy with copy_index={artifact_copy.copy_index} already exists in this disk.")

        if any(existing_copy.artifact_version.id == artifact_copy.artifact_version.id for existing_copy in self.copies):
            raise ValueError("Disk must not contain more than one copy of the same artifact version.")

        if self.get_used_space_bytes() + artifact_copy.size_bytes > self.total_capacity_bytes:
            raise ValueError("Disk copies exceed total capacity.")

        self.copies.append(artifact_copy)

    def remove_copy(self, copy_id: int) -> None:
        """Remove an existing copy from this disk by copy id."""
        for index, artifact_copy in enumerate(self.copies):
            if artifact_copy.id == copy_id:
                del self.copies[index]
                return

        raise ValueError(f"ArtifactCopy with id={copy_id} was not found.")

    def get_copies(self) -> list[ArtifactCopy]:
        """Return a copy of the copies currently stored in this disk."""
        return list(self.copies)

    def can_store_size(self, size_bytes: int) -> bool:
        """Return whether the disk can store a payload of the given size."""
        if size_bytes < 0:
            raise ValueError("size_bytes must be >= 0.")
        return size_bytes <= self.free_space_bytes

    def get_used_space_bytes(self) -> int:
        """Return the currently used space on the disk from stored copies."""
        return sum(artifact_copy.size_bytes for artifact_copy in self.copies)

    def is_online(self) -> bool:
        """Return whether the disk is currently online."""
        return self.state == "online"

    def is_retired(self) -> bool:
        """Return whether the disk is retired and should not receive new copies."""
        return self.state == "retired"
