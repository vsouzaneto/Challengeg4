"""Captura um print de cada aba do Decision Gate para o README.

Pré-requisito: app rodando em http://localhost:8501 (uv run streamlit run app/streamlit_app.py).
Uso: uv run --with playwright==1.57.0 python scripts/capture_app.py
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "http://localhost:8501"
OUT = Path(__file__).resolve().parents[1] / "outputs" / "figures" / "app"
TABS = [
    ("1 · Os dados servem?", "g6-app-1-gate0.png", None),
    ("2 · Painel com margem de erro", "g6-app-2-painel.png", None),
    ("3 · Aprovar patrocínio", "g6-app-3-contrato.png", "Checar contrato"),
    ("4 · Fechar ciclo de 30 dias", "g6-app-4-fechamento.png", None),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1100}, color_scheme="light")
        page.goto(URL)
        page.get_by_text("Decision Gate · Social Media").first.wait_for(timeout=60_000)
        page.wait_for_timeout(2_000)
        for tab, filename, button in TABS:
            page.get_by_role("tab", name=tab).click()
            page.wait_for_timeout(2_500)
            if button:
                page.get_by_role("button", name=button).click()
                page.wait_for_timeout(2_500)
            page.screenshot(path=OUT / filename, full_page=True)
            print(OUT / filename)
        browser.close()


if __name__ == "__main__":
    main()
