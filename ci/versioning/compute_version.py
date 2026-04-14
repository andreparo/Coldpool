# ci/versioning/compute_version.py
#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


CHANGELOG_PATH = Path("CHANGELOG.md")
VERSION_HEADER_RE = re.compile(r"^## v(\d+)\.(\d+)\.(\d+) - (.+)$", re.MULTILINE)


def run_git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def get_short_sha() -> str:
    return run_git("rev-parse", "--short", "HEAD")


def get_commit_subject() -> str:
    return run_git("log", "-1", "--pretty=%s").strip()


def get_commit_count() -> int:
    return int(run_git("rev-list", "--count", "HEAD"))


def read_changelog() -> str:
    if not CHANGELOG_PATH.exists():
        raise FileNotFoundError("CHANGELOG.md not found")
    return CHANGELOG_PATH.read_text(encoding="utf-8")


def parse_version_headers(changelog_text: str) -> list[tuple[int, int, int, str]]:
    headers: list[tuple[int, int, int, str]] = []
    for match in VERSION_HEADER_RE.finditer(changelog_text):
        major, minor, patch, title = match.groups()
        headers.append((int(major), int(minor), int(patch), title.strip()))
    return headers


def latest_stable_version(changelog_text: str) -> tuple[int, int, int]:
    headers = parse_version_headers(changelog_text)

    # No stable versions in changelog yet:
    # treat v0.0.0 as the existing internal baseline.
    if not headers:
        return (0, 0, 0)

    major, minor, patch, _title = headers[0]
    return major, minor, patch


def top_entry_matches_commit(changelog_text: str, commit_subject: str) -> tuple[bool, str | None]:
    headers = parse_version_headers(changelog_text)
    if not headers:
        return False, None

    major, minor, patch, title = headers[0]
    version = f"v{major}.{minor}.{patch}"
    return title == commit_subject, version


def main() -> int:
    try:
        changelog_text = read_changelog()
        commit_subject = get_commit_subject()
        short_sha = get_short_sha()

        is_stable_commit, stable_version = top_entry_matches_commit(changelog_text, commit_subject)

        if is_stable_commit and stable_version is not None:
            version = stable_version
            is_stable = "true"
        else:
            major, minor, patch = latest_stable_version(changelog_text)
            alpha_n = get_commit_count()
            version = f"v{major}.{minor}.{patch + 1}-alpha.{alpha_n}"
            is_stable = "false"

        print(f"VERSION={version}")
        print(f"SHORT_SHA={short_sha}")
        print(f"IS_STABLE={is_stable}")
        return 0

    except Exception as exc:
        print(f"ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())