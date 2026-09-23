"""Streamlit Community Cloud entrypoint.

The challenge app stays offline during normal use. This wrapper performs the
one-time public-data bootstrap required by an ephemeral cloud checkout.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
ARTIFACTS = ROOT / "artifacts"
SOURCES = (
    (
        "https://www.kaggle.com/api/v1/datasets/download/"
        "suraj520/customer-support-ticket-dataset",
        ROOT / "data/raw/customer_support_tickets.csv",
    ),
    (
        "https://www.kaggle.com/api/v1/datasets/download/"
        "adisongoh/it-service-ticket-classification-dataset",
        ROOT / "data/raw/all_tickets_processed_improved_v3.csv",
    ),
)


def _download_csv(url: str, destination: Path) -> None:
    """Download a public Kaggle ZIP and atomically publish its expected CSV."""
    if destination.is_file() and destination.stat().st_size:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "support-copilot/1.0"})
    with tempfile.TemporaryDirectory(prefix="support-copilot-") as temporary:
        archive_path = Path(temporary) / "dataset.zip"
        with urllib.request.urlopen(request, timeout=120) as response:  # noqa: S310
            archive_path.write_bytes(response.read())
        with zipfile.ZipFile(archive_path) as archive:
            matches = [name for name in archive.namelist() if Path(name).name == destination.name]
            if len(matches) != 1:
                raise RuntimeError(f"CSV esperado ausente no ZIP: {destination.name}")
            staged = destination.with_suffix(f"{destination.suffix}.tmp")
            with archive.open(matches[0]) as source, staged.open("wb") as target:
                shutil.copyfileobj(source, target)
            if not staged.stat().st_size:
                raise RuntimeError(f"CSV extraído vazio: {destination.name}")
            staged.replace(destination)


def _run(*arguments: str) -> None:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(SRC)
    subprocess.run(  # noqa: S603
        [sys.executable, *arguments],
        cwd=ROOT,
        env=environment,
        check=True,
        timeout=600,
    )


def _artifacts_ready() -> bool:
    if not (ARTIFACTS / "manifest.json").is_file():
        return False
    sys.path.insert(0, str(SRC))
    from support_copilot.ui import load_artifacts

    return load_artifacts(ARTIFACTS).get("queue.customer").status == "ready"


@st.cache_resource(show_spinner=False)
def bootstrap() -> None:
    """Prepare verified artifacts once per Streamlit server lifecycle."""
    if _artifacts_ready():
        return
    if ARTIFACTS.exists():
        shutil.rmtree(ARTIFACTS)
    for url, destination in SOURCES:
        _download_csv(url, destination)
    customer, it = (str(destination) for _, destination in SOURCES)
    reproduce = [
        "scripts/reproduce.py",
        "--customer",
        customer,
        "--it",
        it,
        "--output",
        str(ARTIFACTS),
    ]
    _run(*reproduce)
    _run(
        "-m",
        "support_copilot.retrieval",
        "prepare-review",
        "--artifacts",
        str(ARTIFACTS),
        "--split",
        "calibration",
    )
    _run(
        "-m",
        "support_copilot.retrieval",
        "lock-review",
        "--artifacts",
        str(ARTIFACTS),
        "--split",
        "calibration",
        "--decision",
        "disabled",
    )
    _run(*reproduce)
    if not _artifacts_ready():
        raise RuntimeError("Bootstrap concluído sem liberar a fila em modo seguro.")


def main() -> None:
    bootstrap()
    os.chdir(ROOT)
    sys.path.insert(0, str(SRC))
    from app import main as run_app

    run_app()


if __name__ == "__main__":
    main()
