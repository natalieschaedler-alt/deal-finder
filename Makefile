PYTHON ?= /usr/local/bin/python3

.PHONY: check-quick check-full

check-quick:
	$(PYTHON) -m pytest -q tests/test_evaluate.py tests/test_advanced_evaluate.py tests/test_filters.py tests/test_main_integration.py

check-full:
	$(PYTHON) -m pytest --cov=. --cov-report=term-missing -q
