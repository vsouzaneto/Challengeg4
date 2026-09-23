from __future__ import annotations

import io
import zipfile
from pathlib import Path

import deploy_app


def test_streamlit_pages_bootstrap_src_before_package_import():
    pages = Path(__file__).parents[1] / "pages"

    for page in pages.glob("*.py"):
        source = page.read_text()
        assert source.index("sys.path.insert") < source.index("from support_copilot.ui")


def test_download_csv_extracts_expected_member_atomically(tmp_path, monkeypatch):
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, "w") as archive:
        archive.writestr("nested/customer.csv", "ticket,status\n1,Open\n")
        archive.writestr("nested/ignored.csv", "ignored\n")

    monkeypatch.setattr(
        deploy_app.urllib.request,
        "urlopen",
        lambda *_args, **_kwargs: io.BytesIO(payload.getvalue()),
    )
    destination = tmp_path / "customer.csv"

    deploy_app._download_csv("https://example.test/dataset", destination)

    assert destination.read_text() == "ticket,status\n1,Open\n"
    assert not destination.with_suffix(".csv.tmp").exists()
