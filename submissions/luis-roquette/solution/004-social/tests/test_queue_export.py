from __future__ import annotations

import csv
import io
import json
import os
import tempfile
import unittest
from contextlib import closing
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import streamlit as st
from streamlit.testing.v1 import AppTest

from analysis import (HISTORICAL_METHOD_VERSIONS, analysis_report, decision_baseline,
                      executive_summary, export_evidence)
from storage import connect, list_decisions, record_decision, record_import, record_outcome
from tests.helpers import csv_bytes
from tests.test_app import APP, valid_upload
from tests.test_exports import parse_export, sample_result
from tests.test_storage import decision_event, import_event, outcome_event


class CompleteQueueExportTests(unittest.TestCase):
    def test_fourth_ui_action_download_and_reopened_baseline_preserve_complete_priority(self):
        base = list(csv.DictReader(io.StringIO(valid_upload().decode())))
        upload = csv_bytes([{**row, "id": f"{category}-{row['id']}",
                             "content_id": f"{category}-{row['content_id']}", "content_category": category}
                            for category in ("one", "two", "three", "four") for row in base])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "queue.sqlite3"
            with patch.dict(os.environ, {"SOCIAL_COCKPIT_DB_PATH": str(path)}):
                app = AppTest.from_file(str(APP), default_timeout=20).run()
                with patch("streamlit.download_button", wraps=st.download_button) as download:
                    app.file_uploader[0].set_value(("four.csv", upload, "text/csv")).run()
                self.assertFalse(app.exception)
                result = app.session_state["active_result"]
                queue = result["all_recommendations"]
                self.assertEqual(len(queue), 4)
                self.assertEqual(result["recommendations"], queue[:3])
                payload = next(call.args[1] for call in download.call_args_list
                               if call.args[0] == "Baixar evidências e decisões (CSV)")
                self.assertEqual(payload, export_evidence(result, []))
                rows = parse_export(payload)
                self.assertEqual(csv.field_size_limit(), 131072)
                exported = [row for row in rows if row["record_type"] == "recommendation"]
                self.assertEqual([row["evidence_id"] for row in exported], [item["evidence_id"] for item in queue])
                for rank, (item, row) in enumerate(zip(queue, exported, strict=True), 1):
                    self.assertEqual(int(row["rank"]), rank)
                    self.assertEqual(float(row["priority"]), item["priority"])
                    for key in ("priority_values", "normalization", "frequency_hypothesis", "context"):
                        self.assertEqual(json.loads(row[key]), item[key])
                    for key, value in item["priority_components"].items():
                        self.assertEqual(float(row[key]), value)
                    for key in ("action", "action_type", "owner", "execution_window", "review_window"):
                        self.assertEqual(row[key], item[key])
                    self.assertTrue(any(e["record_type"] == "evidence" and e["evidence_id"] == item["evidence_id"] for e in rows))
                    self.assertTrue(any(e["record_type"] == "source_ref" and e["evidence_id"] == item["evidence_id"] for e in rows))
                    snapshot = decision_baseline(item["evidence_snapshot"])["evidence_snapshot"]
                    self.assertEqual(snapshot["recommendation"], {"rank": rank, **{
                        key: value for key, value in item.items() if key != "evidence_snapshot"}})
                fourth = queue[3]
                for report in (executive_summary(result, []), analysis_report(result).split("## O que os dados", 1)[0]):
                    self.assertNotIn(fourth["evidence_id"], report)
                app.selectbox(key="decision_recommendation").set_value(fourth).run()
                app.button(key="save_decision").click().run()
                self.assertFalse(app.exception)
                with closing(connect(path)) as conn:
                    history = list_decisions(conn)
                baseline = history[0]["baseline"]
                expected = decision_baseline(fourth["evidence_snapshot"])
                self.assertEqual(baseline["evidence_snapshot"], expected["evidence_snapshot"])
                history_rows = parse_export(export_evidence(result, history))
                decision = next(row for row in history_rows if row["record_type"] == "decision")
                serialized = decision["baseline"] or "".join(json.loads(row["field_value"]) for row in history_rows
                    if row["record_type"] == "history_field" and row["field_name"] == "baseline")
                self.assertEqual(json.loads(serialized), baseline)
                saved = deepcopy(expected)
                fourth["normalization"]["views"] = -1
                self.assertEqual(expected, saved)
                with closing(connect(path)) as conn:
                    self.assertEqual(list_decisions(conn)[0]["baseline"], baseline)

    def test_legacy_result_fallback_and_method_22_history_are_preserved(self):
        result = sample_result()
        self.assertNotIn("all_recommendations", result)
        self.assertEqual(len([row for row in parse_export(export_evidence(result, []))
                              if row["record_type"] == "recommendation"]), 1)
        self.assertIn("2.2.0", HISTORICAL_METHOD_VERSIONS)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "legacy.sqlite3"
            with closing(connect(path)) as conn:
                record_import(conn, import_event("source-a"))
                record_import(conn, import_event("source-b"))
                event = decision_event(method_version="2.2.0")
                decision_id = record_decision(conn, event)
                record_outcome(conn, outcome_event(decision_id=decision_id, method_version="2.2.0"))
            with closing(connect(path)) as conn:
                saved = list_decisions(conn)[0]
            self.assertEqual(saved["baseline"], event["baseline"])
            self.assertEqual(saved["method_version"], "2.2.0")
            self.assertEqual((saved["outcomes"][0]["status"], saved["outcomes"][0]["reason"]),
                             ("pending", "method_mismatch"))
