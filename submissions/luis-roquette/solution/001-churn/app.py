from __future__ import annotations

import json
import os
import sys
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

SOLUTION_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SOLUTION_ROOT / "src"))

from ravenstack_churn.publish import (
    DIMENSION_LABELS,
    ELIGIBILITY_LABELS,
    FINDING_LABELS,
    MRR_BAND_LABELS,
    QUALITY_LABELS,
    SEGMENT_LABELS,
    ArtifactConsistencyError,
    validate_artifact_set,
)

st.set_page_config(page_title="RavenStack Churn", layout="wide")
st.markdown(
    """
    <style>
    :root {
        --ink: #17201f;
        --paper: #f2efe7;
        --paper-deep: #e8e3d8;
        --signal: #a63a2a;
        --sage: #557164;
        --muted: #53615d;
        --line: rgba(23, 32, 31, .16);
        --font-body: "Source Sans 3", "Source Sans", sans-serif;
        --font-display: "Source Serif 4", "Source Serif", Georgia, serif;
    }
    html { color-scheme: light; }
    [data-testid="stAppViewContainer"] {
        color: var(--ink);
        background:
            linear-gradient(rgba(23, 32, 31, .025) 1px, transparent 1px),
            linear-gradient(90deg, rgba(23, 32, 31, .025) 1px, transparent 1px),
            var(--paper);
        background-size: 32px 32px;
    }
    [data-testid="stHeader"] { background: transparent; }
    .stMainBlockContainer {
        max-width: 1440px;
        padding: 2.25rem 3.5rem 5rem;
    }
    :focus-visible {
        outline: 3px solid #fffaf0 !important;
        outline-offset: 1px;
        box-shadow: 0 0 0 6px var(--ink) !important;
    }
    h1, h2, h3 { font-family: var(--font-display); color: var(--ink); }
    p, label, button, [data-testid="stCaptionContainer"] {
        font-family: var(--font-body);
    }
    .hero {
        position: relative;
        overflow: hidden;
        margin: 0 0 1.5rem;
        padding: 2rem 2.25rem 2.2rem;
        color: #f7f2e8;
        border-radius: 2px;
        background: var(--ink);
        box-shadow: 12px 12px 0 var(--paper-deep);
    }
    .hero::after {
        content: "";
        position: absolute;
        right: -4rem;
        bottom: -7rem;
        width: 24rem;
        height: 24rem;
        border: 1px solid rgba(247, 242, 232, .16);
        border-radius: 50%;
        box-shadow: 0 0 0 3rem rgba(247, 242, 232, .025), 0 0 0 6rem rgba(247, 242, 232, .02);
    }
    .hero-meta {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 2rem;
        color: #cfd5cc;
        font: 700 .72rem/1.2 var(--font-body);
        letter-spacing: .16em;
        text-transform: uppercase;
    }
    .hero-meta span:first-child::before {
        content: "";
        display: inline-block;
        width: .55rem;
        height: .55rem;
        margin-right: .65rem;
        border-radius: 50%;
        background: var(--signal);
        box-shadow: 0 0 0 4px rgba(214, 74, 50, .18);
    }
    .hero-grid { display: grid; grid-template-columns: 1.7fr .7fr; gap: 2rem; align-items: end; }
    .hero h1 {
        max-width: 760px;
        margin: 0;
        color: #fffaf0;
        font-size: clamp(3rem, 7vw, 6.6rem);
        font-weight: 500;
        line-height: .88;
        letter-spacing: -.055em;
    }
    .hero h1 em { color: #ef765f; font-weight: 400; }
    .hero-copy {
        max-width: 640px;
        margin: 1.25rem 0 0;
        color: #cfd5cc;
        font: 400 1rem/1.55 var(--font-body);
    }
    .hero-stamp {
        position: relative;
        z-index: 1;
        padding: 1.25rem;
        border: 1px solid rgba(247, 242, 232, .3);
        background: rgba(255, 255, 255, .04);
        font: 600 .78rem/1.65 var(--font-body);
        letter-spacing: .08em;
        text-transform: uppercase;
    }
    .hero-stamp strong { display: block; color: #ef765f; font-size: 1.05rem; }
    [data-testid="stTabs"] [role="tablist"] {
        gap: .35rem;
        padding: .35rem;
        border: 1px solid var(--line);
        background: rgba(232, 227, 216, .72);
    }
    [data-testid="stTab"] {
        min-height: 2.8rem;
        padding: .65rem 1rem;
        color: var(--muted);
        font-weight: 700;
        letter-spacing: .01em;
    }
    [data-testid="stTab"][aria-selected="true"] { color: #fffaf0; background: var(--ink); }
    [data-testid="stTab"] .react-aria-SelectionIndicator { display: none; }
    .section-heading {
        display: grid;
        grid-template-columns: 3.5rem 1fr;
        gap: 1rem;
        align-items: start;
        margin: 2.6rem 0 1.1rem;
        padding-top: 1rem;
        border-top: 1px solid var(--ink);
    }
    .section-heading > span {
        color: var(--signal);
        font: 800 .72rem/1 var(--font-body);
        letter-spacing: .14em;
    }
    .section-heading h2 { margin: -.25rem 0 .15rem; font-size: 2rem; font-weight: 500; }
    .section-heading p { margin: 0; color: var(--muted); font-size: .92rem; }
    [data-testid="stMetric"] {
        min-height: 132px;
        padding: 1.25rem 1.35rem;
        border: 1px solid var(--line);
        border-top: 4px solid var(--ink);
        background: rgba(255, 253, 247, .72);
        box-shadow: 0 8px 22px rgba(23, 32, 31, .05);
    }
    [data-testid="stMetricLabel"] { color: var(--muted); font-weight: 700; }
    [data-testid="stMetricValue"] {
        color: var(--ink);
        font-family: var(--font-display);
        font-size: 2.55rem;
        letter-spacing: -.04em;
    }
    [data-testid="stTable"] {
        overflow: hidden;
        border: 1px solid var(--line);
        border-radius: 2px;
        background: rgba(255, 253, 247, .74);
    }
    [data-testid="stTable"] thead tr th { color: #f7f2e8; background: var(--ink); }
    [data-testid="stTable"] tbody tr:nth-child(even) { background: rgba(232, 227, 216, .45); }
    [data-testid="stTable"] tbody tr:hover { background: rgba(214, 74, 50, .08); }
    [data-testid="stVegaLiteChart"] {
        padding: 1rem;
        border: 1px solid var(--line);
        background: rgba(255, 253, 247, .72);
    }
    .verdict {
        margin: 1.2rem 0;
        padding: 1.35rem 1.5rem;
        color: #fff8ee;
        border-left: 7px solid var(--signal);
        background: var(--ink);
    }
    .verdict small {
        display: block;
        margin-bottom: .4rem;
        color: #ef765f;
        font: 800 .68rem/1 var(--font-body);
        letter-spacing: .15em;
        text-transform: uppercase;
    }
    .verdict strong { font: 500 1.35rem/1.25 var(--font-display); }
    .insight-card {
        min-height: 100%;
        padding: 1.35rem 1.5rem;
        border: 1px solid var(--line);
        background: var(--paper-deep);
    }
    .insight-card small { color: var(--signal); font-weight: 800; letter-spacing: .12em; }
    .insight-card h3 { margin: .55rem 0 .75rem; font-size: 1.55rem; font-weight: 500; }
    .insight-card p { color: #45504c; line-height: 1.55; }
    .answer-block {
        display: grid;
        grid-template-columns: 4.5rem minmax(0, 1fr);
        gap: 1rem;
        margin: 0;
        padding: 1.35rem 0;
        border-top: 1px solid var(--line);
    }
    .answer-block:last-of-type { border-bottom: 1px solid var(--line); }
    .answer-index {
        color: var(--signal);
        font: 500 2.6rem/1 var(--font-display);
        letter-spacing: -.05em;
    }
    .answer-block h2 { margin: 0 0 .3rem; font-size: 1.7rem; font-weight: 500; }
    .answer-block p { max-width: 920px; margin: 0; color: var(--muted); line-height: 1.55; }
    .canonical-item {
        margin: .65rem 0 0;
        padding: .75rem 1rem;
        border-left: 3px solid var(--sage);
        background: rgba(255, 253, 247, .7);
    }
    .canonical-item strong { color: var(--signal); font: 800 .72rem/1 var(--font-body); }
    [data-testid="stAlert"] { border-radius: 2px; border-left-width: 6px; }
    [data-testid="stDataFrame"] { border: 1px solid var(--line); }
    [data-testid="stExpander"] { border: 1px solid var(--line); border-radius: 2px; }
    .stDownloadButton button {
        min-height: 2.8rem;
        color: #fffaf0;
        border: 1px solid var(--ink);
        border-radius: 2px;
        background: var(--ink);
        font-weight: 700;
    }
    .stDownloadButton button:hover { color: #fffaf0; border-color: var(--signal); background: var(--signal); }
    @media (max-width: 800px) {
        .stMainBlockContainer { padding: 1rem 1rem 3rem; }
        .hero { padding: 1rem; box-shadow: 6px 6px 0 var(--paper-deep); }
        .hero-grid { grid-template-columns: 1fr; gap: 1rem; }
        .hero h1 { font-size: 2.9rem; }
        .hero-copy { margin-top: .7rem; font-size: .9rem; }
        .hero-stamp { padding: .8rem; line-height: 1.45; }
        .hero-meta { align-items: flex-start; flex-direction: column; }
        .section-heading { grid-template-columns: 2rem 1fr; gap: .55rem; margin-top: 1.8rem; }
        .section-heading h2 { font-size: 1.7rem; }
        .answer-block { grid-template-columns: 2.4rem minmax(0, 1fr); gap: .6rem; }
        .answer-index { font-size: 1.8rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

artifact_dir = Path(os.environ.get("RAVENSTACK_ARTIFACT_DIR", SOLUTION_ROOT / "artifacts"))
try:
    manifest = validate_artifact_set(artifact_dir)
except (ArtifactConsistencyError, OSError, ValueError) as error:
    st.error(f"Artefatos inválidos: {error}. Execute `make reproduce`.")
    st.stop()


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(artifact_dir / name)


findings = read_csv("findings.csv")
segments = read_csv("segment_metrics.csv")
queue = read_csv("account_queue.csv")
watchlist = read_csv("account_watchlist.csv")
quality = json.loads((artifact_dir / "quality_report.json").read_text(encoding="utf-8"))
answer = json.loads((artifact_dir / "ceo_answer.json").read_text(encoding="utf-8"))
monthly_churn = read_csv("monthly_churn.csv")
reason_distribution = read_csv("reason_distribution.csv")
event_metrics = read_csv("event_cohort_metrics.csv")
mechanism_scorecard = read_csv("mechanism_scorecard.csv")
diagnostic_cutoff = pd.to_datetime(answer["parameters"]["scoring_cutoff"], errors="coerce")
cutoff_label = (
    f"{diagnostic_cutoff.day:02d} "
    f"{['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'][diagnostic_cutoff.month - 1]} "
    f"{diagnostic_cutoff.year}"
    if pd.notna(diagnostic_cutoff)
    else "não disponível"
)
analysis_status = {
    "supported": "Mecanismo sustentado",
    "tied": "Mecanismos empatados",
    "inconclusive": "Evidência inconclusiva",
    "unavailable": "Evidência indisponível",
}[answer["mechanism_status"]]
action_kind_labels = {
    "validation": "Validação",
    "intervention_proposal": "Proposta de intervenção",
}

st.markdown(
    f"""
    <section class="hero">
        <div class="hero-meta">
            <span>RavenStack / Retention Intelligence</span>
            <span>Challenge 001 · diagnóstico reproduzível</span>
        </div>
        <div class="hero-grid">
            <div>
                <h1>Churn,<br><em>sem atalhos.</em></h1>
                <p class="hero-copy">{escape(answer["headline"])}</p>
            </div>
            <div class="hero-stamp">
                Status da análise
                <strong>{analysis_status}</strong>
                Corte diagnóstico · {cutoff_label}<br>
                Modelo publicado · {"sim" if manifest["publish_model"] else "não"}
                <br>Análise · {escape(answer["analysis_id"][:10])}
            </div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)


