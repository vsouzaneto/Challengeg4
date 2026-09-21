# Baseline 2 — brief-streamlit — saída bruta (sem edição)

# Lead Scorer — Challenge 003 (Python + Streamlit)

Abaixo está uma solução completa e funcional para o challenge: um app Streamlit que carrega os quatro CSVs do dataset *CRM Sales Predictive Analytics*, calcula um score de 0 a 100 para cada oportunidade **aberta** (Prospecting / Engaging), explica o porquê de cada score e permite filtrar por vendedor, manager, região, produto e setor.

Estrutura de arquivos:

```
lead-scorer/
├── app.py              # interface Streamlit
├── scoring.py          # carga de dados, features e lógica de scoring
├── requirements.txt
├── README.md
└── data/
    ├── accounts.csv
    ├── products.csv
    ├── sales_teams.csv
    └── sales_pipeline.csv
```

---

## 1. A fórmula do score

O score é uma **soma ponderada de 7 componentes**, cada um normalizado para a escala 0–100, aplicada apenas a deals abertos (Won/Lost servem como histórico para calibrar os componentes).

```
Score = 0.20 · Estágio
      + 0.20 · Frescor (tempo no pipeline)
      + 0.15 · Valor do produto
      + 0.15 · Histórico da conta
      + 0.15 · Performance vendedor × produto
      + 0.10 · Porte da conta
      + 0.05 · Taxa de conversão do setor
```

| Componente | Peso | Como é calculado (0–100) | Por que importa |
|---|---|---|---|
| **Estágio** | 20% | Engaging = 100, Prospecting = 40 | Deal em Engaging já teve contato ativo; a probabilidade de fechar é muito maior que em Prospecting. |
| **Frescor** | 20% | Dias desde `engage_date` comparados com a mediana do ciclo dos deals ganhos. Até a mediana = 100; cai linearmente até 0 em 2× a mediana. Sem `engage_date` = 50 (neutro). | Deals que ultrapassam muito o ciclo típico tendem a morrer ("esfriar"). Deal recente merece atenção antes que isso aconteça. |
| **Valor do produto** | 15% | Percentil do `sales_price` do produto dentro do catálogo. | Priorizar ticket maior, mas ponderado (não é o único critério, como o brief pede). |
| **Histórico da conta** | 15% | Taxa de vitória histórica da conta (Won / (Won+Lost)), com suavização bayesiana em direção à média global (prior de 5 deals). | Contas que já compraram várias vezes tendem a comprar de novo. |
| **Vendedor × produto** | 15% | Taxa de vitória do vendedor naquele produto específico, também suavizada. | Alguns vendedores convertem muito melhor certos produtos — é sinal real de fit. |
| **Porte da conta** | 10% | `revenue` da conta em escala log, normalizada min-max. Sem conta = 50. | Empresas maiores têm mais orçamento e expansão futura. |
| **Setor** | 5% | Taxa de vitória histórica do setor, suavizada. | Alguns setores fecham mais; peso pequeno para não enviesar demais. |

**Faixas de prioridade**

- **Quente** — score ≥ 70 → agir esta semana
- **Morno** — 45 ≤ score < 70 → manter cadência
- **Frio** — score < 45 → baixa prioridade / considerar desqualificar

A explicação exibida ao vendedor lista os componentes que mais contribuíram (positiva e negativamente), em linguagem natural, por exemplo:

> **Score 82 — Quente.** Deal em Engaging (+20). Conta Acme Corp já ganhou 78% dos deals anteriores (+12). Produto GTX Pro é o 2º mais caro do catálogo (+12). Ponto de atenção: deal há 61 dias no pipeline, acima da mediana de 48 dias (−7).

---

## 2. `scoring.py`

