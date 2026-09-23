from __future__ import annotations

import json
import os
import platform
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .config import (
    DEFAULT_CUTOFFS,
    DEFAULT_WINDOWS,
    MIN_COVERAGE,
    MIN_SEGMENT_ACCOUNTS,
    MIN_SEGMENT_CHURNS,
    OBSERVATION_END,
    RAW_FILE_SHA256,
    SCORING_CUTOFF,
    sha256_file,
)
from .diagnosis import CANDIDATES, rank_findings

CLAIM_LABELS = {
    "C-usage-growth": "Uso da plataforma (C-usage-growth)",
    "C-satisfaction-ok": "Satisfação dos clientes (C-satisfaction-ok)",
}
COHORT_LABELS = {"overall": "Todas as contas", "churn_next_30d": "Churn em até 30 dias"}
STATUS_LABELS = {
    "up": "Aumentou",
    "down": "Caiu",
    "concern": "Exige atenção",
    "ok": "Adequada",
}
FINDING_LABELS = {
    "F-product-usage-drop": "Queda de uso",
    "F-product-errors": "Erros de produto",
    "F-support-escalation": "Escalações de suporte",
    "F-support-satisfaction": "Baixa satisfação",
    "F-commercial-downgrade": "Downgrade comercial",
    "F-commercial-renewal": "Renovação automática desligada",
}
FAILURE_LABELS = {
    "association_gate": "Associação insuficiente",
    "chronology_instability": "Instável entre cronologias",
    "sample_or_coverage_gate": "Amostra ou cobertura insuficiente",
    "cross_table_gate": "Sem confirmação entre tabelas",
    "model_failure:LinAlgError": "Modelo estatístico instável",
    "model_failure:ValueError": "Modelo estatístico inválido",
}
QUALITY_LABELS = {
    "usage_before_subscription": "Usos anteriores à assinatura",
    "usage_before_signup": "Usos anteriores ao cadastro",
    "tickets_before_signup": "Tickets anteriores ao cadastro",
    "accounts_flag_vs_terminal_event": "Flags de conta divergentes do evento",
    "usage_after_subscription": "Usos posteriores ao fim da assinatura",
    "subscription_accounts_flag_vs_terminal_event": "Flags de assinatura divergentes por conta",
    "duplicate_usage_id_groups": "Grupos de IDs de uso duplicados",
}
DIMENSION_LABELS = {
    "industry": "Indústria",
    "country": "País",
    "referral_source": "Origem",
    "plan_tier": "Plano",
    "billing_frequency": "Cobrança",
    "is_trial": "Trial",
    "mrr_band": "Faixa de MRR",
}
ELIGIBILITY_LABELS = {"eligible": "Elegível", "inconclusive": "Inconclusivo"}
MRR_BAND_LABELS = {"low": "Baixo", "mid": "Médio", "high": "Alto"}
SEGMENT_LABELS = {
    **MRR_BAND_LABELS,
    "mixed": "Misto",
    "annual": "Anual",
    "monthly": "Mensal",
    "True": "Sim",
    "False": "Não",
    "ads": "Anúncios",
    "event": "Eventos",
    "organic": "Orgânico",
    "other": "Outros",
    "partner": "Parceiros",
}
EVIDENCE_LEVEL_LABELS = {
    "confirmed_fact": "Fato confirmado",
    "supported_mechanism": "Mecanismo sustentado",
    "plausible_hypothesis": "Hipótese plausível",
    "inconclusive": "Evidência inconclusiva",
}
EVIDENCE_CONFIDENCE_LABELS = {
    "confirmed_fact": "Alta confiança",
    "supported_mechanism": "Moderada confiança",
    "plausible_hypothesis": "Baixa confiança",
    "inconclusive": "Baixa confiança",
}


class ArtifactConsistencyError(ValueError):
    pass


@dataclass(frozen=True)
class AnalysisResult:
    quality_report: dict[str, Any]
    panel: pd.DataFrame
    claim_checks: pd.DataFrame
    findings: pd.DataFrame
    segment_metrics: pd.DataFrame
    monthly_churn: pd.DataFrame
    reason_distribution: pd.DataFrame
    event_cohort_metrics: pd.DataFrame
    mechanism_scorecard: pd.DataFrame
    model_evaluation: dict[str, Any]
    model_scores: pd.DataFrame | None = None


QUEUE_COLUMNS = (
    "account_id",
    "priority",
    "finding_id",
    "mrr_exposed_max",
    "plan_tier",
    "mrr_band",
    "risk_probability",
    "signals",
    "immediate_action",
    "structural_action",
    "owner",
    "status",
)
EXPECTED_ARTIFACT_FILENAMES = {
    "account_panel.csv",
    "account_queue.csv",
    "account_watchlist.csv",
    "claim_checks.csv",
    "ceo_answer.json",
    "event_cohort_metrics.csv",
    "findings.csv",
    "mechanism_scorecard.csv",
    "model_evaluation.json",
    "monthly_churn.csv",
    "quality_report.json",
    "reason_distribution.csv",
    "report.md",
    "segment_metrics.csv",
}
REQUIRED_EVIDENCE_COLUMNS = {
    "monthly_churn.csv": {
        "evidence_id",
        "period_start",
        "period_end",
        "population",
        "status",
        "period_kind",
        "dimension",
        "segment",
        "churn_rate",
    },
    "reason_distribution.csv": {
        "evidence_id",
        "period_start",
        "period_end",
        "population",
        "reason_code",
        "eligible_events",
        "share",
    },
    "event_cohort_metrics.csv": {
        "evidence_id",
        "period_start",
        "period_end",
        "population",
        "chronology",
        "metric",
        "cohort",
        "relative_window_start",
        "relative_window_end",
        "value",
    },
    "mechanism_scorecard.csv": {
        "evidence_id",
        "period_start",
        "period_end",
        "population",
        "status",
        "mechanism_id",
        "finding_id",
        "evidence_level",
        "temporal_support",
        "comparison_support",
        "sample_support",
        "association_support",
        "chronology_support",
        "cross_table_support",
    },
}


def _mrr_band(value: float) -> str:
    if value <= 500:
        return "low"
    if value <= 2_000:
        return "mid"
    return "high"


def _translated_signals(value: str) -> str:
    return ", ".join(FINDING_LABELS.get(signal, signal) for signal in value.split("|"))


def _json_default(value: object) -> object:
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    if isinstance(value, (np.ndarray, pd.Series)):
        return value.tolist()
    if pd.isna(value):
        return None
    raise TypeError(f"cannot serialize {type(value).__name__}")


def _json_ready(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, np.ndarray, pd.Series)):
        return [_json_ready(item) for item in value]
    if isinstance(value, (np.integer, np.floating)):
        value = value.item()
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    if value is pd.NA or value is pd.NaT:
        return None
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def _json_text(value: object) -> str:
    return json.dumps(
        _json_ready(value),
        default=_json_default,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
        allow_nan=False,
    )


