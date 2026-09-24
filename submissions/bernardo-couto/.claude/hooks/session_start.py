#!/usr/bin/env python3
"""SessionStart: inject project status into context (branch, data integrity, tests, last decisions)."""
import hashlib
import subprocess
from pathlib import Path

from _common import project_dir, read_payload

read_payload()
root = project_dir()
lines = ["[Lead Scorer — status da sessão]"]

def run(cmd, cwd=None, timeout=60):
    try:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout).stdout.strip()
    except Exception as exc:  # noqa: BLE001
        return f"(erro: {exc})"

repo = root.parents[1]
branch = run(["git", "branch", "--show-current"], cwd=repo)
lines.append(f"- Branch: {branch or '(desconhecida)'}" + ("" if branch == "submission/bernardo-couto" else "  ⚠ esperado: submission/bernardo-couto"))
outside = run(["git", "status", "--short"], cwd=repo)
dirty_outside = [l for l in outside.splitlines() if l[3:] and not l[3:].startswith("submissions/bernardo-couto")]
if dirty_outside:
    lines.append(f"- ⚠ Alterações fora da pasta de submissão: {len(dirty_outside)} (PR seria rejeitado)")

raw = root / "solution" / "data" / "raw"
sums = raw / "SHA256SUMS"
if sums.exists():
    bad = []
    for entry in sums.read_text().splitlines():
        digest, _, name = entry.partition("  ")
        f = raw / name.strip()
        if not f.exists() or hashlib.sha256(f.read_bytes()).hexdigest() != digest:
            bad.append(name.strip())
    lines.append("- Dados raw: íntegros (SHA256 ok)" if not bad else f"- ⚠ Dados raw alterados/ausentes: {bad}")
else:
    lines.append("- ⚠ solution/data/raw/SHA256SUMS ausente")

lines.append("- Snapshot dos dados: 2017-12-31 (nunca usar today()/current_date()).")
jh = run(["/usr/libexec/java_home", "-v", "21"]) or run(["/usr/libexec/java_home", "-v", "17"])
default_java = run(["/usr/libexec/java_home"])
if jh and not jh.startswith("(erro"):
    dflt_name = default_java.split("/JavaVirtualMachines/")[-1].split("/")[0] if "/JavaVirtualMachines/" in default_java else default_java
    warn = "" if default_java == jh else f"  ⚠ JDK padrão do sistema é {dflt_name}; Spark 3.5 exige 17/21 → exportar JAVA_HOME={jh}"
    lines.append(f"- JDK para Spark: {jh}{warn}")
else:
    lines.append("- ⚠ Nenhum JDK 17/21 encontrado: PySpark não vai subir. Instale Corretto/Temurin 21.")
models = root / "solution" / "models" / "latest"
lines.append(f"- Modelo: {models.read_text().strip() if models.exists() else 'nenhum treinado ainda'}")
gold = root / "solution" / "data" / "gold" / "scores"
lines.append(f"- gold/scores: {'existe' if gold.exists() and any(gold.iterdir()) else 'ainda não gerado (jobs build_features → train → score)'}")

present = [d for d in ("shared/lead_scorer_contracts", "pipeline", "api", "web", "docs-site") if (root / "solution" / d).exists()]
lines.append(f"- Projetos em solution/: {', '.join(present) or 'nenhum'}. DoD: make test && make lint (JAVA_HOME=JDK 17/21).")

dec = root / "process-log" / "decisions.md"
if dec.exists():
    heads = [l for l in dec.read_text(encoding="utf-8").splitlines() if l.startswith("## ")]
    lines.append(f"- Decision log: {len(heads)} entradas. Última: {heads[-1][3:] if heads else '-'}")
else:
    lines.append("- Decision log ainda não existe: use /log-process na primeira decisão.")

lines.append("- Fluxo: product-manager/owner → revops → tech-lead → data-engineer → data-scientist → machine-learning-engineer → backend-engineer ∥ product-designer → application-engineer → quality-engineer → code-reviewer/security-engineer/g4-evaluator → tech-writer. /pr-check antes de push.")
print("\n".join(lines))
