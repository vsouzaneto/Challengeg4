"""Gera a demo estática do Lead Kanban: a interface e os dados prontos, sem servidor Python.

    python build_static.py --out dist

Copia web/ para a pasta de saída e grava em data/board.json o mesmo payload que o
servidor entrega em /api/board. O resultado roda em qualquer hospedagem de arquivos
estáticos (a demo pública usa o GitHub Pages) e não precisa de dependências.
"""

from __future__ import annotations

from pathlib import Path
import argparse
import json
import shutil

from server import WEB_DIR, board_payload


def build(out: Path) -> Path:
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(WEB_DIR, out)
    # Marca a página como estática: os dados vêm direto de data/board.json, sem tentar /api/board.
    index = out / "index.html"
    html = index.read_text(encoding="utf-8")
    index.write_text(html.replace("<head>", '<head>\n  <meta name="lead-kanban-static" content="1">', 1), encoding="utf-8")
    (out / "data").mkdir(exist_ok=True)
    target = out / "data" / "board.json"
    target.write_text(json.dumps(board_payload(), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")  # GitHub Pages: servir os arquivos como estão
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo estática do Lead Kanban")
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "dist")
    args = parser.parse_args()
    target = build(args.out)
    print(f"Demo estática em {args.out} · dados: {target.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