```python
"""
scoring.py — Carga de dados, engenharia de features e lógica de scoring
para o Lead Scorer (Challenge 003).

Uso isolado:
    from scoring import load_data, score_pipeline
    data = load_data("data")
    scored = score_pipeline(data)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------- #
# Configuração
# --------------------------------------------------------------------------- #

WEIGHTS: dict[str, float] = {
    "stage": 0.20,
    "freshness": 0.20,
    "product_value": 0.15,
    "account_history": 0.15,
    "agent_product_fit": 0.15,
    "account_size": 0.10,
    "sector_rate": 0.05,
}

COMPONENT_LABELS: dict[str, str] = {
    "stage": "Estágio do deal",
    "freshness": "Tempo no pipeline",
    "product_value": "Valor do produto",
    "account_history": "Histórico da conta",
    "agent_product_fit": "Vendedor × produto",
    "account_size": "Porte da conta",
    "sector_rate": "Conversão do setor",
}

OPEN_STAGES = ("Prospecting", "Engaging")
STAGE_SCORE = {"Engaging": 100.0, "Prospecting": 40.0}

HOT_THRESHOLD = 70
WARM_THRESHOLD = 45

# Prior bayesiano: quantos "deals fictícios" na média global usamos
# para suavizar taxas de vitória de grupos pequenos.
PRIOR_STRENGTH = 5


@dataclass
class CRMData:
    pipeline: pd.DataFrame
    accounts: pd.DataFrame
    products: pd.DataFrame
    teams: pd.DataFrame
    reference_date: pd.Timestamp = field(default=None)


# --------------------------------------------------------------------------- #
# Carga
# --------------------------------------------------------------------------- #

def load_data(data_dir: str | Path = "data") -> CRMData:
    """Lê os quatro CSVs do dataset e devolve um CRMData com tipos corrigidos."""
    data_dir = Path(data_dir)

    pipeline = pd.read_csv(data_dir / "sales_pipeline.csv")
    accounts = pd.read_csv(data_dir / "accounts.csv")
    products = pd.read_csv(data_dir / "products.csv")
    teams = pd.read_csv(data_dir / "sales_teams.csv")

    for col in ("engage_date", "close_date"):
        pipeline[col] = pd.to_datetime(pipeline[col], errors="coerce")
    pipeline["close_value"] = pd.to_numeric(pipeline["close_value"], errors="coerce")

    # Normaliza strings para evitar joins quebrados por espaço/caixa.
    for df, cols in (
        (pipeline, ["sales_agent", "product", "account", "deal_stage"]),
        (accounts, ["account", "sector"]),
        (products, ["product", "series"]),
        (teams, ["sales_agent", "manager", "regional_office"]),
    ):
        for c in cols:
            if c in df.columns:
                df[c] = df[c].astype("string").str.strip()

    # Corrige inconsistência conhecida do dataset ("GTXPro" vs "GTX Pro").
    pipeline["product"] = pipeline["product"].replace({"GTXPro": "GTX Pro"})

    # O dataset é histórico (2017). Usamos a última data conhecida como "hoje"
    # para que "dias no pipeline" faça sentido.
    reference_date = max(
        pipeline["close_date"].max(), pipeline["engage_date"].max()
    )

    return CRMData(pipeline, accounts, products, teams, reference_date)


# --------------------------------------------------------------------------- #
# Helpers estatísticos
# --------------------------------------------------------------------------- #

def _smoothed_win_rate(
    closed: pd.DataFrame, key: str | list[str], global_rate: float
) -> pd.DataFrame:
    """Taxa de vitória por grupo com suavização bayesiana.

    rate = (wins + k * global_rate) / (n + k), k = PRIOR_STRENGTH.
    Grupos com poucos deals ficam próximos da média global.
    """
    keys = [key] if isinstance(key, str) else key
    g = closed.groupby(keys, dropna=False)["is_won"].agg(["sum", "count"]).reset_index()
    g["rate"] = (g["sum"] + PRIOR_STRENGTH * global_rate) / (g["count"] + PRIOR_STRENGTH)
    g = g.rename(columns={"sum": "wins", "count": "n"})
    return g


def _minmax(series: pd.Series, fill: float = 50.0) -> pd.Series:
    s = series.astype(float)
    lo, hi = s.min(), s.max()
    if pd.isna(lo) or pd.isna(hi) or hi == lo:
        return pd.Series(fill, index=s.index)
    out = (s - lo) / (hi - lo) * 100
    return out.fillna(fill)


# --------------------------------------------------------------------------- #
# Scoring
# --------------------------------------------------------------------------- #

def score_pipeline(data: CRMData, weights: dict[str, float] | None = None) -> pd.DataFrame:
    """Devolve um DataFrame com um registro por deal aberto, contendo:
    - colunas de contexto (vendedor, manager, região, produto, conta, setor...)
    - score_<componente> (0-100) para cada componente
    - contrib_<componente> (pontos efetivos = score * peso)
    - score (0-100), priority (Quente/Morno/Frio) e explanation (texto)
    """
    weights = weights or WEIGHTS
    if abs(sum(weights.values()) - 1.0) > 1e-6:
        raise ValueError("Os pesos precisam somar 1.0")

    p = data.pipeline.copy()
    p["is_won"] = (p["deal_stage"] == "Won").astype(int)
    closed = p[p["deal_stage"].isin(["Won", "Lost"])].copy()
    global_rate = closed["is_won"].mean() if len(closed) else 0.5

    # Enriquecimento ---------------------------------------------------------
    df = p[p["deal_stage"].isin(OPEN_STAGES)].merge(
        data.accounts, on="account", how="left"
    ).merge(
        data.products, on="product", how="left"
    ).merge(
        data.teams, on="sales_agent", how="left"
    )

    # 1) Estágio -------------------------------------------------------------
    df["score_stage"] = df["deal_stage"].map(STAGE_SCORE).fillna(40.0)

    # 2) Frescor -------------------------------------------------------------
    won = closed[closed["is_won"] == 1]
    cycle_days = (won["close_date"] - won["engage_date"]).dt.days.dropna()
    median_cycle = float(cycle_days.median()) if len(cycle_days) else 45.0

    df["days_in_pipeline"] = (data.reference_date - df["engage_date"]).dt.days
    ratio = df["days_in_pipeline"] / median_cycle
    # <= 1x mediana: 100; 2x mediana: 0; entre: linear.
    fresh = (100 * (2 - ratio)).clip(lower=0, upper=100)
    df["score_freshness"] = fresh.where(df["days_in_pipeline"].notna(), 50.0)

    # 3) Valor do produto ----------------------------------------------------
    price_rank = data.products.set_index("product")["sales_price"].rank(pct=True) * 100
    df["score_product_value"] = df["product"].map(price_rank).fillna(50.0)

    # 4) Histórico da conta --------------------------------------------------
    acc_rate = _smoothed_win_rate(closed.dropna(subset=["account"]), "account", global_rate)
    df = df.merge(
        acc_rate.rename(columns={"rate": "account_win_rate", "n": "account_n_deals",
                                 "wins": "account_wins"}),
        on="account", how="left",
    )
    df["account_win_rate"] = df["account_win_rate"].fillna(global_rate)
    df["account_n_deals"] = df["account_n_deals"].fillna(0).astype(int)
    df["account_wins"] = df["account_wins"].fillna(0).astype(int)
    df["score_account_history"] = df["account_win_rate"] * 100

    # 5) Vendedor × produto --------------------------------------------------
    ap_rate = _smoothed_win_rate(closed, ["sales_agent", "product"], global_rate)
    df = df.merge(
        ap_rate.rename(columns={"rate": "agent_product_win_rate",
                                "n": "agent_product_n", "wins": "agent_product_wins"}),
        on=["sales_agent", "product"], how="left",
    )
    df["agent_product_win_rate"] = df["agent_product_win_rate"].fillna(global_rate)
    df["agent_product_n"] = df["agent_product_n"].fillna(0).astype(int)
    df["score_agent_product_fit"] = df["agent_product_win_rate"] * 100

    # 6) Porte da conta ------------------------------------------------------
    df["score_account_size"] = _minmax(np.log1p(df["revenue"].astype(float)), fill=50.0)

    # 7) Setor ---------------------------------------------------------------
    closed_sector = closed.merge(data.accounts[["account", "sector"]], on="account", how="left")
    sec_rate = _smoothed_win_rate(closed_sector.dropna(subset=["sector"]), "sector", global_rate)
    df = df.merge(
        sec_rate[["sector", "rate"]].rename(columns={"rate": "sector_win_rate"}),
        on="sector", how="left",
    )
    df["sector_win_rate"] = df["sector_win_rate"].fillna(global_rate)
    df["score_sector_rate"] = df["sector_win_rate"] * 100

    # Score final ------------------------------------------------------------
    for comp, w in weights.items():
        df[f"contrib_{comp}"] = df[f"score_{comp}"] * w
    df["score"] = sum(df[f"contrib_{c}"] for c in weights).round(0).astype(int)
    df["priority"] = pd.cut(
        df["score"],
        bins=[-1, WARM_THRESHOLD - 1, HOT_THRESHOLD - 1, 101],
        labels=["Frio", "Morno", "Quente"],
    ).astype(str)

    # Valor esperado: preço do produto × prob. estimada (média das taxas)
    est_prob = (df["account_win_rate"] + df["agent_product_win_rate"]) / 2
    df["expected_value"] = (df["sales_price"].fillna(0) * est_prob).round(0)

    # Explicação -------------------------------------------------------------
    ctx = {"median_cycle": median_cycle, "global_rate": global_rate, "weights": weights}
    df["explanation"] = df.apply(lambda r: build_explanation(r, ctx), axis=1)

    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    df.attrs["median_cycle"] = median_cycle
    df.attrs["global_rate"] = global_rate
    df.attrs["reference_date"] = data.reference_date
    return df


# --------------------------------------------------------------------------- #
# Explicabilidade
# --------------------------------------------------------------------------- #

def build_explanation(r: pd.Series, ctx: dict) -> str:
    """Gera um texto curto, em linguagem de vendedor, explicando o score."""
    w = ctx["weights"]
    median_cycle = ctx["median_cycle"]
    global_rate = ctx["global_rate"]
    parts: list[str] = []

    # Estágio
    pts = r["contrib_stage"]
    if r["deal_stage"] == "Engaging":
        parts.append(f"Deal já em Engaging (+{pts:.0f})")
    else:
        parts.append(f"Ainda em Prospecting (+{pts:.0f} de {100 * w['stage']:.0f} possíveis)")

    # Frescor
    if pd.notna(r["days_in_pipeline"]):
        d = int(r["days_in_pipeline"])
        if d <= median_cycle:
            parts.append(f"{d} dias no pipeline, dentro do ciclo típico de {median_cycle:.0f} dias (+{r['contrib_freshness']:.0f})")
        else:
            parts.append(f"Atenção: {d} dias no pipeline, acima do ciclo típico de {median_cycle:.0f} dias (+{r['contrib_freshness']:.0f} de {100 * w['freshness']:.0f})")
    else:
        parts.append("Sem data de engajamento registrada (neutro)")

    # Produto
    parts.append(f"Produto {r['product']} custa ${r['sales_price']:,.0f} — percentil {r['score_product_value']:.0f} do catálogo (+{r['contrib_product_value']:.0f})")

    # Conta
    if r["account_n_deals"] > 0:
        parts.append(f"Conta {r['account']} ganhou {r['account_wins']} de {r['account_n_deals']} deals anteriores, taxa ajustada {r['account_win_rate']:.0%} vs média {global_rate:.0%} (+{r['contrib_account_history']:.0f})")
    else:
        parts.append(f"Conta sem histórico fechado — usando média global {global_rate:.0%} (+{r['contrib_account_history']:.0f})")

    # Vendedor × produto
    if r["agent_product_n"] > 0:
        parts.append(f"{r['sales_agent']} converte {r['agent_product_win_rate']:.0%} em {r['product']} ({r['agent_product_n']} deals fechados) (+{r['contrib_agent_product_fit']:.0f})")
    else:
        parts.append(f"{r['sales_agent']} ainda não fechou {r['product']} — usando média global (+{r['contrib_agent_product_fit']:.0f})")

    # Porte
    if pd.notna(r.get("revenue")):
        parts.append(f"Receita da conta ${r['revenue']:,.0f}M (+{r['contrib_account_size']:.0f})")
    else:
        parts.append("Conta não cadastrada em accounts.csv (porte neutro)")

    # Setor
    if pd.notna(r.get("sector")):
        parts.append(f"Setor {r['sector']} converte {r['sector_win_rate']:.0%} (+{r['contrib_sector_rate']:.0f})")

    return " · ".join(parts)


def recommended_action(r: pd.Series) -> str:
    """Sugestão de próximo passo com base no score e nos componentes."""
    if r["priority"] == "Quente":
        if r["deal_stage"] == "Prospecting":
            return "Agendar reunião de descoberta esta semana — conta e produto são fortes."
        return "Enviar proposta / fechar. Priorizar hoje."
    if r["priority"] == "Morno":
        if r["score_freshness"] < 50:
            return "Deal esfriando: fazer contato de reativação nos próximos 2 dias."
        return "Manter cadência normal de follow-up."
    if r["score_freshness"] == 0:
        return "Muito tempo parado: qualificar ou desqualificar para limpar o pipeline."
    return "Baixa prioridade — trabalhar apenas quando os quentes estiverem cobertos."


def component_table(r: pd.Series, weights: dict[str, float] | None = None) -> pd.DataFrame:
    """Tabela componente → nota (0-100) → peso → pontos, para exibir no app."""
    weights = weights or WEIGHTS
    rows = []
    for comp, w in weights.items():
        rows.append({
            "Componente": COMPONENT_LABELS[comp],
            "Nota (0-100)": round(float(r[f"score_{comp}"]), 0),
            "Peso": f"{w:.0%}",
            "Pontos": round(float(r[f"contrib_{comp}"]), 1),
            "Máx. possível": round(100 * w, 1),
        })
    return pd.DataFrame(rows).sort_values("Pontos", ascending=False)
```

