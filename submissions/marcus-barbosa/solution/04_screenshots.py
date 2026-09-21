"""Capturas de tela reproduzíveis do app, com Playwright (Chromium headless).

Uso:
    streamlit run app.py --server.port 8511 --server.headless true   (em outro terminal)
    python 04_screenshots.py [--base http://localhost:8511]
Escreve PNGs em ../process-log/screenshots/app/.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "process-log" / "screenshots" / "app"
VIEWS = [
    ("01-vendedor-brief", "?papel=Vendedor&vendedor=Vicki%20Laflamme"),
    ("02-vendedor-pipeline-darcel", "?papel=Vendedor&vendedor=Darcel%20Schlecht"),
    ("03-gerente-central", "?papel=Gerente&regiao=Central"),
    ("04-revops", "?papel=RevOps"),
    ("05-revops-30-setembro", "?papel=RevOps&data=2017-09-30"),
    ("06-vendedor-30-junho", "?papel=Vendedor&vendedor=Vicki%20Laflamme&data=2017-06-30"),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8511")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        for name, query in VIEWS:
            page.goto(args.base + "/" + query, wait_until="networkidle")
            time.sleep(4)  # Streamlit termina de renderizar depois do networkidle
            page.wait_for_selector("text=Lead Scorer", timeout=30000)
            page.screenshot(path=str(OUT / f"{name}.png"), full_page=True)
            print("ok", name)
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
