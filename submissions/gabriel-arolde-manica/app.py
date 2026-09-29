import pandas as pd
import streamlit as st
import plotly.express as px

from solution.scoring import (
    calculate_product_win_rates,
    calculate_score
)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="DealPilot",
    page_icon="🎯",
    layout="wide"
)


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

@st.cache_data
def load_data():

    pipeline = pd.read_csv(
        "data/sales_pipeline.csv"
    )

    accounts = pd.read_csv(
        "data/accounts.csv"
    )

    teams = pd.read_csv(
        "data/sales_teams.csv"
    )

    pipeline["engage_date"] = pd.to_datetime(
        pipeline["engage_date"],
        errors="coerce"
    )

    pipeline["close_date"] = pd.to_datetime(
        pipeline["close_date"],
        errors="coerce"
    )

    pipeline = pipeline.merge(
        accounts[
            [
                "account",
                "revenue",
                "employees"
            ]
        ],
        on="account",
        how="left"
    )

    pipeline = pipeline.merge(
        teams[
            [
                "sales_agent",
                "manager",
                "regional_office"
            ]
        ],
        on="sales_agent",
        how="left"
    )

    return pipeline


# ============================================================
# SCORING
# ============================================================

def score_pipeline(pipeline):

    product_win_rates = (
        calculate_product_win_rates(
            pipeline
        )
    )

    open_deals = pipeline[
        pipeline["deal_stage"].isin(
            [
                "Prospecting",
                "Engaging"
            ]
        )
    ].copy()

    reference_date = pipeline[
        "engage_date"
    ].max()

    results = []

    for _, deal in open_deals.iterrows():

        result = calculate_score(
            deal,
            product_win_rates,
            reference_date
        )

        results.append(
            {
                "opportunity_id":
                    deal["opportunity_id"],

                "sales_agent":
                    deal["sales_agent"],

                "manager":
                    deal["manager"],

                "regional_office":
                    deal["regional_office"],

                "product":
                    deal["product"],

                "account":
                    deal["account"],

                "stage":
                    deal["deal_stage"],

                "revenue":
                    deal["revenue"],

                "employees":
                    deal["employees"],

                "score":
                    result["score"],

                "reasons":
                    result["reasons"],

                "risk_flags":
                    result["risk_flags"]
            }
        )

    return pd.DataFrame(results)


# ============================================================
# CARREGAR
# ============================================================

pipeline = load_data()

scored = score_pipeline(
    pipeline
)


# ============================================================
# HEADER
# ============================================================

st.title("🎯 DealPilot")

st.subheader(
    "Prioridade inteligente para oportunidades comerciais"
)

st.caption(
    "O Priority Score indica quais oportunidades "
    "merecem atenção primeiro. Ele não representa "
    "probabilidade de fechamento."
)


# ============================================================
# SIDEBAR — FILTROS
# ============================================================

st.sidebar.header(
    "Filtros"
)

agents = sorted(
    scored["sales_agent"]
    .dropna()
    .unique()
)

selected_agent = st.sidebar.multiselect(
    "Vendedor",
    agents
)

managers = sorted(
    scored["manager"]
    .dropna()
    .unique()
)

selected_manager = st.sidebar.multiselect(
    "Gerente",
    managers
)

regions = sorted(
    scored["regional_office"]
    .dropna()
    .unique()
)

selected_region = st.sidebar.multiselect(
    "Região",
    regions
)

stages = sorted(
    scored["stage"]
    .dropna()
    .unique()
)

selected_stage = st.sidebar.multiselect(
    "Etapa",
    stages
)


# ============================================================
# APLICAR FILTROS
# ============================================================

filtered = scored.copy()

if selected_agent:

    filtered = filtered[
        filtered["sales_agent"].isin(
            selected_agent
        )
    ]

if selected_manager:

    filtered = filtered[
        filtered["manager"].isin(
            selected_manager
        )
    ]

if selected_region:

    filtered = filtered[
        filtered["regional_office"].isin(
            selected_region
        )
    ]

if selected_stage:

    filtered = filtered[
        filtered["stage"].isin(
            selected_stage
        )
    ]


# ============================================================
# KPIs
# ============================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Oportunidades abertas",
    len(filtered)
)

col2.metric(
    "Score médio",
    f"{filtered['score'].mean():.1f}"
    if len(filtered)
    else "0"
)

col3.metric(
    "Alta prioridade",
    len(
        filtered[
            filtered["score"] >= 80
        ]
    )
)

col4.metric(
    "Em Engaging",
    len(
        filtered[
            filtered["stage"] == "Engaging"
        ]
    )
)


st.divider()


# ============================================================
# GRÁFICO
# ============================================================

left, right = st.columns(2)


with left:

    st.subheader(
        "Distribuição de prioridade"
    )

    fig = px.histogram(
        filtered,
        x="score",
        nbins=20,
        labels={
            "score": "Priority Score"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


with right:

    st.subheader(
        "Oportunidades por etapa"
    )

    stage_counts = (
        filtered["stage"]
        .value_counts()
        .reset_index()
    )

    stage_counts.columns = [
        "stage",
        "count"
    ]

    fig_stage = px.bar(
        stage_counts,
        x="stage",
        y="count",
        labels={
            "stage": "Etapa",
            "count": "Oportunidades"
        }
    )

    st.plotly_chart(
        fig_stage,
        use_container_width=True
    )


# ============================================================
# TOP PRIORIDADES
# ============================================================

st.divider()

st.header(
    "🔥 O que atacar primeiro"
)

top_deals = (
    filtered
    .sort_values(
        [
            "score",
            "opportunity_id"
        ],
        ascending=[
            False,
            True
        ]
    )
    .head(20)
    .copy()
)

display_columns = [
    "opportunity_id",
    "sales_agent",
    "product",
    "stage",
    "score",
    "account"
]

st.dataframe(
    top_deals[
        display_columns
    ],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DETALHE DA OPORTUNIDADE
# ============================================================

st.divider()

st.header(
    "🔎 Por que essa oportunidade?"
)

if len(filtered) > 0:

    selected_opportunity = st.selectbox(
        "Selecione uma oportunidade",
        filtered[
            "opportunity_id"
        ].tolist()
    )

    deal = filtered[
        filtered["opportunity_id"]
        == selected_opportunity
    ].iloc[0]

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Priority Score",
            int(deal["score"])
        )

        st.write(
            f"**Vendedor:** {deal['sales_agent']}"
        )

        st.write(
            f"**Produto:** {deal['product']}"
        )

        st.write(
            f"**Etapa:** {deal['stage']}"
        )

        st.write(
            f"**Conta:** {deal['account']}"
        )

    with col2:

        st.subheader(
            "Motivos do score"
        )

        for reason in deal["reasons"]:

            st.success(
                reason
            )

        if deal["risk_flags"]:

            st.subheader(
                "⚠️ Alertas"
            )

            for risk in deal["risk_flags"]:

                st.warning(
                    risk
                )


# ============================================================
# RODAPÉ
# ============================================================

st.divider()

st.caption(
    "DealPilot • AI Master Challenge • "
    "Priority scoring baseado em dados históricos "
    "e regras explicáveis."
)
