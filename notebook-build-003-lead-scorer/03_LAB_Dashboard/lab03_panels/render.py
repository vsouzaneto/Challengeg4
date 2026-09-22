"""Renderização no notebook Databricks (display) ou fallback local."""

from __future__ import annotations

from .common import REQUIRED_SECTIONS, DashboardPanels


def render_panels(panels: DashboardPanels, display_fn=None) -> list[str]:
    rendered = []
    for key in REQUIRED_SECTIONS:
        panel = panels.panels[key]
        if display_fn is not None:
            if panel.figure is not None:
                display_fn(panel.figure)
            display_fn(panel.frame)
        rendered.append(key)
    return rendered


def add_repo_lib_to_path() -> str:
    import sys
    from pathlib import Path

    here = Path.cwd().resolve()
    candidates = [
        here / "lib",
        here.parent / "lib",
        here.parent.parent / "lib",
        here.parent.parent.parent / "lib",
        Path(__file__).resolve().parents[1],
    ]
    for candidate in candidates:
        package = candidate / "lab03_panels"
        if package.is_dir() and (package / "__init__.py").exists():
            path = str(candidate)
            if path not in sys.path:
                sys.path.insert(0, path)
            return path
    raise FileNotFoundError("lib/lab03_panels não encontrado a partir de " + str(here))