def _accepted_findings(findings: pd.DataFrame) -> pd.DataFrame:
    return rank_findings(findings).loc[lambda frame: frame["confidence"].eq("accepted")]


def _exposed(values: pd.Series, operator: str, threshold: object) -> pd.Series:
    return {
        "le": values.le(threshold),
        "ge": values.ge(threshold),
        "eq": values.eq(threshold),
    }[operator].fillna(False)


def _scoring_accounts(panel: pd.DataFrame) -> pd.DataFrame:
    scoring = panel.loc[
        panel["cutoff"].eq(SCORING_CUTOFF) & panel["chronology"].eq("strict")
    ].copy()
    if "has_active_subscription" in scoring:
        scoring = scoring.loc[scoring["has_active_subscription"].fillna(False)]
    return scoring


def _build_queue(result: AnalysisResult) -> pd.DataFrame:
    accepted = _accepted_findings(result.findings)
    scoring = _scoring_accounts(result.panel)
    rows: list[dict[str, object]] = []
    for finding in accepted.itertuples(index=False):
        feature, _, _, operator, threshold = CANDIDATES[finding.finding_id]
        values = scoring[feature]
        exposed = _exposed(values, operator, threshold)
        for account in scoring.loc[exposed].itertuples(index=False):
            rows.append(
                {
                    "account_id": account.account_id,
                    "priority": finding.priority_rank,
                    "finding_id": finding.finding_id,
                    "mrr_exposed_max": account.mrr_active,
                    "plan_tier": getattr(account, "plan_tier", "n/d"),
                    "mrr_band": _mrr_band(float(account.mrr_active)),
                    "risk_probability": np.nan,
                    "signals": f"{feature}={getattr(account, feature)}",
                    "immediate_action": finding.immediate_action,
                    "structural_action": finding.structural_action,
                    "owner": finding.owner,
                    "status": "",
                }
            )
    queue = pd.DataFrame(rows, columns=QUEUE_COLUMNS)
    if queue.empty:
        return queue
    if result.model_scores is not None and result.model_evaluation.get("publish_model"):
        queue = queue.drop(columns="risk_probability").merge(
            result.model_scores[["account_id", "risk_probability"]],
            on="account_id",
            how="left",
            validate="many_to_one",
        )
    return (
        queue.sort_values(
            ["priority", "mrr_exposed_max", "risk_probability", "account_id"],
            ascending=[True, False, False, True],
            na_position="last",
        )
        .drop_duplicates("account_id")
        .loc[:, QUEUE_COLUMNS]
        .reset_index(drop=True)
    )


def _build_watchlist(result: AnalysisResult) -> pd.DataFrame:
    scoring = _scoring_accounts(result.panel)
    signal_map: dict[str, list[str]] = {str(account_id): [] for account_id in scoring.account_id}
    for finding_id, (feature, _, _, operator, threshold) in CANDIDATES.items():
        if feature not in scoring:
            continue
        exposed_accounts = scoring.loc[
            _exposed(scoring[feature], operator, threshold), "account_id"
        ]
        for account_id in exposed_accounts:
            signal_map[str(account_id)].append(finding_id)

    rows = []
    for account in scoring.itertuples(index=False):
        signals = signal_map[str(account.account_id)]
        if not signals:
            continue
        mrr = float(account.mrr_active)
        rows.append(
            {
                "account_id": account.account_id,
                "signal_count": len(signals),
                "mrr_exposed_max": mrr,
                "plan_tier": getattr(account, "plan_tier", "n/d"),
                "mrr_band": _mrr_band(mrr),
                "signals": "|".join(signals),
                "status": "validation_only",
            }
        )
    columns = (
        "account_id",
        "validation_rank",
        "signal_count",
        "mrr_exposed_max",
        "plan_tier",
        "mrr_band",
        "signals",
        "status",
    )
    if not rows:
        return pd.DataFrame(columns=columns)
    watchlist = pd.DataFrame(rows).sort_values(
        ["signal_count", "mrr_exposed_max", "account_id"], ascending=[False, False, True]
    )
    watchlist.insert(1, "validation_rank", range(1, len(watchlist) + 1))
    return watchlist.loc[:, columns].reset_index(drop=True)


def _manifest_parameters(result: AnalysisResult) -> dict[str, object]:
    return {
        "chronology_modes": ["observed", "strict"],
        "cutoffs": [str(DEFAULT_CUTOFFS.min().date()), str(DEFAULT_CUTOFFS.max().date())],
        "scoring_cutoff": str(SCORING_CUTOFF.date()),
        "windows_days": list(DEFAULT_WINDOWS),
        "min_segment_accounts": MIN_SEGMENT_ACCOUNTS,
        "min_segment_churns": MIN_SEGMENT_CHURNS,
        "min_coverage": MIN_COVERAGE,
        "observation_end": str(OBSERVATION_END.date()),
        "label_policy": result.quality_report.get("label_policy"),
    }


def _analysis_payloads(
    result: AnalysisResult, queue: pd.DataFrame, watchlist: pd.DataFrame
) -> dict[str, object]:
    return {
        "account_panel.csv": result.panel,
        "account_queue.csv": queue,
        "account_watchlist.csv": watchlist,
        "claim_checks.csv": result.claim_checks,
        "findings.csv": rank_findings(result.findings),
        "segment_metrics.csv": result.segment_metrics,
        "monthly_churn.csv": result.monthly_churn,
        "reason_distribution.csv": result.reason_distribution,
        "event_cohort_metrics.csv": result.event_cohort_metrics,
        "mechanism_scorecard.csv": result.mechanism_scorecard,
        "quality_report.json": result.quality_report,
        "model_evaluation.json": result.model_evaluation,
    }


def _payload_bytes(filename: str, payload: object) -> bytes:
    if filename.endswith(".csv"):
        return payload.to_csv(index=False, lineterminator="\n").encode("utf-8")  # type: ignore[union-attr]
    return (_json_text(payload) + "\n").encode("utf-8")


