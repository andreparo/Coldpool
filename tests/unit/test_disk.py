from __future__ import annotations

from datetime import datetime

import pytest

from coldpool_server.artifact.artifact import Artifact
from coldpool_server.artifact.artifact_copy import ArtifactCopy
from coldpool_server.artifact.artifact_version import ArtifactVersion
from coldpool_server.disk.disk import Disk


def _build_empty_disk(
    disk_id: int = 1,
    name: str = "disk_a",
    total_capacity_bytes: int = 1_000,
    health_score: float = 0.8,
    location: str | None = None,
    state: str = "offline",
) -> Disk:
    return Disk(
        id=disk_id,
        name=name,
        total_capacity_bytes=total_capacity_bytes,
        health_score=health_score,
        location=location,
        state=state,
        copies=[],
    )


def _build_artifact(
    artifact_id: int,
    name: str,
    priority_score: int = 100,
    desired_copy_count: int = 2,
) -> Artifact:
    return Artifact(
        id=artifact_id,
        name=name,
        priority_score=priority_score,
        desired_copy_count=desired_copy_count,
        artifact_type="zip",
    )


def _build_artifact_version(
    version_id: int,
    artifact: Artifact,
    size_bytes: int,
    created_at: datetime | None = None,
) -> ArtifactVersion:
    version = ArtifactVersion(
        id=version_id,
        artifact=artifact,
        created_at=created_at or datetime(2026, 4, 15, 10, 30, 0),
        size_bytes=size_bytes,
        version_label=f"v{version_id}",
        checksum=f"checksum-{version_id}",
        copies=[],
    )
    artifact.add_version(version)
    return version


def _build_copy(
    copy_id: int,
    artifact_version: ArtifactVersion,
    copy_index: int,
    disk: Disk,
    disk_path: str | None = None,
) -> ArtifactCopy:
    return ArtifactCopy(
        id=copy_id,
        artifact_version=artifact_version,
        copy_index=copy_index,
        disk=disk,
        disk_path=disk_path or f"/mnt/{disk.name}/copy_{copy_id}.bin",
        is_present=True,
        status="verified",
    )


def test_disk_is_created_with_valid_data() -> None:
    disk = _build_empty_disk(
        disk_id=1,
        name="disk_a",
        total_capacity_bytes=1_000,
        health_score=0.8,
        location="office",
        state="offline",
    )

    assert disk.id == 1
    assert disk.name == "disk_a"
    assert disk.total_capacity_bytes == 1_000
    assert disk.free_space_bytes == 1_000
    assert disk.health_score == 0.8
    assert disk.location == "office"
    assert disk.state == "offline"
    assert disk.get_copies() == []


def test_disk_raises_when_id_is_not_positive() -> None:
    with pytest.raises(ValueError, match="Disk id must be > 0."):
        _build_empty_disk(disk_id=0)


def test_disk_raises_when_name_is_blank() -> None:
    with pytest.raises(ValueError, match="Disk name must not be empty."):
        _build_empty_disk(name="   ")


def test_disk_raises_when_total_capacity_bytes_is_negative() -> None:
    with pytest.raises(
        ValueError,
        match="Disk total_capacity_bytes must be >= 0.",
    ):
        _build_empty_disk(total_capacity_bytes=-1)


def test_disk_raises_when_health_score_is_below_zero() -> None:
    with pytest.raises(
        ValueError,
        match="Disk health_score must be between 0.0 and 1.0.",
    ):
        _build_empty_disk(health_score=-0.1)


def test_disk_raises_when_health_score_is_above_one() -> None:
    with pytest.raises(
        ValueError,
        match="Disk health_score must be between 0.0 and 1.0.",
    ):
        _build_empty_disk(health_score=1.1)


def test_disk_raises_when_location_is_blank() -> None:
    with pytest.raises(
        ValueError,
        match="Disk location must not be empty if provided.",
    ):
        _build_empty_disk(location="   ")


