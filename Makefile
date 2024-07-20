
.SILENT: format
.PHONY: format


format:
    ruff format .
    ruff check . --fix
