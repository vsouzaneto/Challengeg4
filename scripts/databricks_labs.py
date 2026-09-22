#!/usr/bin/env python3
"""Upload the four lab packs to a Databricks workspace and optionally run jobs.

Auth is only DATABRICKS_HOST + DATABRICKS_TOKEN from the environment.
Never print the token.
"""

from __future__ import annotations

import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PACKS = (
    "notebook-data-001-churn",
    "notebook-process-002-support",
    "notebook-build-003-lead-scorer",
    "notebook-marketing-004-social",
)

SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules", ".ipynb_checkpoints"}
MAX_UPLOAD_BYTES = 9_000_000

DEFAULT_JOBS = {
    "001": os.environ.get("DATABRICKS_JOB_001", "463412912486977"),
    "002": os.environ.get("DATABRICKS_JOB_002", "888714546284385"),
    "003": os.environ.get("DATABRICKS_JOB_003", "335361037070072"),
    "004": os.environ.get("DATABRICKS_JOB_004", "22696065654490"),
}


def workspace_path(user: str, relative: str) -> str:
    return f"/Users/{user}/ai-master-challenge/{relative}".replace("\\", "/")


def import_path(local: Path, dest: str) -> str:
    if local.suffix == ".ipynb":
        return dest[: -len(".ipynb")] if dest.endswith(".ipynb") else dest
    return dest


def should_skip_file(path: Path, limit: int = MAX_UPLOAD_BYTES) -> bool:
    return path.is_file() and path.stat().st_size > limit


def iter_pack_files(pack_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in pack_dir.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        files.append(path)
    return files


def require_auth() -> tuple[str, str, str]:
    host = os.environ.get("DATABRICKS_HOST", "").rstrip("/")
    token = os.environ.get("DATABRICKS_TOKEN", "")
    user = os.environ.get("DATABRICKS_USER", "")
    missing = [
        name
        for name, value in (
            ("DATABRICKS_HOST", host),
            ("DATABRICKS_TOKEN", token),
            ("DATABRICKS_USER", user),
        )
        if not value
    ]
    if missing:
        raise SystemExit(
            "Defina no ambiente (não grave o token no git): " + ", ".join(missing)
        )
    return host, token, user


def api(host: str, token: str, method: str, route: str, body: dict | None = None) -> dict:
    request = urllib.request.Request(
        f"{host}{route}",
        data=None if body is None else json.dumps(body).encode("utf-8"),
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            raw = response.read()
            return json.loads(raw.decode("utf-8")) if raw else {}
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:400]
        raise SystemExit(f"Databricks {method} {route} -> {error.code}: {detail}") from error


def mkdir(host: str, token: str, path: str) -> None:
    api(host, token, "POST", "/api/2.0/workspace/mkdirs", {"path": path})


def upload_file(host: str, token: str, local: Path, dest: str) -> None:
    content = base64.b64encode(local.read_bytes()).decode("ascii")
    fmt = "JUPYTER" if local.suffix == ".ipynb" else "AUTO"
    api(
        host,
        token,
        "POST",
        "/api/2.0/workspace/import",
        {
            "path": import_path(local, dest),
            "format": fmt,
            "content": content,
            "overwrite": True,
        },
    )


def check() -> None:
    missing = [name for name in PACKS if not (ROOT / name).is_dir()]
    if missing:
        raise SystemExit("Pastas de lab ausentes: " + ", ".join(missing))
    print(f"ok {len(PACKS)} packs")


def upload() -> None:
    host, token, user = require_auth()
    root_ws = workspace_path(user, "").rstrip("/")
    mkdir(host, token, root_ws)
    skipped: list[str] = []
    uploaded = 0
    for pack in PACKS:
        pack_dir = ROOT / pack
        mkdir(host, token, workspace_path(user, pack))
        for local in iter_pack_files(pack_dir):
            relative = local.relative_to(ROOT).as_posix()
            dest = workspace_path(user, relative)
            mkdir(host, token, dest.rsplit("/", 1)[0])
            if should_skip_file(local):
                skipped.append(f"{relative} ({local.stat().st_size} bytes)")
                continue
            upload_file(host, token, local, dest)
            uploaded += 1
            print(f"ok {relative}")
    print(f"enviados {uploaded} arquivos para {root_ws}")
    if skipped:
        print("pulados (>9 MB; use Volume ou data_path):")
        for item in skipped:
            print(f"  {item}")


def run_jobs() -> None:
    host, token, _user = require_auth()
    for label, job_id in DEFAULT_JOBS.items():
        result = api(host, token, "POST", "/api/2.1/jobs/run-now", {"job_id": int(job_id)})
        run_id = result.get("run_id")
        print(f"job {label} ({job_id}) run_id={run_id}")


def main(argv: list[str]) -> None:
    command = argv[1] if len(argv) > 1 else "help"
    if command == "check":
        check()
        return
    if command == "upload":
        check()
        upload()
        return
    if command == "run":
        run_jobs()
        return
    if command == "all":
        check()
        upload()
        run_jobs()
        return
    print("uso: python scripts/databricks_labs.py check|upload|run|all")
    raise SystemExit(2)


if __name__ == "__main__":
    main(sys.argv)
