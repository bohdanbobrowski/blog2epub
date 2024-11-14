.SILENT: format, check, test, integration_test, unit_test, unit_coverage, unit_coverage_html, clear_win
.PHONY: format, check, test, integration_test, unit_test, unit_coverage, unit_coverage_html, clear_win

format:
	poetry run ruff format .
	poetry run ruff check . --fix

check:
	poetry run mypy .

test:
	poetry run pytest tests -s

integration_test:
	poetry run pytest tests/integration -s

unit_test:
	poetry run pytest tests/unit -s

unit_coverage:
	poetry run pytest --cov=blog2epub ./tests/unit

unit_coverage_html:
	poetry run pytest --cov=blog2epub --cov-report=html ./tests/unit

clear_win:
	del *.epub
	echo y|rd /s tests_cache
