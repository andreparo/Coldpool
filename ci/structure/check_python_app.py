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


def collect_python_package_errors(package_root: Path) -> list[str]:
    errors: list[str] = []

    for current_dir, _, files in os.walk(package_root):
        current_path = Path(current_dir)

        python_files = [
            file_name
            for file_name in files
            if file_name.endswith(".py")
        ]

        if not python_files:
            continue

        init_path = current_path / "__init__.py"
        if not init_path.is_file():
            errors.append(
                f"Python package directory contains .py files but is missing __init__.py: {current_path}"
            )

    return errors


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 ci/structure/check_python_app.py <app_path>")
        sys.exit(2)

    app_path = Path(sys.argv[1]).resolve()
    app_name = app_path.name
    src_dir = app_path / "src"
    package_dir = src_dir / app_name

    if not app_path.exists():
        fail(f"Python app path is missing: {app_path}")
    ok(f"Python app path exists: {app_path}")

    if not app_path.is_dir():
        fail(f"Python app path is not a directory: {app_path}")
    ok(f"Python app path is a directory: {app_path}")

    pyproject_path = app_path / "pyproject.toml"
    if not pyproject_path.exists():
        fail(f"pyproject.toml is missing: {pyproject_path}")
    ok(f"pyproject.toml exists: {pyproject_path}")

    if not pyproject_path.is_file():
        fail(f"pyproject.toml is not a regular file: {pyproject_path}")
    ok(f"pyproject.toml is a regular file: {pyproject_path}")

    if not src_dir.exists():
        fail(f"src directory is missing: {src_dir}")
    ok(f"src directory exists: {src_dir}")

    if not src_dir.is_dir():
        fail(f"src path is not a directory: {src_dir}")
    ok(f"src path is a directory: {src_dir}")

    if not package_dir.exists():
        fail(f"Main package directory is missing: {package_dir}")
    ok(f"Main package directory exists: {package_dir}")

    if not package_dir.is_dir():
        fail(f"Main package path is not a directory: {package_dir}")
    ok(f"Main package path is a directory: {package_dir}")

    init_path = package_dir / "__init__.py"
    if not init_path.exists():
        fail(f"Main package __init__.py is missing: {init_path}")
    ok(f"Main package __init__.py exists: {init_path}")

    if not init_path.is_file():
        fail(f"Main package __init__.py is not a regular file: {init_path}")
    ok(f"Main package __init__.py is a regular file: {init_path}")

    main_module_path = package_dir / "main.py"
    if not main_module_path.exists():
        fail(f"Main package main.py is missing: {main_module_path}")
    ok(f"Main package main.py exists: {main_module_path}")

    if not main_module_path.is_file():
        fail(f"Main package main.py is not a regular file: {main_module_path}")
    ok(f"Main package main.py is a regular file: {main_module_path}")

    dunder_main_path = package_dir / "__main__.py"
    if not dunder_main_path.exists():
        fail(f"Main package __main__.py is missing: {dunder_main_path}")
    ok(f"Main package __main__.py exists: {dunder_main_path}")

    if not dunder_main_path.is_file():
        fail(f"Main package __main__.py is not a regular file: {dunder_main_path}")
    ok(f"Main package __main__.py is a regular file: {dunder_main_path}")

    package_errors = collect_python_package_errors(package_dir)
    if package_errors:
        print()
        for error in package_errors:
            print(f"[FAIL] {error}")
        print()
        print(f"Python app structure check failed with {len(package_errors)} package error(s).")
        sys.exit(1)

    print("Python app structure check passed.")


if __name__ == "__main__":
    main()