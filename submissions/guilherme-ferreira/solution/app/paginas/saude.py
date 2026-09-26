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
from src.formato import numero_br, percentual_br  # noqa: E402


def cartao(titulo, pergunta, numero, leitura):
    with st.container(border=True, key=f"cartao_{titulo.split()[-1]}"):
        st.markdown(f"**{titulo}.** {pergunta}")
        st.markdown(f"### {numero}")
        st.markdown(leitura)


def main():
    tema.cabecalho("Saúde do", "dado")
    resumos = carregar_resumos("laudo.csv", "simulacao.csv")
    if resumos is None:
        return
    laudo = dict(zip(resumos[0]["chave"], resumos[0]["valor"]))
    simulacao = resumos[1]

    st.markdown("## Resultado: sem sinal. Operação: sem critério.")
    st.markdown(
        "O arquivo não diz o que funciona, porque todo post rende igual dentro do sorteio. "
        "Mas diz como a operação trabalha: patrocina sem relação com o conteúdo, espalha patrocínio e divulga mal."
    )

    indices = [laudo[k] for k in ("indice_views", "indice_likes", "indice_shares", "indice_comentarios")]
    esquerda, direita = st.columns(2)
    with esquerda:
        cartao(
            "Teste 1", "Cada métrica é um sorteio em torno de um valor fixo?",
            f"Índice de dispersão de {numero_br(min(indices), 3)} a {numero_br(max(indices), 3)}",
            "Perto de 1: nada além do acaso explica a diferença entre um post e outro.",
        )
        cartao(
            "Teste 3", "A operação escolhe com critério?",
            f"Patrocinador combina com o conteúdo em {percentual_br(laudo['fit'], 1)} dos posts patrocinados",
            f"Igual ao que daria um sorteio ({percentual_br(laudo['fit_sorteio'], 1)}). "
            f"{percentual_br(laudo['patrocinadores_um_post'], 1)} dos patrocinadores aparecem num post só. "
            f"Formatos em proporção redonda: vídeo {percentual_br(laudo['formato_video'], 1)}, "
            f"imagem {percentual_br(laudo['formato_image'], 1)}.",
        )
    with direita:
        cartao(
            "Teste 2", "O tamanho do creator é confiável?",
            f"{percentual_br(laudo['creators_seguidores_variam'], 1)} dos creators mudam de tamanho entre posts",
            f"Na mediana, o maior número do mesmo creator é {numero_br(laudo['razao_seguidores_mediana'], 1)} vezes o menor. "
            "A faixa do creator fica fora das conclusões.",
        )
        cartao(
            "Teste 4", "Os textos são reais?",
            f"{numero_br(laudo['posts_lingua_com_escrita'])} de {numero_br(laudo['posts_lingua_nao_latina'])} posts",
            "em chinês, japonês ou hindi têm algum caractere da língua. Descrições e comentários são palavras sorteadas.",
        )

    st.subheader("O método acha efeitos quando eles existem")
    st.markdown(
        "Numa cópia do dado, plantamos efeitos conhecidos (+15%, +10% e +3%) em células sorteadas e rodamos o mesmo "
        "método, 200 vezes para cada efeito. Nenhum número das outras telas vem dessa cópia."
    )
    tabela = pd.DataFrame(
        {
            "Efeito plantado": simulacao["efeito"].map(lambda v: percentual_br(v, 0, sinal=True)),
            "Vira sinal": simulacao["taxa_sinal"].map(lambda v: percentual_br(v, 1)),
            "Percebido, abaixo do limiar": simulacao["taxa_abaixo_do_limiar"].map(lambda v: percentual_br(v, 1)),
            "Efeito medido": simulacao["lift_medido_medio"].map(lambda v: percentual_br(v, 2, sinal=True)),
            "Falsos sinais por rodada": simulacao["falsos_positivos_por_rodada"].map(lambda v: numero_br(v, 2)),
        }
    )
    st.table(tabela.style.hide(axis="index"))
    st.caption("+10% é a fronteira: a regra pede diferença acima de 10%, então esse efeito vira sinal em cerca de metade das rodadas.")


main()
