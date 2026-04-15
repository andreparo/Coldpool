#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    sys.exit(1)


def ok(message: str) -> None:
    print(f"[ OK ] {message}")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 ci/structure/check_readme.py <repo_root>")
        sys.exit(2)

    repo_root = Path(sys.argv[1]).resolve()
    readme_path = repo_root / "README.md"

    if not repo_root.is_dir():
        fail(f"Repository root is not a directory: {repo_root}")

    if not readme_path.exists():
        fail(f"README.md is missing at top level: {readme_path}")
    ok(f"README.md exists at top level: {readme_path}")

    if not readme_path.is_file():
        fail(f"README.md is not a regular file: {readme_path}")
    ok(f"README.md is a regular file: {readme_path}")

    try:
        content = readme_path.read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"README.md is not readable: {readme_path} ({exc})")

    if not content.strip():
        fail(f"README.md is empty: {readme_path}")
    ok(f"README.md is not empty: {readme_path}")

    print("README check passed.")


if __name__ == "__main__":
    main()