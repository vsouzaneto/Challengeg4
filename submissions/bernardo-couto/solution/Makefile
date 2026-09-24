# Entry points for the whole solution. Run from solution/.
SHELL := /bin/bash
AS_OF ?= 2017-12-31
JAVA_HOME ?= $(shell /usr/libexec/java_home -v 21 2>/dev/null || echo "$$JAVA_HOME")
export JAVA_HOME

.PHONY: help up down logs test lint pipeline docs openapi gen-api install

help: ## List targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

up: ## docker compose up (api :8000, web :5173, docs :8001)
	docker compose up --build -d
	@echo "web  http://localhost:5173 | api http://localhost:8000/docs | docs http://localhost:8001"

down: ## Stop and remove containers
	docker compose down

logs: ## Tail compose logs
	docker compose logs -f --tail=100

install: ## Install every project locally (uv + npm)
	cd shared/lead_scorer_contracts && uv sync
	cd pipeline && uv sync
	cd api && uv sync
	cd docs-site && uv sync
	cd web && npm install --no-audit --no-fund

test: ## Run all test suites
	cd shared/lead_scorer_contracts && uv run pytest -q
	cd pipeline && uv run pytest -q
	cd api && uv run pytest -q
	cd web && npm run test

lint: ## ruff + mypy (python) and eslint + prettier + tsc (web)
	cd pipeline && uv run ruff check . && uv run ruff format --check . && uv run mypy src tests
	cd api && uv run ruff check . && uv run ruff format --check . && uv run mypy src tests
	cd shared/lead_scorer_contracts && uv run ruff check . && uv run mypy src
	cd web && npm run lint && npm run typecheck

pipeline: ## build_features -> train -> score for AS_OF (needs JDK 17/21 or the pipeline profile)
	cd pipeline && uv run python -m lead_scorer.jobs build-features --as-of $(AS_OF)
	cd pipeline && uv run python -m lead_scorer.jobs train --as-of $(AS_OF)
	cd pipeline && uv run python -m lead_scorer.jobs score --as-of $(AS_OF)

openapi: ## Export openapi.json into the docs site
	cd api && uv run python -m api.export_openapi > ../docs-site/docs/api/openapi.json
	uvx openapi-spec-validator docs-site/docs/api/openapi.json

gen-api: openapi ## Generate TS types from the exported OpenAPI (no running API needed)
	cd web && OPENAPI_URL=../docs-site/docs/api/openapi.json npm run gen:api

docs: openapi ## Build the MkDocs site (strict)
	cd docs-site && uv run mkdocs build --strict
