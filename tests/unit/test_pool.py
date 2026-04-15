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


def _attach_copy_to_version_and_disk(
    copy_id: int,
    artifact_version: ArtifactVersion,
    copy_index: int,
    disk: Disk,
) -> ArtifactCopy:
    artifact_copy = _build_copy(
        copy_id=copy_id,
        artifact_version=artifact_version,
        copy_index=copy_index,
        disk=disk,
    )
    artifact_version.add_copy(artifact_copy)
    disk.add_copy(artifact_copy)
    return artifact_copy


def test_pool_is_created_with_valid_disks_and_artifacts() -> None:
    disk_a = _build_disk(1, "disk_a", 1_000)
    disk_b = _build_disk(2, "disk_b", 2_000)

    artifact_a = _build_artifact(1, "artifact_a")
    artifact_b = _build_artifact(2, "artifact_b")

    version_a = _build_version(1, artifact_a, 200)
    version_b = _build_version(2, artifact_b, 300)

    _attach_copy_to_version_and_disk(1, version_a, 1, disk_a)
    _attach_copy_to_version_and_disk(2, version_b, 1, disk_b)

    pool = Pool(
        disks=[disk_a, disk_b],
        artifacts=[artifact_a, artifact_b],
    )

    assert pool.disks == [disk_a, disk_b]
    assert pool.artifacts == [artifact_a, artifact_b]


def test_pool_get_total_capacity_bytes_returns_sum_of_disk_capacities() -> None:
    disk_a = _build_disk(1, "disk_a", 1_000)
    disk_b = _build_disk(2, "disk_b", 2_000)

    pool = Pool(
        disks=[disk_a, disk_b],
        artifacts=[],
    )

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

    _attach_copy_to_version_and_disk(1, version_a, 1, disk_a)
    _attach_copy_to_version_and_disk(2, version_b, 1, disk_a)
    _attach_copy_to_version_and_disk(3, version_c, 1, disk_b)

    pool = Pool(
        disks=[disk_a, disk_b],
        artifacts=[artifact_a, artifact_b, artifact_c],
    )

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

    _attach_copy_to_version_and_disk(1, version_a, 1, disk_a)
    _attach_copy_to_version_and_disk(2, version_b, 1, disk_a)
    _attach_copy_to_version_and_disk(3, version_c, 1, disk_b)

    pool = Pool(
        disks=[disk_a, disk_b],
        artifacts=[artifact_a, artifact_b, artifact_c],
    )

    assert pool.get_total_free_space_bytes() == 2_100


def test_pool_raises_when_disk_ids_are_duplicated() -> None:
    disk_a = _build_disk(1, "disk_a", 1_000)
    disk_b = _build_disk(1, "disk_b", 2_000)

    with pytest.raises(ValueError, match="duplicate ids"):
        Pool(
            disks=[disk_a, disk_b],
            artifacts=[],
        )


def test_pool_raises_when_disk_names_are_duplicated() -> None:
    disk_a = _build_disk(1, "disk_a", 1_000)
    disk_b = _build_disk(2, "disk_a", 2_000)

    with pytest.raises(ValueError, match="duplicate names"):
        Pool(
            disks=[disk_a, disk_b],
            artifacts=[],
        )


def test_pool_raises_when_artifact_ids_are_duplicated() -> None:
    artifact_a = _build_artifact(1, "artifact_a")
    artifact_b = _build_artifact(1, "artifact_b")

    with pytest.raises(ValueError, match="duplicate artifact ids"):
        Pool(
            disks=[],
            artifacts=[artifact_a, artifact_b],
        )


def test_pool_raises_when_artifact_copy_points_to_disk_not_in_pool() -> None:
    disk_in_pool = _build_disk(1, "disk_a", 1_000)
    disk_out_of_pool = _build_disk(2, "disk_b", 2_000)

    artifact = _build_artifact(1, "artifact_a")
    version = _build_version(1, artifact, 200)

    artifact_copy = _build_copy(
        copy_id=1,
        artifact_version=version,
        copy_index=1,
        disk=disk_out_of_pool,
    )
    version.add_copy(artifact_copy)
    disk_out_of_pool.add_copy(artifact_copy)

    with pytest.raises(ValueError, match="copy.*disk.*not in pool"):
        Pool(
            disks=[disk_in_pool],
            artifacts=[artifact],
        )


