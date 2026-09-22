"""Checagem antes do PR: todo caminho citado nos Markdown existe, e nada necessário ficou de fora do git.

O .gitignore da raiz do repositório ignora submissions/ inteiro (herdado do upstream), então
arquivos novos só entram com `git add -f`. Este script lista o que está citado mas não existe,
o que existe mas não está versionado, e o que está versionado mas não deveria.

Uso:  python 05_check_repo.py   (dentro de solution/; precisa de git)
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

SUB = Path(__file__).resolve().parents[1]
REPO = SUB.parents[1]
REL = SUB.relative_to(REPO).as_posix()
IGNORE_OK = re.compile(r"(data/raw/(?!README\.md)|__pycache__|\.pytest_cache|\.venv|node_modules|\.streamlit/secrets)")
CITED = re.compile(r"`([^`\n]+?\.(?:md|py|json|txt|toml|ps1|png|csv))`")


def git(*args: str) -> list[str]:
    out = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, encoding="utf-8")
    return [l for l in out.stdout.splitlines() if l.strip()]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    problems = 0
    tracked = set(git("ls-files", REL))
    ignored = [p for p in git("ls-files", "--others", "--ignored", "--exclude-standard", REL) if not IGNORE_OK.search(p)]
    untracked = [p for p in git("ls-files", "--others", "--exclude-standard", REL) if not IGNORE_OK.search(p)]
    bad_tracked = [p for p in tracked if IGNORE_OK.search(p)]
    outside = [l for l in git("diff", "--stat", "--name-only", "upstream/main...HEAD") if not l.startswith(REL + "/")]

    print(f"versionados na submissão: {len(tracked)}")
    for label, items in (("citados e inexistentes", []), ("existem mas não estão no git (precisam de git add -f)", ignored + untracked),
                         ("versionados indevidamente", bad_tracked), ("alterados fora da pasta da submissão", outside)):
        if label.startswith("citados"):
            continue
        if items:
            problems += len(items); print(f"\n{label}:"); [print("  -", p) for p in items]
    # Baselines são saídas brutas de IA e citam arquivos que não existem por natureza; ficam fora.
    checked = [p for p in SUB.rglob("*.md") if "baselines" not in p.parts and "chat-exports" not in p.parts and "design-panel" not in p.name and "g4-research-sources" not in p.name]
    missing = []
    for mdfile in checked:
        text = mdfile.read_text(encoding="utf-8", errors="ignore")
        for cited in set(CITED.findall(text)):
            if " " in cited or "*" in cited or cited.startswith(("http", "../")) or cited.endswith(".csv"):
                continue
            cand = [mdfile.parent / cited, SUB / cited, SUB / "solution" / cited, SUB / "solution" / "leadscorer" / cited, SUB / "docs" / cited, SUB / "process-log" / cited]
            if not any(c.exists() for c in cand):
                missing.append(f"{mdfile.relative_to(SUB).as_posix()} -> {cited}")
    if missing:
        problems += len(missing); print("\ncitados em Markdown e inexistentes:"); [print("  -", m) for m in sorted(set(missing))]
    for placeholder in ("[[", "a preencher", "TODO"):
        hits = [str(p.relative_to(SUB)) for p in checked if placeholder in p.read_text(encoding="utf-8", errors="ignore") and p.name != "design-system.md"]
        if hits:
            problems += len(hits); print(f"\nmarcador '{placeholder}' sobrando em:"); [print("  -", h) for h in hits]
    print("\nok: nada pendente" if problems == 0 else f"\n{problems} pendências")
    return 0 if problems == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
