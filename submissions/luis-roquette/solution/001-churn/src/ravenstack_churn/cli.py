from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .config import DEFAULT_CUTOFFS, OBSERVATION_END, SCORING_CUTOFF
from .contracts import load_raw_tables, validate_contracts
from .diagnosis import (
    build_claim_checks,
    build_event_cohort_metrics,
    build_mechanism_scorecard,
    build_monthly_churn,
    build_reason_distribution,
    evaluate_candidates,
)
from .modeling import evaluate_model
from .panel import build_account_panel, build_event_aligned_panel, select_first_terminal_events
from .publish import (
    AnalysisResult,
    compare_artifact_sets,
    publish_artifacts,
    validate_artifact_set,
)
from .quality import build_quality_report


def reproduce(raw_dir: Path, output_dir: Path) -> dict[str, Path]:
    tables = load_raw_tables(raw_dir)
    warnings = validate_contracts(tables)
    quality = build_quality_report(tables)
    quality["contract_warnings"] = warnings.to_dict(orient="records")

    cutoffs = DEFAULT_CUTOFFS.append(pd.DatetimeIndex([SCORING_CUTOFF]))
    terminal_events, _ = select_first_terminal_events(
        tables["accounts"], tables["churn_events"], OBSERVATION_END
    )
    observed = build_account_panel(tables, cutoffs, "observed")
    strict = build_account_panel(tables, cutoffs, "strict")
    monthly_churn = build_monthly_churn(tables, terminal_events)
    reasons = build_reason_distribution(tables, terminal_events)
    event_panel = pd.concat(
        [
            build_event_aligned_panel(tables, terminal_events, chronology)
            for chronology in ("observed", "strict")
        ],
        ignore_index=True,
    )
    event_metrics = build_event_cohort_metrics(event_panel)
    findings, segments = evaluate_candidates(
        observed,
        strict,
        terminal_events,
        event_metrics,
        reasons,
    )
    scorecard = build_mechanism_scorecard(findings, event_metrics, reasons)
    claims = build_claim_checks(strict)
    model_evaluation, model_scores = evaluate_model(strict)
    result = AnalysisResult(
        quality_report=quality,
        panel=pd.concat([observed, strict], ignore_index=True),
        claim_checks=claims,
        findings=findings,
        segment_metrics=segments,
        monthly_churn=monthly_churn,
        reason_distribution=reasons,
        event_cohort_metrics=event_metrics,
        mechanism_scorecard=scorecard,
        model_evaluation=model_evaluation,
        model_scores=model_scores,
    )
    paths = publish_artifacts(result, output_dir)
    validate_artifact_set(output_dir)
    print(f"artifacts={output_dir.resolve()}")
    print(
        f"findings_accepted={int(findings['confidence'].eq('accepted').sum())} "
        f"publish_model={bool(model_evaluation.get('publish_model'))}"
    )
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(prog="ravenstack-churn")
    commands = parser.add_subparsers(dest="command", required=True)
    reproduce_parser = commands.add_parser("reproduce")
    reproduce_parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    reproduce_parser.add_argument("--output-dir", type=Path, default=Path("artifacts"))
    compare_parser = commands.add_parser("compare")
    compare_parser.add_argument("--reference-dir", type=Path, required=True)
    compare_parser.add_argument("--candidate-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "reproduce":
        reproduce(args.raw_dir, args.output_dir)
    elif args.command == "compare":
        compare_artifact_sets(args.reference_dir, args.candidate_dir)
        print("artifact_sets=equal")


if __name__ == "__main__":
    main()
