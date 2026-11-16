.PHONY: install test lint frontend-build run generate

install:
	pip install -e '.[dev]'

test:
	pytest -q

lint:
	ruff check src tests

frontend-build:
	cd frontend && npm install --no-audit --no-fund && npm run build

run:
	uvicorn payinsight.api.app:app --reload

generate:
	python scripts/generate_data.py --count 1000
