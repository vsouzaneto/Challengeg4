"""Acquire and verify the immutable RavenStack Kaggle v1 source files."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class DataContractError(RuntimeError):
    """Raised when the downloaded/local source differs from the pinned manifest."""


@dataclass(frozen=True)
class VerifiedFile:
    name: str
    path: Path
    bytes: int
    rows: int
    sha256: str


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        manifest = json.load(handle)
    required = {"manifest_version", "source", "files"}
    missing = required.difference(manifest)
    if missing:
        raise DataContractError(f"Manifesto incompleto: {sorted(missing)}")
    return manifest


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _csv_rows(path: Path) -> int:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        try:
            next(reader)
        except StopIteration as exc:
            raise DataContractError(f"CSV vazio: {path.name}") from exc
        return sum(1 for _ in reader)


def inspect_file(path: Path) -> VerifiedFile:
    return VerifiedFile(
        name=path.name,
        path=path,
        bytes=path.stat().st_size,
        rows=_csv_rows(path),
        sha256=_sha256(path),
    )


def verify_directory(directory: Path, manifest: dict[str, Any]) -> list[VerifiedFile]:
    verified: list[VerifiedFile] = []
    problems: list[str] = []
    for spec in manifest["files"]:
        path = directory / spec["name"]
        if not path.is_file():
            problems.append(f"arquivo ausente: {spec['name']}")
            continue
        observed = inspect_file(path)
        for field in ("bytes", "rows", "sha256"):
            if getattr(observed, field) != spec[field]:
                problems.append(
                    f"{spec['name']} {field}: esperado={spec[field]!r}, "
                    f"observado={getattr(observed, field)!r}"
                )
        verified.append(observed)
    if problems:
        raise DataContractError("Falha no contrato dos dados:\n- " + "\n- ".join(problems))
    return verified


def _locate_downloaded_file(root: Path, name: str) -> Path:
    matches = [path for path in root.rglob(name) if path.is_file()]
    if len(matches) != 1:
        raise DataContractError(
            f"Esperado exatamente um {name} no download; encontrados {len(matches)}."
        )
    return matches[0]


def _copy_manifest_files(source: Path, destination: Path, manifest: dict[str, Any]) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for spec in manifest["files"]:
        source_file = _locate_downloaded_file(source, spec["name"])
        target = destination / spec["name"]
        temporary = target.with_suffix(target.suffix + ".partial")
        shutil.copyfile(source_file, temporary)
        os.replace(temporary, target)


def ensure_raw_data(
    *,
    raw_dir: Path,
    manifest_path: Path,
    source_dir: Path | None = None,
    force_download: bool = False,
) -> tuple[dict[str, Any], list[VerifiedFile]]:
    """Populate ``raw_dir`` from an override or pinned Kaggle v1, then verify it.

    Existing verified raw files are reused. A local override is copied byte-for-byte.
    Kaggle is contacted only when the raw directory is absent/invalid and no override
    was supplied.
    """

    manifest = load_manifest(manifest_path)

    if source_dir is not None:
        source_dir = source_dir.expanduser().resolve()
        if not source_dir.is_dir():
            raise DataContractError(f"Diretório local inexistente: {source_dir}")
        verify_directory(source_dir, manifest)
        if source_dir != raw_dir.expanduser().resolve():
            _copy_manifest_files(source_dir, raw_dir, manifest)
        return manifest, verify_directory(raw_dir, manifest)

    try:
        return manifest, verify_directory(raw_dir, manifest)
    except DataContractError:
        if raw_dir.exists() and not force_download:
            raise DataContractError(
                "Os arquivos raw existem, mas falharam no manifesto. "
                "Remova a cópia local inválida ou rode com --force-download."
            )

    try:
        import kagglehub
    except ImportError as exc:
        raise DataContractError(
            "kagglehub não instalado. Instale requirements.txt ou use --source-dir."
        ) from exc

    handle = manifest["source"]["download_handle"]
    with tempfile.TemporaryDirectory(prefix="ravenstack-kaggle-v1-") as temp:
        download_root = Path(temp)
        try:
            downloaded = Path(
                kagglehub.dataset_download(
                    handle,
                    output_dir=str(download_root),
                    force_download=force_download,
                )
            )
        except Exception as exc:  # network/auth errors vary across kagglehub versions
            raise DataContractError(
                f"Falha ao baixar {handle}. Use --source-dir como alternativa: {exc}"
            ) from exc
        verify_directory(downloaded, manifest)
        _copy_manifest_files(downloaded, raw_dir, manifest)

    return manifest, verify_directory(raw_dir, manifest)

