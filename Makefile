.SILENT: format, check, test, integration_test, unit_test, unit_coverage, unit_coverage_html, clear_win
.PHONY: format, check, test, integration_test, unit_test, unit_coverage, unit_coverage_html, clear_win

precommit: format check unit_test

format:
	ruff format .
	ruff check . --fix

check:
	mypy .

test:
	pytest tests

integration_test:
	pytest tests/integration

unit_test:
	pytest tests/unit

unit_coverage:
	pytest --cov=blog2epub ./tests/unit

unit_coverage_html:
	pytest --cov=blog2epub --cov-report=html ./tests/unit

clear_win:
	del /q *.epub
	rd /s /q tests_cache
