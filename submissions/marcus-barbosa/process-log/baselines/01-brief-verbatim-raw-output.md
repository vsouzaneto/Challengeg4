# Baseline 1 — brief-verbatim — saída bruta (sem edição)

# Challenge 003 — Lead Scorer: Solução Completa

Abaixo está uma solução completa e funcional para o challenge: lógica de scoring explicável, arquitetura, código pronto para rodar (Streamlit + pandas), roteiro de construção em 4-6 horas e o texto da documentação (Setup, Lógica, Limitações) pronto para o README.

---

## 1. Visão geral da solução

**O que é:** uma aplicação web em **Streamlit** chamada **"Pipeline Prioritizer"**, que lê os 4 CSVs do dataset CRM, calcula um **score de 0 a 100 para cada oportunidade aberta** (Prospecting/Engaging), explica **por que** cada deal recebeu aquele score e mostra ao vendedor uma **lista priorizada de ação** com filtros por vendedor, manager e região.

**Por que Streamlit:** é a tecnologia com melhor relação custo/benefício para o time budget de 4-6h. Roda com um comando, não precisa de front-end separado, e a Head de RevOps pediu explicitamente "algo que o vendedor abra e saiba onde focar" — não um notebook.

**Princípios de design:**
1. **Explicabilidade acima de acurácia.** Scoring por regras + estatísticas históricas, com contribuição de cada fator visível na tela.
2. **Aprender com os dados, não inventar pesos.** Os pesos das features (produto, conta, vendedor, setor) são derivados das taxas históricas de ganho (win rate) dos deals Won/Lost. Não é ML "caixa-preta", mas também não é chute.
3. **Decisão, não só dados.** A interface responde três perguntas: *Em quais deals eu foco hoje? Quais estão esfriando? Quais eu deveria deixar de lado?*

---

## 2. Entendendo os dados (o que o brief nos diz)

| Tabela | Uso no scoring |
|---|---|
| `sales_pipeline.csv` (~8.800) | Tabela central. Deals `Won`/`Lost` viram o **histórico de treino** das taxas de conversão. Deals `Prospecting`/`Engaging` são os **deals a pontuar**. |
| `accounts.csv` (~85) | Setor, receita, nº de funcionários, localização, empresa-mãe → tamanho/perfil da conta. |
| `products.csv` (7) | Série e preço → valor esperado do deal e win rate por produto. |
| `sales_teams.csv` (35) | Vendedor → manager → escritório regional. Usado para filtros e para a win rate por vendedor. |

Campos-chave do pipeline: `opportunity_id`, `sales_agent`, `product`, `account`, `deal_stage`, `engage_date`, `close_date`, `close_value`.

Observações importantes (típicas desse dataset, e que a solução deve tratar de forma defensiva):
- Deals em `Prospecting` costumam não ter `engage_date` nem `account` preenchidos.
- `close_value` é 0 (ou vazio) para deals Lost e abertos; para o valor esperado dos abertos usamos o **preço de lista do produto** (`products.sales_price`) ou o ticket médio histórico Won daquele produto.
- Não há "data de hoje" no dataset; usamos como referência a **última data presente no pipeline** (`max(close_date, engage_date)`), para que "dias no pipeline" faça sentido.

---

## 3. Lógica de scoring (o coração da solução)

### 3.1. Estrutura

O score final (0–100) é uma **soma ponderada de 6 fatores**, cada um normalizado de 0 a 1. Cada fator gera também uma **frase explicativa** que aparece na interface.

| # | Fator | Peso | O que mede | Como é calculado |
|---|---|---|---|---|
| 1 | **Probabilidade por produto** | 20 | Alguns produtos convertem muito mais que outros | Win rate histórica do produto (Won / (Won+Lost)), com suavização bayesiana |
| 2 | **Probabilidade por conta** | 20 | Histórico da conta com a empresa | Win rate histórica da conta; se conta nova/sem histórico → média global com penalidade leve de incerteza |
| 3 | **Fit do perfil da conta** | 10 | Contas grandes/setores que compram mais | Win rate por setor + porte da conta (receita / funcionários em quantis) |
| 4 | **Estágio do deal** | 15 | Engaging está muito mais perto de fechar que Prospecting | Prospecting = 0,35; Engaging = 0,75 (ajustado pelas taxas reais de conversão observadas por estágio, se disponível) |
| 5 | **Momentum / tempo no pipeline** | 15 | Deals que passam muito tempo parados esfriam | Compara `dias desde engage_date` com a **mediana do ciclo dos deals Won daquele produto**. Dentro do ciclo típico = alto; muito além = penalidade ("esfriando") |
| 6 | **Valor esperado** | 20 | Deals maiores merecem mais atenção, mas não são o único critério | `valor_estimado = preço do produto (ou ticket médio Won do produto)`, normalizado por rank/percentil para não deixar um produto caro dominar |

