.SILENT: format, check, test, integration_test, unit_test, unit_coverage, unit_coverage_html, clear_win
.PHONY: format, check, test, integration_test, unit_test, unit_coverage, unit_coverage_html, clear_win

precommit: clear_win format check test

format:
	ruff format .
	ruff check . --fix

check:
	mypy .

test:
	pytest tests -s

integration_test:
	pytest tests/integration -s

unit_test:
	pytest tests/unit -s

unit_coverage:
	pytest --cov=blog2epub ./tests/unit

unit_coverage_html:
	pytest --cov=blog2epub --cov-report=html ./tests/unit

clear_win:
	del *.epub
	echo y|rd /s tests_cache
