from __future__ import annotations

from datetime import datetime

import pytest

from coldpool_server.artifact.artifact import Artifact
from coldpool_server.artifact.artifact_copy import ArtifactCopy
from coldpool_server.artifact.artifact_version import ArtifactVersion
from coldpool_server.disk.disk import Disk


def _build_artifact(
    artifact_id: int = 1,
    name: str = "photos_backup",
) -> Artifact:
    return Artifact(
        id=artifact_id,
        name=name,
        priority_score=100,
        desired_copy_count=2,
        artifact_type="zip",
    )


def _build_disk(
    disk_id: int = 1,
    name: str = "disk_a",
) -> Disk:
    return Disk(
        id=disk_id,
        name=name,
        total_capacity_bytes=1_000,
        health_score=0.8,
        copies=[],
    )


def test_artifact_version_is_created_with_valid_data() -> None:
    artifact = _build_artifact()
    created_at = datetime(2026, 4, 15, 10, 30, 0)
    expires_at = datetime(2026, 5, 15, 10, 30, 0)

    artifact_version = ArtifactVersion(
        id=1,
        artifact=artifact,
        created_at=created_at,
        size_bytes=1024,
        version_label="v1",
        checksum="abc123",
        expires_at=expires_at,
        copies=[],
    )

    assert artifact_version.id == 1
    assert artifact_version.artifact == artifact
    assert artifact_version.created_at == created_at
    assert artifact_version.size_bytes == 1024
    assert artifact_version.version_label == "v1"
    assert artifact_version.checksum == "abc123"
    assert artifact_version.expires_at == expires_at
    assert artifact_version.get_copies() == []


def test_artifact_version_raises_when_id_is_not_positive() -> None:
    artifact = _build_artifact()

    with pytest.raises(ValueError, match="ArtifactVersion id must be > 0."):
        ArtifactVersion(
            id=0,
            artifact=artifact,
            created_at=datetime(2026, 4, 15, 10, 30, 0),
            size_bytes=1024,
            copies=[],
        )


def test_artifact_version_raises_when_size_bytes_is_negative() -> None:
    artifact = _build_artifact()

    with pytest.raises(
        ValueError,
        match="ArtifactVersion size_bytes must be >= 0.",
    ):
        ArtifactVersion(
            id=1,
            artifact=artifact,
            created_at=datetime(2026, 4, 15, 10, 30, 0),
            size_bytes=-1,
            copies=[],
        )


def test_artifact_version_raises_when_version_label_is_blank() -> None:
    artifact = _build_artifact()

    with pytest.raises(
        ValueError,
        match="ArtifactVersion version_label must not be empty if provided.",
    ):
        ArtifactVersion(
            id=1,
            artifact=artifact,
            created_at=datetime(2026, 4, 15, 10, 30, 0),
            size_bytes=1024,
            version_label="   ",
            copies=[],
        )


def test_artifact_version_raises_when_checksum_is_blank() -> None:
    artifact = _build_artifact()

    with pytest.raises(
        ValueError,
        match="ArtifactVersion checksum must not be empty if provided.",
    ):
        ArtifactVersion(
            id=1,
            artifact=artifact,
            created_at=datetime(2026, 4, 15, 10, 30, 0),
            size_bytes=1024,
            checksum="   ",
            copies=[],
        )


def test_artifact_version_raises_when_expires_at_is_before_created_at() -> None:
    artifact = _build_artifact()

    with pytest.raises(
        ValueError,
        match="ArtifactVersion expires_at must be >= created_at.",
    ):
        ArtifactVersion(
            id=1,
            artifact=artifact,
            created_at=datetime(2026, 4, 15, 10, 30, 0),
            size_bytes=1024,
            expires_at=datetime(2026, 4, 14, 10, 30, 0),
            copies=[],
        )


