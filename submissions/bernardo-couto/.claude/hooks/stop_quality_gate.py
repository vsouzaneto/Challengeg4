#!/usr/bin/env python3
"""Stop: quality gate. If solution code changed in this session and tests fail, ask Claude to keep going.

Guards against loops via stop_hook_active. Skips when the Python project does not exist yet.
"""
import subprocess

from _common import project_dir, read_payload

payload = read_payload()
if payload.get("stop_hook_active"):
    raise SystemExit(0)

root = project_dir()
solution = root / "solution"
projects = [solution / d for d in ("shared/lead_scorer_contracts", "pipeline", "api") if (solution / d / "pyproject.toml").exists()]
if not projects:
    raise SystemExit(0)

repo = root.parents[1]
try:
    changed = subprocess.run(
        ["git", "status", "--short", "--", "submissions/bernardo-couto/solution"],
        cwd=repo, capture_output=True, text=True, timeout=30,
    ).stdout
except Exception:
    raise SystemExit(0)
if not any(l[3:].endswith((".py", ".toml")) for l in changed.splitlines()):
    raise SystemExit(0)

import os
env = dict(os.environ)
if "JAVA_HOME" not in env:
    for v in ("21", "17"):
        jh = subprocess.run(["/usr/libexec/java_home", "-v", v], capture_output=True, text=True).stdout.strip()
        if jh:
            env["JAVA_HOME"] = jh
            break
failures = []
for proj in projects:
    if not any(l[3:].startswith(str(proj.relative_to(repo)) + "/") for l in changed.splitlines()):
        continue
    try:
        res = subprocess.run(
            ["uv", "run", "--quiet", "pytest", "-q", "-x", "--no-header", "-p", "no:cacheprovider"],
            cwd=proj, capture_output=True, text=True, timeout=240, env=env,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"(quality gate: não foi possível rodar pytest em {proj.name}: {exc})")
        continue
    if res.returncode != 0:
        failures.append((proj.name, "\n".join((res.stdout + res.stderr).strip().splitlines()[-15:])))

if failures:
    tail = "\n\n".join(f"[{n}]\n{o}" for n, o in failures)
    import json
    print(json.dumps({
        "decision": "block",
        "reason": "Quality gate: há código de solução alterado e `uv run pytest -q -x` falhou. "
                  "Corrija os testes (ou explique ao Bernardo por que não dá) antes de encerrar.\n" + tail,
    }))
raise SystemExit(0)
