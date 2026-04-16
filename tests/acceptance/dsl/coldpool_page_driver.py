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
        # TODO: replace this generic title check with the real page title/text once stabilized.
        expect(self.page).to_have_title("Coldpool")

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
        # TODO: these selectors must be aligned with the real React component labels/test ids.
        self.page.get_by_label("Artifact selection").select_option("new")
        self.page.get_by_label("Artifact name").fill(artifact_name)
        self.page.get_by_label("Priority score").fill(str(priority_score))
        self.page.get_by_label("Desired copy count").fill(str(desired_copy_count))
        self.page.get_by_label("Artifact type").fill(artifact_type)

        self.page.get_by_label("Version label").fill(version_label)
        self.page.get_by_label("Created at").fill(created_at)
        self.page.get_by_label("Size bytes").fill(str(size_bytes))
        self.page.get_by_label("Checksum").fill(checksum)

        self.page.get_by_role("button", name="Create artifact version").click()

    def expect_artifact_version_visible(
        self,
        artifact_name: str,
        version_label: str,
    ) -> None:
        """Check that the created artifact/version appears in the list."""
        expect(self.page.get_by_text(artifact_name)).to_be_visible()
        expect(self.page.get_by_text(version_label)).to_be_visible()
        # TODO: make this stricter by targeting the exact display card once the UI structure is stable.