from __future__ import annotations

from datetime import datetime

import pytest

from coldpool_server.artifact.artifact import Artifact
from coldpool_server.artifact.artifact_version import ArtifactVersion
from coldpool_server.disk.disk import Disk


def _build_artifact(
    artifact_id: int,
    name: str,
    size_bytes: int,
    created_at: datetime | None = None,
) -> Artifact:
    artifact = Artifact(
        id=artifact_id,
        name=name,
        priority_score=100,
        desired_copy_count=2,
        artifact_type="zip",
    )
    artifact.add_version(
        ArtifactVersion(
            id=artifact_id,
            artifact_id=artifact_id,
            created_at=created_at or datetime(2026, 4, 15, 10, 30, 0),
            size_bytes=size_bytes,
            version_label="v1",
            checksum=f"checksum-{artifact_id}",
        )
    )
    return artifact


def test_disk_is_created_with_valid_data() -> None:
    disk = Disk(
        id=1,
        name="disk_a",
        total_capacity_bytes=1_000,
        free_space_bytes=400,
        health_score=0.8,
        location="office",
        state="offline",
        artifacts=[],
    )

    assert disk.id == 1
    assert disk.name == "disk_a"
    assert disk.total_capacity_bytes == 1_000
    assert disk.free_space_bytes == 400
    assert disk.health_score == 0.8
    assert disk.location == "office"
    assert disk.state == "offline"


def test_disk_raises_when_id_is_not_positive() -> None:
    with pytest.raises(ValueError, match="Disk id must be > 0."):
        Disk(
            id=0,
            name="disk_a",
            total_capacity_bytes=1_000,
            free_space_bytes=400,
            health_score=0.8,
            artifacts=[],
        )


def test_disk_raises_when_name_is_blank() -> None:
    with pytest.raises(ValueError, match="Disk name must not be empty."):
        Disk(
            id=1,
            name="   ",
            total_capacity_bytes=1_000,
            free_space_bytes=400,
            health_score=0.8,
            artifacts=[],
        )


def test_disk_raises_when_total_capacity_bytes_is_negative() -> None:
    with pytest.raises(
        ValueError,
        match="Disk total_capacity_bytes must be >= 0.",
    ):
        Disk(
            id=1,
            name="disk_a",
            total_capacity_bytes=-1,
            free_space_bytes=400,
            health_score=0.8,
            artifacts=[],
        )


def test_disk_raises_when_free_space_bytes_is_negative() -> None:
    with pytest.raises(
        ValueError,
        match="Disk free_space_bytes must be >= 0.",
    ):
        Disk(
            id=1,
            name="disk_a",
            total_capacity_bytes=1_000,
            free_space_bytes=-1,
            health_score=0.8,
            artifacts=[],
        )


def test_disk_raises_when_free_space_bytes_exceeds_total_capacity_bytes() -> None:
    with pytest.raises(
        ValueError,
        match="Disk free_space_bytes must be <= total_capacity_bytes.",
    ):
        Disk(
            id=1,
            name="disk_a",
            total_capacity_bytes=1_000,
            free_space_bytes=1_001,
            health_score=0.8,
            artifacts=[],
        )


def test_disk_raises_when_health_score_is_below_zero() -> None:
    with pytest.raises(
        ValueError,
        match="Disk health_score must be between 0.0 and 1.0.",
    ):
        Disk(
            id=1,
            name="disk_a",
            total_capacity_bytes=1_000,
            free_space_bytes=400,
            health_score=-0.1,
            artifacts=[],
        )


def test_disk_raises_when_health_score_is_above_one() -> None:
    with pytest.raises(
        ValueError,
        match="Disk health_score must be between 0.0 and 1.0.",
    ):
        Disk(
            id=1,
            name="disk_a",
            total_capacity_bytes=1_000,
            free_space_bytes=400,
            health_score=1.1,
            artifacts=[],
        )


def test_disk_raises_when_location_is_blank() -> None:
    with pytest.raises(
        ValueError,
        match="Disk location must not be empty if provided.",
    ):
        Disk(
            id=1,
            name="disk_a",
            total_capacity_bytes=1_000,
            free_space_bytes=400,
            health_score=0.8,
            location="   ",
            artifacts=[],
        )


def test_disk_raises_when_state_is_invalid() -> None:
    with pytest.raises(
        ValueError,
        match="Disk state must be one of: online, offline, offsite, retired.",
    ):
        Disk(
            id=1,
            name="disk_a",
            total_capacity_bytes=1_000,
            free_space_bytes=400,
            health_score=0.8,
            state="broken",
            artifacts=[],
        )


def test_disk_allows_valid_states() -> None:
    valid_states = ["online", "offline", "offsite", "retired"]

    for state in valid_states:
        disk = Disk(
            id=1,
            name="disk_a",
            total_capacity_bytes=1_000,
            free_space_bytes=400,
            health_score=0.8,
            state=state,
            artifacts=[],
        )

        assert disk.state == state


