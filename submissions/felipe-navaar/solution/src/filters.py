"""Filtros puros sobre a fila já pontuada; nunca recalculam o score."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd


def _selected_values(values: Iterable[str] | None) -> set[str] | None:
    if values is None:
        return None
    selected = {str(value) for value in values}
    return selected or None


def filter_queue(
    queue: pd.DataFrame,
    *,
    sales_agents: Iterable[str] | None = None,
    managers: Iterable[str] | None = None,
    regional_offices: Iterable[str] | None = None,
    products: Iterable[str] | None = None,
    stages: Iterable[str] | None = None,
    min_score: int | None = None,
    max_score: int | None = None,
    search_text: str | None = None,
) -> pd.DataFrame:
    """Aplica filtros combináveis e devolve um subconjunto da fila pontuada.

    A ordem, o score e a posição global recebidos da etapa de scoring são
    preservados. Listas vazias significam que nenhum filtro foi selecionado.
    """

    required = {"sales_agent", "manager", "regional_office", "priority_score"}
    missing = sorted(required - set(queue.columns))
    if missing:
        raise ValueError(f"Fila sem colunas necessárias para filtro: {', '.join(missing)}")

    mask = pd.Series(True, index=queue.index)
    for column, values in (
        ("sales_agent", sales_agents),
        ("manager", managers),
        ("regional_office", regional_offices),
        ("product", products),
        ("deal_stage", stages),
    ):
        selected = _selected_values(values)
        if selected is not None:
            if column not in queue.columns:
                raise ValueError(f"Fila sem colunas necessárias para filtro: {column}")
            mask &= queue[column].astype("string").isin(selected)
    if min_score is not None:
        mask &= queue["priority_score"].ge(min_score)
    if max_score is not None:
        mask &= queue["priority_score"].le(max_score)
    if search_text and search_text.strip():
        searchable = [column for column in ("opportunity_id", "account", "product", "sales_agent") if column in queue]
        terms = queue[searchable].fillna("").astype(str).agg(" ".join, axis=1).str.casefold()
        mask &= terms.str.contains(search_text.strip().casefold(), regex=False)
    return queue.loc[mask].copy()
