# Makefile for web-transaction-monitor

.PHONY: help install test lint type-check format docker-up docker-down docker-logs clean cleanup-screenshots

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies with Poetry"
	@echo "  make test          - Run unit tests"
	@echo "  make lint          - Run code linting"
	@echo "  make type-check    - Run type checking with mypy"
	@echo "  make format        - Format code with ruff"
	@echo "  make docker-up     - Start Docker stack"
	@echo "  make docker-down   - Stop Docker stack"
	@echo "  make docker-logs   - View Docker logs"
	@echo "  make clean         - Clean cache and temp files"
	@echo "  make cleanup-screenshots - Delete old screenshots (7 days)"
	@echo "  make cleanup-screenshots-dry - Preview screenshot cleanup"

install:
	poetry install
	poetry run playwright install chromium

test:
	poetry run pytest -v --cov=. --cov-report=term-missing

test-fast:
	poetry run pytest -v

lint:
	poetry run ruff check .

lint-fix:
	poetry run ruff check --fix .

type-check:
	poetry run mypy main.py monitor_base.py runners/

format:
	poetry run ruff format .

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f web-monitor-app

docker-restart:
	docker-compose restart web-monitor-app

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -f .coverage

cleanup-screenshots:
	python cleanup_screenshots.py --days 7

cleanup-screenshots-dry:
	python cleanup_screenshots.py --days 7 --dry-run

all: lint type-check test