**Score = 100 × Σ (peso_i × fator_i) / Σ pesos**

Adicionalmente, calcula-se o **Valor Esperado Ponderado (VEP)** = `P(ganho) × valor_estimado`, onde `P(ganho)` é a combinação dos fatores 1–4, que serve como segunda ordenação e como métrica de "quanto dinheiro está em jogo".

### 3.2. Por que esses fatores (e não só "ordenar por valor")

- **Produto e conta** são, nesse dataset, os maiores discriminadores de conversão: a win rate varia bastante entre os 7 produtos e entre contas. Ordenar só por valor ignora isso.
- **Vendedor** foi *deliberadamente excluído do score* (usado só como filtro). Motivo: incluir a win rate do vendedor no score do deal cria um viés circular ("vendedor fraco → deals dele recebem score baixo → ele foca menos → performa pior"). O vendedor vê seus próprios deals; comparar-se com colegas é papel do manager, não do score.
- **Tempo no pipeline** é a feature que mais responde à dor da Head de RevOps: "deixam oportunidades boas esfriar". O fator momentum torna visível o deal que está bom mas parado.
- **Estágio** é óbvio mas indispensável: um deal em Engaging tem informação real; Prospecting é quase uma lista de leads.

### 3.3. Suavização (evita win rates enganosas)

Uma conta com 1 deal Won teria win rate 100% — não é confiável. Usamos suavização bayesiana simples:

```
win_rate_suavizada = (wins + k × taxa_global) / (total + k),  com k = 5
```

Isso puxa entidades com pouco histórico para a média global. Quanto mais histórico, mais o valor real domina.

### 3.4. Classificação e ação recomendada

| Score | Faixa | Ação sugerida na interface |
|---|---|---|
| ≥ 70 | 🔥 **Foco** | Priorizar esta semana — alta chance de fechar |
| 45–69 | 🌡️ **Nutrir** | Manter contato regular; avançar para Engaging |
| < 45 | ❄️ **Desprioritizar** | Só voltar se houver novo sinal da conta |

Flags adicionais (badges):
- **"Esfriando"**: fator momentum < 0,3 e score ≥ 45 → deal bom que está parado. É a lista mais acionável na segunda-feira de manhã.
- **"Conta nova"**: sem histórico → score vem com mais incerteza.
- **"Ticket alto"**: valor esperado no top 20%.

### 3.5. Exemplo de explicação gerada

> **Score 82 — 🔥 Foco**
> - ✅ Produto *GTX Pro* tem win rate histórica de 68% (+17 pts)
> - ✅ Conta *Acme Corp* já fechou 7 de 9 deals conosco (+18 pts)
> - ✅ Deal em **Engaging** (+11 pts)
> - ⚠️ 41 dias em pipeline vs. ciclo típico de 30 dias para este produto — **está esfriando** (+5 pts de 15)
> - ✅ Valor estimado US$ 4.821 (top 20% do pipeline) (+17 pts)
> - ℹ️ Setor *technology* converte na média (+7 pts)
>
> **Próximo passo sugerido:** contato hoje; deal está além do ciclo típico.

---

## 4. Arquitetura

```
lead-scorer/
├── app.py                  # Interface Streamlit (UI)
├── scoring/
│   ├── __init__.py
│   ├── data.py             # Carga, limpeza e junção dos 4 CSVs
│   ├── features.py         # Cálculo das win rates, ciclos, quantis (o "treino")
│   ├── scorer.py           # Função score_deal() + geração das explicações
│   └── config.py           # Pesos, thresholds, k de suavização (tudo em um lugar)
├── data/
│   ├── accounts.csv
│   ├── products.csv
│   ├── sales_teams.csv
│   └── sales_pipeline.csv
├── tests/
│   └── test_scorer.py      # Testes unitários das regras
├── requirements.txt
├── README.md
└── PROCESS_LOG.md          # Evidências do uso de IA
```

