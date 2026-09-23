import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_build_backend_is_exactly_locked_and_reused() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    build_requirements = project["build-system"]["requires"]
    lock = (ROOT / "requirements.lock").read_text().splitlines()
    makefile = (ROOT / "Makefile").read_text()

    assert build_requirements == ["setuptools==84.0.0"]
    assert lock.count(build_requirements[0]) == 1
    assert "pip install --no-build-isolation --no-deps -e ." in makefile
    assert "pip install --no-build-isolation -e '.[dev]'" in makefile


def test_manual_data_fallback_requires_zip_extraction_to_exact_paths() -> None:
    makefile = (ROOT / "Makefile").read_text()

    assert "extraia customer_support_tickets.csv e mova para $(CUSTOMER_CSV)" in makefile
    assert (
        "extraia all_tickets_processed_improved_v3.csv e mova para $(IT_CSV)" in makefile
    )
