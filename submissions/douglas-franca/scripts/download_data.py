"""Baixa o dataset do Challenge 004 (Kaggle, licença MIT) para data/raw/.

Não exige login no Kaggle. Uso: uv run python scripts/download_data.py
"""

import shutil
from pathlib import Path

import kagglehub

DATASET = "omenkj/social-media-sponsorship-and-engagement-dataset"
RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def main() -> None:
    source = Path(kagglehub.dataset_download(DATASET))
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for csv in source.glob("*.csv"):
        target = RAW_DIR / csv.name
        shutil.copy2(csv, target)
        print(f"{target} ({target.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
