"""Read-only data access over the pipeline artifacts.

* Discovers ``as_of=YYYY-MM-DD`` partitions under ``settings.scores_dir``.
* Loads one partition with pyarrow, normalises ``reasons`` (list-of-struct **or** JSON string)
  and validates every row against ``ScoredDeal``. Invalid rows fail fast with a clear error.
* Caches validated snapshots in memory (the parquet is immutable per ``as_of``).
* Exposes pure filter/sort helpers used by the routers. Nothing here computes a score.
"""

from __future__ import annotations

import json
import logging
import re
import threading
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Literal

import pyarrow.parquet as pq
from pydantic import ValidationError

from api.errors import (
    ArtifactsInvalidError,
    ArtifactsMissingError,
    AsOfNotFoundError,
    DealNotFoundError,
)
from api.schemas import ScoredDeal
from api.settings import ZOMBIE_DAYS, settings

log = logging.getLogger("api.repository")

_PARTITION_RE = re.compile(r"^as_of=(\d{4}-\d{2}-\d{2})$")

SORTABLE_FIELDS: frozenset[str] = frozenset(
    {
        "priority_score",
        "expected_value",
        "sales_price",
        "p_win",
        "urgency",
        "days_in_engaging",
        "tier",
        "sales_agent",
        "manager",
        "regional_office",
        "product",
        "account",
        "opportunity_id",
        "deal_stage",
    }
)
DEFAULT_SORT = "-priority_score"

# "work": alive deals the seller acts on (<= ZOMBIE_DAYS or no timeline); "confirm": stalled
# deals (> ZOMBIE_DAYS) whose job is to be confirmed or closed in the CRM (revops-review 3c).
Queue = Literal["work", "confirm"]


def in_queue(deal: ScoredDeal, queue: Queue) -> bool:
    days = deal.days_in_engaging
    stalled = days is not None and days > ZOMBIE_DAYS
    return stalled if queue == "confirm" else not stalled


# --------------------------------------------------------------------------- discovery


def list_as_of_partitions(scores_dir: Path) -> list[date]:
    """Return the ``as_of`` dates of non-empty partition folders, ascending."""
    if not scores_dir.is_dir():
        return []
    found: list[date] = []
    for child in scores_dir.iterdir():
        match = _PARTITION_RE.match(child.name)
        if not match or not child.is_dir():
            continue
        if not any(child.glob("*.parquet")):
            continue
        try:
            found.append(date.fromisoformat(match.group(1)))
        except ValueError:
            continue
    return sorted(found)


def partition_path(scores_dir: Path, as_of: date) -> Path:
    return scores_dir / f"as_of={as_of.isoformat()}"


def resolve_latest_model_dir(pointer: Path) -> Path | None:
    """``models/latest`` may be a directory (or symlink) or a one-line pointer to ``models/<v>``."""
    if pointer.is_dir():
        return pointer
    if pointer.is_file():
        value = pointer.read_text(encoding="utf-8").strip()
        if not value:
            return None
        candidate = pointer.parent / value
        return candidate if candidate.is_dir() else None
    return None


def read_model_version(pointer: Path) -> str | None:
    """Model version named by ``models/latest`` (pointer text, symlink target or metrics.json)."""
    if pointer.is_file():
        value = pointer.read_text(encoding="utf-8").strip()
        return value or None
    model_dir = resolve_latest_model_dir(pointer)
    if model_dir is None:
        return None
    metrics = model_dir / "metrics.json"
    if metrics.is_file():
        try:
            data = json.loads(metrics.read_text(encoding="utf-8"))
            version = data.get("model_version") if isinstance(data, dict) else None
            if isinstance(version, str) and version:
                return version
        except json.JSONDecodeError:
            pass
    resolved = model_dir.resolve()
    return resolved.name if resolved.name != "latest" else None


# --------------------------------------------------------------------------- loading


def _coerce_reasons(value: Any) -> Any:
    """Accept list[struct] (pyarrow -> list[dict]), a JSON string, or a list of JSON strings."""
    if value is None:
        return value
    if isinstance(value, str):
        return json.loads(value)
    if isinstance(value, (list, tuple)):
        return [json.loads(item) if isinstance(item, str) else item for item in value]
    return value


def _coerce_row(row: dict[str, Any], as_of: date) -> dict[str, Any]:
    row = dict(row)
    row["reasons"] = _coerce_reasons(row.get("reasons"))
    stamp = row.get("as_of")
    if stamp is None:
        row["as_of"] = as_of  # Spark drops the partition column from the files
    elif isinstance(stamp, datetime):
        row["as_of"] = stamp.date()
    return row


def load_partition(scores_dir: Path, as_of: date) -> list[ScoredDeal]:
    """Read every parquet file of one partition and validate each row. Raises ``ApiError``."""
    path = partition_path(scores_dir, as_of)
    if not path.is_dir() or not any(path.glob("*.parquet")):
        available = [d.isoformat() for d in list_as_of_partitions(scores_dir)]
        raise AsOfNotFoundError(as_of.isoformat(), available)
    try:
        table = pq.read_table(str(path))
    except Exception as exc:  # pyarrow raises several unrelated exception types
        raise ArtifactsInvalidError(f"Falha ao ler {path}: {exc}") from exc

    deals: list[ScoredDeal] = []
    problems: list[Any] = []
    for index, raw in enumerate(table.to_pylist()):
        try:
            deals.append(ScoredDeal.model_validate(_coerce_row(raw, as_of)))
        except (ValidationError, json.JSONDecodeError, TypeError) as exc:
            if len(problems) < 5:
                problems.append(
                    {
                        "row": index,
                        "opportunity_id": raw.get("opportunity_id"),
                        "error": str(exc).splitlines()[0:6],
                    }
                )
    if problems:
        raise ArtifactsInvalidError(
            f"Partição as_of={as_of.isoformat()} tem linhas fora do contrato ScoredDeal "
            f"(mostrando até 5 de {len(problems)}+).",
            problems,
        )
    if not deals:
        raise ArtifactsInvalidError(f"Partição as_of={as_of.isoformat()} está vazia.")
    return deals


