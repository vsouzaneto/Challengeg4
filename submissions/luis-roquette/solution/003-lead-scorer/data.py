"""Verified CRM snapshots and cardinality-preserving normalization (no scoring)."""
from __future__ import annotations

import csv
import argparse
import fcntl
import hashlib
import io
import json
import math
import os
import re
import shutil
import stat
import uuid
import zipfile
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, build_opener
from contextlib import contextmanager
from dataclasses import asdict, dataclass, is_dataclass
from datetime import date
from pathlib import Path
from typing import Mapping

import pandas as pd

ROOT = Path(__file__).resolve().parent
SCHEMA = {
    "accounts.csv": ("account", "year_established"),
    "products.csv": ("product", "series", "sales_price"),
    "sales_teams.csv": ("sales_agent", "manager", "regional_office"),
    "sales_pipeline.csv": ("opportunity_id", "sales_agent", "product", "account",
                           "deal_stage", "engage_date", "close_date", "close_value"),
}
KEYS = {name: fields[0] for name, fields in SCHEMA.items()}
ACTIVE = frozenset(("Engaging", "Prospecting"))
CLOSED = frozenset(("Won", "Lost"))


@dataclass(frozen=True)
class Diagnostic:
    code: str
    scope: str
    file: str | None
    opportunity_id: str | None
    field: str | None
    reason: str
    correction: str


class DataValidationError(ValueError):
    def __init__(self, diagnostics):
        self.diagnostics = tuple(diagnostics)
        super().__init__("; ".join(f"{d.file}: {d.reason}. {d.correction}"
                                   for d in self.diagnostics))


@dataclass(frozen=True)
class Snapshot:
    """Immutable bytes are shared by verification, parsing and cache hashing."""
    files: tuple[tuple[str, bytes], ...]
    manifest_json: str
    dependency_digest: str


@dataclass(frozen=True)
class Dataset:
    """Frames are owned by this result; consumers must not mutate cached frames."""
    opportunities: pd.DataFrame
    accounts: pd.DataFrame
    products: pd.DataFrame
    sales_teams: pd.DataFrame
    diagnostics: tuple[Diagnostic, ...]
    counts: Mapping[str, int]
    data_fingerprint: str


def _block(code, filename, field, reason, correction):
    raise DataValidationError((Diagnostic(code, "global", filename, None, field,
                                          reason, correction),))


