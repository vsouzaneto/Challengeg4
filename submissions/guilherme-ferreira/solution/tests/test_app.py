from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from app.leitura import ResumoAusente, ler_resumo
from app.tema import RODAPE
from src.formato import percentual_br

PASTA_APP = Path(__file__).resolve().parents[1] / "app"
PAGINAS = PASTA_APP / "paginas"


def abrir(pagina, timeout=30):
    return AppTest.from_file(str(PAGINAS / pagina), default_timeout=timeout).run()


def valor_em_dolar(texto):
    return int(texto.replace("US$", "").replace(".", "").strip())


def test_ler_resumo_ausente_diz_como_gerar(tmp_path):
    with pytest.raises(ResumoAusente, match="gerar_resumos.py"):
        ler_resumo("semanas.csv", tmp_path)


def test_ler_resumo_com_coluna_faltando_diz_qual(tmp_path):
    pd.DataFrame({"semana": ["2025-05-19"], "posts": [10]}).to_csv(tmp_path / "semanas.csv", index=False)

    with pytest.raises(ResumoAusente, match="dias"):
        ler_resumo("semanas.csv", tmp_path)


def test_ler_resumo_converte_semana_em_data():
    semanas = ler_resumo("semanas.csv", PASTA_APP / "resumos")

    assert semanas["semana"].dtype.kind == "M"
    assert len(semanas) > 100


def test_brief_abre_com_veredito_e_seis_indicadores():
    at = abrir("brief.py")

    assert not at.exception
    assert len(at.metric) == 6
    assert any("não mude o mix" in m.value for m in at.markdown)


def test_brief_gasto_acompanha_o_custo_por_post():
    at = abrir("brief.py")
    gasto_1500 = valor_em_dolar(next(m.value for m in at.metric if m.label == "Gasto nas práticas a parar"))

    at.slider(key="custo_por_post").set_value(1000).run()
    gasto_1000 = valor_em_dolar(next(m.value for m in at.metric if m.label == "Gasto nas práticas a parar"))

    assert gasto_1000 * 3 == gasto_1500 * 2


def test_brief_sem_resumos_mostra_como_gerar(tmp_path, monkeypatch):
    monkeypatch.setenv("RADAR_RESUMOS", str(tmp_path))

    at = abrir("brief.py")

    assert not at.exception
    assert any("gerar_resumos.py" in e.value for e in at.error)


def test_saude_mostra_veredito_e_numeros_do_laudo():
    laudo = dict(zip(*ler_resumo("laudo.csv", PASTA_APP / "resumos").T.values))

    at = abrir("saude.py")
    textos = " ".join(m.value for m in at.markdown)

    assert not at.exception
    assert "Resultado: sem sinal. Operação: sem critério." in textos
    assert all(f"Teste {i}" in textos for i in range(1, 5))
    assert percentual_br(laudo["fit"], 1) in textos
    assert f"em {percentual_br(laudo['fit'], 1)} dos posts patrocinados" in textos
    assert percentual_br(laudo["patrocinadores_um_post"], 1) in textos


PLATAFORMAS = ["Bilibili", "Instagram", "RedNote", "TikTok", "YouTube"]


def test_mapa_filtra_por_mais_de_uma_plataforma():
    at = abrir("mapa.py")
    assert not at.exception
    assert all(at.checkbox(key=f"plataforma_{p}").value for p in PLATAFORMAS)
    assert len(at.table[0].value) == 60

    for plataforma in ["Bilibili", "Instagram", "RedNote"]:
        at.checkbox(key=f"plataforma_{plataforma}").uncheck().run()

    assert len(at.table[0].value) == 24  # 2 plataformas (TikTok e YouTube) x 3 categorias x 4 formatos


def test_mapa_sem_celulas_mostra_aviso():
    at = abrir("mapa.py")

    for plataforma in PLATAFORMAS:
        at.checkbox(key=f"plataforma_{plataforma}").uncheck().run()

    assert not at.exception
    assert any("Nenhuma célula com esses filtros." in i.value for i in at.info)


