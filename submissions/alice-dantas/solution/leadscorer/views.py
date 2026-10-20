"""Payload único para CLI, API e tela.

O payload é o contrato: a CLI (`--json`), a API e a tela recebem o mesmo
dicionário, o que garante a mesma lista em todas as saídas. Ele leva só chaves,
códigos e números (`codes.py`); o texto é de quem apresenta.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from . import codes, explain, policy, triage
from .data import Dataset
from .errors import NotFoundError


def _optional(value: Any) -> Any:
    return None if pd.isna(value) else value


def meta(dataset: Dataset, ctx: triage.Context) -> Dict[str, Any]:
    """Data de referência, os dois limites que decidem o grupo das Engaging (regra A) e a mediana do ciclo das
    ganhas, que só contextualiza a idade."""
    return {
        "as_of": ctx.as_of.date().isoformat(),
        "won_cycle_median_days": ctx.won_cycle_median_days,
        "won_cycle_limit_days": ctx.won_cycle_limit_days,
        "cycle_limit_days": ctx.cycle_limit_days,
        "cycle_percentile": policy.CYCLE_PERCENTILE,
        "audited": dataset.audited,
        "contract_version": codes.CONTRACT_VERSION,
    }


def context(dataset: Dataset, as_of: Optional[triage.DateLike]) -> triage.Context:
    frame = dataset.opportunities
    return triage.resolve_context(frame, triage.parse_as_of(frame, as_of))


def item(row: pd.Series, info: Dict[str, Any]) -> Dict[str, Any]:
    account = _optional(row["account"])
    engage = _optional(row["engage_date"])
    age = _optional(row["age_days"])
    price = _optional(row["sales_price"])
    band = _optional(row["value_band"])
    missing = _optional(row["missing_field"])
    entry = {
        "opportunity_id": row["opportunity_id"],
        "sales_agent": row["sales_agent"],
        "product": _optional(row["product"]),
        "account": account,
        "sales_price": None if price is None else int(price),
        "value_band": band,
        "engage_date": None if engage is None else engage.date().isoformat(),
        "age_days": None if age is None else int(age),
        "group": row["state"],
        "deal_stage": row["deal_stage"],
        "missing_field": missing,
        "tie_size": int(row["tie_size"]),
    }
    entry["reasons"] = explain.reasons(entry, info)
    entry["next_action"] = explain.next_action(entry)
    return entry


def _code(code: str, **params: Any) -> Dict[str, Any]:
    return {"code": code, "params": params}


def empty_state(state: str, counts: Dict[str, int], ctx: triage.Context) -> Optional[Dict[str, Any]]:
    """Grupo vazio, ou Focar vazio apontando o primeiro grupo seguinte com oportunidades (Q-01)."""
    if counts[state]:
        return None
    if state == policy.FOCAR:
        start = next((s for s in policy.STATES[1:] if counts[s]), None)
        if start:
            return _code(codes.START_WITH_GROUP, group=start, action=policy.START_ACTION_CODES[start],
                         has_engaging=bool(counts[policy.ACOMPANHAR] + counts[policy.REVISAR]),
                         won_cycle_limit_days=ctx.won_cycle_limit_days, cycle_limit_days=ctx.cycle_limit_days)
    return _code(codes.GROUP_EMPTY)


def ordering() -> Dict[str, Any]:
    """A ordem de `triage.order` como dado: grupos na ordem dos estados e, dentro do
    grupo, faixa, preço decrescente e ID. A idade não entra."""
    return {"group_order": list(policy.STATES),
            "within_group": list(codes.ORDER_CRITERIA), "age_affects_order": False}


def value_bands() -> List[Dict[str, Any]]:
    """Faixas de valor de tabela como dado (`triage.value_band`): preço ≥ mínimo, da faixa
    de cima para a de baixo. Os preços são inteiros, então o máximo é o mínimo da faixa
    de cima menos 1; a faixa de cima não tem máximo."""
    bands, upper = [], None
    for label, minimum in policy.VALUE_BANDS:
        bands.append({"band": label, "min_price": minimum, "max_price": None if upper is None else upper - 1})
        upper = minimum
    return bands


def summary(opps: pd.DataFrame) -> Dict[str, int]:
    return {"total": len(opps), **triage.summary(opps), "without_account": int(opps["account"].isna().sum())}


def portfolio(opps: pd.DataFrame, info: Dict[str, Any], ctx: triage.Context, no_open: str) -> Dict[str, Any]:
    """Resumo, ordem e grupos de uma carteira já ordenada. `no_open` é o código de
    carteira vazia (`codes.NO_OPEN_FOR_SELLER` ou `NO_OPEN_FOR_FILTER`)."""
    counts = triage.summary(opps)
    total = len(opps)
    groups = []
    for state in policy.STATES:
        rows = opps[opps["state"] == state]
        groups.append({
            "state": state,
            "count": counts[state],
            "empty": empty_state(state, counts, ctx) if total else _code(codes.GROUP_EMPTY),
            "next_action": explain.group_next_action(state) if len(rows) else None,
            "items": [item(row, info) for _, row in rows.iterrows()],
        })
    return {
        "meta": info,
        "ordering": ordering(),
        "summary": summary(opps),
        "empty": None if total else _code(no_open),
        "groups": groups,
    }


def sellers(dataset: Dataset) -> List[Dict[str, str]]:
    """Vendedores em ordem alfabética, sem nenhuma métrica: nunca um ranking de pessoas (RD-06)."""
    teams = dataset.teams.sort_values("sales_agent")
    return [{"name": row.sales_agent, "manager": row.manager, "office": row.regional_office}
            for row in teams.itertuples(index=False)]


# Colunas do recorte por pessoas: as mesmas em `opportunities` e em `teams`.
SCOPE_COLUMNS = (("seller", "sales_agent"), ("manager", "manager"), ("office", "regional_office"))


def scope(opps: pd.DataFrame, teams: pd.DataFrame, **values: Optional[str]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Recorte por vendedor, manager e escritório, por igualdade exata (sem validar o valor:
    um valor inexistente dá recorte vazio). A Equipe e a Inteligência usam este mesmo recorte,
    então os grupos das abertas são iguais nas duas telas."""
    for key, column in SCOPE_COLUMNS:
        value = values.pop(key, None)
        if value:
            opps, teams = opps[opps[column] == value], teams[teams[column] == value]
    if values:
        raise TypeError(f"recorte desconhecido: {sorted(values)}")
    return opps, teams