def section_heading(number: str, title: str, description: str) -> None:
    st.markdown(
        f'<div class="section-heading"><span>{number}</span><div><h2>{title}</h2>'
        f"<p>{description}</p></div></div>",
        unsafe_allow_html=True,
    )


PERCENT_COLUMNS = {
    "Cobertura",
    "Cobertura da variável",
    "Diferença para taxa geral",
    "Taxa de churn",
    "Taxa geral",
}
CURRENCY_COLUMNS = {"MRR perdido", "MRR exposto", "MRR exposto máximo"}
DECIMAL_COLUMNS = {
    "Início",
    "Fim",
    "Odds ratio ajustado",
    "IC inferior",
    "IC superior",
    "Efeito selecionado",
    "Diferença entre cronologias",
}


def format_display_frame(frame: pd.DataFrame) -> pd.DataFrame:
    display = frame.reset_index(drop=True).copy()
    for column in display.columns:
        if column in PERCENT_COLUMNS:
            display[column] = display[column].map(
                lambda value: "n/d" if pd.isna(value) else f"{value:.1%}"
            )
        elif column in CURRENCY_COLUMNS:
            display[column] = display[column].map(
                lambda value: "n/d" if pd.isna(value) else f"US$ {value:,.0f}"
            )
        elif column == "Risco relativo":
            display[column] = display[column].map(
                lambda value: "n/d" if pd.isna(value) else f"{value:.2f}×"
            )
        elif column in DECIMAL_COLUMNS:
            display[column] = display[column].map(
                lambda value: "n/d" if pd.isna(value) else f"{value:.3f}"
            )
    return display.astype(object).where(pd.notna(display), "n/d")


