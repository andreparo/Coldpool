from __future__ import annotations

from datetime import datetime

import pytest

from coldpool_server.artifact.artifact import Artifact
from coldpool_server.artifact.artifact_copy import ArtifactCopy
from coldpool_server.artifact.artifact_version import ArtifactVersion
from coldpool_server.disk.disk import Disk


def _build_disk(
    disk_id: int = 1,
    name: str = "disk_a",
    total_capacity_bytes: int = 1_000,
) -> Disk:
    return Disk(
        id=disk_id,
        name=name,
        total_capacity_bytes=total_capacity_bytes,
        health_score=0.8,
        copies=[],
    )


def _build_artifact() -> Artifact:
    return Artifact(
        id=1,
        name="photos_backup",
        priority_score=100,
        desired_copy_count=2,
        artifact_type="zip",
    )


def _build_artifact_version(
    artifact: Artifact | None = None,
    version_id: int = 1,
) -> ArtifactVersion:
    parent_artifact = artifact or _build_artifact()
    version = ArtifactVersion(
        id=version_id,
        artifact=parent_artifact,
        created_at=datetime(2026, 4, 15, 10, 30, 0),
        size_bytes=1024,
        version_label="v1",
        checksum="abc123",
        copies=[],
    )
    parent_artifact.add_version(version)
    return version


def test_artifact_copy_is_created_with_valid_data() -> None:
    disk = _build_disk()
    artifact_version = _build_artifact_version()

    artifact_copy = ArtifactCopy(
        id=1,
        artifact_version=artifact_version,
        copy_index=1,
        disk=disk,
        disk_path="/mnt/disk_a/backups/photos_v1.zip",
        is_present=True,
        status="verified",
    )

    assert artifact_copy.id == 1
    assert artifact_copy.artifact_version == artifact_version
    assert artifact_copy.copy_index == 1
    assert artifact_copy.disk == disk
    assert artifact_copy.disk_path == "/mnt/disk_a/backups/photos_v1.zip"
    assert artifact_copy.is_present is True
    assert artifact_copy.status == "verified"


def test_artifact_copy_raises_when_id_is_not_positive() -> None:
    disk = _build_disk()
    artifact_version = _build_artifact_version()

    with pytest.raises(ValueError, match="ArtifactCopy id must be > 0."):
        ArtifactCopy(
            id=0,
            artifact_version=artifact_version,
            copy_index=1,
            disk=disk,
            disk_path="/mnt/disk_a/backups/photos_v1.zip",
        )


def test_artifact_copy_raises_when_copy_index_is_less_than_one() -> None:
    disk = _build_disk()
    artifact_version = _build_artifact_version()

    with pytest.raises(
        ValueError,
        match="ArtifactCopy copy_index must be >= 1.",
    ):
        ArtifactCopy(
            id=1,
            artifact_version=artifact_version,
            copy_index=0,
            disk=disk,
            disk_path="/mnt/disk_a/backups/photos_v1.zip",
        )


def test_artifact_copy_raises_when_disk_path_is_blank() -> None:
    disk = _build_disk()
    artifact_version = _build_artifact_version()

    with pytest.raises(
        ValueError,
        match="ArtifactCopy disk_path must not be empty.",
    ):
        ArtifactCopy(
            id=1,
            artifact_version=artifact_version,
            copy_index=1,
            disk=disk,
            disk_path="   ",
        )


def test_artifact_copy_raises_when_status_is_invalid() -> None:
    disk = _build_disk()
    artifact_version = _build_artifact_version()

    with pytest.raises(
        ValueError,
        match="ArtifactCopy status must be one of: verified, stale, missing.",
    ):
        ArtifactCopy(
            id=1,
            artifact_version=artifact_version,
            copy_index=1,
            disk=disk,
            disk_path="/mnt/disk_a/backups/photos_v1.zip",
            status="broken",
        )


def test_artifact_copy_allows_valid_statuses() -> None:
    disk = _build_disk()
    artifact_version = _build_artifact_version()
    valid_statuses = ["verified", "stale", "missing"]

    for status in valid_statuses:
        artifact_copy = ArtifactCopy(
            id=1,
            artifact_version=artifact_version,
            copy_index=1,
            disk=disk,
            disk_path="/mnt/disk_a/backups/photos_v1.zip",
            status=status,
        )

        assert artifact_copy.status == status


