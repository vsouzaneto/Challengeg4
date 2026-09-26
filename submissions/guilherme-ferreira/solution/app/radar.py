"""Radar de Conteúdo: entrada do app.

Rodar, a partir da raiz do repositório (como no Streamlit Cloud):
    streamlit run submissions/guilherme-ferreira/solution/app/radar.py
"""
import sys
from pathlib import Path

PASTA_APP = Path(__file__).resolve().parent
for pasta in (PASTA_APP, PASTA_APP.parent):
    if str(pasta) not in sys.path:
        sys.path.insert(0, str(pasta))

import streamlit as st  # noqa: E402

import tema  # noqa: E402

st.set_page_config(page_title="Radar de Conteúdo", layout="wide")
tema.aplicar()
paginas = [
    st.Page(PASTA_APP / "paginas" / "brief.py", title="Brief de segunda", default=True),
    st.Page(PASTA_APP / "paginas" / "saude.py", title="Saúde do dado"),
    st.Page(PASTA_APP / "paginas" / "mapa.py", title="Mapa de sinal e ruído"),
    st.Page(PASTA_APP / "paginas" / "calculadora.py", title="Calculadora de teste"),
]
st.navigation(paginas, position="top").run()
tema.rodape()
