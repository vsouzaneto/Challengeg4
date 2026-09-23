"""Prepared offline app; navigation never downloads, trains or adjusts policies."""

import streamlit as st

from support_copilot.ui import apply_design_system, render_director_brief


def main() -> None:
    st.set_page_config(
        page_title="Support Decision Copilot",
        page_icon="◈",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_design_system()
    navigation = st.navigation([
        st.Page(
            render_director_brief,
            title="Resposta ao Diretor",
            icon=":material/strategy:",
            default=True,
        ),
        st.Page("pages/queue.py", title="Fila diária", icon=":material/inbox:"),
        st.Page("pages/scorecard.py", title="Scorecard", icon=":material/monitoring:"),
        st.Page("pages/it_lab.py", title="Laboratório IT", icon=":material/science:"),
        st.Page("pages/evidence.py", title="Evidências", icon=":material/fact_check:"),
    ])
    with st.spinner("Carregando artefatos locais e verificando integridade…"):
        navigation.run()


if __name__ == "__main__":
    main()
