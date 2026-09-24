"""Model artifacts written by the ``train`` job: metrics.json, feature_list.json, model_card.md."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter

from api.errors import ModelArtifactsMissingError
from api.repository import read_model_version, resolve_latest_model_dir
from api.routers._common import _err
from api.schemas import ModelMetricsResponse
from api.settings import SOLUTION_DIR, settings

router = APIRouter(tags=["modelo"])

ERR_503_MODEL = _err(
    "Artefatos do modelo ausentes.",
    "MODEL_ARTIFACTS_MISSING",
    "Artefato do modelo ausente: models/latest.",
    "Rode `make pipeline` (job `train`) para gerar models/<versão>/ e o ponteiro models/latest.",
)


@router.get(
    "/model/metrics",
    response_model=ModelMetricsResponse,
    operation_id="get_model_metrics",
    summary="Métricas do backtest e model card do modelo em produção",
    description=(
        "Lê `models/latest/metrics.json` (backtest temporal vs. baselines aleatório, preço, "
        "mais-novo-primeiro e taxa-base; calibração), `feature_list.json` e `model_card.md`. "
        "O conteúdo de `metrics` é o JSON gravado pelo job `train`, sem transformação. "
        "Retorna 503 com a instrução de geração quando o pipeline ainda não treinou."
    ),
    responses={503: ERR_503_MODEL},
)
def get_model_metrics() -> ModelMetricsResponse:
    pointer = settings.latest_model_pointer
    model_dir = resolve_latest_model_dir(pointer)
    if model_dir is None:
        raise ModelArtifactsMissingError(_relative(pointer))
    metrics_path = model_dir / "metrics.json"
    if not metrics_path.is_file():
        raise ModelArtifactsMissingError(_relative(metrics_path))
    try:
        metrics: Any = json.loads(metrics_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ModelArtifactsMissingError(f"{_relative(metrics_path)} (JSON inválido)") from exc
    if not isinstance(metrics, dict):
        raise ModelArtifactsMissingError(f"{_relative(metrics_path)} (esperado objeto JSON)")

    features: list[str] | None = None
    features_path = model_dir / "feature_list.json"
    if features_path.is_file():
        try:
            loaded = json.loads(features_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ModelArtifactsMissingError(f"{_relative(features_path)} (JSON inválido)") from exc
        if isinstance(loaded, list):
            features = [str(f) for f in loaded]

    card_path = model_dir / "model_card.md"
    card = card_path.read_text(encoding="utf-8") if card_path.is_file() else None
    version = read_model_version(pointer) or str(metrics.get("model_version") or "unknown")
    return ModelMetricsResponse(
        model_version=version,
        metrics=metrics,
        feature_list=features,
        model_card_path=_relative(card_path),
        model_card_markdown=card,
    )


def _relative(path: Any) -> str:
    try:
        return str(path.resolve().relative_to(SOLUTION_DIR))
    except ValueError:
        return str(path)
