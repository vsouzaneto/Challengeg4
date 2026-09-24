#!/usr/bin/env python3
"""PreToolUse (Edit|Write|MultiEdit|NotebookEdit): enforce G4 file-scope rules.

- Deny edits outside the submission folder (PR rule: only submissions/bernardo-couto/).
- Deny edits to raw data (immutable, checksummed).
- Deny writing secret-looking files.
"""
from pathlib import Path

from _common import deny, is_inside, project_dir, read_payload

payload = read_payload()
tool_input = payload.get("tool_input") or {}
raw = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
if not raw:
    raise SystemExit(0)

root = project_dir()
target = Path(raw)
if not target.is_absolute():
    target = Path(payload.get("cwd") or root) / target
target = target.resolve()

if not is_inside(target, root):
    deny(
        f"Bloqueado: '{target}' está fora de '{root}'. Regra do G4: o PR só pode alterar "
        "arquivos dentro de submissions/bernardo-couto/. Se precisar de algo fora "
        "(ex.: .gitignore da raiz), documente a limitação em vez de editar."
    )

raw_dir = (root / "solution" / "data" / "raw").resolve()
if is_inside(target, raw_dir):
    deny(
        "Bloqueado: solution/data/raw/ é imutável (verificado por SHA256SUMS). "
        "Corrija dados em código (solution/pipeline/src/lead_scorer/data/clean.py), não no CSV."
    )

name = target.name.lower()
if name in {".env", ".env.local", "kaggle.json", "credentials.json"} or name.startswith(".env."):
    deny(f"Bloqueado: '{name}' parece conter segredos e não pode ser criado/commitado neste projeto.")

raise SystemExit(0)
