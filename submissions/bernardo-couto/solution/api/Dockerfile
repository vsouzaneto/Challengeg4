# syntax=docker/dockerfile:1.7
# Build context must be solution/ (the shared contracts package lives one level up from api/).

FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY shared/lead_scorer_contracts /app/shared/lead_scorer_contracts
COPY api/pyproject.toml api/uv.lock api/README.md api/.python-version /app/api/
COPY api/src /app/api/src
WORKDIR /app/api
RUN uv sync --frozen --no-dev --no-editable

FROM python:3.12-slim AS runtime
RUN groupadd --system app && useradd --system --gid app --home /app app \
    && apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder --chown=app:app /app/api/.venv /app/api/.venv
COPY --chown=app:app api/src /app/api/src
ENV PATH="/app/api/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    LEAD_SCORER_SCORES_DIR=/app/data/gold/scores \
    LEAD_SCORER_MODELS_DIR=/app/models \
    LEAD_SCORER_FEEDBACK_DIR=/app/data/feedback
USER app
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/api/v1/health || exit 1
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