---

## 3. `app.py`

```python
"""
app.py — Interface Streamlit do Lead Scorer (Challenge 003).

Rodar:
    streamlit run app.py
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from scoring import (
    COMPONENT_LABELS,
    WEIGHTS,
    HOT_THRESHOLD,
    WARM_THRESHOLD,
    component_table,
    load_data,
    recommended_action,
    score_pipeline,
)

st.set_page_config(page_title="Lead Scorer", page_icon="🎯", layout="wide")

PRIORITY_COLORS = {"Quente": "#d62728", "Morno": "#ff9f1c", "Frio": "#4a90d9"}


@st.cache_data(show_spinner="Calculando scores…")
def get_scored(data_dir: str, weights: tuple) -> pd.DataFrame:
    data = load_data(data_dir)
    return score_pipeline(data, dict(weights))


# --------------------------------------------------------------------------- #
# Sidebar: filtros e pesos
# --------------------------------------------------------------------------- #

st.sidebar.title("🎯 Lead Scorer")
data_dir = st.sidebar.text_input("Pasta dos CSVs", value="data")

with st.sidebar.expander("Ajustar pesos (avançado)", expanded=False):
    st.caption("Os pesos são normalizados automaticamente para somar 100%.")
    raw = {}
    for comp, w in WEIGHTS.items():
        raw[comp] = st.slider(COMPONENT_LABELS[comp], 0, 40, int(w * 100), step=5)
    total = sum(raw.values()) or 1
    weights = {k: v / total for k, v in raw.items()}

try:
    scored = get_scored(data_dir, tuple(sorted(weights.items())))
except FileNotFoundError as e:
    st.error(f"Não encontrei os arquivos em `{data_dir}`. Coloque os 4 CSVs lá. ({e})")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.subheader("Filtros")


def multiselect(label: str, col: str) -> list:
    opts = sorted(scored[col].dropna().unique().tolist())
    return st.sidebar.multiselect(label, opts)


f_region = multiselect("Região", "regional_office")
f_manager = multiselect("Manager", "manager")
f_agent = multiselect("Vendedor", "sales_agent")
f_product = multiselect("Produto", "product")
f_sector = multiselect("Setor", "sector")
f_stage = st.sidebar.multiselect("Estágio", ["Engaging", "Prospecting"])
f_priority = st.sidebar.multiselect("Prioridade", ["Quente", "Morno", "Frio"])

view = scored.copy()
for col, sel in [
    ("regional_office", f_region), ("manager", f_manager), ("sales_agent", f_agent),
    ("product", f_product), ("sector", f_sector), ("deal_stage", f_stage),
    ("priority", f_priority),
]:
    if sel:
        view = view[view[col].isin(sel)]

# --------------------------------------------------------------------------- #
# Cabeçalho e KPIs
# --------------------------------------------------------------------------- #

st.title("Onde focar esta semana")
ref = scored.attrs["reference_date"]
st.caption(
    f"Data de referência dos dados: **{ref:%d/%m/%Y}** · "
    f"Ciclo mediano de fechamento: **{scored.attrs['median_cycle']:.0f} dias** · "
    f"Taxa de vitória global: **{scored.attrs['global_rate']:.0%}**"
)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Deals abertos", f"{len(view):,}")
c2.metric("🔥 Quentes", int((view["priority"] == "Quente").sum()))
c3.metric("🌤️ Mornos", int((view["priority"] == "Morno").sum()))
c4.metric("❄️ Frios", int((view["priority"] == "Frio").sum()))
c5.metric("Valor esperado (soma)", f"${view['expected_value'].sum():,.0f}")

tab_list, tab_detail, tab_overview, tab_method = st.tabs(
    ["📋 Lista priorizada", "🔍 Detalhe do deal", "📊 Visão geral", "ℹ️ Como o score funciona"]
)

# --------------------------------------------------------------------------- #
# Aba 1: lista
# --------------------------------------------------------------------------- #

with tab_list:
    top_n = st.slider("Mostrar top N", 10, 500, 50, step=10)
    cols = [
        "score", "priority", "opportunity_id", "sales_agent", "account", "product",
        "deal_stage", "days_in_pipeline", "sales_price", "expected_value",
        "regional_office", "manager", "sector", "explanation",
    ]
    table = view[cols].head(top_n).rename(columns={
        "score": "Score", "priority": "Prioridade", "opportunity_id": "Deal",
        "sales_agent": "Vendedor", "account": "Conta", "product": "Produto",
        "deal_stage": "Estágio", "days_in_pipeline": "Dias no pipeline",
        "sales_price": "Preço", "expected_value": "Valor esperado",
        "regional_office": "Região", "manager": "Manager", "sector": "Setor",
        "explanation": "Por quê",
    })
    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%d"),
            "Preço": st.column_config.NumberColumn(format="$%d"),
            "Valor esperado": st.column_config.NumberColumn(format="$%d"),
            "Por quê": st.column_config.TextColumn(width="large"),
        },
    )
    st.download_button(
        "⬇️ Baixar lista filtrada (CSV)",
        data=view[cols].to_csv(index=False).encode("utf-8"),
        file_name="pipeline_priorizado.csv",
        mime="text/csv",
    )

# --------------------------------------------------------------------------- #
# Aba 2: detalhe
# --------------------------------------------------------------------------- #

with tab_detail:
    if view.empty:
        st.info("Nenhum deal com os filtros atuais.")
    else:
        options = view["opportunity_id"] + " — " + view["account"].fillna("(sem conta)") \
            + " · " + view["product"] + " · score " + view["score"].astype(str)
        choice = st.selectbox("Escolha um deal", options.tolist())
        r = view.iloc[options.tolist().index(choice)]

        left, right = st.columns([1, 2])
        with left:
            color = PRIORITY_COLORS[r["priority"]]
            st.markdown(
                f"<h1 style='color:{color};margin:0'>{r['score']}</h1>"
                f"<h3 style='color:{color};margin:0'>{r['priority']}</h3>",
                unsafe_allow_html=True,
            )
            st.markdown(f"**Vendedor:** {r['sales_agent']}  \n"
                        f"**Manager:** {r['manager']} · **Região:** {r['regional_office']}  \n"
                        f"**Conta:** {r['account']} ({r['sector']})  \n"
                        f"**Produto:** {r['product']} — ${r['sales_price']:,.0f}  \n"
                        f"**Estágio:** {r['deal_stage']}  \n"
                        f"**Dias no pipeline:** {r['days_in_pipeline'] if pd.notna(r['days_in_pipeline']) else '—'}")
            st.success(f"**Próximo passo sugerido:** {recommended_action(r)}")

        with right:
            ct = component_table(r, weights)
            fig = px.bar(
                ct.sort_values("Pontos"), x="Pontos", y="Componente", orientation="h",
                text="Pontos", range_x=[0, max(ct["Máx. possível"]) + 5],
                title="De onde vêm os pontos",
            )
            fig.add_bar(
                x=ct.sort_values("Pontos")["Máx. possível"], y=ct.sort_values("Pontos")["Componente"],
                orientation="h", opacity=0.15, name="Máximo possível", marker_color="gray",
            )
            fig.update_layout(barmode="overlay", showlegend=False, height=350, margin=dict(t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(ct, hide_index=True, use_container_width=True)

        st.markdown("**Explicação completa:**")
        for line in r["explanation"].split(" · "):
            st.markdown(f"- {line}")

# --------------------------------------------------------------------------- #
# Aba 3: visão geral (para managers)
# --------------------------------------------------------------------------- #

with tab_overview:
    a, b = st.columns(2)
    with a:
        by_agent = (
            view.groupby("sales_agent")
            .agg(deals=("score", "size"), quentes=("priority", lambda s: (s == "Quente").sum()),
                 score_medio=("score", "mean"), valor_esperado=("expected_value", "sum"))
            .sort_values("quentes", ascending=False).reset_index()
        )
        st.subheader("Por vendedor")
        st.dataframe(by_agent.round(0), hide_index=True, use_container_width=True)
    with b:
        st.subheader("Distribuição de scores")
        fig = px.histogram(view, x="score", color="priority", nbins=25,
                           color_discrete_map=PRIORITY_COLORS)
        fig.update_layout(height=350, margin=dict(t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Quentes por região e produto")
    hot = view[view["priority"] == "Quente"]
    if not hot.empty:
        pivot = hot.pivot_table(index="regional_office", columns="product",
                                values="score", aggfunc="size", fill_value=0)
        st.dataframe(pivot, use_container_width=True)
    else:
        st.info("Nenhum deal quente com os filtros atuais.")

# --------------------------------------------------------------------------- #
# Aba 4: metodologia
# --------------------------------------------------------------------------- #

with tab_method:
    st.markdown(f"""
O score vai de **0 a 100** e é a soma ponderada de 7 componentes, cada um numa nota de 0 a 100.
Somente deals **abertos** (Prospecting/Engaging) recebem score; deals Won/Lost são usados como histórico.

| Componente | Peso | O que mede |
|---|---|---|
| Estágio do deal | {weights['stage']:.0%} | Engaging = 100, Prospecting = 40 |
| Tempo no pipeline | {weights['freshness']:.0%} | Dias desde o engajamento vs. ciclo mediano dos deals ganhos ({scored.attrs['median_cycle']:.0f} dias). Até a mediana = 100; 2× a mediana = 0 |
| Valor do produto | {weights['product_value']:.0%} | Percentil de preço do produto no catálogo |
| Histórico da conta | {weights['account_history']:.0%} | Taxa de vitória da conta, suavizada para a média global |
| Vendedor × produto | {weights['agent_product_fit']:.0%} | Taxa de vitória do vendedor naquele produto, suavizada |
| Porte da conta | {weights['account_size']:.0%} | Receita da conta (escala log) |
| Conversão do setor | {weights['sector_rate']:.0%} | Taxa de vitória do setor, suavizada |

**Faixas:** Quente ≥ {HOT_THRESHOLD} · Morno {WARM_THRESHOLD}–{HOT_THRESHOLD - 1} · Frio < {WARM_THRESHOLD}

**Valor esperado** = preço do produto × média entre taxa da conta e taxa vendedor×produto.
""")
```

