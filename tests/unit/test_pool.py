from __future__ import annotations

from datetime import datetime

import pytest

from coldpool_server.artifact.artifact import Artifact
from coldpool_server.artifact.artifact_copy import ArtifactCopy
from coldpool_server.artifact.artifact_version import ArtifactVersion
from coldpool_server.disk.disk import Disk
from coldpool_server.pool.pool import Pool


def _build_disk(
    disk_id: int,
    name: str,
    total_capacity_bytes: int,
    health_score: float = 0.8,
    state: str = "offline",
) -> Disk:
    return Disk(
        id=disk_id,
        name=name,
        total_capacity_bytes=total_capacity_bytes,
        health_score=health_score,
        state=state,
        copies=[],
    )


def _build_artifact(
    artifact_id: int,
    name: str,
) -> Artifact:
    return Artifact(
        id=artifact_id,
        name=name,
        priority_score=100,
        desired_copy_count=2,
        artifact_type="zip",
    )


def _build_version(
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
) -> ArtifactCopy:
    return ArtifactCopy(
        id=copy_id,
        artifact_version=artifact_version,
        copy_index=copy_index,
        disk=disk,
        disk_path=f"/mnt/{disk.name}/copy_{copy_id}.bin",
        is_present=True,
        status="verified",
    )


def test_pool_is_created_with_valid_disks() -> None:
    disk_a = _build_disk(
        disk_id=1,
        name="disk_a",
        total_capacity_bytes=1_000,
    )
    disk_b = _build_disk(
        disk_id=2,
        name="disk_b",
        total_capacity_bytes=2_000,
    )

    pool = Pool(disks=[disk_a, disk_b])

    assert pool.disks == [disk_a, disk_b]


def test_pool_get_total_capacity_bytes_returns_sum_of_disk_capacities() -> None:
    disk_a = _build_disk(
        disk_id=1,
        name="disk_a",
        total_capacity_bytes=1_000,
    )
    disk_b = _build_disk(
        disk_id=2,
        name="disk_b",
        total_capacity_bytes=2_000,
    )

    pool = Pool(disks=[disk_a, disk_b])

    assert pool.get_total_capacity_bytes() == 3_000


def test_pool_get_total_used_space_bytes_returns_sum_of_disk_used_space() -> None:
    disk_a = _build_disk(1, "disk_a", 1_000)
    disk_b = _build_disk(2, "disk_b", 2_000)

    artifact_a = _build_artifact(1, "artifact_a")
    artifact_b = _build_artifact(2, "artifact_b")
    artifact_c = _build_artifact(3, "artifact_c")

    version_a = _build_version(1, artifact_a, 200)
    version_b = _build_version(2, artifact_b, 300)
    version_c = _build_version(3, artifact_c, 400)

    disk_a.add_copy(_build_copy(1, version_a, 1, disk_a))
    disk_a.add_copy(_build_copy(2, version_b, 1, disk_a))
    disk_b.add_copy(_build_copy(3, version_c, 1, disk_b))

    pool = Pool(disks=[disk_a, disk_b])

    assert pool.get_total_used_space_bytes() == 900


def test_pool_get_total_free_space_bytes_returns_sum_of_disk_free_space() -> None:
    disk_a = _build_disk(1, "disk_a", 1_000)
    disk_b = _build_disk(2, "disk_b", 2_000)

    artifact_a = _build_artifact(1, "artifact_a")
    artifact_b = _build_artifact(2, "artifact_b")
    artifact_c = _build_artifact(3, "artifact_c")

    version_a = _build_version(1, artifact_a, 200)
    version_b = _build_version(2, artifact_b, 300)
    version_c = _build_version(3, artifact_c, 400)

    disk_a.add_copy(_build_copy(1, version_a, 1, disk_a))
    disk_a.add_copy(_build_copy(2, version_b, 1, disk_a))
    disk_b.add_copy(_build_copy(3, version_c, 1, disk_b))

    pool = Pool(disks=[disk_a, disk_b])

    assert pool.get_total_free_space_bytes() == 2_100


def test_pool_raises_when_disk_ids_are_duplicated() -> None:
    disk_a = _build_disk(1, "disk_a", 1_000)
    disk_b = _build_disk(1, "disk_b", 2_000)

    with pytest.raises(ValueError, match="Pool disks must not contain duplicate ids."):
        Pool(disks=[disk_a, disk_b])


def test_pool_raises_when_disk_names_are_duplicated() -> None:
    disk_a = _build_disk(1, "disk_a", 1_000)
    disk_b = _build_disk(2, "disk_a", 2_000)

    with pytest.raises(
        ValueError,
        match="Pool disks must not contain duplicate names.",
    ):
        Pool(disks=[disk_a, disk_b])


def test_pool_returns_zero_totals_when_empty() -> None:
    pool = Pool(disks=[])

    assert pool.get_total_capacity_bytes() == 0
    assert pool.get_total_used_space_bytes() == 0
    assert pool.get_total_free_space_bytes() == 0