from __future__ import annotations

from dataclasses import dataclass, field

from coldpool_server.artifact.artifact_version import ArtifactVersion


@dataclass(slots=True)
class Artifact:
    """A logical backup artifact that can contain multiple versions."""

    id: int
    name: str
    priority_score: int
    desired_copy_count: int
    artifact_type: str | None = None
    shelf_life_days: int | None = None
    _versions: list[ArtifactVersion] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        """Validate Artifact field values after initialization."""
        if self.id <= 0:
            raise ValueError("Artifact id must be > 0.")

        if not self.name.strip():
            raise ValueError("Artifact name must not be empty.")

        if self.priority_score < 0:
            raise ValueError("Artifact priority_score must be >= 0.")

        if self.desired_copy_count < 0:
            raise ValueError("Artifact desired_copy_count must be >= 0.")

        if self.artifact_type is not None and not self.artifact_type.strip():
            raise ValueError("Artifact artifact_type must not be empty if provided.")

        if self.shelf_life_days is not None and self.shelf_life_days < 0:
            raise ValueError("Artifact shelf_life_days must be >= 0 if provided.")

    def add_version(self, version: ArtifactVersion) -> None:
        """Add a new version to this artifact."""
        if version.artifact is not self:
            raise ValueError("ArtifactVersion artifact does not match Artifact.")

        if any(existing_version.id == version.id for existing_version in self._versions):
            raise ValueError(f"ArtifactVersion with id={version.id} already exists in this artifact.")

        self._versions.append(version)

    def remove_version(self, version_id: int) -> None:
        """Remove an existing version from this artifact by version id."""
        for index, version in enumerate(self._versions):
            if version.id == version_id:
                del self._versions[index]
                return

        raise ValueError(f"ArtifactVersion with id={version_id} was not found.")

    def get_versions(self) -> list[ArtifactVersion]:
        """Return a copy of the versions currently stored in this artifact."""
        return list(self._versions)

    def get_most_recent_version(self) -> ArtifactVersion | None:
        """Return the most recent version of this artifact, if any."""
        if not self._versions:
            return None

        return max(
            self._versions,
            key=lambda version: (version.created_at, version.id),
        )