def _analysis_id(result: AnalysisResult, queue: pd.DataFrame, watchlist: pd.DataFrame) -> str:
    evidence_checksums = {
        filename: sha256(_payload_bytes(filename, payload)).hexdigest()
        for filename, payload in _analysis_payloads(result, queue, watchlist).items()
    }
    identity = {
        "input_checksums": RAW_FILE_SHA256,
        "parameters": _manifest_parameters(result),
        "evidence_checksums": evidence_checksums,
    }
    canonical = json.dumps(_json_ready(identity), sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def _iso_date(value: object) -> str | None:
    if pd.isna(value):
        return None
    return str(pd.Timestamp(value).date())


def _stable_number(value: object) -> object:
    if isinstance(value, (np.integer, np.floating)):
        value = value.item()
    if isinstance(value, float) and np.isfinite(value):
        return round(value, 15)
    return value


def _claim(
    claim_id: str,
    statement: str,
    evidence_level: str | None,
    status: str,
    value: object,
    unit: str,
    population: str,
    period_start: object,
    period_end: object,
    evidence_ids: list[str],
    limitation: str,
    *,
    numerator: object = None,
    denominator: object = None,
    comparator_id: str | None = None,
    uncertainty_method: str = "not_estimated",
    uncertainty_level: object = None,
    uncertainty_low: object = None,
    uncertainty_high: object = None,
    uncertainty_reason: str | None = None,
    counterevidence: str | None = None,
) -> dict[str, object]:
    return {
        "id": claim_id,
        "statement": statement,
        "evidence_level": evidence_level,
        "confidence_label": EVIDENCE_CONFIDENCE_LABELS.get(str(evidence_level), "Baixa confiança"),
        "status": status,
        "value": _stable_number(value),
        "unit": unit,
        "numerator": _stable_number(numerator),
        "denominator": _stable_number(denominator),
        "population": population,
        "period_start": _iso_date(period_start),
        "period_end": _iso_date(period_end),
        "comparator_id": comparator_id,
        "uncertainty": {
            "method": uncertainty_method,
            "level": _stable_number(uncertainty_level),
            "low": _stable_number(uncertainty_low),
            "high": _stable_number(uncertainty_high),
            "reason": uncertainty_reason,
        },
        "evidence_ids": evidence_ids,
        "limitation": limitation,
        "counterevidence": counterevidence,
    }


def _build_ceo_answer(result: AnalysisResult) -> dict[str, object]:
    queue = _build_queue(result)
    watchlist = _build_watchlist(result)
    analysis_id = _analysis_id(result, queue, watchlist)
    evidence_refs: dict[str, dict[str, object]] = {}

    def add_ref(
        ref_id: str,
        artifact: str,
        row: pd.Series,
        key_columns: tuple[str, ...],
        columns: tuple[str, ...],
    ) -> str:
        evidence_refs[ref_id] = {
            "artifact": artifact,
            "row_key": {column: _json_ready(row[column]) for column in key_columns},
            "columns": list(columns),
            "calculation": row.get("calculation", "published_table"),
            "source_tables": str(row.get("source_refs", artifact)).split("|"),
            "period_start": _iso_date(row.get("period_start", row.get("cutoff_start"))),
            "period_end": _iso_date(row.get("period_end", row.get("cutoff_end"))),
            "population": str(row.get("population", "declared_population")),
            "unit": str(row.get("rate_unit", row.get("unit", "declared_unit"))),
        }
        return ref_id

    blocks: dict[str, dict[str, object]] = {
        block_id: {"id": block_id, "title": title, "summary": summary, "claims": [], "actions": []}
        for block_id, title, summary in (
            ("what_changed", "O que mudou", "Mudança de churn no recorte histórico declarado."),
            ("where", "Onde está concentrado", "Recortes descritivos, sem inferir causalidade."),
            (
                "strongest_mechanism",
                "Mecanismo mais forte",
                "Gates de evidência antes da prioridade.",
            ),
            (
                "unknowns",
                "O que ainda não sabemos",
                "Cobertura e contradições limitam a conclusão.",
            ),
            ("next_actions", "Próximas ações", "Ações proporcionais à força da evidência."),
        )
    }
    evidence_refs["quality:report"] = {
        "artifact": "quality_report.json",
        "row_key": {"scope": "quality_report"},
        "columns": ["rows", "contradictions"],
        "calculation": "build_quality_report",
        "source_tables": sorted(result.quality_report.get("rows", {})),
        "period_start": None,
        "period_end": str(OBSERVATION_END.date()),
        "population": "all_input_rows",
        "unit": "data_quality_rules",
    }

    history = result.monthly_churn
    overall = history.loc[
        history.get("period_kind", pd.Series(index=history.index, dtype=str)).eq(
            "comparison_period"
        )
        & history.get("dimension", pd.Series(index=history.index, dtype=str)).eq("all")
        & history.get("segment", pd.Series(index=history.index, dtype=str)).eq("all")
    ]
    if not overall.empty:
        recent = overall.sort_values("period_end").iloc[-1]
        reference = overall.sort_values("period_end").iloc[0]
        recent_ref = add_ref(
            str(recent["evidence_id"]),
            "monthly_churn.csv",
            recent,
            ("evidence_id",),
            ("churn_rate", "rate_difference", "mrr_lost", "at_risk_accounts"),
        )
        reference_ref = add_ref(
            str(reference["evidence_id"]),
            "monthly_churn.csv",
            reference,
            ("evidence_id",),
            ("churn_rate", "terminal_churns", "at_risk_accounts"),
        )
        difference = recent.get("rate_difference")
        if pd.isna(difference):
            difference = recent.get("churn_rate") - reference.get("churn_rate")
        status = "up" if difference > 0 else "down" if difference < 0 else "flat"
        statement = (
            f"A taxa mensal ponderada de churn ficou em {recent['churn_rate']:.1%} no período "
            f"recente, variação de {difference * 100:+.1f} pp versus a referência."
        )
        blocks["what_changed"]["claims"].append(
            _claim(
                "C-churn-change",
                statement,
                "confirmed_fact",
                status,
                difference,
                "percentage_points_fraction",
                str(recent.get("population", "registered_at_start")),
                recent.get("period_start"),
                recent.get("period_end"),
                [recent_ref, reference_ref],
                "Taxa de período ponderada por exposições conta-mês; não é probabilidade semestral.",
                numerator=recent.get("terminal_churns"),
                denominator=recent.get("at_risk_accounts"),
                uncertainty_method=str(recent.get("ci_method", "cluster_bootstrap_account")),
                uncertainty_level=recent.get("ci_level"),
                uncertainty_low=recent.get("difference_ci_low"),
                uncertainty_high=recent.get("difference_ci_high"),
            )
        )
        formatted_mrr = f"{recent['mrr_lost']:,.0f}".replace(",", ".")
        impact_statement = (
            f"O MRR perdido observado no período recente foi US$ {formatted_mrr}; "
            "é impacto associado aos churns, não receita automaticamente recuperável."
        )
        blocks["what_changed"]["claims"].append(
            _claim(
                "C-churn-impact",
                impact_statement,
                "confirmed_fact",
                "observed",
                recent.get("mrr_lost"),
                "monthly_recurring_revenue",
                str(recent.get("population", "registered_at_start")),
                recent.get("period_start"),
                recent.get("period_end"),
                [recent_ref],
                "Soma do MRR conhecido nos eventos terminais; não estima receita recuperável.",
            )
        )
        blocks["what_changed"]["summary"] = f"{statement} {impact_statement}"

    usage = result.claim_checks.loc[result.claim_checks["claim_id"].eq("C-usage-growth")]
    usage_overall = usage.loc[usage["cohort"].eq("overall")]
    usage_churn = usage.loc[usage["cohort"].eq("churn_next_30d")]
    if (
        not usage_overall.empty
        and not usage_churn.empty
        and usage_overall.iloc[0][["start_value", "end_value"]].notna().all()
        and usage_churn.iloc[0][["start_value", "end_value"]].notna().all()
    ):
        overall_row = usage_overall.iloc[0]
        churn_row = usage_churn.iloc[0]
        overall_ref = add_ref(
            "claim:C-usage-growth:overall",
            "claim_checks.csv",
            overall_row,
            ("claim_id", "cohort"),
            ("start_value", "end_value", "coverage", "status"),
        )
        churn_ref = add_ref(
            "claim:C-usage-growth:churn_next_30d",
            "claim_checks.csv",
            churn_row,
            ("claim_id", "cohort"),
            ("start_value", "end_value", "coverage", "status"),
        )
        trend_label = {
            "up": "cresceu",
            "down": "caiu",
            "flat": "ficou estável",
            "insufficient": "não pôde ser concluído",
        }
        overall_trend = trend_label.get(str(overall_row["status"]), "variou")
        churn_trend = trend_label.get(str(churn_row["status"]), "variou")
        connector = "mas" if overall_trend != churn_trend else "e também"
        usage_statement = (
            f"O uso {overall_trend} no agregado "
            f"({overall_row['start_value']:.3f}→{overall_row['end_value']:.3f}), {connector} "
            f"{churn_trend} entre as contas que churnariam em 30 dias "
            f"({churn_row['start_value']:.3f}→{churn_row['end_value']:.3f})."
        )
        blocks["what_changed"]["claims"].extend(
            [
                _claim(
                    "C-usage-overall",
                    (
                        "Uso diário por conta no agregado: "
                        f"{overall_row['start_value']:.3f}→{overall_row['end_value']:.3f}."
                    ),
                    "confirmed_fact",
                    str(overall_row["status"]),
                    overall_row["end_value"] - overall_row["start_value"],
                    "usage_events/account/day",
                    "accounts_with_usage_coverage",
                    overall_row.get("cutoff_start"),
                    overall_row.get("cutoff_end"),
                    [overall_ref],
                    str(overall_row["limitation"]),
                ),
                _claim(
                    "C-usage-churn-next-30d",
                    (
                        "Uso diário por conta entre futuros churners de 30 dias: "
                        f"{churn_row['start_value']:.3f}→{churn_row['end_value']:.3f}."
                    ),
                    "confirmed_fact",
                    str(churn_row["status"]),
                    churn_row["end_value"] - churn_row["start_value"],
                    "usage_events/account/day",
                    "retrospective_churn_next_30d",
                    churn_row.get("cutoff_start"),
                    churn_row.get("cutoff_end"),
                    [churn_ref],
                    "Coorte retrospectiva; descreve seleção, não causa.",
                ),
            ]
        )
        blocks["what_changed"]["summary"] = f"{blocks['what_changed']['summary']} {usage_statement}"

    eligible = result.segment_metrics.loc[
        result.segment_metrics.get(
            "confidence", pd.Series("inconclusive", index=result.segment_metrics.index)
        ).eq("eligible")
    ]
    if not eligible.empty:
        top_segment = eligible.sort_values("relative_risk", ascending=False).iloc[0]
        segment_ref = add_ref(
            f"segment:{top_segment['dimension']}:{top_segment['segment']}",
            "segment_metrics.csv",
            top_segment,
            ("dimension", "segment"),
            ("churn_rate", "relative_risk", "mrr_lost", "confidence"),
        )
        segment_statement = (
            f"{top_segment['dimension']} / {top_segment['segment']} teve risco relativo "
            f"descritivo de {top_segment['relative_risk']:.2f}x."
        )
        blocks["where"]["claims"].append(
            _claim(
                "C-top-segment",
                segment_statement,
                "confirmed_fact",
                "descriptive",
                top_segment.get("relative_risk"),
                "relative_risk",
                "diagnostic_snapshot",
                SCORING_CUTOFF - pd.Timedelta(days=31),
                SCORING_CUTOFF - pd.Timedelta(days=1),
                [segment_ref],
                "Ranking descritivo restrito aos segmentos que passaram os limiares de amostra.",
            )
        )
        blocks["where"]["summary"] = (
            "Não há concentração material demonstrada: o maior recorte elegível tem "
            f"RR {top_segment['relative_risk']:.2f}×, abaixo do limiar descritivo de 1,25×."
            if top_segment["relative_risk"] < 1.25
            else segment_statement
        )

    scorecard = result.mechanism_scorecard
    supported = scorecard.loc[
        scorecard.get("evidence_level", pd.Series(dtype=str)).eq("supported_mechanism")
    ]
    selected_mechanism_id = None
    if len(supported) == 1:
        mechanism_status = "supported"
        selected_mechanism_id = str(supported.iloc[0]["mechanism_id"])
    elif len(supported) > 1:
        mechanism_status = "tied"
    else:
        mechanism_status = "inconclusive" if not scorecard.empty else "unavailable"
    mechanism = supported.iloc[0] if len(supported) == 1 else None
    if mechanism_status in {"inconclusive", "unavailable"}:
        blocks["strongest_mechanism"].update(
            {
                "title": "Causa ainda não demonstrada",
                "summary": "Nenhuma hipótese passou todos os gates; não há causa identificada.",
            }
        )
    elif mechanism_status == "tied":
        blocks["strongest_mechanism"].update(
            {
                "title": "Mecanismos sustentados empatados",
                "summary": "Há mais de um mecanismo sustentado; nenhum foi eleito isoladamente.",
            }
        )
    mechanism_ref = None
    if mechanism is not None:
        mechanism_ref = add_ref(
            str(mechanism["evidence_id"]),
            "mechanism_scorecard.csv",
            mechanism,
            ("evidence_id",),
            (
                "evidence_level",
                "temporal_support",
                "comparison_support",
                "sample_support",
                "association_support",
                "chronology_support",
                "cross_table_support",
            ),
        )
        evidence_label = EVIDENCE_LEVEL_LABELS.get(
            str(mechanism["evidence_level"]), "Evidência inconclusiva"
        )
        mechanism_statement = f"{mechanism['claim']} Estado: {evidence_label}."
        blocks["strongest_mechanism"]["claims"].append(
            _claim(
                "M-strongest",
                mechanism_statement,
                str(mechanism.get("evidence_level")),
                str(mechanism.get("status", "inconclusive")),
                mechanism.get("effect"),
                str(mechanism.get("effect_unit", "adjusted_odds_ratio")),
                str(mechanism.get("population", "diagnostic_horizon")),
                mechanism.get("period_start"),
                mechanism.get("period_end"),
                [mechanism_ref],
                str(
                    mechanism.get(
                        "limitation", "Associação observacional; causalidade não identificada."
                    )
                ),
                uncertainty_method=str(mechanism.get("ci_method", "glm_hc3")),
                uncertainty_level=mechanism.get("ci_level"),
                uncertainty_low=mechanism.get("ci_low"),
                uncertainty_high=mechanism.get("ci_high"),
                counterevidence=mechanism.get("counterevidence"),
            )
        )
        blocks["strongest_mechanism"]["summary"] = mechanism_statement

    satisfaction = result.claim_checks.loc[result.claim_checks["claim_id"].eq("C-satisfaction-ok")]
    satisfaction_overall = satisfaction.loc[satisfaction["cohort"].eq("overall")]
    satisfaction_churn = satisfaction.loc[satisfaction["cohort"].eq("churn_next_30d")]
    unknown_ref = None
    if (
        not satisfaction_overall.empty
        and not satisfaction_churn.empty
        and satisfaction_overall.iloc[0][["start_value", "end_value"]].notna().all()
        and satisfaction_churn.iloc[0][["start_value", "end_value"]].notna().all()
    ):
        satisfaction_row = satisfaction_overall.iloc[0]
        satisfaction_churn_row = satisfaction_churn.iloc[0]
        unknown_ref = add_ref(
            "claim:C-satisfaction-ok:overall",
            "claim_checks.csv",
            satisfaction_row,
            ("claim_id", "cohort"),
            ("start_value", "end_value", "coverage", "status"),
        )
        satisfaction_churn_ref = add_ref(
            "claim:C-satisfaction-ok:churn_next_30d",
            "claim_checks.csv",
            satisfaction_churn_row,
            ("claim_id", "cohort"),
            ("start_value", "end_value", "coverage", "status"),
        )
        satisfaction_overall_trend = (
            "subiu"
            if satisfaction_row["end_value"] > satisfaction_row["start_value"]
            else "caiu"
            if satisfaction_row["end_value"] < satisfaction_row["start_value"]
            else "ficou estável"
        )
        satisfaction_churn_trend = (
            "subiu"
            if satisfaction_churn_row["end_value"] > satisfaction_churn_row["start_value"]
            else "caiu"
            if satisfaction_churn_row["end_value"] < satisfaction_churn_row["start_value"]
            else "ficou estável"
        )
        unknown_statement = (
            f"A satisfação geral dos respondentes {satisfaction_overall_trend} de "
            f"{satisfaction_row['start_value']:.2f}→{satisfaction_row['end_value']:.2f} "
            f"(cobertura {satisfaction_row['coverage']:.1%}); entre "
            f"futuros churners, {satisfaction_churn_trend} de "
            f"{satisfaction_churn_row['start_value']:.2f}→{satisfaction_churn_row['end_value']:.2f} "
            f"(cobertura {satisfaction_churn_row['coverage']:.1%}). "
            "São apenas tickets respondidos; não representam toda a base."
        )
        blocks["unknowns"]["claims"].extend(
            [
                _claim(
                    "C-satisfaction-overall",
                    (
                        "Satisfação geral entre tickets respondidos: "
                        f"{satisfaction_row['start_value']:.2f}→{satisfaction_row['end_value']:.2f}."
                    ),
                    "confirmed_fact",
                    str(satisfaction_row["status"]),
                    satisfaction_row.get("end_value"),
                    "satisfaction_points/response",
                    "support_ticket_respondents",
                    satisfaction_row.get("cutoff_start"),
                    satisfaction_row.get("cutoff_end"),
                    [unknown_ref],
                    str(satisfaction_row["limitation"]),
                ),
                _claim(
                    "C-satisfaction-churn-next-30d",
                    (
                        "Satisfação entre respondentes que churnariam em 30 dias: "
                        f"{satisfaction_churn_row['start_value']:.2f}→"
                        f"{satisfaction_churn_row['end_value']:.2f}."
                    ),
                    "confirmed_fact",
                    str(satisfaction_churn_row["status"]),
                    satisfaction_churn_row.get("end_value"),
                    "satisfaction_points/response",
                    "support_ticket_respondents_churn_next_30d",
                    satisfaction_churn_row.get("cutoff_start"),
                    satisfaction_churn_row.get("cutoff_end"),
                    [satisfaction_churn_ref],
                    "Coorte retrospectiva e restrita a tickets com resposta.",
                ),
            ]
        )
        blocks["unknowns"]["summary"] = unknown_statement

    contradictions = result.quality_report.get("contradictions", {})
    anomaly_count = sum(int(count) for count in contradictions.values() if count)
    if anomaly_count:
        anomaly_statement = (
            f"A auditoria sinalizou {anomaly_count:,} ocorrências de regras de qualidade; "
            "uma mesma linha pode aparecer em mais de uma regra."
        ).replace(",", ".")
        blocks["unknowns"]["claims"].append(
            _claim(
                "C-data-quality-anomalies",
                anomaly_statement,
                "confirmed_fact",
                "concern",
                anomaly_count,
                "quality_rule_hits",
                "all_input_rows",
                None,
                OBSERVATION_END,
                ["quality:report"],
                "Contagem de ocorrências por regra, não de linhas distintas.",
            )
        )
        blocks["unknowns"]["summary"] = f"{blocks['unknowns']['summary']} {anomaly_statement}"

    finding = (
        result.findings.loc[result.findings["finding_id"].eq(selected_mechanism_id)].iloc[0]
        if selected_mechanism_id is not None
        else None
    )
    if finding is not None:
        actions = [
            {
                "id": "A-intervene",
                "kind": "intervention_proposal",
                "description": str(finding["immediate_action"]),
                "evidence_ids": [mechanism_ref],
                "owner_role": str(finding["owner"]),
                "deadline_days": 7,
                "population": "contas expostas no snapshot diagnóstico",
                "success_metric": str(finding.get("success_metric", "sinal e churn da coorte")),
                "advance_if": "o sinal persistir com cobertura e comparação suficientes",
                "stop_if": "a auditoria contradizer o sinal ou revelar viés de cobertura",
                "limitation": "Proposta; nenhum contato ou automação foi autorizado.",
            }
        ]
    else:
        actions = [
            {
                "id": "A-data-integrity",
                "kind": "validation",
                "description": "Sanear eventos fora do ciclo de vida e medir novamente o churn.",
                "evidence_ids": ["quality:report"],
                "owner_role": "Head de Dados",
                "deadline_days": 7,
                "population": "eventos e contas sinalizados pelas regras de qualidade",
                "success_metric": "zero evento inválido aceito e métricas reproduzidas",
                "advance_if": "churn e coortes permanecerem estáveis após o saneamento",
                "stop_if": "a correção alterar materialmente denominadores ou tendências",
                "limitation": "Validação interna; não autoriza intervenção em clientes.",
            },
            {
                "id": "A-usage-prospective",
                "kind": "validation",
                "description": "Acompanhar uso e churn prospectivamente por 30 dias.",
                "evidence_ids": [
                    "claim:C-usage-growth:churn_next_30d"
                    if "claim:C-usage-growth:churn_next_30d" in evidence_refs
                    else "quality:report"
                ],
                "owner_role": "Head de Produto",
                "deadline_days": 30,
                "population": "contas ativas no início da janela prospectiva",
                "success_metric": "uso prévio e churn em 30 dias com cobertura >=70%",
                "advance_if": "a queda de uso anteceder churn com comparação suficiente",
                "stop_if": "o sinal desaparecer ou ocorrer apenas após o churn",
                "limitation": "Teste observacional prospectivo; não prova causalidade sozinho.",
            },
            {
                "id": "A-satisfaction-sample",
                "kind": "validation",
                "description": "Medir satisfação numa amostra representativa, fora dos tickets.",
                "evidence_ids": [
                    "claim:C-satisfaction-ok:churn_next_30d"
                    if "claim:C-satisfaction-ok:churn_next_30d" in evidence_refs
                    else "quality:report"
                ],
                "owner_role": "Head de CS",
                "deadline_days": 30,
                "population": "amostra estratificada de contas ativas e recém-churnadas",
                "success_metric": "resposta >=70% por estrato e diferença entre coortes",
                "advance_if": "a diferença persistir com cobertura representativa",
                "stop_if": "a diferença sumir fora da amostra de tickets",
                "limitation": "Amostragem mede associação e representatividade, não causa.",
            },
        ]
    blocks["next_actions"]["actions"].extend(actions)
    blocks["next_actions"]["summary"] = (
        str(actions[0]["description"])
        if finding is not None
        else "Validar dados, uso e satisfação antes de intervir em clientes."
    )

    block_list = [
        blocks[block_id]
        for block_id in (
            "what_changed",
            "where",
            "strongest_mechanism",
            "unknowns",
            "next_actions",
        )
    ]
    headline_claim_ids = [
        claim["id"]
        for claim in block_list[0]["claims"]  # type: ignore[index]
    ]
    headline = f"Resposta curta: {block_list[0]['summary']}"
    if mechanism_status in {"inconclusive", "unavailable"}:
        headline += (
            " Nenhum mecanismo passou todos os gates. Decisão: validar dados, uso e "
            "satisfação antes de intervir."
        )
    elif mechanism_status == "tied":
        headline += (
            " Há mecanismos sustentados empatados; nenhum foi selecionado isoladamente. "
            "Decisão: comparar os mecanismos antes de priorizar intervenção."
        )
    else:
        headline += " Decisão: priorizar a intervenção sustentada e medir o resultado."
    block_confidence = {
        "what_changed": "Alta confiança",
        "where": "Alta confiança",
        "strongest_mechanism": (
            "Moderada confiança" if mechanism_status in {"supported", "tied"} else "Baixa confiança"
        ),
        "unknowns": "Baixa confiança",
        "next_actions": "Baixa confiança",
    }
    for block in block_list:
        block["confidence_label"] = block_confidence[str(block["id"])]
    return {
        "schema_version": 1,
        "analysis_id": analysis_id,
        "parameters": _manifest_parameters(result),
        "headline": headline,
        "headline_claim_ids": headline_claim_ids,
        "selected_mechanism_id": selected_mechanism_id,
        "mechanism_status": mechanism_status,
        "blocks": block_list,
        "evidence_refs": evidence_refs,
    }


def _value(value: object) -> str:
    if pd.isna(value):
        return "n/d"
    if isinstance(value, (float, np.floating)):
        return f"{value:.3f}"
    return str(value).replace("|", r"\|").replace("\n", "<br>")


def _markdown_table(frame: pd.DataFrame, columns: tuple[str, ...]) -> list[str]:
    if frame.empty:
        return ["Sem linhas elegíveis."]
    labels = [column.replace("_", " ") for column in columns]
    lines = ["| " + " | ".join(labels) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    lines.extend(
        "| " + " | ".join(_value(row[column]) for column in columns) + " |"
        for _, row in frame.loc[:, columns].iterrows()
    )
    return lines


def _build_legacy_report(
    result: AnalysisResult, queue: pd.DataFrame, watchlist: pd.DataFrame
) -> str:
    accepted = _accepted_findings(result.findings)
    renewal_accounts = int(
        result.findings.set_index("finding_id").loc["F-commercial-renewal", "affected_accounts"]
    )
    decision = (
        f"Priorizar {FINDING_LABELS.get(accepted.iloc[0]['finding_id'], accepted.iloc[0]['finding_id'])}."
        if not accepted.empty
        else "Evidência insuficiente para priorizar uma causa"
    )
    lines = ["# Diagnóstico executivo de churn", "", "## Decisão executiva", "", decision, ""]

    claim_index = result.claim_checks.set_index(["claim_id", "cohort"])
    usage_overall = STATUS_LABELS[claim_index.loc[("C-usage-growth", "overall"), "status"]]
    usage_churn = STATUS_LABELS[claim_index.loc[("C-usage-growth", "churn_next_30d"), "status"]]
    satisfaction = STATUS_LABELS[claim_index.loc[("C-satisfaction-ok", "overall"), "status"]]
    lines.extend(
        [
            (
                "**Leitura em uma frase:** uso "
                f"{usage_overall.lower()} no agregado e {usage_churn.lower()} na coorte que "
                "churnará em 30 dias; "
                f"satisfação {satisfaction.lower()}; "
                + (
                    "há mecanismo observacional sustentado, sem prova causal."
                    if not accepted.empty
                    else "nenhuma hipótese passou todos os gates."
                )
            ),
            "",
        ]
    )

    lines.extend(["## O que não bate", ""])
    claims = result.claim_checks.loc[
        result.claim_checks["cohort"].isin(["overall", "churn_next_30d"])
    ].copy()
    claims = claims.replace(
        {"claim_id": CLAIM_LABELS, "cohort": COHORT_LABELS, "status": STATUS_LABELS}
    ).rename(
        columns={
            "claim_id": "métrica",
            "cohort": "coorte",
            "start_value": "início",
            "end_value": "fim",
            "slope": "tendência",
            "status": "leitura",
            "coverage": "cobertura",
        }
    )
    lines.extend(
        _markdown_table(
            claims,
            ("métrica", "coorte", "início", "fim", "tendência", "leitura", "cobertura"),
        )
    )

    quality_rows = pd.DataFrame(
        [
            {"regra": rule, "linhas": count}
            for rule, count in result.quality_report.get("contradictions", {}).items()
            if count
        ],
        columns=["regra", "linhas"],
    ).sort_values("linhas", ascending=False)
    quality_rows["regra"] = quality_rows["regra"].replace(QUALITY_LABELS)
    lines.extend(["", "## Qualidade que limita a decisão", ""])
    lines.extend(_markdown_table(quality_rows, ("regra", "linhas")))

    lines.extend(["", "## Hipóteses avaliadas", ""])
    if accepted.empty:
        failed = (
            result.findings[["finding_id", "failure_reason"]]
            .replace({"finding_id": FINDING_LABELS, "failure_reason": FAILURE_LABELS})
            .rename(columns={"finding_id": "hipótese", "failure_reason": "por que não passou"})
        )
        lines.extend(_markdown_table(failed, ("hipótese", "por que não passou")))
    else:
        lines.extend(
            _markdown_table(
                accepted,
                (
                    "finding_id",
                    "confidence",
                    "mrr_exposed_max",
                    "affected_accounts",
                    "counterevidence",
                    "limitation",
                ),
            )
        )

    lines.extend(["", "## Segmentos descritivos", ""])
    segment_confidence = result.segment_metrics.get(
        "confidence", pd.Series("inconclusive", index=result.segment_metrics.index)
    )
    ordered_segments = result.segment_metrics.assign(_eligible=segment_confidence.eq("eligible"))
    segment_order = [
        column
        for column in ("_eligible", "relative_risk", "mrr_lost")
        if column in ordered_segments
    ]
    ordered_segments = ordered_segments.sort_values(segment_order, ascending=False)
    ordered_segments["confidence"] = segment_confidence
    ordered_segments["dimension"] = ordered_segments["dimension"].replace(DIMENSION_LABELS)
    ordered_segments["segment"] = ordered_segments["segment"].replace(SEGMENT_LABELS)
    ordered_segments["confidence"] = ordered_segments["confidence"].replace(ELIGIBILITY_LABELS)
    ordered_segments = ordered_segments.rename(
        columns={
            "dimension": "dimensão",
            "segment": "segmento",
            "sample_size": "contas",
            "churn_rate": "taxa de churn",
            "overall_churn_rate": "taxa geral",
            "relative_risk": "risco relativo",
            "mrr_lost": "MRR perdido",
            "confidence": "elegibilidade",
        }
    )
    segment_columns = tuple(
        column
        for column in (
            "dimensão",
            "segmento",
            "contas",
            "taxa de churn",
            "taxa geral",
            "risco relativo",
            "MRR perdido",
            "elegibilidade",
        )
        if column in ordered_segments
    )
    eligible_segments = ordered_segments.loc[ordered_segments["elegibilidade"].eq("Elegível")]
    if not eligible_segments.empty:
        top_segment = eligible_segments.sort_values("risco relativo", ascending=False).iloc[0]
        lines.append(
            "Entre os segmentos elegíveis, "
            f"{top_segment['dimensão']} / {top_segment['segmento']} tem o maior risco relativo "
            f"({top_segment['risco relativo']:.2f}x); valores maiores abaixo permanecem "
            "inconclusivos por amostra ou número de churns."
        )
        lines.append("")
    lines.extend(_markdown_table(ordered_segments.head(15), segment_columns))

    lines.extend(["", "## Contas para validação" if queue.empty else "## Contas prioritárias", ""])
    if queue.empty:
        lines.append(
            "Nenhuma conta está autorizada para intervenção: não há finding aceito. "
            "As contas abaixo servem somente para validação dos sinais e dos dados."
        )
        visible_watchlist = watchlist.head(10).copy()
        visible_watchlist["signals"] = visible_watchlist["signals"].map(_translated_signals)
        visible_watchlist["status"] = "Somente validação"
        visible_watchlist = visible_watchlist.rename(
            columns={
                "account_id": "conta",
                "validation_rank": "ordem de validação",
                "signal_count": "quantidade de sinais",
                "mrr_exposed_max": "MRR exposto máximo",
                "signals": "sinais",
                "status": "uso permitido",
            }
        )
        lines.extend(
            _markdown_table(
                visible_watchlist,
                (
                    "conta",
                    "ordem de validação",
                    "quantidade de sinais",
                    "MRR exposto máximo",
                    "sinais",
                    "uso permitido",
                ),
            )
        )
    else:
        lines.extend(
            _markdown_table(
                queue.head(20),
                ("account_id", "priority", "finding_id", "mrr_exposed_max", "risk_probability"),
            )
        )

    lines.extend(["", "## Plano de ação", ""])
    if accepted.empty:
        lines.extend(
            [
                (
                    "- **1 semana:** colocar eventos fora do ciclo de vida em quarentena analítica, "
                    f"auditar uma amostra das {renewal_accounts} contas com renovação automática "
                    "desligada e corrigir os vínculos de data."
                ),
                (
                    "- **30–90 dias:** instrumentar o ciclo de vida com chaves e relógios confiáveis, "
                    "acompanhar uma coorte prospectiva e repetir os gates antes de automatizar contato."
                ),
                (
                    "- **Medição:** cobertura temporal válida, estabilidade observed/strict e MRR "
                    "realmente perdido na coorte prospectiva."
                ),
            ]
        )
    else:
        top = accepted.iloc[0]
        lines.extend(
            [
                f"- **1 semana:** {top['immediate_action']}",
                f"- **30–90 dias:** {top['structural_action']}",
                f"- **Medição:** {top.get('success_metric', 'MRR perdido e evolução da coorte exposta')}",
            ]
        )

    lines.extend(
        [
            "",
            "## Metodologia e limitações",
            "",
            (
                "Painel conta-data de corte, leitura strict para decisão e observed apenas para "
                "sensibilidade. As associações não demonstram causalidade; MRR exposto é "
                "oportunidade máxima, não receita recuperável."
            ),
            "",
            (
                "O modelo preditivo só é publicado quando supera todos os gates fora do tempo. "
                f"Nesta execução: publish_model={bool(result.model_evaluation.get('publish_model'))}."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _build_report(
    result: AnalysisResult,
    queue: pd.DataFrame,
    watchlist: pd.DataFrame,
    answer: dict[str, object],
) -> str:
    lines = ["# Resposta executiva canônica", "", str(answer["headline"]), ""]
    for index, block in enumerate(answer["blocks"], start=1):  # type: ignore[union-attr]
        lines.extend(
            [
                f"## {index}. {block['title']}",
                "",
                f"**{block['confidence_label']}**",
                "",
                str(block["summary"]),
                "",
            ]
        )
        lines.extend(f"- **{claim['id']}:** {claim['statement']}" for claim in block["claims"])
        lines.extend(
            f"- **{action['id']}:** {action['description']}" for action in block["actions"]
        )
        lines.append("")
    lines.extend(["---", "", _build_legacy_report(result, queue, watchlist)])
    return "\n".join(lines)


def _dependency_versions() -> dict[str, str]:
    dependencies = {}
    for package in ("numpy", "pandas", "scikit-learn", "scipy", "statsmodels", "streamlit"):
        try:
            dependencies[package] = version(package)
        except PackageNotFoundError:
            dependencies[package] = "missing"
    return dependencies


def _git_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def publish_artifacts(result: AnalysisResult, output_dir: Path) -> dict[str, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    queue = _build_queue(result)
    watchlist = _build_watchlist(result)
    answer = _build_ceo_answer(result)
    filename_payloads = _analysis_payloads(result, queue, watchlist)
    filename_payloads["ceo_answer.json"] = answer
    filename_payloads["report.md"] = _build_report(result, queue, watchlist, answer)
    paths: dict[str, Path] = {}
    for filename, payload in filename_payloads.items():
        path = output_dir / filename
        temporary = path.with_suffix(path.suffix + ".tmp")
        if filename.endswith((".csv", ".json")):
            temporary.write_bytes(_payload_bytes(filename, payload))
        else:
            temporary.write_text(str(payload), encoding="utf-8")
        temporary.replace(path)
        paths[path.stem] = path

    manifest = {
        "schema_version": 1,
        "analysis_id": answer["analysis_id"],
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source_git_sha": _git_sha(),
        "runtime": {"python": platform.python_version(), "dependencies": _dependency_versions()},
        "input_checksums": RAW_FILE_SHA256,
        "parameters": _manifest_parameters(result),
        "test_status": os.environ.get("RAVENSTACK_TEST_STATUS", "unknown"),
        "publish_model": bool(result.model_evaluation.get("publish_model")),
        "artifact_checksums": {path.name: sha256_file(path) for path in paths.values()},
    }
    manifest_path = output_dir / "run_manifest.json"
    temporary_manifest = manifest_path.with_suffix(".json.tmp")
    temporary_manifest.write_text(_json_text(manifest) + "\n", encoding="utf-8")
    temporary_manifest.replace(manifest_path)
    paths["run_manifest"] = manifest_path
    return paths


def validate_artifact_set(output_dir: Path) -> dict[str, object]:
    output_dir = Path(output_dir)
    manifest_path = output_dir / "run_manifest.json"
    if not manifest_path.is_file():
        raise ArtifactConsistencyError("run_manifest.json missing")
    try:
        manifest = json.loads(
            manifest_path.read_text(encoding="utf-8"),
            parse_constant=lambda value: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON number: {value}")
            ),
        )
    except ValueError as error:
        raise ArtifactConsistencyError(f"invalid manifest JSON: {error}") from error
    checksums = manifest.get("artifact_checksums", {})
    if not isinstance(checksums, dict):
        raise ArtifactConsistencyError("artifact_checksums must be an object")
    if set(checksums) != EXPECTED_ARTIFACT_FILENAMES:
        raise ArtifactConsistencyError("artifact manifest is incomplete or has unknown files")
    for filename, expected in checksums.items():
        path = output_dir / filename
        if not path.is_file():
            raise ArtifactConsistencyError(f"{filename} missing")
        if sha256_file(path) != expected:
            raise ArtifactConsistencyError(f"{filename} checksum mismatch")
    for filename, required_columns in REQUIRED_EVIDENCE_COLUMNS.items():
        frame = pd.read_csv(output_dir / filename)
        missing = required_columns - set(frame.columns)
        if missing:
            raise ArtifactConsistencyError(f"{filename} schema missing columns: {sorted(missing)}")
        if frame["evidence_id"].duplicated().any():
            raise ArtifactConsistencyError(f"{filename} has duplicate evidence_id")
        numeric = frame.select_dtypes(include="number")
        if not numeric.empty and np.isinf(numeric.to_numpy(dtype=float)).any():
            raise ArtifactConsistencyError(f"{filename} contains infinite numbers")
    scorecard = pd.read_csv(output_dir / "mechanism_scorecard.csv")
    gate_columns = [
        "temporal_support",
        "comparison_support",
        "sample_support",
        "association_support",
        "chronology_support",
        "cross_table_support",
    ]
    if not set(scorecard[gate_columns].stack()).issubset({"pass", "fail", "unavailable"}):
        raise ArtifactConsistencyError("mechanism_scorecard.csv has invalid gate state")
    try:
        answer = json.loads(
            (output_dir / "ceo_answer.json").read_text(encoding="utf-8"),
            parse_constant=lambda value: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON number: {value}")
            ),
        )
    except ValueError as error:
        raise ArtifactConsistencyError(f"invalid ceo_answer.json: {error}") from error
    if answer.get("schema_version") != 1:
        raise ArtifactConsistencyError("ceo_answer.json schema_version must be 1")
    if answer.get("analysis_id") != manifest.get("analysis_id"):
        raise ArtifactConsistencyError("analysis_id mismatch")
    if answer.get("parameters") != manifest.get("parameters"):
        raise ArtifactConsistencyError("answer parameters mismatch")
    expected_blocks = [
        "what_changed",
        "where",
        "strongest_mechanism",
        "unknowns",
        "next_actions",
    ]
    blocks = answer.get("blocks")
    if not isinstance(blocks, list) or [block.get("id") for block in blocks] != expected_blocks:
        raise ArtifactConsistencyError("canonical block order is invalid")
    evidence_refs = answer.get("evidence_refs")
    if not isinstance(evidence_refs, dict):
        raise ArtifactConsistencyError("evidence_refs must be an object")
    allowed_artifacts = set(checksums) | set(RAW_FILE_SHA256)
    for evidence_id, reference in evidence_refs.items():
        artifact = reference.get("artifact")
        if artifact not in allowed_artifacts:
            raise ArtifactConsistencyError(f"{evidence_id} references unknown artifact")
        if not str(artifact).endswith(".csv"):
            continue
        frame = pd.read_csv(output_dir / str(artifact))
        row_key = reference.get("row_key")
        columns = reference.get("columns")
        if not isinstance(row_key, dict) or not row_key:
            raise ArtifactConsistencyError(f"{evidence_id} row_key is invalid")
        if not isinstance(columns, list) or not columns:
            raise ArtifactConsistencyError(f"{evidence_id} columns are invalid")
        missing_columns = (set(row_key) | set(columns)) - set(frame.columns)
        if missing_columns:
            raise ArtifactConsistencyError(
                f"{evidence_id} references missing columns: {sorted(missing_columns)}"
            )
        selected = pd.Series(True, index=frame.index)
        for column, value in row_key.items():
            selected &= (
                frame[column].isna() if value is None else frame[column].astype(str).eq(str(value))
            )
        if int(selected.sum()) != 1:
            raise ArtifactConsistencyError(f"{evidence_id} row_key must resolve exactly one row")

    claims = [claim for block in blocks for claim in block.get("claims", [])]
    actions = [action for block in blocks for action in block.get("actions", [])]
    claim_ids = [claim.get("id") for claim in claims]
    if len(claim_ids) != len(set(claim_ids)):
        raise ArtifactConsistencyError("duplicate claim id")
    known_ids = set(evidence_refs) | set(claim_ids)
    for item in [*claims, *actions]:
        references = item.get("evidence_ids")
        if not isinstance(references, list) or not references:
            raise ArtifactConsistencyError(f"{item.get('id')} lacks evidence_ids")
        if not set(references).issubset(evidence_refs):
            raise ArtifactConsistencyError(f"{item.get('id')} has unresolved evidence_ids")
        comparator_id = item.get("comparator_id")
        if comparator_id is not None and comparator_id not in known_ids:
            raise ArtifactConsistencyError(f"{item.get('id')} has unresolved comparator_id")
    if any(action.get("kind") == "intervention_proposal" for action in actions) and not any(
        claim.get("evidence_level") == "supported_mechanism" for claim in claims
    ):
        raise ArtifactConsistencyError("intervention proposal requires supported mechanism")
    return manifest


def compare_artifact_sets(reference_dir: Path, candidate_dir: Path) -> None:
    reference = validate_artifact_set(reference_dir)
    candidate = validate_artifact_set(candidate_dir)
    ignored = {"generated_at_utc", "source_git_sha"}
    for manifest in (reference, candidate):
        for key in ignored:
            manifest.pop(key, None)
    if reference != candidate:
        raise ArtifactConsistencyError("artifact sets differ")
