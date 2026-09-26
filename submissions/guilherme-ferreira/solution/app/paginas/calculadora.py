import sys
from pathlib import Path

PASTA_APP = Path(__file__).resolve().parents[1]
for pasta in (PASTA_APP, PASTA_APP.parent):
    if str(pasta) not in sys.path:
        sys.path.insert(0, str(pasta))

import streamlit as st  # noqa: E402

import tema  # noqa: E402
from src.experimentos import amostra_por_grupo, duracao_semanas  # noqa: E402
from src.formato import numero_br  # noqa: E402

HIPOTESES = {
    "Nenhuma": None,
    "H1 · fit": (
        "Porque 60,1% dos patrocínios não têm relação com o conteúdo, acreditamos que patrocinar só conteúdo compatível "
        "vai aumentar as vendas com cupom por post em 20% ou mais.",
        "Vendas com cupom por post", "Cliques por mil views", "Custo por post; divulgação correta",
    ),
    "H2 · parceria recorrente": (
        "Porque 90% dos patrocinadores aparecem num post só, acreditamos que o segundo post do mesmo patrocinador com o mesmo "
        "creator vai gerar 20% ou mais vendas com cupom do que o primeiro post de um patrocinador novo.",
        "Vendas com cupom por post", "Comentários por view", "Engajamento não cai mais de 10%",
    ),
    "H3 · portfólio micro e nano": (
        "Porque o arquivo não permite escolher creator por tamanho, acreditamos que dividir o orçamento entre creators micro "
        "e nano vai reduzir o custo por venda em 20% ou mais em relação a creators macro.",
        "Custo por venda", "Vendas por post", "Alcance total da campanha",
    ),
}
EFEITOS = {"10%": 0.10, "20%": 0.20, "30%": 0.30, "Outro": None}
VARIACOES = {"Pouca (CV 0,5)": 0.5, "Média (CV 1)": 1.0, "Muita (CV 2)": 2.0, "Outra": None}


def main():
    tema.cabecalho("Calculadora de", "teste")

    escolha = st.radio("Começar de uma hipótese da estratégia", list(HIPOTESES), horizontal=True, key="hipotese")
    if HIPOTESES[escolha]:
        texto, principal, secundaria, guardrail = HIPOTESES[escolha]
        with st.container(border=True, key="cartao_hipotese"):
            st.markdown(texto)
            st.markdown(f"**Métrica principal:** {principal}. **Secundária:** {secundaria}. **Não pode piorar:** {guardrail}.")

    rotulo_efeito = st.radio("1. Qual é o menor efeito que vale detectar?", list(EFEITOS), index=1, horizontal=True, key="efeito")
    efeito = EFEITOS[rotulo_efeito]
    if efeito is None:
        efeito = st.number_input("Efeito mínimo (%)", min_value=1, max_value=100, value=15, step=1, key="efeito_outro") / 100

    rotulo_variacao = st.radio(
        "2. Quanto a métrica varia de um post para outro?", list(VARIACOES), index=1, horizontal=True, key="variacao",
        help="Coeficiente de variação (CV): desvio-padrão dividido pela média. O rastreamento mede o valor real em duas semanas.",
    )
    cv = VARIACOES[rotulo_variacao]
    if cv is None:
        cv = st.number_input("Coeficiente de variação", min_value=0.1, max_value=10.0, value=1.5, step=0.1, key="cv_outro")

    posts_semana = st.number_input(
        "3. Quantos posts por semana entram no teste?", min_value=1, value=214, step=1, key="posts_semana",
        help="Padrão: os 214 posts patrocinados por semana de hoje.",
    )

    n = amostra_por_grupo(efeito, cv)
    semanas = duracao_semanas(n, posts_semana)
    esquerda, direita = st.columns(2)
    esquerda.metric("Posts por grupo", numero_br(n), border=True)
    direita.metric("Semanas", numero_br(semanas), border=True)
    st.markdown(
        f"Com dois grupos sorteados, o teste precisa de {numero_br(2 * n)} posts no total: cerca de {numero_br(semanas)} "
        "semanas no volume informado. Defina o tamanho antes de começar e não encerre antes da hora."
    )


main()
