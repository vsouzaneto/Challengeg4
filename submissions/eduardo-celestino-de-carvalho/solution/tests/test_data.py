"""Contratos de carga que evitam perda silenciosa e vazamento de desfecho."""

from __future__ import annotations

from copy import deepcopy
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from zipfile import ZipFile
import csv

from leadscore.data import DataQualityError, EXPECTED_COLUMNS, load_dataset, quality_report


def _tables() -> dict[str, list[dict[str, str]]]:
    return {
        "accounts.csv": [{
            "account": "Conta A", "sector": "technolgy", "year_established": "2010",
            "revenue": "10.5", "employees": "20", "office_location": "US",
            "subsidiary_of": "",
        }],
        "products.csv": [{"product": "GTX Pro", "series": "GTX", "sales_price": "100"}],
        "sales_teams.csv": [{
            "sales_agent": "Vendedor A", "manager": "Manager A", "regional_office": "East",
        }],
        "sales_pipeline.csv": [
            {
                "opportunity_id": "O1", "sales_agent": "Vendedor A", "product": "GTXPro",
                "account": "Conta A", "deal_stage": "Won", "engage_date": "2017-01-01",
                "close_date": "2017-02-01", "close_value": "110",
            },
            {
                "opportunity_id": "O2", "sales_agent": "Vendedor A", "product": "GTX Pro",
                "account": "Conta A", "deal_stage": "Lost", "engage_date": "2017-01-01",
                "close_date": "2017-02-02", "close_value": "0",
            },
            {
                "opportunity_id": "O3", "sales_agent": "Vendedor A", "product": "GTXPro",
                "account": "", "deal_stage": "Engaging", "engage_date": "2017-03-01",
                "close_date": "", "close_value": "",
            },
            {
                "opportunity_id": "O4", "sales_agent": "Vendedor A", "product": "GTX Pro",
                "account": "", "deal_stage": "Prospecting", "engage_date": "",
                "close_date": "", "close_value": "",
            },
        ],
    }


def _write_archive(path: Path, tables: dict[str, list[dict[str, str]]]) -> None:
    with ZipFile(path, "w") as archive:
        for name, rows in tables.items():
            text = StringIO()
            writer = csv.DictWriter(text, fieldnames=EXPECTED_COLUMNS[name])
            writer.writeheader()
            writer.writerows(rows)
            archive.writestr(name, text.getvalue())


class DatasetContractTests(TestCase):
    def setUp(self) -> None:
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "crm.zip"
        self.tables = _tables()

    def load(self):
        _write_archive(self.path, self.tables)
        return load_dataset(self.path, expected_sha256=None)

    def test_valid_dataset_preserves_all_rows_and_traces_aliases(self) -> None:
        dataset = self.load()
        self.assertEqual(len(dataset.opportunities), 4)
        self.assertEqual(dataset.opportunities[0].product_raw, "GTXPro")
        self.assertEqual(dataset.opportunities[0].product, "GTX Pro")
        self.assertIsNone(dataset.opportunities[2].account)
        self.assertIsNone(dataset.opportunities[2].close_value)
        self.assertEqual(dataset.accounts["Conta A"].sector, "technology")
        self.assertEqual(dataset.alias_counts["product:GTXPro->GTX Pro"], 2)
        self.assertEqual(quality_report(dataset)["dropped_rows"], 0)
        self.assertEqual(quality_report(dataset)["missing_by_stage"]["Engaging"]["account"], 1)

    def test_duplicate_opportunity_is_rejected(self) -> None:
        duplicate = deepcopy(self.tables["sales_pipeline.csv"][0])
        self.tables["sales_pipeline.csv"].append(duplicate)
        with self.assertRaisesRegex(DataQualityError, "Oportunidade duplicada"):
            self.load()

    def test_unknown_product_does_not_disappear_in_join(self) -> None:
        self.tables["sales_pipeline.csv"][0]["product"] = "Produto inexistente"
        with self.assertRaisesRegex(DataQualityError, "Produto desconhecido"):
            self.load()

    def test_future_close_date_cannot_precede_engagement(self) -> None:
        self.tables["sales_pipeline.csv"][0]["close_date"] = "2016-12-31"
        with self.assertRaisesRegex(DataQualityError, "engage_date após close_date"):
            self.load()

    def test_open_deal_cannot_contain_outcome(self) -> None:
        self.tables["sales_pipeline.csv"][2]["close_value"] = "100"
        with self.assertRaisesRegex(DataQualityError, "Negócio aberto com desfecho"):
            self.load()

    def test_missing_account_is_allowed_only_as_explicit_none(self) -> None:
        dataset = self.load()
        self.assertIsNone(dataset.opportunities[3].account)
        self.tables["sales_pipeline.csv"][3]["account"] = "Conta desconhecida"
        with self.assertRaisesRegex(DataQualityError, "Conta desconhecida"):
            self.load()

    def test_changed_source_hash_requires_reaudit(self) -> None:
        _write_archive(self.path, self.tables)
        with self.assertRaisesRegex(DataQualityError, "SHA-256 inesperado"):
            load_dataset(self.path, expected_sha256="0" * 64)
