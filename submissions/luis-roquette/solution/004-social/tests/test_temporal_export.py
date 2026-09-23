from __future__ import annotations

import csv
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import streamlit as st
from streamlit.testing.v1 import AppTest

from analysis import analysis_report, executive_summary, export_evidence
from tests.test_app import APP, valid_upload
from tests.test_reconstruction import long_label_result


class TemporalExportTests(unittest.TestCase):
    def test_ui_week_month_and_explicit_interval_round_trip_downloads(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {
            "SOCIAL_COCKPIT_DB_PATH": str(Path(directory) / "period.sqlite3")
        }):
            app = AppTest.from_file(str(APP), default_timeout=20).run()
            app.file_uploader[0].set_value(("period.csv", valid_upload(), "text/csv")).run()
            for mode, start, end, effective_start, partial in (
                ("Semana ISO", "2025-01-13", "2025-01-19", "2025-01-13", True),
                ("Mês calendário", "2025-01-01", "2025-01-31", "2025-01-01", True),
                ("Intervalo personalizado", "2025-01-08", "2025-01-14", "2025-01-08", False),
            ):
                with self.subTest(mode=mode), patch("streamlit.download_button", wraps=st.download_button) as download:
                    app.selectbox(key="period_mode").set_value(mode).run()
                    self.assertFalse(app.exception)
                    result = app.session_state["active_result"]
                    scope = result["scope"]
                    expected = {"period_mode": mode, "requested_start": start + "T00:00:00",
                                "requested_end": end + "T00:00:00", "partial_period": partial}
                    self.assertEqual({key: scope[key] for key in expected}, expected)
                    self.assertEqual(scope["target_start"], effective_start + "T00:00:00")
                    self.assertEqual(scope["target_end"], "2025-01-14T00:00:00")
                    calls = {call.args[0]: call.args[1] for call in download.call_args_list}
                    payload = calls["Baixar evidências e decisões (CSV)"]
                    rows = list(csv.DictReader(io.StringIO(payload.decode())))
                    self.assertEqual(json.loads(rows[0]["scope"]), scope)
                    self.assertEqual(csv.field_size_limit(), 131072)
                    self.assertEqual(payload, export_evidence(result, []))
                    page = calls["Baixar resumo executivo (HTML)"].decode()
                    self.assertEqual(page, executive_summary(result, []))
                    for text in (page, analysis_report(result)):
                        self.assertIn(mode, text)
                        self.assertIn(start + "T00:00:00", text)
                        self.assertIn(end + "T00:00:00", text)
                        self.assertIn("cobertura temporal parcial (janela incompleta)" if partial else
                                      "cobertura temporal completa no intervalo solicitado", text)

    def test_temporal_state_precedes_long_filters_and_does_not_infer_legacy_metadata(self):
        _, result = long_label_result()
        before = executive_summary(result, [])
        self.assertNotIn("cobertura temporal", before)
        result["scope"].update(period_mode="Mês calendário", requested_start="2025-01-01T00:00:00",
                               requested_end="2025-01-31T00:00:00", partial_period=True)
        page = executive_summary(result, [])
        self.assertIn("cobertura temporal parcial (janela incompleta)", page)
        self.assertLess(page.index("cobertura temporal parcial"), page.index("Plataforma"))
        rows = list(csv.DictReader(io.StringIO(export_evidence(result, []).decode())))
        parts = [row for row in rows if row["record_type"] == "analysis_field" and row["evidence_id"] == "" and row["field_name"] == "summary.scope"]
        scope = json.loads("".join(json.loads(row["field_value"]) for row in parts))
        self.assertEqual(scope, result["scope"])


if __name__ == "__main__":
    unittest.main()