def _canonical(value):
    if is_dataclass(value):
        value = asdict(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def _read_manifest(manifest_path):
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entries = manifest["files"]
        if not isinstance(entries, dict) or manifest["schema_version"] != 1 or set(entries) != set(SCHEMA):
            raise ValueError("schema_version/files")
        for name, entry in entries.items():
            if not isinstance(entry, dict) or not isinstance(entry.get("headers"), list):
                raise ValueError(name)
            if not all(isinstance(column, str) for column in entry["headers"]) or not all(
                isinstance(entry.get(key), str) and entry[key]
                for key in ("sha256", "source_url", "license", "download_url")):
                raise ValueError(name)
            if len(entry["sha256"]) != 64 or any(c not in "0123456789abcdef" for c in entry["sha256"]):
                raise ValueError(name)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        _block("manifest_invalid", str(manifest_path), None,
               f"Manifesto ausente ou inválido ({exc})", "Restaure o manifesto versionado")
    return manifest


def read_snapshot(raw_dir, manifest_path, verify_checksums=True):
    return _read_snapshot(raw_dir, manifest_path, verify_checksums)


def _read_snapshot(raw_dir, manifest_path, verify_checksums=True, *, recovery=False):
    raw_dir, manifest_path = Path(raw_dir), Path(manifest_path)
    marker = raw_dir.parent / ".recovery.lock"
    def check_marker():
        if not recovery and (marker.exists() or marker.is_symlink()):
            _block("recovery_in_progress", str(marker), None,
                   "Recuperação em andamento ou interrompida",
                   "Execute data.py recover --resume com o mesmo manifesto e diretório raw")
    check_marker()
    manifest = _read_manifest(manifest_path)
    entries = manifest["files"]
    buffers = []
    for name in sorted(SCHEMA):
        try:
            content = (raw_dir / name).read_bytes()
        except OSError as exc:
            _block("missing_file", name, None, f"Arquivo indisponível ({exc})",
                   "Restaure os quatro CSVs da versão registrada")
        if verify_checksums and hashlib.sha256(content).hexdigest() != entries[name]["sha256"]:
            _block("checksum_mismatch", name, None, "SHA-256 diverge do manifesto",
                   "Restaure o arquivo original; não atualize o checksum automaticamente")
        buffers.append((name, content))
    check_marker()
    try:
        dependency_digest = hashlib.sha256((ROOT / "requirements.txt").read_bytes()).hexdigest()
    except OSError:
        _block("dependencies_missing", "requirements.txt", None,
               "Lock de dependências ausente", "Restaure requirements.txt")
    return Snapshot(tuple(buffers), _canonical(manifest), dependency_digest)


def fingerprint(snapshot, config):
    identity = {
        "files": {name: hashlib.sha256(content).hexdigest() for name, content in snapshot.files},
        "manifest": json.loads(snapshot.manifest_json),
        "config": asdict(config) if is_dataclass(config) else config,
        "dependencies": snapshot.dependency_digest,
    }
    return hashlib.sha256(_canonical(identity).encode("utf-8")).hexdigest()


def _number(value):
    try:
        parsed = float(value)
        return parsed if math.isfinite(parsed) else None
    except (ValueError, TypeError):
        return None


def _iso_date(value):
    if value is None:
        return None
    try:
        parsed = date.fromisoformat(value)
        return parsed if parsed.isoformat() == value else None
    except (ValueError, TypeError):
        return None


def _parse_table(name, content, expected_headers):
    """Parse and normalize one owned frame before checking its identity."""
    try:
        text = content.decode("utf-8-sig")
        rows = list(csv.reader(io.StringIO(text), strict=True))
        header = rows[0]
        if len(header) != len(set(header)) or any(len(row) != len(header) for row in rows[1:]):
            raise ValueError("colunas duplicadas ou quantidade de células irregular")
        if header != expected_headers:
            _block("manifest_schema_mismatch", name, None,
                   "Cabeçalhos divergem do manifesto", "Restaure o esquema registrado")
        missing = set(SCHEMA[name]) - set(header)
        if missing:
            _block("missing_columns", name, ",".join(sorted(missing)),
                   f"Colunas obrigatórias ausentes: {sorted(missing)}", "Corrija o cabeçalho")
        frame = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    except DataValidationError:
        raise
    except (UnicodeError, ValueError, csv.Error, IndexError, pd.errors.ParserError) as exc:
        _block("unreadable_csv", name, None, f"CSV inválido ({exc})", "Restaure o CSV original")
    for column in frame:
        frame[column] = frame[column].map(lambda v: v.strip() or None)
    if "product" in frame:
        frame["product"] = frame["product"].replace({"GTXPro": "GTX Pro"})
    key = KEYS[name]
    if frame[key].isna().any() or frame[key].duplicated().any():
        _block("invalid_primary_key", name, key,
               "Chave primária vazia ou duplicada após normalização",
               f"Preencha e torne {key} único")
    return frame


def _join_opportunities(tables):
    """Enrich each opportunity without dropping or multiplying identities."""
    opportunities = tables["sales_pipeline.csv"]
    count = len(opportunities)
    for name, key, indicator in (("products.csv", "product", "product_match"),
                                  ("accounts.csv", "account", "account_match"),
                                  ("sales_teams.csv", "sales_agent", "seller_match")):
        opportunities = opportunities.merge(tables[name], on=key, how="left",
                                              validate="many_to_one", indicator=indicator)
        assert len(opportunities) == count, "A junção alterou a quantidade de oportunidades"
    return opportunities


def _normalize_context(record, issue):
    """Validate portfolio/catalog support and choose the account route."""
    if record["deal_stage"] not in ACTIVE | CLOSED:
        issue("invalid_stage", "deal_stage", "Estágio desconhecido",
              "Use Prospecting, Engaging, Won ou Lost")
    for field, indicator in (("product", "product_match"), ("sales_agent", "seller_match")):
        if record[indicator] != "both":
            issue("unknown_key", field, f"{field} ausente ou sem correspondência",
                  f"Corrija {field} usando uma chave do cadastro")
    price = _number(record.get("sales_price"))
    if price is None or price <= 0:
        issue("invalid_price", "sales_price", "Preço de catálogo não é finito e positivo",
              "Corrija sales_price no catálogo para um número maior que zero")
    if pd.isna(record.get("series")):
        issue("missing_series", "series", "Série do produto ausente", "Preencha series no catálogo")
    for field in ("manager", "regional_office"):
        if pd.isna(record.get(field)):
            issue("missing_team_field", field, f"{field} ausente",
                  f"Preencha {field} no cadastro do vendedor")
    year = _number(record.get("year_established"))
    full = record["account_match"] == "both" and year is not None and year > 0 and year.is_integer()
    if not full:
        issue("account_fallback", "year_established" if record["account_match"] == "both" else "account",
              "Conta ausente, não cadastrada ou ano de fundação inválido; rota sem conta",
              "Confira account e um year_established inteiro positivo", blocking=False)
    record["year_established"] = int(year) if full else None
    record["sales_price"] = price
    record["route"] = "full" if full else "fallback"


def _normalize_dates(record, issue):
    """Keep optional active dates distinct from required closed history dates."""
    stage = record["deal_stage"]
    for field in ("engage_date", "close_date"):
        raw = record[field]
        parsed = _iso_date(raw)
        required = stage in CLOSED or (stage == "Engaging" and field == "engage_date")
        if (not pd.isna(raw) and parsed is None) or (required and parsed is None):
            issue("invalid_date", field, f"{field} ausente ou fora do formato ISO YYYY-MM-DD",
                  f"Corrija {field} para uma data válida", blocking=stage in CLOSED or field == "engage_date")
        record[field] = parsed
    if stage in CLOSED and record["close_date"] and record["engage_date"] and record["close_date"] < record["engage_date"]:
        issue("date_order", "close_date", "Fechamento anterior ao engajamento",
              "Corrija a sequência engage_date <= close_date")


def _normalize_opportunity(record, diagnostics):
    """Account for one owned row, preserving label/financial eligibility separation."""
    oid, stage = record["opportunity_id"], record["deal_stage"]
    supported = True

    def issue(code, field, reason, correction, blocking=True):
        nonlocal supported
        diagnostics.append(Diagnostic(code, "row", "sales_pipeline.csv", oid,
                                      field, reason, correction))
        if blocking:
            supported = False

    _normalize_context(record, issue)
    _normalize_dates(record, issue)
    value = _number(record["close_value"])
    financial = stage in CLOSED and value is not None and ((stage == "Won" and value >= 0) or (stage == "Lost" and value == 0))
    if stage in CLOSED and not financial:
        issue("invalid_financial_label", "close_value",
              "Valor de fechamento inválido; excluído apenas da avaliação financeira",
              "Won requer valor finito não negativo; Lost requer zero", blocking=False)
    record["close_value"] = value
    record["eligible_history"] = supported and stage in CLOSED
    record["eligible_active"] = supported and stage in ACTIVE
    record["financial_eligible"] = financial and record["eligible_history"]
    record["input_status"] = ("supported_active" if record["eligible_active"] else
                              "supported_history" if record["eligible_history"] else
                              "unsupported_active" if stage in ACTIVE else "excluded_history_or_stage")
    return record


def load_dataset(snapshot):
    manifest = json.loads(snapshot.manifest_json)
    tables = {name: _parse_table(name, content, manifest["files"][name]["headers"])
              for name, content in snapshot.files}
    if set(tables) != set(SCHEMA):
        _block("missing_file", None, None, "Snapshot incompleto", "Forneça os quatro CSVs")
    opportunities = _join_opportunities(tables)
    diagnostics = []
    normalized = [_normalize_opportunity(record, diagnostics)
                  for record in opportunities.to_dict("records")]
    frame = pd.DataFrame(normalized, columns=list(opportunities.columns) + [
        "route", "eligible_history", "eligible_active", "financial_eligible", "input_status"])
    if frame.empty or not frame["eligible_history"].any():
        diagnostics.append(Diagnostic("no_usable_history", "global", "sales_pipeline.csv", None,
                                      "deal_stage", "Nenhum histórico fechado utilizável",
                                      "Forneça oportunidades Won/Lost com chaves e datas válidas"))
        raise DataValidationError(diagnostics)
    counts = {name: len(table) for name, table in tables.items()}
    counts.update({str(status): int(n) for status, n in frame["input_status"].value_counts().items()})
    counts["financial_eligible"] = int(frame["financial_eligible"].sum())
    return Dataset(frame, tables["accounts.csv"], tables["products.csv"], tables["sales_teams.csv"],
                   tuple(diagnostics), counts, fingerprint(snapshot, {}))


class RecoveryError(ValueError):
    """An explicit operation failed; no implicit retry or checksum update."""


def _check_source(url):
    parsed = urlsplit(url)
    # Literal loopback HTTP is reserved for local integration fixtures.
    if (parsed.username or parsed.password or not parsed.hostname or
            (parsed.scheme != "https" and not
             (parsed.scheme == "http" and parsed.hostname in ("127.0.0.1", "::1")))):
        raise RecoveryError("Fonte deve usar HTTPS; HTTP é restrito ao loopback de testes")


class _SafeRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        _check_source(newurl)
        return super().redirect_request(request, fp, code, msg, headers, newurl)


def _download(url):
    _check_source(url)
    with build_opener(_SafeRedirect()).open(url, timeout=30) as response:
        _check_source(response.geturl())
        content = response.read(20 * 1024 * 1024 + 1)
    if len(content) > 20 * 1024 * 1024:
        raise RecoveryError("Download excede o limite de 20 MiB")
    return content


def _archive_content(content, name, entries):
    entry = entries[name]
    if entry["archive_member"] != name:
        raise RecoveryError("Membro ZIP deve ser o nome exato do CSV")
    allowed = {n for n, item in entries.items() if item["download_url"] == entry["download_url"]
               and item.get("archive_member") == n}
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        members = archive.infolist()
        if len(members) != len(allowed) or {item.filename for item in members} != allowed:
            raise RecoveryError("ZIP contém membros ausentes, duplicados ou não autorizados")
        for item in members:
            mode = item.external_attr >> 16
            if (item.is_dir() or stat.S_ISLNK(mode) or
                    stat.S_IFMT(mode) not in (0, stat.S_IFREG) or
                    item.file_size > 10 * 1024 * 1024 or item.flag_bits & 1):
                raise RecoveryError("ZIP contém membro inseguro ou acima de 10 MiB")
        return archive.read(name)


def _stage_files(stage, manifest):
    entries = manifest["files"]
    downloads = {}
    for name, entry in entries.items():
        url = entry["download_url"]
        if url not in downloads:
            downloads[url] = _download(url)
        content = downloads[url]
        if entry.get("archive_member") is not None:
            content = _archive_content(content, name, entries)
        if hashlib.sha256(content).hexdigest() != entry["sha256"]:
            raise RecoveryError(f"SHA-256 divergente: {name}; original preservado")
        (stage / name).write_bytes(content)


def _directory_digests(directory):
    if directory.is_symlink() or not directory.is_dir():
        raise RecoveryError(f"Diretório original indisponível ou simbólico: {directory}")
    result = {}
    for path in directory.iterdir():
        if path.name not in SCHEMA or path.is_symlink() or not path.is_file():
            raise RecoveryError(f"Conteúdo não autorizado no snapshot: {path.name}")
        result[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def _transaction_paths(parent, record):
    expected_keys = {"version", "id", "raw", "stage", "backup", "displaced", "original"}
    if (not isinstance(record, dict) or set(record) != expected_keys or
            record["version"] != 1 or not isinstance(record["id"], str) or
            not re.fullmatch(r"[0-9a-f]{32}", record["id"]) or record["raw"] != "raw"):
        raise RecoveryError("Registro de transação inválido; nenhum caminho foi alterado")
    digests = record["original"]
    if (not isinstance(digests, dict) or not set(digests) <= set(SCHEMA) or
            any(not isinstance(v, str) or not re.fullmatch(r"[0-9a-f]{64}", v)
                for v in digests.values())):
        raise RecoveryError("Digests originais inválidos no registro")
    paths = {"raw": parent / "raw"}
    for role in ("stage", "backup", "displaced"):
        if record[role] != f".recovery-{record['id']}-{role}":
            raise RecoveryError("Caminho de transação fora do escopo permitido")
        paths[role] = parent / record[role]
    if any(p.is_symlink() or (p.exists() and not p.is_dir()) for p in paths.values()):
        raise RecoveryError("Caminho de transação simbólico ou não é diretório")
    return paths


def _restore_original(paths, original):
    raw, backup, displaced = (paths[k] for k in ("raw", "backup", "displaced"))
    if backup.exists():
        if _directory_digests(backup) != original:
            raise RecoveryError("Backup original diverge dos digests; preservado para inspeção")
        if raw.exists():
            if displaced.exists():
                raise RecoveryError("Destino de rollback ocupado; nenhum original foi removido")
            raw.rename(displaced)
        backup.rename(raw)
    if _directory_digests(raw) != original:
        raise RecoveryError("Restauração não reproduziu todos os bytes originais")


def _clear_transaction(marker, paths):
    # Call only after the original or replacement has been verified.
    # Keep successful backups: a crash during cleanup must not destroy the original.
    for role in ("stage", "displaced"):
        path = paths[role]
        if path.exists():
            _directory_digests(path)
            shutil.rmtree(path)
    completed = marker.parent / (paths["backup"].name.removesuffix("-backup") + "-completed")
    if completed.exists() or completed.is_symlink():
        raise RecoveryError("Destino do registro concluído já existe")
    # One rename clears the read guard without a record-less interruption window.
    marker.rename(completed)


def _recovery_scope(manifest_path, raw_dir):
    raw, manifest_path = Path(raw_dir).absolute(), Path(manifest_path).absolute()
    parent = raw.parent.resolve(strict=True)
    if (raw.name != "raw" or raw.is_symlink() or manifest_path.is_symlink() or
            manifest_path.parent.resolve(strict=True) != parent):
        raise RecoveryError("Use raw e manifesto regulares no mesmo diretório data")
    raw, manifest_path = parent / "raw", parent / manifest_path.name
    marker = parent / ".recovery.lock"
    if marker.is_symlink():
        raise RecoveryError("Marcador simbólico rejeitado; nenhum arquivo alterado")
    return raw, manifest_path, marker


@contextmanager
def _recovery_owner(parent):
    """Keep one stable advisory-lock inode, including before marker publication."""
    owner_dir = parent / ".recovery-owner"
    if owner_dir.is_symlink():
        raise RecoveryError("Diretório de controle simbólico rejeitado")
    owner_dir.mkdir(mode=0o700, exist_ok=True)
    owner = owner_dir / "owner"
    if owner.is_symlink():
        raise RecoveryError("Arquivo de controle simbólico rejeitado")
    with owner.open("a+b") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RecoveryError("Outra recuperação ainda está executando") from exc
        yield


def _publish_transaction(raw, marker):
    identity = uuid.uuid4().hex
    record = {"version": 1, "id": identity, "raw": "raw",
              **{role: f".recovery-{identity}-{role}"
                 for role in ("stage", "backup", "displaced")},
              "original": _directory_digests(raw)}
    paths = _transaction_paths(raw.parent, record)
    if any(paths[role].exists() for role in ("stage", "backup", "displaced")):
        raise RecoveryError("Destino exclusivo já existe")
    prepared = raw.parent / f".recovery-{identity}-init"
    prepared.mkdir(mode=0o700)
    with (prepared / "transaction.json").open("x", encoding="utf-8") as transaction:
        transaction.write(_canonical(record))
        transaction.flush()
        os.fsync(transaction.fileno())
    # Publish a complete record and read guard together, never an empty marker.
    prepared.rename(marker)
    return record, paths


def _resume_recovery(raw, marker):
    if not marker.exists():
        # Interrupted private initialization cannot have changed raw.
        return {"status": "no_published_transaction", "original": _directory_digests(raw)}
    record_path = marker / "transaction.json"
    if record_path.is_symlink() or record_path.stat().st_size > 8192:
        raise RecoveryError("Registro de transação simbólico ou excede 8 KiB")
    record = json.loads(record_path.read_text(encoding="utf-8"))
    paths = _transaction_paths(raw.parent, record)
    _restore_original(paths, record["original"])
    _clear_transaction(marker, paths)
    return {"status": "original_restored", "original": record["original"]}


def _promote_snapshot(raw, manifest_path, manifest, record, paths):
    paths["stage"].mkdir()
    _stage_files(paths["stage"], manifest)
    load_dataset(_read_snapshot(paths["stage"], manifest_path, recovery=True))
    if _directory_digests(raw) != record["original"]:
        raise RecoveryError("Original mudou durante o download; substituição recusada")
    # Two guarded renames, not one atomic transaction.
    raw.rename(paths["backup"])
    paths["stage"].rename(raw)
    result = load_dataset(_read_snapshot(raw, manifest_path, recovery=True))
    return {"status": "recovered", "fingerprint": result.data_fingerprint,
            "backup": str(paths["backup"])}


def _replace_with_rollback(raw, manifest_path, marker, hint):
    manifest = _read_manifest(manifest_path)
    record, paths = _publish_transaction(raw, marker)
    try:
        result = _promote_snapshot(raw, manifest_path, manifest, record, paths)
        _clear_transaction(marker, paths)
        return result
    except Exception as exc:
        # Every ordinary failure after publication must attempt verified rollback.
        # Interruptions retain the complete record for the explicit resume command.
        try:
            _restore_original(paths, record["original"])
            _clear_transaction(marker, paths)
        except Exception as rollback:
            raise RecoveryError(f"Recuperação falhou ({exc}); rollback pendente ({rollback}). "
                                f"Backup e marcador preservados. {hint}") from exc
        raise RecoveryError(f"Recuperação recusada; bytes originais preservados: {exc}") from exc


def recover_dataset(manifest_path, raw_dir, *, resume=False):
    """Explicit verified replacement; interrupted transactions restore originals first."""
    raw, manifest_path, marker = _recovery_scope(manifest_path, raw_dir)
    hint = (f"Execute: .venv/bin/python data.py recover --resume --manifest "
            f"{str(manifest_path)!r} --raw-dir {str(raw)!r}")
    with _recovery_owner(raw.parent):
        if not resume:
            if marker.exists():
                raise RecoveryError(f"Recuperação já registrada. {hint}")
            return _replace_with_rollback(raw, manifest_path, marker, hint)
        try:
            return _resume_recovery(raw, marker)
        except (OSError, ValueError, TypeError, KeyError) as exc:
            raise RecoveryError(f"Retomada não concluída; marcador/backup preservados: {exc}. {hint}") from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description="Recuperação explícita dos quatro CSVs verificados")
    commands = parser.add_subparsers(dest="command", required=True)
    recover = commands.add_parser("recover", help="verifica todos os dados antes de substituir raw",
                                  epilog=".venv/bin/python data.py recover --manifest data/manifest.json --raw-dir data/raw")
    recover.add_argument("--manifest", type=Path, required=True)
    recover.add_argument("--raw-dir", type=Path, required=True)
    recover.add_argument("--resume", action="store_true", help="restaura primeiro o original de uma transação interrompida")
    args = parser.parse_args(argv)
    try:
        result = recover_dataset(args.manifest, args.raw_dir, resume=args.resume)
    except (RecoveryError, OSError) as exc:
        parser.exit(1, f"{exc}\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
