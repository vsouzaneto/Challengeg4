"""Build development first; only explicit, frozen review decisions release test."""

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import tempfile
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

import joblib
import pandas as pd

from support_copilot.analytics import (
    add_operational_fields,
    grouped_bottlenecks,
    operational_summary,
    recoverable_excess_hours,
    satisfaction_associations,
)
from support_copilot.data import (
    ANALYTICS_SCHEMA_VERSION,
    CUSTOMER_TAXONOMY,
    GROUPING_VERSION,
    IT_TAXONOMY,
    SANITIZER_VERSION,
    atomic_json,
    content_hash,
    load_customer_analytics,
    load_customer_tickets,
    load_it_tickets,
    make_split,
    write_manifest,
)
from support_copilot.decision import derive_signals
from support_copilot.modeling import Prediction, evaluate_frozen_test, train_domain_model
from support_copilot.retrieval import (
    fit_retriever,
    load_retrieval_policy,
    prepare_review,
    verify_test_gate,
)
from support_copilot.ui import assess_ticket, current_environment, logical_payload


def _atomic_csv(frame: pd.DataFrame, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", dir=destination.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            frame.to_csv(stream, index=False, lineterminator="\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    except OSError:
        raise ValueError("artifact_write_failed") from None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _records(frame: pd.DataFrame) -> list[dict]:
    return json.loads(frame.to_json(orient="records"))


def _register_artifact(manifest: dict, output: Path, key: str, relative: str,
                       artifact_type: str, logical_value: object, *, domain="customer",
                       dependencies=None) -> None:
    destination = output / relative
    manifest["artifacts"][key] = {
        "path": relative, "type": artifact_type, "schema_version": 1,
        "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
        "logical_sha256": content_hash(logical_value), "domain": domain,
        "dependencies": dependencies if dependencies is not None else
        ["data.customer.train", "data.customer.calibration"],
        "status": "ready", "reason": None,
    }


def _build(customer: Path, it: Path, output: Path) -> dict:
    solution = Path(__file__).resolve().parents[1]
    configuration = json.loads((solution / "configuration.json").read_text())
    stamp = datetime.fromisoformat(configuration["evaluation_created_at"])
    if (configuration.get("schema_version") != 1 or configuration.get("seed") != 42
            or stamp.tzinfo is None or stamp > datetime.now(UTC)):
        raise ValueError("invalid_evaluation_configuration")
    configuration.update(
        sanitizer=SANITIZER_VERSION,
        analytics_schema=ANALYTICS_SCHEMA_VERSION,
        grouping=GROUPING_VERSION,
        mode="development_then_locked_test",
        protocol=1,
    )
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=solution, text=True
    ).strip()
    # Include uncommitted/untracked implementation bytes, not raw/runtime/artifacts.
    fingerprint = current_environment()["code"]
    manifest = {
        "schema_version": 1, "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "code_revision": f"{revision}+code.{fingerprint}",
        "configuration_sha256": content_hash(configuration),
        "lock_sha256": hashlib.sha256((solution / "requirements.lock").read_bytes()).hexdigest(),
        "runtime": {"python": platform.python_version(), "dependencies": {
            name: importlib.metadata.version(name)
            for name in (line.split("==")[0] for line in
                         (solution / "requirements.lock").read_text().splitlines() if "==" in line)
        }},
        "sources": {}, "splits": {}, "models": {},
        "retrieval": {
            "status": "unavailable", "reason": "not_implemented_human_review_pending",
            "reference_split": None, "index_version": None, "policy_version": None,
            "packet_ids": [], "rubric_sha256": {}, "lock_sha256": None,
            "threshold": None, "eligible_queries": None, "reviewed_queries": 0,
        },
        "artifacts": {},
    }
    frames, splits, results = {}, {}, {}
    customer_split = None
    for domain, path, loader, taxonomy in (
        ("customer", customer, load_customer_tickets, CUSTOMER_TAXONOMY),
        ("it", it, load_it_tickets, IT_TAXONOMY),
    ):
        frame = loader(path)
        split = make_split(frame, "target")
        frames[domain], splits[domain] = frame, split
        if domain == "customer":
            customer_split = split
        manifest["sources"][domain] = frame.attrs["source"]
        manifest["splits"][domain] = split.manifest
        manifest["models"][domain] = {
            "status": "unavailable", "reason": "not_implemented", "candidate": None,
            "features": ["text"], "taxonomy": list(taxonomy), "cv": None,
            "calibration": None, "model_version": None, "automation_enabled": False,
            "threshold": None, "configuration_lock_sha256": None,
        }
        for partition in ("train", "calibration"):
            part = getattr(split, partition)
            relative = f"data/{domain}-{partition}.json"
            records = part.to_dict("records")
            destination = output / relative
            atomic_json(records, destination)
            manifest["artifacts"][f"data.{domain}.{partition}"] = {
                "path": relative, "type": "sanitized-frame", "schema_version": 1,
                "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
                "logical_sha256": content_hash(records), "domain": domain,
                "dependencies": [f"sources.{domain}", f"splits.{domain}"],
                "status": "ready", "reason": None,
            }
        for key in (f"models.{domain}", f"queue.{domain}"):
            manifest["artifacts"][key] = {
                "path": None, "type": "future", "schema_version": 1,
                "sha256": None, "logical_sha256": None, "domain": domain,
                "dependencies": [], "status": "unavailable",
                "reason": "not_implemented_test_sealed",
            }

    if customer_split is None:
        raise ValueError("analytics_customer_data_unavailable")
    analytics_frame = load_customer_analytics(customer)
    analytics_source = analytics_frame.attrs["source"]
    manifest["sources"]["customer"]["analytics"] = {
        "lane": analytics_source["lane"],
        "data_version": analytics_source["data_version"],
        "sanitizer_version": analytics_source["sanitizer_version"],
        "allowed_columns": analytics_source["allowed_columns"],
        "quality": analytics_source["quality"],
    }
    analytics_records = analytics_frame.to_dict("records")
    analytics_relative = "data/customer-analytics.json"
    atomic_json(analytics_records, output / analytics_relative)
    _register_artifact(
        manifest, output, "data.customer.analytics", analytics_relative, "sanitized-frame",
        analytics_records, dependencies=["sources.customer"],
    )
    operational = add_operational_fields(analytics_frame)
    operational.attrs = analytics_frame.attrs.copy()
    bottlenecks = grouped_bottlenecks(operational)
    waste = recoverable_excess_hours(operational)
    satisfaction = satisfaction_associations(operational)
    summary = operational_summary(operational)
    summary_payload = asdict(summary)
    satisfaction_payload = asdict(satisfaction)
    reports = {
        "analytics.operational_summary": (
            "analytics/operational-summary.json", "operational-summary", summary_payload
        ),
        "analytics.satisfaction_model": (
            "analytics/satisfaction-model.json", "satisfaction-model", satisfaction_payload
        ),
    }
    for key, (relative, artifact_type, payload) in reports.items():
        atomic_json(payload, output / relative)
        _register_artifact(
            manifest, output, key, relative, artifact_type, payload,
            dependencies=["data.customer.analytics"],
        )

    association_columns = [
        "feature", "level", "n", "mean_rating", "median_rating", "association_metric",
        "association_value", "evidence_kind",
    ]
    associations = pd.DataFrame(satisfaction.univariate_effects, columns=association_columns)
    automation = pd.DataFrame([{
        "opportunity": "cross_domain_automation_evidence",
        "customer_evidence": "operational_diagnostic_available",
        "it_evidence": "operational_outcomes_absent",
        "relationship": "aggregate_only_no_record_join",
        "status": "unavailable",
        "reason": "Dataset IT não contém desfecho operacional nem chave com Customer Support.",
    }])
    tables = {
        "analytics.bottlenecks": ("analytics/bottlenecks.csv", bottlenecks),
        "analytics.waste_opportunities": ("analytics/waste-opportunities.csv", waste),
        "analytics.satisfaction_associations": (
            "analytics/satisfaction-associations.csv", associations
        ),
        "analytics.automation_opportunities": (
            "analytics/automation-opportunities.csv", automation
        ),
    }
    for key, (relative, table) in tables.items():
        _atomic_csv(table, output / relative)
        _register_artifact(
            manifest, output, key, relative, "csv-report", _records(table),
            dependencies=["data.customer.analytics"],
        )

    def save(key, relative, payload, artifact_type="json", domain=None, dependencies=()):
        destination = output / relative
        if artifact_type in {"domain-model", "retriever"}:
            destination.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(payload, destination)
        else:
            atomic_json(payload, destination)
        _register_artifact(manifest, output, key, relative, artifact_type,
                           logical_payload(payload), domain=domain,
                           dependencies=list(dependencies))

    for domain, split in splits.items():
        result = train_domain_model(domain, split)
        results[domain] = result
        manifest["models"][domain] = {
            "status": result.status, "reason": ",".join(result.reason_codes),
            "candidate": result.selection.candidate, "features": ["text"],
            "taxonomy": list(CUSTOMER_TAXONOMY if domain == "customer" else IT_TAXONOMY),
            "cv": asdict(result.selection), "calibration": result.development,
            "model_version": result.policy.model_version,
            "automation_enabled": result.policy.automation_enabled,
            "threshold": result.policy.threshold,
            "configuration_lock_sha256": result.configuration_sha256,
        }
        save(f"policies.{domain}", f"models/{domain}-policy.json", asdict(result.policy),
             domain=domain, dependencies=(f"sources.{domain}", f"splits.{domain}"))
        if result.model is not None:
            save(f"models.{domain}", f"models/{domain}.joblib", result, "domain-model",
                 domain, (f"policies.{domain}", f"data.{domain}.train",
                          f"data.{domain}.calibration"))
        else:
            manifest["artifacts"][f"models.{domain}"]["reason"] = result.status
        predictions = [asdict(result.model.predict_one(row.text)) if result.model else
                       asdict(Prediction(domain, "unsupported", reason_codes=result.reason_codes))
                       for row in split.calibration.itertuples()]
        save(f"predictions.{domain}.development", f"models/{domain}-development.json",
             {"ids": split.calibration.ticket_id.tolist(), "predictions": predictions},
             domain=domain, dependencies=(f"policies.{domain}",))
    save("risk_policy", "risk-policy.json",
         {domain: asdict(result.policy) for domain, result in results.items()},
         dependencies=("policies.customer", "policies.it"))

    retriever = fit_retriever(
        customer_split.train, split_manifest=customer_split.manifest,
        source_sha256=manifest["sources"]["customer"]["sha256"],
        configuration_sha256=manifest["configuration_sha256"],
    )
    save("retrieval.customer", "retrieval/customer.joblib", retriever, "retriever", "customer",
         ("data.customer.train", "splits.customer"))

    def signals_for(frame):
        result = results["customer"]
        return {row["ticket_id"]: derive_signals(
            row["text"], domain="customer", ticket_id=row["ticket_id"],
            priority=row["Ticket Priority"], prediction=result.model.predict_one(row["text"])
            if result.model else Prediction("customer", "unsupported",
                                            reason_codes=result.reason_codes),
            policy=result.policy, artifact_valid=True, privacy_passed=True,
        ) for row in frame.to_dict("records")}

    packet = prepare_review(retriever, customer_split.calibration,
                            signals_for(customer_split.calibration), artifacts=output,
                            created_at=configuration["evaluation_created_at"])
    retrieval_policy = None
    model_locks = {domain: result.policy for domain, result in results.items()}
    if (output / "review/retrieval-policy-lock.json").exists():
        retrieval_policy = load_retrieval_policy(retriever, output)
        verify_test_gate(retriever, output, model_locks)
    elif (output / "review/retrieval-test-opened.json").exists():
        raise ValueError("test_opened_lock_missing")

    metrics = {"status": "sealed", "domains": {
        domain: {"status": "sealed", "reason": "retrieval_review_decision_pending"}
        for domain in results}}
    if retrieval_policy is not None:
        metrics["status"] = "released_after_locks"
        for domain, split in splits.items():
            # This is the only final payload materialization, AFTER verify_test_gate.
            test = frames[domain].set_index("ticket_id").loc[split.test.ticket_id].reset_index()
            test["text_group_id"] = split.test.text_group_id.to_numpy()
            save(f"data.{domain}.test", f"data/{domain}-test.json", test.to_dict("records"),
                 "sanitized-frame", domain, (f"sources.{domain}", f"splits.{domain}"))
            metrics["domains"][domain] = asdict(evaluate_frozen_test(
                results[domain], test, results[domain].policy))
            if domain == "customer":
                prepare_review(retriever, test, signals_for(test), artifacts=output,
                               split="test", model_locks=model_locks,
                               created_at=configuration["evaluation_created_at"])
                queue = [assess_ticket(row, results[domain].model, results[domain].policy,
                                       retriever, retrieval_policy) for row in
                         test.to_dict("records")]
                queue.sort(key=lambda row: (*[-v for v in row["priority_score"]],
                                           row["ticket_id"]))
                save("queue.customer", "queue/customer-test.json", queue, domain="customer",
                     dependencies=("data.customer.test", "policies.customer",
                                   "retrieval.customer", "retrieval.policy")
                     + (("models.customer",) if results[domain].model is not None else ()))
                _atomic_csv(pd.DataFrame([{"ticket_id": row["ticket_id"],
                                          "text": row["text"], "priority": row["priority"],
                                          "gate_action": row["route"]["action"]}
                                         for row in queue], columns=["ticket_id", "text",
                                         "priority", "gate_action"]),
                            output / "queue/customer-test.csv")
        save("retrieval.policy", "retrieval/policy.json", asdict(retrieval_policy),
             dependencies=("retrieval.customer",))
    else:
        manifest["artifacts"]["queue.customer"]["reason"] = "test_sealed_review_pending"
        manifest["artifacts"]["retrieval.policy"] = {
            "path": None, "type": "json", "schema_version": 1, "sha256": None,
            "logical_sha256": None, "domain": "customer", "dependencies": [],
            "status": "unavailable", "reason": packet["status"],
        }
    save("models.metrics", "models/metrics.json", metrics)
    save("retrieval.metrics", "retrieval/metrics.json", {
        "status": packet["status"] if retrieval_policy is None else retrieval_policy.status,
        "eligible": packet["eligible"], "reviewed": 0,
        "reason": "human_evaluation_not_completed", "complete": False,
    })
    manifest["retrieval"] = {
        "status": packet["status"] if retrieval_policy is None else retrieval_policy.status,
        "reason": "human_evaluation_pending", "reference_split": customer_split.split_version,
        "index_version": retriever.index_version,
        "policy_version": retrieval_policy.policy_version if retrieval_policy else None,
        "packet_ids": [packet["packet_id"]], "rubric_sha256": {},
        "lock_sha256": hashlib.sha256((output / "review/retrieval-policy-lock.json").read_bytes())
        .hexdigest() if retrieval_policy else None,
        "threshold": retrieval_policy.threshold if retrieval_policy else None,
        "eligible_queries": packet["eligible"], "reviewed_queries": 0,
    }
    for path in sorted((output / "review").glob("*")):
        if path.suffix == ".json":
            value, kind = json.loads(path.read_text()), "json"
        else:
            value, kind = _records(pd.read_csv(path, keep_default_na=False)), "review-template"
        _register_artifact(manifest, output, "review." + path.stem,
                           str(path.relative_to(output)), kind, value, dependencies=[])
    write_manifest(manifest, output / "manifest.json")
    return manifest


