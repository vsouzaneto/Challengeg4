import json
import os
import subprocess
from dataclasses import replace
from pathlib import Path

import pandas as pd
import pytest

from ravenstack_churn.config import sha256_file
from ravenstack_churn.publish import (
    ArtifactConsistencyError,
    _build_ceo_answer,
    _markdown_table,
    compare_artifact_sets,
    publish_artifacts,
    validate_artifact_set,
)


def _run_check_with_stub(tmp_path, reproduce_exit: int) -> tuple[subprocess.CompletedProcess, str]:
    stub = tmp_path / "python-stub"
    log = tmp_path / "calls.log"
    stub.write_text(
        "#!/bin/sh\n"
        'printf "%s\\n" "$*" >> "$STUB_LOG"\n'
        'case "$*" in\n'
        f'  *"ravenstack_churn.cli reproduce"*) exit {reproduce_exit} ;;\n'
        "esac\n"
        "exit 0\n"
    )
    stub.chmod(0o755)
    environment = {**os.environ, "STUB_LOG": str(log)}
    completed = subprocess.run(
        ["make", "check", f"PYTHON={stub}"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
        env=environment,
    )
    return completed, log.read_text() if log.exists() else ""


def test_check_stops_before_compare_when_reproduce_fails(tmp_path) -> None:
    completed, calls = _run_check_with_stub(tmp_path, reproduce_exit=7)

    assert completed.returncode != 0
    assert "ravenstack_churn.cli reproduce" in calls
    assert "ravenstack_churn.cli compare" not in calls


def test_check_reaches_compare_when_reproduce_succeeds(tmp_path) -> None:
    completed, calls = _run_check_with_stub(tmp_path, reproduce_exit=0)

    assert completed.returncode == 0
    assert "ravenstack_churn.cli compare" in calls


def test_ceo_answer_and_report_share_claim_ids_and_values(analysis_result, tmp_path) -> None:
    paths = publish_artifacts(analysis_result, tmp_path)
    answer = json.loads(paths["ceo_answer"].read_text())
    report = paths["report"].read_text()

    assert [block["id"] for block in answer["blocks"]] == [
        "what_changed",
        "where",
        "strongest_mechanism",
        "unknowns",
        "next_actions",
    ]
    for block in answer["blocks"]:
        for claim in block["claims"]:
            assert claim["id"] in report
            assert claim["statement"] in report


def test_ceo_answer_reconciles_usage_and_satisfaction_claims(analysis_result) -> None:
    answer = _build_ceo_answer(analysis_result)
    claims = {claim["id"]: claim for block in answer["blocks"] for claim in block["claims"]}

    assert "uso cresceu no agregado" in answer["headline"]
    assert "caiu entre as contas que churnariam em 30 dias" in answer["headline"]
    assert claims["C-usage-overall"]["period_start"] == "2024-06-30"
    assert claims["C-usage-churn-next-30d"]["status"] == "down"
    assert claims["C-satisfaction-overall"]["population"] == "support_ticket_respondents"
    assert claims["C-satisfaction-churn-next-30d"]["period_end"] == "2024-11-30"
    assert answer["headline"].startswith("Resposta curta:")
    assert "Decisão:" in answer["headline"]
    assert len(answer["headline"].split()) <= 120


def test_executive_answer_has_no_causal_overclaim(analysis_result) -> None:
    result = replace(
        analysis_result,
        findings=analysis_result.findings.assign(confidence="inconclusive"),
        mechanism_scorecard=analysis_result.mechanism_scorecard.assign(
            evidence_level="plausible_hypothesis", status="inconclusive"
        ),
    )

    answer = _build_ceo_answer(result)
    executive_text = " ".join(
        [
            answer["headline"],
            *[f"{block['title']} {block['summary']}" for block in answer["blocks"]],
        ]
    ).lower()

    assert "mecanismo mais forte" not in executive_text
    assert "plausible_hypothesis" not in executive_text
    assert "auto_renew_off" not in executive_text
    assert "causa ainda não demonstrada" in executive_text


def test_ceo_answer_quantifies_impact_and_denies_false_concentration(
    analysis_result,
) -> None:
    result = replace(
        analysis_result,
        segment_metrics=analysis_result.segment_metrics.assign(relative_risk=1.08),
    )

    answer = _build_ceo_answer(result)
    claims = {claim["id"]: claim for block in answer["blocks"] for claim in block["claims"]}
    recent = (
        analysis_result.monthly_churn.loc[
            analysis_result.monthly_churn["period_kind"].eq("comparison_period")
            & analysis_result.monthly_churn["dimension"].eq("all")
            & analysis_result.monthly_churn["segment"].eq("all")
        ]
        .sort_values("period_end")
        .iloc[-1]
    )
    where = next(block for block in answer["blocks"] if block["id"] == "where")

    assert claims["C-churn-impact"]["unit"] == "monthly_recurring_revenue"
    assert claims["C-churn-impact"]["value"] == recent["mrr_lost"]
    assert claims["C-churn-impact"]["period_start"] == "2024-06-01"
    assert claims["C-churn-impact"]["period_end"] == "2024-11-30"
    assert "não há concentração material demonstrada" in where["summary"].lower()


def test_inconclusive_mechanisms_create_validation_plan_not_winner(
    analysis_result,
) -> None:
    result = replace(
        analysis_result,
        findings=analysis_result.findings.assign(confidence="inconclusive"),
        mechanism_scorecard=analysis_result.mechanism_scorecard.assign(
            evidence_level="plausible_hypothesis", status="inconclusive"
        ),
    )

    answer = _build_ceo_answer(result)
    mechanism = next(block for block in answer["blocks"] if block["id"] == "strongest_mechanism")
    actions = next(block for block in answer["blocks"] if block["id"] == "next_actions")["actions"]

    assert mechanism["title"] == "Causa ainda não demonstrada"
    assert mechanism["claims"] == []
    assert len(actions) == 3
    assert {action["owner_role"] for action in actions} == {
        "Head de Dados",
        "Head de Produto",
        "Head de CS",
    }
    assert all(action["advance_if"] and action["stop_if"] for action in actions)


def test_rehashed_invalid_reference_is_rejected(analysis_result, tmp_path) -> None:
    paths = publish_artifacts(analysis_result, tmp_path)
    answer = json.loads(paths["ceo_answer"].read_text())
    evidence_id = next(iter(answer["evidence_refs"]))
    answer["evidence_refs"][evidence_id]["artifact"] = "missing.csv"
    paths["ceo_answer"].write_text(json.dumps(answer, allow_nan=False))
    manifest = json.loads(paths["run_manifest"].read_text())
    manifest["artifact_checksums"]["ceo_answer.json"] = sha256_file(paths["ceo_answer"])
    paths["run_manifest"].write_text(json.dumps(manifest))

    with pytest.raises(ArtifactConsistencyError, match="unknown artifact"):
        validate_artifact_set(tmp_path)


def test_rehashed_invalid_schema_is_rejected(analysis_result, tmp_path) -> None:
    paths = publish_artifacts(analysis_result, tmp_path)
    scorecard = pd.read_csv(paths["mechanism_scorecard"]).drop(columns="temporal_support")
    scorecard.to_csv(paths["mechanism_scorecard"], index=False)
    manifest = json.loads(paths["run_manifest"].read_text())
    manifest["artifact_checksums"]["mechanism_scorecard.csv"] = sha256_file(
        paths["mechanism_scorecard"]
    )
    paths["run_manifest"].write_text(json.dumps(manifest))

    with pytest.raises(ArtifactConsistencyError, match="schema missing columns"):
        validate_artifact_set(tmp_path)


def test_rehashed_non_finite_json_is_rejected(analysis_result, tmp_path) -> None:
    paths = publish_artifacts(analysis_result, tmp_path)
    text = paths["ceo_answer"].read_text().replace('"value": 0.04', '"value": NaN', 1)
    paths["ceo_answer"].write_text(text)
    manifest = json.loads(paths["run_manifest"].read_text())
    manifest["artifact_checksums"]["ceo_answer.json"] = sha256_file(paths["ceo_answer"])
    paths["run_manifest"].write_text(json.dumps(manifest))

    with pytest.raises(ArtifactConsistencyError, match="non-finite JSON number"):
        validate_artifact_set(tmp_path)


def test_all_inconclusive_keeps_facts_and_empty_queue(analysis_result, tmp_path) -> None:
    findings = analysis_result.findings.assign(confidence="inconclusive")
    scorecard = analysis_result.mechanism_scorecard.assign(
        evidence_level="plausible_hypothesis", status="inconclusive"
    )
    paths = publish_artifacts(
        replace(analysis_result, findings=findings, mechanism_scorecard=scorecard), tmp_path
    )
    answer = json.loads(paths["ceo_answer"].read_text())

    assert answer["selected_mechanism_id"] is None
    assert answer["mechanism_status"] == "inconclusive"
    assert answer["blocks"][0]["claims"]
    assert pd.read_csv(paths["account_queue"]).empty


def test_analysis_id_is_stable_and_non_recursive(analysis_result, tmp_path) -> None:
    first = publish_artifacts(analysis_result, tmp_path / "first")
    second = publish_artifacts(analysis_result, tmp_path / "second")

    first_answer = _build_ceo_answer(analysis_result)
    assert first_answer["analysis_id"] == json.loads(first["ceo_answer"].read_text())["analysis_id"]
    assert (
        json.loads(first["run_manifest"].read_text())["analysis_id"]
        == json.loads(second["run_manifest"].read_text())["analysis_id"]
    )


def test_ceo_answer_orders_quality_source_tables_deterministically(analysis_result) -> None:
    rows = analysis_result.quality_report["rows"]
    reordered_result = replace(
        analysis_result,
        quality_report={
            **analysis_result.quality_report,
            "rows": dict(reversed(list(rows.items()))),
        },
    )

    first = _build_ceo_answer(analysis_result)["evidence_refs"]["quality:report"]
    reordered = _build_ceo_answer(reordered_result)["evidence_refs"]["quality:report"]

    assert first["source_tables"] == reordered["source_tables"] == sorted(rows)


def test_ceo_answer_rounds_machine_precision_noise(analysis_result) -> None:
    monthly_churn = analysis_result.monthly_churn.copy()
    recent_index = (
        monthly_churn.loc[
            monthly_churn["period_kind"].eq("comparison_period")
            & monthly_churn["dimension"].eq("all")
            & monthly_churn["segment"].eq("all")
        ]
        .sort_values("period_end")
        .index[-1]
    )
    monthly_churn.loc[recent_index, "rate_difference"] += 4e-17

    original = _build_ceo_answer(analysis_result)["blocks"][0]["claims"][0]
    perturbed = _build_ceo_answer(replace(analysis_result, monthly_churn=monthly_churn))["blocks"][
        0
    ]["claims"][0]

    assert original["value"] == perturbed["value"]


def test_queue_and_report_use_same_finding_ids(analysis_result, tmp_path) -> None:
    paths = publish_artifacts(analysis_result, tmp_path)
    findings = pd.read_csv(paths["findings"])
    claim_checks = pd.read_csv(paths["claim_checks"])
    queue = pd.read_csv(paths["account_queue"])
    report = paths["report"].read_text()
    assert set(queue.finding_id).issubset(set(findings.finding_id))
    assert all(
        finding_id in report
        for finding_id in findings.query("confidence != 'inconclusive'").finding_id
    )
    assert set(claim_checks.claim_id) == {"C-usage-growth", "C-satisfaction-ok"}
    assert all(claim_id in report for claim_id in claim_checks.claim_id.unique())
    assert {"plan_tier", "mrr_band"}.issubset(queue.columns)
    assert "Qualidade que limita a decisão" in report
    assert "Entre os segmentos elegíveis" in report


def test_manifest_rejects_modified_artifact(analysis_result, tmp_path) -> None:
    publish_artifacts(analysis_result, tmp_path)
    (tmp_path / "findings.csv").write_text("changed")
    with pytest.raises(ArtifactConsistencyError, match="findings.csv checksum mismatch"):
        validate_artifact_set(tmp_path)


def test_manifest_uses_quality_label_policy(analysis_result, tmp_path) -> None:
    analysis_result.quality_report["label_policy"] = "first_valid_non_reactivation_event"

    publish_artifacts(analysis_result, tmp_path)
    manifest = validate_artifact_set(tmp_path)

    assert manifest["parameters"]["label_policy"] == "first_valid_non_reactivation_event"
    assert manifest["parameters"]["observation_end"] == "2024-12-31"


def test_manifest_rejects_missing_artifact_entry(analysis_result, tmp_path) -> None:
    publish_artifacts(analysis_result, tmp_path)
    manifest_path = tmp_path / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["artifact_checksums"].pop("report.md")
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ArtifactConsistencyError, match="manifest is incomplete"):
        validate_artifact_set(tmp_path)


