#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    sys.exit(1)


def ok(message: str) -> None:
    print(f"[ OK ] {message}")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 ci/structure/check_license.py <repo_root>")
        sys.exit(2)

    repo_root = Path(sys.argv[1]).resolve()
    license_path = repo_root / "LICENSE"

    if not repo_root.is_dir():
        fail(f"Repository root is not a directory: {repo_root}")

    if not license_path.exists():
        fail(f"LICENSE is missing at top level: {license_path}")
    ok(f"LICENSE exists at top level: {license_path}")

    if not license_path.is_file():
        fail(f"LICENSE is not a regular file: {license_path}")
    ok(f"LICENSE is a regular file: {license_path}")

    if not os.access(license_path, os.R_OK):
        fail(f"LICENSE is not readable: {license_path}")
    ok(f"LICENSE is readable: {license_path}")

    print("LICENSE check passed.")


if __name__ == "__main__":
    main()