def team_pipeline(dataset: Dataset, manager: Optional[str] = None, office: Optional[str] = None,
                  as_of: Optional[triage.DateLike] = None) -> Dict[str, Any]:
    """Carteira filtrada por manager e/ou escritório, na mesma ordem declarada.
    Filtro sem abertas (ou inexistente) devolve lista vazia com o código de vazio."""
    ctx = context(dataset, as_of)
    opps, teams = scope(triage.classify(dataset.opportunities, ctx), dataset.teams, manager=manager, office=office)
    payload = portfolio(triage.order(opps), meta(dataset, ctx), ctx, codes.NO_OPEN_FOR_FILTER)
    return {"filter": {"manager": manager, "office": office}, **payload, "by_seller": by_seller(opps, teams)}


def by_seller(opps: pd.DataFrame, teams: pd.DataFrame) -> List[Dict[str, Any]]:
    """O resumo de cada vendedor do filtro, inclusive quem não tem abertas, em ordem
    alfabética: é a carteira de cada um, nunca um ranking de pessoas (AC-2.9)."""
    return [{"seller": name, **summary(opps[opps["sales_agent"] == name])}
            for name in sorted(teams["sales_agent"])]


def rules(dataset: Dataset, as_of: Optional[triage.DateLike] = None) -> Dict[str, Any]:
    """A política que monta a lista, como dado, para a página Como funciona."""
    ctx = context(dataset, as_of)
    return {"meta": meta(dataset, ctx), "ordering": ordering(), "value_bands": value_bands()}


def seller_pipeline(dataset: Dataset, seller: str, as_of: Optional[triage.DateLike] = None) -> Dict[str, Any]:
    if seller not in dataset.sellers:
        raise NotFoundError(f"Vendedor '{seller}' não encontrado em sales_teams.csv.",
                            code=codes.SELLER_NOT_FOUND, seller=seller)
    ctx = context(dataset, as_of)
    opps = triage.classify(dataset.opportunities, ctx)
    opps = triage.order(opps[opps["sales_agent"] == seller])
    payload = portfolio(opps, meta(dataset, ctx), ctx, codes.NO_OPEN_FOR_SELLER)
    return {"seller": seller, **payload}


def opportunity_detail(dataset: Dataset, opportunity_id: str,
                       as_of: Optional[triage.DateLike] = None) -> Dict[str, Any]:
    """O item como aparece na lista do vendedor, com motivos e `meta`."""
    frame = dataset.opportunities
    match = frame[(frame["opportunity_id"] == opportunity_id) & frame["deal_stage"].isin(policy.OPEN_STAGES)]
    if match.empty:
        raise NotFoundError(f"Oportunidade aberta {opportunity_id} não encontrada.",
                            code=codes.OPPORTUNITY_NOT_FOUND, opportunity_id=opportunity_id)
    payload = seller_pipeline(dataset, match["sales_agent"].iloc[0], as_of)
    entry = next(e for g in payload["groups"] for e in g["items"] if e["opportunity_id"] == opportunity_id)
    return {"meta": payload["meta"], "seller": payload["seller"], "item": entry}
