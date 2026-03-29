#!/usr/bin/env sh
set -e

PYTHON_BIN="${PYTHON_BIN:-/usr/local/bin/python3}"

"$PYTHON_BIN" -m pytest --cov=. --cov-report=term-missing -q