---

## 4. `requirements.txt`

```
streamlit>=1.32
pandas>=2.0
numpy>=1.24
plotly>=5.18
```

---

## 5. `README.md`

````markdown
# Lead Scorer — Challenge 003 (Vendas / RevOps)

Ferramenta que o vendedor abre na segunda de manhã, vê o pipeline aberto ordenado
por score e entende **por que** cada deal está quente, morno ou frio.

## Setup

1. Baixe o dataset [CRM Sales Predictive Analytics](https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics)
   e coloque os quatro arquivos em `data/`:
   `accounts.csv`, `products.csv`, `sales_teams.csv`, `sales_pipeline.csv`.
2. Crie o ambiente e instale as dependências:

   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\activate  |  Linux/macOS: source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Rode o app:

   ```bash
   streamlit run app.py
   ```

   Abra `http://localhost:8501`.

Uso sem interface (gera CSV priorizado):

```python
from scoring import load_data, score_pipeline
scored = score_pipeline(load_data("data"))
scored.to_csv("pipeline_priorizado.csv", index=False)
```

## Como usar

- **Lista priorizada:** pipeline aberto do maior para o menor score, com a coluna "Por quê".
  Filtre por região, manager, vendedor, produto, setor, estágio ou prioridade na barra lateral.
- **Detalhe do deal:** escolha um deal e veja o gráfico de contribuição de cada componente,
  a explicação completa e um próximo passo sugerido.
