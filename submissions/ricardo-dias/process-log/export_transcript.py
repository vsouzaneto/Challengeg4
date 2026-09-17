"""Converte o transcript de uma sessão do Claude Code (.jsonl) em Markdown legível para o process log.

Uso:
  uv run --project ../solution/analysis python export_transcript.py <sessao.jsonl> <saida.md>

O que entra: mensagens do usuário (inclusive as enviadas no meio de um turno), respostas do assistente,
cada chamada de ferramenta (descrição, comando/caminho, saída resumida), perguntas de múltipla escolha
com as respostas e os planos aprovados na íntegra.
O que não entra: contexto de sistema e lembretes automáticos, blocos de raciocínio (a sessão não guarda
o conteúdo deles), conteúdo integral de arquivos escritos (está no git) e notificações de tarefas em segundo plano.
Sanitização: e-mails, caminho do usuário do Windows e identificadores de conta de trabalho.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

LOCAL_TZ = timezone(timedelta(hours=-3))  # horário de Brasília
MAX_RESULT = 1_200
MAX_COMMAND = 700
MAX_EDIT_PREVIEW = 240

REDACTIONS = [
    (re.compile(r"[A-Za-z0-9._%+-]+@(?!anthropic\.com)[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[e-mail]"),
    (re.compile(r"(?i)[A-Z]:[\\/]+Users[\\/]+rsdias"), "~"),
    (re.compile(r"(?i)/c/Users/rsdias"), "~"),
    (re.compile(r"(?i)\brsdias\b"), "usuario"),
    (re.compile(r"(?i)viteunimed"), "[conta-de-trabalho]"),
    (re.compile(r"(?i)\b(sk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{20,}|vck_[A-Za-z0-9]{16,})"), "[segredo]"),
]
SYSTEM_TAGS = re.compile(r"<(system-reminder|command-name|command-message|command-args|local-command-stdout)>.*?</\1>", re.S)


def clean(text: str) -> str:
    text = SYSTEM_TAGS.sub("", text)
    for pattern, repl in REDACTIONS:
        text = pattern.sub(repl, text)
    return text.strip()


def clip(text: str, limit: int) -> str:
    text = clean(text)
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + f"\n… [+{len(text) - limit} caracteres omitidos]"


def fence(text: str, lang: str = "") -> str:
    ticks = "````" if "```" in text else "```"
    return f"{ticks}{lang}\n{text}\n{ticks}"


def when(ts: str | None) -> str:
    if not ts:
        return ""
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(LOCAL_TZ)
    return dt.strftime("%d/%m %H:%M")


def result_text(content) -> str:
    if isinstance(content, str):
        return content
    parts = []
    for c in content or []:
        if c.get("type") == "text":
            parts.append(c["text"])
        elif c.get("type") == "image":
            parts.append("[imagem]")
    return "\n".join(parts)


def describe_tool(name: str, inp: dict) -> str:
    desc = inp.get("description")
    head = f"**🔧 {name}**" + (f": {clean(desc)}" if desc else "")
    if name in ("Bash", "PowerShell"):
        return head + "\n\n" + fence(clip(inp.get("command", ""), MAX_COMMAND), "bash")
    if name == "Write":
        lines = inp.get("content", "").count("\n") + 1
        return head + f" `{clean(inp.get('file_path', ''))}` ({lines} linhas)"
    if name == "Edit":
        old = clip(inp.get("old_string", ""), MAX_EDIT_PREVIEW)
        new = clip(inp.get("new_string", ""), MAX_EDIT_PREVIEW)
        return head + f" `{clean(inp.get('file_path', ''))}`\n\n" + fence(f"- {old}\n+ {new}", "diff")
    if name in ("Read", "Grep", "Glob"):
        target = inp.get("file_path") or inp.get("path") or ""
        extra = inp.get("pattern", "")
        return head + f" `{clean(target)}` {clean(extra)}".rstrip()
    if name == "WebFetch":
        return head + f" {inp.get('url', '')}"
    if name == "AskUserQuestion":
        out = [head]
        for q in inp.get("questions", []):
            out.append(f"\n> **{clean(q['question'])}**")
            for o in q.get("options", []):
                out.append(f"> - {clean(o['label'])}: {clean(o.get('description', ''))}")
        return "\n".join(out)
    if name in ("ExitPlanMode", "ToolSearch", "TaskStop"):
        return head
    return head + "\n\n" + fence(clip(json.dumps(inp, ensure_ascii=False, indent=1), MAX_COMMAND), "json")


def main(src: Path, dst: Path) -> None:
    rows = [json.loads(line) for line in src.open(encoding="utf-8")]
    user_prompts = {clean(r["message"]["content"]) for r in rows
                    if r.get("type") == "user" and isinstance(r.get("message", {}).get("content"), str)}
    tool_names: dict[str, str] = {}
    out = [
        "# Transcript — Claude Code (sessão principal)",
        "",
        f"Exportado de `{src.name}` por `process-log/export_transcript.py`. Horários em Brasília.",
        "",
        "Inclui mensagens do Ricardo, respostas do Claude, chamadas de ferramentas com saída resumida e planos aprovados.",
        "Omite contexto de sistema, conteúdo integral de arquivos (está no git) e blocos de raciocínio (não registrados na sessão).",
        "Dados pessoais e identificadores de conta foram substituídos por marcadores.",
        "",
    ]
    turn = 0
    for r in rows:
        kind = r.get("type")
        ts = when(r.get("timestamp"))
        if kind == "user" and isinstance(r["message"].get("content"), str):
            text = clean(r["message"]["content"])
            if not text:
                continue
            turn += 1
            out += ["", "---", "", f"## 🧑 Ricardo · {ts}", "", text]
        elif kind == "attachment" and r["attachment"].get("type") == "queued_command":
            att = r["attachment"]
            text = clean(att.get("prompt", ""))
            if (att.get("origin") or {}).get("kind") == "human" and text and text not in user_prompts:
                out += ["", f"### 🧑 Ricardo (mensagem enviada durante o turno) · {when(att.get('timestamp'))}", "", text]
        elif kind == "assistant":
            for c in r["message"]["content"]:
                if c["type"] == "text" and clean(c["text"]):
                    out += ["", f"**🤖 Claude** · {ts}", "", clean(c["text"])]
                elif c["type"] == "tool_use":
                    tool_names[c["id"]] = c["name"]
                    out += ["", describe_tool(c["name"], c.get("input", {}))]
        elif kind == "user" and isinstance(r["message"].get("content"), list):
            for c in r["message"]["content"]:
                if c.get("type") != "tool_result":
                    continue
                name = tool_names.get(c.get("tool_use_id"), "")
                text = result_text(c.get("content"))
                if name in ("ToolSearch",):
                    continue
                if name == "ExitPlanMode":
                    out += ["", "<details><summary>Plano aprovado (íntegra)</summary>", "", clean(text), "", "</details>"]
                    continue
                if name == "AskUserQuestion":
                    out += ["", f"> **Resposta:** {clip(text, MAX_RESULT)}"]
                    continue
                if name in ("Write", "Edit") and not c.get("is_error"):
                    continue
                label = "Erro" if c.get("is_error") else "Saída"
                out += ["", f"<details><summary>{label}</summary>", "", fence(clip(text, MAX_RESULT)), "", "</details>"]

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{dst}: {turn} mensagens diretas, {len(tool_names)} chamadas de ferramenta, {dst.stat().st_size / 1e3:.0f} kB")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]), Path(sys.argv[2]))
