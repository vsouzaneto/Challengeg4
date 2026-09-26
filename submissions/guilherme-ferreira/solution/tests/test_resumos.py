import pandas as pd
import pytest

from src.metricas import adicionar_metricas
from src.resumos import (
    marcar_problemas,
    resumo_celulas,
    resumo_laudo,
    resumo_semanas,
    resumo_semanas_grupos,
    semana,
)


def test_semana_comeca_na_segunda():
    datas = pd.Series(pd.to_datetime(["2025-05-28 11:08", "2025-05-25 23:00", "2025-05-19 00:15"]))

    assert semana(datas).tolist() == [pd.Timestamp("2025-05-26"), pd.Timestamp("2025-05-19"), pd.Timestamp("2025-05-19")]


def test_marcar_problemas_por_post(posts_minimos):
    marcas = marcar_problemas(posts_minimos)

    # post 0: cosméticos em beauty, explícito, Acme tem 2 posts -> nenhum problema
    # post 1: games em beauty (sem fit), implícito, só hashtag
    # post 2: comida em lifestyle (fit), implícito, Beta tem 1 post
    assert marcas["sem_fit"].tolist() == [False, True, False, False, False, False]
    assert marcas["implicita"].tolist() == [False, True, True, False, False, False]
    assert marcas["so_hashtag"].tolist() == [False, True, False, False, False, False]
    assert marcas["um_post_so"].tolist() == [False, False, True, False, False, False]
    assert marcas["algum_problema"].tolist() == [False, True, True, False, False, False]


def test_resumo_semanas_conta_por_semana(posts_minimos):
    tabela = resumo_semanas(posts_minimos).set_index("semana")

    assert tabela.loc[pd.Timestamp("2025-05-19")].to_dict() == {
        "dias": 4, "ultimo_post": pd.Timestamp("2025-05-25 18:00"), "posts": 4, "patrocinados": 2, "sem_fit": 1,
        "implicita": 1, "so_hashtag": 1, "um_post_so": 0, "algum_problema": 1,
    }
    assert tabela.loc[pd.Timestamp("2025-05-26")].to_dict() == {
        "dias": 2, "ultimo_post": pd.Timestamp("2025-05-28 08:00"), "posts": 2, "patrocinados": 1, "sem_fit": 0,
        "implicita": 1, "so_hashtag": 0, "um_post_so": 1, "algum_problema": 1,
    }


def test_resumo_semanas_grupos_tem_grupos_e_total(posts_minimos):
    tabela = resumo_semanas_grupos(adicionar_metricas(posts_minimos))
    semana_19 = tabela[tabela["semana"] == pd.Timestamp("2025-05-19")].set_index(["dimensao", "valor"])

    assert semana_19.loc[("platform", "TikTok"), "n"] == 2
    assert semana_19.loc[("platform", "YouTube"), "n"] == 2
    assert semana_19.loc[("total", "total"), "n"] == 4
    assert semana_19.loc[("total", "total"), "media"] == pytest.approx((13 / 100 + 16 / 110 + 13 / 100 + 12 / 95) / 4)


def test_resumo_celulas_empilha_os_quatro_objetivos(posts_minimos):
    tabela = resumo_celulas(adicionar_metricas(posts_minimos))

    assert set(tabela["objetivo"]) == {"engajamento", "alcance", "conversa", "compartilhamento"}
    assert len(tabela) == 4 * tabela.groupby("objetivo").size().iloc[0]


def test_resumo_laudo_traz_os_numeros_da_saude_do_dado(posts_minimos):
    laudo = dict(zip(*resumo_laudo(posts_minimos).T.values))

    assert laudo["posts"] == 6
    assert laudo["patrocinados"] == 3
    assert laudo["fit"] == pytest.approx(2 / 3)
    assert laudo["implicita"] == pytest.approx(2 / 3)
    assert laudo["so_hashtag"] == pytest.approx(1 / 3)
    assert laudo["patrocinadores"] == 2
    assert laudo["patrocinadores_um_post"] == pytest.approx(0.5)
    assert laudo["creators"] == 3
    assert laudo["creators_seguidores_variam"] == pytest.approx(1 / 3)
    assert laudo["razao_seguidores_mediana"] == pytest.approx(1.0)
    assert laudo["posts_lingua_nao_latina"] == 3
    assert laudo["posts_lingua_com_escrita"] == 1
    assert laudo["formato_video"] == pytest.approx(0.5)
    assert laudo["categoria_beauty"] == pytest.approx(0.5)
