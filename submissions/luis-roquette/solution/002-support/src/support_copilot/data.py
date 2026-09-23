"""Sanitized domain boundaries and reproducible development partitions.

Regexes cannot establish universal anonymity. Suspicious text is rejected, and
public examples still require human inspection. Final-test frames expose IDs only.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import re
import tempfile
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypedDict

import pandas as pd

Domain = Literal["customer", "it"]
SANITIZER_VERSION = "conservative-v2"
GROUPING_VERSION = "canonical-v1"
ANALYTICS_SCHEMA_VERSION = "structured-operational-v1"
IT_TAXONOMY = (
    "Access", "Administrative rights", "HR Support", "Hardware", "Internal Project",
    "Miscellaneous", "Purchase", "Storage",
)
CUSTOMER_TAXONOMY = (
    "Billing inquiry", "Cancellation request", "Product inquiry", "Refund request",
    "Technical issue",
)
CUSTOMER_COLUMNS = (
    "Ticket ID", "Customer Name", "Customer Email", "Customer Age", "Customer Gender",
    "Product Purchased", "Date of Purchase", "Ticket Type", "Ticket Subject",
    "Ticket Description", "Ticket Status", "Resolution", "Ticket Priority", "Ticket Channel",
    "First Response Time", "Time to Resolution", "Customer Satisfaction Rating",
)
OPERATIONAL_COLUMNS = (
    "Ticket Status", "Ticket Priority", "Ticket Channel", "First Response Time",
    "Time to Resolution", "Customer Satisfaction Rating",
)
SOURCES = {
    "customer": (
        "customer_support_tickets.csv",
        "https://www.kaggle.com/api/v1/datasets/download/suraj520/customer-support-ticket-dataset",
    ),
    "it": (
        "all_tickets_processed_improved_v3.csv",
        "https://www.kaggle.com/api/v1/datasets/download/adisongoh/"
        "it-service-ticket-classification-dataset",
    ),
}
EMAIL = re.compile(r"[\w.+-]+@[\w.-]+\.[\w-]+", re.UNICODE)
PHONE = re.compile(r"(?<!\w)\+?\d[\d\s().-]{6,}\d(?!\w)")
NAME_CUE = re.compile(
    r"\b(?:my name is|i am|i'm|sou|me chamo|meu nome [ée]|contact|dear|regards|"
    r"sincerely|attn|mr\.?|mrs\.?|ms\.?|dr\.?)\s+([\wÀ-ÿ'-]+)", re.I,
)
SAFE_CUE_WORDS = frozenset(
    "having unable experiencing writing requesting trying using not still a an the support "
    "team customer agent user administrator [name]".split()
)
CAPITAL_PAIR = re.compile(r"\b[A-ZÀ-Ý][a-zà-ÿ]+(?:[ '-]+[A-ZÀ-Ý][a-zà-ÿ]+)+\b")
# This small allowlist describes products/operations, never personal names.
SAFE_PHRASES = frozenset({
    "Customer Support", "Technical Support", "Support Team", "Windows Update",
    "Microsoft Office", "Microsoft Teams", "Google Drive", "Active Directory",
    "Service Desk", "Help Desk", "Thank You", "Best Regards",
})
SAFE_CAPITAL_WORDS = frozenset(
    "a an the i we it my our your this that these those please thank thanks hello hi dear "
    "regards best sincerely after before when since if can could would should will have has "
    "help issue problem error unable cannot device computer laptop printer phone account "
    "access request reset password software hardware network storage billing refund cancel "
    "customer support technical team service desk windows microsoft google linux mac apple "
    "android office outlook excel word teams chrome firefox vpn usb cpu ram ssd hr it id "
    "closed open pending low medium high critical".split()
)


class SourceManifest(TypedDict):
    filename: str
    sha256: str
    schema: list[str]
    allowed_columns: list[str]
    total_rows: int
    quality: dict
    data_version: str
    sanitizer_version: str


class SplitManifest(TypedDict):
    seed: int
    strategy: str
    split_version: str
    status: str
    partitions: dict
    counts_by_class: dict
    exclusions: dict


class ModelManifest(TypedDict):
    status: str
    reason: str
    candidate: str | None
    features: list[str]
    taxonomy: list[str]
    cv: dict | None
    calibration: dict | None
    model_version: str | None
    automation_enabled: bool
    threshold: float | None
    configuration_lock_sha256: str | None


class RetrievalManifest(TypedDict):
    status: str
    reason: str
    reference_split: str | None
    index_version: str | None
    policy_version: str | None
    packet_ids: list[str]
    rubric_sha256: dict
    lock_sha256: str | None
    threshold: float | None
    eligible_queries: int | None
    reviewed_queries: int


class ArtifactEntry(TypedDict):
    path: str | None
    type: str
    schema_version: int
    sha256: str | None
    logical_sha256: str | None
    domain: Domain | None
    dependencies: list[str]
    status: Literal["ready", "unavailable"]
    reason: str | None


class Manifest(TypedDict):
    schema_version: int
    generated_at: str
    code_revision: str
    configuration_sha256: str
    lock_sha256: str
    runtime: dict
    sources: dict[Domain, SourceManifest]
    splits: dict[Domain, SplitManifest]
    models: dict[Domain, ModelManifest]
    retrieval: RetrievalManifest
    artifacts: dict[str, ArtifactEntry]


def canonical_json(value: object) -> bytes:
    try:
        return (json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                           separators=(",", ":")) + "\n").encode("utf-8")
    except (TypeError, ValueError):
        raise ValueError("invalid_json: finite JSON values required") from None


def content_hash(value: object) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def sanitize_text(value: str | None, names: Sequence[str] = ()) -> str:
    """Mask known PII; reject suspected remaining names without echoing input."""
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError("invalid_type:text")
    text = unicodedata.normalize("NFKC", value)
    text = EMAIL.sub("[EMAIL]", text)
    text = PHONE.sub("[PHONE]", text)
    for name in sorted({n.strip() for n in names if isinstance(n, str) and n.strip()},
                       key=lambda n: (-len(n), n)):
        tokens = [name, *[part for part in re.split(r"\W+", name) if len(part) > 1]]
        for token in tokens:
            text = re.sub(r"(?<!\w)" + re.escape(token) + r"(?!\w)", "[NAME]", text,
                          flags=re.I)
    text = re.sub(r"https?://\S+|www\.\S+", "[URL]", text, flags=re.I)
    text = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "[IP]", text)
    text = re.sub(r"\b(?=\w*[a-zA-Z])(?=\w*\d)\w+\b", "[IDENTIFIER]", text)
    # Validate exactly the text downstream consumers receive. Joining whitespace AFTER
    # these checks could create a newly suspicious name pair across a line break.
    text = " ".join(text.split())
    # Quarantine residual named entities; false positives are safer than publishing PII.
    if any(match.group() not in SAFE_PHRASES for match in CAPITAL_PAIR.finditer(text)):
        raise ValueError("privacy_quarantine:suspected_name")
    if any(match.group(1).casefold() not in SAFE_CUE_WORDS
           for match in NAME_CUE.finditer(text)):
        raise ValueError("privacy_quarantine:suspected_name")
    unmasked = re.sub(r"\[[A-Z]+\]", "", text)
    if any(word.casefold() not in SAFE_CAPITAL_WORDS
           for word in re.findall(r"\b[A-ZÀ-Ý][a-zà-ÿ]+\b", unmasked)):
        raise ValueError("privacy_quarantine:unrecognized_entity")
    if re.search(r"\b(?:address|cpf|ssn|passport|account number|credit card)\s*[:#]", text, re.I):
        raise ValueError("privacy_quarantine:identifier")
    return text


def canonical_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold()
    text = re.sub(r"\[[a-z]+\]|\b\w*\d\w*\b|\bx{3,}\b", " variable ", text)
    return " ".join(re.sub(r"[^\w\s]", " ", text).split())


def _text_group(text: str, domain: Domain) -> str:
    return f"{domain}:group:{content_hash(canonical_text(text))}"


def _read(path: Path, domain: Domain, columns: Sequence[str]) -> tuple[pd.DataFrame, str]:
    if not path.is_file():
        filename, url = SOURCES[domain]
        raise ValueError(
            f"source_missing:{domain}; download ZIP {url}; extract {filename}; "
            f"place at data/raw/{filename}"
        )
    try:
        raw = path.read_bytes()
        # Read as strings; downstream conversion never prints source values.
        frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    except (OSError, UnicodeError, pd.errors.ParserError, pd.errors.EmptyDataError):
        raise ValueError(f"source_unreadable:{domain}") from None
    if set(frame.columns) != set(columns):
        raise ValueError(f"schema_mismatch:{domain}")
    return frame, hashlib.sha256(raw).hexdigest()


def _validate_customer_frame(frame: pd.DataFrame) -> None:
    if not set(CUSTOMER_COLUMNS).issubset(frame.columns):
        raise ValueError("schema_mismatch:customer")
    ids = frame["Ticket ID"].astype(str)
    if not ids.str.fullmatch(r"[1-9]\d*").all() or ids.duplicated().any():
        raise ValueError("invalid_or_duplicate_id:customer")
    if not frame["Ticket Type"].isin(CUSTOMER_TAXONOMY).all():
        raise ValueError("invalid_taxonomy:customer")
    for column, allowed in {
        "Ticket Status": {"Open", "Pending Customer Response", "Closed"},
        "Ticket Priority": {"Low", "Medium", "High", "Critical"},
        "Ticket Channel": {"Email", "Phone", "Chat", "Social media"},
    }.items():
        if not frame[column].isin(allowed).all():
            raise ValueError(f"invalid_enum:{column}")


def sanitize_customer_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Textual lane: quarantine a row when either description or resolution is unsafe."""
    _validate_customer_frame(frame)
    records = []
    excluded = {"privacy_quarantine": 0, "empty_text": 0}
    for row in frame.to_dict("records"):
        try:
            text = sanitize_text(row["Ticket Description"], [row["Customer Name"]])
            resolution = sanitize_text(row["Resolution"] or None, [row["Customer Name"]])
        except ValueError:
            excluded["privacy_quarantine"] += 1
            continue
        if not text:
            excluded["empty_text"] += 1
            continue
        record = {column: row[column] or None for column in OPERATIONAL_COLUMNS}
        record.update(ticket_id=f"customer:{row['Ticket ID']}", domain="customer", text=text,
                      target=row["Ticket Type"], text_group_id=_text_group(text, "customer"),
                      resolution=resolution or None)
        records.append(record)
    result = pd.DataFrame(records, columns=[*OPERATIONAL_COLUMNS, "ticket_id", "domain", "text",
                                            "target", "text_group_id", "resolution"])
    quality = _clean_operational_fields(result)
    result.attrs["quality"] = {
        "input_rows": len(frame), "sanitized_rows": len(result), "excluded": excluded,
        **quality, "public_sample_review": "pending_human_review",
    }
    return result


