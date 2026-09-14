from pathlib import Path

import streamlit as st

from ui import sidebar_footer, sidebar_header


st.set_page_config(
    page_title="RavenStack | Verdade antes do churn",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_DIR = Path(__file__).resolve().parent

sidebar_header()

pages = [
    st.Page(APP_DIR / "pages" / "01_capa.py", title="Capa", icon="🏠", default=True),
    st.Page(APP_DIR / "pages" / "02_qualidade.py", title="Qualidade e gate", icon="🧭"),
    st.Page(APP_DIR / "pages" / "03_one_page.py", title="One-page executivo", icon="📊"),
    st.Page(APP_DIR / "pages" / "04_diagnostico.py", title="Diagnóstico", icon="🔎"),
    st.Page(APP_DIR / "pages" / "05_risco.py", title="Triagem de risco", icon="🎯"),
    st.Page(APP_DIR / "pages" / "06_acoes.py", title="Plano de ação", icon="🛠️"),
]

navigation = st.navigation(pages, position="sidebar")
sidebar_footer()
navigation.run()
