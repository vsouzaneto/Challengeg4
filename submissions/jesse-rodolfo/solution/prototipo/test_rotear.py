import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rotear import carregar, rotear  # noqa: E402


@pytest.fixture(scope="module")
def modelo():
    return carregar()


def test_modelo_carrega(modelo):
    assert set(modelo.classes_) == {"Access", "Administrative rights", "HR Support", "Hardware",
                                    "Internal Project", "Miscellaneous", "Purchase", "Storage"}


def test_texto_vazio_vai_para_humano(modelo):
    assert rotear("", modelo)["rota"] == "humano"
    assert rotear("   ", modelo)["rota"] == "humano"


def test_confianca_baixa_vai_para_humano(modelo):
    r = rotear("bom dia gostaria de uma informacao", modelo, limiar=0.999)
    assert r["rota"] == "humano" and r["motivo"] == "confiança abaixo do limiar"


def test_portao_vai_para_humano_mesmo_com_confianca_alta(modelo):
    r = rotear("new purchase po allocation please log allocation after receive item order", modelo,
               limiar=0.0, portoes={"Purchase"})
    assert r["categoria"] == "Purchase" and r["confianca"] >= 0.9
    assert r["rota"] == "humano" and r["motivo"] == "portão de autoridade"


def test_texto_claro_acerta_a_categoria(modelo):
    r = rotear("new purchase po allocation purchase po dear purchased please log allocation "
               "after receive item order kind regards administrator", modelo)
    assert r["categoria"] == "Purchase"
