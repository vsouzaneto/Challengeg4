"""Single-page local cockpit for Challenge 004."""

from __future__ import annotations

import hashlib
import html
import json
import os
import sqlite3
import string
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from numbers import Integral
from typing import Any

import pandas as pd
import streamlit as st

from analysis import (METHOD_VERSION, align_scope_timestamp, analyze, content_strategy_30d,
                      decision_baseline, executive_answers, executive_summary,
                      export_evidence, load_csv, observe_evidence,
                      sponsorship_break_even)
from storage import connect, list_decisions, record_decision, record_import, record_outcome, utc_now


def _render_design_system() -> None:
    st.markdown(
        """
        <style>
        :root {
          --ink: #17201e;
          --ink-soft: #53605c;
          --paper: #f3efe5;
          --paper-raised: #fffdf7;
          --line: #c8c2b3;
          --signal: #ef674f;
          --signal-dark: #b63828;
          --proof: #26705f;
        }

        .stApp {
          color: var(--ink);
          background:
            linear-gradient(rgba(23, 32, 30, .035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(23, 32, 30, .035) 1px, transparent 1px),
            radial-gradient(circle at 86% 4%, rgba(239, 103, 79, .11), transparent 24rem),
            var(--paper);
          background-size: 28px 28px, 28px 28px, auto, auto;
        }

        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none; }
        [data-testid="stAppViewContainer"] > .main { background: transparent; }
        .block-container { max-width: 1440px; padding-top: 2.25rem; padding-bottom: 5rem; }

        h1, h2, h3 {
          color: var(--ink);
          font-family: "Iowan Old Style", "Baskerville", "Palatino Linotype", serif;
          letter-spacing: -.035em;
        }
        h1 { font-size: clamp(2.8rem, 6vw, 5.8rem) !important; line-height: .92 !important; max-width: 900px; }
        h3 { margin-top: 2.5rem !important; font-size: 2rem !important; }
        p, label, button, input, textarea { font-family: "Avenir Next", "Segoe UI", sans-serif; }

        .cockpit-kicker {
          display: flex;
          justify-content: space-between;
          gap: 1rem;
          margin-bottom: 1.2rem;
          padding-bottom: .8rem;
          border-bottom: 1px solid var(--ink);
          color: var(--ink);
          font: 700 .72rem/1.2 "Avenir Next", sans-serif;
          letter-spacing: .16em;
          text-transform: uppercase;
        }
        .cockpit-kicker__signal::before {
          content: "";
          display: inline-block;
          width: .65rem;
          height: .65rem;
          margin-right: .55rem;
          border-radius: 50%;
          background: var(--signal);
          box-shadow: 0 0 0 4px rgba(239, 103, 79, .14);
        }

        .workflow-rail {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          margin: 1.75rem 0 2.4rem;
          border: 1px solid var(--line);
          background: rgba(255, 253, 247, .7);
        }
        .workflow-rail span {
          padding: .8rem 1rem;
          color: var(--ink-soft);
          font: 700 .72rem/1.2 "Avenir Next", sans-serif;
          letter-spacing: .1em;
          text-transform: uppercase;
        }
        .workflow-rail span + span { border-left: 1px solid var(--line); }
        .workflow-rail b { color: var(--signal-dark); margin-right: .45rem; }

        [data-testid="stMetric"] {
          min-height: 8rem;
          padding: 1.15rem 1.25rem;
          border: 1px solid var(--line);
          border-top: 4px solid var(--ink);
          background: var(--paper-raised);
          box-shadow: 8px 8px 0 rgba(23, 32, 30, .06);
        }
        [data-testid="stMetricValue"] {
          color: var(--ink);
          font-family: "Iowan Old Style", "Baskerville", serif;
          font-size: clamp(2rem, 3.5vw, 3.25rem);
          letter-spacing: -.04em;
        }
        [data-testid="stMetricLabel"] { color: var(--ink-soft); letter-spacing: .04em; }

        .head-answers {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 1rem;
          margin: 1rem 0 2rem;
        }
        .head-answer {
          padding: 1.1rem;
          border: 1px solid var(--line);
          border-top: 5px solid var(--signal);
          background: var(--paper-raised);
          box-shadow: 8px 8px 0 rgba(23, 32, 30, .06);
        }
        .head-answer h4 {
          min-height: 2.5rem;
          margin: 0 0 .8rem;
          color: var(--ink-soft);
          font: 700 .72rem/1.3 "Avenir Next", sans-serif;
          letter-spacing: .09em;
          text-transform: uppercase;
        }
        .head-answer strong { display: block; min-height: 3.5rem; color: var(--ink); line-height: 1.25; }
        .head-answer .answer-kpi { margin: .9rem 0 .55rem; color: var(--signal-dark); font-weight: 800; }
        .head-answer p { margin: .45rem 0; color: var(--ink-soft); font-size: .88rem; line-height: 1.45; }
        .head-answer .answer-action { padding-top: .55rem; border-top: 1px solid var(--line); color: var(--ink); }

        [data-testid="stFileUploaderDropzone"] {
          border: 1px dashed var(--ink-soft);
          border-radius: 0;
          background: rgba(255, 253, 247, .7);
        }
        [data-testid="stFileUploaderDropzone"]:hover { border-color: var(--signal); background: var(--paper-raised); }

        [data-testid="stExpander"] {
          overflow: hidden;
          border: 1px solid var(--line);
          border-radius: 0;
          background: rgba(255, 253, 247, .58);
        }
        [data-testid="stExpander"] summary:hover { color: var(--signal-dark); }
        [data-testid="stVerticalBlockBorderWrapper"] {
          border-color: var(--line) !important;
          border-radius: 0 !important;
          background: rgba(255, 253, 247, .78);
        }
        [data-testid="stForm"] { border: 1px solid var(--ink) !important; border-radius: 0; background: var(--paper-raised); }

        .stButton > button, .stDownloadButton > button {
          border: 1px solid var(--ink);
          border-radius: 0;
          background: var(--ink);
          color: var(--paper-raised);
          font-weight: 700;
          letter-spacing: .025em;
          transition: transform 120ms ease, box-shadow 120ms ease, background 120ms ease;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
          border-color: var(--signal-dark);
          background: var(--signal);
          color: var(--ink);
          box-shadow: 4px 4px 0 var(--ink);
          transform: translate(-2px, -2px);
        }
        button:focus-visible, input:focus-visible, textarea:focus-visible, [role="combobox"]:focus-visible {
          outline: 3px solid var(--signal) !important;
          outline-offset: 3px;
        }

        [data-testid="stDataFrame"] { border: 1px solid var(--ink); background: var(--paper-raised); }
        [data-testid="stAlert"] { border-radius: 0; border-left-width: 5px; }
        code { color: var(--proof); background: rgba(38, 112, 95, .08); border-radius: 2px; }
        hr { border-color: var(--line); }

        @media (max-width: 720px) {
          .block-container { padding: 1.25rem 1rem 3rem; }
          .cockpit-kicker { display: block; }
          .cockpit-kicker span { display: block; margin-bottom: .5rem; }
          .workflow-rail { grid-template-columns: 1fr; }
          .workflow-rail span + span { border-left: 0; border-top: 1px solid var(--line); }
          .head-answers { grid-template-columns: 1fr; }
          .head-answer h4, .head-answer strong { min-height: 0; }
        }
        @media (prefers-reduced-motion: reduce) {
          *, *::before, *::after { scroll-behavior: auto !important; transition: none !important; }
        }
        </style>
        <div class="cockpit-kicker">
          <span class="cockpit-kicker__signal">Signal Desk / Social Intelligence</span>
          <span>Challenge 004 · decisão reproduzível</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def app_now() -> datetime:
    simulated = os.environ.get("SOCIAL_COCKPIT_SIMULATION_NOW")
    if simulated:
        value = datetime.fromisoformat(simulated)
        if value.tzinfo is None:
            raise ValueError("SOCIAL_COCKPIT_SIMULATION_NOW exige timezone explícito.")
        return value
    return utc_now()


def database_path() -> Path:
    configured = os.environ.get("SOCIAL_COCKPIT_DB_PATH")
    return Path(configured).expanduser() if configured else Path.home() / ".local/share/ai-master-challenge-004/cockpit.sqlite3"


def _source_metadata(name: str, raw: bytes, frame: pd.DataFrame) -> dict[str, object]:
    return {
        "source_hash": str(frame.iloc[0]["source_hash"]),
        "file_name": Path(name).name,
        "byte_count": len(raw),
        "row_count": len(frame),
        "columns": list(frame.columns),
        "period_start": min(frame["post_date"]).isoformat(),
        "period_end": max(frame["post_date"]).isoformat(),
        "platforms": sorted(frame["platform"].unique().tolist()),
        "imported_at": app_now().isoformat(),
        "method_version": METHOD_VERSION,
    }


def _find_evidence(value: object, evidence_id: str) -> dict[str, object] | None:
    if isinstance(value, dict):
        if value.get("evidence_id") == evidence_id:
            return value
        for child in value.values():
            found = _find_evidence(child, evidence_id)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_evidence(child, evidence_id)
            if found:
                return found
    return None


def _baseline(recommendation: dict[str, object]) -> dict[str, object]:
    return {**decision_baseline(recommendation["evidence_snapshot"]),
            "simulation": bool(os.environ.get("SOCIAL_COCKPIT_SIMULATION_NOW"))}


def _recommendation_context(item: dict[str, object], *, literal: bool = False) -> str:
    context = item.get("context", {})
    assert isinstance(context, dict)
    def abbreviated(value: object, limit: int = 32) -> str:
        text = str(value)
        return text if len(text) <= limit else text[:limit - 1] + "…"

    labels = (("platform", "Plataforma"), ("content_type", "Formato"),
              ("content_category", "Categoria"), ("follower_band", "Faixa"),
              ("period_month", "Mês"))
    values = ((key, label, abbreviated(context[key])) for key, label in labels if context.get(key) is not None)
    parts = [f"{label}: {_literal_caption(value) if literal else value}" for _, label, value in values]
    return " · ".join(parts) or "Contexto amplo"


def _display_number(value: object) -> str:
    number = float(value)
    return "0" if number == 0 else f"{number:.6g}"


def _display_integer(value: object) -> str:
    """Format UI counts with the Brazilian thousands separator."""
    return f"{int(value):,}".replace(",", ".")


def _literal_caption(value: object) -> str:
    return "".join(f"\\{character}" if character in string.punctuation else character for character in str(value))


def _table_numbers(frame: pd.DataFrame) -> pd.DataFrame:
    """Keep integer counts exact and consistently formatted for display."""
    for column in frame.columns:
        if any(isinstance(value, Integral) for value in frame[column]):
            frame = frame.copy()
            frame[column] = frame[column].map(
                lambda value: _display_integer(value) if isinstance(value, Integral) else value
            )
    return frame


def _render_head_answers(answers: list[dict[str, str]]) -> None:
    def safe(value: object) -> str:
        return html.escape(str(value))

    cards = "".join(
        f"""<article class="head-answer">
        <h4>{safe(item['question'])}</h4><strong>{safe(item['verdict'])}</strong>
        <p class="answer-kpi">{safe(item['kpi'])}</p><p>{safe(item['comparison'])}</p>
        <p>{safe(item['sample'])}</p><p class="answer-action"><b>Ação:</b> {safe(item['action'])}</p>
        <p><b>Força:</b> {safe(item['strength'])}</p><p><b>Cobertura:</b> {safe(item['coverage'])}</p>
        <p><b>Estabilidade:</b> {safe(item['stability'])}</p><p><b>Evidência:</b> {safe(item['evidence_id'])}</p>
        <p><b>O que mudaria a decisão:</b> {safe(item['change_trigger'])}</p>
        </article>"""
        for item in answers
    )
    st.subheader("Quatro respostas obrigatórias do challenge")
    st.markdown(f'<section class="head-answers">{cards}</section>', unsafe_allow_html=True)


def _render_decision_program(result: dict[str, object]) -> None:
    drivers = result.get("engagement_drivers", {}).get("contexts", [])
    st.subheader("Drivers contextuais")
    if drivers:
        st.dataframe(
            _table_numbers(pd.DataFrame([
                {
                    "contexto": " / ".join(str(item["context"][key]) for key in ("platform", "content_type", "content_category", "follower_band")),
                    "delta_erv_pp": item["median_delta_erv_pp"],
                    "estabilidade": item["stability"],
                    "força": item["strength"],
                    "meses": item["eligible_months"],
                    "posts": item["posts"],
                    "creators": item["creators"],
                }
                for item in drivers
            ])),
            hide_index=True,
            width="stretch",
        )
    else:
        st.caption("Nenhum contexto atingiu amostra mensal comparável; coletar antes de priorizar.")

    st.subheader("Estratégia de 30 dias")
    program = content_strategy_30d(result)
    for week in program["weeks"]:
        st.markdown(
            f"**Semana {week['week']} · {week['window']}** — {week['action']}  \n"
            f"Responsável: {week['owner']} · Métrica: {week['metric']} · Cadência: {week['cadence']} · Gate: {week['gate']}"
        )
    st.caption("Preservar o mix fora dos testes. Nenhuma publicação ou verba é executada automaticamente.")


def _render_financial_scenario(result: dict[str, object], source_hash: str) -> dict[str, object] | None:
    strata = result.get("sponsorship", {}).get("strata", [])
    with st.expander("Cenário financeiro manual", expanded=False):
        st.caption("Simulação efêmera: não altera análise, histórico, decisões ou CSV de evidências.")
        if not strata:
            st.caption("Nenhum estrato orgânico/patrocinado atingiu a amostra comparável mínima.")
            return None
        selected_id = st.selectbox(
            "Estrato comparável",
            [item["evidence_id"] for item in strata],
            key="scenario_sponsorship_stratum",
        )
        selected = next(item for item in strata if item["evidence_id"] == selected_id)
        st.caption("Contexto: " + " / ".join(str(value) for value in selected["context"].values()))
        assumptions = {
            "sponsorship_cost": st.number_input("Custo do patrocínio", min_value=0.0, help="Valor pago ao creator por post.", key="scenario_sponsorship_cost"),
            "incremental_production_cost": st.number_input("Custo incremental de produção", min_value=0.0, help="Custo adicional do conteúdo patrocinado.", key="scenario_production_cost"),
            "value_per_conversion": st.number_input("Valor por conversão", min_value=0.0, help="Valor econômico manual de uma conversão.", key="scenario_value_per_conversion"),
            "organic_conversion_rate": st.number_input("Taxa orgânica", min_value=0.0, max_value=1.0, format="%.4f", help="Fração entre 0 e 1.", key="scenario_organic_rate"),
            "sponsored_conversion_rate": st.number_input("Taxa patrocinada", min_value=0.0, max_value=1.0, format="%.4f", help="Fração entre 0 e 1.", key="scenario_sponsored_rate"),
        }
        signature = json.dumps({"source": source_hash, "evidence_id": selected_id, **assumptions}, sort_keys=True)
        if st.session_state.get("sponsorship_scenario_signature") != signature:
            st.session_state.pop("sponsorship_scenario", None)
        if st.button("Calcular cenário", key="calculate_sponsorship_scenario"):
            st.session_state["sponsorship_scenario"] = sponsorship_break_even(selected, assumptions)
            st.session_state["sponsorship_scenario_signature"] = signature
        scenario = st.session_state.get("sponsorship_scenario")
        if scenario:
            st.markdown(
                "**Cenário manual**  \n"
                f"Status: `{scenario['status']}` · custo máximo: `{scenario['max_sponsorship_cost']}` · "
                f"uplift mínimo: `{scenario['required_uplift_pp']}` p.p."
            )
            st.caption("Não é ROI observado nem prova causal; depende integralmente das premissas informadas.")
        return scenario


def _render_evidence(evidence: dict[str, Any], item: dict[str, Any], result: dict[str, Any]) -> None:
    """Present the engine's evidence without recomputing its comparison."""
    benchmark = evidence.get("benchmark", {})
    target = evidence.get("current", evidence.get("sponsored", evidence.get("values", {})))
    reference = evidence.get("previous", evidence.get("organic", benchmark))
    sponsorship = "sponsored" in evidence
    rate_key = "creator_median_erv" if sponsorship else "median_erv"
    rate = evidence.get("erv", target.get(rate_key))
    median = reference.get("median", reference.get(rate_key))
    q1, q3 = reference.get("q1", reference.get("q1_erv")), reference.get("q3", reference.get("q3_erv"))
    st.write("Taxa-alvo ERv (%):", rate)
    st.write("Volume-alvo — visualizações / interações:", _display_integer(target.get("views", 0)), "/", _display_integer(target.get("interactions", 0)))
    st.write("Benchmark — mediana ERv (%):", median)
    st.write("Benchmark — quartis Q1 / Q3 ERv (%):", q1, "/", q3)
    if sponsorship:
        st.caption("Patrocínio: medianas das medianas por creator; quartis descritivos dos posts orgânicos, não usados no delta.")
    else:
        st.caption("ERv = 100 × (likes + shares + comments_count) / views; medianas e quartis dos posts com taxa definida.")
    st.write("Delta ERv (p.p.):", evidence.get("delta_erv_pp"))
    st.write("Amostra-alvo — posts elegíveis / creators:", _display_integer(target.get("n_rate", 1 if "erv" in evidence else 0)), "/", _display_integer(target.get("creators", 1 if "erv" in evidence else 0)))
    st.write("Amostra do benchmark — posts elegíveis / creators:", _display_integer(reference.get("n_rate", 0)), "/", _display_integer(reference.get("n_creators", reference.get("creators", 0))))
    st.write("Contexto solicitado:")
    st.json(item.get("context", {}))
    st.write("Contexto efetivo:")
    st.json(benchmark.get("effective_context", evidence.get("context", {})))
    st.write("Nível efetivo / fallback:", benchmark.get("effective_level", "núcleo de patrocínio; audiência apenas nos filtros" if sponsorship else "mesmo contexto; período anterior de igual duração" if "current" in evidence else "nenhum comparador elegível"))
    st.write("Controles removidos:", benchmark.get("removed_controls", []))
    st.write("Suficiência:", "suficiente" if benchmark.get("eligible") or "current" in evidence or sponsorship else "insuficiente")
    st.write("Força da evidência (C):", evidence.get("strength", 0.0), evidence.get("strength_label", ""))
    st.write("Volumes usados no score / denominadores P95:")
    st.json({"volumes": item.get("priority_values", {}), "P95": item.get("normalization", {})})
    refs = sorted(set(evidence.get("source_row_ids", []) + evidence.get("previous_source_row_ids", []) + evidence.get("current_source_row_ids", []) + benchmark.get("source_row_ids", []) + ([evidence["source_row_id"]] if "source_row_id" in evidence else [])))
    st.write("Referências de origem:")
    if refs:
        st.dataframe(pd.DataFrame({"source_row_id": refs, "source_line": [result["row_references"].get(value) for value in refs]}), hide_index=True, width="stretch")
    else:
        st.caption("Sem linhas elegíveis: a pendência exige nova coleta.")


def _decision_export(items: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            **item,
            "evidence_id": item["recommendation_key"],
            "text": item["edited_text"] if item["status"] == "edited" else item["original_text"],
        }
        for item in items
    ]