def test_manifest_rejects_invalid_checksum_shape(analysis_result, tmp_path) -> None:
    publish_artifacts(analysis_result, tmp_path)
    manifest_path = tmp_path / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["artifact_checksums"] = []
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ArtifactConsistencyError, match="must be an object"):
        validate_artifact_set(tmp_path)


def test_no_accepted_finding_publishes_honest_empty_queue(analysis_result, tmp_path) -> None:
    result = replace(
        analysis_result,
        findings=analysis_result.findings.assign(confidence="inconclusive"),
    )
    paths = publish_artifacts(result, tmp_path)
    assert pd.read_csv(paths["account_queue"]).empty
    watchlist = pd.read_csv(paths["account_watchlist"])
    assert not watchlist.empty
    assert set(watchlist["status"]) == {"validation_only"}
    report = paths["report"].read_text()
    assert "Evidência insuficiente para priorizar uma causa" in report
    assert "uso aumentou no agregado e caiu na coorte" in report
    renewal_accounts = int(
        result.findings.set_index("finding_id").loc["F-commercial-renewal", "affected_accounts"]
    )
    assert f"amostra das {renewal_accounts} contas" in report


def test_inactive_accounts_never_enter_queue_or_watchlist(analysis_result, tmp_path) -> None:
    panel = analysis_result.panel.assign(
        has_active_subscription=lambda frame: frame["account_id"].ne("A-2")
    )
    paths = publish_artifacts(replace(analysis_result, panel=panel), tmp_path)
    assert "A-2" not in set(pd.read_csv(paths["account_queue"])["account_id"])
    assert "A-2" not in set(pd.read_csv(paths["account_watchlist"])["account_id"])


def test_markdown_table_escapes_cell_separators() -> None:
    table = _markdown_table(pd.DataFrame([{"signals": "usage|errors"}]), ("signals",))
    assert table[-1] == r"| usage\|errors |"


def test_equivalent_runs_compare_equal(analysis_result, tmp_path) -> None:
    reference = tmp_path / "reference"
    candidate = tmp_path / "candidate"
    publish_artifacts(analysis_result, reference)
    publish_artifacts(analysis_result, candidate)
    compare_artifact_sets(reference, candidate)