- **Visão geral:** resumo por vendedor e distribuição de scores (útil para managers).
- **Pesos ajustáveis:** a barra lateral permite mudar os pesos; os scores recalculam na hora.

## Lógica de scoring

Score (0–100) = soma ponderada de 7 componentes, todos em escala 0–100:

| Componente | Peso | Por quê |
|---|---|---|
| Estágio (Engaging=100, Prospecting=40) | 20% | Deal engajado tem chance muito maior de fechar |
| Tempo no pipeline vs. ciclo mediano dos ganhos | 20% | Deals muito acima do ciclo típico esfriam; recentes merecem atenção |
| Valor do produto (percentil de preço) | 15% | Ticket importa, mas não é o único critério |
| Histórico de vitórias da conta (suavizado) | 15% | Contas que já compraram tendem a comprar de novo |
| Taxa de vitória do vendedor naquele produto (suavizada) | 15% | Fit vendedor × produto é sinal real de conversão |
| Porte da conta (log da receita) | 10% | Empresas maiores têm mais orçamento |
| Taxa de vitória do setor (suavizada) | 5% | Sinal fraco, peso pequeno |

Taxas de vitória usam suavização bayesiana (`(wins + 5·média) / (n + 5)`) para que uma
conta ou combinação com 1 ou 2 deals não receba nota extrema.

