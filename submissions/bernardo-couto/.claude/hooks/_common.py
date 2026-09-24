"""Shared helpers for Claude Code hooks (stdlib only, Python 3.9+)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def read_payload() -> dict:
    """Fail closed: an unreadable payload denies the action instead of silently allowing it."""
    try:
        data = json.load(sys.stdin)
    except Exception:
        deny("Hook recebeu payload inválido; ação negada por segurança (fail-closed).")
    if not isinstance(data, dict):
        deny("Hook recebeu payload inesperado; ação negada por segurança (fail-closed).")
    return data


def project_dir() -> Path:
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parents[2]


def deny(reason: str) -> None:
    """PreToolUse: block the tool call and tell Claude why."""
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    sys.exit(0)


def allow() -> None:
    sys.exit(0)


def post_block(reason: str) -> None:
    """PostToolUse: the action already happened; make Claude address the issue."""
    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


def is_inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root)
        return True
    except ValueError:
        return False
