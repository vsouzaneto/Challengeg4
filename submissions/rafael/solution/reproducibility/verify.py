"""Reproducibility check: same interpreter, pinned libraries, same CSV, trained models present and results equal to the reference.

Usage (from submissions/rafael):
  python solution/reproducibility/verify.py                    # fast: versions, data, cached models vs. reference
  python solution/reproducibility/verify.py --retrain --tests  # full: retrain from scratch in a temp dir + pytest
  python solution/reproducibility/verify.py --write-reference  # record the current results as the reference
"""
import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
import tempfile
from importlib import metadata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "solution" / "src"))

PYTHON = (3, 14)
REQUIREMENTS = ROOT / "requirements.txt"   # direct dependencies
LOCK = ROOT / "requirements.lock"           # every package of the tested environment
DATA_SCRIPT = ROOT / "solution" / "scripts" / "get_data.sh"
CSV = ROOT / "data" / "raw" / "social_media_dataset.csv"
REFERENCE = HERE / "reference.json"
VOLATILE = {("meta", "gerado_em")}   # build timestamp: the only payload field allowed to change
REL_TOL, ABS_TOL = 1e-6, 1e-9
MAX_DIFFS = 10
PROBES = [  # planned posts sent to the simulator, as the API receives them
    {},
    {"platform": "YouTube", "content_type": "image", "hour": 8, "is_sponsored": True, "sponsor_category": "electronics",
     "disclosure_type": "implicit", "disclosure_location": "caption"},
    {"platform": "Instagram", "language": "English", "audience_location": "Russia", "follower_count": 1_000_000, "objetivo": "views"},
    {"platform": "TikTok", "content_category": "tech", "language": "Hindi", "content_type": "text", "objetivo": "comments_count"},
]


def check_python() -> tuple[bool, str]:
    ok = sys.version_info[:2] == PYTHON
    return ok, f"Python {sys.version.split()[0]} (esperado {'.'.join(map(str, PYTHON))}.x)"


def read_pins(path: Path) -> dict[str, str]:
    """`name==version` lines → {normalized name: version} (comments ignored)."""
    pins = [line.split("==") for line in path.read_text().splitlines() if "==" in line and not line.startswith("#")]
    return {re.sub(r"[-_.]+", "-", name).lower(): version for name, version in pins}


def check_libraries() -> tuple[bool, str]:
    lock = read_pins(LOCK)
    wrong = [f"{name} {version} em requirements.txt, {lock.get(name, 'ausente')} no lock"
             for name, version in read_pins(REQUIREMENTS).items() if lock.get(name) != version]
    pins = lock.items()
    for name, pinned in pins:
        try:
            installed = metadata.version(name)
        except metadata.PackageNotFoundError:
            installed = "ausente"
        if installed != pinned:
            wrong.append(f"{name} {installed} (fixado {pinned})")
    return not wrong, f"{len(pins)} pacotes do lock na versão exata" + (f"; divergências: {'; '.join(wrong[:MAX_DIFFS])}" if wrong else "")


def check_data() -> tuple[bool, str]:
    expected = re.search(r'SHA256="([0-9a-f]{64})"', DATA_SCRIPT.read_text()).group(1)
    if not CSV.exists():
        return False, f"{CSV.relative_to(ROOT)} não existe (rode solution/scripts/get_data.sh)"
    actual = hashlib.sha256(CSV.read_bytes()).hexdigest()
    return actual == expected, f"sha256 do CSV {'confere' if actual == expected else 'DIFERENTE: ' + actual}"


def fingerprint(state) -> dict:
    """Everything the site shows (payload) plus the simulator's answer for fixed planned posts."""
    from social_web.schemas import PostInput
    predictions = []
    for probe in PROBES:
        post = PostInput(**probe).model_dump()
        predictions.append(state.predictor.predict(post, goal=post.pop("objetivo")))
    from social_insights.site_export import _clean
    return json.loads(json.dumps(_clean({"payload": state.payload, "previsoes": predictions}), ensure_ascii=False))