def _clean_operational_fields(result: pd.DataFrame) -> dict:
    """Normalize allowlisted fields without retaining arbitrary source values."""
    invalid_timestamps = {}
    for column in ("First Response Time", "Time to Resolution"):
        parsed = pd.to_datetime(result[column], errors="coerce", format="mixed", utc=True)
        invalid = result[column].notna() & parsed.isna()
        invalid_timestamps[column] = int(invalid.sum())
        # Preserve an invalid sentinel for analytics, never arbitrary raw field contents.
        result[column] = [None if value is None else "[INVALID_TIMESTAMP]" if bad_date
                          else stamp.isoformat()
                          for value, bad_date, stamp in zip(result[column], invalid, parsed,
                                                            strict=True)]
    ratings = pd.to_numeric(result["Customer Satisfaction Rating"], errors="coerce")
    bad = result["Customer Satisfaction Rating"].notna() & (
        ratings.isna() | ~ratings.between(1, 5) | (ratings % 1 != 0)
    )
    result["satisfaction_status"] = [
        "invalid" if invalid else "missing" if pd.isna(rating) else "valid"
        for invalid, rating in zip(bad, ratings, strict=True)
    ]
    result["Customer Satisfaction Rating"] = ratings.where(~bad).astype(object)
    result.loc[ratings.isna() | bad, "Customer Satisfaction Rating"] = None
    return {
        "invalid_satisfaction": int(bad.sum()),
        "missing_satisfaction": int((result["satisfaction_status"] == "missing").sum()),
        "invalid_timestamps": invalid_timestamps,
    }


