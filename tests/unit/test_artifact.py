from __future__ import annotations

from datetime import datetime

from coldpool_server.artifact import Artifact
from coldpool_server.artifact import ArtifactVersion


def test_add_version_saves_version_in_artifact() -> None:
    artifact = Artifact(
        id=1,
        name="photos_backup",
        priority_score=100,
        desired_copy_count=2,
        artifact_type="zip",
    )

    version = ArtifactVersion(
        id=1,
        artifact_id=1,
        created_at=datetime(2026, 4, 15, 10, 30, 0),
        size_bytes=1024,
        version_label="v1",
        checksum="abc123",
    )

    artifact.add_version(version)

    saved_versions = artifact.get_versions()

    assert len(saved_versions) == 1
    assert saved_versions[0] == version


def test_remove_version_removes_previously_added_version() -> None:
    artifact = Artifact(
        id=1,
        name="photos_backup",
        priority_score=100,
        desired_copy_count=2,
        artifact_type="zip",
    )

    version = ArtifactVersion(
        id=1,
        artifact_id=1,
        created_at=datetime(2026, 4, 15, 10, 30, 0),
        size_bytes=1024,
        version_label="v1",
        checksum="abc123",
    )

    artifact.add_version(version)
    artifact.remove_version(version_id=1)

    saved_versions = artifact.get_versions()

    assert saved_versions == []


def test_get_most_recent_version_returns_latest_added_by_created_at() -> None:
    artifact = Artifact(
        id=1,
        name="photos_backup",
        priority_score=100,
        desired_copy_count=2,
        artifact_type="zip",
    )

    older_version = ArtifactVersion(
        id=1,
        artifact_id=1,
        created_at=datetime(2026, 4, 15, 10, 30, 0),
        size_bytes=1024,
        version_label="v1",
        checksum="checksum-v1",
    )
    middle_version = ArtifactVersion(
        id=2,
        artifact_id=1,
        created_at=datetime(2026, 4, 16, 10, 30, 0),
        size_bytes=2048,
        version_label="v2",
        checksum="checksum-v2",
    )
    newest_version = ArtifactVersion(
        id=3,
        artifact_id=1,
        created_at=datetime(2026, 4, 17, 10, 30, 0),
        size_bytes=4096,
        version_label="v3",
        checksum="checksum-v3",
    )

    artifact.add_version(middle_version)
    artifact.add_version(older_version)
    artifact.add_version(newest_version)

    most_recent_version = artifact.get_most_recent_version()

    assert most_recent_version == newest_version


def test_remove_most_recent_version_keeps_next_most_recent_version_correct() -> None:
    artifact = Artifact(
        id=1,
        name="photos_backup",
        priority_score=100,
        desired_copy_count=2,
        artifact_type="zip",
    )

    older_version = ArtifactVersion(
        id=1,
        artifact_id=1,
        created_at=datetime(2026, 4, 15, 10, 30, 0),
        size_bytes=1024,
        version_label="v1",
        checksum="checksum-v1",
    )
    middle_version = ArtifactVersion(
        id=2,
        artifact_id=1,
        created_at=datetime(2026, 4, 16, 10, 30, 0),
        size_bytes=2048,
        version_label="v2",
        checksum="checksum-v2",
    )
    newest_version = ArtifactVersion(
        id=3,
        artifact_id=1,
        created_at=datetime(2026, 4, 17, 10, 30, 0),
        size_bytes=4096,
        version_label="v3",
        checksum="checksum-v3",
    )

    artifact.add_version(older_version)
    artifact.add_version(middle_version)
    artifact.add_version(newest_version)

    artifact.remove_version(version_id=3)

    most_recent_version = artifact.get_most_recent_version()

    assert most_recent_version == middle_version