def test_artifact_version_allows_optional_fields_to_be_none() -> None:
    artifact = _build_artifact()

    artifact_version = ArtifactVersion(
        id=1,
        artifact=artifact,
        created_at=datetime(2026, 4, 15, 10, 30, 0),
        size_bytes=1024,
        version_label=None,
        checksum=None,
        expires_at=None,
        copies=[],
    )

    assert artifact_version.version_label is None
    assert artifact_version.checksum is None
    assert artifact_version.expires_at is None


def test_add_copy_saves_copy_in_artifact_version() -> None:
    artifact = _build_artifact()
    disk = _build_disk()
    artifact_version = ArtifactVersion(
        id=1,
        artifact=artifact,
        created_at=datetime(2026, 4, 15, 10, 30, 0),
        size_bytes=1024,
        version_label="v1",
        checksum="abc123",
        copies=[],
    )
    artifact.add_version(artifact_version)

    artifact_copy = ArtifactCopy(
        id=1,
        artifact_version=artifact_version,
        copy_index=1,
        disk=disk,
        disk_path="/mnt/disk_a/photos_backup_v1.zip",
        is_present=True,
        status="verified",
    )

    artifact_version.add_copy(artifact_copy)

    saved_copies = artifact_version.get_copies()

    assert len(saved_copies) == 1
    assert saved_copies[0] == artifact_copy
    assert saved_copies[0].artifact_version == artifact_version


def test_remove_copy_removes_previously_added_copy() -> None:
    artifact = _build_artifact()
    disk = _build_disk()
    artifact_version = ArtifactVersion(
        id=1,
        artifact=artifact,
        created_at=datetime(2026, 4, 15, 10, 30, 0),
        size_bytes=1024,
        version_label="v1",
        checksum="abc123",
        copies=[],
    )
    artifact.add_version(artifact_version)

    artifact_copy = ArtifactCopy(
        id=1,
        artifact_version=artifact_version,
        copy_index=1,
        disk=disk,
        disk_path="/mnt/disk_a/photos_backup_v1.zip",
        is_present=True,
        status="verified",
    )

    artifact_version.add_copy(artifact_copy)
    artifact_version.remove_copy(copy_id=1)

    saved_copies = artifact_version.get_copies()

    assert saved_copies == []


def test_add_copy_raises_when_copy_artifact_version_does_not_match() -> None:
    artifact = _build_artifact()
    other_artifact = _build_artifact(artifact_id=2, name="videos_backup")
    disk = _build_disk()

    artifact_version = ArtifactVersion(
        id=1,
        artifact=artifact,
        created_at=datetime(2026, 4, 15, 10, 30, 0),
        size_bytes=1024,
        version_label="v1",
        checksum="abc123",
        copies=[],
    )
    other_version = ArtifactVersion(
        id=2,
        artifact=other_artifact,
        created_at=datetime(2026, 4, 16, 10, 30, 0),
        size_bytes=2048,
        version_label="v2",
        checksum="checksum-v2",
        copies=[],
    )

    artifact.add_version(artifact_version)
    other_artifact.add_version(other_version)

    artifact_copy = ArtifactCopy(
        id=1,
        artifact_version=other_version,
        copy_index=1,
        disk=disk,
        disk_path="/mnt/disk_a/photos_backup_v1.zip",
        is_present=True,
        status="verified",
    )

    with pytest.raises(
        ValueError,
        match="does not match ArtifactVersion",
    ):
        artifact_version.add_copy(artifact_copy)


def test_add_copy_raises_when_copy_id_already_exists() -> None:
    artifact = _build_artifact()
    disk_a = _build_disk(disk_id=1, name="disk_a")
    disk_b = _build_disk(disk_id=2, name="disk_b")
    artifact_version = ArtifactVersion(
        id=1,
        artifact=artifact,
        created_at=datetime(2026, 4, 15, 10, 30, 0),
        size_bytes=1024,
        version_label="v1",
        checksum="abc123",
        copies=[],
    )
    artifact.add_version(artifact_version)

    first_copy = ArtifactCopy(
        id=1,
        artifact_version=artifact_version,
        copy_index=1,
        disk=disk_a,
        disk_path="/mnt/disk_a/photos_backup_v1.zip",
        is_present=True,
        status="verified",
    )
    duplicate_id_copy = ArtifactCopy(
        id=1,
        artifact_version=artifact_version,
        copy_index=2,
        disk=disk_b,
        disk_path="/mnt/disk_b/photos_backup_v1.zip",
        is_present=True,
        status="verified",
    )

    artifact_version.add_copy(first_copy)

    with pytest.raises(ValueError, match="already exists"):
        artifact_version.add_copy(duplicate_id_copy)


