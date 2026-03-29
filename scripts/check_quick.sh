#!/usr/bin/env sh
set -e

PYTHON_BIN="${PYTHON_BIN:-/usr/local/bin/python3}"

"$PYTHON_BIN" -m pytest -q \
  tests/test_evaluate.py \
  tests/test_advanced_evaluate.py \
  tests/test_filters.py \
  tests/test_main_integration.py
