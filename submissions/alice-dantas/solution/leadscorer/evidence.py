"""Evidência do backtest como dado (contrato v5): o que a página Evidência mostra.

Lê o resultado de `scripts/backtest.py` (`policy.EVIDENCE_PATH`) e devolve só códigos e
números. A armadilha de vazamento fica de fora: no relatório ela prova que o backtest a
detecta, mas não é uma estratégia possível. O texto de cada código é de quem apresenta.

O resultado traz o carimbo da regra que ele mediu como servida (`design.served_rule`): se
não for a regra que `triage.py` serve hoje (`codes.SERVED_RANKER`), o arquivo é de outra
regra e não é servido, para um resultado antigo nunca aparecer como o da regra atual.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import codes, policy
from .errors import DataError

METRICS = ("auc_mean", "auc_min", "auc_max", "p_at_k", "lift_at_k", "val_at_k")
DESIGN = ("cuts", "horizon_days", "top_k", "observations", "unique_opportunities", "n_boot_sellers", "audited_data")


def _unavailable(path: Path, why: str) -> DataError:
    return DataError(f"{path.name} {why}: rode scripts/backtest.py com os CSVs em data/raw/.",
                     code=codes.EVIDENCE_UNAVAILABLE, file=path.name)


def _delta(entry: Dict[str, Any]) -> Optional[Dict[str, float]]:
    if "d_val_at_k" not in entry:
        return None
    return {"value": entry["d_val_at_k"], "low": entry["d_val_low"], "high": entry["d_val_high"]}


def _ranker(entry: Dict[str, Any]) -> Dict[str, Any]:
    if entry["code"] not in codes.RANKER_CODES:
        raise KeyError(entry["code"])
    return {"code": entry["code"], **{key: entry[key] for key in METRICS},
            "cuts_auc_above_chance": entry.get("cuts_ci_above_half"),
            "delta_val": _delta(entry), "cuts_val_above_reference": entry.get("cuts_val_above_reference")}


def _rankers(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [_ranker(entry) for entry in entries if not entry["leak"]]


def verdict(rankers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Como fica a regra servida contra as alternativas, pelo IC95% de cada diferença.

    `reference_behind`: alguma alternativa fica à frente com o IC inteiro acima de zero (vale a
    de maior diferença; no empate, a primeira do relatório). `reference_ahead`: todas ficam atrás
    com o IC inteiro abaixo de zero (vale a mais próxima). Fora disso, `inconclusive`.
    """
    others = [r for r in rankers if r["delta_val"] is not None]
    ahead = [r for r in others if r["delta_val"]["low"] > 0]
    if ahead:
        best = max(ahead, key=lambda r: r["delta_val"]["value"])
        return {"code": codes.VERDICT_REFERENCE_BEHIND, "ranker": best["code"], "delta": best["delta_val"]}
    if others and all(r["delta_val"]["high"] < 0 for r in others):
        closest = max(others, key=lambda r: r["delta_val"]["value"])
        return {"code": codes.VERDICT_REFERENCE_AHEAD, "ranker": closest["code"], "delta": closest["delta_val"]}
    return {"code": codes.VERDICT_INCONCLUSIVE, "ranker": None, "delta": None}


def load(path: Path = policy.EVIDENCE_PATH) -> Dict[str, Any]:
    """Desenho, estratégias (na ordem do relatório), o recorte sem as que nunca fecham e o veredito dele."""
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise _unavailable(path, "não encontrado") from None
    except (OSError, ValueError):
        raise _unavailable(path, "ilegível") from None
    try:
        served = result["design"]["served_rule"]
        without = _rankers(result["without_no_outcome"])
        payload = {
            "design": {key: result["design"][key] for key in DESIGN},
            "reference": codes.SERVED_RANKER,
            "rankers": _rankers(result["summary"]),
            "without_no_outcome": without,
            "without_no_outcome_verdict": verdict(without),
        }
    except (KeyError, TypeError):
        raise _unavailable(path, "fora do formato esperado") from None
    if served != codes.SERVED_RANKER:
        raise _unavailable(path, f"mediu outra regra como servida ({served})")
    return payload
