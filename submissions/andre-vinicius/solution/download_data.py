"""Baixa os CSVs públicos indicados no case, mantendo-os fora do Git."""
import hashlib
import io
import urllib.request
import zipfile
from pathlib import Path


URL = "https://www.kaggle.com/api/v1/datasets/download/agungpambudi/crm-sales-predictive-analytics"
EXPECTED_SHA256 = "74d535826330b616758ebb6bb393abf701a5126364a72fbe71003cb6a7a87a9c"
EXPECTED = {"accounts.csv", "products.csv", "sales_teams.csv", "sales_pipeline.csv", "metadata.csv"}
DEST = Path(__file__).parent / "data"


def main():
    DEST.mkdir(exist_ok=True)
    request = urllib.request.Request(URL, headers={"User-Agent": "G4-case-003-reproducibility/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        archive_bytes = response.read()
    digest = hashlib.sha256(archive_bytes).hexdigest()
    if digest != EXPECTED_SHA256:
        print("Aviso: o ZIP mudou desde a auditoria; confira a fonte antes de usar os resultados publicados.")
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        names = {Path(name).name: name for name in archive.namelist() if Path(name).suffix.lower() == ".csv"}
        missing = EXPECTED - names.keys()
        if missing:
            raise RuntimeError(f"Dataset incompleto: {', '.join(sorted(missing))}")
        for filename in sorted(EXPECTED):
            (DEST / filename).write_bytes(archive.read(names[filename]))
    print(f"CSV salvos em {DEST} (ignorado pelo Git). SHA-256 do ZIP: {digest}")


if __name__ == "__main__":
    main()
