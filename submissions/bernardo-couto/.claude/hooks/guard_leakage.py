#!/usr/bin/env python3
"""PostToolUse (Edit|Write): domain guardrails for solution code.

Scans Python files written under solution/pipeline, solution/api or solution/shared for
1. target leakage: use of close_value / close_date / outcome_* in feature or scoring code;
2. wall-clock time: now()/today() instead of SNAPSHOT_DATE;
3. hardcoded typo fixes hidden in the UI instead of the cleaning layer.
Blocks with a reason so Claude must fix or explicitly justify with `# leakage-ok: <why>`.
"""
import re
from pathlib import Path

from _common import is_inside, post_block, project_dir, read_payload

payload = read_payload()
tool_input = payload.get("tool_input") or {}
raw = tool_input.get("file_path") or ""
if not raw or not raw.endswith(".py"):
    raise SystemExit(0)

root = project_dir()
path = Path(raw)
if not path.is_absolute():
    path = Path(payload.get("cwd") or root) / path
path = path.resolve()
solution = (root / "solution").resolve()
if not is_inside(path, solution) or "tests" in path.parts or "analysis" in path.parts or "notebooks" in path.parts:
    raise SystemExit(0)

try:
    text = path.read_text(encoding="utf-8")
except Exception:
    raise SystemExit(0)

problems = []
rel = path.relative_to(root)

# 1. Wall-clock time anywhere in solution code.
for i, line in enumerate(text.splitlines(), 1):
    if "leakage-ok" in line or line.strip().startswith("#"):
        continue
    if re.search(r"\b(datetime|date|pd\.Timestamp|Timestamp)\.(now|today|utcnow)\(\)|\btime\.time\(\)|\bcurrent_date\(\)|\bcurrent_timestamp\(\)|\bF\.(current_date|current_timestamp|now)\b", line):
        problems.append(f"{rel}:{i}: uso de relógio real (Python ou Spark). Use SNAPSHOT_DATE / as_of (dados são um snapshot de 2017-12-31).")
    if re.search(r"\.randomSplit\(|\bCrossValidator\b|\bTrainValidationSplit\b|\btrain_test_split\(", line):
        problems.append(f"{rel}:{i}: split aleatório em dados temporais vaza o futuro. Use os cortes as_of do backtest (skill scoring-methodology).")
    if re.search(r"inferSchema\s*=\s*True|option\([\"']inferSchema[\"'],\s*[\"']?true", line, re.I):
        problems.append(f"{rel}:{i}: inferSchema=True. Declare o StructType (bronze com FAILFAST).")

# 2. Outcome columns in feature/scoring code.
is_feature_or_scoring = any(k in str(rel) for k in ("features", "scoring", "score", "rules", "model", "explain", "/ml/", "jobs/score", "jobs/train")) or "app" in path.parts
if is_feature_or_scoring:
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#") or "leakage-ok" in line:
            continue
        if re.search(r"[\"']close_value[\"']|\bclose_value\b|[\"']close_date[\"']|\bclose_date\b|\boutcome_\w+", line):
            problems.append(f"{rel}:{i}: referência a coluna de desfecho ({stripped[:80]}). Em features/scoring isso é leakage; só permitido em compute_history()/backtest com as_of e comentário `# leakage-ok: <motivo>`.")

# 3. Typo fixes outside the cleaning layer.
if "clean" not in path.name:
    for i, line in enumerate(text.splitlines(), 1):
        if re.search(r"GTXPro|technolgy", line) and "leakage-ok" not in line and not line.strip().startswith("#"):
            problems.append(f"{rel}:{i}: correção de dado ('GTXPro'/'technolgy') fora de data/clean.py. Centralize a limpeza.")

if problems:
    shown = "\n".join(problems[:8])
    more = f"\n(+{len(problems) - 8} outros)" if len(problems) > 8 else ""
    post_block(
        "Guardrail de domínio (leakage/tempo/limpeza) encontrou problemas no arquivo recém-escrito:\n"
        f"{shown}{more}\n"
        "Corrija, ou, se for intencional e seguro, adicione na linha o comentário `# leakage-ok: <motivo>` e registre a decisão com /log-process."
    )

raise SystemExit(0)
