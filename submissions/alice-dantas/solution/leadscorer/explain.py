"""'Por que está aqui' como dado: motivos e próximo passo em código (P0-3).

Sem texto e sem LLM. Cada item tem exatamente dois motivos {code, role, params}: o
que decidiu o grupo e o que decidiu a ordem dentro dele. Os parâmetros são os valores
que a regra usou, tirados do item e do `meta` do payload (RE-04); nada que não decide
entra como motivo (regra A, ADR-006). Quem apresenta (tela e CLI) escreve o texto.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from . import codes, policy

Reason = Dict[str, Any]


def _reason(code: str, role: str, **params: Any) -> Reason:
    return {"code": code, "role": role, "params": params}


def group_reason(item: Dict[str, Any], meta: Dict[str, Any]) -> Reason:
    """O que decidiu o grupo, com os valores usados em `triage.classify`."""
    group = item["group"]
    if group == policy.NAO_PONTUAVEL:
        return _reason(codes.MISSING_FIELD, codes.ROLE_GROUP, field=item["missing_field"])
    if group == policy.QUALIFICAR:
        return _reason(codes.PROSPECTING_STAGE, codes.ROLE_GROUP, deal_stage=item["deal_stage"])
    age, won, longest = item["age_days"], meta["won_cycle_limit_days"], meta["cycle_limit_days"]
    if group == policy.FOCAR:
        return _reason(codes.AGE_WITHIN_WON_CYCLE, codes.ROLE_GROUP, age_days=age, won_cycle_limit_days=won,
                       percentile=meta["cycle_percentile"])
    if group == policy.ACOMPANHAR:
        return _reason(codes.AGE_ABOVE_WON_CYCLE, codes.ROLE_GROUP, age_days=age, won_cycle_limit_days=won,
                       cycle_limit_days=longest, percentile=meta["cycle_percentile"])
    return _reason(codes.AGE_ABOVE_CYCLE_LIMIT, codes.ROLE_GROUP, age_days=age, cycle_limit_days=longest)


def order_reason(item: Dict[str, Any]) -> Reason:
    """O que decidiu a ordem dentro do grupo: faixa e preço de tabela (`triage.order`)."""
    if item["product"] is None:
        return _reason(codes.NO_PRODUCT, codes.ROLE_ORDER)
    if item["sales_price"] is None:
        return _reason(codes.NO_LIST_PRICE, codes.ROLE_ORDER, product=item["product"])
    return _reason(codes.LIST_PRICE, codes.ROLE_ORDER, product=item["product"],
                   sales_price=item["sales_price"], value_band=item["value_band"])


def reasons(item: Dict[str, Any], meta: Dict[str, Any]) -> List[Reason]:
    return [group_reason(item, meta), order_reason(item)]


def _action(code: str, **params: Any) -> Dict[str, Any]:
    return {"code": code, "params": params}


def _verification(code: str, has_account: Optional[bool]) -> Dict[str, Any]:
    """A verificação do grupo; as que citam a conta levam `has_account` (nulo no grupo, que não tem conta)."""
    if code in codes.ACCOUNT_ACTION_CODES:
        return _action(code, has_account=has_account)
    return _action(code)


def next_action(item: Dict[str, Any]) -> Dict[str, Any]:
    """O que verificar agora: depende só do grupo e de a conta estar registrada. Não presume atividade,
    intenção nem compromisso que o CRM da base não registra (ADR-008)."""
    if item["group"] == policy.NAO_PONTUAVEL:
        return _action(codes.FIX_MISSING_FIELD, field=item["missing_field"])
    return _verification(policy.NEXT_ACTIONS[item["group"]], item["account"] is not None)


def group_next_action(state: str) -> Dict[str, Any]:
    if state == policy.NAO_PONTUAVEL:
        return _action(codes.FIX_MISSING_FIELDS)
    return _verification(policy.NEXT_ACTIONS[state], None)