def metrica(at, rotulo):
    return next(m.value for m in at.metric if m.label == rotulo)


def test_calculadora_padrao_e_20_por_cento_com_cv_1():
    at = abrir("calculadora.py")

    assert not at.exception
    assert metrica(at, "Posts por grupo") == "393"
    assert metrica(at, "Semanas") == "4"


def test_calculadora_responde_as_tres_perguntas():
    at = abrir("calculadora.py")

    at.radio(key="efeito").set_value("10%").run()
    at.number_input(key="posts_semana").set_value(100).run()

    assert metrica(at, "Posts por grupo") == "1.570"
    assert metrica(at, "Semanas") == "32"  # 2 x 1.570 / 100 = 31,4, arredondado para cima


def test_calculadora_outro_efeito_tem_minimo_de_1():
    at = abrir("calculadora.py")

    at.radio(key="efeito").set_value("Outro").run()

    assert at.number_input(key="efeito_outro").min == 1


def test_calculadora_mostra_a_hipotese_escolhida():
    at = abrir("calculadora.py")

    at.radio(key="hipotese").set_value("H1 · fit").run()

    assert any("60,1%" in m.value for m in at.markdown)


def test_radar_abre_no_brief_com_rodape():
    at = AppTest.from_file(str(PASTA_APP / "radar.py"), default_timeout=30).run()

    assert not at.exception
    assert any("Brief da" in m.value for m in at.markdown)
    assert any(RODAPE in m.value for m in at.markdown)


def test_radar_navega_ate_a_calculadora():
    at = AppTest.from_file(str(PASTA_APP / "radar.py"), default_timeout=30).run()

    at.switch_page("paginas/calculadora.py").run()

    assert not at.exception
    assert any(m.label == "Posts por grupo" for m in at.metric)


def test_brief_semana_sem_grupos_para_comparar(tmp_path, monkeypatch):
    # 40 posts, todos no Instagram, em vídeo e em beauty: nenhum grupo tem com quem se comparar.
    semana = "2025-05-19"
    pd.DataFrame({"semana": [semana], "dias": [7], "ultimo_post": ["2025-05-25 20:00"], "posts": [40], "patrocinados": [0],
                  "sem_fit": [0], "implicita": [0], "so_hashtag": [0], "um_post_so": [0], "algum_problema": [0]}
                 ).to_csv(tmp_path / "semanas.csv", index=False)
    pd.DataFrame({"semana": [semana] * 4, "dimensao": ["platform", "content_type", "content_category", "total"],
                  "valor": ["Instagram", "video", "beauty", "total"], "n": [40] * 4, "media": [0.2] * 4, "var": [0.0001] * 4}
                 ).to_csv(tmp_path / "semanas_grupos.csv", index=False)
    monkeypatch.setenv("RADAR_RESUMOS", str(tmp_path))

    at = abrir("brief.py")

    assert not at.exception
    assert any("Não há grupos para comparar" in i.value for i in at.info)


def test_mapa_com_intervalos_indefinidos_nao_quebra(tmp_path, monkeypatch):
    pd.DataFrame(
        {"objetivo": ["engajamento"] * 2, "platform": ["TikTok", "YouTube"], "content_category": ["beauty"] * 2,
         "content_type": ["video"] * 2, "n": [1, 1], "media": [0.2, 0.2], "media_resto": [0.2, 0.2], "lift": [0.0, 0.0],
         "ic_inf": [float("nan")] * 2, "ic_sup": [float("nan")] * 2, "p": [float("nan")] * 2,
         "p_ajustado": [float("nan")] * 2, "classe": ["poucos posts"] * 2}
    ).to_csv(tmp_path / "celulas.csv", index=False)
    monkeypatch.setenv("RADAR_RESUMOS", str(tmp_path))

    at = abrir("mapa.py")

    assert not at.exception
    assert len(at.table[0].value) == 2
