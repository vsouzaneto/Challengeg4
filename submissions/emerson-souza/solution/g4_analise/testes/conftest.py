"""
Pula os testes de uma ferramenta quando os dados do desafio dela nao estao na pasta de dados.

Assim quem baixou so parte dos datasets (ex.: so o 001, que vem no repositorio) roda a suite sem falhas falsas:
o que tem dado e testado, o resto aparece como "skipped" com o motivo.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

from nucleo import leitura  # noqa: E402
from nucleo.contratos import MODULOS  # noqa: E402

POR_ARQUIVO = {"test_churn.py": ["churn"], "test_suporte.py": ["suporte"], "test_leads.py": ["leads"],
               "test_midia.py": ["midia"]}


def _faltando(modulos):
    pasta = leitura.pasta_dados_desafio()
    if pasta is None:
        return ["pasta de dados"]
    return [t.arquivo_desafio for m in modulos for t in MODULOS[m].tabelas
            if not os.path.exists(os.path.join(pasta, t.arquivo_desafio))]


def pytest_collection_modifyitems(config, items):
    for item in items:
        arquivo = os.path.basename(str(item.fspath))
        if arquivo == "test_nucleo.py" and item.get_closest_marker("skipif") is None:
            continue   # testes do nucleo que nao usam dados
        falta = _faltando(POR_ARQUIVO.get(arquivo, list(MODULOS)))
        if falta:
            item.add_marker(pytest.mark.skip(reason="dados do desafio ausentes: " + ", ".join(falta[:3])))
