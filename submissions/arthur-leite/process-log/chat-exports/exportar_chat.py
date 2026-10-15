"""Converte o transcript JSONL da sessão do Claude Code em Markdown legível para o process log.

Remove: lembretes de sistema, raciocínio interno, conteúdo da memória pessoal do assistente
(cita outros clientes) e qualquer coisa parecida com token/chave.
"""
import json
import re
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
DST = Path(sys.argv[2])

SENSIVEL = re.compile(r"\.claude[/\\]projects|MEMORY\.md|memory[/\\]|companyId|reference_mavra|feedback_|project_[a-z_]+\.md", re.I)
SEGREDO = re.compile(r"(gho_[A-Za-z0-9]{10,}|AIza[0-9A-Za-z_\-]{20,}|sk-[A-Za-z0-9]{20,}|GEMINI_API_KEY=\S+)")
TAGS = re.compile(r"<(system-reminder|command-[a-z]+|local-command-stdout|task-notification|agent-message)[^>]*>.*?</\1>", re.S)


def limpar(txt: str) -> str:
    txt = TAGS.sub("", txt)
    txt = SEGREDO.sub("[REDIGIDO]", txt)
    return txt.strip()


def cortar(txt: str, n: int) -> str:
    return txt if len(txt) <= n else txt[:n] + f"\n… [+{len(txt) - n} caracteres omitidos]"


def resumo_ferramenta(nome: str, entrada: dict) -> str:
    bruto = json.dumps(entrada, ensure_ascii=False)
    if SENSIVEL.search(bruto):
        return f"**🔧 {nome}**: _[omitido: operação na memória pessoal do assistente]_"
    desc = entrada.get("description") or entrada.get("prompt", "")[:120] if isinstance(entrada, dict) else ""
    corpo = entrada.get("command") or entrada.get("content") or entrada.get("prompt") or entrada.get("new_string") or bruto
    alvo = entrada.get("file_path") or entrada.get("url") or ""
    cab = f"**🔧 {nome}**" + (f" `{alvo}`" if alvo else "") + (f": {desc}" if desc else "")
    return cab + "\n```\n" + cortar(limpar(str(corpo)), 1500) + "\n```"


linhas = ["# Conversa completa com o Claude Code: Challenge 002", "",
          "_Exportada do transcript da sessão. O raciocínio interno do modelo, os lembretes de sistema e o conteúdo da memória "
          "pessoal do assistente (que cita outros projetos) foram removidos. Entradas longas de ferramentas e saídas foram truncadas._", ""]
for l in SRC.read_text(encoding="utf-8").splitlines():
    o = json.loads(l)
    if o.get("type") not in ("user", "assistant") or o.get("isMeta"):
        continue
    cont = o.get("message", {}).get("content")
    blocos = [{"type": "text", "text": cont}] if isinstance(cont, str) else (cont or [])
    for b in blocos:
        t = b.get("type")
        if o["type"] == "user" and t == "text":
            txt = limpar(b["text"])
            if txt and not txt.startswith("Base directory for this skill") and "Claude in Chrome browser automation" not in txt[:80]:
                linhas += ["---", "", "### 👤 Arthur", "", txt, ""]
        elif o["type"] == "assistant" and t == "text":
            txt = limpar(b["text"])
            if txt:
                linhas += ["### 🤖 Claude", "", txt, ""]
        elif t == "tool_use":
            linhas += [resumo_ferramenta(b.get("name", "?"), b.get("input", {})), ""]
        elif t == "tool_result":
            c = b.get("content")
            txt = c if isinstance(c, str) else "\n".join(x.get("text", "[imagem]") for x in (c or []) if isinstance(x, dict))
            if SENSIVEL.search(txt):
                txt = "[omitido: conteúdo da memória pessoal do assistente]"
            linhas += ["<details><summary>resultado</summary>", "", "```", cortar(limpar(txt), 1200), "```", "</details>", ""]

DST.parent.mkdir(parents=True, exist_ok=True)
DST.write_text("\n".join(linhas), encoding="utf-8")
print(f"{DST} ({DST.stat().st_size // 1024} KB)")