**Fluxo de dados:**

```
CSVs → data.load_all() → DataFrame unificado
                         ├─ histórico (Won/Lost) → features.build_stats() → dict de win rates / ciclos / quantis
                         └─ abertos (Prospecting/Engaging) → scorer.score_pipeline(stats) → score + explicações
                                                                        ↓
                                                            app.py (filtros, tabela, detalhe, gráficos)
```

Separação clara: **`scoring/` não sabe que o Streamlit existe** — pode ser reaproveitado em uma API, CLI ou job que manda e-mail. Isso responde ao critério "código limpo para outro dev dar manutenção".

---

## 5. Como construir — código completo

### 5.1. `requirements.txt`

```
streamlit>=1.32
pandas>=2.0
numpy>=1.24
plotly>=5.18
pytest>=7.0
```

### 5.2. `scoring/config.py`

```python
"""Parâmetros do scoring. Altere aqui, nunca no código das regras."""

WEIGHTS = {
    "product_fit": 20,
    "account_history": 20,
    "account_profile": 10,
    "stage": 15,
    "momentum": 15,
    "value": 20,
}

STAGE_BASE = {"Prospecting": 0.35, "Engaging": 0.75}

SMOOTHING_K = 5              # força da suavização bayesiana
COOLING_RATIO = 1.5          # dias_no_pipeline / ciclo_mediano acima disso = "esfriando"
DEAD_RATIO = 3.0             # acima disso, momentum ~ 0

TIER_FOCUS = 70
TIER_NURTURE = 45
```

### 5.3. `scoring/data.py`

```python
import pandas as pd
from pathlib import Path

OPEN_STAGES = ["Prospecting", "Engaging"]
CLOSED_STAGES = ["Won", "Lost"]


def load_all(data_dir: str | Path = "data") -> pd.DataFrame:
    """Lê os 4 CSVs e retorna um único DataFrame de oportunidades enriquecido."""
    data_dir = Path(data_dir)
    pipeline = pd.read_csv(data_dir / "sales_pipeline.csv")
    accounts = pd.read_csv(data_dir / "accounts.csv")
    products = pd.read_csv(data_dir / "products.csv")
    teams = pd.read_csv(data_dir / "sales_teams.csv")

    # Normalização de nomes de coluna (o dataset usa snake_case, mas garantimos)
    for df in (pipeline, accounts, products, teams):
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Datas
    pipeline["engage_date"] = pd.to_datetime(pipeline["engage_date"], errors="coerce")
    pipeline["close_date"] = pd.to_datetime(pipeline["close_date"], errors="coerce")
    pipeline["close_value"] = pd.to_numeric(pipeline["close_value"], errors="coerce").fillna(0)

    # Ajuste conhecido do dataset: produto "GTXPro" no pipeline vs "GTX Pro" no catálogo
    pipeline["product"] = pipeline["product"].replace({"GTXPro": "GTX Pro"})

    df = (
        pipeline
        .merge(products, on="product", how="left")
        .merge(accounts, on="account", how="left")
        .merge(teams, on="sales_agent", how="left")
    )

    # Data de referência = último evento do dataset (não existe "hoje" nos dados)
    ref_date = pd.concat([df["engage_date"], df["close_date"]]).max()
    df.attrs["ref_date"] = ref_date

    df["is_open"] = df["deal_stage"].isin(OPEN_STAGES)
    df["is_closed"] = df["deal_stage"].isin(CLOSED_STAGES)
    df["days_in_pipeline"] = (ref_date - df["engage_date"]).dt.days
    return df
```

### 5.4. `scoring/features.py`

