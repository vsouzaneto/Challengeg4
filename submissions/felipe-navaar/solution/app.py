"""Dashboard Streamlit do Lead Scorer, focado na exploração da carteira."""

from __future__ import annotations

import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.filters import filter_queue
from src.ingest import load_and_prepare
from src.scoring import score_open_opportunities


st.set_page_config(page_title="Lead Scorer | Dashboard", page_icon="🎯", layout="wide")

COLORS = {
    "background": "#070B14",
    "surface": "#101827",
    "surface_alt": "#172235",
    "text": "#F8FAFC",
    "muted": "#A7B4C8",
    "blue": "#60A5FA",
    "teal": "#2DD4BF",
    "amber": "#FBBF24",
    "red": "#FB7185",
    "grid": "#25334B",
}


@st.cache_data(show_spinner="Carregando oportunidades...")
def build_queue() -> pd.DataFrame:
    """Monta a visão da interface a partir das camadas do projeto."""

    enriched = load_and_prepare().enriched
    scored = score_open_opportunities(enriched)
    dimensions = enriched[
        [
            "opportunity_id",
            "account",
            "sales_agent",
            "manager",
            "regional_office",
            "product",
            "deal_stage",
            "sales_price",
            "engage_date",
        ]
    ]
    return scored.merge(dimensions, on="opportunity_id", how="left", validate="one_to_one")


def _display_account(value: object) -> str:
    return "Não informada" if pd.isna(value) else str(value)


def _display_label(value: object) -> str:
    return "Não informado" if pd.isna(value) else str(value)


def _display_price(value: object) -> str:
    return "Indisponível" if pd.isna(value) else f"US$ {float(value):,.2f}"


def _priority_label(score: int | float) -> str:
    return "Alta prioridade" if score >= 70 else "Em acompanhamento"


def _display_warnings(warnings: list[str]) -> list[str]:
    """Traduz avisos técnicos para pendências de informação da interface."""

    display = []
    for warning in warnings:
        if warning.startswith("account ausente"):
            display.append("Conta não informada")
        elif warning.startswith("engage_date ausente"):
            display.append("Data de engajamento não informada")
        elif warning.startswith("preço de catálogo indisponível"):
            display.append("Preço de catálogo indisponível")
        else:
            display.append("Informação pendente de revisão")
    return display


def _friendly_factor(factor: dict[str, object], stage: str) -> tuple[str, str, int]:
    """Apresenta os fatores calculados pelo backend em linguagem comercial."""

    name = str(factor.get("name", ""))
    contribution = int(factor.get("contribution", 0))
    if name == "base":
        return "Ponto de partida", "A oportunidade entra na fila com uma pontuação inicial.", contribution
    if name == "deal_stage":
        if stage == "Engaging":
            return "Estágio comercial", "O estágio atual é Engaging, indicando uma oportunidade em fase de maior acompanhamento.", contribution
        return "Estágio comercial", "O estágio atual é Prospecting, indicando uma oportunidade em fase inicial de acompanhamento.", contribution
    return name.replace("_", " ").title(), str(factor.get("reason", "Critério aplicado à oportunidade.")), contribution


