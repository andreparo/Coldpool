from __future__ import annotations

from playwright.sync_api import Page, expect


class ColdpoolPageDriver:
    """Small DSL/driver for the current single-page Coldpool UI."""

    def __init__(self, page: Page, base_url: str) -> None:
        """Store Playwright page and target base URL."""
        self.page = page
        self.base_url = base_url.rstrip("/")

    def open(self) -> None:
        """Open the Coldpool web page."""
        self.page.goto(f"{self.base_url}/")
        expect(self.page.get_by_test_id("page-title")).to_have_text("Coldpool")

    def create_new_artifact_and_first_version(
        self,
        artifact_name: str,
        priority_score: int,
        desired_copy_count: int,
        artifact_type: str,
        version_label: str,
        created_at: str,
        size_bytes: int,
        checksum: str,
    ) -> None:
        """Create a new artifact together with its first version."""
        self.page.get_by_test_id("artifact-mode-new").check()

        self.page.get_by_test_id("new-artifact-name-input").fill(artifact_name)
        self.page.get_by_test_id("new-artifact-priority-score-input").fill(
            str(priority_score)
        )
        self.page.get_by_test_id(
            "new-artifact-desired-copy-count-input"
        ).fill(str(desired_copy_count))
        self.page.get_by_test_id("new-artifact-type-input").fill(artifact_type)

        self.page.get_by_test_id("version-label-input").fill(version_label)
        self.page.get_by_test_id("created-at-input").fill(
            self._to_datetime_local_value(created_at)
        )
        self.page.get_by_test_id("size-bytes-input").fill(str(size_bytes))
        self.page.get_by_test_id("checksum-input").fill(checksum)

        self.page.get_by_test_id("create-artifact-version-button").click()

    def expect_artifact_version_visible(
        self,
        artifact_name: str,
        version_label: str,
    ) -> None:
        """Check that the created artifact/version appears in the list."""
        expect(self.page.get_by_test_id("artifact-version-list")).to_be_visible()
        expect(self.page.get_by_text(artifact_name)).to_be_visible()
        expect(self.page.get_by_text(f"Version {version_label}")).to_be_visible()

    @staticmethod
    def _to_datetime_local_value(value: str) -> str:
        """Convert ISO datetime strings to datetime-local input format."""
        normalized_value = value.strip()
        if normalized_value.endswith("Z"):
            normalized_value = normalized_value[:-1]
        return normalized_value[:16]