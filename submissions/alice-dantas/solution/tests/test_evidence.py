"""Evidência do backtest servida como dado (contrato v5, AC-4.5)."""
import json

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from api.schemas import Evidence
from leadscorer import codes, evidence, policy
from leadscorer.errors import DataError

from conftest import EVIDENCE_RESULTS, write_evidence


def test_strategies_in_report_order_without_the_leak(evidence_path):
    result = evidence.load(evidence_path)
    assert [r["code"] for r in result["rankers"]] == list(codes.RANKER_CODES)
    assert codes.RANKER_LEAK_QUARTER_END not in json.dumps(result)
    assert result["reference"] == codes.SERVED_RANKER == codes.RANKER_AGE_P90_THEN_MAX_CYCLE
    assert [r["code"] for r in result["without_no_outcome"]] == [
        codes.RANKER_LIST_PRICE_ONLY, codes.RANKER_AGE_MAX_CYCLE_ONLY, codes.RANKER_AGE_P90_THEN_MAX_CYCLE]


def test_numbers_are_the_backtest_numbers(evidence_path):
    result = evidence.load(evidence_path)
    source = {e["code"]: e for e in EVIDENCE_RESULTS["summary"]}
    for ranker in result["rankers"]:
        entry = source[ranker["code"]]
        assert {k: ranker[k] for k in evidence.METRICS} == {k: entry[k] for k in evidence.METRICS}
        assert ranker["cuts_auc_above_chance"] == entry["cuts_ci_above_half"]
        if ranker["code"] == codes.SERVED_RANKER:
            assert ranker["delta_val"] is None and ranker["cuts_val_above_reference"] is None
        else:
            assert ranker["delta_val"] == {"value": entry["d_val_at_k"], "low": entry["d_val_low"],
                                           "high": entry["d_val_high"]}
    assert all(r["cuts_auc_above_chance"] is None for r in result["without_no_outcome"])
    assert result["design"] == {k: EVIDENCE_RESULTS["design"][k] for k in evidence.DESIGN}


@pytest.mark.parametrize("content", [None, "{não é json", json.dumps({"design": {}})])
def test_missing_or_broken_file_is_a_coded_error(tmp_path, content):
    path = tmp_path / "backtest_results.json"
    if content is not None:
        path.write_text(content, encoding="utf-8")
    with pytest.raises(DataError) as error:
        evidence.load(path)
    assert (error.value.code, error.value.params) == (codes.EVIDENCE_UNAVAILABLE, {"file": path.name})


def delta(value, low, high):
    return {"value": value, "low": low, "high": high}


def test_verdict_from_numbers():
    served = {"code": codes.SERVED_RANKER, "delta_val": None}
    price = {"code": codes.RANKER_LIST_PRICE_ONLY, "delta_val": delta(0.01, 0.003, 0.019)}
    previous = {"code": codes.RANKER_AGE_MAX_CYCLE_ONLY, "delta_val": delta(0.01, 0.003, 0.019)}
    behind = evidence.verdict([price, previous, served])
    assert behind == {"code": codes.VERDICT_REFERENCE_BEHIND, "ranker": codes.RANKER_LIST_PRICE_ONLY,
                      "delta": delta(0.01, 0.003, 0.019)}  # no empate, a primeira do relatório
    straddling = {"code": codes.RANKER_LIST_PRICE_ONLY, "delta_val": delta(0.0, -0.01, 0.01)}
    assert evidence.verdict([straddling, served]) == {"code": codes.VERDICT_INCONCLUSIVE, "ranker": None,
                                                      "delta": None}
    far = {"code": codes.RANKER_RANDOM, "delta_val": delta(-0.3, -0.35, -0.25)}
    near = {"code": codes.RANKER_LIST_PRICE_ONLY, "delta_val": delta(-0.046, -0.068, -0.025)}
    assert evidence.verdict([far, near, served]) == {"code": codes.VERDICT_REFERENCE_AHEAD,
                                                     "ranker": codes.RANKER_LIST_PRICE_ONLY,
                                                     "delta": delta(-0.046, -0.068, -0.025)}


def test_fixture_verdict_is_served(evidence_path):
    assert evidence.load(evidence_path)["without_no_outcome_verdict"]["code"] == codes.VERDICT_REFERENCE_BEHIND


@pytest.mark.parametrize("stamp", [codes.RANKER_AGE_MAX_CYCLE_ONLY, None])
def test_a_result_of_another_rule_is_refused(tmp_path, stamp):
    """Um resultado antigo (ou sem carimbo) nunca aparece como o da regra servida."""
    stale = json.loads(json.dumps(EVIDENCE_RESULTS))
    if stamp is None:
        del stale["design"]["served_rule"]
    else:
        stale["design"]["served_rule"] = stamp
    path = write_evidence(tmp_path / "r.json", stale)
    with pytest.raises(DataError) as error:
        evidence.load(path)
    assert (error.value.code, error.value.params) == (codes.EVIDENCE_UNAVAILABLE, {"file": "r.json"})


def test_unknown_strategy_code_is_refused(tmp_path):
    broken = json.loads(json.dumps(EVIDENCE_RESULTS))
    broken["summary"][0]["code"] = "alta_chance"
    with pytest.raises(DataError):
        evidence.load(write_evidence(tmp_path / "r.json", broken))


def test_api_serves_evidence_and_503_without_it(raw_dir, evidence_path, tmp_path):
    response = TestClient(create_app(raw_dir, evidence_path)).get("/api/evidence")
    assert response.status_code == 200
    assert Evidence.model_validate(response.json()).model_dump(mode="json") == response.json()
    missing = TestClient(create_app(raw_dir, tmp_path / "nada.json")).get("/api/evidence")
    assert missing.status_code == 503
    assert missing.json()["code"] == codes.EVIDENCE_UNAVAILABLE and missing.json()["params"] == {"file": "nada.json"}


def test_evidence_does_not_need_the_csvs(evidence_path, tmp_path):
    assert TestClient(create_app(tmp_path / "sem-csv", evidence_path)).get("/api/evidence").status_code == 200


def test_committed_result_is_served_with_the_audited_numbers():
    """O resultado versionado (gerado com os CSVs auditados) é o que a página mostra."""
    result = evidence.load(policy.EVIDENCE_PATH)
    rankers = {r["code"]: r for r in result["rankers"]}
    without = {r["code"]: r for r in result["without_no_outcome"]}
    assert result["design"]["audited_data"] is True and len(result["design"]["cuts"]) == 7
    served, previous = rankers[codes.SERVED_RANKER], rankers[codes.RANKER_AGE_MAX_CYCLE_ONLY]
    assert (served["val_at_k"], previous["val_at_k"], rankers["list_price_only"]["val_at_k"]) == (0.584, 0.569, 0.538)
    assert previous["delta_val"] == delta(-0.015, -0.027, -0.002)
    assert rankers["list_price_only"]["delta_val"] == delta(-0.046, -0.068, -0.025)
    # A limitação principal: sem as que nunca fecham, "só preço" fica à frente da regra servida.
    assert (without[codes.SERVED_RANKER]["val_at_k"], without["list_price_only"]["val_at_k"]) == (0.781, 0.791)
    assert result["without_no_outcome_verdict"] == {"code": codes.VERDICT_REFERENCE_BEHIND,
                                                    "ranker": codes.RANKER_LIST_PRICE_ONLY,
                                                    "delta": delta(0.01, 0.003, 0.019)}
