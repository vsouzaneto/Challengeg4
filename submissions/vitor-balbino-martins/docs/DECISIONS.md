# Architecture Decision Records - vitor-balbino-martins

> ADRs document important architectural decisions made during the project's evolution.
> Add a new entry whenever you make a significant architectural choice.

---

## Template

```markdown
## ADR-XXX: [Short title]

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-XXX

### Context
What is the issue or situation that motivates this decision?

### Decision
What was decided?

### Consequences
What are the trade-offs, positive and negative outcomes?
```

---

## ADR-001: Clean Architecture with Layered Separation

**Date:** 2026-09-30
**Status:** Accepted

### Context
We need a codebase structure that scales with team size and makes it easy for new
developers to understand where to add features without reading the entire codebase.

### Decision
Adopted Clean Architecture with strict inward-only dependency flow:
`API -> Services -> Repositories -> Models -> Infrastructure`

### Consequences
- (+) Easy to test each layer independently
- (+) Infrastructure (DB, cache) can be swapped without touching business logic
- (+) New developers know exactly where code belongs
- (-) More boilerplate for simple CRUD operations
- (-) Requires discipline - linters should enforce import boundaries

---

## ADR-002: Async-first with SQLAlchemy + asyncpg

**Date:** 2026-09-30
**Status:** Accepted

### Context
FastAPI is async-native. Blocking DB calls inside async routes block the event loop.

### Decision
Use `sqlalchemy[asyncio]` with `asyncpg` (PostgreSQL) or `aiosqlite` (SQLite).
All repository methods are `async def`.

### Consequences
- (+) No event loop blocking
- (+) Higher throughput for I/O-bound workloads
- (-) Cannot use synchronous SQLAlchemy patterns (lazy loading is restricted)
- (-) Requires `await` everywhere in the repository/service layer

---

## ADR-003: Pydantic v2 for all schemas

**Date:** 2026-09-30
**Status:** Accepted

### Context
Need typed, validated request/response shapes that integrate with FastAPI's OpenAPI
generation.

### Decision
All DTOs use Pydantic v2 `BaseModel`. `model_config = ConfigDict(from_attributes=True)`
enables ORM mode for serializing SQLAlchemy models.

### Consequences
- (+) Automatic OpenAPI docs
- (+) Runtime validation with clear error messages
- (+) Type-safe service layer inputs
- (-) Pydantic v2 has breaking changes from v1 - check docs when upgrading

---

## ADR-004: [Your next decision here]

**Date:** YYYY-MM-DD
**Status:** Proposed

### Context


### Decision


### Consequences