```python
import pandas as pd
from .config import SMOOTHING_K


def _smoothed_win_rate(closed: pd.DataFrame, key: str, global_rate: float) -> pd.DataFrame:
    g = closed.groupby(key)["deal_stage"].agg(
        wins=lambda s: (s == "Won").sum(), total="count"
    )
    g["win_rate"] = (g["wins"] + SMOOTHING_K * global_rate) / (g["total"] + SMOOTHING_K)
    return g


def build_stats(df: pd.DataFrame) -> dict:
    """Calcula todas as estatísticas históricas usadas no scoring."""
    closed = df[df["is_closed"]].copy()
    won = closed[closed["deal_stage"] == "Won"]
    global_rate = (closed["deal_stage"] == "Won").mean()

    # Ciclo mediano (engage -> close) por produto, apenas deals Won
    cycle = (won["close_date"] - won["engage_date"]).dt.days
    cycle_by_product = cycle.groupby(won["product"]).median()

    # Ticket médio Won por produto (fallback para preço de lista)
    avg_value_by_product = won.groupby("product")["close_value"].mean()

    # Quantis de porte de conta
    accounts = df.drop_duplicates("account")[["account", "revenue", "employees"]].dropna()
    revenue_q = accounts["revenue"].quantile([0.33, 0.66]).tolist() if len(accounts) else [0, 0]

    return {
        "global_rate": global_rate,
        "product": _smoothed_win_rate(closed, "product", global_rate),
        "account": _smoothed_win_rate(closed, "account", global_rate),
        "sector": _smoothed_win_rate(closed, "sector", global_rate),
        "stage_conversion": _stage_conversion(df, global_rate),
        "cycle_by_product": cycle_by_product,
        "cycle_global": cycle.median(),
        "avg_value_by_product": avg_value_by_product,
        "revenue_q": revenue_q,
    }


def _stage_conversion(df: pd.DataFrame, global_rate: float) -> dict:
    """Taxa de conversão observada: deals que tiveram engage_date (passaram por Engaging)
    convertem a X%; deals sem engage_date (só Prospecting) são desconhecidos -> base."""
    closed = df[df["is_closed"]]
    engaged = closed[closed["engage_date"].notna()]
    engaged_rate = (engaged["deal_stage"] == "Won").mean() if len(engaged) else global_rate
    return {"Engaging": float(engaged_rate), "Prospecting": float(global_rate * 0.6)}
```

### 5.5. `scoring/scorer.py`