st.set_page_config(page_title="Cockpit de Social Media", layout="wide")
_render_design_system()
st.title("Cockpit de Social Media")
st.caption("Decisão local, auditável e humana. Nenhuma publicação ou investimento é executado.")
st.markdown(
    """
    <div class="workflow-rail" aria-label="Fluxo do cockpit">
      <span><b>01</b> Importar</span>
      <span><b>02</b> Interpretar</span>
      <span><b>03</b> Decidir</span>
    </div>
    """,
    unsafe_allow_html=True,
)
simulation = bool(os.environ.get("SOCIAL_COCKPIT_SIMULATION_NOW"))
if simulation:
    try:
        st.warning(f"SIMULAÇÃO / REPLAY RETROSPECTIVO — relógio controlado: {app_now().isoformat()}. Dados sintéticos não são resultados de produção.")
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

try:
    connection = connect(database_path())
except (OSError, sqlite3.Error, RuntimeError) as exc:
    st.error(f"Banco local indisponível: {exc}")
    st.stop()

uploaded = st.file_uploader("Enviar CSV", type=["csv"], help="UTF-8, até 50 MiB; o arquivo bruto não é persistido.")
if uploaded is not None:
    raw = uploaded.getvalue()
    source_key = hashlib.sha256(raw).hexdigest()
    if st.session_state.get("validated_source_key") != source_key:
        frame, diagnostics = load_csv(raw)
        if diagnostics:
            st.error("Arquivo rejeitado. A fonte válida anterior, se houver, continua ativa.")
            st.dataframe(pd.DataFrame(diagnostics), hide_index=True, width="stretch")
        elif frame is not None:
            metadata = _source_metadata(uploaded.name, raw, frame)
            try:
                record_import(connection, metadata)
            except sqlite3.Error as exc:
                st.error(f"Importação validada, mas a proveniência não foi salva: {exc}")
            else:
                st.session_state["active_frame"] = frame
                st.session_state["active_metadata"] = metadata
                st.session_state["validated_source_key"] = source_key

