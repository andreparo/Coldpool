# ci/versioning/verify_changelog.py
#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import re
import subprocess
import sys
from pathlib import Path 


CHANGELOG_PATH = Path("CHANGELOG.md")
HEADER_RE = re.compile(r"^## v(\d+)\.(\d+)\.(\d+) - (.+)$", re.MULTILINE)
DATE_RE = re.compile(r"^\d{1,2} [A-Z][a-z]{2}\. \d{4}$")


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def run_git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def get_commit_subject() -> str:
    return run_git("log", "-1", "--pretty=%s").strip()


def read_lines() -> list[str]:
    if not CHANGELOG_PATH.exists():
        raise FileNotFoundError("CHANGELOG.md not found")
    return CHANGELOG_PATH.read_text(encoding="utf-8").splitlines()


def parse_headers(lines: list[str]) -> list[tuple[int, tuple[int, int, int], str]]:
    headers: list[tuple[int, tuple[int, int, int], str]] = []
    for idx, line in enumerate(lines):
        match = HEADER_RE.match(line)
        if match:
            major, minor, patch, title = match.groups()
            headers.append((idx, (int(major), int(minor), int(patch)), title.strip()))
    return headers


def expected_today_string() -> str:
    today = dt.date.today()
    month_map = {
        1: "Jan.",
        2: "Feb.",
        3: "Mar.",
        4: "Apr.",
        5: "May.",
        6: "Jun.",
        7: "Jul.",
        8: "Aug.",
        9: "Sep.",
        10: "Oct.",
        11: "Nov.",
        12: "Dec.",
    }
    return f"{today.day} {month_map[today.month]} {today.year}"


def ensure_file_header(lines: list[str]) -> None:
    if not lines:
        raise ValueError("CHANGELOG.md is empty")
    if lines[0] != "# Changelog":
        raise ValueError('CHANGELOG.md must start exactly with "# Changelog"')
    if len(lines) >= 2 and lines[1] != "":
        raise ValueError('There must be exactly one empty line after "# Changelog"')


def ensure_no_triple_empty_lines(lines: list[str]) -> None:
    empty_run = 0
    for line in lines:
        if line == "":
            empty_run += 1
            if empty_run >= 3:
                raise ValueError("CHANGELOG.md must not contain three empty lines in a row")
        else:
            empty_run = 0


def ensure_version_order(headers: list[tuple[int, tuple[int, int, int], str]]) -> None:
    versions = [version for _idx, version, _title in headers]
    for i in range(len(versions) - 1):
        if versions[i] <= versions[i + 1]:
            raise ValueError("Changelog versions must be ordered newest first")


def ensure_top_entry_date(lines: list[str], top_header_index: int) -> None:
    for idx in range(top_header_index + 1, len(lines)):
        line = lines[idx].strip()
        if not line:
            continue
        if not DATE_RE.match(line):
            raise ValueError(
                "The first meaningful line after the top version header must be a date like '3 Dec. 2025'"
            )
        expected = expected_today_string()
        if line != expected:
            raise ValueError(f"Top changelog date must be today's date: {expected}")
        return

    raise ValueError("Top version entry is missing its date line")


def ensure_top_entry_matches_commit(headers: list[tuple[int, tuple[int, int, int], str]]) -> None:
    if not headers:
        raise ValueError("CHANGELOG.md must contain at least one version entry")
    _idx, version, title = headers[0]
    commit_subject = get_commit_subject()
    if title != commit_subject:
        version_str = f"v{version[0]}.{version[1]}.{version[2]}"
        raise ValueError(
            f'Top changelog title for {version_str} must exactly match commit message. '
            f'Expected "{title}", got "{commit_subject}"'
        )


def main() -> int:
    try:
        lines = read_lines()
        ensure_file_header(lines)
        ensure_no_triple_empty_lines(lines)

        headers = parse_headers(lines)
        if not headers:
            raise ValueError("No version headers found in CHANGELOG.md")

        ensure_version_order(headers)
        top_header_index, _top_version, _top_title = headers[0]
        ensure_top_entry_date(lines, top_header_index)
        ensure_top_entry_matches_commit(headers)

        print("CHANGELOG_OK=true")
        return 0

    except Exception as exc:
        return fail(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())