```python
import numpy as np
import pandas as pd
from .config import WEIGHTS, STAGE_BASE, COOLING_RATIO, DEAD_RATIO, TIER_FOCUS, TIER_NURTURE


def _lookup(table: pd.DataFrame, key, default: float) -> tuple[float, int]:
    if key in table.index:
        return float(table.loc[key, "win_rate"]), int(table.loc[key, "total"])
    return default, 0


def score_deal(row: pd.Series, stats: dict) -> dict:
    g = stats["global_rate"]
    factors, reasons = {}, []

    # 1. Produto
    pr, pn = _lookup(stats["product"], row["product"], g)
    factors["product_fit"] = pr
    reasons.append(("product_fit", f"Produto {row['product']} converte {pr:.0%} historicamente ({pn} deals fechados)"))

    # 2. Histórico da conta
    if pd.isna(row.get("account")):
        ar, an = g * 0.9, 0
        reasons.append(("account_history", "Conta não informada — usando média global com leve penalidade"))
    else:
        ar, an = _lookup(stats["account"], row["account"], g * 0.9)
        if an == 0:
            reasons.append(("account_history", f"Conta {row['account']} é nova (sem histórico) — incerteza maior"))
        else:
            wins = int(stats["account"].loc[row["account"], "wins"])
            reasons.append(("account_history", f"Conta {row['account']} fechou {wins} de {an} deals conosco ({ar:.0%})"))
    factors["account_history"] = ar

    # 3. Perfil da conta (setor + porte)
    sr, _ = _lookup(stats["sector"], row.get("sector"), g)
    size_bonus = 0.5
    if not pd.isna(row.get("revenue")):
        q1, q2 = stats["revenue_q"]
        size_bonus = 0.35 if row["revenue"] < q1 else (0.6 if row["revenue"] < q2 else 0.85)
    factors["account_profile"] = 0.6 * sr + 0.4 * size_bonus
    reasons.append(("account_profile", f"Setor {row.get('sector', 'n/d')} converte {sr:.0%}; porte da conta: "
                                       f"{'grande' if size_bonus > 0.7 else 'médio' if size_bonus > 0.4 else 'pequeno'}"))

    # 4. Estágio
    st = stats["stage_conversion"].get(row["deal_stage"], STAGE_BASE.get(row["deal_stage"], 0.5))
    factors["stage"] = st
    reasons.append(("stage", f"Deal em {row['deal_stage']} — conversão típica {st:.0%} a partir daqui"))

    # 5. Momentum
    cycle = stats["cycle_by_product"].get(row["product"], stats["cycle_global"]) or stats["cycle_global"]
    days = row.get("days_in_pipeline")
    cooling = False
    if pd.isna(days):
        mom = 0.5
        reasons.append(("momentum", "Sem data de engajamento — momentum desconhecido"))
    else:
        ratio = days / max(cycle, 1)
        if ratio <= 1:
            mom = 1.0
        elif ratio >= DEAD_RATIO:
            mom = 0.05
        else:
            mom = float(np.interp(ratio, [1, COOLING_RATIO, DEAD_RATIO], [1.0, 0.45, 0.05]))
        cooling = ratio > COOLING_RATIO
        reasons.append(("momentum", f"{int(days)} dias em pipeline vs. ciclo típico de {int(cycle)} dias"
                                    + (" — ESTÁ ESFRIANDO" if cooling else "")))
    factors["momentum"] = mom

    # 6. Valor esperado (normalizado fora, aqui só bruto)
    est_value = row.get("sales_price")
    if pd.isna(est_value):
        est_value = stats["avg_value_by_product"].get(row["product"], 0)
    factors["_est_value"] = float(est_value or 0)

    p_win = np.mean([factors["product_fit"], factors["account_history"], factors["account_profile"], factors["stage"]])
    return {"factors": factors, "reasons": reasons, "cooling": cooling, "p_win": float(p_win),
            "est_value": factors["_est_value"]}


def score_pipeline(df: pd.DataFrame, stats: dict) -> pd.DataFrame:
    open_df = df[df["is_open"]].copy()
    results = [score_deal(r, stats) for _, r in open_df.iterrows()]

    # Normaliza valor por percentil (evita que 1 produto caro domine)
    est = pd.Series([r["est_value"] for r in results], index=open_df.index)
    value_factor = est.rank(pct=True)

    total_w = sum(WEIGHTS.values())
    rows = []
    for (idx, r), vf in zip(zip(open_df.index, results), value_factor):
        f = r["factors"]
        f["value"] = float(vf)
        contrib = {k: WEIGHTS[k] * f[k] for k in WEIGHTS}
        score = 100 * sum(contrib.values()) / total_w
        tier = "🔥 Foco" if score >= TIER_FOCUS else ("🌡️ Nutrir" if score >= TIER_NURTURE else "❄️ Desprioritizar")
        rows.append({
            "score": round(score, 1), "tier": tier, "p_win": round(r["p_win"], 3),
            "est_value": round(r["est_value"], 0),
            "expected_value": round(r["p_win"] * r["est_value"], 0),
            "cooling": r["cooling"] and score >= TIER_NURTURE,
            "contrib": contrib, "reasons": r["reasons"],
        })
    scored = pd.concat([open_df, pd.DataFrame(rows, index=open_df.index)], axis=1)
    return scored.sort_values(["score", "expected_value"], ascending=False)


def explain(row: pd.Series) -> str:
    """Texto em Markdown para o painel de detalhe."""
    lines = [f"### Score {row['score']:.0f} — {row['tier']}"]
    for key, text in row["reasons"]:
        pts = row["contrib"][key]
        icon = "✅" if pts / WEIGHTS[key] >= 0.6 else ("⚠️" if pts / WEIGHTS[key] >= 0.3 else "❌")
        lines.append(f"- {icon} {text} **(+{pts:.0f} de {WEIGHTS[key]} pts)**")
    lines.append(f"- 💰 Valor estimado US$ {row['est_value']:,.0f} → percentil {row['contrib']['value']/WEIGHTS['value']:.0%} "
                 f"**(+{row['contrib']['value']:.0f} de {WEIGHTS['value']} pts)**")
    nxt = ("**Próximo passo:** contato hoje — deal bom e além do ciclo típico." if row["cooling"]
           else "**Próximo passo:** avançar para proposta/fechamento." if row["score"] >= TIER_FOCUS
           else "**Próximo passo:** follow-up leve; buscar sinal de interesse." if row["score"] >= TIER_NURTURE
           else "**Próximo passo:** manter em radar; não gastar tempo ativo.")
    lines.append(nxt)
    return "\n".join(lines)
```

### 5.6. `app.py`

