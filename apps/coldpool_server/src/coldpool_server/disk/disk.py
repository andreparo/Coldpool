from __future__ import annotations

from dataclasses import dataclass, field

from coldpool_server.artifact.artifact import Artifact


@dataclass(slots=True)
class Disk:
    """A physical storage disk available for artifact copy placement."""

    id: int
    name: str
    total_capacity_bytes: int
    health_score: float
    location: str | None = None
    state: str = "offline"
    artifacts: list[Artifact] = field(default_factory=list)

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

        self._validate_artifacts_have_no_duplicates()
        self._validate_artifacts_have_most_recent_versions()
        self._validate_artifacts_fit_total_capacity()

    @property
    def free_space_bytes(self) -> int:
        """Return the remaining free space derived from stored artifacts."""
        return self.total_capacity_bytes - self.get_used_space_bytes()

    def _validate_artifacts_have_no_duplicates(self) -> None:
        """Validate that the artifacts list does not contain duplicates."""
        seen_artifact_ids: set[int] = set()

        for artifact in self.artifacts:
            if artifact.id in seen_artifact_ids:
                raise ValueError("Disk artifacts must not contain duplicates.")
            seen_artifact_ids.add(artifact.id)

    def _validate_artifacts_have_most_recent_versions(self) -> None:
        """Validate that every artifact has a most recent version."""
        for artifact in self.artifacts:
            if artifact.get_most_recent_version() is None:
                raise ValueError("Disk artifacts must have a most recent version.")

    def _validate_artifacts_fit_total_capacity(self) -> None:
        """Validate that artifact sizes fit inside the disk total capacity."""
        if self.get_used_space_bytes() > self.total_capacity_bytes:
            raise ValueError("Disk artifacts exceed total capacity.")

    def can_store_size(self, size_bytes: int) -> bool:
        """Return whether the disk can store a payload of the given size."""
        if size_bytes < 0:
            raise ValueError("size_bytes must be >= 0.")
        return size_bytes <= self.free_space_bytes

    def get_used_space_bytes(self) -> int:
        """Return the currently used space on the disk from stored artifacts."""
        used_space_bytes = 0

        for artifact in self.artifacts:
            most_recent_version = artifact.get_most_recent_version()
            if most_recent_version is None:
                raise ValueError("Disk artifacts must have a most recent version.")
            used_space_bytes += most_recent_version.size_bytes

        return used_space_bytes

    def is_online(self) -> bool:
        """Return whether the disk is currently online."""
        return self.state == "online"

    def is_retired(self) -> bool:
        """Return whether the disk is retired and should not receive new copies."""
        return self.state == "retired"
