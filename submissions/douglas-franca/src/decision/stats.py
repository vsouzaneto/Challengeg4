"""Comparação de médias com IC, equivalência (TOST) e correção de Benjamini-Hochberg.

Compartilhado pela análise do G3 (src/analysis/run_inference.py) e pelo Decision Gate (app/).
"""

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

from src.decision.rules import SESOI_PP

Z95, Z90, Z_POWER = stats.norm.ppf(0.975), stats.norm.ppf(0.95), stats.norm.ppf(0.80)

VERDICT_HELP = {
    "EQUIVALENTE": "não faz diferença para a decisão",
    "DIFERENTE, MAS IRRELEVANTE": "existe, mas é pequeno demais para mudar verba",
    "DIFERENTE": "faz diferença para a decisão",
    "INCONCLUSIVO": "faltam dados para concluir",
}


def verdict(diff: float, se: float, p_adj: float, sesoi: float = SESOI_PP) -> str:
    equivalent = diff - Z90 * se > -sesoi and diff + Z90 * se < sesoi
    significant = p_adj < 0.05
    if equivalent and significant:
        return "DIFERENTE, MAS IRRELEVANTE"
    if equivalent:
        return "EQUIVALENTE"
    if significant:
        return "DIFERENTE"
    return "INCONCLUSIVO"


def compare(a: pd.Series, b: pd.Series) -> dict:
    diff = a.mean() - b.mean()
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return {"n_grupo": len(a), "n_resto": len(b), "media_grupo": a.mean(), "diferenca_pp": diff, "se": se,
            "ic95_inf": diff - Z95 * se, "ic95_sup": diff + Z95 * se,
            "p": 2 * stats.norm.sf(abs(diff / se)), "mde_pp": (Z95 + Z_POWER) * se}


def finalize(table: pd.DataFrame, sesoi: float = SESOI_PP) -> pd.DataFrame:
    table["p_ajustado_bh"] = multipletests(table.p, method="fdr_bh")[1]
    table["veredito"] = [verdict(d, s, p, sesoi) for d, s, p in
                         zip(table.diferenca_pp, table.se, table.p_ajustado_bh)]
    return table


def level_vs_rest(df: pd.DataFrame, col: str, metric: str = "er", levels: list | None = None,
                  min_n: int = 2) -> pd.DataFrame:
    """Cada nível de `col` contra o resto, com veredito corrigido para múltiplos testes."""
    rows = []
    for level in levels if levels is not None else sorted(df[col].dropna().unique()):
        mask = df[col] == level
        if mask.sum() >= min_n and (~mask).sum() >= min_n:
            rows.append({"nivel": str(level), **compare(df.loc[mask, metric], df.loc[~mask, metric])})
    if not rows:
        return pd.DataFrame()
    return finalize(pd.DataFrame(rows))