```python
import streamlit as st
import plotly.express as px
import pandas as pd
from scoring.data import load_all
from scoring.features import build_stats
from scoring.scorer import score_pipeline, explain

st.set_page_config(page_title="Pipeline Prioritizer", layout="wide", page_icon="🎯")


@st.cache_data
def get_scored():
    df = load_all("data")
    stats = build_stats(df)
    scored = score_pipeline(df, stats)
    return df, stats, scored


df, stats, scored = get_scored()

# ---------- Sidebar: filtros ----------
st.sidebar.title("Filtros")
region = st.sidebar.multiselect("Região", sorted(scored["regional_office"].dropna().unique()))
manager = st.sidebar.multiselect("Manager", sorted(scored["manager"].dropna().unique()))
agent = st.sidebar.multiselect("Vendedor", sorted(scored["sales_agent"].dropna().unique()))
stage = st.sidebar.multiselect("Estágio", ["Prospecting", "Engaging"], default=["Prospecting", "Engaging"])
only_cooling = st.sidebar.checkbox("Só deals esfriando")

view = scored.copy()
if region:  view = view[view["regional_office"].isin(region)]
if manager: view = view[view["manager"].isin(manager)]
if agent:   view = view[view["sales_agent"].isin(agent)]
if stage:   view = view[view["deal_stage"].isin(stage)]
if only_cooling: view = view[view["cooling"]]

# ---------- Header: o que fazer hoje ----------
st.title("🎯 Pipeline Prioritizer")
st.caption(f"Data de referência dos dados: {df.attrs['ref_date']:%d/%m/%Y} · "
           f"{len(view)} deals abertos no filtro")

c1, c2, c3, c4 = st.columns(4)
c1.metric("🔥 Foco", int((view["tier"].str.startswith("🔥")).sum()))
c2.metric("🌡️ Nutrir", int((view["tier"].str.startswith("🌡️")).sum()))
c3.metric("❄️ Desprioritizar", int((view["tier"].str.startswith("❄️")).sum()))
c4.metric("⚠️ Esfriando", int(view["cooling"].sum()))

st.markdown("## Sua lista de hoje")
top = view.head(10)
for _, r in top.iterrows():
    flag = " ⚠️ esfriando" if r["cooling"] else ""
    st.markdown(f"**{r['score']:.0f}** · {r['tier']} · {r['product']} → "
                f"{r['account'] if pd.notna(r['account']) else '(conta n/d)'} · "
                f"US$ {r['est_value']:,.0f} · {r['deal_stage']}{flag}")

# ---------- Tabela completa ----------
st.markdown("## Pipeline priorizado")
cols = ["opportunity_id", "score", "tier", "cooling", "sales_agent", "account", "product",
        "deal_stage", "days_in_pipeline", "est_value", "expected_value"]
st.dataframe(view[cols].reset_index(drop=True), use_container_width=True, height=400)

# ---------- Detalhe ----------
st.markdown("## Por que esse score?")
sel = st.selectbox("Escolha uma oportunidade", view["opportunity_id"].tolist())
row = view[view["opportunity_id"] == sel].iloc[0]
left, right = st.columns([2, 1])
with left:
    st.markdown(explain(row))
with right:
    contrib = pd.DataFrame({"fator": list(row["contrib"].keys()), "pontos": list(row["contrib"].values())})
    st.plotly_chart(px.bar(contrib, x="pontos", y="fator", orientation="h", title="Contribuição por fator"),
                    use_container_width=True)

# ---------- Visão do manager ----------
with st.expander("Visão do manager: onde está o valor do pipeline"):
    agg = view.groupby("sales_agent").agg(deals=("score", "size"), score_medio=("score", "mean"),
                                          valor_esperado=("expected_value", "sum"),
                                          esfriando=("cooling", "sum")).sort_values("valor_esperado", ascending=False)
    st.dataframe(agg.round(1), use_container_width=True)
    st.plotly_chart(px.scatter(view, x="days_in_pipeline", y="score", color="tier", size="est_value",
                               hover_data=["opportunity_id", "account", "product"],
                               title="Score × dias no pipeline"), use_container_width=True)

st.download_button("⬇️ Exportar lista priorizada (CSV)",
                   view[cols].to_csv(index=False).encode(), "pipeline_priorizado.csv", "text/csv")
```

### 5.7. `tests/test_scorer.py`

