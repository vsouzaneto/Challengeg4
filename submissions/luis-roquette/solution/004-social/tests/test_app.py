from __future__ import annotations

import os
import atexit
import json
import csv
import io
import sqlite3
import tempfile
import unittest
from copy import deepcopy
from contextlib import closing
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import streamlit as st
from analysis import analyze, export_evidence, load_csv

from streamlit.testing.v1 import AppTest
from streamlit.testing.v1.app_test import TMP_DIR

from tests.helpers import csv_bytes, driver_rows, make_post, sponsorship_rows
from tests.test_exports import historical_log, parse_export
from storage import list_decisions, record_import


APP = Path(__file__).parents[1] / "app.py"
# Streamlit owns this process-wide test directory; close it explicitly before
# Python's finalizer reports implicit cleanup under PYTHONWARNINGS=error.
atexit.register(TMP_DIR.cleanup)


def valid_upload() -> bytes:
    rows: list[dict[str, object]] = []
    for period, start, interactions in (
        ("before", datetime(2025, 1, 1, 12), 4),
        ("current", datetime(2025, 1, 8, 12), 8),
    ):
        for index in range(30):
            rows.append(
                make_post(
                    id=f"{period}-{index}",
                    content_id=f"{period}-content-{index}",
                    creator_id=f"creator-{index % 5}",
                    post_date=(start + timedelta(days=index % 7)).isoformat(),
                    likes=interactions,
                    shares=0,
                    comments_count=0,
                )
            )
    return csv_bytes(rows)


def later_upload(start: datetime | None = None) -> bytes:
    start = start or datetime(2025, 1, 15, 12)
    return csv_bytes(
        [
            make_post(
                id=f"later-{index}",
                content_id=f"later-content-{index}",
                creator_id=f"creator-{index % 5}",
                post_date=(start + timedelta(days=index % 7)).isoformat(),
                likes=9,
                shares=0,
                comments_count=0,
            )
            for index in range(30)
        ]
    )


def driver_upload() -> bytes:
    return csv_bytes(driver_rows([1.0, 1.2, 0.8]))


def sponsorship_upload() -> bytes:
    rows = sponsorship_rows().drop(columns=["source_row_id"], errors="ignore")
    rows["is_sponsored"] = rows["is_sponsored"].map({True: "TRUE", False: "FALSE"})
    return csv_bytes(rows.to_dict(orient="records"))


class AppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.previous = os.environ.get("SOCIAL_COCKPIT_DB_PATH")
        os.environ["SOCIAL_COCKPIT_DB_PATH"] = str(Path(self.directory.name) / "cockpit.sqlite3")

    def tearDown(self) -> None:
        if self.previous is None:
            os.environ.pop("SOCIAL_COCKPIT_DB_PATH", None)
        else:
            os.environ["SOCIAL_COCKPIT_DB_PATH"] = self.previous
        self.directory.cleanup()

    def app(self) -> AppTest:
        return AppTest.from_file(str(APP), default_timeout=20).run()

    def stored(self):
        with closing(sqlite3.connect(Path(self.directory.name) / "cockpit.sqlite3")) as connection:
            return list_decisions(connection)

    def test_dashboard_shows_multivariate_answers_and_four_week_strategy(self):
        app = self.app()
        app.file_uploader[0].set_value(("drivers.csv", driver_upload(), "text/csv")).run()
        text = "\n".join(item.value for item in app.markdown)
        for expected in ("Força", "Cobertura", "Estabilidade", "Evidência", "O que mudaria a decisão", "Semana 1", "Semana 4"):
            self.assertIn(expected, text)

    def test_financial_scenario_is_manual_ephemeral_and_does_not_change_evidence(self):
        app = self.app()
        app.file_uploader[0].set_value(("sponsorship.csv", sponsorship_upload(), "text/csv")).run()
        app.selectbox(key="period_mode").set_value("Todo o histórico").run()
        before = deepcopy(app.session_state["active_result"])
        selected = before["sponsorship"]["strata"][0]["evidence_id"]
        app.selectbox(key="scenario_sponsorship_stratum").set_value(selected)
        for key, value in {
            "scenario_sponsorship_cost": 1_000.0,
            "scenario_production_cost": 200.0,
            "scenario_value_per_conversion": 100.0,
            "scenario_organic_rate": 0.01,
            "scenario_sponsored_rate": 0.013,
        }.items():
            app.number_input(key=key).set_value(value)
        app.button(key="calculate_sponsorship_scenario").click().run()
        self.assertIn("Cenário manual", "\n".join(item.value for item in app.markdown))
        self.assertEqual(app.session_state["active_result"], before)
        self.assertNotIn(b"value_per_conversion", export_evidence(before, []))

    def test_operational_filters_do_not_recompute_full_history_answers(self):
        app = self.app()
        app.file_uploader[0].set_value(("drivers.csv", driver_upload(), "text/csv")).run()
        answers = deepcopy(app.session_state["head_answers"])
        app.multiselect(key="filter_content_type").set_value(["text"]).run()
        self.assertEqual(app.session_state["head_answers"], answers)

    def test_baseline_above_int64_survives_reopen_and_download(self):
        rows = list(csv.DictReader(io.StringIO(valid_upload().decode())))
        for row in rows[30:32]:
            row["views"] = 2**63 - 1
        app = self.app()
        app.file_uploader[0].set_value(("overflow.csv", csv_bytes(rows), "text/csv")).run()
        snapshot = app.session_state["active_result"]["recommendations"][0]["evidence_snapshot"]
        app.button(key="save_decision").click().run()
        self.assertFalse(app.exception)
        expected = 2 * (2**63 - 1) + 28 * 100
        baseline = self.stored()[0]["baseline"]
        self.assertEqual(baseline["views"], expected)
        self.assertEqual(baseline["evidence_snapshot"], snapshot)
        with patch("streamlit.download_button", wraps=st.download_button) as download:
            reopened = self.app()
            reopened.file_uploader[0].set_value(("overflow.csv", csv_bytes(rows), "text/csv")).run()
            self.assertFalse(reopened.exception)
            payload = next(call.args[1] for call in reversed(download.call_args_list) if call.args[0] == "Baixar evidências e decisões (CSV)")
        decision = next(row for row in parse_export(payload) if row["record_type"] == "decision")
        self.assertEqual(json.loads(decision["baseline"])["views"], expected)

    @patch("storage.utc_now")
    def test_segment_outcome_and_historical_snapshot_ignore_new_active_filters(self, clock):
        clock.return_value = datetime(2025, 1, 14, 18, tzinfo=timezone.utc)
        tech = list(csv.DictReader(io.StringIO(valid_upload().decode())))
        beauty = [{**row, "id": "beauty-" + row["id"], "content_id": "beauty-" + row["content_id"], "content_category": "beauty"} for row in tech]
        raw = csv_bytes(tech + beauty)
        app = self.app()
        app.file_uploader[0].set_value(("mixed.csv", raw, "text/csv")).run()
        selected = next(item for item in app.session_state["active_result"]["recommendations"] if item["context"]["content_category"] == "tech")
        app.selectbox(key="decision_recommendation").set_value(selected).run()
        app.button(key="save_decision").click().run()
        saved = self.stored()[0]
        reopened = self.app()
        history = next(item for item in reopened.expander if item.label.startswith("Evidência histórica salva"))
        self.assertEqual(json.loads(history.json[1].value), saved["baseline"]["evidence_snapshot"])
        reopened.file_uploader[0].set_value(("mixed.csv", raw, "text/csv")).run()
        reopened.multiselect(key="filter_content_category").set_value(["beauty"]).run()
        self.assertFalse(reopened.exception)
        self.assertTrue(all(item["context"]["content_category"] == "beauty" for item in reopened.session_state["active_result"]["recommendations"]))
        history = next(item for item in reopened.expander if item.label.startswith("Evidência histórica salva"))
        self.assertEqual(json.loads(history.json[1].value), saved["baseline"]["evidence_snapshot"])
        refs = history.dataframe[0].value
        self.assertEqual((len(refs), set(refs["papel"]), set(refs["content_category"])), (60, {"target", "comparator"}, {"tech"}))
        self.assertFalse(refs["source_line"].isna().any())
        clock.return_value = datetime(2025, 1, 22, 18, tzinfo=timezone.utc)
        later = list(csv.DictReader(io.StringIO(later_upload().decode())))
        later += [{**row, "id": "beauty-" + row["id"], "content_id": "beauty-" + row["content_id"], "content_category": "beauty", "likes": 99} for row in later]
        reopened.file_uploader[0].set_value(("later-mixed.csv", csv_bytes(later), "text/csv")).run()
        reopened.button(key="save_outcome").click().run()
        self.assertFalse(reopened.exception)
        outcome = self.stored()[0]["outcomes"][0]
        self.assertEqual((outcome["status"], outcome["observed"]["median"], outcome["comparison"]["median_delta"]), ("observed", 9.0, 1.0))
        self.assertEqual(outcome["observed"]["n_rate"], 30)

    def test_production_future_observation_is_pending_and_simulation_is_labeled(self):
        app = self.app()
        app.file_uploader[0].set_value(("social.csv", valid_upload(), "text/csv")).run()
        app.button(key="save_decision").click().run()
        future = (datetime.now(timezone.utc) + timedelta(days=1)).replace(tzinfo=None)
        app.file_uploader[0].set_value(("synthetic-future.csv", later_upload(future), "text/csv")).run()
        app.button(key="save_outcome").click().run()
        self.assertTrue(any("pending — observation_in_future" in item.value for item in app.success))
        with patch.dict(os.environ, {"SOCIAL_COCKPIT_SIMULATION_NOW": "2025-01-22T18:00:00+00:00"}):
            replay = self.app()
            self.assertTrue(any("SIMULAÇÃO / REPLAY RETROSPECTIVO" in item.value for item in replay.warning))

    def test_timezone_custom_dates_and_quality_diagnostics_are_visible(self):
        rows = list(csv.DictReader(io.StringIO(valid_upload().decode())))
        for row in rows:
            row["post_date"] += "+02:00"
            row["engagement_rate"] = "99"
        app = self.app()
        app.file_uploader[0].set_value(("offset.csv", csv_bytes(rows), "text/csv")).run()
        app.selectbox(key="period_mode").set_value("Intervalo personalizado").run()
        self.assertFalse(app.exception)
        self.assertTrue(any("engagement_rate foi ignorada" in item.value for item in app.warning))
        self.assertTrue(app.session_state["active_result"]["scope"]["target_start"].endswith("+02:00"))
        text = " ".join(item.value for item in (*app.markdown, *app.caption))
        for expected in ("Níveis de benchmark tentados", "Contextos sem benchmark suficiente", "estratos elegíveis / sem contraparte", "Audiência condicionada", "30 taxas definidas e 5 creators"):
            self.assertIn(expected, text)

    def test_download_after_reopen_uses_complete_historical_rows(self):
        original, revision, outcome_id = historical_log(Path(self.directory.name) / "cockpit.sqlite3")
        with patch("streamlit.download_button", wraps=st.download_button) as download:
            app = self.app()
            app.file_uploader[0].set_value(("active-c.csv", valid_upload(), "text/csv")).run()
            self.assertFalse(app.exception)
            calls = [call for call in download.call_args_list if call.args[0] == "Baixar evidências e decisões (CSV)"]
            payload = calls[-1].args[1]
        rows = parse_export(payload)
        decisions = {row["decision_id"]: row for row in rows if row["record_type"] == "decision"}
        self.assertEqual(set(decisions), {original, revision})
        self.assertEqual(decisions[revision]["revision_of"], original)
        self.assertEqual(decisions[revision]["source_hash"], "source-a")
        self.assertEqual(decisions[revision]["event_id"], "revision-event")
        self.assertEqual(decisions[revision]["effective_text"], "'+Editado")
        outcome = next(row for row in rows if row["record_type"] == "outcome")
        self.assertEqual((outcome["outcome_id"], outcome["decision_id"], outcome["source_hash"]), (outcome_id, revision, "source-b"))
        self.assertEqual(outcome["decision_source_hash"], "source-a")
        self.assertEqual(outcome["median_delta"], "1.0")
        self.assertEqual(outcome["execution_status"], "yes")
        active = next(row["source_hash"] for row in rows if row["record_type"] == "summary")
        self.assertNotIn(active, {"source-a", "source-b"})
        with patch("streamlit.download_button", wraps=st.download_button) as download:
            reopened = self.app()
            reopened.file_uploader[0].set_value(("active-c.csv", valid_upload(), "text/csv")).run()
            calls = [call for call in download.call_args_list if call.args[0] == "Baixar evidências e decisões (CSV)"]
            self.assertEqual(calls[-1].args[1], payload)

    def test_initial_render_has_title_uploader_source_state_and_history(self) -> None:
        app = self.app()
        self.assertFalse(app.exception)
        self.assertIn("Cockpit de Social Media", app.title[0].value)
        design_markup = "\n".join(item.value for item in app.markdown)
        self.assertIn("Signal Desk / Social Intelligence", design_markup)
        self.assertIn("workflow-rail", design_markup)
        self.assertEqual(app.file_uploader[0].label, "Enviar CSV")
        text = " ".join(item.value for item in (*app.markdown, *app.caption, *app.info))
        self.assertIn("Nenhuma fonte ativa", text)
        self.assertIn("Histórico de decisões", [item.value for item in app.subheader])

    def test_valid_then_invalid_upload_preserves_active_analysis(self) -> None:
        app = self.app()
        app.file_uploader[0].set_value(("social.csv", valid_upload(), "text/csv")).run()
        self.assertFalse(app.exception)
        active = next(item.value for item in app.caption if "Fonte ativa" in item.value)
        self.assertIn("60 linhas", active)
        self.assertGreaterEqual(len(app.metric), 3)
        self.assertEqual(len(app.download_button), 2)

        app.file_uploader[0].set_value(("invalid.csv", b"id\n1\n", "text/csv")).run()
        self.assertFalse(app.exception)
        self.assertTrue(any("Arquivo rejeitado" in item.value for item in app.error))
        self.assertTrue(any(item.value == active for item in app.caption))
        self.assertGreaterEqual(len(app.metric), 3)

    def test_priority_drilldown_and_decision_survive_new_session(self) -> None:
        app = self.app()
        app.file_uploader[0].set_value(("social.csv", valid_upload(), "text/csv")).run()
        labels = [item.label for item in app.number_input]
        self.assertEqual(labels, ["Impacto", "Força", "Atualidade"])
        self.assertTrue(any("Registros de origem" in item.label for item in app.expander))
        app.selectbox(key="decision_status").set_value("accepted")
        app.button(key="save_decision").click().run()
        self.assertTrue(any("Decisão registrada" in item.value for item in app.success))
        with closing(sqlite3.connect(Path(self.directory.name) / "cockpit.sqlite3")) as connection:
            baseline = json.loads(connection.execute("SELECT baseline_json FROM decisions").fetchone()[0])
        self.assertEqual(baseline["n_rate"], 30)
        self.assertEqual(baseline["creators"], 5)
        self.assertEqual(len(baseline["source_row_ids"]), 30)

        reopened = self.app()
        self.assertFalse(reopened.exception)
        self.assertTrue(any("accepted" in item.value for item in reopened.markdown))
        self.assertTrue(any("Reenvie o CSV" in item.value for item in reopened.caption))

    def test_priority_renders_engine_evidence_before_source_references(self) -> None:
        app = self.app()
        app.file_uploader[0].set_value(("social.csv", valid_upload(), "text/csv")).run()
        text = "\n".join(item.value for item in app.markdown)
        for expected in (
            "Taxa-alvo ERv (%): `8.0`", "Volume-alvo — visualizações / interações: 3.000 / 240",
            "Benchmark — mediana ERv (%): `4.0`", "Benchmark — quartis Q1 / Q3 ERv (%): `4.0` / `4.0`",
            "Delta ERv (p.p.): `4.0`", "Amostra-alvo — posts elegíveis / creators: 30 / 5",
            "Amostra do benchmark — posts elegíveis / creators: 30 / 5",
            "Contexto solicitado:", "Contexto efetivo:", "Nível efetivo / fallback: mesmo contexto; período anterior de igual duração",
            "Suficiência: suficiente", "Força da evidência (C): `0.06`", "Referências de origem:",
        ):
            self.assertIn(expected, text)
        self.assertLess(text.index("Taxa-alvo"), text.index("Referências de origem"))
        drilldown = next(item for item in app.expander if item.label == "Registros de origem e contexto")
        contexts = [json.loads(item.value) for item in drilldown.json]
        self.assertEqual(contexts[0], contexts[1])
        self.assertEqual(contexts[0]["platform"], "Instagram")

    def test_fourth_eligible_context_has_labeled_drilldown_and_can_be_decided(self) -> None:
        base = list(csv.DictReader(io.StringIO(valid_upload().decode())))
        rows = [
            {
                **row,
                "id": f"{category}-{row['id']}",
                "content_id": f"{category}-{row['content_id']}",
                "content_category": category,
            }
            for category in ("one", "two", "three", "four")
            for row in base
        ]
        app = self.app()
        app.file_uploader[0].set_value(("four-contexts.csv", csv_bytes(rows), "text/csv")).run()

        self.assertFalse(app.exception)
        self.assertEqual(len(app.session_state["active_result"]["recommendations"]), 3)
        self.assertEqual(len(app.session_state["active_result"]["all_recommendations"]), 4)
        additional = app.selectbox(key="additional_recommendation")
        self.assertEqual(additional.label, "Ação adicional para detalhar")
        self.assertEqual(len(additional.options), 1)
        self.assertTrue(any(item.label == "Outras ações elegíveis (1)" for item in app.expander))
        decision = app.selectbox(key="decision_recommendation")
        self.assertEqual(len(decision.options), 4)
        fourth = app.session_state["active_result"]["all_recommendations"][3]
        decision.set_value(fourth).run()
        app.button(key="save_decision").click().run()
        self.assertTrue(any("Decisão registrada" in item.value for item in app.success))
        self.assertEqual(self.stored()[0]["recommendation_key"], fourth["recommendation_key"])

    def test_session_analysis_reuse_and_strict_invalidation(self) -> None:
        tech = list(csv.DictReader(io.StringIO(valid_upload().decode())))
        beauty = [{**row, "id": f"beauty-{row['id']}", "content_id": f"beauty-{row['content_id']}",
                   "content_category": "beauty"} for row in tech]
        raw = csv_bytes(tech + beauty)
        with (
            patch("analysis.load_csv", wraps=load_csv) as validate,
            patch("analysis.analyze", wraps=analyze) as engine,
            patch("storage.record_import", wraps=record_import) as provenance,
            patch("streamlit.download_button", wraps=st.download_button) as download,
        ):
            app = self.app()
            app.file_uploader[0].set_value(("mixed.csv", raw, "text/csv")).run()
            self.assertEqual((validate.call_count, provenance.call_count, engine.call_count), (1, 1, 2))
            head_answers = app.session_state["head_answers"]
            self.assertEqual(len(head_answers), 4)
            self.assertIn("Quatro respostas obrigatórias do challenge", [item.value for item in app.subheader])
            rendered = "\n".join(item.value for item in app.markdown)
            self.assertTrue(all(item["verdict"] in rendered for item in head_answers))

            second = app.session_state["active_result"]["all_recommendations"][1]
            app.selectbox(key="decision_recommendation").set_value(second).run()
            app.button(key="save_decision").click().run()
            self.assertEqual((validate.call_count, provenance.call_count, engine.call_count), (1, 1, 2))
            self.assertEqual(self.stored()[0]["recommendation_key"], second["recommendation_key"])
            payload = next(call.args[1] for call in reversed(download.call_args_list)
                           if call.args[0] == "Baixar evidências e decisões (CSV)")
            self.assertTrue(any(row["record_type"] == "decision" for row in parse_export(payload)))

            app.multiselect(key="filter_content_category").set_value(["beauty"]).run()
            self.assertEqual((validate.call_count, provenance.call_count, engine.call_count), (1, 1, 3))
            self.assertEqual(app.session_state["head_answers"], head_answers)

            app.selectbox(key="period_mode").set_value("Todo o histórico").run()
            self.assertEqual((validate.call_count, provenance.call_count, engine.call_count), (1, 1, 4))

            changed = csv_bytes([{**row, "likes": int(row["likes"]) + 1} for row in tech + beauty])
            app.file_uploader[0].set_value(("changed.csv", changed, "text/csv")).run()
            self.assertEqual((validate.call_count, provenance.call_count, engine.call_count), (2, 2, 6))
            preserved = app.session_state["active_result"]

            app.file_uploader[0].set_value(("invalid.csv", b"invalid", "text/csv")).run()
            self.assertEqual((validate.call_count, provenance.call_count, engine.call_count), (3, 2, 6))
            self.assertEqual(app.session_state["active_result"]["scope"], preserved["scope"])
            self.assertTrue(app.error)

    def test_recommendation_labels_expose_context_without_changing_identity(self) -> None:
        base = list(csv.DictReader(io.StringIO(valid_upload().decode())))
        rows = [{**row, "id": f"{category}-{row['id']}", "content_id": f"{category}-{row['content_id']}",
                 "content_category": category} for category in ("alpha", "beta", "gamma", "delta") for row in base]
        app = self.app()
        app.file_uploader[0].set_value(("contexts.csv", csv_bytes(rows), "text/csv")).run()

        options = app.selectbox(key="decision_recommendation").options
        self.assertGreaterEqual(len(options), 2)
        self.assertNotEqual(options[0], options[1])
        for expected in ("Plataforma: Instagram", "Formato: video", "Categoria:", "Faixa: 10,000–49,999"):
            self.assertTrue(all(expected in option for option in options))
        additional_options = app.selectbox(key="additional_recommendation").options
        self.assertTrue(all("Plataforma: Instagram" in option and "Categoria:" in option
                            for option in additional_options))
        captions = [item.value for item in app.caption if item.value.startswith("Contexto —")]
        self.assertGreaterEqual(len(captions), 3)
        self.assertTrue(all("Plataforma: Instagram" in caption and "Categoria:" in caption for caption in captions))

        selected = app.session_state["active_result"]["all_recommendations"][1]
        app.selectbox(key="decision_recommendation").set_value(selected).run()
        app.button(key="save_decision").click().run()
        self.assertEqual(self.stored()[0]["recommendation_key"], selected["recommendation_key"])

    def test_sponsorship_month_and_long_context_are_concise_without_identity_loss(self) -> None:
        categories = tuple("categoria-" + "X" * 3999 + suffix for suffix in "ABCD")
        rows = [
            make_post(
                id=f"{category[-1]}-{flag}-{index}",
                content_id=f"content-{category[-1]}-{flag}-{index}",
                creator_id=f"creator-{index % 5}",
                is_sponsored=str(flag).upper(),
                likes=8 if flag else 4,
                shares=0,
                comments_count=0,
                content_category=category,
            )
            for category in categories
            for flag in (False, True)
            for index in range(30)
        ]
        app = self.app()
        app.file_uploader[0].set_value(("long-context.csv", csv_bytes(rows), "text/csv")).run()

        self.assertFalse(app.exception)
        options = app.selectbox(key="decision_recommendation").options
        additional_options = app.selectbox(key="additional_recommendation").options
        captions = [item.value for item in app.caption if item.value.startswith("Contexto —")]
        self.assertEqual((len(options), len(additional_options)), (4, 1))
        self.assertEqual(len(set(options)), 4)
        labels = (*captions, *options, *additional_options)
        self.assertTrue(all("Mês: 2025\\-01" in value and "…" in value for value in captions))
        self.assertTrue(all("Mês: 2025-01" in value and "…" in value for value in (*options, *additional_options)))
        self.assertTrue(all(len(value) < 320 for value in labels))
        self.assertTrue(all(category not in value for category in categories for value in labels))

        selected = app.session_state["active_result"]["all_recommendations"][1]
        self.assertEqual(len(selected["context"]["content_category"]), 4010)
        app.selectbox(key="decision_recommendation").set_value(selected).run()
        app.button(key="save_decision").click().run()
        stored = self.stored()[0]
        self.assertEqual(stored["recommendation_key"], selected["recommendation_key"])
        self.assertEqual(stored["baseline"]["evidence_snapshot"]["context"]["content_category"],
                         selected["context"]["content_category"])

    def test_tiny_priority_components_keep_magnitude_zero_and_sign(self) -> None:
        base = list(csv.DictReader(io.StringIO(valid_upload().decode())))
        rows = [{**row, "id": f"{category}-{row['id']}", "content_id": f"{category}-{row['content_id']}",
                 "content_category": category} for category in ("one", "two", "three", "four") for row in base]
        tiny_score = 1.1444091796875e-05
        tiny_component = 1.9073486328125e-06

        def controlled_analysis(*args, **kwargs):
            result = analyze(*args, **kwargs)
            if len(result["all_recommendations"]) < 4:
                return result
            first, zero, additional = (result["all_recommendations"][index] for index in (0, 1, 3))
            first["priority"] = tiny_score
            first["priority_components"] = {"impact": 0.0, "strength": -tiny_component, "recency": tiny_component}
            zero["priority"] = 0.0
            additional["priority"] = -tiny_score
            additional["priority_components"] = {"impact": 0.0, "strength": -tiny_component, "recency": tiny_component}
            return result

        with patch("analysis.analyze", side_effect=controlled_analysis):
            app = self.app()
            app.file_uploader[0].set_value(("tiny-scores.csv", csv_bytes(rows), "text/csv")).run()

        self.assertFalse(app.exception)
        captions = [item.value for item in app.caption if "prioridade " in item.value]
        self.assertTrue(any("prioridade 1.14441e-05" in value for value in captions))
        self.assertTrue(any(value.endswith("prioridade 0") for value in captions))
        self.assertTrue(any("prioridade -1.14441e-05" in value for value in captions))
        first_id = app.session_state["active_result"]["all_recommendations"][0]["evidence_id"]
        inputs = [item for item in app.number_input if first_id in str(item.key)]
        self.assertEqual([item.value for item in inputs], [0.0, -tiny_component, tiny_component])
        self.assertEqual([item.proto.format % item.value for item in inputs],
                         ["0", "-1.90735e-06", "1.90735e-06"])
        self.assertTrue(all(item.proto.format == "%.6g" for item in app.number_input))
        self.assertEqual(app.session_state["active_result"]["all_recommendations"][0]["priority"], tiny_score)

    def test_external_context_is_literal_in_captions_and_complete_in_identity(self) -> None:
        platform = "![x](https://x.invalid/x)"
        category = "**bold** `code` [link](x)"
        content_type = "<b>tag</b> _special_!"
        rows = list(csv.DictReader(io.StringIO(valid_upload().decode())))
        for row in rows:
            row.update({"platform": platform, "content_category": category, "content_type": content_type})
        app = self.app()
        app.file_uploader[0].set_value(("literal.csv", csv_bytes(rows), "text/csv")).run()

        self.assertFalse(app.exception)
        source = next(item.value for item in app.caption if item.value.startswith("Fonte ativa"))
        context = next(item.value for item in app.caption if item.value.startswith("Contexto —"))
        escaped_image = r"\!\[x\]\(https\:\/\/x\.invalid\/x\)"
        self.assertIn(escaped_image, source)
        self.assertIn(escaped_image, context)
        for marker in (r"\*\*bold\*\*", r"\`code\`", r"\[link\]\(x\)", r"\<b\>tag\<\/b\>", r"\_special\_\!"):
            self.assertIn(marker, context)
        self.assertEqual(len(app.image), 0)

        selected = app.session_state["active_result"]["all_recommendations"][0]
        self.assertEqual(selected["context"]["platform"], platform)
        self.assertEqual(selected["context"]["content_category"], category)
        option = app.selectbox(key="decision_recommendation").options[0]
        self.assertIn(platform, option)
        self.assertIn(category, option)
        self.assertNotIn(escaped_image, option)
        app.button(key="save_decision").click().run()
        snapshot = self.stored()[0]["baseline"]["evidence_snapshot"]["context"]
        self.assertEqual((snapshot["platform"], snapshot["content_category"]), (platform, category))

    def test_week_and_month_clip_before_timestamp_at_upper_date_boundary(self) -> None:
        rows = [
            make_post(
                id=f"{sponsored}-{index}",
                content_id=f"{sponsored}-{index}",
                creator_id=f"creator-{index % 5}",
                is_sponsored=sponsored,
                post_date="2262-04-09T12:00:00",
            )
            for sponsored in ("TRUE", "FALSE")
            for index in range(30)
        ]
        app = self.app()
        app.file_uploader[0].set_value(("upper-date.csv", csv_bytes(rows), "text/csv")).run()
        for mode, requested_end in (
            ("Semana ISO", "2262-04-13T00:00:00"),
            ("Mês calendário", "2262-04-30T00:00:00"),
        ):
            with self.subTest(mode=mode):
                app.selectbox(key="period_mode").set_value(mode).run()
                self.assertFalse(app.exception)
                scope = app.session_state["active_result"]["scope"]
                self.assertEqual(scope["requested_end"], requested_end)
                self.assertEqual(scope["target_end"], "2262-04-09T00:00:00")
                self.assertTrue(scope["partial_period"])

    def test_post_priority_discloses_fallback_and_benchmark_references(self) -> None:
        rows = [make_post(id=f"before-{i}", content_id=f"before-{i}", creator_id=f"creator-{i % 5}", post_date="2024-11-01T12:00:00", audience_location="US", likes=[2, 4, 6, 8, 10, 12][i % 6], shares=0, comments_count=0) for i in range(30)]
        rows.append(make_post(id="target", content_id="target", creator_id="new-creator", likes=30, shares=0, comments_count=0))
        app = self.app()
        app.file_uploader[0].set_value(("post.csv", csv_bytes(rows), "text/csv")).run()
        self.assertFalse(app.exception)
        text = "\n".join(item.value for item in app.markdown)
        for expected in ("Taxa-alvo ERv (%): `30.0`", "Benchmark — mediana ERv (%): `7.0`", "Benchmark — quartis Q1 / Q3 ERv (%): `4.0` / `10.0`", "Delta ERv (p.p.): `23.0`", "Amostra do benchmark — posts elegíveis / creators: 30 / 5", "core+age+gender/365d"):
            self.assertIn(expected, text)
        drilldown = next(item for item in app.expander if item.label == "Registros de origem e contexto")
        contexts = [json.loads(item.value) for item in drilldown.json]
        self.assertEqual(contexts[0]["audience_location"], "BR")
        self.assertNotIn("audience_location", contexts[1])
        self.assertIn("audience_location", contexts[2])
        self.assertEqual(len(drilldown.dataframe[0].value), 31)

    def test_sponsorship_priority_labels_creator_medians_and_post_quartiles(self) -> None:
        rows = [make_post(id=f"{sponsored}-{i}", content_id=f"{sponsored}-{i}", creator_id=f"creator-{i % 5}", is_sponsored=sponsored, likes=8 if sponsored == "TRUE" else 4, shares=0, comments_count=0) for sponsored in ("TRUE", "FALSE") for i in range(30)]
        app = self.app()
        app.file_uploader[0].set_value(("sponsorship.csv", csv_bytes(rows), "text/csv")).run()
        self.assertFalse(app.exception)
        text = "\n".join(item.value for item in (*app.markdown, *app.caption))
        for expected in ("Taxa-alvo ERv (%): `8.0`", "Benchmark — mediana ERv (%): `4.0`", "Delta ERv (p.p.): `4.0`", "medianas das medianas por creator", "quartis descritivos dos posts orgânicos", "núcleo de patrocínio; audiência apenas nos filtros"):
            self.assertIn(expected, text)

    def test_revision_and_original_survive_new_session_without_csv(self) -> None:
        app = self.app()
        app.file_uploader[0].set_value(("social.csv", valid_upload(), "text/csv")).run()
        app.button(key="save_decision").click().run()
        reopened = self.app()
        reopened.selectbox(key="revision_status").set_value("edited")
        reopened.text_area(key="revision_text").set_value("Testar somente um vídeo.")
        reopened.button(key="save_revision").click().run()
        self.assertTrue(any("Revisão registrada" in item.value for item in reopened.success))
        final = self.app()
        self.assertFalse(final.exception)
        with closing(sqlite3.connect(Path(self.directory.name) / "cockpit.sqlite3")) as connection:
            rows = connection.execute("SELECT decision_id, revision_of, status, baseline_json FROM decisions ORDER BY decided_at").fetchall()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1][1], rows[0][0])
        self.assertEqual([row[2] for row in rows], ["accepted", "edited"])
        self.assertEqual(rows[0][3], rows[1][3])
        self.assertTrue(any(rows[0][0] in item.value and "Revisão da decisão" in item.value for item in final.caption))
        self.assertTrue(any("Testar somente um vídeo." in item.value for item in final.markdown))

    def test_empty_filter_has_explicit_state(self) -> None:
        app = self.app()
        app.file_uploader[0].set_value(("social.csv", valid_upload(), "text/csv")).run()
        app.multiselect(key="platform_filter").set_value([]).run()
        self.assertFalse(app.exception)
        self.assertTrue(any("Filtro vazio" in item.value for item in app.warning))

    def test_incompatible_filter_intersection_hides_performance_and_recovers(self) -> None:
        instagram_tech = list(csv.DictReader(io.StringIO(valid_upload().decode())))
        tiktok_beauty = [
            {
                **row,
                "id": f"beauty-{row['id']}",
                "content_id": f"beauty-{row['content_id']}",
                "platform": "TikTok",
                "content_category": "beauty",
            }
            for row in instagram_tech
        ]
        app = self.app()
        app.file_uploader[0].set_value(("mixed.csv", csv_bytes(instagram_tech + tiktok_beauty), "text/csv")).run()
        app.button(key="save_decision").click().run()

        app.multiselect(key="platform_filter").set_value(["Instagram"]).run()
        app.multiselect(key="filter_content_category").set_value(["beauty"]).run()

        self.assertFalse(app.exception)
        self.assertTrue(any(
            "Nenhum registro corresponde aos filtros/período selecionados" in item.value
            for item in app.warning
        ))
        self.assertEqual(len(app.metric), 0)
        self.assertEqual(len(app.download_button), 0)
        self.assertEqual(app.multiselect(key="platform_filter").value, ["Instagram"])
        self.assertEqual(app.multiselect(key="filter_content_category").value, ["beauty"])
        self.assertTrue(any("120 linhas" in item.value for item in app.caption))
        self.assertEqual(len(self.stored()), 1)
        self.assertTrue(any("accepted" in item.value for item in app.markdown))

        app.multiselect(key="filter_content_category").set_value(["tech"]).run()

        self.assertFalse(app.exception)
        self.assertEqual({item.label: item.value for item in app.metric}["Posts"], "30")
        self.assertEqual(len(app.download_button), 2)
        self.assertEqual(len(self.stored()), 1)

    def test_accepted_and_rejected_ignore_stray_text_in_decisions_and_revisions(self) -> None:
        app = self.app()
        app.file_uploader[0].set_value(("social.csv", valid_upload(), "text/csv")).run()
        for status in ("accepted", "rejected"):
            with self.subTest(status=status):
                app.selectbox(key="decision_status").set_value(status)
                app.text_area(key="decision_text").set_value("Texto indevido da decisão.")
                app.button(key="save_decision").click().run()
                self.assertFalse(app.exception)
                app.selectbox(key="revision_status").set_value(status)
                app.text_area(key="revision_text").set_value("Texto indevido da revisão.")
                app.button(key="save_revision").click().run()
                self.assertFalse(app.exception)
        with closing(sqlite3.connect(Path(self.directory.name) / "cockpit.sqlite3")) as connection:
            rows = connection.execute("SELECT status, original_text, edited_text, revision_of FROM decisions ORDER BY decided_at").fetchall()
        self.assertEqual([row[0] for row in rows], ["accepted", "accepted", "rejected", "rejected"])
        self.assertTrue(all(row[1] == rows[0][1] and row[2] == "" for row in rows))
        self.assertEqual([row[3] is not None for row in rows], [False, True, False, True])
        reopened = self.app()
        text = "\n".join(item.value for item in reopened.markdown)
        self.assertNotIn("Texto indevido", text)
        self.assertEqual(text.count(rows[0][1]), 4)

    def test_edited_decision_and_revision_require_nonempty_text(self) -> None:
        app = self.app()
        app.file_uploader[0].set_value(("social.csv", valid_upload(), "text/csv")).run()
        app.selectbox(key="decision_status").set_value("edited")
        app.text_area(key="decision_text").set_value("   ")
        app.button(key="save_decision").click().run()
        self.assertTrue(any("Informe o texto editado" in item.value for item in app.error))
        app.text_area(key="decision_text").set_value("Ação editada inicial.")
        app.button(key="save_decision").click().run()
        app.selectbox(key="revision_status").set_value("edited")
        app.text_area(key="revision_text").set_value("   ")
        app.button(key="save_revision").click().run()
        self.assertTrue(any("Informe o texto da revisão" in item.value for item in app.error))
        app.text_area(key="revision_text").set_value("Ação revisada depois.")
        app.button(key="save_revision").click().run()
        with closing(sqlite3.connect(Path(self.directory.name) / "cockpit.sqlite3")) as connection:
            rows = connection.execute("SELECT status, edited_text FROM decisions ORDER BY decided_at").fetchall()
        self.assertEqual(rows, [("edited", "Ação editada inicial."), ("edited", "Ação revisada depois.")])

    @patch("storage.utc_now")
    def test_no_and_unknown_execution_remain_distinct_after_reopen(self, clock) -> None:
        clock.return_value = datetime(2025, 1, 14, 18, tzinfo=timezone.utc)
        app = self.app()
        app.file_uploader[0].set_value(("social.csv", valid_upload(), "text/csv")).run()
        app.button(key="save_decision").click().run()
        clock.return_value = datetime(2025, 1, 22, 18, tzinfo=timezone.utc)
        app.file_uploader[0].set_value(("synthetic-retrospective.csv", later_upload(), "text/csv")).run()
        for status, reason in (("no", "comparable_action_not_executed"), ("unknown", "comparable_execution_unknown")):
            app.selectbox(key="execution_status").set_value(status)
            app.button(key="save_outcome").click().run()
            self.assertTrue(any(f"Observação registrada: observed — {reason}" in item.value for item in app.success))
        reopened = self.app()
        self.assertFalse(reopened.exception)
        text = "\n".join(item.value for item in (*reopened.markdown, *reopened.caption))
        for expected in ("comparable_action_not_executed", "comparable_execution_unknown", "Execução declarada: no", "Execução declarada: unknown"):
            self.assertIn(expected, text)
        self.assertEqual(text.count("Observação não causal"), 2)

    def test_partial_period_label_and_posterior_observation(self) -> None:
        app = self.app()
        app.file_uploader[0].set_value(("social.csv", valid_upload(), "text/csv")).run()
        app.selectbox(key="period_mode").set_value("Semana ISO").run()
        self.assertTrue(any("cobertura parcial" in item.value for item in app.caption))
        app.selectbox(key="period_mode").set_value("Últimos 7 dias").run()
        app.button(key="save_decision").click().run()
        self.assertTrue(any("Decisão registrada" in item.value for item in app.success))

        app.file_uploader[0].set_value(("later.csv", later_upload(), "text/csv")).run()
        self.assertTrue(any(item.value == "Observação posterior" for item in app.subheader))
        self.assertEqual([item.value for item in app.number_input], [0.0, 0.0, 0.0])
        app.selectbox(key="execution_status").set_value("yes")
        app.date_input(key="execution_date").set_value(date(2025, 1, 14))
        app.button(key="save_outcome").click().run()
        self.assertTrue(
            any("Observação registrada: pending — execution_before_decision" in item.value for item in app.success)
        )
        reopened = self.app()
        self.assertFalse(reopened.exception)
        text = "\n".join(item.value for item in (*reopened.markdown, *reopened.caption))
        for expected in ("Observação pending", "execution_before_decision", "Execução declarada: yes", "2025-01-14", "Janela observada: 2025-01-15 a 2025-01-21", "mediana baseline / observada / delta (p.p.): `8.0` / `9.0` / `1.0`", "Visualizações por dia — baseline / observada:", "Observação não causal"):
            self.assertIn(expected, text)
        self.assertIn("428.57142857142856", text)

    @patch("storage.utc_now")
    def test_valid_observation_survives_reopen(self, clock) -> None:
        clock.return_value = datetime(2025, 1, 14, 18, tzinfo=timezone.utc)
        app = self.app()
        app.file_uploader[0].set_value(("social.csv", valid_upload(), "text/csv")).run()
        app.button(key="save_decision").click().run()
        now = clock.return_value
        synthetic_start = datetime(2025, 1, 15, 12)
        clock.return_value = datetime(2025, 1, 22, 18, tzinfo=timezone.utc)
        app.file_uploader[0].set_value(("synthetic-retrospective.csv", later_upload(synthetic_start), "text/csv")).run()
        app.selectbox(key="execution_status").set_value("yes")
        app.date_input(key="execution_date").set_value(now.date())
        app.button(key="save_outcome").click().run()
        self.assertTrue(any("Observação registrada: observed — comparable_after_declared_execution" in item.value for item in app.success))
        reopened = self.app()
        self.assertFalse(reopened.exception)
        text = "\n".join(item.value for item in (*reopened.markdown, *reopened.caption))
        for expected in ("Observação observed", "comparable_after_declared_execution", synthetic_start.date().isoformat(), "mediana baseline / observada / delta", "Visualizações por dia", "Observação não causal"):
            self.assertIn(expected, text)


if __name__ == "__main__":
    unittest.main()
