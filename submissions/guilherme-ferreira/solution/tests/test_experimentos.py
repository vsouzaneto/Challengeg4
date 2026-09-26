import math

import pytest
from statsmodels.stats.power import NormalIndPower

from src.experimentos import amostra_por_grupo, duracao_semanas


def test_amostra_por_grupo_segue_a_formula_de_duas_medias():
    # 2 x (1,96 + 0,84)² x (CV / MDE)² = 1.569,8, arredondado para cima
    assert amostra_por_grupo(mde=0.10, cv=1.0) == 1570


def test_amostra_por_grupo_bate_com_o_statsmodels():
    referencia = NormalIndPower().solve_power(effect_size=0.20 / 1.5, alpha=0.05, power=0.8, ratio=1)

    assert amostra_por_grupo(mde=0.20, cv=1.5) == math.ceil(referencia)


@pytest.mark.parametrize(
    "n_por_grupo, posts_por_semana, grupos, esperado",
    [(1570, 214, 2, 15), (393, 214, 2, 4), (100, 50, 3, 6)],
)
def test_duracao_semanas_arredonda_para_cima(n_por_grupo, posts_por_semana, grupos, esperado):
    assert duracao_semanas(n_por_grupo, posts_por_semana, grupos) == esperado
