from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import math

import pandas as pd


# -----------------------------------------------------------------------------
# DATA CONTRACT
# -----------------------------------------------------------------------------
SUPPORTED_EXTENSIONS = {".csv", ".parquet"}


# -----------------------------------------------------------------------------
# SERIALIZATION AND NORMALIZATION
# -----------------------------------------------------------------------------
def _json_safe(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def _norm(name: str) -> str:
    return " ".join(str(name).strip().lower().replace("_", " ").split())


# -----------------------------------------------------------------------------
# AUDIT MODELS
# -----------------------------------------------------------------------------
@dataclass
class AuditFinding:
    code: str
    severity: str
    title: str
    detail: str
    impact: str


# -----------------------------------------------------------------------------
# AUDIT SERVICE
# -----------------------------------------------------------------------------
class DataAudit:
    def __init__(self, raw_dir: str | Path):
        self.raw_dir = Path(raw_dir)

    def run(self) -> dict[str, Any]:
        files = sorted(
            p for p in self.raw_dir.glob("*")
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
        )
        datasets = []
        findings: list[AuditFinding] = []

        for path in files:
            try:
                df = self._load(path)
                summary, file_findings = self._audit_dataframe(path, df)
                datasets.append(summary)
                findings.extend(file_findings)
            except Exception as exc:
                findings.append(AuditFinding(
                    code="DATASET_READ_ERROR",
                    severity="critical",
                    title=f"Failed to read {path.name}",
                    detail=str(exc),
                    impact="The file cannot be analyzed until the source issue is corrected.",
                ))

        return {
            "status": "ready" if datasets else "awaiting_data",
            "raw_dir": str(self.raw_dir),
            "dataset_count": len(datasets),
            "datasets": datasets,
            "findings": [asdict(item) for item in findings],
            "methodology": {
                "observed": "Value measured directly from the dataset.",
                "derived": "Value calculated only from observed data.",
                "projected": "Estimate applied to the stated operational scale of ~30,000 tickets/year.",
                "rule": "Historical ticket creation dates are never inferred without observable evidence.",
            },
        }

    @staticmethod
    def _load(path: Path) -> pd.DataFrame:
        if path.suffix.lower() == ".parquet":
            return pd.read_parquet(path)
        return pd.read_csv(path, low_memory=False)

    def _audit_dataframe(self, path: Path, df: pd.DataFrame) -> tuple[dict[str, Any], list[AuditFinding]]:
        findings: list[AuditFinding] = []
        normalized = {_norm(c): c for c in df.columns}

        dataset_kind = "unknown"
        if "ticket id" in normalized and "ticket description" in normalized:
            dataset_kind = "operational_support"
        elif "document" in normalized and "topic group" in normalized:
            dataset_kind = "it_classification"

        total_cells = int(df.shape[0] * df.shape[1]) if df.shape[1] else 0
        missing_cells = int(df.isna().sum().sum())
        duplicate_rows = int(df.duplicated().sum())

        column_profiles = []
        for col in df.columns:
            s = df[col]
            missing = int(s.isna().sum())
            profile = {
                "name": str(col),
                "dtype": str(s.dtype),
                "rows": int(len(s)),
                "missing": missing,
                "missing_pct": round((missing / len(s) * 100), 2) if len(s) else 0,
                "unique": int(s.nunique(dropna=True)),
            }
            column_profiles.append(profile)

        temporal = self._temporal_audit(df, normalized, findings)
        operational = self._operational_preview(df, normalized)

        if dataset_kind == "operational_support":
            if "created at" not in normalized and "ticket created at" not in normalized and "created date" not in normalized:
                findings.append(AuditFinding(
                    code="MISSING_CREATED_AT",
                    severity="critical",
                    title="Missing ticket creation timestamp",
                    detail="Dataset 1 has no observable ticket creation or intake timestamp.",
                    impact="Daily or monthly volume, seasonality, and historical end-to-end SLA cannot be measured without fabricating a timestamp.",
                ))

            if "first response time" in normalized:
                findings.append(AuditFinding(
                    code="FIRST_RESPONSE_IS_TIMESTAMP",
                    severity="warning",
                    title="First Response Time requires semantic validation",
                    detail="The field behaves as a timestamp, while the briefing describes it as time to first response.",
                    impact="It must not be used as a duration until its semantics are supported by the data.",
                ))

            if "time to resolution" in normalized:
                findings.append(AuditFinding(
                    code="RESOLUTION_IS_TIMESTAMP",
                    severity="warning",
                    title="Time to Resolution requires semantic validation",
                    detail="The field behaves as a timestamp, while the briefing describes it as total time to resolution.",
                    impact="It must not be used as a duration until the chronology is validated.",
                ))

        if duplicate_rows:
            findings.append(AuditFinding(
                code="DUPLICATE_ROWS",
                severity="warning",
                title="Duplicate rows detected",
                detail=f"Found {duplicate_rows:,} fully duplicated rows.",
                impact="Duplicate rows can inflate volume, category mix, and annual projections.",
            ))

        summary = {
            "file": path.name,
            "kind": dataset_kind,
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "duplicate_rows": duplicate_rows,
            "missing_cells": missing_cells,
            "missing_pct": round((missing_cells / total_cells * 100), 2) if total_cells else 0,
            "column_profiles": column_profiles,
            "temporal": temporal,
            "operational_preview": operational,
        }
        return summary, findings

    @staticmethod
    def _temporal_audit(df: pd.DataFrame, normalized: dict[str, str], findings: list[AuditFinding]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        candidates = [
            "date of purchase",
            "first response time",
            "time to resolution",
            "created at",
            "ticket created at",
        ]
        parsed: dict[str, pd.Series] = {}

        for key in candidates:
            actual = normalized.get(key)
            if not actual:
                continue
            series = pd.to_datetime(df[actual], errors="coerce")
            parsed[key] = series
            valid = series.dropna()
            result[key] = {
                "column": actual,
                "parseable": int(series.notna().sum()),
                "missing_or_invalid": int(series.isna().sum()),
                "min": _json_safe(valid.min()) if not valid.empty else None,
                "max": _json_safe(valid.max()) if not valid.empty else None,
                "unique_dates": int(valid.dt.date.nunique()) if not valid.empty else 0,
            }

        first = parsed.get("first response time")
        resolution = parsed.get("time to resolution")
        if first is not None and resolution is not None:
            mask = first.notna() & resolution.notna()
            backwards = mask & (resolution < first)
            equal_seconds = mask & (first.dt.second == resolution.dt.second)
            pairs = int(mask.sum())
            result["response_resolution_pair"] = {
                "comparable_rows": pairs,
                "resolution_before_first_response": int(backwards.sum()),
                "resolution_before_first_response_pct": round((int(backwards.sum()) / pairs * 100), 2) if pairs else 0,
                "same_second_component": int(equal_seconds.sum()),
                "same_second_component_pct": round((int(equal_seconds.sum()) / pairs * 100), 2) if pairs else 0,
            }
            if backwards.any():
                findings.append(AuditFinding(
                    code="NEGATIVE_RESPONSE_RESOLUTION_ORDER",
                    severity="critical",
                    title="Inconsistent response and resolution chronology",
                    detail=f"{int(backwards.sum()):,} of {pairs:,} valid pairs have resolution earlier than the first response.",
                    impact="Resolution timestamps cannot be used as raw SLA until a validated recovery rule exists.",
                ))

        return result

    @staticmethod
    def _operational_preview(df: pd.DataFrame, normalized: dict[str, str]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key in ["ticket status", "ticket channel", "ticket priority", "ticket type", "product purchased", "topic group"]:
            actual = normalized.get(key)
            if not actual:
                continue
            counts = df[actual].fillna("<missing>").astype(str).value_counts(dropna=False).head(20)
            result[key] = [
                {"label": str(label), "count": int(count)}
                for label, count in counts.items()
            ]
        return result
