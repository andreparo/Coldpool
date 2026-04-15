from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from coldpool_server.artifact.artifact import Artifact
    from coldpool_server.artifact.artifact_copy import ArtifactCopy


@dataclass(slots=True)
class ArtifactVersion:
    """A concrete stored version of one logical artifact."""

    id: int
    artifact: Artifact
    created_at: datetime
    size_bytes: int
    version_label: str | None = None
    checksum: str | None = None
    expires_at: datetime | None = None
    copies: list[ArtifactCopy] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate ArtifactVersion field values after initialization."""
        if self.id <= 0:
            raise ValueError("ArtifactVersion id must be > 0.")

        if self.size_bytes < 0:
            raise ValueError("ArtifactVersion size_bytes must be >= 0.")

        if self.version_label is not None and not self.version_label.strip():
            raise ValueError("ArtifactVersion version_label must not be empty if provided.")

        if self.checksum is not None and not self.checksum.strip():
            raise ValueError("ArtifactVersion checksum must not be empty if provided.")

        if self.expires_at is not None and self.expires_at < self.created_at:
            raise ValueError("ArtifactVersion expires_at must be >= created_at.")

        self._validate_initial_copies()

    def _validate_initial_copies(self) -> None:
        """Validate all copies provided at initialization."""
        seen_copy_ids: set[int] = set()
        seen_copy_indexes: set[int] = set()

        for artifact_copy in self.copies:
            if artifact_copy.artifact_version is not self:
                raise ValueError("ArtifactCopy artifact_version does not match ArtifactVersion.")

            if artifact_copy.id in seen_copy_ids:
                raise ValueError(f"ArtifactCopy with id={artifact_copy.id} already exists in this artifact version.")
            seen_copy_ids.add(artifact_copy.id)

            if artifact_copy.copy_index in seen_copy_indexes:
                raise ValueError(f"ArtifactCopy with copy_index={artifact_copy.copy_index} already exists in this artifact version.")
            seen_copy_indexes.add(artifact_copy.copy_index)

    def add_copy(self, artifact_copy: ArtifactCopy) -> None:
        """Add a new copy to this artifact version."""
        if artifact_copy.artifact_version is not self:
            raise ValueError("ArtifactCopy artifact_version does not match ArtifactVersion.")

        if any(existing_copy.id == artifact_copy.id for existing_copy in self.copies):
            raise ValueError(f"ArtifactCopy with id={artifact_copy.id} already exists in this artifact version.")

        if any(existing_copy.copy_index == artifact_copy.copy_index for existing_copy in self.copies):
            raise ValueError(f"ArtifactCopy with copy_index={artifact_copy.copy_index} already exists in this artifact version.")

        self.copies.append(artifact_copy)

    def remove_copy(self, copy_id: int) -> None:
        """Remove an existing copy from this artifact version by copy id."""
        for index, artifact_copy in enumerate(self.copies):
            if artifact_copy.id == copy_id:
                del self.copies[index]
                return

        raise ValueError(f"ArtifactCopy with id={copy_id} was not found.")

    def get_copies(self) -> list[ArtifactCopy]:
        """Return a copy of the copies currently stored in this artifact version."""
        return list(self.copies)

    def get_copy_by_index(self, copy_index: int) -> ArtifactCopy | None:
        """Return the copy with the given copy index, if present."""
        for artifact_copy in self.copies:
            if artifact_copy.copy_index == copy_index:
                return artifact_copy
        return None