def test_artifact_copy_is_present_can_be_false() -> None:
    disk = _build_disk()
    artifact_version = _build_artifact_version()

    artifact_copy = ArtifactCopy(
        id=1,
        artifact_version=artifact_version,
        copy_index=1,
        disk=disk,
        disk_path="/mnt/disk_a/backups/photos_v1.zip",
        is_present=False,
        status="missing",
    )

    assert artifact_copy.is_present is False
    assert artifact_copy.status == "missing"


def test_artifact_copy_exposes_size_bytes_from_its_artifact_version() -> None:
    disk = _build_disk()
    artifact_version = _build_artifact_version()

    artifact_copy = ArtifactCopy(
        id=1,
        artifact_version=artifact_version,
        copy_index=1,
        disk=disk,
        disk_path="/mnt/disk_a/backups/photos_v1.zip",
        is_present=True,
        status="verified",
    )

    assert artifact_copy.size_bytes == 1024


def test_artifact_copy_exposes_artifact_from_its_artifact_version() -> None:
    disk = _build_disk()
    artifact = _build_artifact()
    artifact_version = _build_artifact_version(artifact=artifact)

    artifact_copy = ArtifactCopy(
        id=1,
        artifact_version=artifact_version,
        copy_index=1,
        disk=disk,
        disk_path="/mnt/disk_a/backups/photos_v1.zip",
        is_present=True,
        status="verified",
    )

    assert artifact_copy.artifact == artifact


def test_artifact_copy_is_missing_returns_true_only_for_missing_status() -> None:
    disk_a = _build_disk(disk_id=1, name="disk_a")
    disk_b = _build_disk(disk_id=2, name="disk_b")
    artifact_version = _build_artifact_version()

    missing_copy = ArtifactCopy(
        id=1,
        artifact_version=artifact_version,
        copy_index=1,
        disk=disk_a,
        disk_path="/mnt/disk_a/backups/photos_v1.zip",
        status="missing",
    )
    verified_copy = ArtifactCopy(
        id=2,
        artifact_version=artifact_version,
        copy_index=2,
        disk=disk_b,
        disk_path="/mnt/disk_b/backups/photos_v1.zip",
        status="verified",
    )

    assert missing_copy.is_missing() is True
    assert verified_copy.is_missing() is False


def test_artifact_copy_is_verified_returns_true_only_for_verified_status() -> None:
    disk_a = _build_disk(disk_id=1, name="disk_a")
    disk_b = _build_disk(disk_id=2, name="disk_b")
    artifact_version = _build_artifact_version()

    verified_copy = ArtifactCopy(
        id=1,
        artifact_version=artifact_version,
        copy_index=1,
        disk=disk_a,
        disk_path="/mnt/disk_a/backups/photos_v1.zip",
        status="verified",
    )
    stale_copy = ArtifactCopy(
        id=2,
        artifact_version=artifact_version,
        copy_index=2,
        disk=disk_b,
        disk_path="/mnt/disk_b/backups/photos_v1.zip",
        status="stale",
    )

    assert verified_copy.is_verified() is True
    assert stale_copy.is_verified() is False


def test_artifact_copy_is_stale_returns_true_only_for_stale_status() -> None:
    disk_a = _build_disk(disk_id=1, name="disk_a")
    disk_b = _build_disk(disk_id=2, name="disk_b")
    artifact_version = _build_artifact_version()

    stale_copy = ArtifactCopy(
        id=1,
        artifact_version=artifact_version,
        copy_index=1,
        disk=disk_a,
        disk_path="/mnt/disk_a/backups/photos_v1.zip",
        status="stale",
    )
    missing_copy = ArtifactCopy(
        id=2,
        artifact_version=artifact_version,
        copy_index=2,
        disk=disk_b,
        disk_path="/mnt/disk_b/backups/photos_v1.zip",
        status="missing",
    )

    assert stale_copy.is_stale() is True
    assert missing_copy.is_stale() is False