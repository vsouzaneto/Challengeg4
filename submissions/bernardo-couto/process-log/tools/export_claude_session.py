#!/usr/bin/env python3
"""Export a Claude Code session transcript (JSONL) to readable Markdown.

Usage: python3 export_claude_session.py <session.jsonl> <out.md> [--filter-file patterns.txt]
                                        [--since ISO8601] [--until ISO8601]

- Keeps user prompts, assistant text, tool calls (name + trimmed input) and trimmed tool results.
- Drops thinking blocks and harness metadata.
- Blocks matching any pattern in the filter file are not exported (and neither are the results of
  filtered tool calls).
- --since/--until (UTC ISO timestamps) slice one long JSONL into per-session exports.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

MAX_INPUT = 900
MAX_RESULT = 1200


def load_patterns(path: str | None) -> list[re.Pattern[str]]:
    if not path:
        return []
    return [re.compile(p, re.I) for p in Path(path).read_text().splitlines() if p.strip() and not p.startswith("#")]


def matches(text: str, patterns: list[re.Pattern[str]]) -> bool:
    return any(p.search(text) for p in patterns)


def fmt_ts(ts: str) -> str:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ts


def trim(s: str, n: int) -> str:
    s = s.strip()
    return s if len(s) <= n else s[:n].rstrip() + f"\n… [{len(s) - n} caracteres omitidos]"


def opt(name: str) -> str | None:
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else None


def main() -> None:
    src, out = sys.argv[1], sys.argv[2]
    patterns = load_patterns(opt("--filter-file"))
    since, until = opt("--since"), opt("--until")
    lines = ["# Chat export — sessão Claude Code", "",
             f"Fonte: `{Path(src).name}` · gerado em {datetime.now().strftime('%Y-%m-%d %H:%M')}", "",
             "Prompts, respostas, chamadas de ferramenta e resultados (resumidos). Blocos de raciocínio interno do modelo não são exportados.", ""]
    dropped_tool_ids: set[str] = set()
    for raw in open(src, encoding="utf-8"):
        try:
            d = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if d.get("type") not in ("user", "assistant") or d.get("isSidechain"):
            continue
        ts = d.get("timestamp") or ""
        if (since and ts < since) or (until and ts >= until):
            continue
        msg = d.get("message") or {}
        content = msg.get("content")
        ts = fmt_ts(d.get("timestamp", ""))
        blocks = content if isinstance(content, list) else [{"type": "text", "text": str(content)}]
        for b in blocks:
            t = b.get("type")
            if t == "thinking":
                continue
            if t == "text":
                text = b.get("text", "")
                if not text.strip() or text.startswith("<ide_") or text.startswith("<system-reminder") or matches(text, patterns):
                    continue
                if d.get("isMeta") or text.startswith("Another Claude session sent a message"):
                    lines += [f"### 🤖 Subagente → orquestrador · {ts}", "", trim(text, MAX_RESULT), ""]
                    continue
                who = "👤 Bernardo" if d["type"] == "user" else "🧠 Claude"
                lines += [f"### {who} · {ts}", "", text.strip(), ""]
            elif t == "tool_use":
                inp = b.get("input", {})
                desc = (inp.get("description") or inp.get("prompt", "")[:120]) if isinstance(inp, dict) else ""
                body = json.dumps(inp, ensure_ascii=False, indent=1) if isinstance(inp, dict) else str(inp)
                if matches(body, patterns) or matches(str(desc), patterns):
                    dropped_tool_ids.add(b.get("id", ""))
                    continue
                lines += [f"**🔧 Ferramenta `{b.get('name')}`** — {desc}", "", "```json", trim(body, MAX_INPUT), "```", ""]
            elif t == "tool_result":
                if b.get("tool_use_id") in dropped_tool_ids:
                    continue
                c = b.get("content")
                if isinstance(c, list):
                    c = "\n".join(x.get("text", "") for x in c if isinstance(x, dict))
                c = str(c or "")
                if matches(c, patterns):
                    continue
                lines += ["<details><summary>Resultado</summary>", "", "```", trim(c, MAX_RESULT), "```", "", "</details>", ""]
    Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"ok: {out} ({len(lines)} linhas)")


if __name__ == "__main__":
    main()
