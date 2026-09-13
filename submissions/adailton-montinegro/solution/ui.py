from __future__ import annotations

import json
import math
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


SUBMISSION_ROOT = Path(__file__).resolve().parent.parent
ARTIFACT_DATA_DIR = SUBMISSION_ROOT / "artifacts" / "data"
REPORT_CONTEXT = ARTIFACT_DATA_DIR / "report_context.json"
BUILD_SCRIPT = SUBMISSION_ROOT / "scripts" / "build.py"

EXPORTS = {
    "quality_summary": "quality_summary.csv",
    "quality_issues": "quality_issues.csv",
    "analysis_scope": "analysis_scope.csv",
    "account_snapshot": "account_snapshot.csv",
    "monthly_events": "monthly_events.csv",
    "segment_snapshot": "segment_snapshot.csv",
    "churn_reasons": "churn_reasons.csv",
    "account_triage": "account_triage.csv",
    "metric_catalog": "metric_catalog.csv",
    "pre_event_signals": "pre_event_signals.csv",
    "statistical_tests": "statistical_tests.csv",
}


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        :root { color-scheme:light; --ink:#0f172a; --muted:#64748b; --navy:#10253f; --blue:#0f6cbd;
                --cyan:#13a8a8; --amber:#d97706; --red:#b42318; --paper:#f7f9fc; }
        html, body, [data-testid="stAppViewContainer"], .stApp { background:#ffffff !important; }
        header[data-testid="stHeader"] { height:3.5rem; background:rgba(255,255,255,.98);
            border-bottom:1px solid #e7edf4; }
        .block-container { padding-top: 5rem !important; padding-bottom: 4rem; max-width: 1480px; }
        [data-testid="stSidebar"] { background:#f7f9fc; border-right:1px solid #e3eaf2; }
        [data-testid="stSidebarNav"] { padding-top:.35rem; }
        h1, h2, h3 { color: var(--navy); letter-spacing: -0.02em; }
        [data-testid="stMetric"] { background:#fff; border:1px solid #dbe4ef; border-radius:14px;
            padding:14px 16px; box-shadow:0 8px 24px rgba(15,35,60,.05); }
        .eyebrow { color:#0f6cbd; font-size:.78rem; font-weight:800; letter-spacing:.12em;
            text-transform:uppercase; margin-bottom:.35rem; }
        .hero { background:linear-gradient(120deg,#0b1f35,#153f66); color:#fff; padding:34px 38px;
            border-radius:20px; box-shadow:0 18px 42px rgba(16,37,63,.18); margin-bottom:24px; }
        .hero h1 { color:#fff; margin:0 0 8px 0; font-size:2.45rem; }
        .hero p { color:#d9e8f6; max-width:940px; font-size:1.08rem; margin:0; }
        .truth-card { background:#fff; border:1px solid #dbe4ef; border-top:4px solid #0f6cbd;
            border-radius:14px; padding:18px; min-height:145px; }
        .truth-card h3 { font-size:1rem; margin:0 0 9px 0; }
        .truth-card p { color:#475569; margin:0; }
        .stop-callout { background:#fff4ed; border:2px solid #f04438; border-left:10px solid #b42318;
            border-radius:16px; padding:24px 26px; margin:28px 0 14px; }
        .stop-callout h2 { color:#912018; margin:0 0 9px; }
        .stop-callout p, .stop-callout li { color:#5c211c; }
        .demo-banner { background:#fff8e7; border:1px solid #f4c95d; border-radius:12px;
            color:#754c00; padding:12px 16px; margin:0 0 20px; }
        .tag { display:inline-block; border-radius:999px; padding:3px 9px; margin-right:6px;
            font-size:.72rem; font-weight:800; letter-spacing:.03em; }
        .tag-observado { background:#e8f5ef; color:#176b4d; }
        .tag-derivado { background:#e8f1fb; color:#0f548c; }
        .tag-condicional { background:#fff3da; color:#8a5700; }
        .tag-unavailable { background:#feeceb; color:#912018; }
        .small-note { color:#64748b; font-size:.82rem; }
        .sidebar-brand { padding:.35rem .15rem .8rem; }
        .sidebar-brand strong { color:#10253f; display:block; font-size:1.05rem; }
        .sidebar-brand span { color:#64748b; font-size:.78rem; }
        .sidebar-footer { border-top:1px solid #dbe4ef; margin-top:1.5rem; padding:.9rem .15rem 0;
            color:#64748b; font-size:.75rem; line-height:1.55; }
        .quadrant-card { background:#fff; border:1px solid #dbe4ef; border-radius:12px;
            padding:14px 16px; min-height:126px; }
        .quadrant-card strong { color:#10253f; display:block; margin-bottom:5px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def sidebar_header() -> None:
    st.sidebar.markdown(
        '<div class="sidebar-brand"><strong>RavenStack</strong><span>Diagnóstico de churn · Challenge 001</span></div>',
        unsafe_allow_html=True,
    )


def sidebar_footer() -> None:
    updated_at = "data não disponível"
    if REPORT_CONTEXT.exists():
        context = json.loads(REPORT_CONTEXT.read_text(encoding="utf-8"))
        generated_at = context.get("generated_at")
        if generated_at:
            updated_at = datetime.fromisoformat(generated_at.replace("Z", "+00:00")).strftime("%d/%m/%Y")
    st.sidebar.markdown(
        f'<div class="sidebar-footer"><strong>Adailton Montinegro</strong><br>'
        f'Atualizado em {updated_at}<br>Dados RavenStack · Kaggle v1</div>',
        unsafe_allow_html=True,
    )


def page_header(eyebrow: str, title: str, description: str) -> None:
    inject_theme()
    st.markdown(f'<div class="eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(description)


def hero(title: str, description: str) -> None:
    inject_theme()
    st.markdown(
        f'<section class="hero"><div class="eyebrow" style="color:#69d4d4">AI MASTER · CHALLENGE 001</div>'
        f'<h1>{title}</h1><p>{description}</p></section>',
        unsafe_allow_html=True,
    )


def demonstrative_banner() -> None:
    st.markdown(
        '<div class="demo-banner"><strong>A recomendação profissional é parar.</strong> Esta seção continua '
        'apenas como demonstração estatística sobre a parcela recuperável. Ela não substitui a correção do '
        'sistema de eventos nem autoriza decisões automáticas sobre clientes.</div>',
        unsafe_allow_html=True,
    )
    if not st.session_state.get("quality_gate_ack", False):
        accepted = st.checkbox(
            "Reconheço que esta continuação é demonstrativa e não deve orientar ações automáticas.",
            key="quality_gate_ack_direct",
        )
        if accepted:
            st.session_state["quality_gate_ack"] = True
            st.rerun()
        st.stop()


def stop_callout() -> None:
    st.markdown(
        """
        <section class="stop-callout">
          <div class="eyebrow" style="color:#b42318">GATE PROFISSIONAL DE DECISÃO</div>
          <h2>Pare a análise aqui.</h2>
          <p><strong>A recomendação correta para uma empresa real é interromper o diagnóstico de churn</strong>
          e concentrar os esforços em localizar e corrigir o sistema de logs, os contratos de eventos e a
          reconstrução do ciclo de vida de contas e assinaturas. Continuar agora cria precisão aparente sobre
          fatos incompatíveis.</p>
          <p>Se a liderança precisar de evidência em curto prazo, a investigação deve ocorrer por fora da
          telemetria contaminada:</p>
          <ul>
            <li>pesquisa de satisfação com clientes ativos, churnados e reativados;</li>
            <li>coleta estruturada de sugestões, fricções e melhorias solicitadas;</li>
            <li>entrevistas e revisão manual das contas de maior impacto;</li>
            <li>avaliação interna conjunta com Customer Success e Suporte.</li>
          </ul>
          <p><strong>As páginas seguintes existem por exigência demonstrativa do desafio</strong>, com cobertura,
          premissas e incerteza expostas.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.warning(
        "As páginas executiva, analítica, de triagem e de plano de ação só serão liberadas após você "
        "marcar o reconhecimento abaixo."
    )
    accepted = st.checkbox(
        "Reconheço o gate e quero abrir a análise demonstrativa da parcela recuperável.",
        key="quality_gate_ack_on_quality",
        value=st.session_state.get("quality_gate_ack", False),
    )
    st.session_state["quality_gate_ack"] = accepted


def artifacts_ready() -> bool:
    return REPORT_CONTEXT.exists() and all((ARTIFACT_DATA_DIR / filename).exists() for filename in EXPORTS.values())


def require_artifacts() -> None:
    if artifacts_ready():
        return
    st.error("Os artefatos Gold ainda não foram construídos neste ambiente.")
    st.code("python scripts/build.py", language="bash")
    if st.button("Baixar, validar e construir agora", type="primary"):
        with st.spinner("Construindo raw, stage, gold e exports..."):
            result = subprocess.run(
                [sys.executable, str(BUILD_SCRIPT)],
                cwd=SUBMISSION_ROOT,
                capture_output=True,
                text=True,
            )
        if result.returncode != 0:
            st.error(result.stderr or result.stdout)
        else:
            st.cache_data.clear()
            st.success("Pipeline concluído.")
            st.rerun()
    st.stop()


@st.cache_data(show_spinner=False)
def load_table(name: str) -> pd.DataFrame:
    require_artifacts()
    return pd.read_csv(ARTIFACT_DATA_DIR / EXPORTS[name])


@st.cache_data(show_spinner=False)
def load_context() -> dict:
    require_artifacts()
    return json.loads(REPORT_CONTEXT.read_text(encoding="utf-8"))


def fmt_int(value: float | int) -> str:
    return f"{int(round(value)):,}".replace(",", ".")


def fmt_pct(value: float | int, decimals: int = 1) -> str:
    return f"{float(value):.{decimals}f}%".replace(".", ",")


def fmt_money(value: float | int | None, compact: bool = False) -> str:
    if value is None or pd.isna(value):
        return "Indisponível"
    value = float(value)
    if not math.isfinite(value):
        return "Indisponível"
    if compact and abs(value) >= 1_000_000:
        return f"US$ {value / 1_000_000:.2f} mi".replace(".", ",")
    if compact and abs(value) >= 1_000:
        return f"US$ {value / 1_000:.1f} mil".replace(".", ",")
    return (f"US$ {value:,.0f}").replace(",", ".")


def metric_note(state: str, universe: str) -> None:
    allowed = {"observado", "derivado", "condicional", "indisponível"}
    normalized = state.strip().lower()
    if normalized not in allowed:
        raise ValueError(f"Estado de métrica inválido: {state}")
    css = "unavailable" if normalized == "indisponível" else normalized
    st.markdown(
        f'<span class="tag tag-{css}">{state}</span><span class="small-note">{universe}</span>',
        unsafe_allow_html=True,
    )


def as_bool(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes", "sim"})


def footer() -> None:
    st.markdown("---")
    st.caption(
        "Fonte: RavenStack Synthetic SaaS Dataset · River @ Rivalytics · "
        "Métricas reconstruídas em DuckDB · valores financeiros são proxies quando indicado."
    )