def test_add_copy_raises_when_copy_index_already_exists() -> None:
    artifact = _build_artifact()
    disk_a = _build_disk(disk_id=1, name="disk_a")
    disk_b = _build_disk(disk_id=2, name="disk_b")
    artifact_version = ArtifactVersion(
        id=1,
        artifact=artifact,
        created_at=datetime(2026, 4, 15, 10, 30, 0),
        size_bytes=1024,
        version_label="v1",
        checksum="abc123",
        copies=[],
    )
    artifact.add_version(artifact_version)

    first_copy = ArtifactCopy(
        id=1,
        artifact_version=artifact_version,
        copy_index=1,
        disk=disk_a,
        disk_path="/mnt/disk_a/photos_backup_v1.zip",
        is_present=True,
        status="verified",
    )
    duplicate_index_copy = ArtifactCopy(
        id=2,
        artifact_version=artifact_version,
        copy_index=1,
        disk=disk_b,
        disk_path="/mnt/disk_b/photos_backup_v1.zip",
        is_present=True,
        status="verified",
    )

    artifact_version.add_copy(first_copy)

    with pytest.raises(ValueError, match="copy_index=1 already exists"):
        artifact_version.add_copy(duplicate_index_copy)


def test_remove_copy_raises_when_copy_does_not_exist() -> None:
    artifact = _build_artifact()
    artifact_version = ArtifactVersion(
        id=1,
        artifact=artifact,
        created_at=datetime(2026, 4, 15, 10, 30, 0),
        size_bytes=1024,
        version_label="v1",
        checksum="abc123",
        copies=[],
    )
    artifact.add_version(artifact_version)

    with pytest.raises(ValueError, match="was not found"):
        artifact_version.remove_copy(copy_id=999)


def test_get_copy_by_index_returns_matching_copy() -> None:
    artifact = _build_artifact()
    disk_a = _build_disk(disk_id=1, name="disk_a")
    disk_b = _build_disk(disk_id=2, name="disk_b")
    artifact_version = ArtifactVersion(
        id=1,
        artifact=artifact,
        created_at=datetime(2026, 4, 15, 10, 30, 0),
        size_bytes=1024,
        version_label="v1",
        checksum="abc123",
        copies=[],
    )
    artifact.add_version(artifact_version)

    first_copy = ArtifactCopy(
        id=1,
        artifact_version=artifact_version,
        copy_index=1,
        disk=disk_a,
        disk_path="/mnt/disk_a/photos_backup_v1.zip",
        is_present=True,
        status="verified",
    )
    second_copy = ArtifactCopy(
        id=2,
        artifact_version=artifact_version,
        copy_index=2,
        disk=disk_b,
        disk_path="/mnt/disk_b/photos_backup_v1.zip",
        is_present=True,
        status="verified",
    )

    artifact_version.add_copy(first_copy)
    artifact_version.add_copy(second_copy)

    found_copy = artifact_version.get_copy_by_index(copy_index=2)

    assert found_copy == second_copy


def test_get_copy_by_index_returns_none_when_missing() -> None:
    artifact = _build_artifact()
    artifact_version = ArtifactVersion(
        id=1,
        artifact=artifact,
        created_at=datetime(2026, 4, 15, 10, 30, 0),
        size_bytes=1024,
        version_label="v1",
        checksum="abc123",
        copies=[],
    )
    artifact.add_version(artifact_version)

    found_copy = artifact_version.get_copy_by_index(copy_index=1)

    assert found_copy is None