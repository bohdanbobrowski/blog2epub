.SILENT: format
.PHONY: format

format:
	python -m ruff format .
	python -m ruff check . --fix