def test_disk_raises_when_state_is_invalid() -> None:
    with pytest.raises(
        ValueError,
        match="Disk state must be one of: online, offline, offsite, retired.",
    ):
        _build_empty_disk(state="broken")


def test_disk_allows_valid_states() -> None:
    valid_states = ["online", "offline", "offsite", "retired"]

    for state in valid_states:
        disk = _build_empty_disk(state=state)

        assert disk.state == state


def test_disk_add_copy_saves_copy_in_disk() -> None:
    disk = _build_empty_disk()
    artifact = _build_artifact(1, "artifact_a")
    version = _build_artifact_version(1, artifact, 200)
    copy = _build_copy(1, version, 1, disk)

    disk.add_copy(copy)

    saved_copies = disk.get_copies()

    assert len(saved_copies) == 1
    assert saved_copies[0] == copy
    assert saved_copies[0].disk == disk


def test_disk_remove_copy_removes_previously_added_copy() -> None:
    disk = _build_empty_disk()
    artifact = _build_artifact(1, "artifact_a")
    version = _build_artifact_version(1, artifact, 200)
    copy = _build_copy(1, version, 1, disk)

    disk.add_copy(copy)
    disk.remove_copy(copy_id=1)

    assert disk.get_copies() == []


def test_disk_add_copy_raises_when_copy_disk_does_not_match() -> None:
    disk = _build_empty_disk(disk_id=1, name="disk_a")
    other_disk = _build_empty_disk(disk_id=2, name="disk_b")
    artifact = _build_artifact(1, "artifact_a")
    version = _build_artifact_version(1, artifact, 200)
    copy = _build_copy(1, version, 1, other_disk)

    with pytest.raises(
        ValueError,
        match="ArtifactCopy disk does not match Disk.",
    ):
        disk.add_copy(copy)


def test_disk_add_copy_raises_when_copy_id_already_exists() -> None:
    disk = _build_empty_disk()
    artifact_a = _build_artifact(1, "artifact_a")
    artifact_b = _build_artifact(2, "artifact_b")
    version_a = _build_artifact_version(1, artifact_a, 200)
    version_b = _build_artifact_version(2, artifact_b, 300)

    first_copy = _build_copy(1, version_a, 1, disk)
    duplicate_id_copy = _build_copy(1, version_b, 1, disk)

    disk.add_copy(first_copy)

    with pytest.raises(ValueError, match="already exists"):
        disk.add_copy(duplicate_id_copy)


def test_disk_add_copy_raises_when_same_artifact_version_and_copy_index_are_duplicated() -> None:
    disk = _build_empty_disk()
    artifact = _build_artifact(1, "artifact_a")
    version = _build_artifact_version(1, artifact, 200)

    first_copy = _build_copy(1, version, 1, disk)
    duplicate_slot_copy = _build_copy(2, version, 1, disk)

    disk.add_copy(first_copy)

    with pytest.raises(ValueError, match="copy_index=1 already exists"):
        disk.add_copy(duplicate_slot_copy)


def test_disk_add_copy_raises_when_same_artifact_version_has_two_copies_on_same_disk() -> None:
    disk = _build_empty_disk()
    artifact = _build_artifact(1, "artifact_a")
    version = _build_artifact_version(1, artifact, 200)

    first_copy = _build_copy(1, version, 1, disk)
    second_copy = _build_copy(2, version, 2, disk)

    disk.add_copy(first_copy)

    with pytest.raises(
        ValueError,
        match="Disk must not contain more than one copy of the same artifact version.",
    ):
        disk.add_copy(second_copy)


