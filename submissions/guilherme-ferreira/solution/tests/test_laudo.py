import pandas as pd
import pytest

from src.laudo import (
    indice_dispersao,
    proporcao_esperada_uniforme,
    usa_escrita_nao_latina,
    variacao_seguidores,
)


def test_indice_dispersao_e_variancia_amostral_sobre_media():
    # média 5; variância amostral (9 + 1 + 1 + 9) / 3 = 20/3
    assert indice_dispersao([2, 4, 6, 8]) == pytest.approx((20 / 3) / 5)


def test_variacao_seguidores_compara_maior_e_menor_valor_do_mesmo_creator():
    df = pd.DataFrame(
        {"creator_id": ["a", "a", "b", "b", "b"], "follower_count": [100, 250, 50, 50, 50]}
    )

    tabela = variacao_seguidores(df)

    assert tabela.loc["a", "razao"] == pytest.approx(2.5)
    assert tabela.loc["b", "razao"] == pytest.approx(1.0)


def test_proporcao_esperada_uniforme_por_faixa():
    limites = [0, 10_000, 50_000, 500_000, float("inf")]

    esperado = proporcao_esperada_uniforme(limites, minimo=1_000, maximo=1_000_000)

    total = 999_000
    assert esperado == pytest.approx(
        [9_000 / total, 40_000 / total, 450_000 / total, 500_000 / total]
    )


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("你好，世界", True),  # chinês
        ("こんにちは", True),  # japonês
        ("नमस्ते", True),  # hindi
        ("Professional radio usually something.", False),
        ("café com pão", False),  # latino com acento
        (None, False),
        (float("nan"), False),
    ],
)
def test_usa_escrita_nao_latina(texto, esperado):
    assert usa_escrita_nao_latina(texto) is esperado
