.PHONY: run dev test lint format migrate migration

run:
	uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

dev:
	uvicorn main:app --reload --port 8000

test:
	pytest tests/ -v --cov=. --cov-report=term-missing

lint:
	ruff check .

format:
	ruff format .

migrate:
	alembic upgrade head

migration:
	alembic revision --autogenerate -m "$(msg)"
