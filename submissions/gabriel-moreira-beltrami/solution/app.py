"""Fila de priorização de oportunidades de CRM, transparente e sem vazamento."""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_DIRECTORY = PROJECT_ROOT / "data" / "raw"
PRODUCT_ALIASES = {"GTXPro": "GTX Pro"}
STAGE_LABELS = {"Prospecting": "Prospecção", "Engaging": "Em negociação"}
HISTORY_PRIOR_STRENGTH = 20


def format_currency(value: float | int | None) -> str:
    return "—" if pd.isna(value) else f"${value:,.0f}"


@st.cache_data(show_spinner=False)
def load_data(source_directory: str) -> dict[str, pd.DataFrame]:
    """Carrega os CSVs e normaliza a inconsistência conhecida de produto."""
    source = Path(source_directory)
    filenames = {
        "accounts": "accounts.csv",
        "products": "products.csv",
        "sales_teams": "sales_teams.csv",
        "sales_pipeline": "sales_pipeline.csv",
    }
    missing = [file for file in filenames.values() if not (source / file).is_file()]
    if missing:
        raise FileNotFoundError(f"Arquivo(s) de dados ausente(s) em {source}: {', '.join(missing)}")
    tables = {name: pd.read_csv(source / filename) for name, filename in filenames.items()}
    pipeline = tables["sales_pipeline"].copy()
    for column in ["engage_date", "close_date"]:
        pipeline[column] = pd.to_datetime(pipeline[column], errors="coerce")
    pipeline["close_value"] = pd.to_numeric(pipeline["close_value"], errors="coerce")
    pipeline["product_clean"] = pipeline["product"].replace(PRODUCT_ALIASES)
    tables["sales_pipeline"] = pipeline
    return tables


