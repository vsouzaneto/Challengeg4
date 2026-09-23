"""Pure validation and decision-support engine for Challenge 004."""

from __future__ import annotations

import csv
from copy import deepcopy
import argparse
import hashlib
import html
import io
import json
import math
import os
import re
import sys
import tempfile
import unicodedata
from collections.abc import Iterable
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd


METHOD_VERSION = "2.5.0"
HISTORICAL_METHOD_VERSIONS = ("1.0.0", "2.0.0", "2.1.0", "2.2.0", "2.3.0", "2.4.0")
MAX_CSV_BYTES = 50 * 1024 * 1024
MAX_INT64 = 2**63 - 1
MIN_OPERATIONAL_DATE = pd.Timestamp("1971-01-01T00:00:00")
MAX_OPERATIONAL_DATE = pd.Timestamp("2262-04-10T23:59:59.999999999")
DATE_TIME_POLICY = (
    "ISO-8601 entre 1971-01-01 e 2262-04-10 ou %m/%d/%y %I:%M %p; "
    "datas todas sem offset ou todas com o mesmo offset UTC explícito"
)
ISO_DATE_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d{1,9})?)?(?:[zZ]|[+-]\d{2}:?\d{2})?)?$"
)
ISO_OFFSET_RE = re.compile(r"[+-](\d{2}):?(\d{2})$")
LEGACY_DATE_RE = re.compile(r"^\d{1,2}/\d{1,2}/\d{2} \d{1,2}:\d{2} [AP]M$")
REQUIRED_COLUMNS = (
    "id",
    "platform",
    "content_id",
    "creator_id",
    "content_type",
    "content_category",
    "post_date",
    "views",
    "likes",
    "shares",
    "comments_count",
    "follower_count",
    "is_sponsored",
    "audience_age_distribution",
    "audience_gender_distribution",
    "audience_location",
)
OPTIONAL_COLUMNS = (
    "creator_name",
    "content_url",
    "language",
    "content_length",
    "content_description",
    "hashtags",
    "comments_text",
    "disclosure_type",
    "sponsor_name",
    "sponsor_category",
    "disclosure_location",
)
METRIC_COLUMNS = ("views", "likes", "shares", "comments_count", "follower_count")
CORE_KEYS = ("platform", "content_type", "content_category", "follower_band", "is_sponsored")
GROUP_KEYS = ("platform", "content_type", "content_category", "follower_band")
DRIVER_KEYS = GROUP_KEYS
SPONSORSHIP_KEYS = (*GROUP_KEYS, "period_month")
AUDIENCE_KEYS = (
    "audience_age_distribution",
    "audience_gender_distribution",
    "audience_location",
)
DIMENSION_KEYS = {
    "platform": "platform",
    "content_type": "content_type",
    "content_category": "content_category",
    "creator_band": "follower_band",
    "audience_age": "audience_age_distribution",
    "audience_gender": "audience_gender_distribution",
    "audience_location": "audience_location",
    "month": "period_month",
}


def _error(row: int | None, column: str | None, problem: str, expected: str) -> dict[str, object]:
    return {"row": row, "column": column, "problem": problem, "expected": expected}


def _parse_post_date(value: str) -> pd.Timestamp:
    if LEGACY_DATE_RE.fullmatch(value):
        parsed = pd.Timestamp(datetime.strptime(value, "%m/%d/%y %I:%M %p"))
    elif ISO_DATE_RE.fullmatch(value):
        offset = ISO_OFFSET_RE.search(value)
        if offset:
            hours, minutes = (int(component) for component in offset.groups())
            if hours > 14 or minutes > 59 or (hours == 14 and minutes != 0):
                raise ValueError("unsupported UTC offset")
        parsed = pd.Timestamp(value)
    else:
        raise ValueError("unsupported date grammar")
    parsed = parsed.as_unit("ns")
    if pd.isna(parsed):
        raise ValueError("NaT is not an analytical date")
    if parsed.tzinfo is not None:
        offset = parsed.utcoffset()
        if offset is None or abs(offset.total_seconds()) > 14 * 60 * 60:
            raise ValueError("unsupported UTC offset")
    civil = parsed.tz_localize(None) if parsed.tzinfo is not None else parsed
    if civil < MIN_OPERATIONAL_DATE or civil > MAX_OPERATIONAL_DATE:
        raise OverflowError("date outside operational range")
    return parsed


def load_csv(raw: bytes) -> tuple[pd.DataFrame | None, list[dict[str, object]]]:
    """Validate a complete CSV atomically and return normalized rows."""
    if not raw:
        return None, [_error(None, None, "empty_file", "CSV UTF-8 não vazio")]
    if len(raw) > MAX_CSV_BYTES:
        return None, [_error(None, None, "file_too_large", "até 50 MiB")]
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        return None, [_error(exc.start, None, "invalid_encoding", "UTF-8 ou UTF-8-BOM")]

    prior_field_limit = csv.field_size_limit()
    try:
        csv.field_size_limit(MAX_CSV_BYTES)
        try:
            reader = csv.reader(io.StringIO(text), strict=True)
            rows = []
            physical_lines = []
            while True:
                start_line = reader.line_num + 1
                record = next(reader, None)
                if record is None:
                    break
                rows.append(record)
                physical_lines.append(start_line)
        except csv.Error as exc:
            return None, [_error(None, None, "malformed_csv", str(exc))]
    finally:
        csv.field_size_limit(prior_field_limit)
    if not rows or not rows[0]:
        return None, [_error(None, None, "missing_header", "cabeçalho CSV")]
    header = rows[0]
    nul_errors: list[dict[str, object]] = []
    for record_index, record in enumerate(rows):
        for column_index, value in enumerate(record):
            if "\x00" in value:
                column = (
                    f"header[{column_index + 1}]"
                    if record_index == 0
                    else header[column_index] if column_index < len(header) else f"column[{column_index + 1}]"
                )
                nul_errors.append(
                    _error(physical_lines[record_index], column, "nul_character", "texto UTF-8 sem byte NUL")
                )
    if nul_errors:
        return None, nul_errors
    duplicates = sorted({name for name in header if header.count(name) > 1})
    if duplicates:
        return None, [_error(1, name, "duplicate_header", "nomes de colunas únicos") for name in duplicates]
    malformed_rows = [index for index, row in enumerate(rows[1:], start=1) if len(row) != len(header)]
    if malformed_rows:
        return None, [_error(physical_lines[index], None, "malformed_row", f"{len(header)} campos") for index in malformed_rows]

    missing = [name for name in REQUIRED_COLUMNS if name not in header]
    if missing:
        return None, [_error(1, name, "missing_required_column", "coluna obrigatória") for name in missing]

    frame = pd.DataFrame(rows[1:], columns=header, dtype=str)
    if frame.empty:
        return None, [_error(None, None, "empty_file", "ao menos uma linha de dados")]
    data_physical_lines = physical_lines[1:]

    def physical_line(index: object) -> int:
        return data_physical_lines[int(index)]

    errors: list[dict[str, object]] = []
    for column in REQUIRED_COLUMNS:
        empty = frame[column].astype(str).str.strip().eq("")
        errors.extend(
            _error(physical_line(index), column, "missing_value", "valor obrigatório")
            for index in frame.index[empty]
        )

    numeric_columns: dict[str, pd.Series] = {}
    maximum_integer = str(MAX_INT64)
    for column in METRIC_COLUMNS:
        parsed_integers: list[int | None] = []
        for index, value in frame[column].items():
            if not value.isascii() or not value.isdigit():
                parsed_integers.append(None)
                errors.append(
                    _error(
                        physical_line(index),
                        column,
                        "invalid_nonnegative_integer",
                        "inteiro decimal sem sinal, ponto ou expoente",
                    )
                )
                continue
            canonical = value.lstrip("0") or "0"
            if len(canonical) > len(maximum_integer) or (
                len(canonical) == len(maximum_integer) and canonical > maximum_integer
            ):
                parsed_integers.append(None)
                errors.append(
                    _error(physical_line(index), column, "integer_out_of_range", f"inteiro entre 0 e {MAX_INT64}")
                )
                continue
            parsed_integers.append(int(canonical))
        numeric_columns[column] = pd.Series(parsed_integers, index=frame.index, dtype="object")

    allowed_flags = {"TRUE": True, "FALSE": False, "true": True, "false": False}
    invalid_flags = ~frame["is_sponsored"].isin(allowed_flags)
    errors.extend(
        _error(physical_line(index), "is_sponsored", "invalid_boolean", "TRUE/FALSE ou true/false")
        for index in frame.index[invalid_flags]
    )

    parsed_dates: list[pd.Timestamp | None] = []
    timezone_offsets: list[tuple[int, float]] = []
    timezone_awareness: list[tuple[int, bool]] = []
    for index, value in frame["post_date"].items():
        try:
            parsed = _parse_post_date(value)
            timezone_awareness.append((int(index), parsed.tzinfo is not None))
            if parsed.tzinfo is not None:
                offset = parsed.utcoffset()
                if offset is None:
                    raise ValueError("timezone has no UTC offset")
                timezone_offsets.append((int(index), offset.total_seconds()))
            parsed_dates.append(parsed)
        except (ValueError, TypeError):
            parsed_dates.append(None)
            errors.append(_error(physical_line(index), "post_date", "invalid_date", DATE_TIME_POLICY))
        except OverflowError:
            parsed_dates.append(None)
            errors.append(
                _error(physical_line(index), "post_date", "date_out_of_operational_range", DATE_TIME_POLICY)
            )
    awareness = [aware for _, aware in timezone_awareness]
    if awareness and any(awareness) and not all(awareness):
        errors.append(_error(None, "post_date", "mixed_timezone_semantics", DATE_TIME_POLICY))
    if timezone_offsets:
        expected_offset = timezone_offsets[0][1]
        errors.extend(
            _error(physical_line(index), "post_date", "incompatible_timezone_offset", DATE_TIME_POLICY)
            for index, offset in timezone_offsets[1:]
            if offset != expected_offset
        )

    duplicated_ids = frame["id"].duplicated(keep=False)
    errors.extend(
        _error(physical_line(index), "id", "duplicate_identity", "id único no arquivo")
        for index in frame.index[duplicated_ids]
    )
    duplicated_content = frame.duplicated(["platform", "content_id"], keep=False)
    errors.extend(
        _error(physical_line(index), "content_id", "duplicate_identity", "(platform, content_id) único no arquivo")
        for index in frame.index[duplicated_content]
    )
    if errors:
        errors.sort(key=lambda item: (item["row"] is None, item["row"] or 0, str(item["column"])))
        return None, errors

    source_hash = hashlib.sha256(raw).hexdigest()
    frame = frame.assign(
        **{column: numeric_columns[column].astype("int64") for column in METRIC_COLUMNS},
        is_sponsored=frame["is_sponsored"].map(allowed_flags).astype("bool"),
        post_date=pd.Series(parsed_dates, index=frame.index),
        source_hash=source_hash,
        source_row_id=source_hash + ":" + frame["id"].astype(str),
        source_line=physical_lines[1:],
    )
    return frame, []


def follower_band(followers: int) -> str:
    if followers < 10_000:
        return "0–9,999"
    if followers < 50_000:
        return "10,000–49,999"
    if followers < 100_000:
        return "50,000–99,999"
    if followers < 500_000:
        return "100,000–499,999"
    return "500,000+"


def derive_metrics(df: pd.DataFrame) -> pd.DataFrame:
    interactions = pd.Series(
        (
            int(likes) + int(shares) + int(comments)
            for likes, shares, comments in df[["likes", "shares", "comments_count"]].itertuples(index=False, name=None)
        ),
        index=df.index,
        dtype="object",
    )
    erv = pd.Series(
        (
            100.0 * int(interaction) / int(view) if int(view) > 0 else None
            for interaction, view in zip(interactions, df["views"], strict=True)
        ),
        index=df.index,
        dtype="float64",
    )
    erf = pd.Series(
        (
            100.0 * int(interaction) / int(followers) if int(followers) > 0 else None
            for interaction, followers in zip(interactions, df["follower_count"], strict=True)
        ),
        index=df.index,
        dtype="float64",
    )
    return df.assign(
        interactions=interactions,
        erv=erv,
        erf=erf,
        follower_band=df["follower_count"].map(lambda value: follower_band(int(value))),
        period_month=df["post_date"].dt.strftime("%Y-%m"),
    )


def _strength(rows: pd.DataFrame) -> tuple[float, dict[str, float]]:
    defined = rows.dropna(subset=["erv"])
    n_rate = len(defined)
    n_creators = int(defined["creator_id"].nunique())
    max_share = float(defined["creator_id"].value_counts(normalize=True).max()) if n_rate else 1.0
    factors = {
        "post_factor": min(n_rate / 100, 1),
        "creator_factor": min(n_creators / 20, 1),
        "concentration_factor": 1 - max_share,
    }
    return math.prod(factors.values()), factors


def _strength_label(value: float) -> str:
    if value < 0.40:
        return "limited"
    if value < 0.70:
        return "moderate"
    return "strong"


def _integer_sum(values: Iterable[object]) -> int:
    return sum(int(value) for value in values)


def _summary(rows: pd.DataFrame) -> dict[str, object]:
    rates = rows["erv"].dropna()
    eligible = rows.loc[rows["views"] > 0]
    views = _integer_sum(rows["views"])
    interactions = _integer_sum(rows["interactions"])
    creator_exposure = _integer_sum(rows.groupby("creator_id")["follower_count"].max()) if len(rows) else 0
    eligible_views = _integer_sum(eligible["views"])
    eligible_interactions = _integer_sum(eligible["interactions"])
    return {
        "posts": int(len(rows)),
        "creators": int(rows["creator_id"].nunique()),
        "views": views,
        "interactions": interactions,
        "creator_exposure": creator_exposure,
        "n_rate": int(len(rates)),
        "undefined_rates": int(rows["erv"].isna().sum()),
        "zero_interaction_share": float(rows["interactions"].eq(0).mean()) if len(rows) else None,
        "median_erv": float(rates.median()) if len(rates) else None,
        "median_views_per_post": float(rows["views"].median()) if len(rows) else None,
        "median_interactions_per_post": float(rows["interactions"].median()) if len(rows) else None,
        "q1_erv": float(rates.quantile(0.25)) if len(rates) else None,
        "q3_erv": float(rates.quantile(0.75)) if len(rates) else None,
        "weighted_erv": float(100.0 * eligible_interactions / eligible_views) if eligible_views else None,
    }


def _dimensions(
    rows: pd.DataFrame, source_hash: str, scope_identity: dict[str, object]
) -> dict[str, list[dict[str, object]]]:
    dimensions: dict[str, list[dict[str, object]]] = {}
    for name, column in DIMENSION_KEYS.items():
        items: list[dict[str, object]] = []
        for value, group in rows.groupby(column, dropna=False, sort=True):
            items.append(
                {
                    "evidence_id": _stable_id(
                        "dimension",
                        source_hash,
                        {
                            "scope": scope_identity,
                            "statistic": "descriptive_group_summary",
                            "dimension": name,
                            "value": value,
                        },
                    ),
                    "dimension": name,
                    "value": str(value),
                    **_summary(group),
                    "source_row_ids": sorted(group["source_row_id"].astype(str)),
                }
            )
        dimensions[name] = items
    return dimensions


def align_scope_timestamp(value: object, post_dates: pd.Series) -> pd.Timestamp:
    """Align a UI/date boundary to the dataset timezone without changing its civil date."""
    dataset_timezone = post_dates.dt.tz
    timestamp = pd.Timestamp(value)
    if dataset_timezone is None:
        aligned = timestamp.tz_localize(None) if timestamp.tzinfo is not None else timestamp
    else:
        aligned = timestamp.tz_localize(dataset_timezone) if timestamp.tzinfo is None else timestamp.tz_convert(dataset_timezone)
    return aligned


def _scope_dates(frame: pd.DataFrame, scope: dict[str, object]) -> tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp]:
    reference = align_scope_timestamp(scope.get("reference_date") or max(frame["post_date"]), frame["post_date"])
    end_exclusive = align_scope_timestamp(scope.get("target_end") or reference, frame["post_date"]).normalize() + timedelta(days=1)
    start = align_scope_timestamp(scope.get("target_start") or (reference - timedelta(days=6)), frame["post_date"]).normalize()
    return start, end_exclusive, reference