def reproduce(customer: Path, it: Path, output: Path) -> dict:
    """Stage complete files; publish manifest last, never touch runtime decisions."""
    output = output.absolute()
    if output.is_symlink() or any(path.is_symlink() for path in output.parents):
        raise ValueError("artifact_root_symlink")
    output.mkdir(parents=True, exist_ok=True)
    if any(path.is_symlink() for path in output.rglob("*")):
        raise ValueError("artifact_symlink_rejected")
    with tempfile.TemporaryDirectory(prefix=".reproduce-", dir=output.parent) as directory:
        staging = Path(directory)
        if (output / "review").exists():
            shutil.copytree(output / "review", staging / "review", symlinks=False)
        manifest = _build(customer, it, staging)
        for path in sorted(staging.rglob("*")):
            if path.is_file() and path.name != "manifest.json":
                target = output / path.relative_to(staging)
                target.parent.mkdir(parents=True, exist_ok=True)
                os.replace(path, target)
        os.replace(staging / "manifest.json", output / "manifest.json")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--customer", type=Path,
                        default=Path("data/raw/customer_support_tickets.csv"))
    parser.add_argument("--it", type=Path,
                        default=Path("data/raw/all_tickets_processed_improved_v3.csv"))
    parser.add_argument("--output", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    try:
        manifest = reproduce(args.customer, args.it, args.output)
    except (ValueError, OSError, importlib.metadata.PackageNotFoundError) as error:
        parser.exit(2, f"Reprodução indisponível: {error}. Corrija e execute make reproduce.\n")
    for domain in ("customer", "it"):
        source = manifest["sources"][domain]
        split = manifest["splits"][domain]
        print(f"{domain}: source={source['total_rows']}, "
              f"sanitized={source['quality']['sanitized_rows']}, split={split['status']}")
    analytics = manifest["artifacts"]["analytics.operational_summary"]
    print(f"diagnóstico de desenvolvimento: {analytics['status']} ({analytics['path']})")
    print("Diagnóstico histórico estruturado; modelos/retrieval preservam splits próprios.")


if __name__ == "__main__":
    main()