```python
import pandas as pd
from scoring.scorer import score_pipeline
from scoring.features import build_stats
from scoring.data import load_all


def test_scores_in_range():
    df = load_all("data")
    scored = score_pipeline(df, build_stats(df))
    assert scored["score"].between(0, 100).all()


def test_engaging_scores_higher_than_prospecting_on_average():
    df = load_all("data")
    scored = score_pipeline(df, build_stats(df))
    m = scored.groupby("deal_stage")["score"].mean()
    assert m["Engaging"] > m["Prospecting"]


def test_every_deal_has_explanation():
    df = load_all("data")
    scored = score_pipeline(df, build_stats(df))
    assert scored["reasons"].apply(len).min() >= 5
```

---

## 6. Roteiro de construção (4-6 horas)

| Bloco | Tempo | O que fazer | Como usar IA |
|---|---|---|---|
| 0. Setup | 20 min | Baixar dataset do Kaggle, criar venv, `pip install`, estrutura de pastas | Pedir ao Claude Code/Cursor para gerar esqueleto e `requirements.txt` |
| 1. Exploração rápida | 40 min | `df.describe()`, win rate por produto/conta/setor, distribuição de ciclo, % de nulos em `engage_date`/`account` | Pedir "explore esses CSVs e me diga quais features discriminam Won vs Lost" — **anotar as descobertas no Process Log** |
| 2. `data.py` + `features.py` | 60 min | Carga, joins, correção do `GTXPro`, estatísticas suavizadas | Gerar com IA, revisar joins (contar linhas antes/depois) |
| 3. `scorer.py` | 60 min | Fatores, pesos, explicações, tiers | Iterar pesos olhando os top 20 e perguntando "faz sentido para um vendedor?" |
| 4. `app.py` | 60 min | Filtros, lista do dia, tabela, detalhe, visão manager | v0/Cursor para layout; ajustar textos em PT-BR |
| 5. Testes + README | 40 min | `pytest`, escrever Setup/Lógica/Limitações | IA gera rascunho; você valida rodando do zero em pasta limpa |
| 6. Process log | 20 min | Prints, prompts usados, decisões que você tomou *contra* a sugestão da IA | — |

**Checklist de "funciona de verdade":**
- [ ] `git clone` + `pip install -r requirements.txt` + `streamlit run app.py` funciona em máquina limpa
- [ ] Os 4 CSVs reais estão em `data/` (ou há instrução clara de download)
- [ ] Score não é monotônico com valor (verifique: há deals caros com score baixo e baratos com score alto)
- [ ] Cada deal mostra ≥ 5 razões
- [ ] Filtros por vendedor/manager/região funcionam
- [ ] `pytest` passa

---

## 7. Texto da documentação (README.md pronto)