def differences(expected, actual, path=()) -> list[str]:
    """Recursive comparison: numbers within tolerance, everything else exactly."""
    if path[1:] in VOLATILE:
        return []
    where = "/".join(map(str, path)) or "raiz"
    if isinstance(expected, dict) and isinstance(actual, dict):
        if expected.keys() != actual.keys():
            return [f"{where}: chaves diferentes ({sorted(set(expected) ^ set(actual))[:5]})"]
        return [d for k in expected for d in differences(expected[k], actual[k], path + (k,))]
    if isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            return [f"{where}: {len(expected)} itens na referência, {len(actual)} agora"]
        return [d for i, (e, a) in enumerate(zip(expected, actual)) for d in differences(e, a, path + (i,))]
    numbers = all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (expected, actual))
    if numbers and math.isclose(expected, actual, rel_tol=REL_TOL, abs_tol=ABS_TOL):
        return []
    return [] if expected == actual else [f"{where}: referência {expected!r}, agora {actual!r}"]


def compare(current: dict, label: str) -> tuple[bool, str]:
    if not REFERENCE.exists():
        return False, f"{REFERENCE.relative_to(ROOT)} não existe (rode com --write-reference)"
    diffs = differences(json.loads(REFERENCE.read_text(encoding="utf-8")), current)
    detail = "".join(f"\n      {d[:220]}" for d in diffs[:MAX_DIFFS]) + (f"\n      … e mais {len(diffs) - MAX_DIFFS}" if len(diffs) > MAX_DIFFS else "")
    return not diffs, f"{label}: {'idêntico à referência' if not diffs else f'{len(diffs)} diferenças'}{detail}"


def run_tests() -> tuple[bool, str]:
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "solution/tests"], cwd=ROOT, capture_output=True, text=True)
    summary = (result.stdout.strip().splitlines() or ["sem saída"])[-1]
    return result.returncode == 0, f"pytest: {summary}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--retrain", action="store_true", help="retreina tudo do zero numa pasta temporária e compara com a referência")
    parser.add_argument("--tests", action="store_true", help="roda também a suíte de testes")
    parser.add_argument("--write-reference", action="store_true", help="grava os resultados atuais como referência")
    args = parser.parse_args()

    from social_web.state import CACHE_DIR, load_state
    checks = [("Interpretador", check_python()), ("Bibliotecas", check_libraries()), ("Dados", check_data())]
    if not checks[-1][1][0]:
        return report(checks)

    models_ok = (CACHE_DIR / "web_models.joblib").exists() and (CACHE_DIR / "site_payload.json").exists()
    checks.append(("Modelos treinados", (models_ok, f"{CACHE_DIR.relative_to(ROOT)}: " + ("presentes" if models_ok else "ausentes (rode social-web --build-only)"))))
    if models_ok:
        current = fingerprint(load_state())
        if args.write_reference:
            REFERENCE.parent.mkdir(exist_ok=True)
            REFERENCE.write_text(json.dumps(current, ensure_ascii=False, sort_keys=True, indent=1), encoding="utf-8")
            print(f"Referência gravada em {REFERENCE.relative_to(ROOT)}")
        checks.append(("Resultados (modelos em cache)", compare(current, "payload + simulador")))
    if args.retrain:
        with tempfile.TemporaryDirectory() as tmp:
            print("Retreinando do zero (~5 min)…", flush=True)
            checks.append(("Resultados (retreino do zero)", compare(fingerprint(load_state(rebuild=True, cache_dir=Path(tmp))), "payload + simulador")))
    if args.tests:
        checks.append(("Testes", run_tests()))
    return report(checks)


def report(checks: list) -> int:
    print("\nChecagem de reprodutibilidade")
    for name, (ok, detail) in checks:
        print(f"  [{'OK' if ok else 'FALHA'}] {name}: {detail}")
    failed = [name for name, (ok, _) in checks if not ok]
    print("\nResultado: " + ("reproduzível." if not failed else f"falhou em {', '.join(failed)}."))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