def sanitize_customer_analytics_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Structured lane: keep operational rows independently of free-text quarantine.

    Never copy free text, demographics, products, or contact fields into this lane.
    Ticket type is an observed diagnostic dimension, not a textual training target here.
    """
    _validate_customer_frame(frame)
    result = frame.loc[:, list(OPERATIONAL_COLUMNS)].astype(object).replace("", None)
    result = result.where(result.notna(), None)
    result["ticket_id"] = "customer:" + frame["Ticket ID"].astype(str)
    result["domain"] = "customer"
    result["target"] = frame["Ticket Type"]
    quality = _clean_operational_fields(result)
    result = result.sort_values("ticket_id").reset_index(drop=True)
    result.attrs = {
        "domain": "customer", "lane": "structured_operational",
        "quality": {
            "input_rows": len(frame), "sanitized_rows": len(result), "excluded": {},
            "text_fields_retained": False, **quality,
        },
    }
    return result


def _source(frame: pd.DataFrame, domain: Domain, sha256: str, total: int,
            schema: Sequence[str]) -> pd.DataFrame:
    frame.attrs["domain"] = domain
    frame.attrs["source"] = {
        "filename": SOURCES[domain][0], "sha256": sha256, "schema": list(schema),
        "allowed_columns": list(frame.columns), "total_rows": total,
        "quality": frame.attrs["quality"], "sanitizer_version": SANITIZER_VERSION,
        "data_version": content_hash([domain, sha256, list(schema), SANITIZER_VERSION,
                                      GROUPING_VERSION]),
    }
    return frame


def load_customer_tickets(path: Path) -> pd.DataFrame:
    frame, sha256 = _read(path, "customer", CUSTOMER_COLUMNS)
    return _source(sanitize_customer_frame(frame), "customer", sha256, len(frame), CUSTOMER_COLUMNS)


def load_customer_analytics(path: Path) -> pd.DataFrame:
    """Load observed structured Customer data; never route this frame into textual splits."""
    raw, sha256 = _read(path, "customer", CUSTOMER_COLUMNS)
    result = _source(sanitize_customer_analytics_frame(raw), "customer", sha256,
                     len(raw), CUSTOMER_COLUMNS)
    result.attrs["source"].update({
        "lane": "structured_operational", "sanitizer_version": ANALYTICS_SCHEMA_VERSION,
        "data_version": content_hash([
            "customer", sha256, list(CUSTOMER_COLUMNS), ANALYTICS_SCHEMA_VERSION,
            list(result.columns),
        ]),
    })
    return result


def load_it_tickets(path: Path) -> pd.DataFrame:
    frame, sha256 = _read(path, "it", ("Document", "Topic_group"))
    if set(frame["Topic_group"]) != set(IT_TAXONOMY):
        raise ValueError("invalid_taxonomy:it_expected_eight_classes")
    records = []
    excluded = {"privacy_quarantine": 0, "empty_text": 0}
    for ordinal, row in enumerate(frame.to_dict("records")):
        try:
            text = sanitize_text(row["Document"])
        except ValueError:
            excluded["privacy_quarantine"] += 1
            continue
        if not text:
            excluded["empty_text"] += 1
            continue
        records.append({
            "ticket_id": f"it:{content_hash([sha256, ordinal, row['Document']])}",
            "domain": "it", "text": text, "target": row["Topic_group"],
            "text_group_id": _text_group(text, "it"),
        })
    result = pd.DataFrame(
        records, columns=["ticket_id", "domain", "text", "target", "text_group_id"]
    )
    result.attrs["quality"] = {
        "input_rows": len(frame), "sanitized_rows": len(result), "excluded": excluded,
        "public_sample_review": "pending_human_review",
    }
    return _source(result, "it", sha256, len(frame), ("Document", "Topic_group"))


@dataclass(frozen=True)
class DatasetSplit:
    domain: Domain
    train: pd.DataFrame
    calibration: pd.DataFrame
    test: pd.DataFrame  # IDs/groups ONLY until the later, validated policy lock.
    split_version: str
    calibration_fit: pd.DataFrame
    policy_selection: pd.DataFrame
    manifest: SplitManifest


def make_split(frame: pd.DataFrame, target: str, random_state: int = 42) -> DatasetSplit:
    if frame.attrs.get("lane") == "structured_operational":
        raise ValueError("split_forbidden:structured_analytics")
    required = {"ticket_id", "domain", "text", "text_group_id", target}
    if not required.issubset(frame.columns):
        raise ValueError("split_schema_mismatch")
    domains = set(frame["domain"]) or {frame.attrs.get("domain")}
    if len(domains) != 1 or not domains <= {"customer", "it"}:
        raise ValueError("split_domain_mismatch")
    domain = next(iter(domains))
    if frame["ticket_id"].duplicated().any() or frame[list(required)].isna().any().any():
        raise ValueError("split_invalid_ids_or_values")
    data = frame.sort_values("ticket_id").copy()
    data = data.reset_index(drop=True)
    data["text_group_id"] = data["text"].map(lambda text: _text_group(text, domain))
    conflicts = data.groupby("text_group_id")[target].nunique()
    conflict_rows = data["text_group_id"].isin(conflicts[conflicts > 1].index)
    eligible = data.loc[~conflict_rows].drop_duplicates("text_group_id")
    exclusions = {"input_rows": len(data), "conflicting_rows": int(conflict_rows.sum()),
                  "conflicting_groups": int((conflicts > 1).sum()),
                  "duplicate_rows": len(data) - int(conflict_rows.sum()) - len(eligible),
                  "representatives": len(eligible)}
    counts = eligible[target].value_counts().sort_index().to_dict()
    supported = bool(counts) and min(counts.values()) >= 10
    partitions = {key: [] for key in ("train", "calibration", "test")}
    if supported:
        rng = random.Random(random_state)
        for _, rows in eligible.groupby(target, sort=True):
            indices = list(rows.index)
            rng.shuffle(indices)
            n_train, n_calibration = len(indices) * 6 // 10, len(indices) * 2 // 10
            partitions["train"].extend(indices[:n_train])
            partitions["calibration"].extend(indices[n_train:n_train + n_calibration])
            partitions["test"].extend(indices[n_train + n_calibration:])
    parts = {key: data.loc[index].sort_values("ticket_id").reset_index(drop=True)
             for key, index in partitions.items()}
    halves = {"calibration_fit": [], "policy_selection": []}
    rng = random.Random(random_state)
    for _, rows in parts["calibration"].groupby(target, sort=True):
        indices = list(rows.index)
        rng.shuffle(indices)
        halves["calibration_fit"].extend(indices[:len(indices) // 2])
        halves["policy_selection"].extend(indices[len(indices) // 2:])
    parts.update({key: parts["calibration"].loc[index].sort_values("ticket_id")
                  .reset_index(drop=True) for key, index in halves.items()})
    metadata = {
        key: {"ids": list(part.ticket_id), "groups": list(part.text_group_id)}
        for key, part in parts.items()
    }
    manifest = {
        "seed": random_state, "strategy": "canonical-representative-stratified-60/20/20",
        "status": "ready" if supported else "insufficient_support",
        "partitions": metadata,
        "counts_by_class": {key: part[target].value_counts().sort_index().to_dict()
                            for key, part in parts.items()},
        "eligible_counts_by_class": counts, "exclusions": exclusions,
        "rounding": "per-class floor(0.6*n), floor(0.2*n), remainder; calibration floor/ceil",
        "minimum_support": "10 representatives/class; train >=5, each calibration half >=1",
        "limitation": "near-duplicates without canonical equality may remain",
        "test_state": "sealed_ids_only", "grouping_version": GROUPING_VERSION,
    }
    manifest["split_version"] = content_hash(manifest)
    return DatasetSplit(domain, parts["train"], parts["calibration"],
                        parts["test"][["ticket_id", "domain", "text_group_id"]],
                        manifest["split_version"], parts["calibration_fit"],
                        parts["policy_selection"], manifest)


def atomic_json(value: object, destination: Path) -> None:
    payload = canonical_json(value)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    except OSError:
        raise ValueError("artifact_write_failed") from None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def write_manifest(manifest: Manifest, destination: Path) -> None:
    if set(manifest) != set(Manifest.__required_keys__) or manifest["schema_version"] != 1:
        raise ValueError("manifest_schema_mismatch")
    for field in ("configuration_sha256", "lock_sha256"):
        if not re.fullmatch(r"[a-f0-9]{64}", manifest[field]):
            raise ValueError(f"manifest_invalid:{field}")
    if not manifest["code_revision"] or not manifest["generated_at"].endswith("Z"):
        raise ValueError("manifest_invalid:revision_or_timestamp")
    for field, schema in (("sources", SourceManifest), ("splits", SplitManifest),
                          ("models", ModelManifest)):
        if not set(manifest[field]) <= {"customer", "it"}:
            raise ValueError("manifest_invalid:domain")
        for value in manifest[field].values():
            if not isinstance(value, dict) or not schema.__required_keys__.issubset(value):
                raise ValueError(f"manifest_invalid:{field}_schema")
    if not RetrievalManifest.__required_keys__.issubset(manifest["retrieval"]):
        raise ValueError("manifest_invalid:retrieval_schema")
    for entry in manifest["artifacts"].values():
        path = entry.get("path")
        if entry.get("status") == "unavailable":
            if (path is not None or entry.get("sha256") is not None
                    or entry.get("logical_sha256") is not None or not entry.get("reason")):
                raise ValueError("manifest_invalid:unavailable_artifact")
        elif entry.get("status") == "ready":
            if (not isinstance(path, str) or Path(path).is_absolute() or ".." in Path(path).parts
                    or Path(path).name == destination.name
                    or not re.fullmatch(r"[a-f0-9]{64}", entry.get("sha256") or "")
                    or not re.fullmatch(r"[a-f0-9]{64}", entry.get("logical_sha256") or "")):
                raise ValueError("manifest_invalid:artifact_path_or_hash")
        else:
            raise ValueError("manifest_invalid:artifact_status")
    atomic_json(manifest, destination)
