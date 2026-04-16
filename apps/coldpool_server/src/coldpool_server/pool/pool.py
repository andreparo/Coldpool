from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from coldpool_server.artifact.artifact import Artifact
    from coldpool_server.artifact.artifact_copy import ArtifactCopy
    from coldpool_server.artifact.artifact_version import ArtifactVersion
    from coldpool_server.disk.disk import Disk


@dataclass(slots=True)
class Pool:
    """A connected storage pool composed of disks and managed artifacts."""

    disks: list[Disk]
    artifacts: list[Artifact]

    def __post_init__(self) -> None:
        """Validate pool-level uniqueness and graph consistency."""
        self._validate_unique_disks()
        self._validate_unique_artifacts()
        self._validate_copy_graph_consistency()

    def _validate_unique_disks(self) -> None:
        """Validate that disk ids and names are unique in the pool."""
        seen_disk_ids: set[int] = set()
        seen_disk_names: set[str] = set()

        for disk in self.disks:
            if disk.id in seen_disk_ids:
                raise ValueError("Pool disks must not contain duplicate ids.")
            seen_disk_ids.add(disk.id)

            if disk.name in seen_disk_names:
                raise ValueError("Pool disks must not contain duplicate names.")
            seen_disk_names.add(disk.name)

    def _validate_unique_artifacts(self) -> None:
        """Validate that artifact ids are unique in the pool."""
        seen_artifact_ids: set[int] = set()

        for artifact in self.artifacts:
            if artifact.id in seen_artifact_ids:
                raise ValueError("Pool must not contain duplicate artifact ids.")
            seen_artifact_ids.add(artifact.id)

    def _validate_copy_graph_consistency(self) -> None:
        """Validate that artifact-side and disk-side copy views are consistent."""
        pool_disks_by_id = {disk.id: disk for disk in self.disks}
        pool_artifact_ids = {artifact.id for artifact in self.artifacts}

        artifact_side_copies: set[int] = set()
        disk_side_copies: set[int] = set()

        for artifact in self.artifacts:
            for version in artifact.get_versions():
                self._validate_version_belongs_to_artifact(
                    artifact=artifact,
                    version=version,
                )

                for artifact_copy in version.get_copies():
                    self._validate_artifact_side_copy(
                        artifact_copy=artifact_copy,
                        version=version,
                        pool_disks_by_id=pool_disks_by_id,
                    )
                    artifact_side_copies.add(id(artifact_copy))

        for disk in self.disks:
            for artifact_copy in disk.get_copies():
                self._validate_disk_side_copy(
                    artifact_copy=artifact_copy,
                    disk=disk,
                    pool_artifact_ids=pool_artifact_ids,
                )
                disk_side_copies.add(id(artifact_copy))

        if artifact_side_copies != disk_side_copies:
            raise ValueError("Pool artifact-side copies and disk-side copies are inconsistent.")

    def _validate_version_belongs_to_artifact(
        self,
        artifact: Artifact,
        version: ArtifactVersion,
    ) -> None:
        """Validate that a version points back to the artifact that contains it."""
        if version.artifact is not artifact:
            raise ValueError("Pool contains an artifact version whose artifact reference is inconsistent.")

    def _validate_artifact_side_copy(
        self,
        artifact_copy: ArtifactCopy,
        version: ArtifactVersion,
        pool_disks_by_id: dict[int, Disk],
    ) -> None:
        """Validate one copy reached from the artifact/version side."""
        if artifact_copy.artifact_version is not version:
            raise ValueError("Pool contains a copy whose artifact version reference is inconsistent.")

        if artifact_copy.disk.id not in pool_disks_by_id:
            raise ValueError("Pool contains a copy whose disk is not in pool.")

        pool_disk = pool_disks_by_id[artifact_copy.disk.id]
        if artifact_copy.disk is not pool_disk:
            raise ValueError("Pool contains a copy whose disk object is inconsistent with pool disks.")

        if artifact_copy not in pool_disk.get_copies():
            raise ValueError("Pool contains a copy missing from disk.")

    def _validate_disk_side_copy(
        self,
        artifact_copy: ArtifactCopy,
        disk: Disk,
        pool_artifact_ids: set[int],
    ) -> None:
        """Validate one copy reached from the disk side."""
        if artifact_copy.disk is not disk:
            raise ValueError("Pool contains a disk copy whose disk reference is inconsistent.")

        artifact = artifact_copy.artifact
        if artifact.id not in pool_artifact_ids:
            raise ValueError("Pool contains a disk copy whose artifact is not in pool.")

        if artifact_copy not in artifact_copy.artifact_version.get_copies():
            raise ValueError("Pool contains a disk copy missing from version.")

    def get_disk_by_id(self, disk_id: int) -> Disk | None:
        """Return the disk with the given id, if present."""
        for disk in self.disks:
            if disk.id == disk_id:
                return disk
        return None

    def get_artifact_by_id(self, artifact_id: int) -> Artifact | None:
        """Return the artifact with the given id, if present."""
        for artifact in self.artifacts:
            if artifact.id == artifact_id:
                return artifact
        return None

    def get_version_by_id(self, version_id: int) -> ArtifactVersion | None:
        """Return the artifact version with the given id, if present."""
        for artifact in self.artifacts:
            for version in artifact.get_versions():
                if version.id == version_id:
                    return version
        return None

    def get_copy_by_id(self, copy_id: int) -> ArtifactCopy | None:
        """Return the artifact copy with the given id, if present."""
        for artifact in self.artifacts:
            for version in artifact.get_versions():
                for artifact_copy in version.get_copies():
                    if artifact_copy.id == copy_id:
                        return artifact_copy
        return None

    def get_all_versions(self) -> list[ArtifactVersion]:
        """Return all artifact versions across all artifacts."""
        versions: list[ArtifactVersion] = []
        for artifact in self.artifacts:
            versions.extend(artifact.get_versions())
        return versions

    def get_all_copies(self) -> list[ArtifactCopy]:
        """Return all artifact copies across all artifacts."""
        copies: list[ArtifactCopy] = []
        for version in self.get_all_versions():
            copies.extend(version.get_copies())
        return copies

    def add_disk(self, disk: Disk) -> None:
        """Add a new disk to the pool after validating uniqueness."""
        if self.get_disk_by_id(disk.id) is not None:
            raise ValueError("Pool disks must not contain duplicate ids.")

        if any(existing_disk.name == disk.name for existing_disk in self.disks):
            raise ValueError("Pool disks must not contain duplicate names.")

        self.disks.append(disk)

    def remove_disk_if_empty(self, disk_id: int) -> None:
        """Remove an existing disk from the pool only if it contains no copies."""
        for index, disk in enumerate(self.disks):
            if disk.id != disk_id:
                continue

            if disk.get_copies():
                raise ValueError(f"Disk with id={disk_id} is not empty.")

            del self.disks[index]
            return

        raise ValueError(f"Disk with id={disk_id} was not found.")

    def get_total_capacity_bytes(self) -> int:
        """Return the total storage capacity across all disks."""
        return sum(disk.total_capacity_bytes for disk in self.disks)

    def get_total_used_space_bytes(self) -> int:
        """Return the total used storage across all disks."""
        return sum(disk.get_used_space_bytes() for disk in self.disks)

    def get_total_free_space_bytes(self) -> int:
        """Return the total free storage across all disks."""
        return sum(disk.free_space_bytes for disk in self.disks)