def test_disk_accepts_artifacts_that_fit_in_used_space_budget() -> None:
    artifact_a = _build_artifact(1, "artifact_a", 200)
    artifact_b = _build_artifact(2, "artifact_b", 300)

    disk = Disk(
        id=1,
        name="disk_a",
        total_capacity_bytes=1_000,
        free_space_bytes=500,
        health_score=0.8,
        artifacts=[artifact_a, artifact_b],
    )

    assert disk.artifacts == [artifact_a, artifact_b]


def test_disk_raises_when_artifact_list_contains_duplicate_artifact_objects() -> None:
    artifact_a = _build_artifact(1, "artifact_a", 200)

    with pytest.raises(ValueError, match="Disk artifacts must not contain duplicates."):
        Disk(
            id=1,
            name="disk_a",
            total_capacity_bytes=1_000,
            free_space_bytes=800,
            health_score=0.8,
            artifacts=[artifact_a, artifact_a],
        )


def test_disk_raises_when_artifact_list_contains_duplicate_artifact_ids() -> None:
    artifact_a_v1 = _build_artifact(1, "artifact_a", 200)
    artifact_a_v2 = _build_artifact(1, "artifact_a_duplicate", 300)

    with pytest.raises(ValueError, match="Disk artifacts must not contain duplicates."):
        Disk(
            id=1,
            name="disk_a",
            total_capacity_bytes=1_000,
            free_space_bytes=500,
            health_score=0.8,
            artifacts=[artifact_a_v1, artifact_a_v2],
        )


def test_disk_raises_when_artifact_does_not_fit_in_available_used_space_budget() -> None:
    artifact_a = _build_artifact(1, "artifact_a", 200)
    artifact_b = _build_artifact(2, "artifact_b", 400)

    with pytest.raises(
        ValueError,
        match="Disk artifacts exceed the allowed used space.",
    ):
        Disk(
            id=1,
            name="disk_a",
            total_capacity_bytes=1_000,
            free_space_bytes=500,
            health_score=0.8,
            artifacts=[artifact_a, artifact_b],
        )


def test_disk_get_used_space_bytes_returns_sum_of_most_recent_artifact_version_sizes() -> None:
    artifact_a = _build_artifact(1, "artifact_a", 200)
    artifact_b = _build_artifact(2, "artifact_b", 300)

    disk = Disk(
        id=1,
        name="disk_a",
        total_capacity_bytes=1_000,
        free_space_bytes=500,
        health_score=0.8,
        artifacts=[artifact_a, artifact_b],
    )

    assert disk.get_used_space_bytes() == 500


def test_disk_can_store_size_returns_true_when_size_fits_remaining_free_space() -> None:
    artifact_a = _build_artifact(1, "artifact_a", 200)
    artifact_b = _build_artifact(2, "artifact_b", 300)

    disk = Disk(
        id=1,
        name="disk_a",
        total_capacity_bytes=1_000,
        free_space_bytes=500,
        health_score=0.8,
        artifacts=[artifact_a, artifact_b],
    )

    assert disk.can_store_size(500) is True


def test_disk_can_store_size_returns_false_when_size_exceeds_remaining_free_space() -> None:
    artifact_a = _build_artifact(1, "artifact_a", 200)
    artifact_b = _build_artifact(2, "artifact_b", 300)

    disk = Disk(
        id=1,
        name="disk_a",
        total_capacity_bytes=1_000,
        free_space_bytes=500,
        health_score=0.8,
        artifacts=[artifact_a, artifact_b],
    )

    assert disk.can_store_size(501) is False


def test_disk_uses_most_recent_artifact_version_size_when_calculating_used_space() -> None:
    artifact = Artifact(
        id=1,
        name="artifact_a",
        priority_score=100,
        desired_copy_count=2,
        artifact_type="zip",
    )
    artifact.add_version(
        ArtifactVersion(
            id=1,
            artifact_id=1,
            created_at=datetime(2026, 4, 15, 10, 30, 0),
            size_bytes=200,
            version_label="v1",
            checksum="checksum-v1",
        )
    )
    artifact.add_version(
        ArtifactVersion(
            id=2,
            artifact_id=1,
            created_at=datetime(2026, 4, 16, 10, 30, 0),
            size_bytes=350,
            version_label="v2",
            checksum="checksum-v2",
        )
    )

    disk = Disk(
        id=1,
        name="disk_a",
        total_capacity_bytes=1_000,
        free_space_bytes=650,
        health_score=0.8,
        artifacts=[artifact],
    )

    assert disk.get_used_space_bytes() == 350


def test_disk_raises_when_artifact_without_versions_is_passed_in_artifacts_list() -> None:
    artifact_without_versions = Artifact(
        id=1,
        name="artifact_a",
        priority_score=100,
        desired_copy_count=2,
        artifact_type="zip",
    )

    with pytest.raises(
        ValueError,
        match="Disk artifacts must have a most recent version.",
    ):
        Disk(
            id=1,
            name="disk_a",
            total_capacity_bytes=1_000,
            free_space_bytes=1_000,
            health_score=0.8,
            artifacts=[artifact_without_versions],
        )