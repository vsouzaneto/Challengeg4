"""Fixture pequena e sintética SÓ para testes unitários.

Não é usada em nenhuma análise nem no app: a solução roda sobre os CSVs reais do Kaggle.
Os valores aqui foram escolhidos para exercitar casos de borda: produto grafado
"GTXPro", deal aberto sem conta, deal aberto com close_date preenchida por engano,
ciclo negativo, vendedor sem time.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from leadscorer.data import Tables  # noqa: E402


@pytest.fixture()
def raw_dir(tmp_path: Path) -> Path:
    accounts = pd.DataFrame({
        "account": ["Acme Corporation", "Betasoloin", "Cheers"],
        "sector": ["technolgy", "medical", "entertainment"],
        "year_established": [1996, 1999, 1993],
        "revenue": [1100.04, 251.41, 4269.9],
        "employees": [2822, 495, 6472],
        "office_location": ["United States", "United States", "United States"],
        "subsidiary_of": [None, None, "Massive Dynamic"],
    })
    products = pd.DataFrame({
        "product": ["GTX Basic", "GTX Pro", "MG Special"],
        "series": ["GTX", "GTX", "MG"],
        "sales_price": [550, 4821, 55],
    })
    teams = pd.DataFrame({
        "sales_agent": ["Moses Frase", "Darcel Schlecht"],
        "manager": ["Dustin Brinkmann", "Melvin Marxen"],
        "regional_office": ["Central", "Central"],
    })
    pipeline = pd.DataFrame({
        "opportunity_id": ["W1", "W2", "L1", "L2", "E1", "E2", "P1", "P2", "E3"],
        "sales_agent": ["Moses Frase", "Moses Frase", "Darcel Schlecht", "Darcel Schlecht", "Moses Frase", "Darcel Schlecht", "Moses Frase", "Darcel Schlecht", "Alguem Sem Time"],
        "product": ["GTX Basic", "GTXPro", "GTX Basic", "MG Special", "GTXPro", "GTX Basic", "MG Special", "GTX Basic", "GTX Pro"],
        "account": ["Acme Corporation", "Betasoloin", "Acme Corporation", "Cheers", "Acme Corporation", None, None, "Cheers", "Betasoloin"],
        "deal_stage": ["Won", "Won", "Lost", "Lost", "Engaging", "Engaging", "Prospecting", "Prospecting", "Engaging"],
        "engage_date": ["2017-01-10", "2017-02-01", "2017-01-20", "2017-03-15", "2017-10-01", "2017-06-01", None, None, "2017-12-20"],
        "close_date": ["2017-03-01", "2017-01-25", "2017-02-28", "2017-05-01", "2017-11-15", None, None, None, None],
        "close_value": [560, 4900, 0, 0, 3000, None, None, None, None],
    })
    for name, df in (("accounts.csv", accounts), ("products.csv", products), ("sales_teams.csv", teams), ("sales_pipeline.csv", pipeline)):
        df.to_csv(tmp_path / name, index=False)
    return tmp_path