def _match(rows: pd.DataFrame, target: pd.Series, keys: Iterable[str]) -> pd.DataFrame:
    matched = rows
    for key in keys:
        matched = matched.loc[matched[key] == target[key]]
    return matched


def _benchmark_levels(strict: bool) -> list[tuple[str, int, tuple[str, ...]]]:
    levels = [
        ("core+age+gender+location/90d", 90, AUDIENCE_KEYS),
        ("core+age+gender+location/365d", 365, AUDIENCE_KEYS),
        ("core+age+gender/365d", 365, AUDIENCE_KEYS[:2]),
        ("core+age/365d", 365, AUDIENCE_KEYS[:1]),
        ("core/365d", 365, ()),
    ]
    return levels[:2] if strict else levels


def _benchmark_index(
    frame: pd.DataFrame, target_start: pd.Timestamp, strict: bool
) -> list[tuple[str, tuple[str, ...], pd.DataFrame, dict[object, object]]]:
    indexed = []
    for name, days, audience in _benchmark_levels(strict):
        pool = frame.loc[
            (frame["post_date"] < target_start)
            & (frame["post_date"] >= target_start - timedelta(days=days))
        ]
        keys = (*CORE_KEYS, *audience)
        groups = pool.groupby(list(keys), dropna=False, sort=False).indices if len(pool) else {}
        indexed.append((name, audience, pool, groups))
    return indexed


def _benchmark(
    index: list[tuple[str, tuple[str, ...], pd.DataFrame, dict[object, object]]],
    target: pd.Series,
) -> dict[str, object]:
    attempts: list[dict[str, object]] = []
    for name, audience, pool, groups in index:
        keys = (*CORE_KEYS, *audience)
        group_key = tuple(target[key] for key in keys)
        positions = groups.get(group_key, [])
        candidates = pool.iloc[positions]
        candidates = candidates.loc[candidates["creator_id"] != target["creator_id"]].dropna(subset=["erv"])
        n_rate = len(candidates)
        n_creators = int(candidates["creator_id"].nunique())
        reason = (
            None
            if n_rate >= 30 and n_creators >= 5
            else "insufficient_posts_and_creators"
            if n_rate < 30 and n_creators < 5
            else "insufficient_posts"
            if n_rate < 30
            else "insufficient_creators"
        )
        attempt = {"level": name, "n_rate": n_rate, "n_creators": n_creators, "reason": reason}
        attempts.append(attempt)
        if n_rate >= 30 and n_creators >= 5:
            rates = candidates["erv"]
            q1 = float(rates.quantile(0.25))
            q3 = float(rates.quantile(0.75))
            strength, factors = _strength(candidates)
            context = {key: target[key] for key in (*CORE_KEYS, *audience)}
            return {
                "eligible": True,
                "attempts": attempts,
                "effective_level": name,
                "effective_context": context,
                "removed_controls": [key for key in AUDIENCE_KEYS if key not in audience],
                "n_rate": n_rate,
                "n_creators": n_creators,
                "median": float(rates.median()),
                "q1": q1,
                "q3": q3,
                "iqr": q3 - q1,
                "strength": strength,
                "strength_factors": factors,
                "source_row_ids": sorted(candidates["source_row_id"].astype(str)),
                "abstention_reason": None,
            }
    return {
        "eligible": False,
        "attempts": attempts,
        "effective_level": None,
        "effective_context": None,
        "removed_controls": [],
        "n_rate": 0,
        "n_creators": 0,
        "strength": 0.0,
        "strength_factors": {"post_factor": 0.0, "creator_factor": 0.0, "concentration_factor": 0.0},
        "source_row_ids": [],
        "abstention_reason": "fewer_than_30_rates_or_5_creators",
    }


def _stable_id(kind: str, source_hash: str, payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str, separators=(",", ":"))
    return f"{kind}-{hashlib.sha256(f'{METHOD_VERSION}|{source_hash}|{encoded}'.encode()).hexdigest()[:16]}"


def _canonical_filters(filters: dict[str, object]) -> dict[str, object]:
    canonical: dict[str, object] = {}
    for key in sorted(filters):
        value = filters[key]
        if isinstance(value, (list, tuple, set)):
            canonical[key] = sorted(value, key=lambda item: json.dumps(item, ensure_ascii=False, sort_keys=True, default=str))
        else:
            canonical[key] = value
    return canonical


def _canonical_scope(
    scope: dict[str, object], start: pd.Timestamp, end_exclusive: pd.Timestamp, reference: pd.Timestamp
) -> dict[str, object]:
    return {
        "target_start": start.isoformat(),
        "target_end_exclusive": end_exclusive.isoformat(),
        "reference_date": reference.isoformat(),
        "filters": _canonical_filters(dict(scope.get("filters") or {})),
        "strict_audience": bool(scope.get("strict_audience", False)),
        "include_post_alerts": bool(scope.get("include_post_alerts", True)),
        "method_version": METHOD_VERSION,
    }


def _sponsorship(
    targets: pd.DataFrame, source_hash: str, scope_identity: dict[str, object]
) -> dict[str, object]:
    strata: list[dict[str, object]] = []
    uncovered: list[dict[str, object]] = []
    comparable_posts = 0
    for key, group in targets.groupby(list(SPONSORSHIP_KEYS), dropna=False, sort=True):
        context = dict(zip(SPONSORSHIP_KEYS, key, strict=True))
        arms = {flag: group.loc[group["is_sponsored"] == flag].dropna(subset=["erv"]) for flag in (False, True)}
        eligible = all(len(arm) >= 30 and arm["creator_id"].nunique() >= 5 for arm in arms.values())
        if not eligible:
            uncovered.append(
                {
                    **context,
                    "posts": int(len(group)),
                    "organic_posts": int((~group["is_sponsored"]).sum()),
                    "sponsored_posts": int(group["is_sponsored"].sum()),
                    "organic_defined_rates": int(len(arms[False])),
                    "sponsored_defined_rates": int(len(arms[True])),
                    "organic_creators": int(arms[False]["creator_id"].nunique()),
                    "sponsored_creators": int(arms[True]["creator_id"].nunique()),
                    "reason": "missing_or_insufficient_contemporaneous_arm",
                }
            )
            continue
        creator_medians = {
            flag: arms[flag].groupby("creator_id")["erv"].median() for flag in (False, True)
        }
        organic = float(creator_medians[False].median())
        sponsored = float(creator_medians[True].median())
        strength_org, factors_org = _strength(arms[False])
        strength_spon, factors_spon = _strength(arms[True])
        delta = sponsored - organic
        comparable_posts += len(group)
        strata.append(
            {
                "evidence_id": _stable_id(
                    "sponsorship",
                    source_hash,
                    {"scope": scope_identity, "statistic": "creator_median_erv_difference", "context": context},
                ),
                "context": context,
                "organic": {**_summary(arms[False]), "creator_median_erv": organic, "strength_factors": factors_org},
                "sponsored": {**_summary(arms[True]), "creator_median_erv": sponsored, "strength_factors": factors_spon},
                "delta_erv_pp": delta,
                "relative_difference_pct": (100 * delta / organic) if organic > 0 else None,
                "volume_guard": {
                    "statistic": "median_per_post",
                    "organic_views": float(arms[False]["views"].median()),
                    "sponsored_views": float(arms[True]["views"].median()),
                    "delta_views": float(arms[True]["views"].median() - arms[False]["views"].median()),
                    "organic_interactions": float(arms[False]["interactions"].median()),
                    "sponsored_interactions": float(arms[True]["interactions"].median()),
                    "delta_interactions": float(
                        arms[True]["interactions"].median() - arms[False]["interactions"].median()
                    ),
                },
                "strength": min(strength_org, strength_spon),
                "creator_overlap": int(len(set(creator_medians[False].index) & set(creator_medians[True].index))),
                "representative_date": arms[True]["post_date"].median(),
                "source_row_ids": sorted(group["source_row_id"].astype(str)),
                "claim": "observational_association_not_causal_or_financial_roi",
            }
        )
    return {
        "evidence_id": _stable_id(
            "sponsorship-overview",
            source_hash,
            {
                "scope": scope_identity,
                "statistic": "comparable_post_coverage",
                "posts": len(targets),
                "strata": len(strata),
                "uncovered": len(uncovered),
            },
        ),
        "posts": int(len(targets)),
        "eligible_strata": len(strata),
        "uncovered_count": len(uncovered),
        "strata": strata,
        "uncovered_strata": uncovered,
        "coverage": comparable_posts / len(targets) if len(targets) else 0.0,
        "period_granularity": "calendar_month",
        "required_financial_data": ["investment", "production_cost", "revenue_or_conversion_value"],
        "source_row_ids": sorted(targets["source_row_id"].astype(str)),
    }


def sponsorship_break_even(
    evidence: dict[str, object], assumptions: dict[str, float]
) -> dict[str, object]:
    required = (
        "sponsorship_cost",
        "incremental_production_cost",
        "value_per_conversion",
        "organic_conversion_rate",
        "sponsored_conversion_rate",
    )
    missing = [name for name in required if name not in assumptions]
    evidence_id = evidence.get("evidence_id")
    context = evidence.get("context")
    sponsored = evidence.get("sponsored") if isinstance(evidence.get("sponsored"), dict) else {}
    views_per_post = sponsored.get("median_views_per_post") if isinstance(sponsored, dict) else None
    if not evidence_id:
        missing.append("evidence_id")
    if not isinstance(context, dict) or not context:
        missing.append("context")
    numeric: dict[str, float] = {}
    for name in required:
        value = assumptions.get(name)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            if name not in missing:
                missing.append(name)
        else:
            numeric[name] = float(value)
    if (
        isinstance(views_per_post, bool)
        or not isinstance(views_per_post, (int, float))
        or not math.isfinite(float(views_per_post))
        or float(views_per_post) <= 0
    ):
        missing.append("sponsored.median_views_per_post")
    for name in ("sponsorship_cost", "incremental_production_cost"):
        if name in numeric and numeric[name] < 0:
            missing.append(name)
    if "value_per_conversion" in numeric and numeric["value_per_conversion"] <= 0:
        missing.append("value_per_conversion")
    for name in ("organic_conversion_rate", "sponsored_conversion_rate"):
        if name in numeric and not 0 <= numeric[name] <= 1:
            missing.append(name)
    limitations = ["Cenário manual; não é ROI observado nem efeito causal."]
    if missing:
        return {
            "status": "invalid_or_missing_assumptions",
            "evidence_id": evidence_id,
            "context": deepcopy(context) if isinstance(context, dict) else {},
            "incremental_conversion_rate": None,
            "incremental_conversions": None,
            "incremental_value": None,
            "max_sponsorship_cost": None,
            "required_uplift_pp": None,
            "missing": sorted(set(missing)),
            "limitations": limitations,
        }
    views = float(views_per_post)
    incremental_rate = numeric["sponsored_conversion_rate"] - numeric["organic_conversion_rate"]
    incremental_conversions = views * incremental_rate
    incremental_value = incremental_conversions * numeric["value_per_conversion"]
    max_sponsorship_cost = max(0.0, incremental_value - numeric["incremental_production_cost"])
    required_uplift_pp = 100 * (
        numeric["sponsorship_cost"] + numeric["incremental_production_cost"]
    ) / (views * numeric["value_per_conversion"])
    return {
        "status": (
            "meets_break_even_scenario"
            if numeric["sponsorship_cost"] <= max_sponsorship_cost
            else "below_break_even_scenario"
        ),
        "evidence_id": evidence_id,
        "context": deepcopy(context),
        "incremental_conversion_rate": round(incremental_rate, 9),
        "incremental_conversions": round(incremental_conversions, 9),
        "incremental_value": round(incremental_value, 9),
        "max_sponsorship_cost": round(max_sponsorship_cost, 9),
        "required_uplift_pp": round(required_uplift_pp, 9),
        "missing": [],
        "limitations": limitations,
    }


def _sponsorship_context_summaries(result: dict[str, object]) -> list[dict[str, object]]:
    grouped: dict[tuple[object, ...], list[dict[str, object]]] = {}
    for item in result.get("sponsorship", {}).get("strata", []):
        context = item.get("context", {})
        key = tuple(context.get(name) for name in GROUP_KEYS)
        grouped.setdefault(key, []).append(item)
    summaries: list[dict[str, object]] = []
    for key, items in grouped.items():
        ordered = sorted(items, key=lambda item: str(item.get("context", {}).get("period_month", "")))
        deltas = [float(item["delta_erv_pp"]) for item in ordered]
        median_delta = float(pd.Series(deltas).median())
        same_sign = sum((value > 0) == (median_delta > 0) for value in deltas if value != 0)
        context = dict(zip(GROUP_KEYS, key, strict=True))
        summaries.append(
            {
                "evidence_id": _stable_id(
                    "sponsorship-context",
                    str(result.get("source", {}).get("source_hash", "")),
                    {"context": context, "strata": [item["evidence_id"] for item in ordered]},
                ),
                "context": context,
                "median_delta_erv_pp": median_delta,
                "months": len(ordered),
                "stability": same_sign / len(deltas),
                "stable": len(ordered) >= 3,
                "strength": min(float(item.get("strength", 0)) for item in ordered),
                "posts": sum(int(item["organic"]["posts"]) + int(item["sponsored"]["posts"]) for item in ordered),
                "strata_evidence_ids": [item["evidence_id"] for item in ordered],
            }
        )
    return sorted(
        summaries,
        key=lambda item: (-float(item["median_delta_erv_pp"]), json.dumps(item["context"], sort_keys=True, default=str)),
    )


