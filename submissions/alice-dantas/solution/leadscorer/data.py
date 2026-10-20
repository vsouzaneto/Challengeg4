"""Carga, normalização e junções dos CSVs do CRM (ADR-002).

Os CSVs são somente leitura. Cada junção é m:1 e registra as linhas depois
do passo, para provar que nenhuma oportunidade some em silêncio. Qualquer
problema de arquivo vira `DataError` antes de existir uma lista parcial.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Tuple

import pandas as pd

from . import codes, policy
from .errors import DataError

TABLES = ("sales_pipeline", "products", "sales_teams", "accounts")
MAX_IDS_IN_MESSAGE = 10


# Lacunas que cada junção conta (chaves; o texto é da CLI).
GAP_NULL_PRICE, GAP_NULL_MANAGER, GAP_ORPHAN_ACCOUNT = "null_price", "null_manager", "orphan_account"


@dataclass(frozen=True)
class JoinStep:
    table: str
    rows: int
    gap: Optional[str] = None
    gap_count: int = 0


@dataclass(frozen=True)
class Dataset:
    opportunities: pd.DataFrame
    teams: pd.DataFrame
    steps: List[JoinStep]
    hashes: Dict[str, str]
    unmatched_without_map: int
    # Atributos do cliente (setor, receita anual, sede), só para a Inteligência (ADR-007):
    # ficam fora de `opportunities` para o scoring nunca enxergá-los.
    accounts: pd.DataFrame

    @property
    def audited(self) -> bool:
        return all(self.hashes[t] == policy.AUDITED_SHA256[t] for t in TABLES)

    @property
    def sellers(self) -> Tuple[str, ...]:
        return tuple(sorted(self.teams["sales_agent"]))


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(policy.SOLUTION_DIR))
    except ValueError:
        return str(path)


def id_list(ids: Iterable[str]) -> str:
    ids = list(ids)
    shown = ", ".join(ids[:MAX_IDS_IN_MESSAGE])
    rest = len(ids) - MAX_IDS_IN_MESSAGE
    return f"{shown} e mais {rest}" if rest > 0 else shown


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_files(raw_dir: Path) -> None:
    missing = [f"{t}.csv" for t in TABLES if not (raw_dir / f"{t}.csv").is_file()]
    if missing:
        raise DataError(
            f"Arquivo ausente: {', '.join(missing)}. Pasta esperada: {display_path(raw_dir)}/. "
            f"Baixe o dataset pelo navegador em {policy.DATASET_URL} e copie os CSVs para "
            "essa pasta (passo a passo em data/raw/README.md).",
            code=codes.DATA_FILE_MISSING, files=missing, folder=display_path(raw_dir),
        )


def read_table(raw_dir: Path, table: str) -> pd.DataFrame:
    path = raw_dir / f"{table}.csv"
    expected = ", ".join(policy.REQUIRED_COLUMNS[table])
    try:
        # Tudo como texto; só a célula vazia vira nulo ("NA" continua sendo texto).
        frame = pd.read_csv(path, dtype=str, keep_default_na=False, na_values=[""])
    except pd.errors.EmptyDataError:
        raise DataError(f"{table}.csv está vazio. Colunas esperadas: {expected}.",
                        code=codes.DATA_FILE_EMPTY, table=table) from None
    except (pd.errors.ParserError, UnicodeDecodeError):
        raise DataError(f"{table}.csv não é um CSV válido. Colunas esperadas: {expected}.",
                        code=codes.DATA_FILE_INVALID, table=table) from None
    missing = [c for c in policy.REQUIRED_COLUMNS[table] if c not in frame.columns]
    if missing:
        raise DataError(f"{table}.csv sem as colunas: {', '.join(missing)}.",
                        code=codes.DATA_COLUMNS_MISSING, table=table, columns=missing)
    return frame


def unmatched_products(pipeline: pd.DataFrame, products: pd.DataFrame,
                       product_map: Mapping[str, str]) -> pd.DataFrame:
    labels = pipeline["product"].replace(dict(product_map))
    mask = pipeline["product"].notna() & ~labels.isin(products["product"])
    return pipeline.loc[mask, ["opportunity_id", "product"]]


def check_labels(pipeline: pd.DataFrame, products: pd.DataFrame) -> None:
    bad_stage = pipeline[~pipeline["deal_stage"].isin(policy.OPEN_STAGES + policy.CLOSED_STAGES)]
    if not bad_stage.empty:
        labels = sorted(bad_stage["deal_stage"].fillna("(vazio)").unique())
        raise DataError(f"Estágio desconhecido em sales_pipeline.csv: {', '.join(labels)} "
                        f"(IDs: {id_list(bad_stage['opportunity_id'])}). Nenhuma linha foi descartada.",
                        code=codes.DATA_UNKNOWN_LABEL, table="sales_pipeline", column="deal_stage",
                        labels=labels, ids=sorted(bad_stage["opportunity_id"]))
    unknown = unmatched_products(pipeline, products, policy.PRODUCT_MAP)
    if not unknown.empty:
        labels = sorted(unknown["product"].unique())
        raise DataError(
            f"Produto sem cadastro em products.csv: {', '.join(labels)} "
            f"(IDs: {id_list(unknown['opportunity_id'])}). Nenhuma linha foi descartada: inclua o "
            "produto no catálogo ou a grafia em PRODUCT_MAP (leadscorer/policy.py).",
            code=codes.DATA_UNKNOWN_LABEL, table="sales_pipeline", column="product",
            labels=labels, ids=sorted(unknown["opportunity_id"]),
        )


def parse_dates(frame: pd.DataFrame, column: str) -> pd.Series:
    parsed = pd.to_datetime(frame[column], format="%Y-%m-%d", errors="coerce")
    bad = frame[frame[column].notna() & parsed.isna()]
    if not bad.empty:
        raise DataError(f"sales_pipeline.csv: {column} fora do formato AAAA-MM-DD "
                        f"(IDs: {id_list(bad['opportunity_id'])}).",
                        code=codes.DATA_BAD_DATE, table="sales_pipeline", column=column,
                        ids=sorted(bad["opportunity_id"]))
    return parsed


def parse_number(frame: pd.DataFrame, table: str, column: str, key: str, integer: bool) -> pd.Series:
    """Número não negativo (inteiro, se `integer`); a célula vazia fica nula. Qualquer outro
    valor vira erro com as chaves das linhas, sem descarte."""
    parsed = pd.to_numeric(frame[column], errors="coerce")
    invalid = parsed.isna() | (parsed < 0)
    if integer:
        invalid |= parsed.mod(1).fillna(0) != 0
    bad = frame[frame[column].notna() & invalid]
    if not bad.empty:
        kind = "um número inteiro não negativo" if integer else "um número não negativo"
        raise DataError(f"{table}.csv: {column} precisa ser {kind} ({key}: {id_list(bad[key])}).",
                        code=codes.DATA_BAD_NUMBER, table=table, column=column, ids=sorted(bad[key]))
    return parsed.astype("Int64") if integer else parsed.astype("float")


def merge_m1(left: pd.DataFrame, right: pd.DataFrame, key: str, table: str, **kwargs) -> pd.DataFrame:
    try:
        return left.merge(right, on=key, how="left", validate="m:1", **kwargs)
    except pd.errors.MergeError:
        repeated = right[right[key].duplicated()][key].unique()
        raise DataError(f"{table}.csv tem {key} repetido: {', '.join(map(str, repeated))}.",
                        code=codes.DATA_DUPLICATE_KEY, table=table, column=key,
                        values=[str(v) for v in repeated]) from None


def load(raw_dir: Path = policy.RAW_DIR) -> Dataset:
    require_files(raw_dir)
    raw = {t: read_table(raw_dir, t) for t in TABLES}
    hashes = {t: sha256(raw_dir / f"{t}.csv") for t in TABLES}

    pipeline = raw["sales_pipeline"].loc[:, list(policy.REQUIRED_COLUMNS["sales_pipeline"])]
    check_labels(pipeline, raw["products"])
    unmatched_without_map = len(unmatched_products(pipeline, raw["products"], {}))
    pipeline = pipeline.assign(product=pipeline["product"].replace(policy.PRODUCT_MAP))
    steps = [JoinStep("sales_pipeline", len(pipeline))]

    products = raw["products"].loc[:, ["product", "sales_price"]]
    try:
        products = products.assign(sales_price=pd.to_numeric(products["sales_price"]).astype("Int64"))
    except (ValueError, TypeError):
        raise DataError("products.csv: sales_price precisa ser um número inteiro.",
                        code=codes.DATA_BAD_PRICE, table="products", column="sales_price") from None
    frame = merge_m1(pipeline, products, "product", "products")
    steps.append(JoinStep("products", len(frame), GAP_NULL_PRICE, int(frame["sales_price"].isna().sum())))

    teams = raw["sales_teams"].loc[:, list(policy.REQUIRED_COLUMNS["sales_teams"])]
    frame = merge_m1(frame, teams, "sales_agent", "sales_teams")
    steps.append(JoinStep("sales_teams", len(frame), GAP_NULL_MANAGER, int(frame["manager"].isna().sum())))

    accounts = raw["accounts"].loc[:, list(policy.REQUIRED_COLUMNS["accounts"])]
    accounts = accounts.assign(revenue=parse_number(accounts, "accounts", "revenue", "account", integer=False))
    for column, mapping in policy.LABEL_MAPS.items():
        accounts[column] = accounts[column].replace(mapping)
    frame = merge_m1(frame, accounts[["account"]], "account", "accounts", indicator=True)
    orphans = int((frame["account"].notna() & (frame["_merge"] == "left_only")).sum())
    frame = frame.drop(columns="_merge")
    steps.append(JoinStep("accounts", len(frame), GAP_ORPHAN_ACCOUNT, orphans))

    frame["engage_date"] = parse_dates(frame, "engage_date")
    frame["close_date"] = parse_dates(frame, "close_date")
    frame["close_value"] = parse_number(frame, "sales_pipeline", "close_value", "opportunity_id", integer=True)
    return Dataset(frame, teams, steps, hashes, unmatched_without_map, accounts.reset_index(drop=True))
