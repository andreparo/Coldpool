from __future__ import annotations

import pytest

from coldpool_server.artifact.artifact_copy import ArtifactCopy


def test_artifact_copy_is_created_with_valid_data() -> None:
    artifact_copy = ArtifactCopy(
        id=1,
        artifact_version_id=10,
        copy_index=1,
        disk_id=20,
        disk_path="/mnt/disk_a/backups/photos_v1.zip",
        is_present=True,
        status="verified",
    )

    assert artifact_copy.id == 1
    assert artifact_copy.artifact_version_id == 10
    assert artifact_copy.copy_index == 1
    assert artifact_copy.disk_id == 20
    assert artifact_copy.disk_path == "/mnt/disk_a/backups/photos_v1.zip"
    assert artifact_copy.is_present is True
    assert artifact_copy.status == "verified"


def test_artifact_copy_raises_when_id_is_not_positive() -> None:
    with pytest.raises(ValueError, match="ArtifactCopy id must be > 0."):
        ArtifactCopy(
            id=0,
            artifact_version_id=10,
            copy_index=1,
            disk_id=20,
            disk_path="/mnt/disk_a/backups/photos_v1.zip",
        )


def test_artifact_copy_raises_when_artifact_version_id_is_not_positive() -> None:
    with pytest.raises(
        ValueError,
        match="ArtifactCopy artifact_version_id must be > 0.",
    ):
        ArtifactCopy(
            id=1,
            artifact_version_id=0,
            copy_index=1,
            disk_id=20,
            disk_path="/mnt/disk_a/backups/photos_v1.zip",
        )


def test_artifact_copy_raises_when_copy_index_is_less_than_one() -> None:
    with pytest.raises(
        ValueError,
        match="ArtifactCopy copy_index must be >= 1.",
    ):
        ArtifactCopy(
            id=1,
            artifact_version_id=10,
            copy_index=0,
            disk_id=20,
            disk_path="/mnt/disk_a/backups/photos_v1.zip",
        )


def test_artifact_copy_raises_when_disk_id_is_not_positive() -> None:
    with pytest.raises(ValueError, match="ArtifactCopy disk_id must be > 0."):
        ArtifactCopy(
            id=1,
            artifact_version_id=10,
            copy_index=1,
            disk_id=0,
            disk_path="/mnt/disk_a/backups/photos_v1.zip",
        )


def test_artifact_copy_raises_when_disk_path_is_blank() -> None:
    with pytest.raises(
        ValueError,
        match="ArtifactCopy disk_path must not be empty.",
    ):
        ArtifactCopy(
            id=1,
            artifact_version_id=10,
            copy_index=1,
            disk_id=20,
            disk_path="   ",
        )


def test_artifact_copy_raises_when_status_is_invalid() -> None:
    with pytest.raises(
        ValueError,
        match="ArtifactCopy status must be one of: verified, stale, missing.",
    ):
        ArtifactCopy(
            id=1,
            artifact_version_id=10,
            copy_index=1,
            disk_id=20,
            disk_path="/mnt/disk_a/backups/photos_v1.zip",
            status="broken",
        )


def test_artifact_copy_allows_valid_statuses() -> None:
    valid_statuses = ["verified", "stale", "missing"]

    for status in valid_statuses:
        artifact_copy = ArtifactCopy(
            id=1,
            artifact_version_id=10,
            copy_index=1,
            disk_id=20,
            disk_path="/mnt/disk_a/backups/photos_v1.zip",
            status=status,
        )

        assert artifact_copy.status == status


def test_artifact_copy_is_present_can_be_false() -> None:
    artifact_copy = ArtifactCopy(
        id=1,
        artifact_version_id=10,
        copy_index=1,
        disk_id=20,
        disk_path="/mnt/disk_a/backups/photos_v1.zip",
        is_present=False,
        status="missing",
    )

    assert artifact_copy.is_present is False
    assert artifact_copy.status == "missing"