def test_disk_add_copy_raises_when_copies_exceed_total_capacity() -> None:
    disk = _build_empty_disk(total_capacity_bytes=500)
    artifact_a = _build_artifact(1, "artifact_a")
    artifact_b = _build_artifact(2, "artifact_b")
    version_a = _build_artifact_version(1, artifact_a, 300)
    version_b = _build_artifact_version(2, artifact_b, 250)

    copy_a = _build_copy(1, version_a, 1, disk)
    copy_b = _build_copy(2, version_b, 1, disk)

    disk.add_copy(copy_a)

    with pytest.raises(
        ValueError,
        match="Disk copies exceed total capacity.",
    ):
        disk.add_copy(copy_b)


def test_disk_get_used_space_bytes_returns_sum_of_copy_sizes() -> None:
    disk = _build_empty_disk()
    artifact_a = _build_artifact(1, "artifact_a")
    artifact_b = _build_artifact(2, "artifact_b")
    version_a = _build_artifact_version(1, artifact_a, 200)
    version_b = _build_artifact_version(2, artifact_b, 300)

    copy_a = _build_copy(1, version_a, 1, disk)
    copy_b = _build_copy(2, version_b, 1, disk)

    disk.add_copy(copy_a)
    disk.add_copy(copy_b)

    assert disk.get_used_space_bytes() == 500


def test_disk_free_space_bytes_is_derived_from_total_capacity_and_copies() -> None:
    disk = _build_empty_disk()
    artifact_a = _build_artifact(1, "artifact_a")
    artifact_b = _build_artifact(2, "artifact_b")
    version_a = _build_artifact_version(1, artifact_a, 200)
    version_b = _build_artifact_version(2, artifact_b, 300)

    copy_a = _build_copy(1, version_a, 1, disk)
    copy_b = _build_copy(2, version_b, 1, disk)

    disk.add_copy(copy_a)
    disk.add_copy(copy_b)

    assert disk.free_space_bytes == 500


def test_disk_can_store_size_returns_true_when_size_fits_remaining_free_space() -> None:
    disk = _build_empty_disk()
    artifact_a = _build_artifact(1, "artifact_a")
    artifact_b = _build_artifact(2, "artifact_b")
    version_a = _build_artifact_version(1, artifact_a, 200)
    version_b = _build_artifact_version(2, artifact_b, 300)

    copy_a = _build_copy(1, version_a, 1, disk)
    copy_b = _build_copy(2, version_b, 1, disk)

    disk.add_copy(copy_a)
    disk.add_copy(copy_b)

    assert disk.can_store_size(500) is True


def test_disk_can_store_size_returns_false_when_size_exceeds_remaining_free_space() -> None:
    disk = _build_empty_disk()
    artifact_a = _build_artifact(1, "artifact_a")
    artifact_b = _build_artifact(2, "artifact_b")
    version_a = _build_artifact_version(1, artifact_a, 200)
    version_b = _build_artifact_version(2, artifact_b, 300)

    copy_a = _build_copy(1, version_a, 1, disk)
    copy_b = _build_copy(2, version_b, 1, disk)

    disk.add_copy(copy_a)
    disk.add_copy(copy_b)

    assert disk.can_store_size(501) is False


def test_disk_uses_artifact_version_size_when_calculating_used_space() -> None:
    disk = _build_empty_disk()

    artifact = _build_artifact(1, "artifact_a")
    older_version = _build_artifact_version(
        1,
        artifact,
        200,
        created_at=datetime(2026, 4, 15, 10, 30, 0),
    )
    newer_version = _build_artifact_version(
        2,
        artifact,
        350,
        created_at=datetime(2026, 4, 16, 10, 30, 0),
    )

    older_copy = _build_copy(1, older_version, 1, disk)
    newer_copy = _build_copy(2, newer_version, 1, disk)

    disk.add_copy(older_copy)
    disk.add_copy(newer_copy)

    assert disk.get_used_space_bytes() == 550
    assert disk.free_space_bytes == 450


def test_disk_remove_copy_raises_when_copy_does_not_exist() -> None:
    disk = _build_empty_disk()

    with pytest.raises(ValueError, match="was not found"):
        disk.remove_copy(copy_id=999)