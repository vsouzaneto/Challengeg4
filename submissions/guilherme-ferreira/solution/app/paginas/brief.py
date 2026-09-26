import sys
from pathlib import Path

PASTA_APP = Path(__file__).resolve().parents[1]
for pasta in (PASTA_APP, PASTA_APP.parent):
    if str(pasta) not in sys.path:
        sys.path.insert(0, str(pasta))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

import tema  # noqa: E402
from leitura import carregar_resumos  # noqa: E402
from src.brief import destaques_semana, indicadores_semana, semana_padrao, veredito  # noqa: E402
from src.formato import numero_br, percentual_br  # noqa: E402

NOMES = {"platform": "Plataforma", "content_type": "Formato", "content_category": "Categoria"}
QUICK_WINS = """
1. **Rastreamento mínimo:** registrar cada post e contrato, com UTM e cupom (plano de rastreamento).
2. **Auditoria de divulgação:** corrigir os patrocinados no ar com divulgação implícita ou só nas hashtags.
3. **Congelar patrocínio novo sem fit e sem objetivo** até a lista curta de creators ficar pronta.
4. **Seguidores de uma fonte só:** coletar toda semana, pela plataforma, com data.
"""


def tabela_destaques(destaques):
    return pd.DataFrame(
        {
            "": destaques["posicao"].map({"acima": "acima do resto", "abaixo": "abaixo do resto"}),
            "Grupo": destaques["dimensao"].map(NOMES) + ": " + destaques["valor"].astype(str),
            "Posts": destaques["n"].map(numero_br),
            "Diferença": destaques["lift"].map(lambda v: percentual_br(v, 2, sinal=True)),
            "Intervalo de 95%": [
                f"{percentual_br(a, 2, sinal=True)} a {percentual_br(b, 2, sinal=True)}"
                for a, b in zip(destaques["ic_inf"], destaques["ic_sup"])
            ],
            "Classe": destaques["classe"],
        }
    )


def main():
    tema.cabecalho("Brief da", "semana")
    resumos = carregar_resumos("semanas.csv", "semanas_grupos.csv")
    if resumos is None:
        return
    semanas, grupos = resumos

    opcoes = list(semanas["semana"].sort_values(ascending=False))
    padrao = semana_padrao(semanas)
    coluna_semana, coluna_custo = st.columns(2)
    semana = coluna_semana.selectbox(
        "Semana (de segunda a domingo)", opcoes, index=opcoes.index(padrao),
        format_func=lambda d: f"{d:%d/%m/%Y}", key="semana",
    )
    custo = coluna_custo.slider(
        "Custo médio por post patrocinado (US$)", 500, 5000, 1500, step=100, key="custo_por_post",
        help="Premissa declarada na estratégia: o arquivo do desafio não tem custo.",
    )

    ind = indicadores_semana(semanas, semana, custo)
    volume = st.columns(3)
    volume[0].metric("Posts", numero_br(ind["posts"]), border=True)
    volume[1].metric("Patrocinados", percentual_br(ind["patrocinados"], 1), border=True)
    volume[2].metric(
        "Gasto nas práticas a parar", "US$ " + numero_br(ind["gasto"]), border=True,
        help=f"{numero_br(ind['posts_com_problema'])} posts patrocinados com algum problema, vezes o custo por post.",
    )
    problemas = st.columns(3)
    problemas[0].metric("Sem fit", percentual_br(ind["sem_fit"], 1), border=True, help="Entre os patrocinados da semana.")
    problemas[1].metric("Divulgação implícita", percentual_br(ind["implicita"], 1), border=True, help="Entre os patrocinados da semana.")
    problemas[2].metric("Parceria de um post só", percentual_br(ind["um_post_so"], 1), border=True, help="Patrocinador que aparece uma vez em todo o histórico.")

    st.subheader("Top 3 e bottom 3 da semana")
    destaques = destaques_semana(grupos, semana)
    if destaques.empty:
        st.info("Não há grupos para comparar nesta semana.")
    else:
        st.markdown(f"**{veredito(destaques)}**")
        st.table(tabela_destaques(destaques).style.hide(axis="index"))
        st.caption("Cada grupo é comparado com os outros posts da mesma semana. " + tema.LEGENDA_CLASSES)

    st.subheader("Esta semana")
    st.markdown(QUICK_WINS)


main()