def _engagement_drivers(
    targets: pd.DataFrame, source_hash: str, scope: dict[str, object]
) -> dict[str, object]:
    organic = targets.loc[(~targets["is_sponsored"]) & targets["erv"].notna()]
    global_iqr = (
        float(organic["erv"].quantile(0.75) - organic["erv"].quantile(0.25))
        if len(organic)
        else 0.0
    )
    materiality = max(0.10, 0.25 * global_iqr)
    monthly_pools = {
        (str(platform), str(band), str(month)): group
        for (platform, band, month), group in organic.groupby(
            ["platform", "follower_band", "period_month"], dropna=False, sort=True
        )
    }
    contexts: list[dict[str, object]] = []
    for key, all_context_rows in organic.groupby(list(DRIVER_KEYS), dropna=False, sort=True):
        context = dict(zip(DRIVER_KEYS, key, strict=True))
        target_frames: list[pd.DataFrame] = []
        peer_frames: list[pd.DataFrame] = []
        monthly: list[dict[str, object]] = []
        for month, target_month in all_context_rows.groupby("period_month", sort=True):
            peer_month = monthly_pools[(str(context["platform"]), str(context["follower_band"]), str(month))]
            peer_month = peer_month.loc[
                ~(
                    peer_month["content_type"].eq(context["content_type"])
                    & peer_month["content_category"].eq(context["content_category"])
                )
            ]
            if (
                len(target_month) < 30
                or target_month["creator_id"].nunique() < 5
                or len(peer_month) < 30
                or peer_month["creator_id"].nunique() < 5
            ):
                continue
            target_frames.append(target_month)
            peer_frames.append(peer_month)
            monthly.append(
                {
                    "period_month": str(month),
                    "target_posts": int(len(target_month)),
                    "target_creators": int(target_month["creator_id"].nunique()),
                    "peer_posts": int(len(peer_month)),
                    "peer_creators": int(peer_month["creator_id"].nunique()),
                    "target_median_erv": float(target_month["erv"].median()),
                    "peer_median_erv": float(peer_month["erv"].median()),
                    "delta_erv_pp": float(target_month["erv"].median() - peer_month["erv"].median()),
                }
            )
        if not monthly:
            continue
        context_rows = pd.concat(target_frames, ignore_index=False)
        peer_rows = pd.concat(peer_frames, ignore_index=False)
        monthly_deltas = [float(item["delta_erv_pp"]) for item in monthly]
        median_delta = float(pd.Series(monthly_deltas).median())
        same_sign_months = sum(
            (value > 0) == (median_delta > 0) for value in monthly_deltas if value != 0
        )
        stability = same_sign_months / len(monthly_deltas)
        strength = min(_strength(context_rows)[0], _strength(peer_rows)[0])
        eligible = (
            len(monthly) >= 3
            and len(context_rows) >= 90
            and context_rows["creator_id"].nunique() >= 10
        )
        is_leader = eligible and median_delta >= materiality and stability >= 2 / 3 and strength >= 0.40
        is_laggard = eligible and median_delta <= -materiality and stability >= 2 / 3 and strength >= 0.40
        target_views = float(context_rows["views"].median())
        peer_views = float(peer_rows["views"].median())
        target_interactions = float(context_rows["interactions"].median())
        peer_interactions = float(peer_rows["interactions"].median())
        delta_views = target_views - peer_views
        delta_interactions = target_interactions - peer_interactions
        signature = json.dumps(context, ensure_ascii=False, sort_keys=True, default=str)
        evidence_id = _stable_id(
            "driver",
            source_hash,
            {"scope": scope, "context": context, "statistic": "median_monthly_peer_erv_difference"},
        )
        contexts.append(
            {
                "evidence_id": evidence_id,
                "context": context,
                "context_signature": signature,
                "eligible": eligible,
                "eligible_months": len(monthly),
                "months": monthly,
                "posts": int(len(context_rows)),
                "creators": int(context_rows["creator_id"].nunique()),
                "peer_posts": int(len(peer_rows)),
                "peer_creators": int(peer_rows["creator_id"].nunique()),
                "median_delta_erv_pp": median_delta,
                "stability": stability,
                "strength": strength,
                "strength_label": _strength_label(strength),
                "materiality_threshold_pp": materiality,
                "is_leader": is_leader,
                "is_laggard": is_laggard,
                "target": _summary(context_rows),
                "peer": _summary(peer_rows),
                "volume_guard": {
                    "target_median_views": target_views,
                    "peer_median_views": peer_views,
                    "delta_views": delta_views,
                    "target_median_interactions": target_interactions,
                    "peer_median_interactions": peer_interactions,
                    "delta_interactions": delta_interactions,
                    "status": "aligned" if delta_views >= 0 and delta_interactions >= 0 else "tradeoff",
                },
                "target_source_row_ids": sorted(context_rows["source_row_id"].astype(str)),
                "peer_source_row_ids": sorted(peer_rows["source_row_id"].astype(str)),
            }
        )

    positive = sorted(
        (item for item in contexts if item["eligible"] and float(item["median_delta_erv_pp"]) > 0),
        key=lambda item: (
            not bool(item["is_leader"]),
            -float(item["stability"]),
            -float(item["strength"]),
            -float(item["median_delta_erv_pp"]),
            -int(item["posts"]),
            str(item["context_signature"]),
        ),
    )
    negative = sorted(
        (item for item in contexts if item["eligible"] and float(item["median_delta_erv_pp"]) < 0),
        key=lambda item: (
            not bool(item["is_laggard"]),
            -float(item["stability"]),
            -float(item["strength"]),
            float(item["median_delta_erv_pp"]),
            -int(item["posts"]),
            str(item["context_signature"]),
        ),
    )
    contexts.sort(key=lambda item: str(item["context_signature"]))
    leader = next((item for item in positive if item["is_leader"]), None)
    laggard = next((item for item in negative if item["is_laggard"]), None)
    return {
        "evidence_id": _stable_id(
            "driver-overview",
            source_hash,
            {"scope": scope, "statistic": "stable_multivariate_organic_contexts"},
        ),
        "materiality_threshold_pp": materiality,
        "contexts": contexts,
        "leader": leader,
        "laggard": laggard,
        "best_candidate": positive[0] if positive else None,
        "runner_up": positive[1] if len(positive) > 1 else None,
        "verdict": "stable_winner" if leader else "no_sustained_winner",
        "change_trigger": (
            "Reavaliar quando houver três meses elegíveis, efeito material, estabilidade >=2/3 e força >=0,40."
        ),
    }


def _p95(values: pd.Series) -> float:
    if values.empty:
        return 0.0
    value = float(values.quantile(0.95))
    if value > 0:
        return value
    positives = values.loc[values > 0]
    return float(positives.max()) if len(positives) else 0.0


def _aggregate_normalization(targets: pd.DataFrame) -> dict[tuple[str, str], dict[str, float]]:
    pools: dict[tuple[str, str], list[dict[str, float]]] = {}
    specifications = (
        ("editorial", targets.loc[~targets["is_sponsored"]], (*GROUP_KEYS, *AUDIENCE_KEYS)),
        ("sponsorship", targets.loc[targets["is_sponsored"]], SPONSORSHIP_KEYS),
    )
    for kind, rows, keys in specifications:
        for _, group in rows.groupby(list(keys), dropna=False, sort=True):
            platform = str(group.iloc[0]["platform"])
            pools.setdefault((kind, platform), []).append(
                {
                    "views": float(_integer_sum(group["views"])),
                    "interactions": float(_integer_sum(group["interactions"])),
                    "followers": float(_integer_sum(group.groupby("creator_id")["follower_count"].max())),
                }
            )
    return {
        key: {
            name: _p95(pd.Series([values[name] for values in groups]))
            for name in ("views", "interactions", "followers")
        }
        for key, groups in pools.items()
    }


def _priority(values: dict[str, float], denominators: dict[str, float], strength: float, date: pd.Timestamp, reference: pd.Timestamp) -> tuple[float, dict[str, float]]:
    normalized = [min(values[name] / denominators[name], 1.0) if denominators[name] else 0.0 for name in ("views", "interactions", "followers")]
    impact = sum(normalized) / 3
    age = max((reference.normalize() - date.normalize()).days, 0)
    recency = 2 ** (-age / 7)
    score = 100 * impact * strength * recency
    return score, {"impact": impact, "strength": strength, "recency": recency}


def _frequency_hypothesis(
    rows: pd.DataFrame,
    coverage_start: pd.Timestamp,
    coverage_end: pd.Timestamp,
    period_month: object | None = None,
) -> dict[str, object]:
    coverage_start_date = coverage_start.date()
    coverage_end_date = coverage_end.date()
    if period_month is not None:
        year, month = (int(part) for part in str(period_month).split("-", maxsplit=1))
        month_start = date(year, month, 1)
        next_month = date(year + (month == 12), month % 12 + 1, 1)
        coverage_start_date = max(coverage_start_date, month_start)
        coverage_end_date = min(coverage_end_date, next_month - timedelta(days=1))

    first_monday = coverage_start_date + timedelta(days=(-coverage_start_date.weekday()) % 7)
    last_sunday = coverage_end_date - timedelta(days=(coverage_end_date.weekday() + 1) % 7)
    week_starts: list[date] = []
    cursor = first_monday
    while cursor <= last_sunday:
        week_starts.append(cursor)
        cursor += timedelta(days=7)

    observed = rows.assign(
        week_start=rows["post_date"].map(
            lambda value: value.date() - timedelta(days=value.weekday())
        )
    )
    observed = observed.loc[observed["week_start"].isin(week_starts)]
    counts = observed.groupby(["creator_id", "week_start"], sort=True).size()
    observed_weeks = int(observed["week_start"].nunique())
    sufficient = observed_weeks >= 2
    return {
        "status": "test" if sufficient else "collect",
        "value": float(counts.median()) if sufficient else None,
        "unit": "posts_per_creator_per_complete_iso_week",
        "method": "median_observed_posts_per_creator_week",
        "coverage_rule": (
            "complete_iso_weeks_within_calendar_month_and_scope"
            if period_month is not None
            else "complete_iso_weeks_within_scope"
        ),
        "period_month": str(period_month) if period_month is not None else None,
        "sample_creator_weeks": int(len(counts)),
        "sample_creators": int(observed["creator_id"].nunique()),
        "complete_weeks_available": len(week_starts),
        "observed_complete_weeks": observed_weeks,
        "window_start": _calendar_midnight_iso(week_starts[0], coverage_start.tzinfo) if week_starts else None,
        "window_end": _calendar_midnight_iso(week_starts[-1] + timedelta(days=6), coverage_start.tzinfo) if week_starts else None,
        "action_type": "test_observed_cadence" if sufficient else "collect_two_complete_weeks",
        "collection_requirement_weeks": 2,
        "limitation": "frequência observada é hipótese de teste, não efeito causal",
    }


def _calendar_midnight_iso(value: date, timezone: object | None) -> str:
    timestamp = pd.Timestamp(value)
    if timezone is not None:
        timestamp = timestamp.tz_localize(timezone)
    return timestamp.isoformat()


def _context_rows(rows: pd.DataFrame, context: dict[str, object], sponsored: bool | None = None) -> pd.DataFrame:
    selected = rows
    for key, value in context.items():
        if key in selected.columns:
            selected = selected.loc[selected[key] == value]
    if sponsored is not None:
        selected = selected.loc[selected["is_sponsored"] == sponsored]
    return selected


def _apply_filters(rows: pd.DataFrame, filters: dict[str, object]) -> pd.DataFrame:
    selected = rows
    for key, value in filters.items():
        if key in selected.columns and value not in (None, "", []):
            accepted = value if isinstance(value, (list, tuple, set)) else [value]
            selected = selected.loc[selected[key].isin(accepted)]
    return selected


def _observation_summary(rows: pd.DataFrame, statistic: str) -> dict[str, object]:
    """One safe aggregation boundary for durable baseline and follow-up data."""
    defined = rows.dropna(subset=["erv"])
    summary = _summary(rows)
    median = ((defined.groupby("creator_id")["erv"].median().median()
               if statistic == "median_creator_erv" else defined["erv"].median()) if len(defined) else None)
    return {**summary, "metric": "erv", "unit": "percent", "statistic": statistic,
            "median": float(median) if len(defined) else None,
            "creators": int(defined["creator_id"].nunique()),
            "source_row_ids": sorted(rows["source_row_id"].astype(str))}


def decision_baseline(snapshot: dict[str, object]) -> dict[str, object]:
    """Preserve the exact engine evidence plus its explicit follow-up basis."""
    return {**deepcopy(snapshot["context_aggregate"]),
            "evidence_id": snapshot["evidence_id"], "evidence_snapshot": deepcopy(snapshot),
            "contract": deepcopy(snapshot["observation_contract"])}


def observe_evidence(df: pd.DataFrame, baseline: dict[str, object],
                     window: dict[str, object], source_hash: str) -> dict[str, object]:
    """Reapply saved controls/statistic, replacing only the observation window.

    Month is a baseline provenance coordinate, not a permanent segment filter:
    the new explicit window replaces it. All audience and sponsorship controls
    remain fixed. Legacy baselines without a contract cannot be reconstructed.
    """
    frame = derive_metrics(df)
    start, end, _ = _scope_dates(frame, window)
    contract = baseline.get("contract")
    rows = frame.loc[(frame["post_date"] >= start) & (frame["post_date"] < end)]
    if contract:
        rows = _context_rows(_apply_filters(rows, contract["filters"]), contract["context"])
        if contract.get("defined_rates_only"):
            rows = rows.dropna(subset=["erv"])
    else:
        rows = rows.iloc[0:0]
    statistic = contract["statistic"] if contract else "unavailable_legacy_contract"
    return {**_observation_summary(rows, statistic), "contract": deepcopy(contract),
            "source_hash": source_hash,
            "period_start": start.date().isoformat(),
            "period_end": (end - timedelta(days=1)).date().isoformat(),
            "coverage_days": int((end - start).days),
            "scope": {**deepcopy(baseline.get("evidence_snapshot", {}).get("scope", {})),
                      "target_start": start.isoformat(), "target_end_exclusive": end.isoformat()}}


def _editorial(
    frame: pd.DataFrame,
    start: pd.Timestamp,
    end_exclusive: pd.Timestamp,
    source_hash: str,
    scope_identity: dict[str, object],
) -> list[dict[str, object]]:
    duration = int((end_exclusive.normalize() - start.normalize()).days)
    previous_start = start.normalize() - timedelta(days=duration)
    current = frame.loc[(frame["post_date"] >= start) & (frame["post_date"] < end_exclusive) & ~frame["is_sponsored"]]
    previous = frame.loc[(frame["post_date"] >= previous_start) & (frame["post_date"] < start) & ~frame["is_sponsored"]]
    evidence: list[dict[str, object]] = []
    keys = [*GROUP_KEYS, *AUDIENCE_KEYS]
    for key, now in current.groupby(keys, dropna=False, sort=True):
        context = dict(zip(keys, key, strict=True))
        before = previous
        for name, value in context.items():
            before = before.loc[before[name] == value]
        now_defined = now.dropna(subset=["erv"])
        before_defined = before.dropna(subset=["erv"])
        if min(len(now_defined), len(before_defined)) < 30 or min(now_defined["creator_id"].nunique(), before_defined["creator_id"].nunique()) < 5:
            continue
        current_strength, _ = _strength(now_defined)
        previous_strength, _ = _strength(before_defined)
        delta_erv = float(now_defined["erv"].median() - before_defined["erv"].median())
        delta_views = float(now["views"].median() - before["views"].median())
        delta_interactions = float(now["interactions"].median() - before["interactions"].median())
        evidence.append(
            {
                "evidence_id": _stable_id(
                    "editorial",
                    source_hash,
                    {"scope": scope_identity, "statistic": "period_median_erv_difference", "context": context},
                ),
                "context": context,
                "current": _summary(now),
                "previous": _summary(before),
                "current_source_row_ids": sorted(now["source_row_id"].astype(str)),
                "previous_source_row_ids": sorted(before["source_row_id"].astype(str)),
                "delta_erv_pp": delta_erv,
                "delta_views_per_post": delta_views,
                "delta_interactions_per_post": delta_interactions,
                "strength": min(current_strength, previous_strength),
                "representative_date": now["post_date"].median(),
                "source_row_ids": sorted(now["source_row_id"].astype(str)),
                "creator_overlap": int(len(set(now["creator_id"]) & set(before["creator_id"]))),
            }
        )
    return evidence


ACTION_TEXT = {
    "scale_test": "Ampliar gradualmente o padrão editorial em teste controlado; reavaliar taxa e volume antes de escalar",
    "test": "Testar o padrão em escala limitada e coletar evidência antes de ampliar esforço ou investimento",
    "review": "Revisar o criativo e evitar repetir o padrão até novo teste",
    "review_stop": "Revisar a interrupção do padrão editorial com sinais negativos concordantes; decidir humanamente antes de parar",
    "sponsorship_test_after_costs": "Obter custos reais e, somente depois, avaliar um teste controlado de patrocínio; não autorizar desembolso automaticamente",
    "review_renewal": "Revisar a renovação do patrocínio diante de taxa e volume negativos; obter custos e decisão humana antes de renovar ou interromper",
    "collect": "Coletar amostra comparável antes de recomendar mudança",
}


def _audience_analysis(targets: pd.DataFrame, source_hash: str, scope: dict[str, object]) -> list[dict[str, object]]:
    """Pair eligible labels within monthly core strata, also controlling sponsorship.

    Labels are post metadata, not personas. Effects remain observational; other
    audience dimensions are not controlled and no cross-stratum winner is ranked.
    """
    controls = [*SPONSORSHIP_KEYS, "is_sponsored"]
    output = []
    for dimension in AUDIENCE_KEYS:
        keys = [*controls, dimension]
        cells = targets.groupby(keys, dropna=False, sort=True).agg(
            posts=("id", "size"), n_rate=("erv", "count"),
        )
        creators = targets.dropna(subset=["erv"]).groupby(keys, dropna=False)["creator_id"].nunique()
        cells["creators"] = creators.reindex(cells.index, fill_value=0)
        eligible = cells.loc[(cells["n_rate"] >= 30) & (cells["creators"] >= 5)]
        comparisons = []
        covered_ids: set[str] = set()
        eligible_strata = 0
        for key, labels in eligible.groupby(level=list(range(len(controls))), sort=True):
            if len(labels) < 2:
                continue
            eligible_strata += 1
            context = dict(zip(controls, key, strict=True))
            context["is_sponsored"] = bool(context["is_sponsored"])
            pool = _context_rows(targets, context)
            arms = {str(label[-1]): pool.loc[pool[dimension] == label[-1]].dropna(subset=["erv"])
                    for label in labels.index}
            names = sorted(arms)
            for index, label in enumerate(names):
                for comparator in names[:index]:
                    target, reference = arms[label], arms[comparator]
                    target_ids = sorted(target["source_row_id"].astype(str))
                    reference_ids = sorted(reference["source_row_id"].astype(str))
                    covered_ids.update(target_ids + reference_ids)
                    comparisons.append({
                        "evidence_id": _stable_id("audience", source_hash, {"scope": scope, "dimension": dimension,
                            "context": context, "target": label, "comparator": comparator, "statistic": "post_median_erv_difference"}),
                        "context": {**context, "dimension": dimension, "target_label": label, "comparator_label": comparator},
                        "target": _summary(target), "comparator": _summary(reference),
                        "delta_erv_pp": float(target["erv"].median() - reference["erv"].median()),
                        "strength": min(_strength(target)[0], _strength(reference)[0]),
                        "target_source_row_ids": target_ids, "comparator_source_row_ids": reference_ids,
                    })
        total_strata = targets.groupby(controls, dropna=False).ngroups
        output.append({
            "evidence_id": _stable_id("audience-overview", source_hash, {"scope": scope, "dimension": dimension,
                "statistic": "eligible_audience_label_pair_coverage"}),
            "dimension": dimension, "controls": controls, **_summary(targets),
            "total_strata": total_strata, "eligible_strata": eligible_strata,
            "uncovered_count": total_strata - eligible_strata, "total_cells": len(cells),
            "eligible_cells": len(eligible), "max_cell_defined_rates": int(cells["n_rate"].max()) if len(cells) else 0,
            "covered_posts": len(covered_ids), "coverage": len(covered_ids) / len(targets) if len(targets) else 0.0,
            "required_rates_per_label": 30, "required_creators_per_label": 5,
            "status": "observational_pairs" if comparisons else "insufficient_comparable_labels",
            "comparisons": comparisons, "source_row_ids": sorted(targets["source_row_id"].astype(str)),
        })
    return output


