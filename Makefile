PYTHON ?= python

.PHONY: build-data results

build-data:
	$(PYTHON) -m src.pygrowthstandards.data.main

results:
	PYTHONPATH=src $(PYTHON) scripts/generate_results.py