def _inject_style() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #070B14; color: #F8FAFC; }
        .main .block-container { max-width: 1500px; padding-top: 2.2rem; padding-bottom: 3rem; }
        [data-testid="stSidebar"] { background: #0E1625; border-right: 1px solid #25334B; }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
        [data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: #E5EDF8; }
        [data-testid="stSidebar"] [data-baseweb="select"] > div,
        [data-testid="stSidebar"] input { background: #172235 !important; color: #F8FAFC !important; }
        [data-testid="stSidebar"] [data-baseweb="select"] svg { fill: #E5EDF8; }
        .hero { background: linear-gradient(120deg, #111C33 0%, #173E78 100%); border: 1px solid #315889;
                border-radius: 20px; padding: clamp(22px, 4vw, 42px); margin-bottom: 22px; }
        .hero h1 { color: #FFFFFF; margin: 0; font-size: clamp(2rem, 4vw, 3.3rem); line-height: 1.08; }
        .hero p { color: #D8E6FB; margin: 10px 0 0; font-size: clamp(1rem, 1.6vw, 1.2rem); }
        .eyebrow { color: #93C5FD; font-size: .8rem; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; }
        .kpi-card { background: #101827; border: 1px solid #25334B; border-top: 3px solid var(--accent);
                    border-radius: 16px; padding: 18px; min-height: 144px; margin-bottom: 12px; overflow: hidden; }
        .kpi-label { color: #A7B4C8; font-size: .88rem; min-height: 2.5em; overflow-wrap: anywhere; }
        .kpi-value { color: #F8FAFC; font-size: clamp(1.65rem, 2.6vw, 2.5rem); font-weight: 700;
                      line-height: 1.12; margin: 12px 0 8px; overflow-wrap: anywhere; }
        .kpi-detail { color: #8FA2BB; font-size: .78rem; overflow-wrap: anywhere; }
        h1, h2, h3, p, span, div { color: inherit; }
        [data-testid="stTabs"] button { color: #A7B4C8; font-weight: 600; }
        [data-testid="stTabs"] button[aria-selected="true"] { color: #FFFFFF; }
        [data-testid="stDataFrame"] { border: 1px solid #25334B; border-radius: 12px; overflow: hidden; }
        .stDownloadButton button, .stButton button { border-radius: 9px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _chart_layout(fig: go.Figure, *, height: int = 350) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        height=height,
        margin=dict(l=10, r=10, t=28, b=12),
        paper_bgcolor=COLORS["surface"],
        plot_bgcolor=COLORS["surface"],
        font=dict(color=COLORS["text"], family="Arial"),
        hoverlabel=dict(bgcolor=COLORS["surface_alt"], font_color=COLORS["text"]),
        showlegend=False,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, color=COLORS["muted"])
    fig.update_yaxes(gridcolor=COLORS["grid"], zeroline=False, color=COLORS["muted"])
    return fig


def _kpi_card(label: str, value: str, detail: str, accent: str) -> str:
    return (
        f'<div class="kpi-card" style="--accent:{accent}">'
        f'<div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>'
        f'<div class="kpi-detail">{detail}</div></div>'
    )


def _reset_filters() -> None:
    for key in ("agents", "managers", "regions", "products", "stages", "score_range", "search"):
        st.session_state.pop(key, None)


def _render_sidebar(queue: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.markdown("## Explorar carteira")
    st.sidebar.caption("Encontre rapidamente a seleção que deseja acompanhar.")
    if st.sidebar.button("Limpar filtros", use_container_width=True):
        _reset_filters()
        st.rerun()

    agents = st.sidebar.multiselect("Vendedor", sorted(queue["sales_agent"].dropna().unique()), key="agents")
    managers = st.sidebar.multiselect("Manager", sorted(queue["manager"].dropna().unique()), key="managers")
    regions = st.sidebar.multiselect("Região", sorted(queue["regional_office"].dropna().unique()), key="regions")
    stages = st.sidebar.multiselect("Estágio", ["Engaging", "Prospecting"], key="stages")
    products = st.sidebar.multiselect("Produto", sorted(queue["product"].dropna().unique()), key="products")
    score_range = st.sidebar.slider("Faixa de prioridade", 0, 100, (0, 100), key="score_range")
    search = st.sidebar.text_input("Buscar oportunidade, conta ou vendedor", placeholder="Ex.: 021Z2J9L", key="search")
    return filter_queue(
        queue,
        sales_agents=agents,
        managers=managers,
        regional_offices=regions,
        products=products,
        stages=stages,
        min_score=score_range[0],
        max_score=score_range[1],
        search_text=search,
    )


def _render_kpis(queue: pd.DataFrame, filtered: pd.DataFrame) -> None:
    visible, total = len(filtered), len(queue)
    high_priority = int(filtered["priority_score"].ge(70).sum()) if visible else 0
    missing_accounts = int(filtered["account"].isna().sum()) if visible else 0
    catalog_total = filtered["sales_price"].sum(min_count=1) if visible else None
    sellers = int(filtered["sales_agent"].nunique()) if visible else 0
    cards = st.columns(4, gap="medium")
    with cards[0]:
        st.markdown(_kpi_card("Oportunidades na seleção", f"{visible:,}", f"de {total:,} oportunidades abertas", COLORS["blue"]), unsafe_allow_html=True)
    with cards[1]:
        st.markdown(_kpi_card("Alta prioridade", f"{high_priority:,}", "oportunidades para olhar primeiro", COLORS["teal"]), unsafe_allow_html=True)
    with cards[2]:
        value = "—" if pd.isna(catalog_total) else f"US$ {catalog_total:,.0f}"
        st.markdown(_kpi_card("Valor de catálogo", value, "visão consolidada da seleção", COLORS["amber"]), unsafe_allow_html=True)
    with cards[3]:
        st.markdown(_kpi_card("Equipe na seleção", f"{sellers:,}", f"{missing_accounts:,} contas a revisar", COLORS["red"]), unsafe_allow_html=True)


def _render_overview(filtered: pd.DataFrame) -> None:
    st.markdown("### Visão da carteira")
    viz = filtered.assign(
        manager_label=filtered["manager"].map(_display_label),
        region_label=filtered["regional_office"].map(_display_label),
    )
    left, right = st.columns(2)
    with left:
        stages = viz["deal_stage"].value_counts().rename_axis("Estágio").reset_index(name="Oportunidades")
        fig = px.pie(stages, names="Estágio", values="Oportunidades", hole=.62, color="Estágio", color_discrete_map={"Engaging": COLORS["teal"], "Prospecting": COLORS["amber"]})
        fig.update_traces(textinfo="label+percent", textfont_color=COLORS["text"], hovertemplate="%{label}<br>%{value:,} oportunidades<extra></extra>")
        st.plotly_chart(_chart_layout(fig), use_container_width=True, config={"displayModeBar": False})
    with right:
        by_region = viz["region_label"].value_counts().rename_axis("Região").reset_index(name="Oportunidades")
        fig = px.bar(by_region, x="Oportunidades", y="Região", orientation="h", color_discrete_sequence=[COLORS["blue"]])
        fig.update_traces(hovertemplate="%{y}<br>%{x:,} oportunidades<extra></extra>")
        fig.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(_chart_layout(fig), use_container_width=True, config={"displayModeBar": False})

    left, right = st.columns(2)
    with left:
        managers = viz["manager_label"].value_counts().head(10).rename_axis("Manager").reset_index(name="Oportunidades")
        fig = px.bar(managers, x="Oportunidades", y="Manager", orientation="h", color_discrete_sequence=[COLORS["teal"]])
        fig.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(_chart_layout(fig), use_container_width=True, config={"displayModeBar": False})
    with right:
        products = viz["product"].value_counts().head(7).rename_axis("Produto").reset_index(name="Oportunidades")
        fig = px.bar(products, x="Produto", y="Oportunidades", color_discrete_sequence=[COLORS["amber"]])
        st.plotly_chart(_chart_layout(fig), use_container_width=True, config={"displayModeBar": False})


def _friendly_table(frame: pd.DataFrame) -> pd.DataFrame:
    table = frame.copy()
    table["Status de prioridade"] = table["priority_score"].map(_priority_label)
    table["account"] = table["account"].map(_display_account)
    table["sales_price"] = table["sales_price"].map(_display_price)
    return table.rename(
        columns={
            "rank": "Posição",
            "opportunity_id": "Oportunidade",
            "account": "Conta",
            "sales_agent": "Vendedor",
            "deal_stage": "Estágio",
            "product": "Produto",
            "priority_score": "Prioridade",
            "sales_price": "Preço de catálogo",
        }
    )


def _export_selection(filtered: pd.DataFrame) -> bytes:
    export_columns = ["rank", "opportunity_id", "priority_score", "deal_stage", "account", "sales_agent", "manager", "regional_office", "product", "sales_price", "warnings"]
    export = filtered[export_columns].copy().rename(columns={"priority_score": "prioridade", "sales_price": "preco_catalogo", "rank": "posicao"})
    export["warnings"] = export["warnings"].map(_display_warnings).map(json.dumps)
    return export.to_csv(index=False).encode("utf-8-sig")


def _render_queue(filtered: pd.DataFrame) -> None:
    st.markdown("### Fila de oportunidades")
    controls, export = st.columns([2, 1])
    with controls:
        show_all = st.checkbox("Mostrar todas as oportunidades", value=False)
    with export:
        st.download_button("Baixar seleção em CSV", _export_selection(filtered), "leadscore-selecao.csv", "text/csv", use_container_width=True)
    visible = filtered if show_all else filtered.head(100)
    if not show_all and len(filtered) > 100:
        st.caption("Exibindo as 100 primeiras oportunidades da seleção.")
    table = _friendly_table(visible)
    st.dataframe(
        table[["Posição", "Oportunidade", "Status de prioridade", "Conta", "Vendedor", "Estágio", "Produto", "Prioridade", "Preço de catálogo"]],
        hide_index=True,
        use_container_width=True,
        height=540,
        column_config={"Prioridade": st.column_config.ProgressColumn("Prioridade", min_value=0, max_value=100, format="%d")},
    )


def _render_detail(filtered: pd.DataFrame) -> None:
    st.markdown("### Detalhe da oportunidade")
    selected_id = st.selectbox("Selecione uma oportunidade", filtered["opportunity_id"].astype(str).tolist())
    detail = filtered.loc[filtered["opportunity_id"].astype(str).eq(selected_id)].iloc[0]
    left, right = st.columns([1, 1.5])
    with left:
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=int(detail["priority_score"]),
            number={"suffix": " / 100", "font": {"color": COLORS["text"]}},
            title={"text": _priority_label(detail["priority_score"]), "font": {"color": COLORS["text"]}},
            gauge={"axis": {"range": [0, 100], "tickcolor": COLORS["muted"]}, "bar": {"color": COLORS["teal"] if detail["priority_score"] >= 70 else COLORS["amber"]}, "bgcolor": COLORS["surface_alt"], "steps": [{"range": [0, 40], "color": COLORS["surface"]}, {"range": [40, 70], "color": "#3B321C"}]},
        ))
        st.plotly_chart(_chart_layout(gauge, height=300), use_container_width=True, config={"displayModeBar": False})
    with right:
        st.markdown(f"## {selected_id}")
        st.caption(f"Posição {int(detail['rank'])} · {detail['deal_stage']} · {_display_price(detail['sales_price'])}")
        a, b = st.columns(2)
        a.write(f"**Conta**  \n{_display_account(detail['account'])}")
        b.write(f"**Produto**  \n{_display_label(detail['product'])}")
        a.write(f"**Vendedor**  \n{_display_label(detail['sales_agent'])}")
        b.write(f"**Manager / Região**  \n{_display_label(detail['manager'])} · {_display_label(detail['regional_office'])}")
        st.markdown("#### Por que esta oportunidade tem esta prioridade?")
        st.caption("Os motivos abaixo são os fatores calculados para esta oportunidade.")
        for factor in detail["score_factors"]:
            label, reason, contribution = _friendly_factor(factor, str(detail["deal_stage"]))
            st.markdown(f"- **{label} · +{contribution}** — {reason}")
        display_warnings = _display_warnings(detail["warnings"])
        if display_warnings:
            st.warning("Informações a revisar: " + "; ".join(display_warnings))
        else:
            st.success("Informações completas para esta oportunidade.")


def _render_data_quality(filtered: pd.DataFrame) -> None:
    st.markdown("### Cobertura dos dados")
    fields = pd.DataFrame(
        {
            "Campo": ["Conta", "Data de engajamento", "Preço de catálogo", "Manager", "Região"],
            "Preenchidos": [
                filtered["account"].notna().sum(), filtered["engage_date"].notna().sum(), filtered["sales_price"].notna().sum(), filtered["manager"].notna().sum(), filtered["regional_office"].notna().sum(),
            ],
        }
    )
    fields["Cobertura"] = fields["Preenchidos"] / len(filtered)
    fig = px.bar(fields, x="Campo", y="Cobertura", text=fields["Cobertura"].map("{:.0%}".format), range_y=[0, 1], color_discrete_sequence=[COLORS["blue"]])
    fig.update_traces(textposition="outside", textfont_color=COLORS["text"], hovertemplate="%{x}<br>Cobertura: %{y:.0%}<extra></extra>")
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(_chart_layout(fig, height=350), use_container_width=True, config={"displayModeBar": False})
    st.caption("Campos não preenchidos permanecem visíveis para facilitar a revisão da carteira.")


def main() -> None:
    _inject_style()
    st.markdown(
        """<div class="hero"><div class="eyebrow">Painel comercial</div><h1>🎯 Lead Scorer</h1><p>Explore oportunidades, acompanhe a carteira e encontre o que precisa de atenção.</p></div>""",
        unsafe_allow_html=True,
    )
    try:
        queue = build_queue()
        filtered = _render_sidebar(queue)
    except Exception as error:  # pragma: no cover - estado exibido pelo Streamlit
        st.error(f"Não foi possível carregar as oportunidades: {error}")
        st.stop()

    _render_kpis(queue, filtered)
    if filtered.empty:
        st.warning("Nenhuma oportunidade corresponde aos filtros selecionados. Ajuste ou limpe os filtros na lateral.")
        return

    overview, queue_tab, detail, quality = st.tabs(["Visão executiva", "Oportunidades", "Detalhe", "Cobertura dos dados"])
    with overview:
        _render_overview(filtered)
    with queue_tab:
        _render_queue(filtered)
    with detail:
        _render_detail(filtered)
    with quality:
        _render_data_quality(filtered)


if __name__ == "__main__":
    main()
