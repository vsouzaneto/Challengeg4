from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

from analysis import METHOD_VERSION, analyze, content_strategy_30d, executive_answers
from tests.helpers import (default_scope_all_history, driver_rows, frame_from_rows,
                           monthly_sponsorship_rows)


ROOT = Path(__file__).resolve().parents[1]


def result_with_full_executive_evidence() -> dict[str, object]:
    drivers = [{**row, "id": f"driver-{row['id']}", "content_id": f"driver-{row['content_id']}"}
               for row in driver_rows([1.0, 1.2, 0.8])]
    sponsorship = [{**row, "id": f"sponsor-{row['id']}", "content_id": f"sponsor-{row['content_id']}"}
                   for row in monthly_sponsorship_rows(3)]
    rows = drivers + sponsorship
    return analyze(frame_from_rows(rows), default_scope_all_history(rows), "matrix-hash")


class PublishedAnalysisAcceptanceTests(unittest.TestCase):
    def test_four_executive_answers_cover_the_required_matrix(self):
        result = result_with_full_executive_evidence()
        answers = executive_answers(result)
        self.assertEqual(len(answers), 4)
        for answer in answers:
            self.assertTrue(answer["verdict"])
            self.assertTrue(answer["comparison"] and answer["evidence_id"])
            self.assertTrue(answer["stability"])
            self.assertTrue(answer["action"] and answer["change_trigger"])
        strategy = content_strategy_30d(result)
        self.assertEqual(len(strategy["weeks"]), 4)
        self.assertTrue(all(item["owner"] and item["gate"] for item in strategy["weeks"]))

    def test_sponsorship_without_comparable_months_abstains_explicitly(self):
        rows = driver_rows([1.0, 1.2, 0.8])
        answer = executive_answers(
            analyze(frame_from_rows(rows), default_scope_all_history(rows), "no-sponsorship")
        )[1]
        self.assertEqual(answer["verdict"], "NÃO ESCALAR PATROCÍNIO AGORA")
        self.assertIn("não mensurável", answer["stability"].lower())

    def test_published_csv_parses_in_fresh_process_with_default_field_limit(self):
        completed = subprocess.run(
            [sys.executable, "-c", "import csv,sys; assert csv.field_size_limit()==131072; f=open(sys.argv[1],newline=''); rows=list(csv.DictReader(f)); f.close(); assert rows; assert csv.field_size_limit()==131072", str(ROOT / "evidence.csv")],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_published_queue_matches_export_order_and_recomputes_priority(self):
        with (ROOT / "evidence.csv").open(encoding="utf-8", newline="") as handle:
            rows = [row for row in csv.DictReader(handle) if row["record_type"] == "recommendation"]
        report = (ROOT / "analysis.md").read_text(encoding="utf-8").split("## O que os dados", 1)[0]
        cited = re.findall(r"Evidência: ([\w-]+)", report)
        self.assertGreaterEqual(len(rows), 3)
        self.assertEqual(cited, [row["evidence_id"] for row in rows[:3]])
        for rank, row in enumerate(rows, 1):
            self.assertEqual(row["method_version"], METHOD_VERSION)
            self.assertEqual(int(row["rank"]), rank)
            values, normalization = json.loads(row["priority_values"]), json.loads(row["normalization"])
            impact = sum(min(value / normalization[key], 1) if normalization[key] else 0 for key, value in values.items()) / 3
            self.assertAlmostEqual(float(row["impact"]), impact)
            expected = 100 * impact * float(row["strength"]) * float(row["recency"])
            self.assertAlmostEqual(float(row["priority"]), expected, delta=abs(expected) * 1e-12)
            if rank > 3:
                continue
            self.assertIn(f"{expected:.6g}", report)
            frequency = json.loads(row["frequency_hypothesis"])
            self.assertEqual(frequency["status"], "test")
            self.assertEqual(frequency["period_month"], json.loads(row["context"])["period_month"])
            self.assertEqual(frequency["coverage_rule"], "complete_iso_weeks_within_calendar_month_and_scope")
            self.assertIn(f"mês {frequency['period_month']}", report)
            self.assertIn(frequency["coverage_rule"], report)
            self.assertIn(f"Testar {frequency['value']:g} posts por creator por semana ISO completa", report)
            self.assertIn(f"{frequency['sample_creator_weeks']} creator-semanas", report)
            self.assertIn(f"{frequency['observed_complete_weeks']} semanas observadas", report)

    def test_every_evidence_id_cited_by_report_exists_in_export(self):
        with (ROOT / "evidence.csv").open(encoding="utf-8", newline="") as handle:
            exported = {row["evidence_id"] for row in csv.DictReader(handle) if row["record_type"] == "evidence"}
        cited = set(re.findall(r"`((?:summary|dimension|driver(?:-overview)?|strategy(?:-week)?|sponsorship(?:-overview)?|audience(?:-overview)?)-[0-9a-f]{16})`", (ROOT / "analysis.md").read_text(encoding="utf-8")))
        self.assertTrue(cited)
        self.assertEqual(cited - exported, set())

    def test_report_covers_mandatory_analysis_and_strategy_topics(self):
        report = (ROOT / "analysis.md").read_text(encoding="utf-8").lower()
        for term in ("plataforma", "conteúdo", "categoria", "creator", "audiência", "patrocínio", "frequência", "parar/revisar", "quick wins", "roi", "causalidade"):
            with self.subTest(term=term):
                self.assertIn(term, report)

    def test_report_answers_all_mandatory_questions_with_kpis_and_actions(self):
        report = (ROOT / "analysis.md").read_text(encoding="utf-8")
        required = {
            "O que gera engajamento?": (
                "NÃO EXISTE VENCEDOR SUSTENTADO; NÃO REDISTRIBUIR O MIX",
                "Limiar material: 0,162 p.p.", "20 contextos avaliados", "Ação:",
            ),
            "Vale patrocinar influenciadores?": (
                "NÃO ESCALAR PATROCÍNIO AGORA", "Cobertura comparável: 1,56%",
                "12 estratos elegíveis", "Estabilidade: 100,0% em 4 meses", "Ação:",
            ),
            "Qual deve ser a estratégia?": (
                "EXECUTAR PROGRAMA DE 30 DIAS PARA VALIDAR YOUTUBE / VÍDEO / ESTILO DE VIDA / 100.000–499.999",
                "4 semanas", "C=0,950", "3 meses elegíveis", "Ação:",
            ),
            "Qual perfil de audiência mais engaja?": (
                "NÃO HÁ PERFIL GLOBAL COMPROVADO", "Cobertura controlada",
                "Ação:",
            ),
        }
        executive = report.split("## Decisão para segunda-feira", 1)[0]
        self.assertEqual(executive.count("- KPI:"), 4)
        self.assertEqual(executive.count("- Comparação:"), 4)
        self.assertEqual(executive.count("- Amostra:"), 4)
        self.assertEqual(executive.count("- Ação:"), 4)
        self.assertEqual(executive.count("- Estabilidade"), 4)
        self.assertEqual(executive.count("- Muda se:"), 4)
        self.assertEqual(executive.count("- Evidência:"), 4)
        for question, evidence in required.items():
            section = executive.split(f"### {question}", 1)[1].split("### ", 1)[0]
            for expected in evidence:
                self.assertIn(expected, section)


if __name__ == "__main__":
    unittest.main()
