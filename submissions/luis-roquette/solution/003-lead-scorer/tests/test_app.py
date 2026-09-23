"""Fixture-first tests for the Streamlit portfolio and session contract."""
import argparse
import contextlib
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import http.server
import ipaddress
import json
import math
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import tempfile
import threading
import time
from types import MappingProxyType
import unittest
from urllib.parse import urlparse
from urllib.request import urlopen
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
RENDER_TIMEOUT_MS = 120_000
sys.path.insert(0, str(ROOT))

import scoring as s


def _free_port():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _wait_for_streamlit(process, port, timeout=120):
    deadline = time.monotonic() + timeout
    while process.poll() is None:
        try:
            with urlopen(f"http://127.0.0.1:{port}/_stcore/health", timeout=1) as response:
                if response.status == 200:
                    return
        except OSError:
            pass
        if time.monotonic() >= deadline:
            break
        time.sleep(.1)
    raise RuntimeError(f"Streamlit não iniciou; status={process.poll()}")


@contextlib.contextmanager
def managed_streamlit_server(app_path, python=sys.executable, timeout=120):
    """Own exactly one child and tear down only that process."""
    port = _free_port()
    process = subprocess.Popen((python, "-m", "streamlit", "run", str(app_path),
        "--server.headless=true", "--server.address=127.0.0.1", f"--server.port={port}",
        "--browser.gatherUsageStats=false"),
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        env={**os.environ, "STREAMLIT_BROWSER_GATHER_USAGE_STATS": "false"})
    try:
        _wait_for_streamlit(process, port, timeout)
        yield process, f"http://127.0.0.1:{port}"
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def verify_live_revision(url, expected_revision, expected_source_digest, expected_fingerprint):
    """Verify rendered identity and active-stage UI; TC-47 calls this after deploy."""
    expected = {
        "url": url,
        "revision": expected_revision,
        "source_digest": expected_source_digest,
        "fingerprint": expected_fingerprint,
    }
    if any(not isinstance(value, str) or not value.strip() for value in expected.values()):
        raise ValueError("url, expected_revision, expected_source_digest e expected_fingerprint são obrigatórios")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("URL de verificação deve ser HTTP(S) absoluta")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=120_000)
            page.get_by_role("heading", name="Prioridades comerciais explicáveis").wait_for(
                timeout=RENDER_TIMEOUT_MS)
            page.get_by_text(re.compile(r"revisão .+fingerprint .+fonte .+"),
                             exact=False).wait_for(timeout=RENDER_TIMEOUT_MS)
            body = page.locator("body").inner_text()
            required = (f"revisão {expected_revision}", f"fingerprint {expected_fingerprint}",
                        f"fonte {expected_source_digest}")
            missing = [token for token in required if token not in body]
            if missing:
                raise AssertionError(f"Identidade renderizada divergente: {missing}")
            for stage in ("Engaging", "Prospecting"):
                if page.get_by_role("tab", name=stage, exact=True).count() != 1:
                    raise AssertionError(f"Visão de estágio ausente: {stage}")
            if not any(label in body for label in ("Probabilidade validada", "Prioridade relativa",
                    "Dados insuficientes", "Nenhuma oportunidade neste filtro")):
                raise AssertionError("Visão ativa de oportunidades ausente")
        finally:
            browser.close()
    return True


