"""Formatação de números e datas em português do Brasil."""
from __future__ import annotations

import pandas as pd


def fmt_int(value: int) -> str:
    """Inteiro com separador de milhar brasileiro: 8800 -> '8.800'."""
    return f"{int(value):,}".replace(",", ".")


def fmt_date(value: pd.Timestamp) -> str:
    return value.strftime("%d/%m/%Y")
