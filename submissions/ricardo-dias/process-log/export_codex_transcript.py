"""Converte uma sessão do Codex (rollout .jsonl) em Markdown legível para o process log.

Uso:
  uv run --project ../solution/analysis python export_codex_transcript.py <rollout.jsonl> <saida.md>

Entra: mensagens do usuário e do Codex, cada chamada de ferramenta (script executado, resumido) e a saída
resumida, com o modelo e o esforço de raciocínio registrados na sessão.
Não entra: instruções de sistema/desenvolvedor e contexto injetado automaticamente (perfil pessoal do Codex,
AGENTS.md global, lista de plugins, ambiente) e blocos de raciocínio (criptografados na sessão).
Sanitização: a mesma de export_transcript.py (e-mails, usuário do Windows, contas, segredos).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from export_transcript import MAX_RESULT, clean, clip, fence, when

MAX_SCRIPT = 900
# Blocos que o Codex injeta como mensagem de "user" mas não foram digitados pelo usuário.
INJECTED_PREFIXES = ("# AGENTS.md instructions", "<environment_context>", "<recommended_plugins>", "<user_instructions>",
                     "<permissions", "<skills_instructions>", "<turn_aborted>")


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    return "\n".join(c.get("text", "") for c in content or [] if isinstance(c, dict))


def main(src: Path, dst: Path) -> None:
    rows = [json.loads(line) for line in src.open(encoding="utf-8")]
    meta = next((r["payload"] for r in rows if r.get("type") == "session_meta"), {})
    ctx = next((r["payload"] for r in rows if r.get("type") == "turn_context"), {})
    out = [
        "# Transcript — Codex (sessão do projeto)",
        "",
        f"Exportado de `{src.name}` por `process-log/export_codex_transcript.py`. Horários em Brasília.",
        "",
        f"- **Modelo:** `{ctx.get('model')}` · **raciocínio:** `{ctx.get('effort')}` · **cliente:** `{meta.get('originator')}` {meta.get('cli_version', '')}",
        f"- **Diretório:** `{clean(meta.get('cwd', ''))}`",
        "",
        "Inclui mensagens do Ricardo e do Codex, chamadas de ferramenta com script e saída resumidos.",
        "Omite instruções de sistema e contexto injetado automaticamente (perfil pessoal do Codex, AGENTS.md global,",
        "plugins) e blocos de raciocínio (criptografados). Dados pessoais foram substituídos por marcadores.",
        "",
    ]
    users = calls = 0
    for r in rows:
        p = r.get("payload") or {}
        ts = when(r.get("timestamp"))
        if r.get("type") != "response_item":
            continue
        kind = p.get("type")
        if kind == "message":
            role = p.get("role")
            text = text_of(p.get("content"))
            if role == "user":
                if text.lstrip().startswith(INJECTED_PREFIXES) or not clean(text):
                    continue
                users += 1
                out += ["", "---", "", f"## 🧑 Ricardo · {ts}", "", clean(text)]
            elif role == "assistant" and clean(text):
                out += ["", f"**🤖 Codex** · {ts}", "", clean(text)]
        elif kind in ("custom_tool_call", "function_call"):
            calls += 1
            body = p.get("input") if kind == "custom_tool_call" else p.get("arguments", "")
            out += ["", f"**🔧 {p.get('name')}**", "", fence(clip(str(body), MAX_SCRIPT), "js")]
        elif kind in ("custom_tool_call_output", "function_call_output"):
            output = p.get("output")
            text = text_of(output) if not isinstance(output, str) else output
            out += ["", "<details><summary>Saída</summary>", "", fence(clip(text, MAX_RESULT)), "", "</details>"]

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{dst}: {users} mensagens do usuário, {calls} chamadas de ferramenta, {dst.stat().st_size / 1e3:.0f} kB")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]), Path(sys.argv[2]))