decisions = list_decisions(connection)
active_frame = st.session_state.get("active_frame")
metadata = st.session_state.get("active_metadata")
result = None
financial_scenario = None

if active_frame is None or metadata is None:
    st.info("Nenhuma fonte ativa. Envie um CSV válido para iniciar a análise; o histórico local continua disponível.")
else:
    st.caption(
        f"Fonte ativa `{str(metadata['source_hash'])[:12]}…` · {_display_integer(metadata['row_count'])} linhas · "
        f"{metadata['period_start']} a {metadata['period_end']} · "
        f"{_literal_caption(', '.join(metadata['platforms']))}"
    )
    st.caption("Dados históricos são rotulados pela data do dataset; associação não implica causalidade nem ROI.")

    head_answer_key = (str(metadata["source_hash"]), METHOD_VERSION)
    if st.session_state.get("head_answer_key") != head_answer_key:
        with st.spinner("Consolidando as quatro respostas no histórico completo…"):
            history_scope = {
                "target_start": min(active_frame["post_date"]).isoformat(),
                "target_end": max(active_frame["post_date"]).isoformat(),
                "reference_date": max(active_frame["post_date"]).isoformat(),
                "filters": {},
                "strict_audience": False,
                "include_post_alerts": False,
                "method_version": METHOD_VERSION,
            }
            history_result = analyze(active_frame, history_scope, str(metadata["source_hash"]))
            st.session_state["head_result"] = history_result
            st.session_state["head_answer_key"] = head_answer_key
    history_result = st.session_state["head_result"]
    st.session_state["head_answers"] = executive_answers(history_result)
    _render_head_answers(st.session_state["head_answers"])
    _render_decision_program(history_result)

    filter_columns = {
        "platform": "Plataformas",
        "content_type": "Formatos",
        "content_category": "Categorias",
        "audience_age_distribution": "Idades",
        "audience_gender_distribution": "Gêneros",
        "audience_location": "Localizações",
    }
    filters: dict[str, list[object]] = {}
    with st.expander("Filtros da análise", expanded=False):
        period_mode = st.selectbox(
            "Período",
            ("Últimos 7 dias", "Semana ISO", "Mês calendário", "Todo o histórico", "Intervalo personalizado"),
            key="period_mode",
        )
        reference = max(active_frame["post_date"])
        dataset_start_date = min(active_frame["post_date"]).date()
        dataset_end_date = reference.date()
        if period_mode == "Semana ISO":
            requested_start_date = dataset_end_date - timedelta(days=dataset_end_date.weekday())
            requested_end_date = requested_start_date + timedelta(days=6)
        elif period_mode == "Mês calendário":
            requested_start_date = dataset_end_date.replace(day=1)
            next_month = date(requested_start_date.year + (requested_start_date.month == 12), requested_start_date.month % 12 + 1, 1)
            requested_end_date = next_month - timedelta(days=1)
        elif period_mode == "Todo o histórico":
            requested_start_date, requested_end_date = dataset_start_date, dataset_end_date
        elif period_mode == "Intervalo personalizado":
            selected_dates = st.date_input(
                "Intervalo explícito",
                value=(max(dataset_start_date, dataset_end_date - timedelta(days=6)), dataset_end_date),
                min_value=dataset_start_date,
                max_value=dataset_end_date,
            )
            if len(selected_dates) == 2:
                requested_start_date, requested_end_date = selected_dates
            else:
                requested_start_date = requested_end_date = dataset_end_date
        else:
            requested_start_date, requested_end_date = dataset_end_date - timedelta(days=6), dataset_end_date
        target_start_date = max(requested_start_date, dataset_start_date)
        target_end_date = min(requested_end_date, dataset_end_date)
        target_start, target_end = (
            align_scope_timestamp(value.isoformat(), active_frame["post_date"])
            for value in (target_start_date, target_end_date)
        )
        requested_start = datetime.combine(requested_start_date, datetime.min.time(), tzinfo=reference.tzinfo)
        requested_end = datetime.combine(requested_end_date, datetime.min.time(), tzinfo=reference.tzinfo)
        partial_period = target_start_date > requested_start_date or target_end_date < requested_end_date
        for index, (column, label) in enumerate(filter_columns.items()):
            options = sorted(active_frame[column].dropna().unique().tolist())
            filters[column] = st.multiselect(
                label,
                options,
                default=options,
                key="platform_filter" if index == 0 else f"filter_{column}",
            )

    if any(not selected for selected in filters.values()):
        st.warning("Filtro vazio: selecione ao menos um valor em cada dimensão. A fonte ativa foi preservada.")
    else:
        scope = {
            "filters": filters,
            "strict_audience": False,
            "method_version": METHOD_VERSION,
            "target_start": target_start.isoformat(),
            "target_end": target_end.isoformat(),
            "reference_date": reference.isoformat(),
            "period_mode": period_mode,
            "requested_start": requested_start.isoformat(),
            "requested_end": requested_end.isoformat(),
            "partial_period": partial_period,
        }
        analysis_key = (
            str(metadata["source_hash"]), METHOD_VERSION,
            json.dumps(scope, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
        )
        if st.session_state.get("analysis_key") == analysis_key and st.session_state.get("active_result") is not None:
            result = st.session_state["active_result"]
        else:
            result = analyze(active_frame, scope, str(metadata["source_hash"]))
            st.session_state["active_result"] = result
            st.session_state["analysis_key"] = analysis_key
        analysis_state = result["analysis_state"]
        has_observations = bool(analysis_state["has_observations"])
        metrics = result["metrics"]
        st.caption(
            f"Período selecionado: {result['scope']['target_start']} a {result['scope']['target_end']} · "
            f"referência {result['scope']['reference_date']} · método {METHOD_VERSION} · "
            f"cobertura {'parcial' if partial_period else 'completa'}"
        )
        if has_observations:
            columns = st.columns(3)
            columns[0].metric("Posts", _display_integer(metrics["posts"]))
            columns[1].metric("Visualizações", _display_integer(metrics["views"]))
            columns[2].metric("Interações", _display_integer(metrics["interactions"]))
        else:
            st.warning(str(analysis_state["message"]))

        financial_scenario = _render_financial_scenario(result, str(metadata["source_hash"]))

        for warning in result["quality"].get("warnings", []):
            st.warning(warning["message"])
        with st.expander("Qualidade, suficiência e cobertura"):
            quality = result["quality"]
            st.write("Colunas opcionais ausentes:", quality["optional_columns_missing"])
            st.write("Níveis de benchmark tentados:", quality["benchmark_levels_attempted"])
            st.caption("Cada comparador precisa de 30 taxas definidas e 5 creators elegíveis. Views=0 não fornece taxa.")
            diagnostics = quality.get("benchmark_diagnostics", [])
            st.write("Contextos sem benchmark suficiente:", _display_integer(len(diagnostics)))
            for diagnostic in diagnostics[:20]:
                st.json(diagnostic)
            if len(diagnostics) > 20:
                st.caption("Mostrando 20 contextos; todos os motivos estão no CSV de evidências.")
            sponsorship = result["sponsorship"]
            st.write("Patrocínio — estratos elegíveis / sem contraparte suficiente:", _display_integer(sponsorship["eligible_strata"]), "/", _display_integer(sponsorship["uncovered_count"]))
            st.write("Cobertura patrocinada:", sponsorship["coverage"])
            if sponsorship["uncovered_strata"]:
                st.dataframe(pd.DataFrame(sponsorship["uncovered_strata"]), hide_index=True, width="stretch")
            st.write("Audiência condicionada — cobertura e insuficiência:")
            st.caption("Controles: plataforma, formato, categoria, faixa, mês e patrocínio; rótulos de posts, não personas nem vencedores causais.")
            st.dataframe(pd.DataFrame([{key: item[key] for key in ("dimension", "status", "eligible_strata", "uncovered_count", "covered_posts", "coverage")} for item in result.get("audience", [])]), hide_index=True, width="stretch")

        if has_observations:
            st.subheader("Prioridades para decisão")
        priorities = (result["recommendations"] or result["pending"]) if has_observations else []
        all_recommendations = result.get("all_recommendations", result["recommendations"]) if has_observations else []
        for rank, item in enumerate(priorities[:3], start=1):
            title = item.get("action", item.get("reason", "Coletar evidência"))
            with st.container(border=True):
                st.markdown(f"**{rank}. {title}**")
                st.caption(f"Contexto — {_recommendation_context(item, literal=True)}")
                components = item.get("priority_components", {"impact": 0.0, "strength": 0.0, "recency": 0.0})
                component_columns = st.columns(3)
                for column, (label, key) in zip(component_columns, (("Impacto", "impact"), ("Força", "strength"), ("Atualidade", "recency")), strict=True):
                    column.number_input(label, value=float(components.get(key, 0.0)), format="%.6g", disabled=True, key=f"{label}-{item['evidence_id']}")
                st.caption(f"Evidência `{item['evidence_id']}` · prioridade {_display_number(item.get('priority', 0))}")
                evidence = _find_evidence(result, str(item["evidence_id"])) or {}
                with st.expander("Registros de origem e contexto"):
                    _render_evidence(evidence, item, result)

        additional_recommendations = all_recommendations[3:]
        if additional_recommendations:
            with st.expander(f"Outras ações elegíveis ({len(additional_recommendations)})"):
                st.caption("As três prioridades acima permanecem executivas; selecione outra ação para consultar a mesma evidência e decidir sem alterar filtros ou scores.")
                additional = st.selectbox(
                    "Ação adicional para detalhar",
                    additional_recommendations,
                    format_func=lambda item: f"{_recommendation_context(item)} — {item['action']} · {item['evidence_id']}",
                    key="additional_recommendation",
                )
                components = additional.get("priority_components", {"impact": 0.0, "strength": 0.0, "recency": 0.0})
                component_columns = st.columns(3)
                for column, (label, key) in zip(component_columns, (("Impacto", "impact"), ("Força", "strength"), ("Atualidade", "recency")), strict=True):
                    column.number_input(label, value=float(components.get(key, 0.0)), format="%.6g", disabled=True, key=f"additional-{label}-{additional['evidence_id']}")
                st.caption(f"Evidência `{additional['evidence_id']}` · prioridade {_display_number(additional.get('priority', 0))}")
                _render_evidence(_find_evidence(result, str(additional["evidence_id"])) or {}, additional, result)

        if has_observations:
            st.subheader("Ranking secundário")
        platform_rows = result["dimensions"].get("platform", []) if has_observations else []
        if platform_rows:
            st.dataframe(
                _table_numbers(pd.DataFrame(platform_rows)[
                    ["value", "posts", "creators", "views", "interactions", "median_erv"]
                ].rename(columns={"value": "plataforma", "median_erv": "mediana_erv"})),
                hide_index=True,
                width="stretch",
            )

        if all_recommendations:
            selected = st.selectbox(
                "Recomendação para decidir",
                all_recommendations,
                format_func=lambda item: f"{_recommendation_context(item)} — {item['action']} · {item['evidence_id']}",
                key="decision_recommendation",
            )
            with st.form("decision_form"):
                status = st.selectbox(
                    "Decisão",
                    ("accepted", "rejected", "edited"),
                    format_func={"accepted": "Aceitar", "rejected": "Rejeitar", "edited": "Editar"}.get,
                    key="decision_status",
                )
                edited_text = st.text_area("Texto editado (obrigatório se editar)", help="Usado somente quando a decisão é Editar; Aceitar ou Rejeitar preserva o texto original.", key="decision_text")
                submitted = st.form_submit_button("Registrar decisão", key="save_decision")
            if submitted:
                if status == "edited" and not edited_text.strip():
                    st.error("Informe o texto editado antes de registrar.")
                else:
                    event_id = st.session_state.setdefault("decision_event_id", str(uuid.uuid4()))
                    event = {
                        "event_id": event_id,
                        "recommendation_key": selected["recommendation_key"],
                        "revision_of": None,
                        "source_hash": metadata["source_hash"],
                        "decided_at": app_now().isoformat(),
                        "status": status,
                        "original_text": selected["action"],
                        "edited_text": edited_text.strip() if status == "edited" else "",
                        "owner": selected.get("owner", "Gestor de Social Media"),
                        "execution_window": selected.get("execution_window", "próximos 7 dias"),
                        "scope": result["scope"],
                        "baseline": _baseline(selected),
                        "method_version": METHOD_VERSION,
                    }
                    try:
                        decision_id = record_decision(connection, event)
                        confirmed = next(item for item in list_decisions(connection) if item["decision_id"] == decision_id)
                    except (sqlite3.Error, StopIteration, ValueError) as exc:
                        st.error(f"A decisão não foi salva: {exc}")
                    else:
                        st.success(f"Decisão registrada: {confirmed['decision_id']}")
                        st.session_state["decision_event_id"] = str(uuid.uuid4())
                        decisions = list_decisions(connection)

        eligible_outcomes = [item for item in decisions if item["source_hash"] != metadata["source_hash"]] if has_observations else []
        if eligible_outcomes:
            st.subheader("Observação posterior")
            st.caption("A observação usa o segmento e a estatística salvos na decisão; somente a janela vem da análise ativa. Outros filtros atuais não redefinem o baseline.")
            outcome_decision = st.selectbox(
                "Decisão de referência",
                eligible_outcomes,
                format_func=lambda item: f"{item['decision_id']} — {item['status']}",
                key="outcome_decision",
            )
            with st.form("outcome_form"):
                execution_status = st.selectbox(
                    "A ação foi executada?",
                    ("unknown", "yes", "no"),
                    format_func={"unknown": "Não informado", "yes": "Sim", "no": "Não"}.get,
                    key="execution_status",
                )
                execution_date = st.date_input("Data declarada de execução", value=None, key="execution_date")
                outcome_submitted = st.form_submit_button("Registrar observação", key="save_outcome")
            if outcome_submitted:
                event_id = st.session_state.setdefault("outcome_event_id", str(uuid.uuid4()))
                observed = observe_evidence(active_frame, outcome_decision["baseline"], result["scope"], str(metadata["source_hash"]))
                event = {
                    "event_id": event_id,
                    "decision_id": outcome_decision["decision_id"],
                    "source_hash": metadata["source_hash"],
                    "recorded_at": app_now().isoformat(),
                    "execution_status": execution_status,
                    "execution_date": execution_date.isoformat() if execution_date else None,
                    "scope": observed["scope"] or outcome_decision["scope"],
                    "observed": observed,
                    "method_version": METHOD_VERSION,
                }
                try:
                    outcome_id = record_outcome(connection, event, clock=app_now, simulation=simulation)
                    refreshed = list_decisions(connection)
                    confirmed = next(
                        outcome
                        for decision in refreshed
                        for outcome in decision["outcomes"]
                        if outcome["outcome_id"] == outcome_id
                    )
                except (sqlite3.Error, StopIteration, ValueError) as exc:
                    st.error(f"A observação não foi salva: {exc}")
                else:
                    st.success(f"Observação registrada: {confirmed['status']} — {confirmed['reason']}")
                    st.session_state["outcome_event_id"] = str(uuid.uuid4())
                    decisions = refreshed

st.subheader("Histórico de decisões")
if not decisions:
    st.caption("Nenhuma decisão registrada.")
else:
    with st.expander("Revisar decisão existente"):
        original = st.selectbox("Decisão para revisar", decisions, format_func=lambda item: f"{item['decision_id']} — {item['status']}", key="revision_decision")
        with st.form("revision_form"):
            revision_status = st.selectbox("Nova decisão", ("accepted", "rejected", "edited"), format_func={"accepted": "Aceitar", "rejected": "Rejeitar", "edited": "Editar"}.get, key="revision_status")
            revision_text = st.text_area("Texto da revisão (obrigatório se editar)", help="Usado somente quando a nova decisão é Editar; Aceitar ou Rejeitar preserva o texto original.", key="revision_text")
            revision_submitted = st.form_submit_button("Registrar revisão", key="save_revision")
        if revision_submitted:
            if revision_status == "edited" and not revision_text.strip():
                st.error("Informe o texto da revisão antes de registrar.")
            else:
                event = {**original, "event_id": st.session_state.setdefault("revision_event_id", str(uuid.uuid4())), "revision_of": original["decision_id"], "decided_at": app_now().isoformat(), "status": revision_status, "edited_text": revision_text.strip() if revision_status == "edited" else ""}
                try:
                    revision_id = record_decision(connection, event)
                    decisions = list_decisions(connection)
                    confirmed = next(item for item in decisions if item["decision_id"] == revision_id)
                except (sqlite3.Error, StopIteration, ValueError) as exc:
                    st.error(f"A revisão não foi salva: {exc}")
                else:
                    st.success(f"Revisão registrada: {confirmed['decision_id']}")
                    st.session_state["revision_event_id"] = str(uuid.uuid4())
    active_hash = str(metadata["source_hash"]) if metadata else None
    for item in reversed(decisions):
        text = item["edited_text"] if item["status"] == "edited" else item["original_text"]
        st.markdown(f"**{item['status']}** · {text}")
        st.caption(f"{item['decided_at']} · fonte `{str(item['source_hash'])[:12]}…` · decisão `{item['decision_id']}`")
        if item["revision_of"]:
            st.caption(f"Revisão da decisão `{item['revision_of']}`; baseline original preservado.")
        with st.expander(f"Evidência histórica salva — {item['decision_id']}"):
            baseline = item["baseline"]
            snapshot = baseline.get("evidence_snapshot")
            st.write("Escopo original da decisão (independente dos filtros ativos):")
            st.json(item["scope"])
            st.write("Snapshot persistido — alvo, comparador e definição estatística:")
            st.json(snapshot or baseline)
            if baseline.get("simulation"):
                st.warning("SIMULAÇÃO / REPLAY RETROSPECTIVO — decisão em fixture; não é resultado de produção.")
            if item["method_version"] != METHOD_VERSION:
                st.warning("Método histórico incompatível com novas comparações; snapshot preservado, outcome ficará pendente.")
            if snapshot and item["source_hash"] == active_hash:
                references = [{"papel": role, "source_row_id": source_id} for role, ids in snapshot["references"].items() for source_id in ids]
                reference_frame = pd.DataFrame(references)
                resolved = reference_frame.merge(active_frame[["source_row_id", "source_line", "post_date", "platform", "content_category"]], on="source_row_id", how="left", validate="many_to_one")
                st.write("Referências verificadas no CSV histórico — escopo salvo:", _display_integer(len(resolved)))
                st.dataframe(resolved, hide_index=True, width="stretch")
            elif item["source_hash"] != active_hash:
                st.caption("Snapshot disponível acima. Reenvie o CSV com este hash para verificar as referências históricas, mesmo fora da fila atual.")
            elif not snapshot:
                st.caption("Registro legado sem snapshot completo; baseline original preservado sem inventar comparador.")
        if not item["outcomes"]:
            st.caption("Resultado pendente: nenhuma observação posterior comparável registrada.")
        for outcome in item["outcomes"]:
            observed, comparison = outcome["observed"], outcome["comparison"]
            if observed.get("simulation"):
                st.warning("SIMULAÇÃO / REPLAY RETROSPECTIVO — observação de fixture, não resultado de produção.")
            st.markdown(f"**Observação {outcome['status']}** · motivo: `{outcome['reason']}`")
            st.caption(f"Execução declarada: {outcome['execution_status']} · data: {outcome['execution_date'] or 'não informada'} · registro: {outcome['recorded_at']}")
            st.write(f"Janela observada: {observed['period_start']} a {observed['period_end']} · cobertura: {_display_integer(observed['coverage_days'])} dias")
            st.write("Comparação ERv (%) — mediana baseline / observada / delta (p.p.):", comparison["baseline_median"], "/", comparison["observed_median"], "/", comparison["median_delta"])
            st.write("Visualizações por dia — baseline / observada:", comparison["baseline_volume_per_day"], "/", comparison["observed_volume_per_day"])
            st.caption("Observação não causal: diferença descritiva; pendência não comprova resultado da ação.")

if result is not None and result["analysis_state"]["has_observations"]:
    decision_rows = _decision_export(decisions)
    st.download_button("Baixar resumo executivo (HTML)", executive_summary(result, decision_rows, financial_scenario).encode("utf-8"), file_name="resumo-executivo.html", mime="text/html")
    st.download_button("Baixar evidências e decisões (CSV)", export_evidence(result, decision_rows), file_name="evidencias-decisoes.csv", mime="text/csv")

connection.close()
