"""Mesa de Suporte com IA — protótipo da Entrega 3 (Challenge 002).

Rodar a partir desta pasta:  streamlit run app.py
"""

import streamlit as st

from motor import config, llm

config.carregar_env()
st.set_page_config(page_title="Mesa de Suporte com IA", page_icon="🎧", layout="wide")

from telas import fila, painel  # noqa: E402

TELAS = {"Fila do agente": fila.render, "Painel do Diretor": painel.render}

escolha = st.sidebar.radio("Tela", list(TELAS), key="tela")
st.sidebar.divider()
st.sidebar.markdown("**LLM**")
st.sidebar.caption("Cadeia: " + " → ".join(llm.cadeia_padrao()))
for prov, ok in llm.chaves_presentes().items():
    st.sidebar.caption(f"{prov}: {'chave configurada' if ok else 'sem chave (a cadeia pula)'}")
st.sidebar.caption("Sem chave, os rascunhos vêm da base de conhecimento (template).")
TELAS[escolha]()
