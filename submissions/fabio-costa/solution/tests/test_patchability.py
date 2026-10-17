from __future__ import annotations

from collections import Counter
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


# -----------------------------------------------------------------------------
# CSS GOVERNANCE
# -----------------------------------------------------------------------------

def test_css_has_no_important_or_version_patch_blocks():
    for path in sorted((ROOT / "static" / "css").glob("*.css")):
        css = path.read_text(encoding="utf-8")

        assert "!important" not in css, (
            f"{path}: !important is prohibited"
        )

        assert re.search(
            r"/\*\s*v\d+\.\d+",
            css,
            flags=re.IGNORECASE,
        ) is None, (
            f"{path}: version-based patch block detected"
        )


def test_css_custom_properties_are_defined():
    for path in sorted((ROOT / "static" / "css").glob("*.css")):
        css = path.read_text(encoding="utf-8")

        definitions = set(
            re.findall(r"--([A-Za-z0-9_-]+)\s*:", css)
        )

        usages = set(
            re.findall(r"var\(\s*--([A-Za-z0-9_-]+)", css)
        )

        undefined = sorted(usages - definitions)

        assert not undefined, (
            f"{path}: undefined CSS custom properties: {undefined}"
        )


# -----------------------------------------------------------------------------
# HTML GOVERNANCE
# -----------------------------------------------------------------------------

def test_html_ids_are_unique_per_template():
    for path in sorted((ROOT / "templates").glob("*.html")):
        html = path.read_text(encoding="utf-8")

        ids = re.findall(r'\bid="([^"]+)"', html)

        duplicates = sorted(
            item
            for item, count in Counter(ids).items()
            if count > 1
        )

        assert not duplicates, (
            f"{path}: duplicate HTML ids: {duplicates}"
        )


# -----------------------------------------------------------------------------
# DATASET ARCHITECTURE CONTRACT
# -----------------------------------------------------------------------------

def test_obsolete_cross_dataset_contracts_are_absent():
    explorer = (
        ROOT / "src" / "dataset_explorer.py"
    ).read_text(encoding="utf-8")

    dataset2 = (
        ROOT / "src" / "dataset2_diagnostics.py"
    ).read_text(encoding="utf-8")

    assert '"cross_dataset":' not in explorer
    assert '"cross_dataset_gate":' not in dataset2
