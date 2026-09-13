import pandas as pd
import streamlit as st

from ui import as_bool, demonstrative_banner, footer, fmt_money, load_table, page_header


page_header(
    "05 · DO DIAGNÓSTICO À AÇÃO",
    "Plano recomendado por prioridade, evidência e impacto",
    "A primeira ação não é uma campanha de retenção: é recuperar a capacidade de medir. A triagem começa "
    "em shadow mode; intervenções só começam após os gates, em experimentos controlados.",
)
demonstrative_banner()

triage = load_table("account_triage")
candidates = triage[~as_bool(triage["snapshot_churn_flag"])].copy()

actions = pd.DataFrame(
    [
        ["P0", "Instrumentação", "Mapear a origem dos eventos, definir state machine e contrato de IDs/datas", "Data + Engenharia", "% eventos válidos; conflitos por 1k eventos", "Recupera capacidade de decisão", "Alta"],
        ["P0", "Qualidade", "Quarentenar eventos impossíveis e criar testes bloqueantes no pipeline", "Analytics Engineering", "% quarentena; tempo de detecção", "Evita KPIs e alertas falsos", "Alta"],
        ["P0", "Pesquisa externa", "Se houver urgência, ouvir clientes ativos, churnados e reativados com roteiro único", "CS + Produto", "taxa de resposta; temas recorrentes", "Cria evidência independente", "Alta"],
        ["P1", "Revisão operacional", "Revisar manualmente contas de maior exposição e baixa confiança", "CS + Suporte", "contas validadas; correções de status", "Reduz risco imediato", "Média"],
        ["P2", "Shadow mode", "Gerar fila diária de triagem sem contato automático", "CS Ops", "precisão manual; cobertura; falsos positivos", "Valida utilidade do score", "Média"],
        ["P3", "Experimentos", "Testar playbooks por sinal com grupo controle", "CS + Produto", "uplift de retenção; custo por conta", "Estima impacto causal", "Baixa hoje"],
    ],
    columns=["Prioridade", "Frente", "Ação concreta", "Dono", "KPI", "Impacto esperado", "Confiança"],
)
st.dataframe(actions, use_container_width=True, hide_index=True)

st.subheader("Rota de curto prazo fora da telemetria")
c1, c2, c3 = st.columns(3)
c1.info("**Clientes:** satisfação, entrevistas de churn, pedidos de melhoria e win/loss.")
c2.info("**CS e Suporte:** revisão de casos, escalonamentos, promessas comerciais e objeções recorrentes.")
c3.info("**Produto:** bugs confirmados, lacunas de adoção e fricções reproduzidas qualitativamente.")

st.subheader("Simulação transparente de oportunidade")
st.info(
    "Esta simulação dimensiona quanto da receita mensal associada às contas selecionadas poderia ser preservada "
    "em um cenário hipotético. Primeiro escolha os grupos que receberiam atenção; depois informe qual parcela da "
    "exposição seria mantida. O resultado não prevê churn nem mede o efeito real da ação."
)
eligible_bands = list(candidates["triage_band"].dropna().unique())
default_bands = [band for band in ["Critical", "High"] if band in eligible_bands]
selected = st.multiselect("Grupos de triagem incluídos", eligible_bands, default=default_bands)
uplift = st.slider("Percentual hipotético da exposição mensal preservada", 0, 30, 10, 5)
scenario = candidates[candidates["triage_band"].isin(selected)] if selected else candidates.iloc[0:0]
lower_base = scenario["mrr_proxy_conservative"].sum(min_count=1)
upper_base = scenario["mrr_proxy_additive"].sum(min_count=1)
lower = (lower_base * uplift / 100) if pd.notna(lower_base) else None
upper = (upper_base * uplift / 100) if pd.notna(upper_base) else None
s1, s2, s3 = st.columns(3)
s1.metric("Contas que receberiam a ação", len(scenario))
s2.metric("Receita potencial preservada · conservadora", fmt_money(lower, True) if lower is not None else "Indisponível")
s3.metric("Receita potencial preservada · aditiva", fmt_money(upper, True) if upper is not None else "Indisponível")
if "Data gap" in selected:
    st.warning("O grupo Data gap tem evidência insuficiente. Incluí-lo dimensiona revisão manual, não uma campanha de retenção.")
st.warning(
    "Para converter oportunidade em ROI são necessários custo da ação, margem e uplift causal observado. "
    "Esses campos não existem na base e não serão inventados."
)

st.subheader("Critério para sair do shadow mode")
st.markdown(
    "1. Cobertura e integridade dentro da meta por quatro semanas.  \n"
    "2. Status de conta reconciliado entre CRM, billing e produto.  \n"
    "3. Fila validada manualmente com falso positivo aceitável.  \n"
    "4. Experimento controlado demonstrando uplift e custo da intervenção."
)
footer()