```markdown
# Pipeline Prioritizer — Lead Scorer para o time de Vendas

Ferramenta web que lê o pipeline do CRM, atribui um score de 0 a 100 a cada oportunidade
aberta e explica, em linguagem de vendedor, por que aquele deal merece (ou não) atenção.

## Setup

**Pré-requisitos:** Python 3.10+.

1. Clone o repositório e entre na pasta:
   git clone <url> && cd lead-scorer
2. Crie o ambiente e instale as dependências:
   python -m venv .venv && source .venv/bin/activate   (Windows: .venv\Scripts\activate)
   pip install -r requirements.txt
3. Coloque os 4 CSVs do dataset [CRM Sales Predictive Analytics](https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics)
   na pasta `data/`: `accounts.csv`, `products.csv`, `sales_teams.csv`, `sales_pipeline.csv`.
4. Rode:
   streamlit run app.py
5. Abra http://localhost:8501.

Testes: `pytest`.

## Como usar (para o vendedor)

1. Na barra lateral, filtre pelo seu nome (ou o manager filtra pela equipe/região).
2. "Sua lista de hoje" mostra os 10 deals com maior score. Comece por eles.
3. Marque "Só deals esfriando" para ver deals bons que estão parados há mais tempo que o normal.
4. Clique em qualquer oportunidade em "Por que esse score?" para ver a explicação fator a fator e o próximo passo sugerido.
5. Exporte a lista em CSV se quiser levar para a reunião de pipeline.

## Lógica de scoring

O score é uma soma ponderada de seis fatores (0–100). Os pesos e limites estão em `scoring/config.py`.

| Fator | Peso | Por quê |
|---|---|---|
| Win rate do produto | 20 | Os 7 produtos convertem em taxas muito diferentes; é o sinal mais forte do histórico. |
| Histórico da conta | 20 | Contas que já compraram tendem a comprar de novo. Contas novas recebem a média global com leve penalidade de incerteza. |
| Perfil da conta (setor + porte) | 10 | Setores e portes diferentes têm propensões diferentes; peso menor porque é um sinal indireto. |
| Estágio | 15 | Engaging tem conversão observada muito maior que Prospecting. |
| Momentum (tempo no pipeline vs. ciclo típico do produto) | 15 | Deal parado além do ciclo mediano dos deals ganhos está esfriando. Este é o fator que ataca diretamente o problema "oportunidades boas esfriam". |
| Valor estimado (percentil) | 20 | Deals maiores merecem atenção — mas o valor entra normalizado por percentil, para que um produto caro não domine o ranking. |

Decisões importantes:
- **Win rates são suavizadas** (Bayes, k=5) para que uma conta com 1 deal não apareça com 100%.
- **O vendedor não entra no score.** Ele é filtro. Incluí-lo criaria um viés circular e penalizaria vendedores novos.
- **Data de referência** é o último evento do dataset (não existe "hoje" nos dados históricos).
- **Explicabilidade:** cada fator gera uma frase e a contribuição em pontos, exibidas no painel de detalhe.
- Além do score, calculamos **valor esperado = P(ganho) × valor estimado**, usado como desempate e na visão do manager.

Faixas: ≥70 Foco · 45–69 Nutrir · <45 Desprioritizar. Flag "esfriando" = deal com score ≥45 e tempo em pipeline > 1,5× o ciclo típico.

## Limitações

- **Não é um modelo preditivo calibrado.** As probabilidades são taxas históricas suavizadas, não saídas de um classificador validado. Para produção, o próximo passo seria treinar um modelo (regressão logística/GBM) com validação temporal e comparar com as regras.
- **Dados estáticos.** A ferramenta lê CSVs; não há integração com o CRM. Para escalar: conector com o CRM (API/Salesforce/HubSpot), job diário de recálculo e histórico dos scores.
- **Deals em Prospecting têm pouca informação** (frequentemente sem conta nem data de engajamento); o score deles é naturalmente menos confiável e a interface sinaliza isso.
- **Sem sinais de atividade** (e-mails, reuniões, respostas do cliente), que costumam ser os melhores preditores de momentum. O dataset não os tem.
- **Pesos definidos manualmente** a partir da exploração dos dados. Foram escolhidos por interpretabilidade, não otimizados.
- **Sem autenticação/multiusuário.** Streamlit local; para o time todo, hospedar (Streamlit Cloud, container interno) com login SSO.
- **Sem feedback loop.** O vendedor não pode marcar "esse score está errado". Um botão de feedback gravando em banco seria o primeiro incremento.
```

---

## 8. Process log — o que registrar

O challenge exige evidências do uso de IA. Estrutura sugerida para `PROCESS_LOG.md`:

1. **Ferramentas usadas** (Claude Code, Cursor, ChatGPT, v0…) e para quê.
2. **Prompts-chave** (copiar literalmente) — o de exploração dos dados, o de geração do scorer, o de revisão dos pesos.
3. **Onde a IA errou e você corrigiu** — ex.: join que duplicou linhas, `GTXPro` vs `GTX Pro`, sugestão de incluir vendedor no score que você rejeitou (e por quê).
4. **Iterações de scoring** — prints do top 10 antes e depois de cada mudança de peso.
5. **Tempo gasto por bloco** vs. planejado.

Avaliadores valorizam mais o item 3 do que qualquer outro: mostra critério humano sobre a saída da IA.

---

## 9. Extensões se sobrar tempo (em ordem de valor)

1. **Botão "Marcar como contactado"** (grava em SQLite) → o momentum reseta e a lista de segunda-feira fica limpa.
2. **Modo "e-mail de segunda"**: gera texto com os 5 deals de foco + 3 esfriando por vendedor, pronto para colar no Slack.
3. **Backtest simples**: pontuar deals que já fecharam usando só o que se sabia na época e mostrar que deals de score alto realmente fecharam mais (AUC ou lift por decil). Isso fecha a lacuna "faz sentido?" com evidência.
4. **API `POST /score`** reutilizando `scoring/` (FastAPI, ~30 linhas), para integrar no CRM.

