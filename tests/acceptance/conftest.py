# pylint: disable=redefined-outer-name
from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from playwright.sync_api import Browser, Page, sync_playwright

from tests.acceptance.dsl.coldpool_page_driver import ColdpoolPageDriver


@pytest.fixture(scope="session")
def base_url() -> str:
    """Return the base URL of the running Coldpool server."""
    return os.environ.get("COLDPOOL_ACCEPTANCE_BASE_URL", "http://127.0.0.1:18080")


@pytest.fixture(scope="session")
def browser() -> Iterator[Browser]:
    """Create one browser for the whole acceptance test session."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture()
def page(browser: Browser) -> Iterator[Page]:
    """Create a fresh page for each acceptance test."""
    page = browser.new_page()
    yield page
    page.close()


@pytest.fixture()
def coldpool_page_driver(page: Page, base_url: str) -> ColdpoolPageDriver:
    """Create the Coldpool page driver used by acceptance tests."""
    return ColdpoolPageDriver(
        page=page,
        base_url=base_url,
    )