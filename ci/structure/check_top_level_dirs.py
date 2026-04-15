#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


REQUIRED_TOP_LEVEL_DIRS = [
    "apps",
    "tests",
    "docs",
    "ci",
]


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    sys.exit(1)


def ok(message: str) -> None:
    print(f"[ OK ] {message}")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 ci/structure/check_top_level_dirs.py <repo_root>")
        sys.exit(2)

    repo_root = Path(sys.argv[1]).resolve()

    if not repo_root.is_dir():
        fail(f"Repository root is not a directory: {repo_root}")

    errors: list[str] = []

    for dir_name in REQUIRED_TOP_LEVEL_DIRS:
        path = repo_root / dir_name

        if not path.exists():
            message = f"Required top-level directory is missing: {path}"
            print(f"[FAIL] {message}")
            errors.append(message)
            continue

        print(f"[ OK ] Required top-level directory exists: {path}")

        if not path.is_dir():
            message = f"Required top-level path is not a directory: {path}"
            print(f"[FAIL] {message}")
            errors.append(message)
            continue

        print(f"[ OK ] Required top-level path is a directory: {path}")

    if errors:
        print()
        print(f"Top-level directory check failed with {len(errors)} error(s).")
        for index, error in enumerate(errors, start=1):
            print(f"  {index}. {error}")
        sys.exit(1)

    print("Top-level directory check passed.")


if __name__ == "__main__":
    main()