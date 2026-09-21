"""Baixa os CSVs do dataset Kaggle "CRM Sales Predictive Analytics" para data/raw/.

Uso:
    python download_data.py            # usa a API do Kaggle (precisa de ~/.kaggle/kaggle.json)
    python download_data.py --zip caminho/para/archive.zip   # usa um zip baixado manualmente

O dataset é público (CC0): https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

DATASET = "agungpambudi/crm-sales-predictive-analytics"
RAW_DIR = Path(__file__).resolve().parent / "data" / "raw"
EXPECTED = ["accounts.csv", "products.csv", "sales_teams.csv", "sales_pipeline.csv"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_zip(zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path) as z:
        names = [n for n in z.namelist() if n.lower().endswith(".csv")]
        for n in names:
            target = RAW_DIR / Path(n).name
            with z.open(n) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            print(f"extraído: {target.name}")


def download_via_api() -> None:
    cmd = [sys.executable, "-m", "kaggle", "datasets", "download", "-d", DATASET, "-p", str(RAW_DIR), "--unzip"]
    print("executando:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def report() -> int:
    missing = [f for f in EXPECTED if not (RAW_DIR / f).exists()]
    for f in EXPECTED:
        p = RAW_DIR / f
        if p.exists():
            lines = sum(1 for _ in p.open("rb")) - 1
            print(f"{f:22s} {p.stat().st_size:>9,d} bytes  {lines:>6,d} linhas  sha256={sha256(p)[:16]}…")
    if missing:
        print("FALTANDO:", ", ".join(missing))
        return 1
    print("ok: 4 arquivos presentes em", RAW_DIR)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--zip", type=Path, help="zip baixado manualmente do Kaggle")
    args = ap.parse_args()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if args.zip:
        extract_zip(args.zip)
    else:
        download_via_api()
    return report()


if __name__ == "__main__":
    raise SystemExit(main())
