"""Offline UI with fail-closed artifacts and confirmed audit writes."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import sqlite3
from contextlib import closing
from dataclasses import asdict, dataclass
from html import escape
from pathlib import Path
from uuid import uuid4

import joblib
import pandas as pd
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

from support_copilot.analytics import (
    OperationalSummary,
    ScenarioAssumptions,
    scenario_projection,
)
from support_copilot.data import IT_TAXONOMY, Manifest, content_hash, sanitize_text
from support_copilot.decision import (
    RoutingPolicy,
    base_policy,
    decide_route,
    derive_signals,
    policy_hash,
    priority_score,
)
from support_copilot.modeling import ModelTrainingResult, Prediction
from support_copilot.retrieval import (
    RetrievalPolicy,
    TicketRetriever,
    load_retrieval_policy,
)
from support_copilot.store import (
    DecisionEvent,
    export_decisions_csv,
    initialize_store,
    list_decisions,
    record_decision,
)


@dataclass(frozen=True)
class FeatureState:
    status: str
    value: object | None
    path: str
    reason: str | None = None
    correction: str = "make reproduce"


@dataclass(frozen=True)
class ArtifactBundle:
    manifest: dict
    features: dict[str, FeatureState]
    version: str
    root: Path

    def get(self, key: str) -> FeatureState:
        return self.features.get(key, FeatureState(
            "missing", None, "manifest.json", "artifact_not_registered"))


def apply_design_system() -> None:
    """Install the product's single visual language without changing its behavior."""
    st.markdown(
        """
        <style>
        :root {
            --paper: #f3f0e7;
            --paper-strong: #fffdf7;
            --ink: #18201c;
            --muted: #66716a;
            --line: #d6d8cc;
            --night: #101814;
            --night-soft: #1a2720;
            --signal: #d8ff46;
            --signal-ink: #172000;
            --alert: #ee6847;
            --info: #4f7562;
            --shadow: 0 18px 50px rgba(23, 32, 27, .08);
        }

        html, body, [class*="css"] {
            font-family: "Avenir Next", "Segoe UI", sans-serif;
            color: var(--ink);
        }

        .stApp {
            background:
                radial-gradient(circle at 85% 8%, rgba(216,255,70,.15), transparent 25rem),
                linear-gradient(rgba(24,32,28,.025) 1px, transparent 1px),
                var(--paper);
            background-size: auto, 100% 32px, auto;
        }

        [data-testid="stAppViewContainer"] > .main {
            background: transparent;
        }

        .block-container {
            max-width: 1500px;
            padding: 3.2rem 3.4rem 5rem;
        }

        [data-testid="stSidebar"] {
            background:
                radial-gradient(circle at 15% 0%, rgba(216,255,70,.13), transparent 18rem),
                var(--night);
            border-right: 1px solid rgba(255,255,255,.08);
        }

        [data-testid="stSidebar"] * { color: #edf2eb; }
        [data-testid="stSidebarNav"] { padding-top: 1.8rem; }
        [data-testid="stSidebarNav"] li { margin: .35rem .7rem; }
        [data-testid="stSidebarNav"] a {
            min-height: 2.9rem;
            border-radius: .8rem;
            padding-inline: .9rem;
            transition: background .18s ease, transform .18s ease;
        }
        [data-testid="stSidebarNav"] a:hover {
            background: rgba(255,255,255,.08);
            transform: translateX(3px);
        }
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background: var(--signal);
        }
        [data-testid="stSidebarNav"] a[aria-current="page"] * {
            color: var(--signal-ink) !important;
            font-weight: 700;
        }

        h1, h2, h3 {
            font-family: Iowan Old Style, Palatino Linotype, Georgia, serif;
            color: var(--ink);
            letter-spacing: -.035em;
        }
        h1 { font-size: clamp(2.7rem, 5vw, 5.2rem) !important; line-height: .96 !important; }
        h2 { margin-top: 2.3rem !important; }
        h3 { margin-top: 1.4rem !important; }
        [data-testid="stHeadingWithActionElements"] > h1 {
            position: absolute !important;
            width: 1px !important;
            height: 1px !important;
            padding: 0 !important;
            margin: -1px !important;
            overflow: hidden !important;
            clip: rect(0, 0, 0, 0) !important;
            white-space: nowrap !important;
            border: 0 !important;
        }

        .ops-hero {
            position: relative;
            overflow: hidden;
            min-height: 220px;
            margin: -.4rem 0 2rem;
            padding: 2.35rem 2.6rem 2.2rem;
            color: #f7f7ef;
            background: var(--night);
            border: 1px solid rgba(255,255,255,.09);
            border-radius: 1.3rem;
            box-shadow: var(--shadow);
        }
        .ops-hero::after {
            content: "";
            position: absolute;
            width: 330px;
            height: 330px;
            right: -85px;
            top: -175px;
            border: 55px solid var(--signal);
            border-radius: 50%;
            opacity: .92;
        }
        .ops-hero__eyebrow {
            position: relative;
            z-index: 1;
            display: flex;
            align-items: center;
            gap: .65rem;
            margin-bottom: 1.3rem;
            color: var(--signal);
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            font-size: .72rem;
            font-weight: 800;
            letter-spacing: .13em;
            text-transform: uppercase;
        }
        .ops-hero__eyebrow::before {
            content: "";
            width: 2.2rem;
            height: 2px;
            background: currentColor;
        }
        .ops-hero__title {
            position: relative;
            z-index: 1;
            max-width: 900px;
            margin: 0 0 .9rem !important;
            color: #fffdf7 !important;
            font-family: Iowan Old Style, Palatino Linotype, Georgia, serif;
            font-size: clamp(2.7rem, 5vw, 5.2rem);
            font-weight: 700;
            line-height: .96;
            letter-spacing: -.035em;
        }
        .ops-hero p {
            position: relative;
            z-index: 1;
            max-width: 760px;
            margin: 0;
            color: #bcc8bf;
            font-size: 1.03rem;
            line-height: 1.6;
        }

        .ops-section-label {
            margin: 2.2rem 0 .8rem;
            color: var(--info);
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            font-size: .71rem;
            font-weight: 800;
            letter-spacing: .13em;
            text-transform: uppercase;
        }

        .ops-stats {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: .85rem;
            margin: 0 0 1.7rem;
        }
        .ops-stat {
            min-height: 112px;
            padding: 1.15rem 1.25rem;
            background: rgba(255,253,247,.88);
            border: 1px solid var(--line);
            border-radius: 1rem;
            box-shadow: 0 8px 28px rgba(23,32,27,.045);
        }
        .ops-stat__value {
            color: var(--ink);
            font-family: Iowan Old Style, Georgia, serif;
            font-size: 2.25rem;
            font-weight: 700;
            line-height: 1;
        }
        .ops-stat__label {
            margin-top: .65rem;
            color: var(--muted);
            font-size: .73rem;
            font-weight: 750;
            letter-spacing: .075em;
            text-transform: uppercase;
        }
        .ops-stat--signal { background: var(--signal); border-color: #c4e938; }
        .ops-stat--alert { border-top: 4px solid var(--alert); }

        .ops-callout {
            margin: .8rem 0 1.2rem;
            padding: 1rem 1.15rem;
            background: #e9eee9;
            border-left: 4px solid var(--info);
            border-radius: 0 .75rem .75rem 0;
            color: #34423a;
            line-height: 1.55;
        }
        .ops-callout strong { color: var(--ink); }

        .ops-answer-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1rem;
            margin: 0 0 1.5rem;
        }
        .ops-answer {
            min-height: 250px;
            padding: 1.35rem 1.4rem;
            background: rgba(255,253,247,.9);
            border: 1px solid var(--line);
            border-radius: 1rem;
            box-shadow: 0 10px 32px rgba(23,32,27,.05);
        }
        .ops-answer__index {
            color: var(--info);
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            font-size: .7rem;
            font-weight: 800;
            letter-spacing: .12em;
            text-transform: uppercase;
        }
        .ops-answer h2 {
            margin: .75rem 0 .7rem !important;
            font-size: 1.65rem;
        }
        .ops-answer__number {
            margin: .2rem 0 .7rem;
            color: var(--ink);
            font-family: Iowan Old Style, Georgia, serif;
            font-size: 2.45rem;
            font-weight: 700;
            line-height: 1;
        }
        .ops-answer p { margin: 0; color: var(--muted); line-height: 1.55; }
        .ops-answer--signal { border-top: 4px solid var(--signal); }
        .ops-answer--alert { border-top: 4px solid var(--alert); }

        .ops-proof-chain {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: .7rem;
            margin: .8rem 0 1.2rem;
        }
        .ops-proof {
            padding: .9rem 1rem;
            background: #e9eee9;
            border-radius: .75rem;
            color: #34423a;
            font-size: .83rem;
            font-weight: 700;
        }
        .ops-proof::before { content: "✓"; margin-right: .45rem; color: var(--info); }

        [data-testid="stMetric"] {
            min-height: 120px;
            padding: 1.1rem 1.25rem;
            background: rgba(255,253,247,.9);
            border: 1px solid var(--line);
            border-radius: 1rem;
            box-shadow: 0 8px 28px rgba(23,32,27,.045);
        }
        [data-testid="stMetricValue"] {
            font-family: Iowan Old Style, Georgia, serif;
            color: var(--ink);
        }

        [data-testid="stDataFrame"], [data-testid="stForm"],
        [data-testid="stExpander"], [data-testid="stVerticalBlockBorderWrapper"] {
            overflow: hidden;
            background: rgba(255,253,247,.78);
            border-color: var(--line) !important;
            border-radius: 1rem !important;
        }
        [data-testid="stDataFrame"] { box-shadow: 0 10px 35px rgba(23,32,27,.05); }

        [data-baseweb="select"] > div, textarea, input {
            background: var(--paper-strong) !important;
            border-color: #c5cbbf !important;
            border-radius: .72rem !important;
        }
        textarea:focus, input:focus, [data-baseweb="select"] > div:focus-within {
            box-shadow: 0 0 0 3px rgba(79,117,98,.2) !important;
            border-color: var(--info) !important;
        }

        .stButton > button, .stDownloadButton > button {
            min-height: 2.7rem;
            padding-inline: 1.15rem;
            color: #f7f7ef;
            background: var(--night);
            border: 1px solid var(--night);
            border-radius: .72rem;
            font-weight: 750;
            transition: transform .16s ease, box-shadow .16s ease, background .16s ease;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            color: var(--signal-ink);
            background: var(--signal);
            border-color: var(--signal);
            transform: translateY(-2px);
            box-shadow: 0 9px 20px rgba(23,32,27,.14);
        }
        .stButton > button:focus-visible, .stDownloadButton > button:focus-visible {
            outline: 3px solid var(--alert);
            outline-offset: 2px;
        }
        .stButton > button:disabled {
            color: #89918c;
            background: #e3e5df;
            border-color: #d3d7cf;
        }

        [data-testid="stAlert"] {
            border-radius: .85rem;
            border: 1px solid rgba(24,32,28,.1);
        }

        @keyframes ops-rise {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .ops-hero, .ops-stats, [data-testid="stDataFrame"] {
            animation: ops-rise .42s ease both;
        }
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after { animation: none !important; transition: none !important; }
        }
        @media (max-width: 800px) {
            .block-container { padding: 1.4rem 1rem 3rem; }
            .ops-hero { min-height: 200px; padding: 1.7rem 1.35rem; }
            .ops-hero::after { width: 200px; height: 200px; right: -95px; top: -105px; }
            .ops-stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .ops-answer-grid, .ops-proof-chain { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _page_intro(eyebrow: str, title: str, description: str) -> None:
    st.markdown(
        f"""
        <section class="ops-hero">
          <div class="ops-hero__eyebrow">{escape(eyebrow)}</div>
          <div class="ops-hero__title" role="heading" aria-level="1">{escape(title)}</div>
          <p>{escape(description)}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _section_label(text: str) -> None:
    st.markdown(f'<div class="ops-section-label">{escape(text)}</div>', unsafe_allow_html=True)


def _stat_strip(items: list[tuple[str, str, str]]) -> None:
    cards = "".join(
        f'<div class="ops-stat {escape(tone)}"><div class="ops-stat__value">'
        f'{escape(value)}</div><div class="ops-stat__label">{escape(label)}</div></div>'
        for value, label, tone in items
    )
    st.markdown(f'<div class="ops-stats">{cards}</div>', unsafe_allow_html=True)


def _value_dict(bundle: ArtifactBundle, key: str) -> dict:
    state = bundle.get(key)
    return state.value if state.status == "ready" and isinstance(state.value, dict) else {}


def automation_evidence(metrics: dict, risk_policy: dict) -> pd.DataFrame:
    """Summarize frozen-test evidence at each domain's locked operating policy."""
    rows = []
    domains = metrics.get("domains", {}) if isinstance(metrics.get("domains"), dict) else {}
    for domain, label in (("customer", "Customer"), ("it", "IT")):
        measured = domains.get(domain, {}) if isinstance(domains.get(domain), dict) else {}
        policy = risk_policy.get(domain, {}) if isinstance(risk_policy.get(domain), dict) else {}
        threshold = policy.get("threshold")
        point = next((row for row in measured.get("risk_coverage", [])
                      if threshold is not None and row.get("threshold") == threshold), {})
        rows.append({
            "Domínio": label,
            "Teste congelado (n)": (measured.get("denominators", {}).get("n_total")
                                    or point.get("n_total")),
            "Macro-F1": measured.get("macro_f1"),
            "ECE": measured.get("ece"),
            "Limiar travado": threshold,
            "Cobertura no teste": point.get("coverage", 0.0),
            "Risco seletivo": point.get("selective_risk"),
            "Decisão atual": ("Bloqueada: 0% elegível" if domain == "customer"
                              else "Somente shadow + revisão humana"),
        })
    return pd.DataFrame(rows)


def render_director_brief(bundle=None) -> None:
    """Answer the sponsor's three questions before exposing implementation detail."""
    bundle = _bundle(bundle)
    st.title("Resposta ao Diretor")
    _page_intro(
        "Decisão executiva · evidência antes de automação",
        "Onde agir, o que automatizar e o que já funciona",
        "A operação tem uma oportunidade mensurável, mas os dados sustentam automação "
        "seletiva — não comunicação externa autônoma.",
    )
    summary = _value_dict(bundle, "analytics.operational_summary")
    metrics = _value_dict(bundle, "models.metrics")
    domains = metrics.get("domains", {}) if isinstance(metrics.get("domains"), dict) else {}
    customer = domains.get("customer", {}) if isinstance(domains.get("customer"), dict) else {}
    it = domains.get("it", {}) if isinstance(domains.get("it"), dict) else {}
    risk_policy = _value_dict(bundle, "risk_policy")
    source_rows = int(summary.get("analysis_rows") or summary.get("development_rows") or 0)
    valid_intervals = int(summary.get("valid_intervals") or 0)
    observed_excess = summary.get("observed_excess_hours")
    customer_curve = customer.get("risk_coverage", [])
    customer_safe = max(
        (float(row.get("coverage") or 0) for row in customer_curve
         if row.get("selective_risk") is not None
         and float(row["selective_risk"]) <= 0.10),
        default=0.0,
    )
    it_f1 = it.get("macro_f1")

    _stat_strip([
        (_number(observed_excess) + " h" if observed_excess is not None else "—",
         "Excesso histórico observado", "ops-stat--alert"),
        (f"{valid_intervals}/{source_rows}" if source_rows else "—",
         "Intervalos utilizáveis", ""),
        (_number(customer_safe, percent=True), "Customer seguro hoje", "ops-stat--alert"),
        (_number(it_f1, percent=True) if it_f1 is not None else "—",
         "Macro-F1 IT no teste", "ops-stat--signal"),
    ])

    _section_label("01 · As três respostas")
    answers = (
        (
            "01 · Onde perdemos tempo?", "4.047,83 h", "ops-answer--alert",
            "Excesso histórico acima das medianas de 20 grupos. Refund request + High "
            "lidera com 274,17 h; é oportunidade observada, não economia realizada.",
        ),
        (
            "02 · O que automatizar?", "0% Customer", "ops-answer--alert",
            "Hoje, nenhum ticket Customer cruza um limiar com risco seletivo aceitável. "
            "Automatize primeiro triagem assistida; mantenha decisão e comunicação humanas.",
        ),
        (
            "03 · Funciona?", "83,51% F1 IT", "ops-answer--signal",
            "O domínio IT foi testado em 5.301 casos. A aplicação também demonstra fila, "
            "gate de risco, decisão auditável e export sem enviar mensagens externas.",
        ),
    )
    cards = "".join(
        '<article class="ops-answer ' + tone + '">'
        f'<div class="ops-answer__index">{escape(label)}</div>'
        f'<div class="ops-answer__number">{escape(number)}</div>'
        f'<p>{escape(body)}</p></article>'
        for label, number, tone, body in answers
    )
    st.markdown(f'<div class="ops-answer-grid">{cards}</div>', unsafe_allow_html=True)

    _section_label("02 · Recomendação executiva")
    st.markdown(
        '<div class="ops-callout"><strong>Decisão agora:</strong> operar como copiloto, '
        'atacar Refund request + High e executar um piloto shadow antes de liberar qualquer '
        'roteamento Customer. O resultado correto hoje é automação Customer bloqueada.</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Precisão Customer medida: macro-F1 "
        f"{_number(customer.get('macro_f1'))}; calibração ECE "
        f"{_number(customer.get('ece'))}. A confiança baixa impede cobertura segura."
    )

    _section_label("03 · Limite medido da automação")
    evidence = automation_evidence(metrics, risk_policy)
    st.dataframe(
        evidence.style.format({
            "Macro-F1": "{:.2%}", "ECE": "{:.2%}", "Limiar travado": "{:.2f}",
            "Cobertura no teste": "{:.2%}", "Risco seletivo": "{:.2%}",
        }, na_rep="—"),
        hide_index=True,
        width="stretch",
    )
    it_evidence = evidence.loc[evidence["Domínio"].eq("IT")]
    if not it_evidence.empty and pd.notna(it_evidence.iloc[0]["Risco seletivo"]):
        coverage = float(it_evidence.iloc[0]["Cobertura no teste"])
        risk = float(it_evidence.iloc[0]["Risco seletivo"])
        threshold = float(it_evidence.iloc[0]["Limiar travado"])
        st.warning(
            f"No teste final, IT cobriu {coverage:.2%} no limiar travado de "
            f"{threshold:.2f}, com erro seletivo de {risk:.2%} — acima do teto de 10%. "
            "Portanto, IT também permanece em shadow; o resultado não autoriza "
            "automação autônoma em produção."
        )
    st.caption(
        "Permitido agora: priorização, fila, classificação assistida e auditoria humana. "
        "Bloqueado: resposta externa, alteração de conta, reembolso e roteamento Customer autônomo."
    )

    _section_label("04 · Prova operacional")
    proof = (
        ("analytics.operational_summary", "Diagnóstico reproduzível"),
        ("models.metrics", "Teste final congelado"),
        ("queue.customer", "Fila e gate em execução"),
        ("retrieval.metrics", "Limite de respostas auditado"),
    )
    ready = [label for key, label in proof if bundle.get(key).status == "ready"]
    st.markdown(
        '<div class="ops-proof-chain">'
        + "".join(f'<div class="ops-proof">{escape(label)}</div>' for label in ready)
        + "</div>",
        unsafe_allow_html=True,
    )
    if len(ready) != len(proof):
        st.warning("Parte da cadeia de evidências está indisponível; execute make reproduce.")
    st.caption(
        "A prova mostra decisão assistida e auditável. Não prova economia realizada, "
        "integração com helpdesk nem efeito causal sobre satisfação."
    )

    _section_label("05 · Próximo experimento")
    st.markdown("**Piloto shadow de duas semanas, sem envio automático.**")
    st.write(
        "Processar no mínimo 1.000 tickets, estratificados por canal, prioridade e tipo. "
        "Registrar o tempo manual atual antes do piloto e comparar cada sugestão da IA "
        "com a decisão humana, sem alterar o helpdesk nem responder ao cliente."
    )
    st.markdown(
        "**Go/no-go — todos obrigatórios:** macro-F1 ≥ 75%; recall por classe ≥ 65%; "
        "ECE ≤ 5%; risco seletivo ≤ 10% com cobertura ≥ 20%; zero escape de PII, ação "
        "sensível ou ticket crítico. **Impacto:** reduzir em ≥ 20% o tempo mediano de "
        "triagem. Se um critério falhar, manter revisão humana e repetir o piloto."
    )
    with st.expander("Rastreabilidade técnica"):
        st.json({
            "evidence_kind": {
                "time_loss": "historical_observed",
                "model_quality": "frozen_test_measured",
                "impact": "projected_only",
            },
            "customer": customer,
            "it": it,
            "operational_summary": summary,
        })


def logical_payload(value):
    """Logical fitted state is independent of pickle serialization metadata."""
    def vectorizer_state(vectorizer):
        return {"vocabulary": vectorizer.get_feature_names_out().tolist(),
                "idf": vectorizer.idf_.tolist()} if vectorizer is not None else None

    if isinstance(value, ModelTrainingResult):
        model = value.model
        fitted = None
        if model is not None:
            classifier = model.pipeline.named_steps["classifier"]
            fitted = {"vectorizer": vectorizer_state(model.pipeline.named_steps["tfidf"]),
                      "classifier": {key: getattr(classifier, key).tolist() for key in (
                          "classes_", "coef_", "intercept_", "class_log_prior_",
                          "feature_log_prob_", "class_count_", "feature_count_")
                          if hasattr(classifier, key)},
                      "sigmoids": [[{"a": float(item.a_), "b": float(item.b_)}
                                    for item in calibrated.calibrators]
                                   for calibrated in model.calibrator.calibrated_classifiers_]}
        return {"status": value.status, "selection": asdict(value.selection),
                "policy": asdict(value.policy), "development": value.development,
                "configuration_sha256": value.configuration_sha256,
                "reason_codes": value.reason_codes, "fitted_state": fitted}
    if isinstance(value, TicketRetriever):
        return {"records": value.records, "index_version": value.index_version,
                "provenance": value.provenance, "partitions": value.partitions,
                "fitted_state": {"vectorizer": vectorizer_state(value.vectorizer),
                                 "matrix": {"shape": value.matrix.shape,
                                            "data": value.matrix.data.tolist(),
                                            "indices": value.matrix.indices.tolist(),
                                            "indptr": value.matrix.indptr.tolist()}
                                 if value.matrix is not None else None}}
    return value


def current_environment():
    """Fingerprint only executable/configuration inputs, never runtime or source data."""
    solution = Path(__file__).resolve().parents[2]
    files = sorted([*solution.joinpath("src").rglob("*.py"),
                    *solution.joinpath("scripts").rglob("*.py"),
                    *solution.joinpath("pages").glob("*.py"), solution / "app.py",
                    solution / "configuration.json", solution / "requirements.lock",
                    solution / "pyproject.toml", solution / "Makefile"])
    configuration = json.loads((solution / "configuration.json").read_text())
    from support_copilot.data import (
        ANALYTICS_SCHEMA_VERSION,
        GROUPING_VERSION,
        SANITIZER_VERSION,
    )

    configuration.update(
        sanitizer=SANITIZER_VERSION,
        analytics_schema=ANALYTICS_SCHEMA_VERSION,
        grouping=GROUPING_VERSION,
        mode="development_then_locked_test",
        protocol=1,
    )
    return {
        "configuration_sha256": content_hash(configuration),
        "lock_sha256": hashlib.sha256((solution / "requirements.lock").read_bytes()).hexdigest(),
        "code": content_hash({str(path.relative_to(solution)): hashlib.sha256(
            path.read_bytes()).hexdigest() for path in files}),
    }


def read_artifact(root: Path, manifest: dict, key: str):
    """Shared CLI/UI boundary. Validate every dependency before any deserialization."""
    environment = current_environment()
    if (manifest.get("schema_version") != 1
            or any(manifest.get(field) != environment[field] for field in (
                "configuration_sha256", "lock_sha256"))
            or manifest.get("code_revision", "").split("+code.")[-1] != environment["code"]):
        raise ValueError("artifact_manifest_incompatible_or_stale")
    root = root.resolve()
    checked = {}

    def validate(name, visiting):
        if name in checked:
            return checked[name]
        if name in visiting:
            raise ValueError("artifact_dependency_cycle")
        entry = manifest["artifacts"].get(name, {})
        if (entry.get("status") != "ready" or entry.get("schema_version") != 1
                or not isinstance(entry.get("dependencies"), list)):
            raise ValueError("artifact_schema_or_state_incompatible")
        relative = Path(entry["path"])
        path = (root / relative).resolve()
        if (relative.is_absolute() or ".." in relative.parts or not path.is_relative_to(root)
                or path.name == "manifest.json"):
            raise ValueError("artifact_path_outside_root")
        for dependency in entry["dependencies"]:
            if dependency.startswith(("sources.", "splits.")):
                group, domain = dependency.split(".", 1)
                if domain != entry.get("domain") or domain not in manifest[group]:
                    raise ValueError("artifact_domain_dependency_mismatch")
            else:
                validate(dependency, visiting | {name})
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != entry.get("sha256"):
            raise ValueError("artifact_hash_mismatch")
        kind = entry["type"]
        if kind in {"domain-model", "retriever"}:
            expected = manifest["runtime"]["dependencies"]
            if (manifest["runtime"].get("python", "").split(".")[:2]
                    != platform.python_version().split(".")[:2]
                    or any(expected.get(package) != importlib.metadata.version(package)
                           for package in ("scikit-learn", "joblib", "pandas", "numpy", "scipy"))):
                raise ValueError("artifact_runtime_incompatible")
        elif kind not in {"csv-report", "review-template", "json", "sanitized-frame",
                          "operational-summary", "satisfaction-model"}:
            raise ValueError("artifact_type_incompatible")
        checked[name] = path, payload, kind
        return checked[name]

    path, payload, kind = validate(key, set())
    if kind in {"domain-model", "retriever"}:
        # Load the verified bytes, not the path: a concurrent replacement cannot swap the payload.
        import io
        return joblib.load(io.BytesIO(payload))
    if kind in {"csv-report", "review-template"}:
        import io
        return json.loads(pd.read_csv(io.BytesIO(payload), keep_default_na=kind == "csv-report")
                          .to_json(orient="records"))
    return json.loads(payload)


def load_artifacts(root: Path) -> ArtifactBundle:
    """Check paths, dependencies and hashes before joblib; no cross-generation cache."""
    root = root.resolve()
    manifest_path = root / "manifest.json"
    try:
        if manifest_path.is_symlink():
            raise ValueError("manifest_symlink")
        raw = manifest_path.read_bytes()
        manifest = json.loads(raw)
        if (not isinstance(manifest, dict) or set(manifest) != set(Manifest.__required_keys__)
                or manifest["schema_version"] != 1):
            raise ValueError("manifest_schema_incompatible")
        entries = manifest["artifacts"]
        if not isinstance(entries, dict):
            raise ValueError("manifest_entries_incompatible")
    except (OSError, ValueError, TypeError):
        state = FeatureState("missing" if not manifest_path.exists() else "incompatible",
                             None, "manifest.json", "manifest_missing_or_incompatible")
        return ArtifactBundle({}, {key: state for key in (
            "queue.customer", "models.customer", "models.it", "analytics.operational_summary",
            "analytics.satisfaction_model", "manifest")}, "unavailable", root)
    environment = current_environment()
    stale = (any(manifest.get(key) != environment[key] for key in (
        "configuration_sha256", "lock_sha256"))
        or manifest.get("code_revision", "").split("+code.")[-1] != environment["code"])
    states, visiting = {}, set()

    def load(key):
        if key in states:
            return states[key]
        entry = entries.get(key)
        path = "manifest.json"
        status, reason = "incompatible", "artifact_schema_incompatible"
        try:
            if stale:
                status, reason = "stale", "code_configuration_or_lock_changed"
                raise ValueError(reason)
            if key in visiting:
                raise ValueError("artifact_dependency_cycle")
            visiting.add(key)
            if not isinstance(entry, dict) or entry.get("schema_version") != 1:
                raise ValueError(reason)
            if entry.get("status") == "unavailable":
                status, reason = "missing", entry.get("reason") or "artifact_unavailable"
                raise ValueError(reason)
            if entry.get("status") != "ready" or not isinstance(entry.get("dependencies"), list):
                raise ValueError(reason)
            relative = Path(entry["path"])
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("artifact_path_outside_root")
            path = relative.as_posix()
            target = (root / relative).resolve()
            if not target.is_relative_to(root) or target == manifest_path:
                raise ValueError("artifact_path_outside_root")
            for dependency in entry["dependencies"]:
                if dependency.startswith(("sources.", "splits.")):
                    group, domain = dependency.split(".", 1)
                    if domain != entry.get("domain") or domain not in manifest[group]:
                        raise ValueError("artifact_domain_dependency_mismatch")
                elif load(dependency).status != "ready":
                    status, reason = "stale", f"dependency_unavailable:{dependency}"
                    raise ValueError(reason)
            if not target.is_file():
                status, reason = "missing", "artifact_file_missing"
                raise ValueError(reason)
            kind = entry.get("type")
            try:
                value = read_artifact(root, manifest, key)
            except ValueError as error:
                reason = str(error)
                status = "corrupt" if "hash" in reason else "incompatible"
                raise
            if kind in {"domain-model", "retriever"}:
                if kind == "domain-model":
                    domain = entry.get("domain")
                    if (not isinstance(value, ModelTrainingResult) or value.model is None
                            or value.model.domain != domain or value.policy.domain != domain
                            or value.model.model_version != manifest["models"][domain]
                            ["model_version"]
                            or value.policy.configuration_sha256 != policy_hash(value.policy)):
                        raise ValueError("artifact_model_incompatible")
                elif not isinstance(value, TicketRetriever):
                    raise ValueError("artifact_retriever_incompatible")
            if content_hash(logical_payload(value)) != entry.get("logical_sha256"):
                status, reason = "corrupt", "artifact_logical_hash_mismatch"
                raise ValueError(reason)
            if key.startswith("policies."):
                policy = RoutingPolicy(**value)
                if (policy.domain != entry["domain"] or not policy.locked
                        or policy.configuration_sha256 != policy_hash(policy)
                        or policy.configuration_sha256 != manifest["models"][policy.domain]
                        ["configuration_lock_sha256"]):
                    status, reason = "stale", "policy_version_mismatch"
                    raise ValueError(reason)
            if key == "retrieval.customer" and value.index_version != manifest["retrieval"][
                    "index_version"]:
                status, reason = "stale", "index_version_mismatch"
                raise ValueError(reason)
            if key == "retrieval.policy":
                actual = load_retrieval_policy(load("retrieval.customer").value, root)
                if asdict(actual) != value:
                    status, reason = "stale", "retrieval_review_changed"
                    raise ValueError(reason)
            if key == "queue.customer":
                if (not isinstance(value, list) or any(
                        not isinstance(row, dict) or not isinstance(row.get("text"), str)
                        or not str(row.get("ticket_id", "")).startswith("customer:")
                        or row.get("priority") not in {"Low", "Medium", "High", "Critical"}
                        for row in value)):
                    raise ValueError("artifact_queue_schema_incompatible")
            state = FeatureState("ready", value, path)
        except (OSError, ValueError, TypeError, KeyError, AttributeError, EOFError, ImportError):
            state = FeatureState(status, None, path, reason)
        states[key] = state
        visiting.discard(key)
        return state

    for key in entries:
        load(key)
    states["manifest"] = FeatureState("ready", manifest, "manifest.json")
    return ArtifactBundle(manifest, states, hashlib.sha256(raw).hexdigest(), root)


def _bundle(bundle=None):
    if isinstance(bundle, ArtifactBundle):
        return bundle
    return load_artifacts(bundle or Path(os.environ.get("SUPPORT_COPILOT_ARTIFACTS", "artifacts")))


_LABELS = {
    "ready": "Disponível", "missing": "Ausente", "corrupt": "Corrompido",
    "incompatible": "Incompatível", "stale": "Desatualizado", "unavailable": "Indisponível",
    "supported": "Com suporte", "exploratory": "Exploratório",
    "insufficient_support": "Suporte insuficiente",
    "insufficient_evidence": "Evidência insuficiente", "pending_review": "Revisão pendente",
    "no_reliable_signal": "Sem sinal confiável", "disabled": "Desativado", "enabled": "Ativado",
    "sealed": "Lacrado", "released_after_locks": "Aberto após congelamento",
    "human_review": "Revisão humana", "auto_route": "Encaminhamento automático",
    "Low": "Baixa", "Medium": "Média", "High": "Alta", "Critical": "Crítica", "Todas": "Todas",
    "Billing inquiry": "Dúvida de cobrança", "Cancellation request": "Pedido de cancelamento",
    "Product inquiry": "Dúvida sobre produto", "Refund request": "Pedido de reembolso",
    "Technical issue": "Problema técnico", "Access": "Acesso",
    "Administrative rights": "Permissões administrativas", "HR Support": "Suporte de RH",
    "Hardware": "Equipamentos", "Internal Project": "Projeto interno",
    "Miscellaneous": "Outros", "Purchase": "Compras", "Storage": "Armazenamento",
    "Email": "E-mail", "Phone": "Telefone", "Chat": "Chat", "Social media": "Redes sociais",
    "Ticket Channel": "Canal", "Ticket Priority": "Prioridade", "target": "Tipo",
    "Ticket Channel+Ticket Priority+target": "Canal, prioridade e tipo",
    "approve": "Aprovado", "edit_approve": "Editado e aprovado", "reject": "Rejeitado",
    "escalate": "Escalonado", "ok": "Disponível", "unsupported": "Sem suporte",
    "classification_unsupported": "Classificação sem suporte", "abstain": "Abstinência",
    "draft": "Rascunho", "validated_threshold": "Limiar validado",
    "validated_precedent": "Precedente validado", "below_threshold": "Abaixo do limiar",
    "ambiguous_input": "Entrada ambígua", "critical_priority": "Prioridade crítica",
    "privacy_failed": "Verificação de privacidade reprovada",
    "artifact_invalid": "Artefato inválido",
    "model_unavailable": "Modelo indisponível", "invalid_prediction": "Predição inválida",
    "domain_mismatch": "Domínio incompatível", "unknown_priority": "Prioridade desconhecida",
    "it_priority_not_observed": "Prioridade não observada no conjunto de TI",
    "risk_detector_unavailable": "Detector de risco indisponível",
    "empty_or_tokenless_input": "Entrada vazia ou sem palavras válidas",
    "invalid_input": "Entrada inválida", "invalid_or_private_input": "Entrada inválida ou privada",
    "ood_zero_vector": "Texto fora do vocabulário",
    "ood_check_unavailable": "Vocabulário não verificado",
    "ood_check_failed": "Verificação de vocabulário reprovada",
    "model_version_mismatch": "Versão do modelo incompatível",
    "automation_disabled": "Automação desativada", "pending_selection": "Seleção pendente",
    "retrieval_unavailable": "Recuperação indisponível", "no_safe_sources": "Sem fontes seguras",
    "no_similar_source": "Sem precedente semelhante",
    "retrieval_policy_not_validated": "Política de recuperação não validada",
    "below_retrieval_threshold": "Similaridade abaixo do limiar",
    "artifact_hash_mismatch": "Integridade do arquivo divergente",
    "dependency_unavailable": "Dependência indisponível",
    "manifest_missing_or_incompatible": "Manifesto ausente ou incompatível",
    "artifact_not_registered": "Recurso não registrado",
    "code_configuration_or_lock_changed": "Código, configuração ou dependências alterados",
    "test_sealed_review_pending": "Teste lacrado; revisão pendente",
    "customer_structured_operational_all_rows": "Todos os registros operacionais estruturados",
    "structured_operational": "Dados operacionais estruturados",
    "spearman_rank_correlation": "Correlação de postos de Spearman",
    "group_rating": "Avaliação por grupo", "observed_proxy": "Indicador observado",
    "projected_scenario": "Cenário projetado", "scenario_projection": "Cenário projetado",
    "valid": "Válidos", "negative": "Intervalo negativo",
    "invalid": "Inválidos", "missing_timestamp": "Data ausente",
    "not_closed": "Ainda não fechado", "invalid_timestamp": "Data inválida",
    "no_eligible_threshold": "Nenhum limiar atende aos critérios de automação",
    "model_prediction_failed": "Modelo não conseguiu classificar a entrada",
    "no_structured_operational_rows": "Sem registros operacionais estruturados",
    "artifact_dependency_cycle": "Dependências circulares",
    "artifact_domain_dependency_mismatch": "Dependência de outro domínio",
    "artifact_file_missing": "Arquivo ausente",
    "artifact_logical_hash_mismatch": "Conteúdo lógico divergente",
    "artifact_manifest_incompatible_or_stale": "Manifesto incompatível ou desatualizado",
    "artifact_model_incompatible": "Modelo incompatível",
    "artifact_path_outside_root": "Caminho fora do diretório permitido",
    "artifact_queue_schema_incompatible": "Estrutura da fila incompatível",
    "artifact_retriever_incompatible": "Índice de recuperação incompatível",
    "artifact_runtime_incompatible": "Ambiente de execução incompatível",
    "artifact_schema_incompatible": "Estrutura do artefato incompatível",
    "artifact_schema_or_state_incompatible": "Estrutura ou estado incompatível",
    "artifact_type_incompatible": "Tipo de artefato incompatível",
    "artifact_unavailable": "Artefato indisponível",
    "index_version_mismatch": "Versão do índice divergente",
    "policy_version_mismatch": "Versão da política divergente",
    "retrieval_review_changed": "Revisão de recuperação alterada",
    "manifest_entries_incompatible": "Registros do manifesto incompatíveis",
    "manifest_schema_incompatible": "Estrutura do manifesto incompatível",
    "manifest_symlink": "Manifesto aponta para um link não permitido",
}


def _label(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "Indisponível"
    if str(value).startswith("category:"):
        return "Categoria sensível: " + _label(str(value).split(":", 1)[1])
    if str(value).startswith(("sensitive:", "text:")):
        return "Expressão sensível detectada"
    if str(value).startswith("dependency_unavailable:"):
        return "Dependência indisponível: " + _resource_label(str(value).split(":", 1)[1])
    return _LABELS.get(str(value), "Não reconhecido; consulte os detalhes técnicos")


def _resource_label(key):
    family = {"models": "Modelos", "policies": "Políticas", "data": "Dados",
              "analytics": "Diagnóstico", "retrieval": "Recuperação", "queue": "Fila",
              "review": "Revisão", "manifest": "Manifesto"}.get(key.split(".")[0], "Recurso")
    domain = " — atendimento" if "customer" in key else " — TI" if ".it" in key else ""
    return family + domain


def _number(value, *, percent=False):
    if value is None or pd.isna(value):
        return "Indisponível"
    return f"{value * 100 if percent else value:,.2f}".replace(",", "_").replace(
        ".", ",").replace("_", ".") + ("%" if percent else "")


def _table(values, labels, *, categories=(), percentages=(), numbers=()):
    """Format a presentation copy; never mutate artifacts or export values."""
    frame = pd.DataFrame(values).reindex(columns=labels).copy()
    for column in labels:
        if column in categories:
            frame[column] = frame[column].map(_label)
        elif column in percentages or column in numbers:
            frame[column] = frame[column].map(
                lambda value, percent=column in percentages: _number(value, percent=percent))
        else:
            frame[column] = frame[column].fillna("Indisponível")
    st.dataframe(frame, hide_index=True, column_config={
        key: st.column_config.TextColumn(label) for key, label in labels.items()})


def _show_state(state):
    st.warning(f"{_label(state.status)}: {state.path} — {_label(state.reason)}. "
               f"Correção: {state.correction}.")
    with st.expander("Detalhes técnicos"):
        st.json(asdict(state) | {"value": None})


def assess_ticket(row, model, policy, retriever=None, retrieval_policy=None, *,
                  artifact_valid=True):
    """Shared pipeline/UI inference; only retriever.suggest can materialize a draft."""
    privacy = True
    try:
        text = sanitize_text(row["text"])
        privacy = text == row["text"]
    except ValueError:
        text, privacy = "", False
    domain = row["domain"]
    prediction = model.predict_one(text) if model and privacy and artifact_valid else Prediction(
        domain, "unavailable", reason_codes=("model_unavailable",))
    signals = derive_signals(text, domain=domain, ticket_id=row["ticket_id"],
                             priority=row.get("Ticket Priority"), prediction=prediction,
                             policy=policy, artifact_valid=artifact_valid, privacy_passed=privacy)
    route = decide_route(prediction, signals, policy)
    retrieval = retriever.suggest(text, retrieval_policy or RetrievalPolicy(), signals=signals) \
        if retriever is not None else None
    risk_count = len(set(signals.validation_reasons) | set(signals.sensitive_matches)
                     | ({"critical_priority"} if signals.priority == "Critical" else set())
                     | ({"ambiguous_input"} if signals.ambiguous else set()))
    return {"ticket_id": row["ticket_id"], "domain": domain, "text": text,
            "priority": signals.priority, "prediction": asdict(prediction),
            "signals": asdict(signals), "route": asdict(route),
            "retrieval": asdict(retrieval) if retrieval else None,
            "priority_score": priority_score(signals.priority, prediction.confidence, risk_count)}


def _model(bundle, domain):
    state = bundle.get(f"models.{domain}")
    return state.value.model if state.status == "ready" else None


def _policy(bundle, domain):
    state = bundle.get(f"policies.{domain}")
    return RoutingPolicy(**state.value) if state.status == "ready" else base_policy(domain)


def _runtime():
    return Path(os.environ.get("SUPPORT_COPILOT_RUNTIME", "data/runtime"))


def authorized_operator() -> str | None:
    """Return a stable OIDC subject only when issuer and subject are allowlisted."""
    try:
        if not st.user.is_logged_in:
            return None
        claims = st.user.to_dict()
        authorization = st.secrets.get("authorization", {})
    except (AttributeError, StreamlitSecretNotFoundError):
        return None
    issuer, subject = claims.get("iss"), claims.get("sub")
    allowed_issuers = authorization.get("allowed_issuers", [])
    allowed_subjects = authorization.get("allowed_subjects", [])
    if (not isinstance(issuer, str) or not isinstance(subject, str)
            or issuer not in allowed_issuers or subject not in allowed_subjects):
        return None
    return f"{issuer}#{subject}"


def _login_available() -> bool:
    try:
        return bool(st.secrets.get("auth"))
    except StreamlitSecretNotFoundError:
        return False


def _access_notice() -> None:
    st.warning("Acesso somente leitura. Decisões e export exigem operador autorizado via OIDC.")
    if _login_available():
        st.button("Entrar como operador", on_click=st.login)


def persist_decision(path, event):
    initialize_store(path)
    with closing(sqlite3.connect(path, isolation_level=None)) as connection:
        written = record_decision(connection, event)
    with closing(sqlite3.connect(path, isolation_level=None)) as connection:
        confirmed = next((row for row in list_decisions(connection) if row.id == written.id), None)
    if confirmed != written:
        raise ValueError("audit_readback_failed")
    return confirmed


def _remember_ticket():
    """Copy widget values before Streamlit removes widgets from an unselected ticket."""
    selected = st.session_state.get("editing_ticket")
    if selected is None:
        return
    saved = st.session_state["ticket_edits"][selected]
    version = saved["version"]
    for field in ("final", "reason"):
        saved[field] = st.session_state.get(f"{field}-{version}", saved[field])
    saved["dirty"] = (saved["final"], saved["reason"]) != saved["baseline"]


def render_queue(bundle=None) -> None:
    bundle = _bundle(bundle)
    operator = authorized_operator()
    st.title("Fila diária")
    _page_intro(
        "Operação assistida · humano no controle",
        "Fila diária",
        "Priorize riscos, entenda cada recomendação e registre decisões sem enviar "
        "mensagens ou fechar tickets externos.",
    )
    model_state = bundle.get("models.customer")
    if model_state.status != "ready":
        _show_state(model_state)
    state = bundle.get("queue.customer")
    if state.status != "ready":
        _show_state(state)
        st.info("Teste lacrado ou artefato indisponível. "
                "Revisão humana não é substituída por demo.")
        return
    model, policy = _model(bundle, "customer"), _policy(bundle, "customer")
    reference = bundle.get("retrieval.customer")
    retrieval_state = bundle.get("retrieval.policy")
    retrieval_policy = RetrievalPolicy(**retrieval_state.value) \
        if retrieval_state.status == "ready" else RetrievalPolicy()
    rows = [assess_ticket({"ticket_id": row["ticket_id"], "domain": "customer",
                           "text": row["text"], "Ticket Priority": row["priority"]},
                          model, policy, reference.value if reference.status == "ready" else None,
                          retrieval_policy,
                          artifact_valid=bundle.get("policies.customer").status == "ready")
            for row in state.value]
    rows.sort(key=lambda row: (*[-v for v in row["priority_score"]], row["ticket_id"]))
    _stat_strip([
        (str(len(rows)), "Tickets avaliados", ""),
        (str(sum(row["route"]["action"] == "human_review" for row in rows)),
         "Revisão humana", "ops-stat--alert"),
        (str(sum(row["route"]["action"] == "auto_route" for row in rows)),
         "Encaminhamento automático", "ops-stat--signal"),
        (str(sum(row["priority"] == "Critical" for row in rows)), "Prioridade crítica", ""),
    ])
    _section_label("01 · Recorte operacional")
    filter_priority, filter_route = st.columns(2)
    with filter_priority:
        priority = st.selectbox(
            "Filtrar prioridade", ["Todas", "Critical", "High", "Medium", "Low"],
            format_func=_label, on_change=_remember_ticket,
        )
    with filter_route:
        route_filter = st.selectbox(
            "Filtrar encaminhamento", ["Todas", "human_review", "auto_route"],
            format_func=_label, on_change=_remember_ticket,
        )
    rows = [row for row in rows if (priority == "Todas" or row["priority"] == priority)
            and (route_filter == "Todas" or row["route"]["action"] == route_filter)]
    if not rows:
        st.info("Nenhum ticket corresponde aos filtros.")
        return
    _section_label("02 · Fila priorizada")
    _table([{"Ticket": row["ticket_id"], "Prioridade": row["priority"],
                   "Categoria": row["prediction"]["label"],
                   "Confiança": row["prediction"]["confidence"],
                   "Encaminhamento": row["route"]["action"]}
           for row in rows], {key: key for key in (
               "Ticket", "Prioridade", "Categoria", "Confiança", "Encaminhamento")},
           categories=("Prioridade", "Categoria", "Encaminhamento"), percentages=("Confiança",))
    _section_label("03 · Ticket em foco")
    selected = st.selectbox("Ticket", [row["ticket_id"] for row in rows],
                            on_change=_remember_ticket)
    row = next(row for row in rows if row["ticket_id"] == selected)
    st.markdown(
        f'<div class="ops-callout"><strong>{escape(selected)}</strong><br>'
        f'{escape(row["text"])}</div>', unsafe_allow_html=True,
    )
    decision_summary, decision_reasons = st.columns([1, 1.35])
    with decision_summary:
        st.markdown("**Leitura do modelo**")
        st.write(f"Categoria: {_label(row['prediction']['label'])}")
        st.write(f"Confiança: {_number(row['prediction']['confidence'], percent=True)}")
        st.write(f"Encaminhamento: {_label(row['route']['action'])}")
    with decision_reasons:
        st.markdown("**Por que este encaminhamento?**")
        st.write(" · ".join(_label(code) for code in row["route"]["reason_codes"]))
    st.caption("Ordem da fila: prioridade, quantidade de riscos e incerteza, nessa sequência.")
    retrieval = row["retrieval"] or {}
    sources = retrieval.get("sources", [])
    _section_label("04 · Precedentes e decisão")
    if operator is None:
        _access_notice()
    st.caption("Similaridade dos precedentes não é probabilidade de correção.")
    _table(sources, {"ticket_id": "Ticket de origem", "similarity": "Similaridade",
                     "resolution": "Resolução sanitizada"}, percentages=("similarity",))
    draft = retrieval.get("draft")
    if not draft:
        st.info("Sem rascunho seguro: " + "; ".join(_label(code) for code in retrieval.get(
            "reason_codes", ["retrieval_unavailable"])))
    with st.expander("Detalhes técnicos"):
        st.json(row)
    version = content_hash({"bundle": bundle.version, "ticket": selected,
                            "draft": draft, "policy": retrieval_policy.policy_version})
    edits = st.session_state.setdefault("ticket_edits", {})
    previous = st.session_state.get("editing_ticket")
    _remember_ticket()
    if previous and previous != selected and edits[previous]["dirty"]:
        st.warning(f"Alterações não persistidas de {previous} preservadas nesta sessão. "
                   "Selecione esse ticket novamente para continuar; nada foi gravado no banco.")
    if selected not in edits:
        edits[selected] = {"version": version, "final": draft or "", "reason": "",
                           "baseline": (draft or "", ""), "dirty": False,
                           "submission_id": str(uuid4()), "confirmed": None}
    saved = edits[selected]
    if saved["version"] != version:
        saved.update(version=version, submission_id=str(uuid4()), confirmed=None,
                     baseline=(draft or "", ""))
        st.warning("Os artefatos deste ticket mudaram. "
                   "Revise o conteúdo preservado antes de salvar.")
    st.session_state["editing_ticket"] = selected
    st.session_state["ticket_version"] = version
    st.session_state["submission_id"] = saved["submission_id"]
    st.session_state["audit_confirmed"] = saved["confirmed"]
    for field in ("final", "reason"):
        st.session_state.setdefault(f"{field}-{version}", saved[field])
    # Outside a form: edits reach session_state on blur, before selection/navigation reruns.
    with st.container():
        final = st.text_area("Resposta final", key=f"final-{version}",
                             disabled=operator is None or not draft or bool(saved["confirmed"]),
                             on_change=_remember_ticket)
        reason = st.text_area("Motivo (obrigatório para rejeitar ou escalonar)",
                              key=f"reason-{version}",
                              disabled=operator is None or bool(saved["confirmed"]),
                              on_change=_remember_ticket)
        confirmed = saved["confirmed"]
        approve_col, edit_col, reject_col, escalate_col = st.columns(4)
        with approve_col:
            approve = st.button("Aprovar", disabled=operator is None or not draft
                                or bool(confirmed),
                                use_container_width=True)
        with edit_col:
            edit = st.button("Editar e aprovar", disabled=operator is None or not draft
                             or bool(confirmed),
                             use_container_width=True)
        with reject_col:
            reject = st.button("Rejeitar", disabled=operator is None or bool(confirmed),
                               use_container_width=True)
        with escalate_col:
            escalate = st.button("Escalonar", disabled=operator is None or bool(confirmed),
                                 use_container_width=True)
    action = next((name for name, clicked in (("approve", approve), ("edit_approve", edit),
                  ("reject", reject), ("escalate", escalate)) if clicked), None)
    if action:
        if authorized_operator() is None:
            st.error("Sessão não autorizada; nenhuma decisão foi gravada.")
            return
        prediction, route = row["prediction"], row["route"]
        event = DecisionEvent(
            submission_id=st.session_state["submission_id"], ticket_id=selected, domain="customer",
            data_version=bundle.manifest["sources"]["customer"]["data_version"],
            model_version=prediction["model_version"], rules_version=policy.rules_version,
            retrieval_version=retrieval.get("index_version"), threshold=route["threshold"],
            retrieval_threshold=retrieval.get("threshold"), prediction_status=prediction["status"],
            suggested_label=prediction["label"], confidence=prediction["confidence"],
            gate_action=route["action"], reason_codes=tuple(route["reason_codes"]),
            source_ids=tuple(source["ticket_id"] for source in sources), human_action=action,
            human_reason=reason, suggestion_text=draft,
            final_text=(draft if action == "approve" else
                        final if action == "edit_approve" else None),
        )
        try:
            stored = persist_decision(_runtime() / "decisions.sqlite3", event)
        except (OSError, sqlite3.Error, ValueError):
            st.error("Decisão não confirmada. Confira motivo/resposta sanitizada e banco local; "
                     "formulário e UUID preservados para nova tentativa.")
        else:
            st.session_state["audit_confirmed"] = stored.id
            saved.update(confirmed=stored.id, baseline=(final, reason), dirty=False)
    if st.session_state.get("audit_confirmed"):
        st.success(f"Decisão persistida e relida: audit_id={st.session_state['audit_confirmed']}")


def render_scorecard(root: Path | ArtifactBundle | None = None) -> None:
    """Render observed history, measured development evidence and projections separately."""
    bundle = _bundle(root)
    st.title("Diagnóstico operacional")
    _page_intro(
        "Leitura executiva · fatos antes de projeções",
        "Diagnóstico operacional",
        "Localize gargalos reais, separe evidência medida de hipótese e modele cenários "
        "sem transformar correlação em promessa.",
    )
    try:
        for key in ("analytics.operational_summary", "analytics.satisfaction_model"):
            if bundle.get(key).status != "ready":
                _show_state(bundle.get(key))
                return
        summary_payload = bundle.get("analytics.operational_summary").value
        satisfaction = bundle.get("analytics.satisfaction_model").value
        summary = OperationalSummary(**summary_payload)
    except (TypeError, ValueError):
        st.warning("Diagnóstico incompatível; execute make reproduce.")
        return
    if summary.status == "insufficient_support":
        st.warning(f"Diagnóstico sem suporte: {_label(summary.reason)}.")

    _section_label("01 · Base factual")
    st.subheader("Histórico observado")
    st.caption(
        "Intervalo pós-primeira-resposta: resolução menos primeira resposta. "
        "Tempo até primeira resposta e resolução total não são observáveis."
    )
    first, second, third = st.columns(3)
    first.metric(
        "Linhas no diagnóstico",
        summary.analysis_rows if summary.analysis_rows is not None else summary.development_rows,
    )
    second.metric("Intervalos válidos", summary.valid_intervals)
    third.metric(
        "Mediana pós-resposta (h)",
        "Indisponível" if summary.median_post_response_hours is None
        else _number(summary.median_post_response_hours),
    )
    analysis_rows = summary.analysis_rows or summary.development_rows
    coverage = summary.valid_intervals / analysis_rows if analysis_rows else 0.0
    st.info(
        f"Cobertura temporal utilizável: {summary.valid_intervals}/{analysis_rows} "
        f"({_number(coverage, percent=True)}). Os demais registros não sustentam comparação "
        "de tempo e não entram nos rankings."
    )
    st.write("Exclusões mutuamente exclusivas: " + "; ".join(
        f"{_label(key)}: {value}" for key, value in summary.interval_exclusions.items()))
    st.caption(
        "Excesso observado é proxy não negativo; não representa economia realizada. "
        f"Escopo: {_label(summary.analysis_scope)}; fonte: {_label(summary.source_lane)}; "
        f"linhas brutas: {_number(summary.source_rows)}, "
        f"sanitizadas: {_number(summary.sanitized_rows)}; "
        f"texto retido: {'sim' if summary.text_fields_retained else 'não'}."
    )
    bottleneck_columns = {
        "grouping": "Agrupamento", "Ticket Channel": "Canal", "Ticket Priority": "Prioridade",
        "target": "Tipo", "n_total": "Total", "n_eligible": "Intervalos válidos",
        "median_hours": "Mediana (h)", "median_ci95_low": "IC95% inferior (h)",
        "median_ci95_high": "IC95% superior (h)", "support_status": "Confiabilidade",
        "q1_hours": "Primeiro quartil (h)",
        "q3_hours": "Terceiro quartil (h)",
    }
    category_columns = (
        "grouping", "Ticket Channel", "Ticket Priority", "target", "support_status"
    )
    hour_columns = (
        "median_hours", "median_ci95_low", "median_ci95_high", "q1_hours", "q3_hours"
    )
    bottleneck_state = bundle.get("analytics.bottlenecks")
    if bottleneck_state.status == "ready":
        bottlenecks = pd.DataFrame(bottleneck_state.value)
        dimension_worst = bottlenecks.loc[
            bottlenecks["grouping"].isin(["Ticket Channel", "Ticket Priority", "target"])
            & bottlenecks["rank_worst"].eq(1)
        ].sort_values("grouping")
        st.markdown("**Gargalo principal por canal, prioridade e tipo**")
        _table(dimension_worst, bottleneck_columns, categories=category_columns,
               numbers=hour_columns)
        worst = bottlenecks.loc[
            bottlenecks["grouping"].eq("Ticket Channel+Ticket Priority+target")
            & bottlenecks["support_status"].eq("supported")
        ].sort_values(["rank_worst", "n_eligible"], ascending=[True, False]).head(5)
        st.markdown("**Piores combinações com suporte mínimo de 30 intervalos**")
        _table(worst, {key: value for key, value in bottleneck_columns.items()
                       if key != "grouping"},
               categories=category_columns, numbers=hour_columns)
        exploratory = bottlenecks.loc[
            bottlenecks["grouping"].eq("Ticket Channel+Ticket Priority+target")
            & bottlenecks["support_status"].eq("exploratory")
        ].sort_values(["rank_worst", "n_eligible"], ascending=[True, False]).head(3)
        if not exploratory.empty:
            st.warning(
                "Combinações com menos de 30 intervalos são exploratórias e não definem "
                "prioridade operacional sem nova amostra."
            )
            with st.expander("Achados exploratórios"):
                _table(exploratory, {key: value for key, value in bottleneck_columns.items()
                                     if key != "grouping"},
                       categories=category_columns, numbers=hour_columns)
    waste_state = bundle.get("analytics.waste_opportunities")
    if waste_state.status == "ready":
        waste = pd.DataFrame(waste_state.value)
        top_waste = waste.loc[waste["status"].eq("supported")].sort_values(
            "rank_excess"
        ).head(5)
        st.markdown("**Maiores excessos sobre a mediana dos pares**")
        _table(top_waste, {"target": "Tipo", "Ticket Priority": "Prioridade",
                          "eligible_n": "Casos elegíveis",
                          "peer_median_hours": "Mediana dos pares (h)",
                          "observed_excess_hours": "Excesso observado (h)",
                          "share_of_supported_excess": "Participação no excesso"},
               categories=category_columns, percentages=("share_of_supported_excess",),
               numbers=("peer_median_hours", "observed_excess_hours"))

    _section_label("02 · Qualidade do sinal")
    st.subheader("Desempenho medido")
    st.write(f"Estado: {_label(satisfaction.get('status'))}. "
             f"Avaliações válidas: {_number(satisfaction.get('valid_ratings'))}; "
             f"ausentes: {_number(satisfaction.get('missing_ratings'))}.")
    st.write(f"Erro médio absoluto — referência: {_number(satisfaction.get('baseline_mae'))}; "
             f"Ridge: {_number(satisfaction.get('ridge_mae'))}.")
    st.caption(
        "Validação cruzada histórica nos campos operacionais estruturados. Avaliações ausentes "
        "ou inválidas podem causar viés de seleção. Associação não demonstra causalidade."
    )
    association_state = bundle.get("analytics.satisfaction_associations")
    if association_state.status == "ready":
        associations = pd.DataFrame(association_state.value)
        interval_association = associations.loc[
            associations["feature"].eq("post_response_hours")
        ]
        if not interval_association.empty:
            row = interval_association.iloc[0]
            st.write(f"Associação intervalo-satisfação: {_label(row['association_metric'])}; "
                     f"valor: {_number(row['association_value'])}; pares: {int(row['n'])}.")
    metrics = bundle.get("models.metrics")
    test_status = metrics.value.get("status") if (
        metrics.status == "ready" and isinstance(metrics.value, dict)) else None
    if test_status == "sealed":
        st.caption("Teste final lacrado: aguardando decisão de revisão e locks válidos.")
    elif test_status == "released_after_locks":
        st.caption("Teste final aberto após locks. A validação cruzada acima continua sendo "
                   "evidência de desenvolvimento, não resultado do teste final.")
    else:
        st.caption("Estado do teste final não verificável; execute make reproduce.")
        if metrics.status != "ready":
            _show_state(metrics)
    retrieval = bundle.get("retrieval.metrics")
    if retrieval.status == "ready" and isinstance(retrieval.value, dict):
        messages = {
            "disabled": "Assistência de recuperação desativada; abertura do teste não "
                        "autoriza respostas automáticas.",
            "insufficient_evidence": "Recuperação sem evidência suficiente; não há "
                                     "validação humana concluída para aprovar drafts.",
            "pending_review": "Recuperação aguardando revisão humana; drafts não aprovados.",
        }
        if retrieval.value.get("status") in messages:
            st.caption(messages[retrieval.value["status"]])

    _section_label("03 · Simulador de impacto")
    st.subheader("Cenários projetados")
    st.caption(
        "O volume inicial de 30.000 tickets/ano vem do contexto do briefing, não do Dataset 1. "
        "O Dataset 1 não observa custo nem moeda. Fração, minutos e custo são premissas "
        "editáveis; o valor monetário fica indisponível até uma premissa de custo ser informada."
    )
    defaults = {
        "conservative": (30_000, 0.10, 3.0, 0.0),
        "base": (30_000, 0.25, 5.0, 0.0),
        "optimistic": (30_000, 0.40, 8.0, 0.0),
    }
    labels = {"conservative": "Conservador", "base": "Base", "optimistic": "Otimista"}
    for name, values in defaults.items():
        with st.expander(labels[name], expanded=name == "base"):
            volume = int(st.number_input(
                "Volume anual elegível", min_value=0, value=values[0], key=f"{name}-volume"
            ))
            share = float(st.number_input(
                "Fração endereçável", min_value=0.0, max_value=1.0, value=values[1],
                key=f"{name}-share",
            ))
            minutes = float(st.number_input(
                "Minutos poupados por caso", min_value=0.0, value=values[2],
                key=f"{name}-minutes",
            ))
            cost = float(st.number_input(
                "Custo por hora (premissa; moeda não definida)", min_value=0.0,
                value=values[3], key=f"{name}-cost"
            ))
            projection = scenario_projection(
                summary,
                ScenarioAssumptions(volume, share, minutes, cost, name),
            )
            st.write(f"Horas mensais projetadas: {_number(projection.annual_hours / 12)}. "
                     f"Horas anuais projetadas: {_number(projection.annual_hours)}. "
                     f"Custo anual projetado: "
                     f"{_number(projection.annual_cost) if cost > 0 else 'não calculado'}. "
                     "Natureza: projeção, não economia realizada.")

    with st.expander("Detalhes técnicos"):
        st.json({"summary": summary_payload, "satisfaction": satisfaction})
        for key in ("analytics.bottlenecks", "analytics.waste_opportunities",
                    "analytics.satisfaction_associations", "analytics.automation_opportunities"):
            state = bundle.get(key)
            st.caption(key)
            st.dataframe(state.value) if state.status == "ready" else _show_state(state)
        metrics = bundle.get("models.metrics")
        if metrics.status == "ready":
            st.json(metrics.value)


def render_it_lab(bundle=None) -> None:
    bundle = _bundle(bundle)
    st.title("Laboratório IT")
    _page_intro(
        "Sandbox seguro · domínio independente",
        "Laboratório IT",
        "Teste a classificação de chamados internos sem misturar registros, taxonomias ou "
        "métricas do atendimento ao cliente.",
    )
    _stat_strip([
        (str(len(IT_TAXONOMY)), "Categorias disponíveis", "ops-stat--signal"),
        ("0", "Dados pessoais permitidos", "ops-stat--alert"),
        ("IT", "Domínio isolado", ""),
        ("HITL", "Gate operacional", ""),
    ])
    _section_label("01 · Nova classificação")
    st.caption("Prioridade e desfecho operacional não observados. Sem união de registros Customer.")
    state = bundle.get("models.it")
    if state.status != "ready":
        _show_state(state)
    with st.form("it-input"):
        text = st.text_area("Descrição IT (sem dados pessoais)")
        submitted = st.form_submit_button("Classificar IT")
    if submitted:
        row = assess_ticket({"ticket_id": "it:local", "domain": "it", "text": text},
                            _model(bundle, "it"), _policy(bundle, "it"),
                            artifact_valid=state.status == "ready")
        if not row["signals"]["privacy_passed"]:
            st.error("Entrada recusada: remova dados pessoais e tente novamente.")
        else:
            _section_label("02 · Resultado")
            st.markdown(
                f'<div class="ops-callout"><strong>{escape(_label(row["prediction"]["label"]))}'
                f'</strong> · {_number(row["prediction"]["confidence"], percent=True)}<br>'
                f'{escape(row["text"])}</div>', unsafe_allow_html=True,
            )
            result_route, result_reasons = st.columns([1, 1.4])
            with result_route:
                st.markdown("**Encaminhamento**")
                st.write(_label(row["route"]["action"]))
            with result_reasons:
                st.markdown("**Critérios aplicados**")
                st.write(" · ".join(_label(code) for code in row["route"]["reason_codes"]))
            with st.expander("Detalhes técnicos"):
                st.json(row)
    metrics = bundle.get("models.metrics")
    if metrics.status == "ready":
        with st.expander("Detalhes técnicos"):
            st.json(metrics.value["domains"]["it"])


def render_evidence(bundle=None) -> None:
    bundle = _bundle(bundle)
    st.title("Evidências e decisões locais")
    _page_intro(
        "Rastreabilidade · estado verificável",
        "Evidências e decisões locais",
        "Inspecione integridade, disponibilidade e decisões humanas persistidas sem esconder "
        "limitações do detector de risco.",
    )
    ready = sum(state.status == "ready" for state in bundle.features.values())
    unavailable = len(bundle.features) - ready
    _stat_strip([
        (str(ready), "Recursos disponíveis", "ops-stat--signal"),
        (str(unavailable), "Recursos com atenção", "ops-stat--alert" if unavailable else ""),
        (bundle.version[:8], "Versão do bundle", ""),
        ("Local", "Persistência", ""),
    ])
    st.caption("Regexes e vetor zero não detectam todo risco/PII/OOD. Revisão humana é necessária.")
    _section_label("01 · Integridade dos artefatos")
    with st.expander("Detalhes técnicos"):
        st.json({key: bundle.manifest.get(key) for key in (
            "code_revision", "configuration_sha256", "lock_sha256", "models", "retrieval")})
    _table([{"recurso": _resource_label(key), "estado": state.status, "causa": state.reason,
                   "caminho": state.path, "correção": state.correction}
            for key, state in bundle.features.items()],
           {"recurso": "Recurso", "estado": "Estado", "causa": "Causa",
            "caminho": "Arquivo", "correção": "Correção"}, categories=("estado", "causa"))
    if authorized_operator() is None:
        _section_label("02 · Trilha de decisões")
        _access_notice()
        return
    path = _runtime() / "decisions.sqlite3"
    try:
        initialize_store(path)
        with closing(sqlite3.connect(path, isolation_level=None)) as connection:
            decisions = list_decisions(connection)
        _section_label("02 · Trilha de decisões")
        _table([asdict(row) for row in decisions], {
            "id": "Registro", "ticket_id": "Ticket", "human_action": "Decisão humana",
            "human_reason": "Motivo", "suggested_label": "Categoria sugerida",
            "confidence": "Confiança", "gate_action": "Encaminhamento",
            "final_text": "Resposta final"},
            categories=("human_action", "suggested_label", "gate_action"),
            percentages=("confidence",))
        with st.expander("Detalhes técnicos"):
            st.json([asdict(row) for row in decisions])
        if st.button("Persistir export CSV"):
            with closing(sqlite3.connect(path, isolation_level=None)) as connection:
                export = export_decisions_csv(connection, _runtime() / "exports" /
                                               f"decisions-{uuid4()}.csv")
            st.session_state["export"] = export
        export = st.session_state.get("export")
        if export:
            st.caption(f"Export persistido: {export.row_count} decisões; SHA-256 {export.sha256}")
            st.download_button("Baixar CSV persistido", export.content, export.path.name,
                               mime="text/csv")
    except (OSError, sqlite3.Error, ValueError):
        st.error("Banco/export indisponível; preserve data/runtime e confira permissões/schema.")
