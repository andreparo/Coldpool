from __future__ import annotations

from tests.acceptance.dsl.coldpool_page_driver import ColdpoolPageDriver


def test_create_artifact_and_see_it_in_list(
    coldpool_page_driver: ColdpoolPageDriver,
) -> None:
    """A user can create a new artifact and then see it in the list."""
    coldpool_page_driver.open()

    coldpool_page_driver.create_new_artifact_and_first_version(
        artifact_name="photos_backup_acceptance",
        priority_score=100,
        desired_copy_count=2,
        artifact_type="zip",
        version_label="v1",
        created_at="2026-04-16T10:30:00",
        size_bytes=1024,
        checksum="abc123acceptance",
    )

    coldpool_page_driver.expect_artifact_version_visible(
        artifact_name="photos_backup_acceptance",
        version_label="v1",
    )