#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


OPTIONAL_APP_DIRS = [
    "public",
    "configs",
    "deployment",
    "dist",
    "node_modules",
]

OPTIONAL_APP_FILES = [
    "src/App.css",
]


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    sys.exit(1)


def ok(message: str) -> None:
    print(f"[ OK ] {message}")


def collect_component_structure_errors(components_root: Path) -> list[str]:
    errors: list[str] = []

    if not components_root.is_dir():
        return errors

    for current_dir in components_root.rglob("*"):
        if not current_dir.is_dir():
            continue

        children = list(current_dir.iterdir())
        if not children:
            continue

        child_dirs = [child for child in children if child.is_dir()]
        child_tsx_files = [child for child in children if child.is_file() and child.suffix == ".tsx"]

        # Grouping folder: contains only directories, no local tsx files
        if child_dirs and not child_tsx_files:
            continue

        folder_name = current_dir.name
        expected_component_file = current_dir / f"{folder_name}.tsx"
        expected_types_file = current_dir / "types.ts"
        expected_css_file = current_dir / f"{folder_name}.module.css"

        # If a folder is not a grouping folder, treat it as a component folder.
        if not expected_component_file.is_file():
            errors.append(
                f"Component folder is missing required component file: {expected_component_file}"
            )

        if not expected_types_file.is_file():
            errors.append(
                f"Component folder is missing required types file: {expected_types_file}"
            )

        if not expected_css_file.is_file():
            errors.append(
                f"Component folder is missing required css module file: {expected_css_file}"
            )

    return errors


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 ci/structure/check_typescript_react_app.py <app_path>")
        sys.exit(2)

    app_path = Path(sys.argv[1]).resolve()

    if not app_path.exists():
        fail(f"React app path is missing: {app_path}")
    ok(f"React app path exists: {app_path}")

    if not app_path.is_dir():
        fail(f"React app path is not a directory: {app_path}")
    ok(f"React app path is a directory: {app_path}")

    mandatory_files = [
        app_path / "package.json",
        app_path / "tsconfig.json",
        app_path / "tsconfig.app.json",
        app_path / "tsconfig.node.json",
        app_path / "vite.config.ts",
        app_path / "eslint.config.js",
        app_path / "index.html",
        app_path / "src" / "main.tsx",
        app_path / "src" / "App.tsx",
        app_path / "src" / "index.css",
    ]

    mandatory_dirs = [
        app_path / "src",
        app_path / "src" / "assets",
        app_path / "src" / "components",
        app_path / "src" / "pages",
        app_path / "src" / "services",
        app_path / "src" / "services" / "api",
        app_path / "src" / "types",
        app_path / "src" / "utils",
        app_path / "src" / "hooks",
    ]

    for path in mandatory_files:
        if not path.exists():
            fail(f"Mandatory file is missing: {path}")
        ok(f"Mandatory file exists: {path}")

        if not path.is_file():
            fail(f"Mandatory file path is not a regular file: {path}")
        ok(f"Mandatory file path is a regular file: {path}")

    for path in mandatory_dirs:
        if not path.exists():
            fail(f"Mandatory directory is missing: {path}")
        ok(f"Mandatory directory exists: {path}")

        if not path.is_dir():
            fail(f"Mandatory directory path is not a directory: {path}")
        ok(f"Mandatory directory path is a directory: {path}")

    for relative_dir in OPTIONAL_APP_DIRS:
        path = app_path / relative_dir
        if not path.exists():
            print(f"[ OK ] Optional directory is absent: {path}")
            continue

        print(f"[ OK ] Optional directory exists: {path}")

        if not path.is_dir():
            fail(f"Optional path exists but is not a directory: {path}")
        ok(f"Optional path is a directory: {path}")

    for relative_file in OPTIONAL_APP_FILES:
        path = app_path / relative_file
        if not path.exists():
            print(f"[ OK ] Optional file is absent: {path}")
            continue

        print(f"[ OK ] Optional file exists: {path}")

        if not path.is_file():
            fail(f"Optional path exists but is not a regular file: {path}")
        ok(f"Optional path is a regular file: {path}")

    component_errors = collect_component_structure_errors(app_path / "src" / "components")
    if component_errors:
        print()
        for error in component_errors:
            print(f"[FAIL] {error}")
        print()
        print(f"React app structure check failed with {len(component_errors)} component error(s).")
        sys.exit(1)

    print("React app structure check passed.")


if __name__ == "__main__":
    main()