def render_table(frame: pd.DataFrame) -> None:
    st.table(format_display_frame(frame).style.hide(axis="index"))


for index, block in enumerate(answer["blocks"], start=1):
    st.markdown(
        f"""
        <section class="answer-block" data-block-id="{escape(str(block["id"]))}">
            <div class="answer-index">{index:02d}</div>
            <div>
                <h2>{escape(str(block["title"]))}</h2>
                <small>{escape(str(block["confidence_label"]))}</small>
                <p>{escape(str(block["summary"]))}</p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    for claim in block["claims"]:
        st.markdown(
            '<div class="canonical-item">'
            f"<strong>{escape(str(claim['id']))}</strong><br>"
            f"{escape(str(claim['statement']))}<br>"
            f"<small>{escape(str(claim['confidence_label']))}</small></div>",
            unsafe_allow_html=True,
        )
    for action in block["actions"]:
        st.markdown(
            '<div class="canonical-item">'
            f"<strong>{escape(str(action['id']))} · "
            f"{escape(action_kind_labels.get(str(action['kind']), str(action['kind'])))}</strong><br>"
            f"{escape(str(action['description']))}<br>"
            f"<small>{escape(str(action['owner_role']))} · {int(action['deadline_days'])} dias · "
            f"avançar se {escape(str(action['advance_if']))}; parar se "
            f"{escape(str(action['stop_if']))}</small></div>",
            unsafe_allow_html=True,
        )


executive_tab, evidence_tab, queue_tab = st.tabs(
    ["Decisão executiva", "Evidências", "Fila operacional"]
)

with executive_tab:
    section_heading(
        "06",
        "Qualidade que limita a decisão",
        "Auditoria após a resposta canônica; não recalcula decisões nem prioridades.",
    )
    quality_rows = pd.DataFrame(
        [
            {"regra": rule, "linhas": count}
            for rule, count in quality.get("contradictions", {}).items()
            if count
        ],
        columns=["regra", "linhas"],
    ).sort_values("linhas", ascending=False)
    quality_rows["regra"] = quality_rows["regra"].replace(QUALITY_LABELS)
    render_table(quality_rows.rename(columns={"regra": "Regra", "linhas": "Linhas afetadas"}))
    section_heading(
        "03",
        "Segmentos observados",
        "Risco descritivo com elegibilidade explícita; amostras pequenas continuam inconclusivas.",
    )
    segment_confidence = segments.get("confidence", pd.Series("inconclusive", index=segments.index))
    visible_executive_segments = segments.assign(elegivel=segment_confidence.eq("eligible"))
    segment_order = [
        column for column in ("elegivel", "relative_risk") if column in visible_executive_segments
    ]
    visible_executive_segments = visible_executive_segments.sort_values(
        segment_order, ascending=False
    )
    segment_display = visible_executive_segments.drop(columns="elegivel").head(15).copy()
    if "confidence" not in segment_display:
        segment_display["confidence"] = "inconclusive"
    segment_display["dimension"] = segment_display["dimension"].replace(DIMENSION_LABELS)
    segment_display["segment"] = segment_display["segment"].replace(SEGMENT_LABELS)
    segment_display["confidence"] = segment_display["confidence"].replace(ELIGIBILITY_LABELS)
    executive_segment_columns = [
        "dimension",
        "segment",
        "sample_size",
        "churn_count",
        "churn_rate",
        "overall_churn_rate",
        "relative_risk",
        "mrr_lost",
        "confidence",
    ]
    segment_display = segment_display[
        [column for column in executive_segment_columns if column in segment_display]
    ]
    render_table(
        segment_display.rename(
            columns={
                "dimension": "Dimensão",
                "segment": "Segmento",
                "sample_size": "Contas",
                "churn_count": "Churns",
                "churn_rate": "Taxa de churn",
                "overall_churn_rate": "Taxa geral",
                "relative_risk": "Risco relativo",
                "mrr_lost": "MRR perdido",
                "mrr_exposed": "MRR exposto",
                "coverage": "Cobertura",
                "confidence": "Elegibilidade",
            }
        )
    )

with evidence_tab:
    section_heading(
        "01",
        "Matriz de evidências",
        "Cada hipótese mantém cálculo, cronologia, fonte, contraevidência e limitação visíveis.",
    )
    finding_options = ["Todos", *findings["finding_id"].astype(str).tolist()]
    dimensions = ["Todas", *sorted(segments["dimension"].dropna().astype(str).unique())]
    evidence_filter_columns = st.columns(3)
    with evidence_filter_columns[0]:
        evidence_finding = st.selectbox(
            "Hipótese",
            finding_options,
            format_func=lambda value: FINDING_LABELS.get(value, value),
            key="evidence_finding_filter",
        )
    with evidence_filter_columns[1]:
        dimension = st.selectbox("Dimensão", dimensions, key="segment_dimension_filter")
    with evidence_filter_columns[2]:
        chronology = st.selectbox(
            "Cronologia",
            ["strict", "observed"],
            format_func=lambda value: {"strict": "Tratada", "observed": "Observada"}[value],
            key="chronology_filter",
        )
    evidence = (
        findings
        if evidence_finding == "Todos"
        else findings.loc[findings["finding_id"].eq(evidence_finding)]
    )
    visible_segments = (
        segments if dimension == "Todas" else segments.loc[segments["dimension"].eq(dimension)]
    )
    chronology_label = {"strict": "tratada", "observed": "observada"}[chronology]
    st.caption(
        f"Cronologia selecionada: {chronology_label}. Fato = métrica observada; associação = efeito "
        "ajustado; hipótese = explicação ainda não comprovada."
    )
    canonical_tables = {
        "Histórico de churn": monthly_churn,
        "Motivos no horizonte": reason_distribution,
        "Coortes relativas": event_metrics.loc[event_metrics["chronology"].eq(chronology)],
        "Scorecard de mecanismos": mechanism_scorecard,
    }
    selected_table = st.selectbox(
        "Tabela canônica",
        list(canonical_tables),
        key="canonical_evidence_table",
    )
    st.dataframe(
        format_display_frame(canonical_tables[selected_table]),
        width="stretch",
        height=260,
        hide_index=True,
    )
    effect_column = f"{chronology}_effect"
    evidence_columns = [
        column
        for column in (
            "finding_id",
            "adjusted_odds_ratio",
            "ci_low",
            "ci_high",
            effect_column,
            "sensitivity_delta",
            "diagnostic_cutoff",
            "horizon_days",
            "exposure_rule",
            "diagnostic_exposed_accounts",
            "diagnostic_exposed_churns",
            "candidate_coverage",
            "source_tables",
            "confidence",
            "counterevidence",
            "limitation",
        )
        if column in evidence
    ]
    evidence_display = evidence[evidence_columns].replace(
        {"finding_id": FINDING_LABELS, "confidence": ELIGIBILITY_LABELS}
    )
    st.dataframe(
        format_display_frame(
            evidence_display.rename(
                columns={
                    "finding_id": "Hipótese",
                    "adjusted_odds_ratio": "Odds ratio ajustado",
                    "ci_low": "IC inferior",
                    "ci_high": "IC superior",
                    effect_column: "Efeito selecionado",
                    "sensitivity_delta": "Diferença entre cronologias",
                    "diagnostic_cutoff": "Cutoff diagnóstico",
                    "horizon_days": "Horizonte em dias",
                    "exposure_rule": "Regra de exposição",
                    "diagnostic_exposed_accounts": "Contas expostas no diagnóstico",
                    "diagnostic_exposed_churns": "Churns entre expostas",
                    "candidate_coverage": "Cobertura da variável",
                    "source_tables": "Tabelas-fonte",
                    "confidence": "Elegibilidade",
                    "counterevidence": "Contraevidência",
                    "limitation": "Limitação",
                }
            )
        ),
        width="stretch",
        height=300,
        hide_index=True,
    )
    visible_segment_display = visible_segments.head(30).copy()
    if "confidence" not in visible_segment_display:
        visible_segment_display["confidence"] = "inconclusive"
    visible_segment_display["dimension"] = visible_segment_display["dimension"].replace(
        DIMENSION_LABELS
    )
    visible_segment_display["segment"] = visible_segment_display["segment"].replace(SEGMENT_LABELS)
    visible_segment_display["confidence"] = visible_segment_display["confidence"].replace(
        ELIGIBILITY_LABELS
    )
    st.dataframe(
        format_display_frame(
            visible_segment_display.rename(
                columns={
                    "dimension": "Dimensão",
                    "segment": "Segmento",
                    "sample_size": "Contas",
                    "churn_count": "Churns",
                    "churn_rate": "Taxa de churn",
                    "overall_churn_rate": "Taxa geral",
                    "churn_rate_delta": "Diferença para taxa geral",
                    "relative_risk": "Risco relativo",
                    "mrr_lost": "MRR perdido",
                    "mrr_exposed": "MRR exposto",
                    "coverage": "Cobertura",
                    "confidence": "Elegibilidade",
                }
            )
        ),
        width="stretch",
        height=420,
        hide_index=True,
    )

with queue_tab:
    section_heading(
        "01",
        "Contas para validação",
        "Uma watchlist descritiva para investigar sinais — nunca uma autorização automática de contato.",
    )
    is_watchlist = queue.empty
    operational = watchlist.copy() if is_watchlist else queue.copy()
    if is_watchlist:
        st.warning(
            "Lista somente para validação: nenhuma conta está autorizada para intervenção ou "
            "contato automático."
        )
        operational["finding_id"] = "validation-only"
        operational["priority"] = operational["validation_rank"]
    if operational.empty:
        st.info("Nenhuma conta entrou na fila ou na watchlist desta execução.")
    queue_filter_columns = st.columns(4)
    finding_values = sorted(operational["finding_id"].dropna().astype(str).unique())
    with queue_filter_columns[0]:
        finding_filter = st.selectbox(
            "Sinal",
            ["Todos", *finding_values],
            format_func=lambda value: {
                **FINDING_LABELS,
                "validation-only": "Validação descritiva",
            }.get(value, value),
            key="finding_filter",
        )
    with queue_filter_columns[1]:
        if is_watchlist and not operational.empty:
            max_rank = int(operational["priority"].max())
            rank_limit = st.slider("Até a posição", 1, max_rank, min(25, max_rank))
            priority_filter = None
        elif is_watchlist:
            rank_limit = 0
            priority_filter = None
        else:
            priorities = sorted(operational["priority"].dropna().unique())
            priority_filter = st.multiselect("Prioridade", priorities, default=priorities)
    plan_values = sorted(operational["plan_tier"].dropna().astype(str).unique())
    with queue_filter_columns[2]:
        plan_filter = st.multiselect(
            "Plano",
            plan_values,
            default=plan_values,
            format_func=lambda value: SEGMENT_LABELS.get(value, value),
        )
    mrr_values = [
        value for value in ("low", "mid", "high") if value in set(operational["mrr_band"])
    ]
    with queue_filter_columns[3]:
        mrr_filter = st.multiselect(
            "Faixa de MRR",
            mrr_values,
            default=mrr_values,
            format_func=lambda value: MRR_BAND_LABELS.get(value, value),
        )
    filtered = operational.copy()
    if finding_filter != "Todos":
        filtered = filtered.loc[filtered["finding_id"].eq(finding_filter)]
    if is_watchlist:
        filtered = filtered.loc[filtered["priority"].le(rank_limit)]
    elif priority_filter:
        filtered = filtered.loc[filtered["priority"].isin(priority_filter)]
    if plan_filter:
        filtered = filtered.loc[filtered["plan_tier"].isin(plan_filter)]
    if mrr_filter:
        filtered = filtered.loc[filtered["mrr_band"].isin(mrr_filter)]
    if filtered.empty:
        st.info("Nenhuma conta acionável passou os filtros e os gates de evidência.")
    display_filtered = filtered.copy()
    display_filtered["finding_id"] = display_filtered["finding_id"].replace(
        {**FINDING_LABELS, "validation-only": "Validação descritiva"}
    )
    display_filtered["signals"] = display_filtered["signals"].map(
        lambda value: ", ".join(FINDING_LABELS.get(item, item) for item in str(value).split("|"))
    )
    display_filtered["mrr_band"] = display_filtered["mrr_band"].replace(MRR_BAND_LABELS)
    display_filtered["plan_tier"] = display_filtered["plan_tier"].replace(SEGMENT_LABELS)
    display_filtered["status"] = display_filtered["status"].replace(
        {"validation_only": "Somente validação"}
    )
    display_filtered = display_filtered.rename(
        columns={
            "account_id": "Conta",
            "validation_rank": "Ordem de validação",
            "signal_count": "Quantidade de sinais",
            "mrr_exposed_max": "MRR exposto máximo",
            "plan_tier": "Plano",
            "mrr_band": "Faixa de MRR",
            "signals": "Sinais",
            "status": "Uso permitido",
            "finding_id": "Hipótese",
            "priority": "Prioridade",
        }
    )
    st.dataframe(format_display_frame(display_filtered), width="stretch", hide_index=True)
    st.download_button(
        "Baixar fila filtrada (CSV)",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name=(
            "ravenstack-validation-watchlist.csv"
            if is_watchlist
            else "ravenstack-account-queue.csv"
        ),
        mime="text/csv",
    )
    if is_watchlist:
        st.caption("O download preserva os códigos canônicos; esta lista não autoriza contato.")
    else:
        st.caption(
            "`owner` e `status` só devem ser editados depois do download; o app é somente leitura."
        )

with st.expander("Metodologia e limitações"):
    st.write(
        "A decisão usa a cronologia strict; observed mede sensibilidade. Janelas sem cobertura "
        "permanecem nulas. MRR exposto é oportunidade máxima, não receita recuperável. "
        "Associações observacionais não provam causalidade."
    )