Faixas: **Quente ≥ 70**, **Morno 45–69**, **Frio < 45**.
A data de referência é a última data presente no dataset (2017), não a data atual.

## Limitações

- **Não é ML supervisionado:** é um modelo de regras/heurísticas com pesos definidos
  manualmente. Não foi validado contra um holdout; os pesos refletem julgamento, não fitting.
- **Dataset estático e histórico:** o app lê CSVs. Para uso real seria preciso conectar ao CRM
  (API/DB) e agendar recálculo diário.
- **Sem dados de atividade:** o dataset não tem e-mails, ligações, reuniões ou notas — sinais
  fortes de intenção que melhorariam muito o score.
- **`engage_date` ausente em muitos deals Prospecting:** esses recebem nota neutra de frescor.
- **Vazamento leve de informação:** taxas de vitória da conta/vendedor são calculadas sobre
  todo o histórico, inclusive deals fechados depois do início dos deals abertos.
- **Sem feedback loop:** não há como o vendedor marcar "esse score estava errado".

## Para escalar

1. Trocar CSVs por conexão ao CRM (Salesforce/HubSpot) e materializar o score em uma coluna
   do próprio CRM.
2. Validar os pesos com backtest (split temporal) e, se valer a pena, treinar um modelo
   logístico/GBM mantendo a explicação por componente (SHAP).
3. Adicionar sinais de atividade (última interação, respostas de e-mail).
4. Autenticação por vendedor com filtro automático e notificação semanal (Slack/e-mail).
5. Testes unitários em `scoring.py` (pesos somam 1, ranges 0–100, joins sem perda).

## Process log

Ver `process-log.md` (prompts usados, iterações e decisões) conforme o guia de submissão.
````

---

## 6. Como o vendedor lê o resultado

Ao abrir o app, ele vê os KPIs no topo (quantos quentes/mornos/frios), filtra pelo próprio nome na barra lateral e recebe a lista ordenada. A coluna **"Por quê"** e a aba **Detalhe** mostram exatamente quais fatores puxaram o score para cima ou para baixo, e o campo **"Próximo passo sugerido"** transforma o número em ação (fechar, reativar, desqualificar). Managers usam a aba **Visão geral** para ver onde cada vendedor deve concentrar esforço.
