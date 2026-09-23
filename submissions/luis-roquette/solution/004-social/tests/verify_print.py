"""Actual Chrome/A4 regression, separate from the portable unit-test suite.

Usage: python tests/verify_print.py /path/to/canonical-summary.html [NEW_OUTPUT_DIR]
Requires Chrome, pdfinfo, pdftotext and pdftoppm; no downloads or paid services.
"""
from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis import _atomic_write, executive_summary
from tests.test_reconstruction import adversarial_decisions, long_label_result


def verify(canonical_html: Path, output: Path) -> None:
    chrome = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    if not chrome.is_file():
        chrome = Path(shutil.which("chromium") or shutil.which("google-chrome") or "missing-chrome")
    if not chrome.is_file():
        raise RuntimeError("Chrome/Chromium is required for the actual print gate")
    for command in ("pdfinfo", "pdftotext", "pdftoppm"):
        if not shutil.which(command):
            raise RuntimeError(f"{command} is required for the actual print gate")
    output.mkdir(parents=True, exist_ok=False)
    label, result = long_label_result()
    result["scope"].update(period_mode="Mês calendário", requested_start="2025-01-01T00:00:00",
                           requested_end="2025-01-31T00:00:00", partial_period=True)
    payloads = {
        "normal": canonical_html.read_bytes(),
        "adversarial": executive_summary(result, adversarial_decisions(result["source"]["source_hash"])).encode(),
    }
    for name, payload in payloads.items():
        page, pdf = output / f"{name}.html", output / f"{name}.pdf"
        _atomic_write(page, payload)
        with tempfile.TemporaryDirectory(prefix="ai-master-a4-profile-") as profile:
            try:
                process = subprocess.run([
                    str(chrome), "--headless", "--disable-gpu", "--no-first-run", "--disable-extensions",
                    "--no-default-browser-check", "--no-pdf-header-footer", f"--user-data-dir={profile}",
                    f"--print-to-pdf={pdf}", page.resolve().as_uri(),
                ], capture_output=True, timeout=15)
                print(name, "chrome_exit", process.returncode)
            except subprocess.TimeoutExpired:
                # Chrome can remain alive after printing. Timeout is reported;
                # the independently parsed NEW artifact, not process exit, is the gate.
                print(name, "chrome_exit=timeout; isolated process terminated after 15s")
        info = subprocess.run(["pdfinfo", str(pdf)], check=True, capture_output=True, text=True).stdout
        assert re.search(r"Pages:\s+1\s", info), info
        assert "(A4)" in info, info
        content = subprocess.run(["pdftotext", str(pdf), "-"], check=True, capture_output=True, text=True).stdout
        for required in ("Resumo executivo social", "Prioridades", "Limite:", "sem investimento", "causalidade"):
            assert required in content, (name, required)
        if name == "adversarial":
            for required in ("REVISÃO RECENTE", "SUPERADA", "outras fontes", "Plataforma", "…",
                             "Mês calendário", "2025-01-31T00:00:00", "cobertura temporal parcial"):
                assert required in content, required
            assert label not in content
            assert "P" * 700 not in content
        subprocess.run(["pdftoppm", "-scale-to", "1600", "-png", "-singlefile", str(pdf), str(output / name)], check=True)
        print(name, "pages=1 A4; essential limitations present", hashlib.sha256(pdf.read_bytes()).hexdigest())
    print("Inspect PNGs for clipping:", output)


if __name__ == "__main__":
    destination = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(tempfile.gettempdir()) / f"ai-master-a4-{uuid.uuid4().hex}"
    verify(Path(sys.argv[1]), destination)