@dataclass(frozen=True)
class Snapshot:
    """One validated ``as_of`` partition held in memory."""

    as_of: date
    deals: list[ScoredDeal]
    by_id: dict[str, ScoredDeal] = field(default_factory=dict)

    @property
    def model_version(self) -> str:
        return self.deals[0].model_version if self.deals else "unknown"

    def get(self, opportunity_id: str) -> ScoredDeal:
        deal = self.by_id.get(opportunity_id)
        if deal is None:
            raise DealNotFoundError(opportunity_id, self.as_of.isoformat())
        return deal


class ScoresRepository:
    """Thread-safe, lazily-populated cache of snapshots keyed by ``as_of``."""

    def __init__(self) -> None:
        self._cache: dict[date, Snapshot] = {}
        self._lock = threading.Lock()

    @property
    def scores_dir(self) -> Path:
        return settings.scores_dir

    def reset(self) -> None:
        with self._lock:
            self._cache.clear()

    def available(self) -> list[date]:
        return list_as_of_partitions(self.scores_dir)

    def latest_as_of(self) -> date:
        partitions = self.available()
        if not partitions:
            raise ArtifactsMissingError()
        return partitions[-1]

    def snapshot(self, as_of: date | None = None) -> Snapshot:
        target = as_of or self.latest_as_of()
        with self._lock:
            cached = self._cache.get(target)
            if cached is not None:
                return cached
            deals = load_partition(self.scores_dir, target)
            snap = Snapshot(target, deals, {d.opportunity_id: d for d in deals})
            self._cache[target] = snap
            log.info("snapshot_loaded as_of=%s rows=%d", target.isoformat(), len(deals))
            return snap

    def warm_up(self) -> Snapshot | None:
        """Boot-time validation: load the latest partition, or return None when there is none."""
        if not self.available():
            log.warning("no_partitions scores_dir=%s", self.scores_dir)
            return None
        return self.snapshot()


repository = ScoresRepository()


# --------------------------------------------------------------------------- filter / sort


def filter_deals(
    deals: Iterable[ScoredDeal],
    *,
    sales_agent: str | None = None,
    manager: str | None = None,
    regional_office: str | None = None,
    deal_stage: str | None = None,
    tier: str | None = None,
    min_score: float | None = None,
    account_known: bool | None = None,
    queue: Queue | None = None,
    min_days_in_engaging: int | None = None,
    max_days_in_engaging: int | None = None,
) -> list[ScoredDeal]:
    def keep(d: ScoredDeal) -> bool:
        if queue is not None and not in_queue(d, queue):
            return False
        if min_days_in_engaging is not None and (
            d.days_in_engaging is None or d.days_in_engaging < min_days_in_engaging
        ):
            return False
        if max_days_in_engaging is not None and (
            d.days_in_engaging is None or d.days_in_engaging > max_days_in_engaging
        ):
            return False
        if sales_agent is not None and d.sales_agent != sales_agent:
            return False
        if manager is not None and d.manager != manager:
            return False
        if regional_office is not None and d.regional_office != regional_office:
            return False
        if deal_stage is not None and d.deal_stage != deal_stage:
            return False
        if tier is not None and d.tier != tier:
            return False
        if min_score is not None and d.priority_score < min_score:
            return False
        return not (account_known is not None and (d.account is not None) != account_known)

    return [d for d in deals if keep(d)]


def parse_sort(sort: str | None) -> list[tuple[str, bool]]:
    """``"-priority_score,sales_agent"`` -> ``[("priority_score", True), ("sales_agent", False)]``.

    Raises ``ValueError`` on unknown fields (routers turn it into a 422).
    """
    keys: list[tuple[str, bool]] = []
    for token in (sort or DEFAULT_SORT).split(","):
        token = token.strip()
        if not token:
            continue
        descending = token.startswith("-")
        name = token.lstrip("+-")
        if name not in SORTABLE_FIELDS:
            raise ValueError(
                f"Campo de ordenação inválido: {name!r}. Use um de: "
                + ", ".join(sorted(SORTABLE_FIELDS))
            )
        keys.append((name, descending))
    return keys or [("priority_score", True)]


def sort_deals(deals: list[ScoredDeal], keys: list[tuple[str, bool]]) -> list[ScoredDeal]:
    """Stable multi-key sort; ``None`` values always go last, ties break by opportunity_id."""
    result = sorted(deals, key=lambda d: d.opportunity_id)
    for name, descending in reversed(keys):
        result.sort(key=_key_for(name), reverse=descending)
        if descending:
            # keep None last even in descending order
            present = [d for d in result if getattr(d, name) is not None]
            missing = [d for d in result if getattr(d, name) is None]
            result = present + missing
    return result


def _key_for(name: str) -> Callable[[ScoredDeal], tuple[int, Any]]:
    def key(d: ScoredDeal) -> tuple[int, Any]:
        value = getattr(d, name)
        return (1, "") if value is None else (0, value)

    return key
