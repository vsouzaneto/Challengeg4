"""Tamanho de amostra e duração de testes que comparam a média de dois grupos de posts."""
import math

from scipy.stats import norm


def amostra_por_grupo(mde, cv, alfa=0.05, poder=0.8) -> int:
    """Posts por grupo para detectar uma diferença relativa `mde` (0,10 = 10%) numa métrica com
    coeficiente de variação `cv` (desvio-padrão dividido pela média), em teste bicaudal."""
    z = norm.ppf(1 - alfa / 2) + norm.ppf(poder)
    return math.ceil(2 * z**2 * (cv / mde) ** 2)


def duracao_semanas(n_por_grupo, posts_por_semana, grupos=2) -> int:
    return math.ceil(n_por_grupo * grupos / posts_por_semana)
