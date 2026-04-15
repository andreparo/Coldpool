#!/usr/bin/env bash
set -euo pipefail

echo "=== UNIT TESTS ==="

export PYTHONPATH="apps/coldpool_server/src"

pytest tests/unit -v