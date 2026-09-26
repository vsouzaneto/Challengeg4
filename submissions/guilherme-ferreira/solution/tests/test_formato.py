import pytest

from src.formato import numero_br, percentual_br, resumo_selecao


@pytest.mark.parametrize(
    "valor, casas, esperado",
    [
        (52214, 0, "52.214"),
        (13.8, 1, "13,8"),
        (1234567.891, 2, "1.234.567,89"),
        (0.199, 3, "0,199"),
        (-6.25, 1, "-6,2"),
    ],
)
def test_numero_br_usa_ponto_no_milhar_e_virgula_no_decimal(valor, casas, esperado):
    assert numero_br(valor, casas) == esperado


@pytest.mark.parametrize(
    "fracao, casas, sinal, esperado",
    [
        (0.1234, 1, False, "12,3%"),
        (0.15, 0, True, "+15%"),
        (-0.0609, 1, True, "-6,1%"),
        (0.515, 1, False, "51,5%"),
    ],
)
def test_percentual_br(fracao, casas, sinal, esperado):
    assert percentual_br(fracao, casas, sinal) == esperado


def test_formato_mostra_traco_quando_nao_ha_numero():
    assert numero_br(float("nan")) == "—"
    assert percentual_br(float("nan"), 1, sinal=True) == "—"


@pytest.mark.parametrize(
    "marcados, total, esperado",
    [
        (["TikTok", "YouTube", "Instagram"], 3, "Todas"),
        ([], 3, "Nenhuma"),
        (["TikTok"], 5, "TikTok"),
        (["TikTok", "YouTube"], 5, "2 de 5"),
    ],
)
def test_resumo_selecao(marcados, total, esperado):
    assert resumo_selecao(marcados, total) == esperado