def test_pool_raises_when_artifact_copy_is_not_present_in_its_disk_copy_list() -> None:
    disk = _build_disk(1, "disk_a", 1_000)
    artifact = _build_artifact(1, "artifact_a")
    version = _build_version(1, artifact, 200)

    artifact_copy = _build_copy(
        copy_id=1,
        artifact_version=version,
        copy_index=1,
        disk=disk,
    )
    version.add_copy(artifact_copy)

    with pytest.raises(ValueError, match="copy.*missing.*disk"):
        Pool(
            disks=[disk],
            artifacts=[artifact],
        )


def test_pool_raises_when_disk_contains_copy_from_artifact_not_in_pool() -> None:
    disk = _build_disk(1, "disk_a", 1_000)

    artifact_in_pool = _build_artifact(1, "artifact_a")
    artifact_not_in_pool = _build_artifact(2, "artifact_b")

    version_not_in_pool = _build_version(2, artifact_not_in_pool, 200)
    artifact_copy = _build_copy(
        copy_id=1,
        artifact_version=version_not_in_pool,
        copy_index=1,
        disk=disk,
    )
    version_not_in_pool.add_copy(artifact_copy)
    disk.add_copy(artifact_copy)

    with pytest.raises(ValueError, match="disk.*copy.*artifact.*not in pool"):
        Pool(
            disks=[disk],
            artifacts=[artifact_in_pool],
        )


def test_pool_raises_when_disk_contains_copy_missing_from_its_version_copy_list() -> None:
    disk = _build_disk(1, "disk_a", 1_000)
    artifact = _build_artifact(1, "artifact_a")
    version = _build_version(1, artifact, 200)

    artifact_copy = _build_copy(
        copy_id=1,
        artifact_version=version,
        copy_index=1,
        disk=disk,
    )
    disk.add_copy(artifact_copy)

    with pytest.raises(ValueError, match="disk.*copy.*missing.*version"):
        Pool(
            disks=[disk],
            artifacts=[artifact],
        )


def test_pool_accepts_multiple_artifacts_versions_and_copies_when_graph_is_consistent() -> None:
    disk_a = _build_disk(1, "disk_a", 2_000)
    disk_b = _build_disk(2, "disk_b", 2_000)

    artifact_a = _build_artifact(1, "artifact_a")
    artifact_b = _build_artifact(2, "artifact_b")

    version_a1 = _build_version(1, artifact_a, 150)
    version_a2 = _build_version(2, artifact_a, 250)
    version_b1 = _build_version(3, artifact_b, 300)

    copy_a1 = _attach_copy_to_version_and_disk(1, version_a1, 1, disk_a)
    copy_a2 = _attach_copy_to_version_and_disk(2, version_a2, 1, disk_b)
    copy_b1 = _attach_copy_to_version_and_disk(3, version_b1, 1, disk_a)

    pool = Pool(
        disks=[disk_a, disk_b],
        artifacts=[artifact_a, artifact_b],
    )

    assert pool.disks == [disk_a, disk_b]
    assert pool.artifacts == [artifact_a, artifact_b]
    assert copy_a1 in disk_a.get_copies()
    assert copy_a2 in disk_b.get_copies()
    assert copy_b1 in disk_a.get_copies()
    assert copy_a1 in version_a1.get_copies()
    assert copy_a2 in version_a2.get_copies()
    assert copy_b1 in version_b1.get_copies()


def test_pool_returns_zero_totals_when_empty() -> None:
    pool = Pool(
        disks=[],
        artifacts=[],
    )

    assert pool.get_total_capacity_bytes() == 0
    assert pool.get_total_used_space_bytes() == 0
    assert pool.get_total_free_space_bytes() == 0