def analyze(df: pd.DataFrame, scope: dict[str, object], source_hash: str) -> dict[str, object]:
    frame = derive_metrics(df)
    start, end_exclusive, reference = _scope_dates(frame, scope)
    scope_identity = _canonical_scope(scope, start, end_exclusive, reference)
    filters = dict(scope.get("filters") or {})
    filtered_frame = _apply_filters(frame, filters)
    targets = filtered_frame.loc[
        (filtered_frame["post_date"] >= start) & (filtered_frame["post_date"] < end_exclusive)
    ]
    has_observations = not targets.empty
    analysis_state = {
        "status": "ready" if has_observations else "empty_scope",
        "has_observations": has_observations,
        "reason": None if has_observations else "no_matching_records",
        "message": (
            None
            if has_observations
            else "Nenhum registro corresponde aos filtros/período selecionados. Ajuste o recorte para continuar."
        ),
    }
    coverage_frame = filtered_frame if len(filtered_frame) else frame
    frequency_coverage_start = max(start.normalize(), min(coverage_frame["post_date"]).normalize())
    frequency_coverage_end = min(
        (end_exclusive - pd.Timedelta(1, unit="ns")).normalize(),
        max(coverage_frame["post_date"]).normalize(),
    )

    alerts: list[dict[str, object]] = []
    benchmark_diagnostics: dict[str, dict[str, object]] = {}
    benchmark_levels_attempted = 0
    benchmark_resolver = _benchmark_index(frame, start, bool(scope.get("strict_audience", False)))
    alert_targets = targets if bool(scope.get("include_post_alerts", True)) else targets.iloc[0:0]
    if len(alert_targets) and not any(len(pool) for _, _, pool, _ in benchmark_resolver):
        valid_targets = alert_targets.dropna(subset=["erv"])
        empty_attempts = [
            {
                "level": name,
                "n_rate": 0,
                "n_creators": 0,
                "reason": "insufficient_posts_and_creators",
            }
            for name, _, _ in _benchmark_levels(bool(scope.get("strict_audience", False)))
        ]
        benchmark_levels_attempted = len(valid_targets) * len(empty_attempts)
        for context_key, group in valid_targets.groupby(
            list((*CORE_KEYS, *AUDIENCE_KEYS)), dropna=False, sort=True
        ):
            requested_context = dict(zip((*CORE_KEYS, *AUDIENCE_KEYS), context_key, strict=True))
            benchmark_diagnostics[json.dumps(requested_context, sort_keys=True, default=str)] = {
                "context": requested_context,
                "reason": "fewer_than_30_rates_or_5_creators",
                "attempts": empty_attempts,
                "target_count": int(len(group)),
                "sample_target_ids": sorted(group["id"].astype(str))[:5],
            }
        alert_targets = alert_targets.iloc[0:0]
    for _, target in alert_targets.sort_values(["post_date", "id"]).iterrows():
        if pd.isna(target["erv"]):
            continue
        benchmark = _benchmark(benchmark_resolver, target)
        benchmark_levels_attempted += len(benchmark["attempts"])
        if not benchmark["eligible"]:
            requested_context = {key: target[key] for key in (*CORE_KEYS, *AUDIENCE_KEYS)}
            signature = json.dumps(
                {"context": requested_context, "attempts": benchmark["attempts"]},
                ensure_ascii=False,
                sort_keys=True,
                default=str,
            )
            diagnostic = benchmark_diagnostics.setdefault(
                signature,
                {
                    "context": requested_context,
                    "reason": benchmark["abstention_reason"],
                    "attempts": benchmark["attempts"],
                    "target_count": 0,
                    "sample_target_ids": [],
                },
            )
            diagnostic["target_count"] = int(diagnostic["target_count"]) + 1
            if len(diagnostic["sample_target_ids"]) < 5:
                diagnostic["sample_target_ids"].append(str(target["id"]))
            continue
        iqr = float(benchmark["iqr"])
        rate = float(target["erv"])
        q1 = float(benchmark["q1"])
        q3 = float(benchmark["q3"])
        median = float(benchmark["median"])
        direction = "high" if rate > q3 + 1.5 * iqr else "low" if rate < q1 - 1.5 * iqr else "within"
        is_outlier = iqr > 0 and direction != "within"
        context = {key: target[key] for key in (*CORE_KEYS, *AUDIENCE_KEYS)}
        alerts.append(
            {
                "evidence_id": _stable_id(
                    "post",
                    source_hash,
                    {
                        "scope": scope_identity,
                        "statistic": "post_erv_vs_tukey_benchmark",
                        "id": target["id"],
                        "context": context,
                    },
                ),
                "evidence_type": "post",
                "source_id": str(target["id"]),
                "source_row_id": str(target["source_row_id"]),
                "context": context,
                "post_date": target["post_date"].isoformat(),
                "erv": rate,
                "delta_erv_pp": rate - median,
                "relative_difference_pct": (100 * (rate - median) / median) if median > 0 else None,
                "direction": direction,
                "is_outlier": is_outlier,
                "strength": float(benchmark["strength"]),
                "strength_label": _strength_label(float(benchmark["strength"])) if iqr > 0 else "limited",
                "benchmark": benchmark,
                "values": {"views": int(target["views"]), "interactions": int(target["interactions"]), "followers": int(target["follower_count"])},
            }
        )

    sponsorship = _sponsorship(targets, source_hash, scope_identity)
    engagement_drivers = _engagement_drivers(targets, source_hash, scope_identity)
    editorial = _editorial(filtered_frame, start, end_exclusive, source_hash, scope_identity)
    candidates: list[dict[str, object]] = []

    platform_denominators: dict[str, dict[str, float]] = {}
    for platform, rows in targets.groupby("platform"):
        platform_denominators[str(platform)] = {
            "views": _p95(rows["views"].astype(float)),
            "interactions": _p95(rows["interactions"].astype(float)),
            "followers": _p95(rows["follower_count"].astype(float)),
        }
    for alert in alerts:
        if not alert["is_outlier"]:
            continue
        platform = str(alert["context"]["platform"])
        score, components = _priority(alert["values"], platform_denominators[platform], float(alert["strength"]), pd.Timestamp(alert["post_date"]), reference)
        limited = float(alert["strength"]) < 0.40
        action_type = "test" if limited or alert["direction"] == "high" else "review"
        topic = "creator" if limited else "quick_win" if alert["direction"] == "high" else "stop"
        candidates.append(
            {
                "recommendation_key": alert["evidence_id"],
                "evidence_id": alert["evidence_id"],
                "evidence_type": "post",
                "topic": topic,
                "action_type": action_type,
                "action": ACTION_TEXT[action_type],
                "owner": "Gestor de Social Media",
                "execution_window": "próximos 7 dias",
                "review_window": "7 dias após o teste",
                "metric": "ERv e volume por post",
                "priority": score,
                "priority_components": components,
                "priority_values": alert["values"],
                "normalization": platform_denominators[platform],
                "delta_erv_pp": alert["delta_erv_pp"],
                "representative_date": alert["post_date"],
                "context": alert["context"],
                "supporting_topics": ["audience", "creator", "frequency"],
                "frequency_hypothesis": _frequency_hypothesis(
                    _context_rows(targets, alert["context"]),
                    frequency_coverage_start,
                    frequency_coverage_end,
                    alert["context"].get("period_month"),
                ),
                "evidence_snapshot": {
                    "family": "post",
                    "evidence_id": alert["evidence_id"],
                    "method_version": METHOD_VERSION,
                    "scope": scope_identity,
                    "statistic": "post_erv_vs_tukey_benchmark",
                    "context": alert["context"],
                    "target": {
                        "source_id": alert["source_id"],
                        "source_row_id": alert["source_row_id"],
                        "post_date": alert["post_date"],
                        "erv": alert["erv"],
                        "values": alert["values"],
                    },
                    "comparator": alert["benchmark"],
                },
            }
        )

    aggregate_items: list[tuple[str, dict[str, object], dict[str, float], str, str]] = []
    for item in editorial:
        current = item["current"]
        values = {"views": float(current["views"]), "interactions": float(current["interactions"]), "followers": float(current["creator_exposure"])}
        delta = float(item["delta_erv_pp"])
        aligned_up = delta > 0 and item["delta_views_per_post"] >= 0 and item["delta_interactions_per_post"] >= 0
        aligned_down = delta < 0 and item["delta_views_per_post"] <= 0 and item["delta_interactions_per_post"] <= 0
        if float(item["strength"]) >= 0.70 and aligned_up:
            action_type, topic = "scale_test", "effort"
        elif float(item["strength"]) >= 0.70 and aligned_down:
            action_type, topic = "review_stop", "stop"
        else:
            action_type, topic = "test", "effort"
        aggregate_items.append(("editorial", item, values, action_type, topic))
    for item in sponsorship["strata"]:
        arm = item["sponsored"]
        values = {"views": float(arm["views"]), "interactions": float(arm["interactions"]), "followers": float(arm["creator_exposure"])}
        delta = float(item["delta_erv_pp"])
        delta_views = float(item["volume_guard"]["delta_views"])
        delta_interactions = float(item["volume_guard"]["delta_interactions"])
        if float(item["strength"]) >= 0.40 and delta > 0 and delta_views >= 0 and delta_interactions >= 0:
            action_type = "sponsorship_test_after_costs"
        elif float(item["strength"]) >= 0.70 and delta < 0 and delta_views <= 0 and delta_interactions <= 0:
            action_type = "review_renewal"
        else:
            action_type = "test"
        aggregate_items.append(("sponsorship", item, values, action_type, "sponsorship"))

    aggregate_denominators = _aggregate_normalization(targets)
    for kind, item, values, action_type, topic in aggregate_items:
        platform = str(item["context"]["platform"])
        representative = pd.Timestamp(item["representative_date"])
        score, components = _priority(values, aggregate_denominators[(kind, platform)], float(item["strength"]), representative, reference)
        candidates.append(
            {
                "recommendation_key": item["evidence_id"],
                "evidence_id": item["evidence_id"],
                "evidence_type": "aggregate",
                "topic": topic,
                "action_type": action_type,
                "action": ACTION_TEXT[action_type],
                "owner": "Gestor de Social Media",
                "execution_window": "próximos 7 dias",
                "review_window": "7 dias após o teste",
                "metric": "ERv, views e interações por post",
                "priority": score,
                "priority_components": components,
                "priority_values": values,
                "normalization": aggregate_denominators[(kind, platform)],
                "delta_erv_pp": item["delta_erv_pp"],
                "representative_date": representative.isoformat(),
                "context": item["context"],
                "supporting_topics": ["audience", "creator", "frequency", "quick_win"],
                "frequency_hypothesis": _frequency_hypothesis(
                    _context_rows(
                        targets,
                        item["context"],
                        sponsored=False if kind == "editorial" else True,
                    ),
                    frequency_coverage_start,
                    frequency_coverage_end,
                    item["context"].get("period_month"),
                ),
                "evidence_snapshot": {
                    "family": kind,
                    "evidence_id": item["evidence_id"],
                    "method_version": METHOD_VERSION,
                    "scope": scope_identity,
                    "statistic": (
                        "creator_median_erv_difference"
                        if kind == "sponsorship"
                        else "period_median_erv_difference"
                    ),
                    "context": item["context"],
                    "target": item["sponsored"] if kind == "sponsorship" else item["current"],
                    "comparator": item["organic"] if kind == "sponsorship" else item["previous"],
                    "source_row_ids": item["source_row_ids"],
                    **({"volume_guard": item["volume_guard"]} if kind == "sponsorship" else {}),
                },
            }
        )

    candidates.sort(key=lambda item: (-float(item["priority"]), -abs(float(item["delta_erv_pp"])), -pd.Timestamp(item["representative_date"]).value, str(item["evidence_id"])))
    all_recommendations: list[dict[str, object]] = []
    seen: set[tuple[object, ...]] = set()
    for item in candidates:
        context = item["context"]
        key = tuple(context.get(name) for name in (*GROUP_KEYS, *AUDIENCE_KEYS)) + (start.isoformat(), end_exclusive.isoformat())
        if key in seen:
            continue
        seen.add(key)
        all_recommendations.append(item)

    recommendations = all_recommendations[:3]

    evidence_by_id = {item["evidence_id"]: item for item in [*alerts, *editorial, *sponsorship["strata"]]}
    for rank, recommendation in enumerate(all_recommendations, 1):
        snapshot = deepcopy(recommendation["evidence_snapshot"])
        family = snapshot["family"]
        evidence = evidence_by_id[snapshot["evidence_id"]]
        context = dict(snapshot["context"])
        if family in ("editorial", "sponsorship"):
            context["is_sponsored"] = family == "sponsorship"
        rows = _context_rows(targets, context)
        if family == "sponsorship":
            rows = rows.dropna(subset=["erv"])
        statistic = "median_creator_erv" if family == "sponsorship" else "median_post_erv"
        observation_context = {key: value for key, value in context.items() if key != "period_month"}
        contract = {"family": family, "filters": scope_identity["filters"], "context": observation_context,
                    "statistic": statistic, "unit": "percent", "metric": "erv",
                    "defined_rates_only": family == "sponsorship",
                    "period_policy": "replace_baseline_window_preserve_segment_controls"}
        baseline_start, baseline_end = start, end_exclusive
        if context.get("period_month"):
            month_start = align_scope_timestamp(context["period_month"] + "-01", frame["post_date"])
            baseline_start = max(start, month_start)
            baseline_end = min(end_exclusive, month_start + pd.offsets.MonthBegin(1))
        aggregate = {**_observation_summary(rows, statistic),
                     "period_start": baseline_start.date().isoformat(),
                     "period_end": (baseline_end - timedelta(days=1)).date().isoformat(),
                     "coverage_days": int((baseline_end - baseline_start).days)}
        if family == "post":
            references = {"target": [evidence["source_row_id"]], "comparator": evidence["benchmark"]["source_row_ids"],
                          "context_aggregate": aggregate["source_row_ids"]}
        elif family == "editorial":
            references = {"target": evidence["current_source_row_ids"], "comparator": evidence["previous_source_row_ids"]}
        else:
            comparator = _context_rows(targets, {**context, "is_sponsored": False}).dropna(subset=["erv"])
            references = {"target": aggregate["source_row_ids"], "comparator": sorted(comparator["source_row_id"].astype(str))}
        snapshot.update({"recommendation": {"rank": rank, **deepcopy({
                             key: value for key, value in recommendation.items() if key != "evidence_snapshot"})},
                         "source_hash": source_hash, "strength": evidence["strength"],
                         "strength_label": evidence.get("strength_label", _strength_label(evidence["strength"])),
                         "delta_erv_pp": evidence["delta_erv_pp"], "references": references,
                         "observation_contract": contract, "context_aggregate": aggregate})
        # Convert NumPy scalar context labels to native JSON values without
        # stringifying booleans, which would change subsequent filter semantics.
        recommendation["evidence_snapshot"] = json.loads(json.dumps(snapshot, default=lambda value: value.item()))

    pending = [] if recommendations else [{
        "evidence_id": _stable_id(
            "pending", source_hash, {
                "scope": scope_identity,
                "statistic": "no_matching_records" if not has_observations else "eligibility_abstention",
            }
        ),
        "action_type": "adjust_scope" if not has_observations else "collect",
        "action": (
            "Ajustar filtros ou período; nenhum registro corresponde ao recorte selecionado"
            if not has_observations
            else ACTION_TEXT["collect"]
        ),
        "reason": "no_matching_records" if not has_observations else "no_eligible_performance_evidence",
    }]
    return {
        "source": {
            "source_hash": source_hash,
            "rows": int(len(frame)),
            "period_start": min(frame["post_date"]).isoformat(),
            "period_end": max(frame["post_date"]).isoformat(),
            "platforms": sorted(frame["platform"].unique().tolist()),
        },
        "scope": {
            **scope,
            **scope_identity,
            "target_end": (end_exclusive - timedelta(days=1)).normalize().isoformat(),
        },
        "analysis_state": analysis_state,
        "quality": {
            "optional_columns_missing": sorted(set(OPTIONAL_COLUMNS) - set(frame.columns)),
            "ignored_source_engagement_rate": "engagement_rate" in frame.columns,
            "warnings": ([{
                "code": "source_engagement_rate_ignored",
                "message": "A coluna engagement_rate foi ignorada; ERv foi recalculada a partir das contagens.",
            }] if "engagement_rate" in frame.columns else []),
            "benchmark_levels_attempted": benchmark_levels_attempted,
            "benchmark_diagnostics": list(benchmark_diagnostics.values()),
            "method_compatibility": {
                "current": METHOD_VERSION,
                "historical_versions": list(HISTORICAL_METHOD_VERSIONS),
                "compatible_for_outcome_comparison": [],
            },
        },
        "metrics": _summary(targets),
        "dimensions": _dimensions(targets, source_hash, scope_identity),
        "audience": _audience_analysis(targets, source_hash, scope_identity),
        "cohorts": {"editorial": editorial},
        "alerts": alerts,
        "sponsorship": sponsorship,
        "engagement_drivers": engagement_drivers,
        "recommendations": recommendations,
        "all_recommendations": all_recommendations,
        "evidence_snapshots": {
            str(item["evidence_id"]): item["evidence_snapshot"] for item in all_recommendations
        },
        "pending": pending,
        "row_references": {str(row["source_row_id"]): int(row["source_line"]) for _, row in frame.iterrows()},
        "target_source_row_ids": sorted(targets["source_row_id"].astype(str)),
    }


