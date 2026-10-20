"""Estados, faixa de valor de tabela e ordem declarada (ADR-001; regra A, ADR-006).

Funções puras sobre o frame de `data.load`. Não há número contínuo nem
probabilidade: a prioridade é estado → faixa → preço de tabela → ID (só para
ordem estável). A idade decide o grupo das Engaging pelos dois limites do
`Context` e não entra na ordem dentro do grupo.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import date
from typing import Dict, Optional, Union

import numpy as np
import pandas as pd

from . import codes, policy
from .errors import DataError, PolicyError

DateLike = Union[date, str, pd.Timestamp]


@dataclass(frozen=True)
class Context:
    """Data de referência e os dois limites de idade das Engaging. Construa sempre por palavra-chave."""
    as_of: pd.Timestamp
    won_cycle_limit_days: int  # L1: piso do P90 do ciclo das ganhas até o as_of
    won_cycle_median_days: int  # mediana do ciclo das ganhas até o as_of: contexto da idade, não decide grupo
    cycle_limit_days: int      # L2: maior ciclo fechado (ganhas e perdidas) até o as_of

    def __post_init__(self) -> None:
        if self.won_cycle_limit_days > self.cycle_limit_days:
            raise ValueError(f"L1 ({self.won_cycle_limit_days} d) acima de L2 ({self.cycle_limit_days} d)")


AS_OF_FORMAT = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_as_of(frame: pd.DataFrame, value: Optional[DateLike]) -> Optional[pd.Timestamp]:
    """Valida o as_of vindo do usuário: AAAA-MM-DD e nunca antes do último
    fechamento (D-4), para não tirar da carteira deals fechados depois dele."""
    if value is None:
        return None
    minimum = frame["close_date"].max()
    minimum_iso = minimum.date().isoformat()
    if isinstance(value, str):
        try:
            if not AS_OF_FORMAT.match(value):
                raise ValueError(value)
            stamp = pd.Timestamp(value)
        except ValueError:
            raise PolicyError(f"Data inválida: '{value}'. Use o formato AAAA-MM-DD, "
                              f"a partir de {minimum_iso}.",
                              code=codes.INVALID_AS_OF_FORMAT, value=value, minimum=minimum_iso) from None
    else:
        stamp = pd.Timestamp(value)
    if stamp < minimum:
        raise PolicyError(f"Data {stamp.date().isoformat()} anterior ao último fechamento registrado. "
                          f"Use uma data a partir de {minimum_iso}, no formato AAAA-MM-DD.",
                          code=codes.AS_OF_BEFORE_LAST_CLOSE, value=stamp.date().isoformat(), minimum=minimum_iso)
    return stamp


def cycle_days(frame: pd.DataFrame, stages, as_of: pd.Timestamp) -> pd.Series:
    """Ciclo (`close_date` − `engage_date`, em dias) das fechadas nos estágios dados até o as_of."""
    closed = frame[frame["deal_stage"].isin(stages) & (frame["close_date"] <= as_of)]
    return (closed["close_date"] - closed["engage_date"]).dt.days.dropna()


def won_cycle_limit(frame: pd.DataFrame, as_of: pd.Timestamp) -> int:
    """L1: piso do P90 linear do ciclo das ganhas até o as_of. A idade é inteira, então
    idade ≤ P90 equivale a idade ≤ piso (a folga de 1e-9 só absorve ruído de ponto flutuante)."""
    cycles = cycle_days(frame, ("Won",), as_of)
    if cycles.empty:
        as_of_iso = as_of.date().isoformat()
        raise DataError(f"Nenhuma venda ganha até {as_of_iso}: sem ela não há como separar as negociações "
                        "pelo tempo das vendas ganhas.", code=codes.NO_WON_HISTORY, as_of=as_of_iso)
    return int(math.floor(cycles.quantile(policy.CYCLE_PERCENTILE / 100) + 1e-9))


def won_cycle_median(frame: pd.DataFrame, as_of: pd.Timestamp) -> int:
    """Mediana (piso) do ciclo das ganhas até o as_of: só descreve o histórico, não entra em grupo nem em ordem."""
    return int(math.floor(cycle_days(frame, ("Won",), as_of).median() + 1e-9))


def resolve_context(frame: pd.DataFrame, as_of: Optional[DateLike] = None) -> Context:
    """`as_of` padrão = maior `close_date`. Os dois limites usam só fechadas até o
    `as_of` (nunca fechamentos posteriores): L1 das ganhas, L2 de todas as fechadas."""
    as_of_ts = frame["close_date"].max() if as_of is None else pd.Timestamp(as_of)
    won_limit = won_cycle_limit(frame, as_of_ts)
    longest = int(cycle_days(frame, policy.CLOSED_STAGES, as_of_ts).max())
    return Context(as_of=as_of_ts, won_cycle_limit_days=won_limit, cycle_limit_days=longest,
                   won_cycle_median_days=won_cycle_median(frame, as_of_ts))


def _flag(condition: pd.Series) -> np.ndarray:
    """Condição booleana sem nulos (pd.NA conta como falso)."""
    return condition.fillna(False).to_numpy(dtype=bool)


def value_band(price: pd.Series) -> pd.Series:
    labels = [label for label, _ in policy.VALUE_BANDS]
    conditions = [_flag(price >= floor) for _, floor in policy.VALUE_BANDS]
    bands = pd.Series(np.select(conditions, labels, default=labels[-1]), index=price.index)
    return bands.where(price.notna(), None)


def missing_field(opps: pd.DataFrame) -> pd.Series:
    """Primeiro campo necessário que falta (RD-03), na ordem de MISSING_FIELDS."""
    needed = {
        "product": opps["product"].isna(),
        "sales_price": opps["sales_price"].isna(),
        "engage_date": (opps["deal_stage"] == "Engaging") & opps["engage_date"].isna(),
    }
    fields = list(policy.MISSING_FIELDS)
    found = np.select([_flag(needed[f]) for f in fields], fields, default="")
    return pd.Series(found, index=opps.index).replace("", None)


def engaging_group(age: np.ndarray, ctx: Context) -> np.ndarray:
    """Grupo de uma Engaging pela idade (regra A): até L1 → focar; até L2 → acompanhar;
    acima → revisar. Vetorizada: `classify` e o backtest (scripts/backtest.py) chamam esta
    mesma função. Quem chama trata antes a idade ausente (vira nao_pontuavel)."""
    age = np.asarray(age, dtype=float)
    return np.select([age <= ctx.won_cycle_limit_days, age <= ctx.cycle_limit_days],
                     [policy.FOCAR, policy.ACOMPANHAR], default=policy.REVISAR)


def classify(frame: pd.DataFrame, ctx: Context) -> pd.DataFrame:
    """Abertas com estado, faixa e idade. Só enxerga os campos permitidos."""
    is_open = frame["deal_stage"].isin(policy.OPEN_STAGES)
    opps = frame.loc[is_open, list(policy.CLASSIFICATION_FIELDS)].copy()

    opps["age_days"] = (ctx.as_of - opps["engage_date"]).dt.days.astype("Int64")
    opps["value_band"] = value_band(opps["sales_price"])
    opps["missing_field"] = missing_field(opps)
    by_age = engaging_group(opps["age_days"].astype("float").to_numpy(), ctx)
    opps["state"] = np.select(
        [opps["missing_field"].notna().to_numpy(), (opps["deal_stage"] == "Engaging").to_numpy(),
         (opps["deal_stage"] == "Prospecting").to_numpy()],
        [policy.NAO_PONTUAVEL, by_age, policy.QUALIFICAR],
        default=policy.NAO_PONTUAVEL,
    )
    return opps


def order(opps: pd.DataFrame) -> pd.DataFrame:
    """Estado → faixa → preço decrescente → ID; `tie_size` marca empates."""
    state_rank = {s: i for i, s in enumerate(policy.STATES)}
    band_rank = {label: i for i, (label, _) in enumerate(policy.VALUE_BANDS)}
    keyed = opps.assign(
        _state=opps["state"].map(state_rank),
        _band=opps["value_band"].map(band_rank),
        _price=-opps["sales_price"].astype("float"),
    )
    ordered = keyed.sort_values(["_state", "_band", "_price", "opportunity_id"], kind="mergesort")
    ordered = ordered.drop(columns=["_state", "_band", "_price"])
    ordered["tie_size"] = ordered.groupby(["state", "product"], dropna=False)["opportunity_id"].transform("size")
    return ordered.reset_index(drop=True)


def summary(opps: pd.DataFrame) -> Dict[str, int]:
    counts = opps["state"].value_counts()
    return {state: int(counts.get(state, 0)) for state in policy.STATES}
