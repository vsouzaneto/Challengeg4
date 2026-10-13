"""Download the two Challenge 002 datasets from Kaggle into <repo>/datasets/.

Needs a Kaggle API token: kaggle.com -> Settings -> API -> "Create New Token",
saved as ~/.kaggle/kaggle.json (or KAGGLE_USERNAME / KAGGLE_KEY in the environment).

Run from the solution folder:  uv run python scripts/download_data.py
"""

import shutil
import sys
from pathlib import Path

import kagglehub

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from support_triage.paths import IT_TICKETS_DIR, TICKETS_DIR

DATASETS = {
    "suraj520/customer-support-ticket-dataset": TICKETS_DIR,
    "adisongoh/it-service-ticket-classification-dataset": IT_TICKETS_DIR,
}


def main() -> None:
    for handle, target in DATASETS.items():
        cached = Path(kagglehub.dataset_download(handle))
        target.mkdir(parents=True, exist_ok=True)
        for src in cached.rglob("*"):
            if src.is_file():
                dest = target / src.relative_to(cached)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
        files = sorted(p for p in target.rglob("*") if p.is_file())
        print(f"{handle} -> {target}")
        for f in files:
            print(f"  {f.relative_to(target)}  {f.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
