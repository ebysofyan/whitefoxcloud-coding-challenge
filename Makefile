.PHONY: help setup db db-init dev test test-unit test-integration coverage lint format fix precommit deploy deploy-prod remove clean

help:
	@echo "Available targets:"
	@echo "  setup        Install dependencies and pre-commit hooks"
	@echo "  db            Start DynamoDB Local (docker compose)"
	@echo "  db-init       Create DynamoDB table in local instance"
	@echo "  dev           Start FastAPI development server"
	@echo "  test          Run all tests (unit + integration)"
	@echo "  test-unit     Run unit tests only"
	@echo "  test-integration  Run integration tests only"
	@echo "  coverage      Run tests with 90% coverage gate"
	@echo "  lint          Run ruff linter"
	@echo "  format        Run ruff formatter"
	@echo "  fix           Auto-fix lint issues and format"
	@echo "  precommit     Run pre-commit hooks on all files"
	@echo "  deploy        Deploy to AWS (dev stage)"
	@echo "  deploy-prod   Deploy to AWS (production stage)"
	@echo "  remove        Remove deployed AWS resources"
	@echo "  clean         Remove local artifacts and caches"

setup:
	uv sync --all-extras
	uv run pre-commit install

db:
	docker compose up -d dynamodb-local
	@echo "DynamoDB Local started at http://localhost:18749"
	@echo "Set DYNAMODB_ENDPOINT=http://localhost:18749 in your .env file"

db-init:
	uv run python scripts/init_db.py

dev:
	uv run fastapi dev src/main.py --port 9876

test:
	uv run pytest -v

test-unit:
	uv run pytest tests/ -v --ignore=tests/integration

test-integration:
	uv run pytest tests/integration/ -v

coverage:
	uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=90 -v

lint:
	uv run ruff check .

format:
	uv run ruff format .

fix:
	uv run ruff check . --fix
	uv run ruff format .

precommit:
	uv run pre-commit run --all-files

deps:
	@echo "Installing Linux-compatible Python dependencies..."
	rm -rf deps
	pip install -r requirements.txt --target deps --platform manylinux2014_x86_64 --only-binary=:all: --python-version 3.14 --upgrade
	rm -rf deps/boto3* deps/botocore* deps/s3transfer* deps/jmespath* deps/urllib3* deps/python_dateutil* deps/six* deps/dateutil deps/bin deps/__pycache__

deploy: deps
	serverless deploy

deploy-prod:
	serverless deploy --stage production

remove:
	serverless remove

clean:
	rm -rf .venv .ruff_cache .pytest_cache __pycache__ .serverless .coverage htmlcov
