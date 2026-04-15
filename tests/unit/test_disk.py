from __future__ import annotations

import pytest

from coldpool_server.disk.disk import Disk


def test_disk_is_created_with_valid_data() -> None:
    disk = Disk(
        id=1,
        name="disk_a",
        total_capacity_bytes=1_000,
        free_space_bytes=400,
        health_score=0.8,
        location="office",
        state="offline",
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
        )


def test_disk_raises_when_name_is_blank() -> None:
    with pytest.raises(ValueError, match="Disk name must not be empty."):
        Disk(
            id=1,
            name="   ",
            total_capacity_bytes=1_000,
            free_space_bytes=400,
            health_score=0.8,
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
        )

        assert disk.state == state