EXPORT_COLUMNS = (
    "record_type", "evidence_id", "source_hash", "method_version", "text",
    "metric_name", "metric_value", "unit", "context", "scope",
    "formula",
    "source_row_id", "source_line", "decision_id", "status", "owner",
    "execution_window", "review_window",
    "rank", "recommendation_key", "priority", "impact", "strength", "recency",
    "priority_values", "normalization", "delta_erv_pp", "representative_date",
    "action", "action_type", "topic", "metric", "frequency_hypothesis",
    "reference_chunk", "reference_index", "reference_role", "statistics",
    "field_name", "field_chunk", "field_value",
)

# History columns are appended only when history exists, preserving the static
# analytical export contract (and its byte identity) for empty local logs.
HISTORY_EXPORT_COLUMNS = (
    "event_id", "revision_of", "decided_at", "baseline", "original_text",
    "edited_text", "effective_text", "outcome_id", "recorded_at",
    "decision_source_hash", "decision_scope", "decision_method_version",
    "execution_status", "execution_date", "observed", "comparison", "reason",
    "period_start", "period_end", "coverage_days", "baseline_coverage_days",
    "coverage_equal", "comparable", "baseline_median", "observed_median",
    "median_delta", "baseline_volume_per_day", "observed_volume_per_day",
    "non_causal",
)


def _cell(value: object) -> str | int | float:
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        return value
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str) if isinstance(value, (dict, list, tuple)) else str(value)
    for char in text:
        if unicodedata.category(char) in ("Cc", "Cf") or char in ("=", "+", "-", "@"):
            return f"'{text}"
        if not char.isspace():
            break
    return text


def _reference_chunks(source_ids: list[str], lines: dict[str, int]) -> Iterable[dict[str, object]]:
    chunk = 1
    ids, indices, physical = [], [], []
    size = 2
    for index, source_id in enumerate(source_ids):
        opaque_id = str(source_id).split(":", 1)[-1]
        # Bound even a single unusually long ID; repeated indices join its fragments.
        for offset in range(0, len(opaque_id), 4096):
            fragment = opaque_id[offset:offset + 4096]
            length = len(json.dumps(fragment, ensure_ascii=False)) + 2
            if ids and (size + length > 32_768 or len(ids) == 500):
                yield {"reference_chunk": chunk, "reference_index": indices, "source_row_id": ids, "source_line": physical}
                chunk += 1
                ids, indices, physical, size = [], [], [], 2
            ids.append(fragment)
            indices.append(index)
            physical.append(lines[str(source_id)])
            size += length
    if ids:
        yield {"reference_chunk": chunk, "reference_index": indices, "source_row_id": ids, "source_line": physical}


