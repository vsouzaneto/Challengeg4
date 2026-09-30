# Developer Onboarding - vitor-balbino-martins

> Welcome to the team! This guide gets you from zero to running in ~10 minutes.

## Prerequisites

- Python 3.11+
- Git
- Docker (recommended for services)

## Quick Start

### 1. Clone & Enter Project

```bash
git clone <repo-url>
cd vitor-balbino-martins
```

### 2. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Copy environment config
cp .env.example .env
# Edit .env with your local values
```

### 3. Setup Database

```bash
# Start PostgreSQL (or use your own)
docker run -d --name postgres -e POSTGRES_PASSWORD=pass -p 5432:5432 postgres:15

# Edit .env with your DATABASE_URL, then run migrations
python manage.py migrate -m "initial"
```

### Run the API

```bash
python manage.py run
# or
uvicorn main:app --reload
```

Open: http://127.0.0.1:8000/docs

## Project Structure (Quick Reference)

| Where to look | What lives there |
|---|---|
| `api/v1/endpoints/` | HTTP handlers - route, call service |
| `services/` | Business logic - validate, orchestrate |
| `repositories/` | DB queries - no logic, just data |
| `models/` | SQLAlchemy table definitions |
| `schemas/` | Pydantic input/output shapes |
| `core/config.py` | All settings from .env |
| `core/exceptions.py` | Custom exception classes |

## Common Tasks

### Add a new resource (CRUD)

```bash
python manage.py add-resource invoice
python manage.py add-resource invoice --auth --events --paginated
```

This creates: model, schema, repository, service, and endpoint automatically.

### Add business logic without a database table

```bash
python manage.py add-service pricing --inject order_service,product_service
```

### Add an external API client

```bash
py-manager add-proxy stripe --url https://api.stripe.com --token-type bearer
py-manager add-proxy sendgrid --url https://api.sendgrid.com --token-type x-api-key
```

### Add a scheduled task

```bash
py-manager add-schedule daily_report --cron "0 9 * * 1-5"
py-manager add-schedule hourly_sync --cron "0 * * * *" --backend apscheduler
```

### Add a queue worker

```bash
py-manager add-queue send_email
py-manager add-queue process_payment
```

### Run tests

```bash
pytest tests/ -v
pytest tests/unit/ -v --cov=services
```

### Lint & format

```bash
ruff check .
ruff format .
```

## Environment Variables Reference

See `.env.example` for all available variables.
Never commit `.env` - it is in `.gitignore`.

## Getting Help

- Read `ARCHITECTURE.md` for system design
- Read `API_GUIDE.md` for step-by-step feature guides
- Check `DECISIONS.md` for architecture decisions and their rationale
