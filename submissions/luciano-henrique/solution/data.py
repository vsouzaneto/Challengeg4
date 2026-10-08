"""Leitura e validação dos CSVs originais, sem escrita em disco."""

import csv
from dataclasses import dataclass
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
OPEN_STAGES = frozenset({"Prospecting", "Engaging"})
CLOSED_STAGES = frozenset({"Won", "Lost"})
REQUIRED_COLUMNS = {
    "accounts": {"account", "sector", "year_established", "revenue", "employees", "office_location", "subsidiary_of"},
    "products": {"product", "series", "sales_price"},
    "sales_teams": {"sales_agent", "manager", "regional_office"},
    "sales_pipeline": {"opportunity_id", "sales_agent", "product", "account", "deal_stage", "engage_date", "close_date", "close_value"},
}


@dataclass
class Dataset:
    accounts: dict[str, dict[str, str]]
    products: dict[str, dict[str, str]]
    sales_teams: dict[str, dict[str, str]]
    opportunities: list[dict[str, str]]

    @property
    def open_opportunities(self):
        return [row for row in self.opportunities if row["deal_stage"] in OPEN_STAGES]

    @property
    def closed_opportunities(self):
        return [row for row in self.opportunities if row["deal_stage"] in CLOSED_STAGES]


def normalize_product(name: str) -> str:
    """Alias conhecido e explícito; não altera o arquivo de origem."""
    return "GTX Pro" if name == "GTXPro" else name


def read_table(directory: Path, name: str) -> list[dict[str, str]]:
    with (directory / f"{name}.csv").open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        columns = reader.fieldnames or []
        missing = REQUIRED_COLUMNS[name] - set(columns)
        if missing or len(columns) != len(set(columns)):
            raise ValueError(f"Cabeçalho inválido em {name}: ausentes={sorted(missing)}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"Tabela vazia: {name}")
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError(f"Linha com número incorreto de colunas em {name}")
    return rows


def unique_index(rows, key):
    index = {}
    for row in rows:
        value = row[key]
        if not value or value in index:
            raise ValueError(f"Chave vazia ou duplicada: {key}={value!r}")
        index[value] = row
    return index


def load_data(directory: Path = DATA_DIR) -> Dataset:
    tables = {name: read_table(Path(directory), name) for name in REQUIRED_COLUMNS}
    for name in ("products", "sales_pipeline"):
        for row in tables[name]:
            row["product"] = normalize_product(row["product"])
    dataset = Dataset(
        unique_index(tables["accounts"], "account"),
        unique_index(tables["products"], "product"),
        unique_index(tables["sales_teams"], "sales_agent"),
        tables["sales_pipeline"],
    )
    unique_index(dataset.opportunities, "opportunity_id")
    for row in dataset.opportunities:
        if row["deal_stage"] not in OPEN_STAGES | CLOSED_STAGES:
            raise ValueError(f"Estágio desconhecido: {row['deal_stage']}")
        for key, index in (("product", dataset.products), ("sales_agent", dataset.sales_teams)):
            if row[key] not in index:
                raise ValueError(f"Sem correspondência: {key}={row[key]!r}")
        # Conta ausente é esperada e nunca elimina uma oportunidade.
        if row["account"] and row["account"] not in dataset.accounts:
            raise ValueError(f"Conta sem correspondência: {row['account']!r}")
    return dataset