@st.cache_data(show_spinner=False)
def score_open_opportunities(
    pipeline: pd.DataFrame, accounts: pd.DataFrame, products: pd.DataFrame, teams: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Pontua apenas oportunidades abertas usando informação disponível antes do resultado."""
    closed = pipeline.loc[pipeline["deal_stage"].isin(["Won", "Lost"])].copy()
    closed["won"] = closed["deal_stage"].eq("Won").astype(int)
    global_rate = closed["won"].mean()
    history = closed.groupby("product_clean", as_index=False).agg(
        closed_outcomes=("opportunity_id", "count"), won_outcomes=("won", "sum")
    )
    history["smoothed_win_rate"] = (
        history["won_outcomes"] + global_rate * HISTORY_PRIOR_STRENGTH
    ) / (history["closed_outcomes"] + HISTORY_PRIOR_STRENGTH)
    catalog = products.rename(columns={"product": "product_clean"})[["product_clean", "series", "sales_price"]]
    product_history = catalog.merge(history, on="product_clean", how="left", validate="one_to_one")

    open_deals = pipeline.loc[pipeline["deal_stage"].isin(STAGE_LABELS)].copy()
    open_deals = open_deals.merge(product_history, on="product_clean", how="left", validate="many_to_one")
    open_deals = open_deals.merge(accounts, on="account", how="left", validate="many_to_one")
    open_deals = open_deals.merge(teams, on="sales_agent", how="left", validate="many_to_one")
    open_deals["expected_catalog_value"] = open_deals["sales_price"] * open_deals["smoothed_win_rate"]
    reference = max(float(open_deals["expected_catalog_value"].quantile(0.90)), 1.0)
    open_deals["value_points"] = (75 * open_deals["expected_catalog_value"] / reference).clip(upper=75)
    open_deals["history_points"] = (15 * open_deals["closed_outcomes"] / 75).clip(upper=15)
    open_deals["context_points"] = np.where(open_deals["account"].notna(), 10, 0)
    open_deals["action_score"] = (
        open_deals["value_points"] + open_deals["history_points"] + open_deals["context_points"]
    ).round().astype(int)

    prospecting = open_deals["deal_stage"].eq("Prospecting")
    open_deals["recommendation"] = "Nutrir"
    open_deals.loc[prospecting & open_deals["action_score"].ge(50), "recommendation"] = "Pesquisar antes"
    open_deals.loc[prospecting & open_deals["action_score"].ge(70) & open_deals["account"].notna(), "recommendation"] = "Engajar agora"
    open_deals.loc[~prospecting, "recommendation"] = pd.cut(
        open_deals.loc[~prospecting, "action_score"], [-1, 49, 69, 100], labels=["Monitorar", "Manter ativa", "Focar agora"]
    ).astype(str)
    open_deals["reason"] = open_deals.apply(priority_reason, axis=1)
    return open_deals.sort_values(["action_score", "expected_catalog_value"], ascending=False), product_history


def priority_reason(lead: pd.Series) -> str:
    product = (
        f"{lead['product_clean']} tem preço de catálogo de ${lead['sales_price']:,.0f} e "
        f"taxa histórica de vitória suavizada de {lead['smoothed_win_rate']:.1%}."
    )
    stage = (
        "A oportunidade já está em negociação: proteja o avanço com um próximo passo claro."
        if lead["deal_stage"] == "Engaging"
        else "A oportunidade está em prospecção: qualifique o cliente antes de investir muito esforço."
    )
    account = "O contexto da conta está disponível." if pd.notna(lead["account"]) else "A conta ainda não foi identificada; pesquisa e qualificação vêm primeiro."
    return " ".join([product, stage, account])


def filters(scored: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    with st.sidebar:
        st.header("Meu foco")
        agent = st.selectbox("Vendedor", ["Todos os vendedores", *sorted(scored["sales_agent"].dropna().unique())])
        manager = st.selectbox("Gestor", ["Todos os gestores", *sorted(scored["manager"].dropna().unique())])
        region = st.selectbox("Escritório regional", ["Todas as regiões", *sorted(scored["regional_office"].dropna().unique())])
        st.markdown("**Estágio do negócio**")
        include_engaging = st.checkbox("Em negociação", value=True, key="filtro-estagio-em-negociacao")
        include_prospecting = st.checkbox("Prospecção", value=True, key="filtro-estagio-prospeccao")
        minimum = st.slider("Pontuação mínima de ação", 0, 100, 0, 5)
    stages = (["Engaging"] if include_engaging else []) + (["Prospecting"] if include_prospecting else [])
    visible = scored.loc[scored["deal_stage"].isin(stages) & scored["action_score"].ge(minimum)].copy()
    if agent != "Todos os vendedores":
        visible = visible.loc[visible["sales_agent"].eq(agent)]
    if manager != "Todos os gestores":
        visible = visible.loc[visible["manager"].eq(manager)]
    if region != "Todas as regiões":
        visible = visible.loc[visible["regional_office"].eq(region)]
    return visible, stages


def table_for(frame: pd.DataFrame) -> pd.DataFrame:
    columns = ["action_score", "recommendation", "opportunity_id", "deal_stage", "product_clean", "account", "sales_agent", "manager", "regional_office", "smoothed_win_rate", "expected_catalog_value", "reason"]
    table = frame[columns].copy()
    table["deal_stage"] = table["deal_stage"].map(STAGE_LABELS)
    table["smoothed_win_rate"] *= 100
    return table.rename(columns={
        "action_score": "Pontuação de ação", "recommendation": "Recomendação", "opportunity_id": "Oportunidade",
        "deal_stage": "Estágio", "product_clean": "Produto", "account": "Conta", "sales_agent": "Responsável",
        "manager": "Gestor", "regional_office": "Região", "smoothed_win_rate": "Probabilidade histórica de vitória (%)",
        "expected_catalog_value": "Valor esperado de catálogo", "reason": "Por que está na fila",
    })


def render_lead_detail(lead: pd.Series, heading: str) -> None:
    st.markdown(f"#### {heading}")
    score, probability, expected = st.columns(3)
    score.metric("Pontuação de ação", f"{lead['action_score']}/100", lead["recommendation"])
    probability.metric("Probabilidade histórica de vitória", f"{lead['smoothed_win_rate']:.1%}")
    expected.metric("Valor esperado de catálogo", format_currency(lead["expected_catalog_value"]))
    st.markdown("##### Por que esta oportunidade é prioridade")
    st.write(lead["reason"])
    components = pd.DataFrame([
        {"Componente": "Valor esperado de catálogo", "Pontos": round(lead["value_points"], 1)},
        {"Componente": "Cobertura histórica do produto", "Pontos": round(lead["history_points"], 1)},
        {"Componente": "Contexto da conta do cliente", "Pontos": round(lead["context_points"], 1)},
    ])
    st.dataframe(components, hide_index=True, use_container_width=True)
    fields = {
        "Oportunidade": lead["opportunity_id"], "Recomendação": lead["recommendation"], "Produto": lead["product_clean"],
        "Série do produto": lead["series"], "Preço de catálogo": format_currency(lead["sales_price"]),
        "Estágio": STAGE_LABELS[lead["deal_stage"]],
        "Data de entrada em negociação": "Ainda não chegou a esta etapa" if pd.isna(lead["engage_date"]) else lead["engage_date"].date().isoformat(),
        "Conta": lead["account"] if pd.notna(lead["account"]) else "Ainda não coletada na prospecção",
        "Receita da conta": format_currency(lead["revenue"] * 1_000_000) if pd.notna(lead["revenue"]) else "Ainda não disponível",
        "Funcionários": "—" if pd.isna(lead["employees"]) else f"{lead['employees']:,.0f}",
        "Responsável": lead["sales_agent"], "Gestor": lead["manager"], "Região": lead["regional_office"],
    }
    st.dataframe(pd.DataFrame(fields.items(), columns=["Campo", "Valor"]), hide_index=True, use_container_width=True)
    if lead["deal_stage"] == "Prospecting":
        st.warning("Próxima ação: identificar a conta, o contato e a necessidade antes de investir mais esforço comercial.")


def render_queue(frame: pd.DataFrame, heading: str, description: str, filename: str) -> None:
    st.subheader(heading)
    st.caption(description)
    st.caption("Use o círculo no início da linha para trocar o detalhe exibido abaixo da tabela.")
    table = table_for(frame)
    event = st.dataframe(
        table, hide_index=True, use_container_width=True, key=f"{filename}-table", on_select="rerun", selection_mode="single-row-required",
        column_config={
            "Pontuação de ação": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d"),
            "Probabilidade histórica de vitória (%)": st.column_config.NumberColumn(format="%.1f"),
            "Valor esperado de catálogo": st.column_config.NumberColumn(format="$%d"),
        },
    )
    selected = list(event.selection.rows)
    if selected and 0 <= selected[0] < len(frame):
        st.divider()
        render_lead_detail(frame.iloc[selected[0]], "Lead selecionado")
    elif frame.empty:
        st.info("Nenhum lead corresponde aos filtros selecionados.")
    st.download_button("Baixar esta fila em CSV", table.to_csv(index=False).encode("utf-8"), filename, "text/csv")


def main() -> None:
    st.set_page_config(page_title="Fila de Prioridades — Classificador de Leads", page_icon="🎯", layout="wide")
    st.title("Fila de Prioridades")
    st.caption("Classificador de Leads • Desafio 003 • Gabriel Moreira Beltrami")
    source = Path(os.environ.get("LEAD_SCORER_DATA_DIR", DEFAULT_DATA_DIRECTORY))
    try:
        tables = load_data(str(source))
    except FileNotFoundError as error:
        st.error(str(error))
        st.stop()
    scored, product_history = score_open_opportunities(tables["sales_pipeline"], tables["accounts"], tables["products"], tables["sales_teams"])
    visible, stages = filters(scored)
    first, second, third, fourth = st.columns(4)
    first.metric("Oportunidades abertas", f"{len(visible):,}")
    second.metric("Leads para engajar", f"{visible['recommendation'].eq('Engajar agora').sum():,}")
    third.metric("Leads em negociação para focar", f"{visible['recommendation'].eq('Focar agora').sum():,}")
    fourth.metric("Valor esperado de catálogo", format_currency(visible["expected_catalog_value"].sum()))
    st.caption("**Pontuação de ação (0–100):** resume a prioridade comercial por valor potencial, confiança no histórico do produto e contexto da conta. Quanto maior, mais cedo agir; não é uma previsão de receita.")

    queues = []
    if "Prospecting" in stages:
        queues.append(("Priorizar prospecção", "Prospecting"))
    if "Engaging" in stages:
        queues.append(("Aumentar atenção", "Engaging"))
    if queues:
        selected_label = st.radio("Fila de trabalho", [label for label, _ in queues], horizontal=True, label_visibility="collapsed")
        stage = next(stage for label, stage in queues if label == selected_label)
        if stage == "Prospecting":
            render_queue(visible.loc[visible["deal_stage"].eq(stage)], "Quem devo abordar?", "Produtos de maior valor com histórico suficiente aparecem primeiro; se falta uma conta, pesquise antes de abordar.", "fila-prospeccao.csv")
        else:
            render_queue(visible.loc[visible["deal_stage"].eq(stage)], "Onde devo aumentar a atenção?", "O CRM não tem histórico de atividades ou do tempo em cada estágio; esta é uma fila por valor esperado, não um alerta de inatividade.", "fila-atencao.csv")
    else:
        st.warning("Selecione ao menos um estágio para exibir uma fila de trabalho.")

    detail_tab, policy_tab, data_tab = st.tabs(["Detalhe do lead", "Política de pontuação", "Qualidade dos dados"])
    with detail_tab:
        st.subheader("Detalhe do lead")
        if visible.empty:
            st.info("Ajuste os filtros para inspecionar um lead.")
        else:
            selected_id = st.selectbox("Escolha uma oportunidade", visible["opportunity_id"].tolist())
            render_lead_detail(visible.loc[visible["opportunity_id"].eq(selected_id)].iloc[0], "Detalhe do lead")
    with policy_tab:
        st.subheader("Política de pontuação")
        st.markdown("**Valor esperado de catálogo** = preço de catálogo × taxa histórica de vitória suavizada. A fila não usa `close_date`, `close_value`, resultado final, porte da empresa, identidade da pessoa vendedora ou cronômetro de inatividade.")
        policy = product_history.copy()
        policy["valor_esperado"] = policy["sales_price"] * policy["smoothed_win_rate"]
        st.dataframe(policy.sort_values("valor_esperado", ascending=False), hide_index=True, use_container_width=True)
    with data_tab:
        st.subheader("Qualidade dos dados")
        st.write("`GTXPro` é normalizado para `GTX Pro`. Não há data de criação do lead, histórico de estágios, último contato ou snapshot; portanto, não há pontuação de inatividade.")


if __name__ == "__main__":
    main()
