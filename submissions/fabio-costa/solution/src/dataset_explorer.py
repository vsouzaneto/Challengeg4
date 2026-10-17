from __future__ import annotations

from math import ceil
from pathlib import Path
from typing import Any

import pandas as pd


# -----------------------------------------------------------------------------
# READ-ONLY DATASET EXPLORER
# -----------------------------------------------------------------------------
class DatasetExplorer:
    """Read-only access to the original challenge datasets.

    The explorer never mutates source rows. Dataset 1 and Dataset 2 remain
    separate and are exposed according to their current project roles.
    """

    DATASET1_REQUIRED = {"Ticket ID", "Ticket Description", "Ticket Type"}
    DATASET2_REQUIRED = {"Document", "Topic_group"}
    DATASET1_FILTERS = ["Ticket Type", "Ticket Priority", "Ticket Channel", "Ticket Status"]
    DATASET2_FILTERS = ["Topic_group"]

    def __init__(self, raw_dir: Path):
        self.raw_dir = Path(raw_dir)

    def summary(self) -> dict[str, Any]:
        sources = self._sources()
        if not sources.get("dataset1") or not sources.get("dataset2"):
            return {
                "status": "awaiting_data",
                "message": "Both datasets must be available in data/raw/.",
            }

        d1 = pd.read_csv(sources["dataset1"])
        d2 = pd.read_csv(sources["dataset2"])

        customer_summary = self._customer_summary(d1)

        return {
            "status": "ready",
            "datasets": {
                "dataset1": self._dataset_summary(
                    "dataset1", sources["dataset1"], d1, self.DATASET1_FILTERS
                ),
                "dataset2": self._dataset_summary(
                    "dataset2", sources["dataset2"], d2, self.DATASET2_FILTERS
                ),
            },
            "customer_summary": customer_summary,
            "dataset_roles": {
                "dataset1": {
                    "unit": "ticket",
                    "relationship": "operational",
                    "has_customer_identity": True,
                    "has_ticket_status": True,
                    "note": "Each row represents an operational ticket and includes customer data.",
                },
                "dataset2": {
                    "unit": "labeled_ticket_text",
                    "relationship": "independent_training_corpus",
                    "has_customer_identity": False,
                    "has_ticket_status": False,
                    "note": "Each row is labeled ticket text from an independent corpus; there is no customer, status, or Ticket ID available for a relational link.",
                },
            },
        }

    # -------------------------------------------------------------------------
    # CUSTOMER EVIDENCE — DATASET 1
    # -------------------------------------------------------------------------
    @staticmethod
    def _customer_summary(df: pd.DataFrame) -> dict[str, Any]:
        if "Customer Email" not in df.columns:
            return {"status": "unavailable", "reason": "Customer Email is not available in Dataset 1."}

        emails = df["Customer Email"].dropna().astype(str).str.strip()
        emails = emails[emails.ne("")]
        counts = emails.value_counts()
        unique_customers = int(counts.size)
        multi_ticket_customers = int((counts > 1).sum())
        tickets_from_multi = int(counts[counts > 1].sum()) if multi_ticket_customers else 0
        total_tickets_with_email = int(counts.sum())
        unique_names = int(df["Customer Name"].nunique(dropna=True)) if "Customer Name" in df.columns else None

        return {
            "status": "ready",
            "identity_key": "Customer Email",
            "tickets_with_customer_email": total_tickets_with_email,
            "unique_customer_emails": unique_customers,
            "unique_customer_names": unique_names,
            "multi_ticket_customers": multi_ticket_customers,
            "multi_ticket_customer_pct": round((multi_ticket_customers / unique_customers * 100) if unique_customers else 0.0, 2),
            "tickets_from_multi_ticket_customers": tickets_from_multi,
            "tickets_from_multi_ticket_customers_pct": round((tickets_from_multi / total_tickets_with_email * 100) if total_tickets_with_email else 0.0, 2),
            "max_tickets_per_customer": int(counts.max()) if unique_customers else 0,
            "note": (
                "Customer Email is used as the observable customer identifier within Dataset 1. "
                "These customers cannot be linked to Dataset 2 because Dataset 2 contains no customer identifier."
            ),
        }

    # -------------------------------------------------------------------------
    # READ-ONLY ROW ACCESS
    # -------------------------------------------------------------------------
    def rows(
        self,
        dataset_id: str,
        page: int = 1,
        page_size: int = 25,
        query: str = "",
        filter_field: str = "",
        filter_value: str = "",
    ) -> dict[str, Any]:
        sources = self._sources()
        if dataset_id not in {"dataset1", "dataset2"}:
            return {"status": "error", "error": "invalid_dataset"}
        source = sources.get(dataset_id)
        if source is None:
            return {"status": "awaiting_data", "error": "dataset_not_found"}

        df = pd.read_csv(source)
        allowed_filters = self.DATASET1_FILTERS if dataset_id == "dataset1" else self.DATASET2_FILTERS

        query = (query or "").strip()
        if query:
            q = query.casefold()
            searchable = df.fillna("").astype(str)
            mask = searchable.apply(
                lambda column: column.str.casefold().str.contains(q, regex=False)
            ).any(axis=1)
            df = df[mask]

        filter_field = (filter_field or "").strip()
        filter_value = (filter_value or "").strip()
        if filter_field and filter_value:
            if filter_field not in allowed_filters or filter_field not in df.columns:
                return {"status": "error", "error": "invalid_filter"}
            df = df[df[filter_field].astype(str) == filter_value]

        page_size = max(10, min(int(page_size or 25), 100))
        total_rows = int(len(df))
        total_pages = max(1, ceil(total_rows / page_size)) if total_rows else 1
        page = max(1, min(int(page or 1), total_pages))
        start = (page - 1) * page_size
        sliced = df.iloc[start : start + page_size].copy()

        records = []
        for record in sliced.to_dict(orient="records"):
            records.append({key: self._json_value(value) for key, value in record.items()})

        return {
            "status": "ready",
            "dataset": dataset_id,
            "file": source.name,
            "columns": [str(c) for c in df.columns],
            "rows": records,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_rows": total_rows,
                "total_pages": total_pages,
            },
            "query": query,
            "filter": {"field": filter_field, "value": filter_value},
        }

    # -------------------------------------------------------------------------
    # SOURCE DISCOVERY AND METADATA
    # -------------------------------------------------------------------------
    def _sources(self) -> dict[str, Path | None]:
        result: dict[str, Path | None] = {"dataset1": None, "dataset2": None}
        if not self.raw_dir.exists():
            return result

        for path in sorted(self.raw_dir.glob("*.csv")):
            try:
                columns = set(pd.read_csv(path, nrows=0).columns)
            except Exception:
                continue
            if self.DATASET1_REQUIRED.issubset(columns):
                result["dataset1"] = path
            elif self.DATASET2_REQUIRED.issubset(columns):
                result["dataset2"] = path
        return result

    def _dataset_summary(
        self, dataset_id: str, source: Path, df: pd.DataFrame, filter_fields: list[str]
    ) -> dict[str, Any]:
        filters: dict[str, list[str]] = {}
        for field in filter_fields:
            if field in df.columns:
                filters[field] = self._ordered_values(df, field)
        return {
            "id": dataset_id,
            "file": source.name,
            "rows": int(len(df)),
            "columns_count": int(len(df.columns)),
            "columns": [str(c) for c in df.columns],
            "filters": filters,
            "read_only": True,
        }

    @staticmethod
    def _ordered_values(df: pd.DataFrame, column: str) -> list[str]:
        if column not in df.columns:
            return []
        return [str(value) for value in df[column].dropna().value_counts().index.tolist()]

    @staticmethod
    def _json_value(value: Any) -> Any:
        if pd.isna(value):
            return None
        if hasattr(value, "item"):
            try:
                return value.item()
            except Exception:
                pass
        return value
