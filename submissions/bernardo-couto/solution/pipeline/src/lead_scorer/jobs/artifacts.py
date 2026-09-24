"""Shared IO helpers for the ``train`` and ``score`` jobs: gold partitions, model registry.

``models/<version>/`` layout::

    pipeline_model/            Spark ML PipelineModel (+ isotonic calibrator)  [gitignored]
    metrics.json               backtest vs baselines, shadow model, promotion, acceptance
    model_card.md              pt-BR model card
    feature_list.json          closed feature list of layer 2
    training_manifest.json     params, frame, coefficients, feature distributions (PSI ref)
    models/latest              one-line pointer file with the version name
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from pyspark.sql import DataFrame, SparkSession

from lead_scorer.config import GOLD_DIR, MODELS_DIR, partition_dir
from lead_scorer.data.gold import MANIFEST_NAME

PIPELINE_MODEL_DIR = "pipeline_model"
METRICS_FILE = "metrics.json"
MODEL_CARD_FILE = "model_card.md"
FEATURE_LIST_FILE = "feature_list.json"
TRAINING_MANIFEST_FILE = "training_manifest.json"
LATEST_POINTER = "latest"
SCORES_TABLE = "scores"

BUILD_FEATURES_HINT = "run `uv run python -m lead_scorer.jobs build-features --as-of {as_of}` first"


class MissingArtifactError(FileNotFoundError):
    """A required gold partition or model artifact is not on disk."""


def gold_partition(table: str, as_of: date, gold_dir: Path = GOLD_DIR) -> Path:
    return partition_dir(gold_dir, table, as_of)


def gold_partition_exists(table: str, as_of: date, gold_dir: Path = GOLD_DIR) -> bool:
    path = gold_partition(table, as_of, gold_dir)
    return path.is_dir() and any(path.glob("*.parquet"))


def read_gold(spark: SparkSession, table: str, as_of: date, gold_dir: Path = GOLD_DIR) -> DataFrame:
    if not gold_partition_exists(table, as_of, gold_dir):
        raise MissingArtifactError(
            f"gold/{table}/as_of={as_of.isoformat()} not found under {gold_dir}; "
            + BUILD_FEATURES_HINT.format(as_of=as_of.isoformat())
        )
    return spark.read.parquet(str(gold_partition(table, as_of, gold_dir)))


def read_gold_manifest(table: str, as_of: date, gold_dir: Path = GOLD_DIR) -> dict[str, Any]:
    path = gold_partition(table, as_of, gold_dir) / MANIFEST_NAME
    if not path.is_file():
        return {}
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


# --- model registry -------------------------------------------------------------------------------


def model_version_name(as_of: date, promoted: bool, revision: int = 1) -> str:
    """``2017-12-31-rules-v1`` in shadow mode, ``2017-12-31-lr-v1`` once the model is promoted."""
    return f"{as_of.isoformat()}-{'lr' if promoted else 'rules'}-v{revision}"


def model_dir(version: str, models_dir: Path = MODELS_DIR) -> Path:
    return models_dir / version


def write_latest_pointer(version: str, models_dir: Path = MODELS_DIR) -> Path:
    pointer = models_dir / LATEST_POINTER
    pointer.parent.mkdir(parents=True, exist_ok=True)
    pointer.write_text(version + "\n", encoding="utf-8")
    return pointer


def resolve_model_dir(model: str | Path = LATEST_POINTER, models_dir: Path = MODELS_DIR) -> Path:
    """Accept ``latest``, ``models/latest``, a version name or a path to ``models/<version>``."""
    candidate = Path(model)
    if candidate.name == LATEST_POINTER:
        pointer = candidate if candidate.is_file() else models_dir / LATEST_POINTER
        if not pointer.is_file():
            raise MissingArtifactError(
                f"{pointer} not found; run `uv run python -m lead_scorer.jobs train` first"
            )
        version = pointer.read_text(encoding="utf-8").strip()
        target = pointer.parent / version
    elif candidate.is_dir():
        target = candidate
    else:
        target = models_dir / str(model)
    if not (target / TRAINING_MANIFEST_FILE).is_file():
        raise MissingArtifactError(f"model directory {target} has no {TRAINING_MANIFEST_FILE}")
    return target


def read_json(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


__all__ = [
    "BUILD_FEATURES_HINT",
    "FEATURE_LIST_FILE",
    "LATEST_POINTER",
    "METRICS_FILE",
    "MODEL_CARD_FILE",
    "PIPELINE_MODEL_DIR",
    "SCORES_TABLE",
    "TRAINING_MANIFEST_FILE",
    "MissingArtifactError",
    "gold_partition",
    "gold_partition_exists",
    "model_dir",
    "model_version_name",
    "read_gold",
    "read_gold_manifest",
    "read_json",
    "resolve_model_dir",
    "write_json",
    "write_latest_pointer",
]
