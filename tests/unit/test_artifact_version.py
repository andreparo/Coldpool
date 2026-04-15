from __future__ import annotations

from datetime import datetime

import pytest

from coldpool_server.artifact.artifact_version import ArtifactVersion


def test_artifact_version_is_created_with_valid_data() -> None:
    created_at = datetime(2026, 4, 15, 10, 30, 0)
    expires_at = datetime(2026, 5, 15, 10, 30, 0)

    artifact_version = ArtifactVersion(
        id=1,
        artifact_id=1,
        created_at=created_at,
        size_bytes=1024,
        version_label="v1",
        checksum="abc123",
        expires_at=expires_at,
    )

    assert artifact_version.id == 1
    assert artifact_version.artifact_id == 1
    assert artifact_version.created_at == created_at
    assert artifact_version.size_bytes == 1024
    assert artifact_version.version_label == "v1"
    assert artifact_version.checksum == "abc123"
    assert artifact_version.expires_at == expires_at


def test_artifact_version_raises_when_id_is_not_positive() -> None:
    with pytest.raises(ValueError, match="ArtifactVersion id must be > 0."):
        ArtifactVersion(
            id=0,
            artifact_id=1,
            created_at=datetime(2026, 4, 15, 10, 30, 0),
            size_bytes=1024,
        )


def test_artifact_version_raises_when_artifact_id_is_not_positive() -> None:
    with pytest.raises(
        ValueError,
        match="ArtifactVersion artifact_id must be > 0.",
    ):
        ArtifactVersion(
            id=1,
            artifact_id=0,
            created_at=datetime(2026, 4, 15, 10, 30, 0),
            size_bytes=1024,
        )


def test_artifact_version_raises_when_size_bytes_is_negative() -> None:
    with pytest.raises(
        ValueError,
        match="ArtifactVersion size_bytes must be >= 0.",
    ):
        ArtifactVersion(
            id=1,
            artifact_id=1,
            created_at=datetime(2026, 4, 15, 10, 30, 0),
            size_bytes=-1,
        )


def test_artifact_version_raises_when_version_label_is_blank() -> None:
    with pytest.raises(
        ValueError,
        match="ArtifactVersion version_label must not be empty if provided.",
    ):
        ArtifactVersion(
            id=1,
            artifact_id=1,
            created_at=datetime(2026, 4, 15, 10, 30, 0),
            size_bytes=1024,
            version_label="   ",
        )


def test_artifact_version_raises_when_checksum_is_blank() -> None:
    with pytest.raises(
        ValueError,
        match="ArtifactVersion checksum must not be empty if provided.",
    ):
        ArtifactVersion(
            id=1,
            artifact_id=1,
            created_at=datetime(2026, 4, 15, 10, 30, 0),
            size_bytes=1024,
            checksum="   ",
        )


def test_artifact_version_raises_when_expires_at_is_before_created_at() -> None:
    with pytest.raises(
        ValueError,
        match="ArtifactVersion expires_at must be >= created_at.",
    ):
        ArtifactVersion(
            id=1,
            artifact_id=1,
            created_at=datetime(2026, 4, 15, 10, 30, 0),
            size_bytes=1024,
            expires_at=datetime(2026, 4, 14, 10, 30, 0),
        )


def test_artifact_version_allows_optional_fields_to_be_none() -> None:
    artifact_version = ArtifactVersion(
        id=1,
        artifact_id=1,
        created_at=datetime(2026, 4, 15, 10, 30, 0),
        size_bytes=1024,
        version_label=None,
        checksum=None,
        expires_at=None,
    )

    assert artifact_version.version_label is None
    assert artifact_version.checksum is None
    assert artifact_version.expires_at is None