.PHONY: install test lint run
install:
	pip install -e '.[dev]'
test:
	pytest -q
lint:
	ruff check payinsight tests
run:
	uvicorn payinsight.api.app:app --reload