@contextlib.contextmanager
def _html_server(html):
    payload = html.encode()
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *_):
            pass
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def _periods():
    return tuple(s.PeriodEvidence(name, tuple(f"{name}-{i}" for i in range(n)), n // 2,
        n - n // 2, n, ()) for name, n in (("train", 200), ("calibration", 100), ("test", 100)))


def _evaluation(candidate, route):
    periods = _periods()
    return s.CandidateEvaluation(f"fixture-{candidate}-{route}", candidate, route, "passed",
        s.DEFAULT_CONFIG.fingerprint, "split", "features", ("product",), periods,
        "2020-01-01", "2020-02-01", .5, .15, .4, .25, .69,
        (s.BandEvidence("baixa", 50, .2, .2, True, ()),
         s.BandEvidence("media", 0, None, None, False, ("empty_band",)),
         s.BandEvidence("alta", 50, .8, .8, True, ())),
        (s.TopKMetric(.1, 10, .5, .3, None), s.TopKMetric(.2, 20, .5, .5, None)),
        (), (), (), 0, 100)


def _score(oid, stage, seller="Ana", manager="Mara", region="Sul", state="calibrated", **changes):
    base = dict(opportunity_id=oid, stage=stage, sales_agent=seller, manager=manager,
        regional_office=region, product=f"Produto {oid}", account="Conta", state=state,
        potential_revenue=100., fingerprint="fixture", diagnostics=(),
        next_action="Validar a necessidade antes do próximo passo")
    if state == "calibrated":
        base.update(route="full", origin="logistic", band="alta", band_kind="probability",
            probability=.8, expected_revenue=80., evaluation_id="fixture-logistic-full",
            observed_n=50, effective_support=50., evidence_strength="moderada",
            explanation_scale="calibrated_log_odds", base_value=0., factors=(
                s.Factor("product", base["product"], math.log(4), "favoravel", "Referência", True),
                s.Factor("series", "S1", -.2, "desfavoravel", "Referência", True)))
    elif state == "relative":
        base.update(route="prospecting" if stage == "Prospecting" else "fallback",
            origin="historical_evidence", band="media", band_kind="relative", relative_index=.52,
            observed_n=25, prior_strength=20., effective_support=45., evidence_strength="fraca",
            explanation_scale="relative_index", base_value=.5)
    else:
        base.update(diagnostics=(s.diagnostic("unknown_product", "Produto não encontrado",
            "Corrija product no cadastro", field="product", opportunity_id=oid, scope="row"),))
    base.update(changes)
    return s.ScoreResult(**base)


def bundle_fixture(fingerprint="fixture"):
    evaluations = tuple(_evaluation(candidate, route) for candidate in ("logistic", "boosting")
                        for route in ("full", "fallback"))
    scores = (
        _score("E-A", "Engaging"),
        _score("E-A2", "Engaging", state="relative"),
        _score("P-A", "Prospecting", state="relative"),
        _score("P-BAD", "Prospecting", state="insufficient_data"),
        _score("E-B", "Engaging", seller="Beto", region="Norte", probability=.7, expected_revenue=70.),
        _score("E-C", "Engaging", seller="Caio", manager="Nina", region="Leste"),
        _score("UNASSIGNED", "Engaging", seller=None, manager=None, region=None,
               state="insufficient_data"),
    )
    return s.ScoringBundle(fingerprint, s.DEFAULT_CONFIG.version, evaluations,
        tuple(s.select_route(evaluations, route) for route in ("full", "fallback")), scores, (),
        {"revision": "fixture-revision", "source_digest": "fixture-source"})


def rejected_bundle_fixture():
    evaluations = tuple(replace(_evaluation(candidate, route), status="rejected",
        reasons=("fewer_than_two_supported_bands",))
        for candidate in ("logistic", "boosting") for route in ("full", "fallback"))
    scores = (
        _score("E-R", "Engaging", state="relative", route="fallback",
               origin="historical_evidence"),
        _score("P-R", "Prospecting", state="relative"),
        _score("P-BAD", "Prospecting", state="insufficient_data"),
    )
    return s.ScoringBundle("fixture-rejected", s.DEFAULT_CONFIG.version, evaluations,
        tuple(s.select_route(evaluations, route) for route in ("full", "fallback")), scores, (),
        {"revision": "fixture-rejected", "source_digest": "fixture-source"})


def empty_stage_bundle_fixture():
    evaluations = tuple(_evaluation(candidate, route) for candidate in ("logistic", "boosting")
                        for route in ("full", "fallback"))
    return s.ScoringBundle("fixture-empty", s.DEFAULT_CONFIG.version, evaluations,
        tuple(s.select_route(evaluations, route) for route in ("full", "fallback")), (), (),
        {"revision": "fixture-empty", "source_digest": "fixture-source"})


class PortfolioContractTests(unittest.TestCase):
    def setUp(self):
        import app
        self.app = app
        self.bundle = bundle_fixture()

    def test_TC33_TC34_seller_stage_sections_and_unsupported_visibility(self):
        rows = self.app.portfolio_rows(self.bundle, "Vendedor", "Ana")
        self.assertEqual({row.opportunity_id for row in rows}, {"E-A", "E-A2", "P-A", "P-BAD"})
        sections = self.app.stage_sections(rows, "Prospecting", None)
        self.assertEqual([row.opportunity_id for row in sections["relative"]], ["P-A"])
        self.assertEqual([row.opportunity_id for row in sections["insufficient_data"]], ["P-BAD"])
        bad = self.app.detail_view(sections["insufficient_data"][0])
        self.assertEqual(bad["Estado"], "Dados insuficientes")
        self.assertIn("Corrija product", bad["Correção"])
        self.assertNotIn("Probabilidade", bad)
        self.assertNotIn("Receita esperada", bad)

    def test_focus_queue_gives_an_ordered_action_plan_per_independent_stage(self):
        rows = self.app.portfolio_rows(self.bundle, "Vendedor", "Ana")
        self.assertEqual([row.opportunity_id for row in self.app.focus_queue(rows, "Engaging")],
                         ["E-A", "E-A2"])
        self.assertEqual([row.opportunity_id for row in self.app.focus_queue(rows, "Prospecting")],
                         ["P-A"])
        with self.assertRaisesRegex(ValueError, "limite"):
            self.app.focus_queue(rows, "Engaging", 0)
        self.assertEqual(self.app.focus_queue([], "Engaging"), [])
        leader = self.app.focus_queue(rows, "Engaging")[0]
        self.assertEqual(self.app.focus_reason(leader),
                         "probabilidade validada; faixa alta; evidência moderada")
        self.assertIn("produto Produto E-A: associação favorável",
                      self.app.focus_signals(leader))
        self.assertIn("série S1: associação desfavorável", self.app.focus_signals(leader))

    def test_C4_sections_delegate_all_ordering_to_canonical_rank_stage(self):
        rows = self.app.portfolio_rows(self.bundle, "Gestor", "Mara")
        with patch.object(self.app, "rank_stage", wraps=s.rank_stage) as canonical:
            sections = self.app.stage_sections(rows, "Engaging", None)
        canonical.assert_called_once_with(rows, "Engaging")
        self.assertEqual([row.opportunity_id for row in sections["calibrated"]], ["E-A", "E-B"])

    def test_C4_native_table_selection_maps_the_displayed_section_positions(self):
        rows = [next(row for row in self.bundle.scores if row.opportunity_id == item)
                for item in ("E-A", "E-B")]
        event = {"selection": {"rows": [1]}}
        with patch.object(self.app.st, "dataframe", return_value=event) as dataframe:
            positions = self.app.render_selectable_table(rows, "calibrated", None, "fixture-grid")
        self.assertEqual(positions, [1])
        self.assertEqual(dataframe.call_args.kwargs["on_select"], "rerun")
        self.assertEqual(dataframe.call_args.kwargs["selection_mode"], "single-row")
        state = {}
        self.app.ensure_session(state, "fixture")
        self.assertEqual(self.app.resolve_selection(state, "Engaging", "page-1",
            [row.opportunity_id for row in rows], positions), "E-B")

    def test_C4_native_selection_keeps_one_active_section_per_stage_page(self):
        state = {}
        self.app.ensure_session(state, "fixture")
        tables = ("engaging-calibrated", "engaging-relative")
        state["calibrated-widget"] = {"selection": {"rows": [0]}}
        self.app.activate_native_selection(state, "Engaging", "page-1",
            "calibrated-widget", tables[0], ("E-A",), tables)
        self.assertEqual(state["selection_by_stage"]["Engaging"]["id"], "E-A")

        state["relative-widget"] = {"selection": {"rows": [0]}}
        self.app.activate_native_selection(state, "Engaging", "page-1",
            "relative-widget", tables[1], ("E-A2",), tables)
        self.assertEqual(state["selection_by_stage"]["Engaging"], {
            "context": "page-1", "id": "E-A2", "source_table": tables[1]})
        self.assertEqual(state["table_reset_by_key"][tables[0]], 1)
        self.assertEqual(state["active_table_by_stage"]["Engaging"], {
            "context": "page-1", "table": tables[1]})

    def test_TC33_unassigned_rows_stay_in_quality_view_without_a_portfolio_owner(self):
        unassigned = next(row for row in self.bundle.scores if row.opportunity_id == "UNASSIGNED")
        for role, identity in (("Vendedor", "Ana"), ("Gestor", "Mara")):
            self.assertNotIn(unassigned, self.app.portfolio_rows(self.bundle, role, identity))
        self.assertEqual(self.app.detail_view(unassigned)["Estado"], "Dados insuficientes")

    def test_TC35_manager_filters_exact_membership_and_score_invariance(self):
        team = self.app.portfolio_rows(self.bundle, "Gestor", "Mara")
        south = self.app.portfolio_rows(self.bundle, "Gestor", "Mara", "Sul", "Todos da equipe")
        beto = self.app.portfolio_rows(self.bundle, "Gestor", "Mara", "Todas as regiões", "Beto")
        self.assertEqual({r.opportunity_id for r in team}, {"E-A", "E-A2", "P-A", "P-BAD", "E-B"})
        self.assertEqual({r.opportunity_id for r in south}, {"E-A", "E-A2", "P-A", "P-BAD"})
        self.assertEqual([r.opportunity_id for r in beto], ["E-B"])
        original = {r.opportunity_id: r.to_dict() for r in self.bundle.scores}
        self.assertEqual(original, {r.opportunity_id: r.to_dict() for r in self.bundle.scores})

    def test_TC36_details_factors_origin_support_action_and_no_stale_selection(self):
        detail = self.app.detail_view(next(r for r in self.bundle.scores if r.opportunity_id == "E-A"))
        self.assertEqual(detail["Origem"], "logistic")
        self.assertEqual(detail["Evidência"], "moderada")
        self.assertEqual(len(detail["Fatores favoráveis"]), 1)
        self.assertEqual(len(detail["Fatores desfavoráveis"]), 1)
        self.assertIn("Validar", detail["Próxima ação"])
        state = {}
        self.app.ensure_session(state, "fixture")
        state["selection_by_stage"]["Engaging"] = {"context": "old", "id": "E-A"}
        self.assertIsNone(self.app.resolve_selection(state, "Engaging", "new", ["E-B"], []))
        self.assertNotIn("Engaging", state["selection_by_stage"])

    def test_TC36_compact_pagination_is_bounded_and_clamps_pages(self):
        rows = list(range(61))
        page, count, visible = self.app.paginate_rows(rows, 1)
        self.assertEqual((page, count, visible), (1, 3, list(range(25, 50))))
        page, count, visible = self.app.paginate_rows(rows, 99)
        self.assertEqual((page, count, visible), (2, 3, list(range(50, 61))))
        self.assertLessEqual(len(visible), 25)

    def test_TC37_TC38_manager_only_pin_preserves_score_and_attribution(self):
        state = {}
        self.app.ensure_session(state, "fixture")
        before = next(r for r in self.bundle.scores if r.opportunity_id == "E-B").to_dict()
        now = datetime(2026, 9, 22, 15, 30, tzinfo=timezone.utc)
        with self.assertRaises(PermissionError):
            self.app.set_temporary_priority(state, "Vendedor", "Engaging", "E-B", "Mara", {"E-B"}, "fixture", now)
        pin = self.app.set_temporary_priority(state, "Gestor", "Engaging", "E-B", "Mara", {"E-B"}, "fixture", now)
        sections = self.app.stage_sections(self.app.portfolio_rows(self.bundle, "Gestor", "Mara"), "Engaging", pin)
        self.assertEqual([r.opportunity_id for r in sections["pinned"]], ["E-B"])
        self.assertEqual(pin.manager, "Mara")
        self.assertEqual(pin.created_at_utc, now)
        self.assertEqual(self.app.format_pin_timestamp(pin),
                         "22/09/2026 12:30:00 (America/Sao_Paulo)")
        self.assertEqual(before, next(r for r in self.bundle.scores if r.opportunity_id == "E-B").to_dict())

    def test_security_priority_audit_is_durable_chained_and_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "audit" / "manager-priorities.jsonl"
            state = {}
            self.app.ensure_session(state, "fixture")
            first = datetime(2026, 9, 22, 15, 30, tzinfo=timezone.utc)
            self.app.set_temporary_priority(state, "Gestor", "Engaging", "E-B", "Mara",
                {"E-B"}, "fixture", first, path)
            self.app.set_temporary_priority(state, "Gestor", "Prospecting", "P-A", "Mara",
                {"P-A"}, "fixture", first, path)
            events = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual([event["event"] for event in events],
                             ["temporary_priority_set", "temporary_priority_set"])
            self.assertFalse(events[0]["actor_verified"])
            self.assertEqual(events[1]["previous_hash"], events[0]["event_hash"])
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

            path.write_text(path.read_text().replace('"stage":"Engaging"',
                                                      '"stage":"Prospecting"', 1))
            state["pins_by_stage"].pop("Engaging", None)
            with self.assertRaisesRegex(self.app.AuditLogError, "adulterada"):
                self.app.set_temporary_priority(state, "Gestor", "Engaging", "E-B", "Mara",
                    {"E-B"}, "fixture", first, path)
            self.assertNotIn("Engaging", state["pins_by_stage"])

    def test_TC39_pin_lifetime_filter_retention_and_resets(self):
        state = {}
        self.app.ensure_session(state, "fixture")
        self.app.set_temporary_priority(state, "Gestor", "Engaging", "E-B", "Mara", {"E-B"}, "fixture")
        self.assertIn("Engaging", state["pins_by_stage"])
        self.assertEqual(self.app.visible_pin(state, "Engaging", {"E-A"}), None)
        self.assertIn("Engaging", state["pins_by_stage"])
        self.app.recalculate(state)
        self.assertEqual(state["pins_by_stage"], {})
        self.assertEqual(state["calculation_generation"], 1)
        self.app.ensure_session(state, "changed")
        self.assertEqual(state["pins_by_stage"], {})
        self.assertEqual(state["calculation_generation"], 0)

    def test_CK19_prospecting_details_and_pin_preserve_support_and_potential_value(self):
        row = next(item for item in self.bundle.scores if item.opportunity_id == "P-A")
        detail = self.app.detail_view(row)
        self.assertEqual(detail["Observações históricas (n)"], 25)
        self.assertEqual(detail["Suporte efetivo (n + prior)"], 45.)
        self.assertEqual(detail["Peso do prior"], 20.)

        state = {}
        self.app.ensure_session(state, "fixture")
        before = row.to_dict()
        pin = self.app.set_temporary_priority(state, "Gestor", "Prospecting", "P-A",
            "Mara", {"P-A"}, "fixture")
        pinned = self.app.stage_sections(self.app.portfolio_rows(
            self.bundle, "Gestor", "Mara"), "Prospecting", pin)["pinned"]
        table = self.app._table(pinned, "pinned", pin)
        self.assertEqual(table.loc[0, "Valor potencial do catálogo"], 100.)
        self.assertEqual(before, row.to_dict())

    def test_TC40_cache_identity_changes_for_data_config_and_source(self):
        from data import Snapshot
        one = Snapshot((("x.csv", b"one"),), "{}", "deps")
        two = Snapshot((("x.csv", b"two"),), "{}", "deps")
        identity = MappingProxyType({"revision": None, "source_digest": "source-a"})
        self.assertNotEqual(self.app.bundle_cache_key(one, s.DEFAULT_CONFIG, identity),
                            self.app.bundle_cache_key(two, s.DEFAULT_CONFIG, identity))
        self.assertNotEqual(self.app.bundle_cache_key(one, s.DEFAULT_CONFIG, identity),
                            self.app.bundle_cache_key(one, replace(s.DEFAULT_CONFIG, seed=43), identity))
        self.assertNotEqual(self.app.bundle_cache_key(one, s.DEFAULT_CONFIG, identity),
                            self.app.bundle_cache_key(one, s.DEFAULT_CONFIG,
                                                      {"revision": None, "source_digest": "source-b"}))

    def test_TC40_app_and_bundle_reuse_one_canonical_source_identity(self):
        from data import Snapshot
        snapshot = Snapshot((("x.csv", b"one"),), "{}", "deps")
        identity = dict(s.source_identity(ROOT))
        expected_hashes = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                           for name in ("app.py", "data.py", "scoring.py", "requirements.txt")}
        self.assertEqual(identity["source_digest"], s.digest(expected_hashes))
        self.assertEqual(dict(self.app.source_identity(ROOT)), identity)
        self.app._cached_bundle.clear()
        with patch.object(self.app, "load_dataset", return_value=object()), \
             patch.object(self.app, "source_identity", return_value=identity), \
             patch.object(self.app, "build_scoring_bundle",
                          return_value=replace(self.bundle, source_identity=identity)) as build:
            bundle = self.app.cached_bundle(snapshot, s.DEFAULT_CONFIG)
        self.assertEqual(dict(build.call_args.args[2]), identity)
        self.assertEqual(bundle.source_identity["source_digest"], identity["source_digest"])

    def test_TC41_cached_bundle_reuses_training_for_same_identity(self):
        from data import Snapshot
        snapshot = Snapshot((("x.csv", b"one"),), "{}", "deps")
        self.app._cached_bundle.clear()
        with patch.object(self.app, "load_dataset", return_value=object()), \
             patch.object(self.app, "build_scoring_bundle", return_value=self.bundle) as build, \
             patch.object(self.app, "source_identity", return_value={"revision": None, "source_digest": "source"}):
            first = self.app.cached_bundle(snapshot, s.DEFAULT_CONFIG)
            second = self.app.cached_bundle(snapshot, s.DEFAULT_CONFIG)
        self.assertIs(first, second)
        self.assertEqual(build.call_count, 1)


class StreamlitFixtureTests(unittest.TestCase):
    def fixture_app(self, factory="bundle_fixture"):
        from streamlit.testing.v1 import AppTest
        tests = Path(__file__).parent
        return AppTest.from_string(f"""\
import sys
sys.path.insert(0, {str(tests)!r})
import streamlit as st
from app import render_portfolio
from test_app import {factory}
render_portfolio({factory}(), st.session_state)
""").run(timeout=20)

    def test_TC33_TC34_fixture_app_renders_two_tabs_and_suppresses_failed_values(self):
        at = self.fixture_app()
        self.assertFalse(at.exception)
        self.assertEqual([tab.label for tab in at.tabs], ["Engaging", "Prospecting"])
        initial = "\n".join(item.value for item in at.markdown)
        self.assertIn("Minha fila agora", initial)
        self.assertIn("Foque neste lead · Engaging", initial)
        self.assertIn("Atenção aos sinais", initial)
        self.assertIn("Por quê:", initial)
        self.assertIn("Sinais:", initial)
        self.assertIn("E-A", initial)
        self.assertIn("P-A", initial)
        labels = {button.label for button in at.button}
        self.assertIn("Abrir P-BAD", labels)
        next(button for button in at.button if button.label == "Abrir P-BAD").click().run()
        rendered = "\n".join(item.value for item in at.markdown)
        self.assertIn("Dados insuficientes", rendered)
        self.assertIn("Corrija product", rendered)

    def test_C5_rejected_routes_and_empty_portfolio_are_honest_in_apptest(self):
        rejected = self.fixture_app("rejected_bundle_fixture")
        self.assertFalse(rejected.exception)
        self.assertGreaterEqual(len(rejected.dataframe), 3)
        surfaces = "\n".join(
            [item.value for item in list(rejected.markdown) + list(rejected.caption)]
            + [frame.value.to_string() for frame in rejected.dataframe])
        self.assertNotIn("Probabilidade", surfaces)
        self.assertNotIn("Receita esperada", surfaces)
        next(button for button in rejected.button if button.label == "Abrir E-R").click().run()
        details = "\n".join(item.value for item in rejected.markdown)
        self.assertIn("Índice relativo", details)
        self.assertNotIn("Probabilidade", details)
        self.assertNotIn("Receita esperada", details)

        empty = self.fixture_app("empty_stage_bundle_fixture")
        self.assertTrue(any(item.value == "Nenhuma oportunidade neste filtro" for item in empty.info))
        self.assertFalse(any(item.value == "### Detalhes" for item in empty.markdown))
        self.assertFalse(any(button.label == "Prioridade temporária do gestor" for button in empty.button))

    def test_TC35_TC37_TC38_TC39_apptest_manager_filter_pin_and_reset(self):
        at = self.fixture_app()
        next(button for button in at.button if button.label == "Abrir E-A").click().run()
        self.assertFalse(any(button.label == "Prioridade temporária do gestor" for button in at.button))
        at.selectbox[0].set_value("Gestor").run()
        at.selectbox[2].set_value("Norte").run()
        at.selectbox[3].set_value("Beto").run()
        self.assertTrue(any(
            caption.value == "Filtros aplicados: Gestor Mara · Região Norte · Vendedor Beto"
            for caption in at.caption))
        next(button for button in at.button if button.label == "Abrir E-B").click().run()
        pin = next(button for button in at.button if button.label == "Prioridade temporária do gestor")
        pin.click().run()
        self.assertTrue(any(caption.value.startswith("Gestor Mara ·") for caption in at.caption))
        self.assertTrue(any(button.label == "Abrir E-B" for button in at.button))
        next(button for button in at.button if button.label == "Recalcular prioridades").click().run()
        self.assertFalse(any(caption.value.startswith("Gestor Mara ·") for caption in at.caption))

    def test_C4_CK19_apptest_replaces_section_selection_and_pins_prospecting(self):
        at = self.fixture_app()
        next(button for button in at.button if button.label == "Abrir E-A").click().run()
        next(button for button in at.button if button.label == "Abrir E-A2").click().run()
        selected = [item.value for item in at.markdown
                    if item.value.startswith("**Oportunidade:**")]
        self.assertEqual(selected, ["**Oportunidade:** E-A2"])

        at.selectbox[0].set_value("Gestor").run()
        next(button for button in at.button if button.label == "Abrir P-A").click().run()
        rendered = "\n".join(item.value for item in at.markdown)
        self.assertIn("**Observações históricas (n):** 25", rendered)
        self.assertIn("**Suporte efetivo (n + prior):** 45.0", rendered)
        self.assertIn("**Peso do prior:** 20.0", rendered)
        next(button for button in at.button
             if button.label == "Prioridade temporária do gestor").click().run()
        pinned = next(frame.value for frame in at.dataframe
                      if "Gestor" in frame.value.columns and "P-A" in set(frame.value["ID"]))
        self.assertEqual(pinned.loc[pinned["ID"] == "P-A",
                                   "Valor potencial do catálogo"].iloc[0], 100.)


class PlaywrightJourneyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.directory = tempfile.TemporaryDirectory()
        path = Path(cls.directory.name) / "fixture_app.py"
        path.write_text(f"""\
import sys
sys.path.insert(0, {str(Path(__file__).parent)!r})
import streamlit as st
from app import render_portfolio
from test_app import bundle_fixture, empty_stage_bundle_fixture, rejected_bundle_fixture
factories = {{"default": bundle_fixture, "empty": empty_stage_bundle_fixture,
             "rejected": rejected_bundle_fixture}}
render_portfolio(factories.get(st.query_params.get("scenario", "default"), bundle_fixture)(),
                 st.session_state)
""", encoding="utf-8")
        cls.server_context = managed_streamlit_server(path, timeout=20)
        cls.server, cls.base_url = cls.server_context.__enter__()
        cls.playwright = sync_playwright().start()
        try:
            cls.browser = cls.playwright.chromium.launch(headless=True)
        except Exception:
            cls.playwright.stop()
            cls.server_context.__exit__(None, None, None)
            cls.directory.cleanup()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server_context.__exit__(None, None, None)
        cls.directory.cleanup()

    def open_details(self, page, value):
        page.get_by_role("button", name=f"Abrir {value}", exact=True).click()

    @staticmethod
    def choose_filter(page, label, value, applied_summary):
        from playwright.sync_api import expect
        field = page.get_by_label(label, exact=True)
        expect(field).to_be_visible()
        field.click()
        field.press("Control+A")
        field.press_sequentially(value)
        field.press("Enter")
        expect(page.get_by_text(applied_summary, exact=True)).to_be_visible()

    def test_TC34_TC35_TC36_TC37_TC38_TC39_rendered_journeys(self):
        from playwright.sync_api import expect

        seller_context = self.browser.new_context()
        seller = seller_context.new_page()
        seller.goto(self.base_url)
        seller.get_by_role("heading", name="Prioridades comerciais explicáveis").wait_for()
        seller.get_by_role("tab", name="Prospecting").click()
        seller.get_by_text("Dados insuficientes", exact=True).first.wait_for()
        self.open_details(seller, "P-BAD")
        seller.get_by_text("Corrija product no cadastro", exact=False).wait_for()
        self.assertEqual(seller.get_by_role("button", name="Prioridade temporária do gestor").count(), 0)
        seller_context.close()

        manager_context = self.browser.new_context()
        manager = manager_context.new_page()
        manager.goto(self.base_url)
        manager.get_by_role("heading", name="Prioridades comerciais explicáveis").wait_for()
        self.choose_filter(manager, "Contexto demonstrado", "Gestor",
            "Filtros aplicados: Gestor Mara · Região Todas as regiões · Vendedor Todos da equipe")
        self.choose_filter(manager, "Escritório regional", "Norte",
            "Filtros aplicados: Gestor Mara · Região Norte · Vendedor Todos da equipe")
        self.choose_filter(manager, "Vendedor da equipe", "Beto",
            "Filtros aplicados: Gestor Mara · Região Norte · Vendedor Beto")
        self.open_details(manager, "E-B")
        manager.get_by_text("Origem:", exact=False).wait_for()
        manager.get_by_role("button", name="Prioridade temporária do gestor").click()
        manager.get_by_text(re.compile(r"^Gestor Mara ·")).wait_for()
        manager.get_by_role("button", name="Recalcular prioridades").click()
        expect(manager.get_by_text(re.compile(r"^Gestor Mara ·"))).to_have_count(0)
        manager_context.close()

    def test_C5_rejected_routes_and_empty_portfolio_are_honest_in_browser(self):
        from playwright.sync_api import expect

        rejected = self.browser.new_page()
        rejected.goto(f"{self.base_url}?scenario=rejected")
        rejected.get_by_role("heading", name="Prioridades comerciais explicáveis").wait_for()
        expect(rejected.locator('[data-testid="stDataFrame"]')).not_to_have_count(0)
        expect(rejected.locator("body")).not_to_contain_text("Probabilidade")
        expect(rejected.locator("body")).not_to_contain_text("Receita esperada")
        self.open_details(rejected, "E-R")
        rejected.get_by_text("Índice relativo:", exact=False).wait_for()
        expect(rejected.locator("body")).not_to_contain_text("Probabilidade")
        expect(rejected.locator("body")).not_to_contain_text("Receita esperada")
        rejected.close()

        empty = self.browser.new_page()
        empty.goto(f"{self.base_url}?scenario=empty")
        empty.get_by_role("heading", name="Prioridades comerciais explicáveis").wait_for()
        empty_messages = empty.get_by_text("Nenhuma oportunidade neste filtro", exact=True)
        expect(empty_messages).to_have_count(2)
        empty_messages.first.wait_for()
        expect(empty.get_by_role("heading", name="Detalhes", exact=True)).to_have_count(0)
        expect(empty.get_by_role("button", name="Prioridade temporária do gestor")).to_have_count(0)
        empty.close()

    def test_C4_CK19_second_section_wins_and_prospecting_support_is_rendered(self):
        from playwright.sync_api import expect

        page = self.browser.new_page()
        page.goto(self.base_url)
        page.get_by_role("heading", name="Prioridades comerciais explicáveis").wait_for()
        self.open_details(page, "E-A")
        page.get_by_text("Oportunidade: E-A", exact=True).wait_for()
        self.open_details(page, "E-A2")
        page.get_by_text("Oportunidade: E-A2", exact=True).wait_for()
        expect(page.get_by_text("Oportunidade: E-A", exact=True)).to_have_count(0)

        self.choose_filter(page, "Contexto demonstrado", "Gestor",
            "Filtros aplicados: Gestor Mara · Região Todas as regiões · Vendedor Todos da equipe")
        page.get_by_role("tab", name="Prospecting").click()
        self.open_details(page, "P-A")
        page.get_by_text("Observações históricas (n): 25", exact=True).wait_for()
        page.get_by_text("Suporte efetivo (n + prior): 45.0", exact=True).wait_for()
        page.get_by_text("Peso do prior: 20.0", exact=True).wait_for()
        page.get_by_role("button", name="Prioridade temporária do gestor").click()
        page.get_by_text(re.compile(r"^Gestor Mara ·")).wait_for()
        page.close()


class VerificationGateTests(unittest.TestCase):
    def test_TC44_offline_runtime_denies_external_and_permits_loopback(self):
        import data
        from test_data import fixture_snapshot, recovery_source
        original_connect = socket.socket.connect

        def offline_connect(sock, address):
            if not isinstance(address, tuple):
                return original_connect(sock, address)
            host = address[0]
            try:
                loopback = host == "localhost" or ipaddress.ip_address(host).is_loopback
            except ValueError:
                loopback = False
            if not loopback:
                raise RuntimeError(f"TC-44 bloqueou rede externa: {host}")
            return original_connect(sock, address)

        with patch.object(socket.socket, "connect", offline_connect):
            with recovery_source(fixture_snapshot()) as (snapshot, _):
                first = next(iter(dict(snapshot.files)))
                manifest = json.loads(snapshot.manifest_json)
                with urlopen(manifest["files"][first]["download_url"], timeout=2) as response:
                    self.assertEqual(response.status, 200)
            external = socket.socket()
            try:
                with self.assertRaisesRegex(RuntimeError, "bloqueou rede externa"):
                    external.connect(("203.0.113.1", 443))
            finally:
                external.close()
            dataset = data.load_dataset(data.read_snapshot(ROOT / "data/raw", ROOT / "data/manifest.json"))
            bundle = s.build_scoring_bundle(dataset)
        self.assertEqual(len(bundle.candidate_evaluations), 4)
        self.assertEqual(len(bundle.scores), 2089)

    def test_TC45_preflight_failure_injection_returns_nonzero(self):
        environment = {**os.environ, "LEAD_SCORER_PREFLIGHT_FAILURE_PROBE": "1",
                       "LEAD_SCORER_PREFLIGHT_FAIL_GATE": "tests"}
        result = subprocess.run(("bash", str(ROOT / "scripts/preflight.sh")), cwd=ROOT,
            env=environment, capture_output=True, text=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("falha injetada no gate tests", result.stderr)
        self.assertNotIn("PREFLIGHT OK", result.stdout)

    def test_codespaces_browser_dependencies_do_not_require_foreground_tty(self):
        script = (ROOT / "scripts/preflight.sh").read_text(encoding="utf-8")
        self.assertIn('sudo -n "$PYTHON" -m playwright install-deps chromium', script)
        self.assertNotIn("playwright install --with-deps", script)

    def test_startup_gate_waits_for_real_cold_render_and_preserves_child_log(self):
        script = (ROOT / "scripts/preflight.sh").read_text(encoding="utf-8")
        self.assertIn('name="Prioridades comerciais explicáveis").wait_for(\n            timeout=120_000)', script)
        self.assertIn('cat "$log" >&2', script)

    def test_TC46_clean_startup_owns_only_its_child_without_recursion(self):
        sentinel = subprocess.Popen((sys.executable, "-c", "import time; time.sleep(30)"))
        server = None
        try:
            with tempfile.TemporaryDirectory() as directory:
                app_path = Path(directory) / "smoke.py"
                app_path.write_text("import streamlit as st\nst.title('TC-46')\n", encoding="utf-8")
                with managed_streamlit_server(app_path, timeout=20) as (server, base_url):
                    self.assertIsNone(server.poll())
                    self.assertIsNone(sentinel.poll())
                    with urlopen(base_url + "/_stcore/health", timeout=2) as response:
                        self.assertEqual(response.status, 200)
                    self.assertFalse(any("preflight.sh" in str(argument) for argument in server.args))
            self.assertIsNotNone(server.poll())
            self.assertIsNone(sentinel.poll())
        finally:
            sentinel.terminate()
            sentinel.wait(timeout=5)

    def test_live_verifier_local_contract_is_not_TC47(self):
        identity = ("revision-abc", "source-def", "fingerprint-ghi")
        html = ("<html><body><h1>Prioridades comerciais explicáveis</h1>"
                f"<p>revisão {identity[0]} · fingerprint {identity[2]} · fonte {identity[1]}</p>"
                "<p>Prioridade relativa</p>"
                "<button role='tab'>Engaging</button><button role='tab'>Prospecting</button>"
                "</body></html>")
        with _html_server(html) as url:
            self.assertTrue(verify_live_revision(url, *identity))
            with self.assertRaisesRegex(AssertionError, "Identidade renderizada divergente"):
                verify_live_revision(url, identity[0], "source-errada", identity[2])
        delayed = ("<html><body><h1>Prioridades comerciais explicáveis</h1><div id='app'></div>"
                   "<script>setTimeout(() => { document.querySelector('#app').innerHTML = `"
                   f"<p>revisão {identity[0]} · fingerprint {identity[2]} · fonte {identity[1]}</p>"
                   "<p>Prioridade relativa</p><button role='tab'>Engaging</button>"
                   "<button role='tab'>Prospecting</button>`; }, 100);</script></body></html>")
        with _html_server(delayed) as url:
            self.assertTrue(verify_live_revision(url, *identity))
        missing_stage = ("<h1>Prioridades comerciais explicáveis</h1>"
                         f"<p>revisão {identity[0]} fingerprint {identity[2]} fonte {identity[1]}</p>"
                         "<p>Prioridade relativa</p>"
                         "<button role='tab'>Engaging</button>")
        with _html_server(missing_stage) as url, self.assertRaisesRegex(AssertionError, "Visão de estágio ausente"):
            verify_live_revision(url, *identity)
        with self.assertRaises(ValueError):
            verify_live_revision("", *identity)


def _run_cli(argv):
    parser = argparse.ArgumentParser(description="Verificação renderizada do Lead Scorer")
    commands = parser.add_subparsers(dest="command", required=True)
    live = commands.add_parser("live", help="Executa o gate pós-deploy TC-47")
    live.add_argument("--url", required=True)
    live.add_argument("--revision", required=True)
    live.add_argument("--source-digest", required=True)
    live.add_argument("--fingerprint", required=True)
    commands.add_parser("startup", help="Valida o app real local em um processo filho")
    args = parser.parse_args(argv)
    if args.command == "live":
        verify_live_revision(args.url, args.revision, args.source_digest, args.fingerprint)
        print("TC-47 LIVE OK")
        return
    with managed_streamlit_server(ROOT / "app.py") as (_, url):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=120_000)
                page.get_by_role("heading", name="Prioridades comerciais explicáveis").wait_for(
                    timeout=RENDER_TIMEOUT_MS)
                for stage in ("Engaging", "Prospecting"):
                    page.get_by_role("tab", name=stage, exact=True).wait_for()
                print("REAL STARTUP OK", " | ".join(page.locator("body").inner_text().splitlines()[:8]))
            finally:
                browser.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("live", "startup"):
        _run_cli(sys.argv[1:])
    else:
        unittest.main(verbosity=2)
