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

generate_keystore:
	keytool -genkey -v -keystore ~/.keystores/mykey.keystore -alias bobrowski_com_pl -keyalg RSA -keysize 2048 -validity 10000
	keytool -importkeystore -srckeystore /home/bohdan/.keystores/mykey.keystore -destkeystore /home/bohdan/.keystores/mykey.keystore -deststoretype pkcs12

build_android_debug:
	buildozer android debug

build_android_release:
