"""Carga verificável do dataset público CRM Sales Predictive Analytics.

O ZIP original é preservado. Correções de grafia acontecem apenas nos registros
tipados retornados por ``load_dataset`` e são contabilizadas no relatório.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from pathlib import Path
from typing import Mapping
from urllib.request import Request, urlopen
from zipfile import BadZipFile, ZipFile
import csv
import io
import json
import os
import shutil


SOURCE_URL = (
    "https://www.kaggle.com/api/v1/datasets/download/"
    "agungpambudi/crm-sales-predictive-analytics"
)
SOURCE_SHA256 = "74d535826330b616758ebb6bb393abf701a5126364a72fbe71003cb6a7a87a9c"
ARCHIVE_NAME = "crm-sales-predictive-analytics.zip"

EXPECTED_COLUMNS: Mapping[str, tuple[str, ...]] = {
    "accounts.csv": (
        "account", "sector", "year_established", "revenue", "employees",
        "office_location", "subsidiary_of",
    ),
    "products.csv": ("product", "series", "sales_price"),
    "sales_teams.csv": ("sales_agent", "manager", "regional_office"),
    "sales_pipeline.csv": (
        "opportunity_id", "sales_agent", "product", "account",
        "deal_stage", "engage_date", "close_date", "close_value",
    ),
}
PRODUCT_ALIASES = {"GTXPro": "GTX Pro"}
SECTOR_ALIASES = {"technolgy": "technology"}
OPEN_STAGES = frozenset({"Prospecting", "Engaging"})
CLOSED_STAGES = frozenset({"Won", "Lost"})


class DataQualityError(ValueError):
    """O dataset mudou ou contém um registro que não atende ao contrato."""


@dataclass(frozen=True)
class Account:
    name: str
    sector_raw: str
    sector: str
    year_established: int
    revenue_musd: Decimal
    employees: int
    office_location: str
    subsidiary_of: str | None


@dataclass(frozen=True)
class Product:
    name: str
    series: str
    sales_price: Decimal


@dataclass(frozen=True)
class SalesAgent:
    name: str
    manager: str
    regional_office: str


@dataclass(frozen=True)
class Opportunity:
    opportunity_id: str
    sales_agent: str
    product_raw: str
    product: str
    account: str | None
    deal_stage: str
    engage_date: date | None
    close_date: date | None
    close_value: Decimal | None


@dataclass(frozen=True)
class Dataset:
    archive_sha256: str
    accounts: Mapping[str, Account]
    products: Mapping[str, Product]
    sales_agents: Mapping[str, SalesAgent]
    opportunities: tuple[Opportunity, ...]
    alias_counts: Mapping[str, int]


def _digest(path: Path) -> str:
    checksum = sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def download_archive(destination: Path, *, expected_sha256: str = SOURCE_SHA256) -> Path:
    """Baixa a versão auditada e falha se a origem pública tiver mudado."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        actual = _digest(destination)
        if actual != expected_sha256:
            raise DataQualityError(
                f"ZIP local mudou: SHA-256 {actual}; esperado {expected_sha256}. "
                "Reaudite a fonte antes de usar outra versão."
            )
        return destination

    partial = destination.with_name(destination.name + ".part")
    try:
        request = Request(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=45) as response, partial.open("wb") as file:
            shutil.copyfileobj(response, file)
        actual = _digest(partial)
        if actual != expected_sha256:
            raise DataQualityError(
                f"Download mudou: SHA-256 {actual}; esperado {expected_sha256}. "
                "Atualize a auditoria antes de continuar."
            )
        os.replace(partial, destination)
    finally:
        partial.unlink(missing_ok=True)
    return destination


def _rows(archive: ZipFile, name: str) -> list[dict[str, str]]:
    try:
        member = archive.getinfo(name)
    except KeyError as exc:
        raise DataQualityError(f"Arquivo obrigatório ausente: {name}") from exc
    if member.file_size > 20_000_000:
        raise DataQualityError(f"Arquivo inesperadamente grande: {name}")

    with archive.open(member) as raw:
        reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", newline=""))
        if reader.fieldnames is None or set(reader.fieldnames) != set(EXPECTED_COLUMNS[name]):
            raise DataQualityError(
                f"Schema inesperado em {name}: {reader.fieldnames}; "
                f"esperado {EXPECTED_COLUMNS[name]}"
            )
        result = []
        for number, row in enumerate(reader, start=2):
            if None in row or any(value is None for value in row.values()):
                raise DataQualityError(f"CSV irregular em {name}, linha {number}")
            result.append(row)
    if not result:
        raise DataQualityError(f"Tabela vazia: {name}")
    return result


def _required(value: str, *, field: str, row: int) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise DataQualityError(f"{field} vazio na linha {row}")
    return cleaned


def _optional(value: str) -> str | None:
    return value.strip() or None


def _integer(value: str, *, field: str, row: int, minimum: int = 1) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise DataQualityError(f"{field} inválido na linha {row}: {value!r}") from exc
    if parsed < minimum:
        raise DataQualityError(f"{field} abaixo de {minimum} na linha {row}")
    return parsed


def _money(value: str, *, field: str, row: int, positive: bool = False) -> Decimal:
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise DataQualityError(f"{field} inválido na linha {row}: {value!r}") from exc
    if not parsed.is_finite() or (parsed <= 0 if positive else parsed < 0):
        raise DataQualityError(f"{field} fora do intervalo na linha {row}: {value!r}")
    return parsed


def _date(value: str, *, field: str, row: int) -> date | None:
    if not value.strip():
        return None
    try:
        return date.fromisoformat(value.strip())
    except ValueError as exc:
        raise DataQualityError(f"{field} inválida na linha {row}: {value!r}") from exc


def _index(items: list, *, label: str, key: str) -> dict:
    result = {}
    for item in items:
        value = getattr(item, key)
        if value in result:
            raise DataQualityError(f"{label} duplicado: {value}")
        result[value] = item
    return result


def load_dataset(
    archive_path: Path, *, expected_sha256: str | None = SOURCE_SHA256
) -> Dataset:
    """Valida todas as linhas e retorna as quatro tabelas tipadas, sem descartes."""
    archive_path = Path(archive_path)
    archive_sha = _digest(archive_path)
    if expected_sha256 is not None and archive_sha != expected_sha256:
        raise DataQualityError(
            f"SHA-256 inesperado: {archive_sha}; esperado {expected_sha256}"
        )
    try:
        with ZipFile(archive_path) as archive:
            raw = {name: _rows(archive, name) for name in EXPECTED_COLUMNS}
    except BadZipFile as exc:
        raise DataQualityError("Arquivo ZIP inválido") from exc

    aliases: Counter[str] = Counter()
    account_items: list[Account] = []
    for number, row in enumerate(raw["accounts.csv"], start=2):
        sector_raw = _required(row["sector"], field="sector", row=number)
        sector = SECTOR_ALIASES.get(sector_raw, sector_raw)
        if sector != sector_raw:
            aliases[f"sector:{sector_raw}->{sector}"] += 1
        year = _integer(row["year_established"], field="year_established", row=number)
        if year > 2100:
            raise DataQualityError(f"year_established improvável na linha {number}")
        account_items.append(Account(
            name=_required(row["account"], field="account", row=number),
            sector_raw=sector_raw,
            sector=sector,
            year_established=year,
            revenue_musd=_money(row["revenue"], field="revenue", row=number),
            employees=_integer(row["employees"], field="employees", row=number),
            office_location=_required(row["office_location"], field="office_location", row=number),
            subsidiary_of=_optional(row["subsidiary_of"]),
        ))
    accounts = _index(account_items, label="Conta", key="name")

    product_items = [Product(
        name=_required(row["product"], field="product", row=number),
        series=_required(row["series"], field="series", row=number),
        sales_price=_money(row["sales_price"], field="sales_price", row=number, positive=True),
    ) for number, row in enumerate(raw["products.csv"], start=2)]
    products = _index(product_items, label="Produto", key="name")
    for raw_name, canonical in PRODUCT_ALIASES.items():
        if canonical not in products:
            raise DataQualityError(f"Alias {raw_name} aponta para produto ausente: {canonical}")

    agent_items = [SalesAgent(
        name=_required(row["sales_agent"], field="sales_agent", row=number),
        manager=_required(row["manager"], field="manager", row=number),
        regional_office=_required(row["regional_office"], field="regional_office", row=number),
    ) for number, row in enumerate(raw["sales_teams.csv"], start=2)]
    agents = _index(agent_items, label="Vendedor", key="name")

    opportunity_items: list[Opportunity] = []
    seen_ids: set[str] = set()
    for number, row in enumerate(raw["sales_pipeline.csv"], start=2):
        opportunity_id = _required(row["opportunity_id"], field="opportunity_id", row=number)
        if opportunity_id in seen_ids:
            raise DataQualityError(f"Oportunidade duplicada: {opportunity_id}")
        seen_ids.add(opportunity_id)

        agent = _required(row["sales_agent"], field="sales_agent", row=number)
        if agent not in agents:
            raise DataQualityError(f"Vendedor desconhecido na linha {number}: {agent}")
        product_raw = _required(row["product"], field="product", row=number)
        product = PRODUCT_ALIASES.get(product_raw, product_raw)
        if product not in products:
            raise DataQualityError(f"Produto desconhecido na linha {number}: {product_raw}")
        if product != product_raw:
            aliases[f"product:{product_raw}->{product}"] += 1
        account = _optional(row["account"])
        if account is not None and account not in accounts:
            raise DataQualityError(f"Conta desconhecida na linha {number}: {account}")

        stage = _required(row["deal_stage"], field="deal_stage", row=number)
        if stage not in OPEN_STAGES | CLOSED_STAGES:
            raise DataQualityError(f"Etapa desconhecida na linha {number}: {stage}")
        engage = _date(row["engage_date"], field="engage_date", row=number)
        close = _date(row["close_date"], field="close_date", row=number)
        value = (
            _money(row["close_value"], field="close_value", row=number)
            if row["close_value"].strip() else None
        )
        if stage == "Prospecting" and engage is not None:
            raise DataQualityError(f"Prospecting já tem engage_date na linha {number}")
        if stage == "Engaging" and engage is None:
            raise DataQualityError(f"Engaging sem engage_date na linha {number}")
        if stage in OPEN_STAGES and (close is not None or value is not None):
            raise DataQualityError(f"Negócio aberto com desfecho na linha {number}")
        if stage in CLOSED_STAGES and (engage is None or close is None or value is None):
            raise DataQualityError(f"Negócio concluído incompleto na linha {number}")
        if engage is not None and close is not None and engage > close:
            raise DataQualityError(f"engage_date após close_date na linha {number}")
        if stage == "Won" and value is not None and value <= 0:
            raise DataQualityError(f"Won sem receita positiva na linha {number}")
        if stage == "Lost" and value is not None and value != 0:
            raise DataQualityError(f"Lost com receita na linha {number}")

        opportunity_items.append(Opportunity(
            opportunity_id=opportunity_id,
            sales_agent=agent,
            product_raw=product_raw,
            product=product,
            account=account,
            deal_stage=stage,
            engage_date=engage,
            close_date=close,
            close_value=value,
        ))

    return Dataset(
        archive_sha256=archive_sha,
        accounts=accounts,
        products=products,
        sales_agents=agents,
        opportunities=tuple(opportunity_items),
        alias_counts=dict(aliases),
    )


def quality_report(dataset: Dataset) -> dict:
    """Resumo serializável sem nomes de clientes nem linhas individuais."""
    opportunities = dataset.opportunities
    stages = Counter(item.deal_stage for item in opportunities)
    dates = {
        field: [getattr(item, field) for item in opportunities if getattr(item, field) is not None]
        for field in ("engage_date", "close_date")
    }
    return {
        "source_url": SOURCE_URL,
        "archive_sha256": dataset.archive_sha256,
        "row_counts": {
            "accounts": len(dataset.accounts),
            "products": len(dataset.products),
            "sales_teams": len(dataset.sales_agents),
            "sales_pipeline": len(opportunities),
        },
        "stages": dict(sorted(stages.items())),
        "closed": sum(stages[stage] for stage in CLOSED_STAGES),
        "open": sum(stages[stage] for stage in OPEN_STAGES),
        "missing": {
            "account": sum(item.account is None for item in opportunities),
            "engage_date": sum(item.engage_date is None for item in opportunities),
            "close_date": sum(item.close_date is None for item in opportunities),
            "close_value": sum(item.close_value is None for item in opportunities),
        },
        "missing_by_stage": {
            stage: {
                "account": sum(item.account is None for item in opportunities if item.deal_stage == stage),
                "engage_date": sum(item.engage_date is None for item in opportunities if item.deal_stage == stage),
                "close_date": sum(item.close_date is None for item in opportunities if item.deal_stage == stage),
                "close_value": sum(item.close_value is None for item in opportunities if item.deal_stage == stage),
            }
            for stage in sorted(stages)
        },
        "aliases_applied": dict(sorted(dataset.alias_counts.items())),
        "date_ranges": {
            field: {"first": min(values).isoformat(), "last": max(values).isoformat()}
            for field, values in dates.items() if values
        },
        "dropped_rows": 0,
    }


def report_json(dataset: Dataset) -> str:
    return json.dumps(quality_report(dataset), ensure_ascii=False, indent=2) + "\n"