def _iter_export_rows(result: dict[str, object], decisions: list[dict[str, object]]) -> Iterable[dict[str, object]]:
    source = result.get("source", {})
    scope = result.get("scope", {})
    source_hash = source.get("source_hash", "")
    method = scope.get("method_version", METHOD_VERSION)
    columns = EXPORT_COLUMNS + (HISTORY_EXPORT_COLUMNS if decisions else ())

    def row(record_type: str, evidence_id: str = "", **values: object) -> dict[str, object]:
        return {name: _cell({"record_type": record_type, "evidence_id": evidence_id, "source_hash": source_hash, "method_version": method, "scope": scope, **values}.get(name, "")) for name in columns}

    def history_row(record_type: str, evidence_id: str, **values: object) -> Iterable[dict[str, object]]:
        # Never infer historical provenance from the currently active analysis.
        values = {"source_hash": "", "scope": None, "method_version": "", **values}
        exported = row(record_type, evidence_id, **values)
        chunks = []
        for name, value in exported.items():
            if isinstance(value, str) and len(value) > 32_768:
                exported[name] = ""
                for offset in range(0, len(value), 4096):
                    chunks.append(row(
                        "history_field", evidence_id,
                        **{key: values.get(key, "") for key in ("source_hash", "method_version", "decision_id", "outcome_id", "event_id")},
                        scope=None, field_name=name, field_chunk=offset // 4096 + 1,
                        field_value=json.dumps(value[offset:offset + 4096], ensure_ascii=False),
                    ))
        yield exported
        yield from chunks

    def analytical_row(record_type: str, evidence_id: str = "", **values: object) -> Iterable[dict[str, object]]:
        exported = row(record_type, evidence_id, **values)
        chunks = []
        for name, value in exported.items():
            if isinstance(value, str) and len(value) > 32_768:
                exported[name] = ""
                for offset in range(0, len(value), 4096):
                    chunks.append(row("analysis_field", evidence_id, scope=None,
                        reference_role=values.get("reference_role", ""), field_name=f"{record_type}.{name}",
                        field_chunk=offset // 4096 + 1, field_value=json.dumps(value[offset:offset + 4096], ensure_ascii=False)))
        yield exported
        yield from chunks

    state = result.get("analysis_state", {})
    has_observations = bool(state.get("has_observations", result.get("metrics", {}).get("posts", 0) > 0))
    yield from analytical_row(
        "summary",
        metric_name="posts" if has_observations else "analysis_state",
        metric_value=result.get("metrics", {}).get("posts") if has_observations else None,
        unit="posts" if has_observations else "",
        text="Escopo analisado" if has_observations else state.get("message", "Nenhum registro corresponde ao recorte."),
        statistics=state,
    )
    summary_id = _stable_id("summary", str(source_hash), scope)
    evidence: list[dict[str, object]] = [{
        "evidence_id": summary_id,
        "dimension": "overall",
        "value": "Escopo completo",
        **result.get("metrics", {}),
        "analysis_state": state,
        "source_row_ids": result.get("target_source_row_ids", []),
    }]
    for items in result.get("dimensions", {}).values():
        evidence.extend(items)
    evidence.extend(result.get("alerts", []))
    evidence.extend(result.get("cohorts", {}).get("editorial", []))
    if result.get("sponsorship", {}).get("evidence_id"):
        evidence.append(result["sponsorship"])
    evidence.extend(result.get("sponsorship", {}).get("strata", []))
    drivers = result.get("engagement_drivers", {})
    if drivers.get("evidence_id"):
        evidence.append({
            "evidence_id": drivers["evidence_id"],
            "export_metric_name": "driver_overview",
            "metric_value": len(drivers.get("contexts", [])),
            "verdict": drivers.get("verdict"),
            "materiality_threshold_pp": drivers.get("materiality_threshold_pp"),
            "change_trigger": drivers.get("change_trigger"),
            "source_row_ids": [],
        })
    for driver in drivers.get("contexts", []):
        evidence.append({
            **driver,
            "export_metric_name": "driver_context",
            "metric_value": driver.get("median_delta_erv_pp"),
            "comparator_source_row_ids": driver.get("peer_source_row_ids", []),
            "comparator": driver.get("peer", {}),
        })
    strategy = content_strategy_30d(result)
    evidence.append({
        **strategy,
        "export_metric_name": "strategy_30d",
        "metric_value": len(strategy["weeks"]),
        "source_row_ids": [],
    })
    for week in strategy["weeks"]:
        evidence.append({
            **week,
            "export_metric_name": "strategy_week",
            "metric_value": week["week"],
            "context": {**strategy["context"], "window": week["window"], "phase": week["phase"]},
            "source_row_ids": [],
        })
    evidence.extend(result.get("pending", []))
    for overview in result.get("audience", []):
        evidence.append(overview)
        evidence.extend(overview.get("comparisons", []))

    emitted: set[str] = set()
    for item in evidence:
        evidence_id = str(item.get("evidence_id", ""))
        if not evidence_id or evidence_id in emitted:
            continue
        emitted.add(evidence_id)
        metric_name = str(item.get("export_metric_name") or ("metric_value" if item.get("metric_value") is not None else "median_erv" if "median_erv" in item else "delta_erv_pp" if item.get("delta_erv_pp") is not None else "coverage" if item.get("coverage") is not None else "posts"))
        metric_value = item.get(metric_name, item.get("metric_value", item.get("posts", "")))
        text = item.get("value", item.get("action", item.get("reason", item.get("claim", item.get("direction", item.get("dimension", "evidence"))))))
        context = dict(item.get("context") or {"dimension": item.get("dimension"), "value": item.get("value")})
        context.update({name: item[name] for name in ("posts", "creators", "n_rate", "views", "interactions", "creator_exposure", "undefined_rates", "zero_interaction_share", "weighted_erv", "q1_erv", "q3_erv", "strength", "organic", "sponsored", "creator_overlap", "eligible_strata", "uncovered_count", "coverage", "period_granularity", "required_financial_data") if name in item})
        formula = "eligible controlled posts / scoped posts" if evidence_id.startswith("sponsorship-overview-") else "median_by_creator(sponsored ERv) - median_by_creator(organic ERv)" if evidence_id.startswith("sponsorship-") else "median(100 * (likes + shares + comments_count) / views)" if evidence_id.startswith(("dimension-", "summary-")) else "method_version contract"
        if "benchmark" in item:
            formula = "target ERv - comparator median; Tukey bounds q1-1.5*IQR, q3+1.5*IQR; IQR=q3-q1"
        elif "current_source_row_ids" in item:
            formula = "median(current ERv) - median(previous ERv); equal duration filtered organic periods"
        elif evidence_id.startswith("audience-overview-"):
            formula = "posts in eligible within-stratum label pairs / scoped posts; each label >=30 defined rates and >=5 creators"
        elif evidence_id.startswith("audience-"):
            formula = "median(target label ERv) - median(comparator label ERv); matched monthly core and sponsorship"
        elif metric_name in ("driver_overview", "driver_context"):
            formula = "median(monthly target ERv - same-platform-and-follower-band peer ERv); organic posts only"
        elif metric_name in ("strategy_30d", "strategy_week"):
            formula = "deterministic 30-day operating sequence derived from the selected driver and decision gates"
        statistics = {key: value for key, value in item.items() if key not in (
            "source_row_ids", "source_row_id", "current_source_row_ids", "previous_source_row_ids",
            "target_source_row_ids", "peer_source_row_ids", "comparator_source_row_ids", "strata", "uncovered_strata", "comparisons", "benchmark")}
        yield from analytical_row("evidence", evidence_id, text=text, metric_name=metric_name, metric_value=metric_value, unit="ratio" if metric_name == "coverage" else "percentage_points" if metric_name in ("delta_erv_pp", "driver_context") else "percent" if "erv" in metric_name else "count", context=context, statistics=statistics, formula=formula)
        roles = {"target": item.get("source_row_ids", [])}
        if "benchmark" in item:
            roles = {"target": [item["source_row_id"]], "comparator": item["benchmark"]["source_row_ids"]}
            for role, stats in (("target", {key: item[key] for key in ("source_id", "post_date", "erv", "values")}),
                                ("comparator", {key: value for key, value in item["benchmark"].items() if key != "source_row_ids"})):
                yield from analytical_row("evidence_detail", evidence_id, reference_role=role, statistics=stats, context=item["context"])
        elif "current_source_row_ids" in item:
            roles = {"target": item["current_source_row_ids"], "comparator": item["previous_source_row_ids"]}
            for role, name in (("target", "current"), ("comparator", "previous")):
                yield from analytical_row("evidence_detail", evidence_id, reference_role=role, statistics=item[name], text=name)
        elif "target_source_row_ids" in item:
            roles = {"target": item["target_source_row_ids"], "comparator": item["comparator_source_row_ids"]}
            for role in roles:
                yield from analytical_row("evidence_detail", evidence_id, reference_role=role, statistics=item[role])
        for role, source_row_ids in roles.items():
            for chunk in _reference_chunks(source_row_ids, result.get("row_references", {})):
                yield from analytical_row("source_ref", evidence_id, scope=None, reference_role=role, **chunk)

    quality = result.get("quality", {})
    yield from analytical_row("quality", statistics={key: value for key, value in quality.items() if key not in ("benchmark_diagnostics", "warnings")})
    for warning in quality.get("warnings", []):
        yield from analytical_row("warning", text=warning.get("message", ""), statistics=warning)
    for index, diagnostic in enumerate(quality.get("benchmark_diagnostics", [])):
        yield from analytical_row("benchmark_diagnostic", f"diagnostic-{index + 1}", statistics=diagnostic, context=diagnostic.get("context", {}))
    for index, uncovered in enumerate(result.get("sponsorship", {}).get("uncovered_strata", [])):
        yield from analytical_row("sponsorship_uncovered", f"uncovered-{index + 1}", statistics=uncovered, context={key: uncovered[key] for key in SPONSORSHIP_KEYS})

    for rank, item in enumerate(result.get("all_recommendations", result.get("recommendations", [])), start=1):
        yield from analytical_row("recommendation", str(item["evidence_id"]), rank=rank,
                  **{name: item.get(name) for name in ("recommendation_key", "priority", "priority_values", "normalization", "delta_erv_pp", "representative_date", "context", "action", "action_type", "topic", "metric", "owner", "execution_window", "review_window", "frequency_hypothesis")},
                  **item.get("priority_components", {}),
                  formula="100 * mean(min(V/P95_V,1), min(I/P95_I,1), min(F/P95_F,1)) * strength * 2**(-age_days/7)")

    for decision in decisions:
        baseline = decision.get("baseline", {})
        evidence_id = str(baseline.get("evidence_id") or decision.get("evidence_id") or decision.get("recommendation_key", ""))
        effective = (decision.get("edited_text", "") if decision.get("status") == "edited" else decision.get("original_text", decision.get("text", decision.get("action", ""))))
        decision_values = {key: decision.get(key, "") for key in (
            "decision_id", "event_id", "revision_of", "decided_at", "recommendation_key",
            "source_hash", "scope", "method_version", "status", "original_text", "edited_text",
            "owner", "execution_window", "review_window",
        )}
        yield from history_row("decision", evidence_id, **decision_values, baseline=baseline, text=effective, effective_text=effective)
        for outcome in decision.get("outcomes", []):
            observed = outcome.get("observed", {})
            comparison = outcome.get("comparison", {})
            yield from history_row(
                "outcome", evidence_id,
                **{key: outcome.get(key, "") for key in ("outcome_id", "event_id", "source_hash", "method_version", "recorded_at", "execution_status", "execution_date", "status", "reason")},
                scope=outcome.get("scope", observed.get("scope")),
                decision_id=decision.get("decision_id", ""), revision_of=decision.get("revision_of"),
                decided_at=decision.get("decided_at", ""),
                decision_source_hash=decision.get("source_hash", ""),
                decision_scope=decision.get("scope"), decision_method_version=decision.get("method_version", ""),
                observed=observed, comparison=comparison,
                metric_name=observed.get("metric", outcome.get("metric_name", "")),
                metric_value=observed.get("median", outcome.get("metric_value")),
                unit="percent" if observed.get("metric") == "erv" else outcome.get("unit", ""),
                **{key: observed.get(key) for key in ("period_start", "period_end", "coverage_days")},
                baseline_coverage_days=baseline.get("coverage_days"),
                **{key: comparison.get(key) for key in ("coverage_equal", "baseline_median", "observed_median", "median_delta", "baseline_volume_per_day", "observed_volume_per_day")},
                comparable=outcome.get("status") == "observed", non_causal=True,
                text="Associação observacional; não demonstra causalidade ou ROI financeiro.",
            )


def iter_export_rows(result: dict[str, object], decisions: list[dict[str, object]]) -> Iterable[dict[str, object]]:
    """Final size boundary, including metadata inherited by existing fragments.

    Ordinary exports retain their exact shape. Exceptional oversized metadata is
    joined by deterministic 1-based base-row ordinal (exclude export_field rows).
    This also bounds IDs/provenance on fragment rows without recursive metadata.
    """
    for ordinal, exported in enumerate(_iter_export_rows(result, decisions), 1):
        chunks = []
        for name, value in exported.items():
            if isinstance(value, str) and len(value) > 32_768:
                exported[name] = ""
                for offset in range(0, len(value), 4096):
                    fragment = dict.fromkeys(exported, "")
                    fragment.update(record_type="export_field", evidence_id=f"export-row-{ordinal}",
                                    field_name=name, field_chunk=offset // 4096 + 1,
                                    field_value=json.dumps(value[offset:offset + 4096], ensure_ascii=False))
                    chunks.append(fragment)
        yield exported
        yield from chunks


def export_evidence(result: dict[str, object], decisions: list[dict[str, object]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=EXPORT_COLUMNS + (HISTORY_EXPORT_COLUMNS if decisions else ()), lineterminator="\n")
    writer.writeheader()
    writer.writerows(iter_export_rows(result, decisions))
    return output.getvalue().encode("utf-8")


RECENCY_NOTE = (
    "Atualidade = 2^(−idade em dias/7), ancorada na data de referência do dataset. "
    "Em grupos agregados, a data representativa é a mediana das datas do grupo-alvo "
    "(posts patrocinados na comparação de patrocínio). Um escopo de dois anos pode "
    "produzir scores muito pequenos: isso preserva a regra de recência e não demonstra "
    "uma oportunidade atual. A ordem é prioridade decrescente, |ΔERv| decrescente, "
    "data representativa decrescente e evidence_id crescente, após deduplicação contextual."
)


def _delta_text(item: dict[str, object], precision: int) -> str:
    delta = item.get("delta_erv_pp")
    if delta is None:
        return "ΔERv não definido — sem comparador elegível"
    return f"ΔERv {float(delta):+.{precision}g} p.p."


def _recommendation_text(item: dict[str, object]) -> str:
    context = " / ".join(str(value) for value in item.get("context", {}).values())
    components = item.get("priority_components", {})
    frequency = item.get("frequency_hypothesis")
    frequency_text = ""
    if frequency:
        cadence = (f"Testar {frequency['value']:g} posts por creator por semana ISO completa"
                   if frequency["value"] is not None else "Coletar antes de sugerir cadência; valor não definido")
        frequency_text = (
            f". Frequência: {cadence}; status {frequency['status']}; unidade {frequency['unit']}; "
            f"mês {frequency.get('period_month') or 'não fixado'}; regra {frequency['coverage_rule']}; "
            f"método {frequency['method']}; {frequency['sample_creator_weeks']} creator-semanas, "
            f"{frequency['sample_creators']} creators; {frequency['complete_weeks_available']} semanas completas disponíveis, "
            f"{frequency['observed_complete_weeks']} semanas observadas; janela {frequency['window_start'] or 'não definida'} a {frequency['window_end'] or 'não definida'}; "
            f"ação {frequency['action_type']}; mínimo de {frequency['collection_requirement_weeks']} semanas completas observadas. "
            f"Limite: {frequency['limitation']}; ausência de linha não equivale a zero."
        )
    return (
        f"{context}: {item.get('action', item.get('reason', 'Coletar evidência'))}. "
        f"Prioridade {item.get('priority', 0):.6g}; impacto {components.get('impact', 0):.6g}; "
        f"força {components.get('strength', 0):.6g}; atualidade {components.get('recency', 0):.6g}; "
        f"{_delta_text(item, 6)}; data representativa {item.get('representative_date', 'não definida')}. "
        f"Responsável: {item.get('owner', 'Gestor de Social Media')}; execução: {item.get('execution_window', 'coletar primeiro')}; "
        f"revisão: {item.get('review_window', 'após coleta')}; métrica: {item.get('metric', 'amostra comparável')}. "
        f"Evidência: {item.get('evidence_id', '')}{frequency_text}"
    )


def _short(value: object, limit: int = 180) -> str:
    value = " ".join(str(value).split())
    return value if len(value) <= limit else value[:limit - 1] + "…"


def _scope_text(result: dict[str, object]) -> str:
    scope, source = result.get("scope", {}), result.get("source", {})
    temporal = ""
    if "period_mode" in scope:
        partial = scope.get("partial_period")
        coverage = ("parcial (janela incompleta)" if partial is True else
                    "completa no intervalo solicitado" if partial is False else "não informada")
        temporal = (f"Seleção temporal: {_short(scope['period_mode'], 40)}; janela solicitada "
                    f"{_short(scope.get('requested_start', 'não informada'), 35)} a "
                    f"{_short(scope.get('requested_end', 'não informada'), 35)}; "
                    f"cobertura temporal {coverage}. ")
    state = result.get("analysis_state", {})
    target_text = (
        f"{result.get('metrics', {}).get('posts', 0)} posts-alvo de {source.get('rows', 0)} linhas na fonte."
        if state.get("has_observations", result.get("metrics", {}).get("posts", 0) > 0)
        else f"{state.get('message', 'Nenhum registro corresponde ao recorte.')} A fonte preserva {source.get('rows', 0)} linhas."
    )
    return (f"{temporal}Método {scope.get('method_version', METHOD_VERSION)}. Escopo efetivo: "
            f"{scope.get('target_start', 'não informado')} a {scope.get('target_end', 'não informado')}; "
            f"referência {scope.get('reference_date', 'não informada')}; "
            f"filtros {json.dumps(scope.get('filters', {}), ensure_ascii=False, sort_keys=True)}. "
            f"{target_text}")


def _coverage_text(result: dict[str, object]) -> str:
    sponsorship, quality = result.get("sponsorship", {}), result.get("quality", {})
    state = result.get("analysis_state", {})
    if not state.get("has_observations", result.get("metrics", {}).get("posts", 0) > 0):
        return "Cobertura analítica não definida: o recorte não contém observações; ajuste filtros ou período."
    diagnostics = quality.get("benchmark_diagnostics", [])
    missing = sum(int(item.get("target_count", 0)) for item in diagnostics)
    return (f"Cobertura parcial: patrocínio {100 * sponsorship.get('coverage', 0):.3g}% dos posts, "
            f"{sponsorship.get('eligible_strata', 0)} estratos elegíveis, {sponsorship.get('uncovered_count', 0)} insuficientes. "
            f"Benchmarks: {quality.get('benchmark_levels_attempted', 0)} níveis tentados; {missing} alvos sem referência elegível; "
            f"alertas post a post {'ativados' if result.get('scope', {}).get('include_post_alerts', True) else 'desativados'}. "
            f"{len(quality.get('warnings', []))} avisos de qualidade; detalhes e motivos completos no CSV.")


def _decision_lines(result: dict[str, object], decisions: list[dict[str, object]]) -> list[str]:
    source_hash = result.get("source", {}).get("source_hash")
    relevant = [item for item in decisions if item.get("source_hash") == source_hash]
    replaced = {str(item["revision_of"]): str(item.get("decision_id", "")) for item in decisions if item.get("revision_of")}

    def order(item: dict[str, object]) -> tuple[int, str]:
        try:
            date = pd.Timestamp(item.get("decided_at")).value
        except (ValueError, TypeError):
            date = 0
        return date, str(item.get("decision_id", ""))

    lines = []
    for item in sorted(relevant, key=order, reverse=True)[:6]:
        effective = item.get("edited_text", "") if item.get("status") == "edited" else item.get("original_text", item.get("text", item.get("action", "")))
        revision = f"; revisa {_short(item['revision_of'], 40)}" if item.get("revision_of") else ""
        superseded = f"; SUPERADA por {_short(replaced[str(item['decision_id'])], 40)}" if str(item.get("decision_id")) in replaced else "; vigente"
        lines.append(f"{_short(item.get('decision_id', ''), 40)} · {_short(item.get('decided_at', 'data ausente'), 32)} · "
                     f"{_short(item.get('status', ''), 20)}{revision}{superseded} · fonte {_short(item.get('source_hash', ''), 12)} · "
                     f"método {_short(item.get('method_version', 'ausente'), 12)} · {_short(effective, 100)}")
    omitted = len(decisions) - len(relevant)
    if omitted:
        lines.append(f"{omitted} eventos de outras fontes ou sem proveniência omitidos deste resumo; íntegra no CSV.")
    if len(relevant) > 6:
        lines.append(f"Exibidos os 6 eventos mais recentes desta fonte, de {len(relevant)}; íntegra no CSV.")
    return lines or ["Nenhuma decisão registrada nesta fonte."]


def _executive_context(context: dict[str, object]) -> str:
    labels = {
        "text": "texto", "video": "vídeo", "image": "imagem", "mixed": "misto",
        "lifestyle": "estilo de vida",
    }
    values = [labels.get(str(context[key]).lower(), str(context[key])).replace(",", ".") for key in GROUP_KEYS if context.get(key) is not None]
    return _short(" / ".join(values), 140)


def content_strategy_30d(result: dict[str, object]) -> dict[str, object]:
    drivers = result.get("engagement_drivers", {})
    driver = drivers.get("leader")
    collection = drivers.get("best_candidate")
    selected = driver or collection
    context = dict(selected.get("context", {})) if selected else {}
    recommendation = next(
        (
            item for item in result.get("all_recommendations", result.get("recommendations", []))
            if all(item.get("context", {}).get(key) == context.get(key) for key in GROUP_KEYS)
        ),
        None,
    )
    frequency = recommendation.get("frequency_hypothesis", {}) if recommendation else {}
    if frequency.get("status") == "test" and frequency.get("value") is not None:
        tested_cadence = f"testar {float(frequency['value']):g} posts por creator/semana ISO completa"
    else:
        tested_cadence = "coletar cadência comparável sem inventar quantidade"
    strength = float(selected.get("strength", 0)) if selected else 0.0
    scale_gate = bool(
        driver
        and strength >= 0.70
        and float(driver.get("median_delta_erv_pp", 0)) >= float(drivers.get("materiality_threshold_pp", 0.10))
        and int(driver.get("eligible_months", 0)) >= 2
        and driver.get("volume_guard", {}).get("status") == "aligned"
    )
    strategy_id = _stable_id(
        "strategy",
        str(result.get("source", {}).get("source_hash", "")),
        {"method": METHOD_VERSION, "context": context, "driver": selected.get("evidence_id") if selected else None},
    )
    week_specs = (
        (1, "D1–D7", "baseline", "Congelar o contexto e registrar o baseline orgânico comparável",
         "ERv mediano, visualizações e interações por post", "manter o mix corrente fora do teste",
         "30 taxas definidas e cinco creators em alvo e comparador"),
        (2, "D8–D14", "test", ("Testar o contexto vencedor" if driver else "Testar o melhor candidato elegível") + " sem alterar o mix fora do experimento",
         "Delta de ERv contra pares da mesma plataforma e faixa", tested_cadence,
         "Efeito acima da materialidade e guards não negativos"),
        (3, "D15–D21", "replicate_or_revise", "Replicar uma vez se o sinal persistir; revisar se divergir",
         "Concordância entre duas janelas e concentração por creator",
         tested_cadence if driver else "coletar sem número inventado",
         "Duas janelas concordantes e força sem queda"),
        (4, "D22–D30", "decide",
         "Propor ampliação como novo teste" if scale_gate else "Manter, revisar ou coletar; não escalar",
         "Confiança, materialidade, visualizações e interações", "manter até decisão humana registrada",
         "C>=0,70, efeito material, duas janelas concordantes e guards não negativos"),
    )
    weeks = [
        {
            "evidence_id": _stable_id("strategy-week", str(result.get("source", {}).get("source_hash", "")),
                                      {"strategy": strategy_id, "week": week}),
            "week": week,
            "window": window,
            "phase": phase,
            "owner": "Gestor de Social Media",
            "action": action,
            "metric": metric,
            "cadence": cadence,
            "gate": gate,
        }
        for week, window, phase, action, metric, cadence, gate in week_specs
    ]
    return {
        "evidence_id": strategy_id,
        "mix_policy": "preserve_current_mix_outside_tests",
        "context": context,
        "driver_evidence_id": selected.get("evidence_id") if selected else drivers.get("evidence_id", ""),
        "weeks": weeks,
        "scale_gate_met": scale_gate,
        "automatic_publication_or_spend": False,
    }


def executive_answers(
    result: dict[str, object], financial_scenario: dict[str, object] | None = None
) -> list[dict[str, str]]:
    """Answer every mandatory challenge question from deterministic evidence."""
    metrics = result.get("metrics", {})
    posts = int(metrics.get("posts", 0))
    count = lambda value: f"{int(value):,}".replace(",", ".")
    decimal = lambda value, digits: f"{float(value):.{digits}f}".replace(".", ",")
    signed = lambda value, digits: f"{float(value):+.{digits}f}".replace(".", ",")
    questions = (
        "O que gera engajamento?",
        "Vale patrocinar influenciadores?",
        "Qual deve ser a estratégia?",
        "Qual perfil de audiência mais engaja?",
    )
    if not result.get("analysis_state", {}).get("has_observations", posts > 0):
        return [
            {
                "question": question,
                "verdict": "SEM BASE PARA RESPONDER",
                "kpi": "0 posts elegíveis",
                "comparison": "Nenhum recorte comparável.",
                "sample": "Cobertura: 0 posts.",
                "action": "Ajustar filtros ou importar dados válidos antes de decidir.",
                "strength": "Força: não mensurável",
                "coverage": "Cobertura: 0 posts",
                "stability": "Estabilidade: não mensurável",
                "evidence_id": str(result.get("pending", [{}])[0].get("evidence_id", "sem-evidência")),
                "change_trigger": "A decisão mudaria após existir um recorte válido e comparável.",
            }
            for question in questions
        ]

    drivers = result.get("engagement_drivers", {})
    leader = drivers.get("leader")
    if leader:
        context_text = _executive_context(leader["context"])
        target, peer = leader["target"], leader["peer"]
        guard = leader["volume_guard"]
        engagement = {
            "question": questions[0],
            "verdict": f"{context_text.upper()} É O MELHOR SINAL ORGÂNICO SUSTENTADO; NÃO É PROVA CAUSAL",
            "kpi": f"ΔERv mediano mensal: {signed(leader['median_delta_erv_pp'], 3)} p.p.",
            "comparison": (
                f"ERv {decimal(target['median_erv'], 3)}% vs. pares {decimal(peer['median_erv'], 3)}%; "
                f"views/post {decimal(guard['target_median_views'], 0)} vs. {decimal(guard['peer_median_views'], 0)}; "
                f"interações/post {decimal(guard['target_median_interactions'], 0)} vs. "
                f"{decimal(guard['peer_median_interactions'], 0)}; volume {guard['status']}."
            ),
            "sample": f"{count(leader['posts'])} posts, {count(leader['creators'])} creators, {leader['eligible_months']} meses elegíveis.",
            "action": "Priorizar este contexto em teste controlado; preservar o mix fora do teste.",
            "strength": f"Força heurística C={decimal(leader['strength'], 3)} ({leader['strength_label']}).",
            "coverage": f"Cobertura: {leader['eligible_months']} meses; alvo {count(leader['posts'])}, pares {count(leader['peer_posts'])} posts.",
            "stability": f"Estabilidade: {decimal(100 * leader['stability'], 1)}% dos meses no mesmo sinal.",
            "evidence_id": str(leader["evidence_id"]),
            "change_trigger": "A decisão mudaria se o efeito cair abaixo da materialidade, a estabilidade ficar <2/3 ou C<0,40.",
        }
    else:
        candidates = list(drivers.get("contexts", []))
        best = max(candidates, key=lambda item: float(item.get("strength", 0)), default={})
        trigger = str(drivers.get("change_trigger", "houver evidência comparável suficiente"))
        engagement = {
            "question": questions[0],
            "verdict": "NÃO EXISTE VENCEDOR SUSTENTADO; NÃO REDISTRIBUIR O MIX",
            "kpi": f"Limiar material: {decimal(drivers.get('materiality_threshold_pp', 0.10), 3)} p.p.",
            "comparison": f"{len(candidates)} contextos avaliados; nenhum passou simultaneamente amostra, materialidade, estabilidade e força.",
            "sample": f"Base: {count(posts)} posts.",
            "action": "Manter o mix e coletar/testar contextos comparáveis antes de priorizar.",
            "strength": f"Melhor força disponível: C={decimal(best.get('strength', 0), 3)}.",
            "coverage": f"Cobertura: {len(candidates)} contextos com ao menos um mês comparável.",
            "stability": "Estabilidade: insuficiente para declarar vencedor.",
            "evidence_id": str(drivers.get("evidence_id", "sem-evidência")),
            "change_trigger": trigger if "mudaria" in trigger.lower() else f"A decisão mudaria quando: {trigger}",
        }

    sponsorship = result.get("sponsorship", {})
    summaries = _sponsorship_context_summaries(result)
    eligible = int(sponsorship.get("eligible_strata", 0))
    if summaries:
        best, worst = summaries[0], summaries[-1]
        comparison = (
            f"Melhor contexto comparável: {_executive_context(best['context'])} "
            f"({signed(best['median_delta_erv_pp'], 3)} p.p.); pior contexto comparável: "
            f"{_executive_context(worst['context'])} ({signed(worst['median_delta_erv_pp'], 3)} p.p.)."
        )
        sponsor_strength = f"Força do melhor contexto: C={decimal(best['strength'], 3)}."
        sponsor_stability = (
            f"Estabilidade: {decimal(100 * best['stability'], 1)}% em {best['months']} meses."
            if best["months"] >= 3 else "Estabilidade: não mensurável; menos de três meses elegíveis no mesmo contexto."
        )
        sponsor_evidence = str(best["evidence_id"])
    else:
        comparison = "Nenhum contexto orgânico/patrocinado comparável."
        sponsor_strength = "Força: não mensurável."
        sponsor_stability = "Estabilidade: não mensurável."
        sponsor_evidence = str(sponsorship.get("evidence_id", "sem-evidência"))
    scenario_status = financial_scenario.get("status") if financial_scenario else None
    if scenario_status == "meets_break_even_scenario":
        sponsor_verdict = "CENÁRIO MANUAL ATINGE O EQUILÍBRIO; TESTAR, NÃO ESCALAR"
        sponsor_kpi = (
            f"Custo máximo de patrocínio: {decimal(financial_scenario['max_sponsorship_cost'], 2)}; "
            f"uplift mínimo: {decimal(financial_scenario['required_uplift_pp'], 3)} p.p."
        )
    elif scenario_status == "below_break_even_scenario":
        sponsor_verdict = "CENÁRIO MANUAL NÃO ATINGE O EQUILÍBRIO; NÃO INVESTIR"
        sponsor_kpi = f"Custo máximo de patrocínio: {decimal(financial_scenario['max_sponsorship_cost'], 2)}."
    else:
        sponsor_verdict = "NÃO ESCALAR PATROCÍNIO AGORA"
        sponsor_kpi = f"Cobertura comparável: {decimal(100 * float(sponsorship.get('coverage', 0)), 2)}%."
    sponsorship_answer = {
        "question": questions[1],
        "verdict": sponsor_verdict,
        "kpi": sponsor_kpi,
        "comparison": comparison,
        "sample": f"{eligible} estratos elegíveis; {count(sponsorship.get('uncovered_count', 0))} insuficientes; ROI observado indisponível.",
        "action": "Coletar custo/conversão e testar apenas o estrato selecionado antes de ampliar investimento.",
        "strength": sponsor_strength,
        "coverage": f"Cobertura: {decimal(100 * float(sponsorship.get('coverage', 0)), 2)}% dos posts.",
        "stability": sponsor_stability,
        "evidence_id": sponsor_evidence,
        "change_trigger": "A decisão mudaria somente com três meses estáveis, força suficiente e cenário financeiro abaixo do ponto de equilíbrio.",
    }

    program = content_strategy_30d(result)
    program_context = _executive_context(program["context"]) or "CONTEXTO A COLETAR"
    selected = leader or drivers.get("best_candidate") or {}
    strategy_verb = "EXECUTAR PROGRAMA DE 30 DIAS PARA" if leader else "EXECUTAR PROGRAMA DE 30 DIAS PARA VALIDAR"
    strategy = {
        "question": questions[2],
        "verdict": f"{strategy_verb} {program_context.upper()}; PRESERVAR O MIX FORA DO TESTE",
        "kpi": "4 semanas: baseline → teste → replicação/revisão → decisão humana.",
        "comparison": f"Contexto escolhido pelo ranking multivariado; escala automática: não; gate final: {'atingido' if program['scale_gate_met'] else 'não atingido'}.",
        "sample": f"Base: {count(posts)} posts; {len(program['weeks'])} janelas operacionais.",
        "action": "Executar D1–D30 com Gestor de Social Media responsável e registrar a decisão na semana 4.",
        "strength": f"Força herdada do driver: C={decimal(selected.get('strength', 0), 3)}.",
        "coverage": f"Cobertura: {selected.get('eligible_months', 0)} meses elegíveis no contexto selecionado.",
        "stability": f"Estabilidade herdada: {decimal(100 * selected.get('stability', 0), 1)}%.",
        "evidence_id": str(program["evidence_id"]),
        "change_trigger": "A decisão mudaria na semana 4 conforme força, materialidade, concordância temporal e guards de volume.",
    }

    audience_overviews = list(result.get("audience", []))
    audience_pairs = [
        pair
        for overview in audience_overviews
        for pair in overview.get("comparisons", [])
    ]
    max_coverage = max((float(item.get("coverage", 0)) for item in audience_overviews), default=0.0)
    total_eligible = sum(int(item.get("eligible_strata", 0)) for item in audience_overviews)
    total_strata = sum(int(item.get("total_strata", 0)) for item in audience_overviews)
    max_cell = max((int(item.get("max_cell_defined_rates", 0)) for item in audience_overviews), default=0)
    if audience_pairs:
        strongest = max(audience_pairs, key=lambda item: abs(float(item.get("delta_erv_pp", 0))))
        context = strongest["context"]
        audience = {
            "question": questions[3],
            "verdict": "NÃO HÁ PERFIL GLOBAL COMPROVADO; EXISTEM APENAS SINAIS CONTEXTUAIS",
            "kpi": f"Maior diferença contextual observada: {signed(strongest['delta_erv_pp'], 3)} p.p.",
            "comparison": (
                f"{context['target_label']} vs. {context['comparator_label']} em "
                f"{_executive_context(context)}; comparação observacional, não persona vencedora."
            ),
            "sample": (
                f"{count(strongest['target']['posts'])} vs. {count(strongest['comparator']['posts'])} posts; "
                f"{total_eligible}/{total_strata} estratos elegíveis."
            ),
            "action": "Usar o sinal somente como hipótese no mesmo contexto; não segmentar verba por persona global.",
            "strength": f"Força heurística C={decimal(strongest.get('strength', 0), 3)}.",
            "coverage": f"Cobertura controlada máxima por dimensão: {decimal(100 * max_coverage, 2)}%.",
            "stability": "Estabilidade: não mensurável entre meses no contrato atual.",
            "evidence_id": str(strongest["evidence_id"]),
            "change_trigger": "A decisão mudaria com pares elegíveis recorrentes no mesmo contexto e estabilidade temporal suficiente.",
        }
    else:
        audience = {
            "question": questions[3],
            "verdict": "NÃO HÁ PERFIL GLOBAL COMPROVADO; DADOS INSUFICIENTES PARA ELEGER UMA AUDIÊNCIA",
            "kpi": f"Cobertura controlada máxima por dimensão: {decimal(100 * max_coverage, 2)}%.",
            "comparison": "Idade, gênero e localização não formaram pares elegíveis dentro do mesmo contexto comparável.",
            "sample": f"{total_eligible}/{total_strata} estratos elegíveis; maior célula com {count(max_cell)} taxas definidas.",
            "action": "Coletar pares de audiência comparáveis; não inventar persona nem redistribuir verba por rótulo marginal.",
            "strength": "Força: não mensurável.",
            "coverage": f"Cobertura controlada máxima por dimensão: {decimal(100 * max_coverage, 2)}%.",
            "stability": "Estabilidade: não mensurável.",
            "evidence_id": str(audience_overviews[0].get("evidence_id", "sem-evidência")) if audience_overviews else "sem-evidência",
            "change_trigger": "A decisão mudaria quando dois rótulos no mesmo contexto tiverem ao menos 30 taxas e cinco creators por braço.",
        }
    return [engagement, sponsorship_answer, strategy, audience]


def executive_summary(
    result: dict[str, object],
    decisions: list[dict[str, object]],
    financial_scenario: dict[str, object] | None = None,
) -> str:
    source = dict(result.get("source", {}))
    source["source_hash"] = _short(source.get("source_hash", ""), 64)
    metrics = result.get("metrics", {})
    recommendations = result.get("recommendations", [])
    dimensions = [item for items in result.get("dimensions", {}).values() for item in items]
    priority_items = recommendations or result.get("pending", [])
    priorities = ""
    for item in priority_items[:3]:
        context = _short(" / ".join(str(value) for value in item.get("context", {}).values()), 150)
        cadence = item.get("frequency_hypothesis", {})
        compact = (f"{context}: {_short(item.get('action', item.get('reason', 'Coletar evidência')), 180)}. "
                   f"Prioridade {item.get('priority', 0):.6g}; força {item.get('priority_components', {}).get('strength', 0):.3g}; "
                   f"{_delta_text(item, 4)}. Responsável {_short(item.get('owner', 'Gestor'), 45)}; "
                   f"execução {_short(item.get('execution_window', 'coletar'), 45)}; revisão {_short(item.get('review_window', 'após coleta'), 45)}. "
                   f"Cadência observacional: {_short(cadence.get('value', 'N/A'), 20)} posts/creator/semana; estado {_short(cadence.get('status', 'collect'), 20)}. "
                   f"Evidência {_short(item.get('evidence_id', ''), 60)}.")
        priorities += f"<li>{html.escape(compact)}<details><summary>Detalhe auditável</summary>{html.escape(_recommendation_text(item))}</details></li>"
    findings = "".join(
        f"<li>{html.escape(_short(item.get('dimension', 'segmento'), 35))} = {html.escape(_short(item.get('value', ''), 80))}: {int(item.get('posts', 0))} posts; mediana ERv {format(float(item['median_erv']), '.2f') + '%' if item.get('median_erv') is not None else 'não definida (views=0: sem denominador para ERv)'} <small>{html.escape(_short(item.get('evidence_id', ''), 60))}</small></li>"
        for item in sorted(dimensions, key=lambda value: (-int(value.get("posts", 0)), str(value.get("evidence_id", ""))))[:5]
    )
    decisions_html = "".join(f"<li>{html.escape(line)}</li>" for line in _decision_lines(result, decisions))
    answers_html = "".join(
        "<article><h3>" + html.escape(item["question"]) + "</h3><strong>" + html.escape(item["verdict"]) +
        "</strong><p><b>KPI:</b> " + html.escape(item["kpi"]) + "</p><p><b>Comparação:</b> " + html.escape(item["comparison"]) +
        "</p><p><b>Amostra:</b> " + html.escape(item["sample"]) + "</p><p><b>Ação:</b> " + html.escape(item["action"]) +
        "</p><details><summary>Confiança, critério de mudança e evidência</summary><p>" + html.escape(item["strength"]) +
        "</p><p>" + html.escape(item["coverage"]) + "</p><p>" + html.escape(item["stability"]) + "</p><p>" +
        html.escape(item["change_trigger"]) + "</p><small>" + html.escape(item["evidence_id"]) + "</small></details></article>"
        for item in executive_answers(result, financial_scenario)
    )
    program = content_strategy_30d(result)
    strategy_html = "".join(
        f"<tr><td>{week['week']}</td><td>{html.escape(week['window'])}</td><td>{html.escape(week['owner'])}</td>"
        f"<td>{html.escape(week['action'])}</td><td>{html.escape(week['metric'])}</td>"
        f"<td>{html.escape(week['cadence'])}</td><td>{html.escape(week['gate'])}</td></tr>"
        for week in program["weeks"]
    )
    warnings = " ".join(_short(item.get("message", ""), 160) for item in result.get("quality", {}).get("warnings", [])[:2])
    state = result.get("analysis_state", {})
    if state.get("has_observations", metrics.get("posts", 0) > 0):
        kpis = (f"<b>{int(metrics.get('posts', 0))} posts</b><b>{int(metrics.get('views', 0))} views</b>"
                f"<b>{int(metrics.get('interactions', 0))} interações</b>")
    else:
        kpis = f"<b>{html.escape(str(state.get('message', 'Nenhum registro corresponde ao recorte.')))}</b>"
    return f"""<!doctype html><html lang=\"pt-BR\"><head><meta charset=\"utf-8\"><title>Resumo executivo social</title><style>@page{{size:A4;margin:12mm}}body{{font:14px system-ui;max-width:900px;margin:auto;color:#17202a;overflow-wrap:anywhere}}h1,h2{{margin:.5em 0}}h3{{margin:.2em 0}}small{{color:#566}}.kpi{{display:flex;gap:2rem}}.answers{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}}.answers article{{border:1px solid #9aa;padding:12px}}.answers strong{{display:block}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #9aa;padding:6px;text-align:left;vertical-align:top}}li{{margin:.25em 0}}@media print{{body{{font-size:10px}}h1{{font-size:20px}}h2{{font-size:14px}}details{{display:none}}}}</style></head><body><h1>Resumo executivo social</h1><p>Fonte {html.escape(str(source.get('source_hash', '')))} · {int(source.get('rows', 0))} linhas</p><p>{html.escape(_short(_scope_text(result), 650))}</p><div class=\"kpi\">{kpis}</div><h2>Quatro respostas obrigatórias do challenge</h2><section class=\"answers\">{answers_html}</section><h2>Estratégia de conteúdo — 30 dias</h2><table><thead><tr><th>Semana</th><th>Janela</th><th>Responsável</th><th>Ação</th><th>Métrica</th><th>Cadência</th><th>Gate</th></tr></thead><tbody>{strategy_html}</tbody></table><p><b>Regra:</b> preservar o mix fora dos testes; nenhuma publicação ou verba é executada automaticamente.</p><h2>Prioridades</h2><ol>{priorities}</ol><p><small>Atualidade = 2^(−idade em dias/7); o histórico completo pode gerar scores muito pequenos, não oportunidades atuais. Ordem e componentes completos no CSV.</small></p><h2>Evidências e cobertura</h2><ul>{findings}</ul><p>{html.escape(_coverage_text(result))} {html.escape(warnings)}</p><h2>Decisões recentes desta fonte</h2><ul>{decisions_html}</ul><p>Textos longos abreviados com …; detalhes integrais no CSV. <b>Limite:</b> associação observacional; sem investimento, receita ou conversão não há ROI financeiro nem causalidade.</p></body></html>"""


def analysis_report(
    result: dict[str, object],
    decisions: list[dict[str, object]] | None = None,
    financial_scenario: dict[str, object] | None = None,
) -> str:
    """Render the standalone strategy from the same evidence and queue as HTML/CSV."""
    source, scope, metrics = result["source"], result["scope"], result["metrics"]
    summary_id = _stable_id("summary", str(source["source_hash"]), scope)
    sponsorship = result.get("sponsorship", {})
    overview_id = sponsorship.get("evidence_id", "")
    state = result.get("analysis_state", {})

    def text(value: object) -> str:
        return html.escape(str(value)).replace("|", "\\|").replace("\n", " ").replace("\r", " ")

    def number(value: object) -> str:
        return "não definida" if value is None else f"{float(value):.6g}"

    if state.get("has_observations", metrics.get("posts", 0) > 0):
        performance_summary = (
            f"{metrics.get('posts', 0)} posts; {metrics.get('creators', 0)} creators; "
            f"{metrics.get('views', 0)} views; {metrics.get('interactions', 0)} interações. "
            f"Mediana ERv: {number(metrics.get('median_erv'))}{'%' if metrics.get('median_erv') is not None else ''}; "
            f"ERv ponderado: {number(metrics.get('weighted_erv'))}{'%' if metrics.get('weighted_erv') is not None else ''}. "
            f"Proporção de posts com zero interação: {number(metrics.get('zero_interaction_share'))}; "
            f"taxas indefinidas: {metrics.get('undefined_rates', 0)}. Evidência: `{summary_id}`."
        )
    else:
        performance_summary = (
            f"{state.get('message', 'Nenhum registro corresponde ao recorte.')} "
            f"Métricas de performance não definidas para este recorte. Evidência: `{summary_id}`."
        )

    lines = ["# Estratégia Social Media — Challenge 004", "", "## Quatro respostas obrigatórias do challenge", ""]
    for item in executive_answers(result, financial_scenario):
        lines += [f"### {text(item['question'])}", "", f"**{text(item['verdict'])}**", "",
                  f"- KPI: {text(item['kpi'])}", f"- Comparação: {text(item['comparison'])}",
                  f"- Amostra: {text(item['sample'])}", f"- Ação: {text(item['action'])}",
                  f"- {text(item['strength'])}", f"- {text(item['coverage'])}",
                  f"- {text(item['stability'])}", f"- Muda se: {text(item['change_trigger'])}",
                  f"- Evidência: `{text(item['evidence_id'])}`", ""]
    program = content_strategy_30d(result)
    lines += ["## Estratégia de conteúdo — 30 dias", "",
              "| Semana | Janela | Responsável | Ação | Métrica | Cadência | Gate |",
              "|---:|---|---|---|---|---|---|"]
    for week in program["weeks"]:
        lines.append(
            f"| {week['week']} | {text(week['window'])} | {text(week['owner'])} | {text(week['action'])} | "
            f"{text(week['metric'])} | {text(week['cadence'])} | {text(week['gate'])} |"
        )
    lines += ["", "Preservar o mix fora dos testes; nenhuma publicação ou verba é executada automaticamente.", "",
             "## Decisão para segunda-feira", "",
             "Fila única: o top 3 abaixo vem de `result[recommendations]`, na mesma ordem do HTML e do início do CSV; "
             "o CSV preserva a fila completa `result[all_recommendations]`, incluindo as demais ações decidíveis na UI. "
             "São propostas para decisão humana; não executam gasto, publicação ou interrupção.", ""]
    for rank, item in enumerate(result.get("recommendations") or result.get("pending", []), 1):
        lines.append(f"{rank}. {text(_recommendation_text(item))}")
    lines += ["", RECENCY_NOTE, "",
              "Força limitada (<0,40) exige coleta/teste, sem ampliação de investimento. "
              "As janelas de execução/revisão são propostas futuras, não datas de performance observada.", "",
              "## O que os dados permitem afirmar", "",
              text(_scope_text(result)), "", text(_coverage_text(result)), "",
              *[text(item.get("message", "")) for item in result.get("quality", {}).get("warnings", [])], "",
              "### Decisões recentes desta fonte", "",
              *[f"- {text(line)}" for line in _decision_lines(result, decisions or [])], "",
              performance_summary, "",
              "ERv = 100 × (likes + shares + comments_count) / views; views=0 deixa a taxa indefinida e preserva volume. "
              "A mediana usa taxas por post; a taxa ponderada usa totais apenas onde views>0. "
              "Views não são alcance único; interações não são pessoas únicas.", "",
              "## Plataforma, conteúdo, categoria, creators, audiência e tempo", "",
              "As tabelas descrevem cada recorte; não criam uma segunda fila de prioridades. "
              "Diferenças pequenas de taxa, sem comparação controlada, não justificam redistribuir o mix. "
              "Idade, gênero e localização são rótulos de posts, não percentuais ou personas. "
              "Estas marginais não identificam vencedores: a análise condicionada e sua cobertura aparecem abaixo. "
              "Bilibili e RedNote permanecem no escopo junto a Instagram, TikTok e YouTube.", ""]
    labels = {"platform": "Plataforma", "content_type": "Formato", "content_category": "Categoria",
              "creator_band": "Faixa de seguidores", "audience_age": "Idade", "audience_gender": "Gênero",
              "audience_location": "Localização", "month": "Mês"}
    for dimension, items in result.get("dimensions", {}).items():
        lines += [f"### {labels.get(dimension, dimension)}", "",
                  "| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |",
                  "|---|---:|---:|---:|---:|---:|---|"]
        for item in items:
            lines.append(f"| {text(item['value'])} | {item.get('posts', 0)} | {item.get('creators', 0)} | "
                         f"{item.get('views', 0)} | {item.get('interactions', 0)} | "
                         f"{number(item.get('median_erv'))} | `{item['evidence_id']}` |")
        lines.append("")
    lines += ["## Audiência condicionada: elegibilidade, efeito e cobertura", "",
              "Para cada rótulo de idade, gênero ou localização, comparamos pares dentro da mesma plataforma, "
              "formato, categoria, faixa de seguidores, mês-calendário e estado de patrocínio. Cada rótulo precisa "
              "de 30 taxas definidas e cinco creators. O efeito é mediana ERv do alvo menos mediana do comparador; "
              "taxa é acompanhada de volume e amostra. As demais dimensões de audiência não são controladas: "
              "associação descritiva, não efeito causal, persona ou vencedor geral. Sem dois rótulos elegíveis, "
              "a resposta é insuficiência quantificada, não uma preferência por público.", "",
              "| Dimensão | Estratos elegíveis/total | Células elegíveis/total | Maior amostra de taxas por célula | Posts cobertos/total | Cobertura | Evidência |",
              "|---|---:|---:|---:|---:|---:|---|"]
    for audience in result.get("audience", []):
        lines.append(f"| {text(audience['dimension'])} | {audience['eligible_strata']}/{audience['total_strata']} | "
                     f"{audience['eligible_cells']}/{audience['total_cells']} | {audience['max_cell_defined_rates']} | "
                     f"{audience['covered_posts']}/{audience['posts']} | {100 * audience['coverage']:.6g}% | `{audience['evidence_id']}` |")
        for pair in audience["comparisons"]:
            target, comparator = pair["target"], pair["comparator"]
            lines.append(f"\nComparação observacional {text(json.dumps(pair['context'], ensure_ascii=False, sort_keys=True))}: "
                         f"ΔERv {pair['delta_erv_pp']:+.6g} p.p.; força {pair['strength']:.6g}; "
                         f"alvo/comparador: {target['n_rate']}/{comparator['n_rate']} taxas, "
                         f"{target['creators']}/{comparator['creators']} creators, {target['views']}/{comparator['views']} views, "
                         f"{target['interactions']}/{comparator['interactions']} interações. Evidência `{pair['evidence_id']}`.\n")
    lines += ["", "## Patrocínio e o que não funciona", "",
              f"{sponsorship.get('eligible_strata', 0)} estratos elegíveis; {sponsorship.get('uncovered_count', 0)} "
              f"sem amostra/contraparte suficiente; cobertura de {100 * sponsorship.get('coverage', 0):.6g}% dos posts. "
              f"Evidência: `{overview_id}`.", "",
              "Controle: mesma plataforma, formato, categoria, faixa de creator e mês-calendário. "
              "Cada mês exige contrapartes contemporâneas; orgânicos de um mês não são comparados a patrocinados de outro. "
              "Cada braço exige 30 taxas definidas e cinco creators; o efeito é a diferença entre "
              "medianas das medianas de ERv por creator. Cobertura baixa restringe as conclusões aos meses/contextos elegíveis; "
              "não sustenta uma política geral de patrocínio. Patrocínio é associação observacional, não causalidade. "
              "Custo implícito e retorno financeiro não podem ser calculados: faltam investimento, "
              "custo de produção, receita/conversão. Nenhum threshold de seguidores justifica desembolso sozinho.", ""]
    strata = sponsorship.get("strata", [])
    if strata:
        for label, item in (("Menor associação de ERv", min(strata, key=lambda item: item["delta_erv_pp"])),
                            ("Maior associação de ERv", max(strata, key=lambda item: item["delta_erv_pp"]))):
            organic, sponsored = item["organic"], item["sponsored"]
            lines += [f"{label}: {text(' / '.join(str(value) for value in item['context'].values()))}; "
                      f"ΔERv {item['delta_erv_pp']:+.6g} p.p.; força {item['strength']:.6g}; "
                      f"orgânicos/patrocinados: {organic['posts']}/{sponsored['posts']} posts, "
                      f"{organic['views']}/{sponsored['views']} views, "
                      f"{organic['interactions']}/{sponsored['interactions']} interações. "
                      f"Evidência: `{item['evidence_id']}`.", ""]
    lines += ["Esses extremos são achados descritivos, não prioridades adicionais nem ordens para suspender renovação. "
              "Sinal negativo isolado ou força insuficiente exige investigação; interromper investimento requer "
              "sinais concordantes, evidência forte e decisão humana. Ausência de zeros observados, quando indicada "
              "acima, limita a avaliação do fracasso: não prova inexistência de posts sem engajamento.", "",
              "## Estratégia operacional e quick wins", "",
              "Responsável sugerido: Gestor de Social Media. Executar nos próximos 7 dias; revisar 7 dias "
              "após cada teste. A estratégia abaixo aplica a fila inicial, sem reordená-la.", "",
              "| Tema | Ação | Critério de revisão |", "|---|---|---|",
              "| Esforço e quick win | Preparar briefs dos contextos da fila na ordem exibida; anexar a evidência e registrar aceitar/rejeitar/editar. | Rever ERv, views e interações por post no mesmo contexto. |",
              "| Público e creators | Preservar rótulos de audiência e faixa de creator do contexto; coletar se faltarem controles. Não inferir uma persona ou threshold de contratação. | Pelo menos 30 taxas e cinco creators por braço; declarar composição e concentração. |",
              "| Frequência | Testar a mediana observada de posts/creator/semana completa indicada em cada prioridade; estado collect pede coleta antes de propor cadência. | Comparar janelas equivalentes; hipótese observacional, não frequência ótima ou efeito causal. Ausência de linha não equivale a zero. |",
              "| Patrocínio | Obter custos reais antes de avaliar desembolso; força limitada pede coleta/teste. | ERv e volume concordantes, grupo comparável e dados financeiros. |",
              "| Parar/revisar | Revisar repetição de padrões negativos; não parar por média global ou sinal isolado. | Interrupção exige a guarda do motor e decisão humana; sem base, coletar. |", "",
              "## Auditabilidade e limites", "",
              f"Fonte SHA-256: `{source['source_hash']}`; método `{scope.get('method_version', METHOD_VERSION)}`. "
              "Cada evidência está em [evidence.csv](./evidence.csv), com escopo, fórmula e referências.", "",
              "Regeração conjunta: `python3 analysis.py /caminho/social_media_dataset.csv --evidence evidence.csv "
              "--summary summary.html --report analysis.md`.", "",
              "Linhas `recommendation` preservam `rank`, score, impacto, força, atualidade, valores originais "
              "V/I/F, denominadores P95, diferença, data representativa, ação, responsável e janelas. "
              "Impacto = média de min(V/P95_V,1), min(I/P95_I,1), min(F/P95_F,1); "
              "prioridade = 100 × impacto × força × atualidade. Scores são relativos à plataforma/tipo/unidade, "
              "não monetários. P95=0 usa máximo positivo ou zero se inexistente.", "",
              "A coluna JSON `frequency_hypothesis` preserva status, valor/unidade, método, amostra de creator-semanas/creators, "
              "mês (`period_month`), regra (`coverage_rule`), semanas completas disponíveis/observadas, janela, ação, mínimo de semanas para coleta e limitação. "
              "No patrocínio mensal, entram apenas semanas ISO completas inteiramente dentro do mês e do escopo; "
              "semanas que atravessam a fronteira mensal ficam fora. Sem mês fixo, vale a cobertura completa do escopo. "
              "O valor é uma hipótese de teste no mesmo contexto da recomendação, não promessa de desempenho.", "",
              "Em `source_ref`, agrupar por `evidence_id` e `reference_role` (target/comparator) e ordenar por `reference_chunk` (base 1). "
              "`source_row_id`, `source_line` e `reference_index` são arrays JSON paralelos, em blocos de até 500 entradas "
              "e 32.768 caracteres no campo de IDs, legíveis pelo limite padrão do csv.reader. "
              "O índice identifica o registro dentro da evidência (base 0); concatenar fragmentos de ID com o mesmo "
              "`reference_index`, conservando a linha física inicial (base 1). IDs acima de 4.096 caracteres "
              "são fragmentados sem perder conteúdo. Reconstituir a chave completa com `source_hash + ':' + ID`. "
              "Campos multilinha contam todas as linhas físicas; células de texto neutralizam fórmulas de planilha.", "",
              "Linhas `evidence_detail` projetam estatísticas do alvo/comparador, incluindo quartis, amostra, fallback "
              "e controles removidos de benchmarks; no editorial, target=current e comparator=previous. "
              "`statistics` preserva os números completos. `quality`, `warning`, `benchmark_diagnostic` e "
              "`sponsorship_uncovered` conservam diagnósticos sem reunir milhares de contextos numa célula. "
              "Campos analíticos acima de 32.768 caracteres ficam vazios na linha-base e são reconstruídos por "
              "`analysis_field`: agrupar evidence_id/reference_role/field_name, ordenar field_chunk e concatenar "
              "json.loads(field_value); field_name tem formato record_type.campo para evitar colisões entre evidência e recomendação. "
              "O mesmo princípio vale para `history_field` no histórico, usando decision_id/outcome_id. "
              "A barreira final também limita campos/metadados de qualquer linha. Se necessário, emite `export_field`: "
              "evidence_id=export-row-N aponta para a N-ésima linha-base (base 1, excluindo export_field); "
              "agrupar por essa chave/field_name e concatenar json.loads(field_value) na ordem field_chunk. "
              "Reconstruir essa camada primeiro, depois analysis_field/history_field; campos normais não mudam. "
              "A neutralização de fórmulas é preservada no texto recomposto.", "",
              "A CLI publica todo o histórico, sem alertas post a post. Ausência de período anterior igualmente "
              "longo pode impedir comparações editoriais; não se inventa tendência. O monitoramento recente "
              "pode produzir outra fila porque tem outro escopo. Não há unidade confirmada de content_length, "
              "causalidade, ROI ou resultados futuros inferidos.", ""]
    return "\n".join(lines)


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
        Path(temporary).replace(path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gera evidências sociais reproduzíveis")
    parser.add_argument("input", type=Path)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--report", type=Path, help="Relatório Markdown da mesma análise")
    args = parser.parse_args(argv)
    try:
        raw = args.input.read_bytes()
    except OSError as exc:
        print(f"input_error: {exc}", file=sys.stderr)
        return 2
    frame, errors = load_csv(raw)
    if errors or frame is None:
        print(json.dumps(errors, ensure_ascii=False), file=sys.stderr)
        return 2
    source_hash = hashlib.sha256(raw).hexdigest()
    result = analyze(frame, {"target_start": min(frame["post_date"]).isoformat(), "target_end": max(frame["post_date"]).isoformat(), "reference_date": max(frame["post_date"]).isoformat(), "filters": {}, "strict_audience": False, "include_post_alerts": False, "method_version": METHOD_VERSION}, source_hash)
    _atomic_write(args.evidence, export_evidence(result, []))
    _atomic_write(args.summary, executive_summary(result, []).encode("utf-8"))
    if args.report:
        _atomic_write(args.report, analysis_report(result).encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
