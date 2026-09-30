# API Development Guide - vitor-balbino-martins

> Step-by-step recipes for common development tasks.

---

## 1. Adding a New Resource (Full CRUD)

```bash
python manage.py add-resource <name> [options]

# Examples
python manage.py add-resource product
python manage.py add-resource order --auth --events
python manage.py add-resource payment --proxy
```

**What gets created:**
- `models/<name>.py` - SQLAlchemy model
- `schemas/<name>.py` - Pydantic schemas (Create, Update, Response)
- `repositories/<name>_repository.py` - DB queries
- `services/<name>_service.py` - business logic
- `api/v1/endpoints/<name>.py` - HTTP routes (GET list, GET one, POST, PUT, DELETE)

**After running:** the endpoint is auto-registered in `api/v1/__init__.py`.

### Customizing the Model

Open `models/<name>.py` and add columns:

```python
class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id:    Mapped[int]        = mapped_column(Integer, primary_key=True)
    name:  Mapped[str]        = mapped_column(String(255), nullable=False, index=True)
    price: Mapped[float]      = mapped_column(Float, nullable=False)       # add this
    sku:   Mapped[str | None] = mapped_column(String(50), unique=True)     # and this
```

Then create a migration:

```bash
python manage.py migrate -m "add product price and sku"
```

---

## 2. Adding an External API Client (Proxy)

```bash
py-manager add-proxy <name> --url <base-url> --token-type <type>

# Token types: bearer | x-api-key | x-api-token | basic | custom
py-manager add-proxy stripe   --url https://api.stripe.com   --token-type bearer
py-manager add-proxy sendgrid --url https://api.sendgrid.com --token-type x-api-key
py-manager add-proxy legacy   --url https://old.api.local    --token-type custom --token-header X-Auth
```

**What gets created:**
- `infrastructure/http/base_client.py` - shared httpx base class (once)
- `infrastructure/http/<name>_client.py` - typed client for this API
- `.env` - `<NAME>_API_TOKEN=` entry added automatically

### Using a client in a service

```python
from infrastructure.http.stripe_client import stripe_client

class PaymentService:
    async def charge(self, amount: int) -> dict:
        return await stripe_client.post("/charges", json={"amount": amount})
```

---

## 3. Adding Scheduled Tasks

### Celery Beat (recommended for production)

```bash
py-manager add-schedule daily_report --cron "0 9 * * 1-5" --backend celery
```

Edit `infrastructure/tasks/schedules/daily_report.py` and implement the task body.

Then register the beat schedule in `celery_app.py`:

```python
from celery.schedules import crontab
celery_app.conf.beat_schedule = {
    "daily_report": {
        "task":     "schedules.daily_report",
        "schedule": crontab(minute="0", hour="9", day_of_week="1-5"),
    },
}
```

Run:
```bash
celery -A infrastructure.tasks.celery_app worker -l info
celery -A infrastructure.tasks.celery_app beat   -l info
```

### APScheduler (simpler, in-process)

```bash
py-manager add-schedule hourly_sync --cron "0 * * * *" --backend apscheduler
```

Register in `main.py` lifespan:

```python
from infrastructure.tasks.scheduler import scheduler
from infrastructure.tasks.schedules.hourly_sync import register_hourly_sync

@asynccontextmanager
async def lifespan(app):
    scheduler.start()
    register_hourly_sync()
    yield
    scheduler.shutdown()
```

---

## 4. Adding Queue Workers (Async Jobs)

```bash
py-manager add-queue send_email
```

**Dispatch a job from anywhere:**

```python
from infrastructure.tasks.workers.send_email_task import send_email_task

# Fire and forget
send_email_task.delay({"to": "user@example.com", "subject": "Hello"})

# With options
send_email_task.apply_async(
    args=[{"to": "user@example.com"}],
    queue="send_email",
    countdown=5,   # delay 5 seconds
    expires=3600,  # discard if not run in 1 hour
)
```

---

## 5. Adding a Middleware

```bash
python manage.py add-middleware rate_limit
```

Then register in `main.py`:

```python
from middlewares.rate_limit import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware)
```

---

## 6. Database Migrations

```bash
# Generate + apply in one step
python manage.py migrate -m "describe the change"

# Generate only
python manage.py migrate --only-gen -m "draft"

# Raw alembic
alembic downgrade -1
alembic history
```

---

## 7. Authentication

Auth strategy is set at `init` time. The `get_current_user` dependency is available in:
`api/v1/dependencies/auth.py`

**Protect a specific route:**

```python
from api.v1.dependencies.auth import get_current_user

@router.get("/secret")
async def secret_route(user: dict = Depends(get_current_user)):
    return {"user": user["id"]}
```

---

## 8. Domain Events

If `--with-events` was used:

```python
from infrastructure.events.bus import bus, DomainEvent

# Publish
await bus.publish(DomainEvent("order.placed", {"order_id": 42}))

# Subscribe (at startup or module level)
@bus.on("order.placed")
async def handle_order_placed(event: DomainEvent):
    print(event.payload)
```
