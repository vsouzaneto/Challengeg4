"""Gera a versão legível do export da conversa do Claude Code.

Uso:  python gerar.py <pasta com o zip do export descompactado> [nome a omitir ...]

O zip vem do menu da sessão no app (Export): transcript.jsonl, subagents/, workflows/ e metadata.json.
Saída, nesta pasta: conversa.md, conversa.html, conversa.json, subagentes.md e checagem.json.

Entra na íntegra: toda mensagem digitada pelo Pedro (inclusive as enviadas no meio de um turno e as respostas às
perguntas de múltipla escolha) e todo texto do assistente. Cada chamada de ferramenta vira uma linha com o nome e o
propósito, e os eventos de sistema (troca de modelo, resumo de contexto, notificações de tarefa) viram notas.
Fica só no zip: o raciocínio interno do modelo, as saídas das ferramentas e o contexto injetado pelo sistema. É ali que
estão os dados pessoais e um segredo: o e-mail da conta (contexto de sessão), o perfil de memória do assistente com
telefone, e-mails e histórico profissional (saída da leitura da memória), o e-mail de autor dos commits (saída do git
log) e a chave da API do Gemini (saída do comando que renomeou o .env). A checagem conta essas ocorrências no bruto,
sem imprimir o valor, e confirma que nenhuma chega à saída.
"""
import json
import re
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
SRC = Path(sys.argv[1])
OUT = Path(__file__).resolve().parent
BRT = timezone(timedelta(hours=-3))  # o Brasil não tem horário de verão desde 2019

SR = re.compile(r"\s*<system-reminder>.*?</system-reminder>\s*", re.S)
PASTE_OPEN = re.compile(r"<pasted_content[^>]*>")
PASTE_CLOSE = re.compile(r"</pasted_content[^>]*>")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}\b")  # sufixo alfabético: não pega pacote@1.2.3
EMAIL_OK = re.compile(r"(example\.(com|org)|anthropic\.com|users\.noreply\.github\.com)$", re.I)
PHONE = re.compile(r"\+?55[\s-]?\(?\d{2}\)?[\s-]?9?\d{4}[\s-]?\d{4}\b|\(\d{2}\)\s?9?\d{4}-?\d{4}\b")
SECRET = re.compile(r"AQ\.[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{20,}|gh[opsu]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}")
HOME_RE = r"(?:[A-Za-z]:|/[a-z])[\\/]+Users[\\/]+pedri"
SESSAO = re.compile(HOME_RE + r"[\\/]+AppData[\\/]+Local[\\/]+Temp[\\/]+claude[\\/]+[^\\/\s\"']+[\\/]+[^\\/\s\"']+", re.I)
REPO = re.compile(HOME_RE + r"[\\/]+Projetos claude code[\\/]+ai-master-challenge[\\/]*", re.I)
HOME = re.compile(HOME_RE, re.I)
# Nomes a omitir, passados na linha de comando para não ficarem gravados aqui (ex.: a segunda conta do GitHub do Pedro)
OUTRA_CONTA = re.compile(r"\b(" + "|".join(map(re.escape, sys.argv[2:])) + r")\b") if sys.argv[2:] else None

redacoes = Counter()


def redact(s):
    def mail(m):
        if EMAIL_OK.search(m.group(0)):
            return m.group(0)
        redacoes["e-mail"] += 1
        return "[e-mail removido]"

    def fone(m):
        redacoes["telefone"] += 1
        return "[telefone removido]"

    def conta(m):
        redacoes["nome da segunda conta do GitHub"] += 1
        return "[outra conta]"

    def segredo(m):
        redacoes["segredo"] += 1
        return "[segredo removido]"

    s = PHONE.sub(fone, EMAIL.sub(mail, s))
    if OUTRA_CONTA:
        s = OUTRA_CONTA.sub(conta, s)
    return SECRET.sub(segredo, s)


def hora(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(BRT)


def rel(p):
    """Caminhos das linhas de ferramenta: repositório relativo, pasta temporária da sessão e home encurtadas."""
    return HOME.sub("~", SESSAO.sub("<sessão>", REPO.sub("", str(p))))


def user_text(t):
    """Texto digitado: sem o contexto injetado, com o texto colado marcado."""
    t = SR.sub("\n", t).strip()
    t = PASTE_OPEN.sub("[texto colado]\n", t)
    return PASTE_CLOSE.sub("\n[fim do texto colado]", t).strip()


def tool_line(b):
    n, i = b["name"], b.get("input", {}) or {}
    short = n.split("__")[-1] if n.startswith("mcp__") else n
    if n in ("Bash", "PowerShell", "Monitor") or (n not in ("Agent",) and isinstance(i.get("description"), str) and "command" in i):
        d = i.get("description") or i.get("command", "")
    elif n in ("Read", "Write", "Edit", "NotebookEdit"):
        d = rel(i.get("file_path", ""))
    elif n in ("Grep", "Glob"):
        d = i.get("pattern", "") + (f" em {rel(i['path'])}" if i.get("path") else "")
    elif n == "Workflow":
        m = re.search(r"name:\s*'([^']+)'", i.get("script", "") or "")
        d = m.group(1) if m else rel(i.get("scriptPath") or i.get("name", ""))
        if i.get("resumeFromRunId"):
            d += f" (retomada de {i['resumeFromRunId']})"
    elif n == "Agent":
        d = i.get("description", "")
    elif n == "Skill":
        d = i.get("skill", "")
    elif n.endswith("mark_chapter"):
        d = i.get("title", "")
    elif n == "ToolSearch":
        d = i.get("query", "")
    elif n == "AskUserQuestion":
        d = " | ".join(q.get("question", "") for q in i.get("questions", []))
    elif n in ("TaskStop", "SendUserFile"):
        d = i.get("task_id") or ", ".join(rel(f) for f in i.get("files", []))
    elif "browser_batch" in n:
        d = ", ".join(a.get("name", "") for a in i.get("actions", []))
    elif "javascript_tool" in n:
        d = "executa JavaScript na página (inspeção)"
    elif any(k in n for k in ("navigate", "preview_start")):
        d = i.get("url") or i.get("name", "")
    elif "export_transcript" in n or "get_session" in n:
        d = i.get("session_id", "")
    else:
        d = json.dumps(i, ensure_ascii=False)
    d = " ".join(rel(d).split())
    return short, redact(d[:220] + ("…" if len(d) > 220 else ""))


# ------------------------------------------------------------------ leitura do transcript principal
main = SRC / "transcript.jsonl"
meta = json.loads((SRC / "metadata.json").read_text(encoding="utf-8"))
events, raw = [], Counter()
ask_ids, raw_assistant_texts, raw_user_texts = set(), [], []
seen_user = set()


def push_user(text, ts, origem):
    key = " ".join(text.split())
    if key in seen_user:
        return
    seen_user.add(key)
    raw_user_texts.append(text)
    events.append({"kind": "user", "ts": ts, "text": redact(text), "origem": origem})


def push_system(text, ts, detalhe=None):
    last = events[-1] if events else None
    if last and last["kind"] == "system" and last.get("base") == text:
        last["n"] += 1
        last["fim"] = ts
        return
    events.append({"kind": "system", "ts": ts, "text": text, "base": text, "n": 1, "fim": ts, "detalhe": detalhe})


def assistant_turn(ts):
    if not events or events[-1]["kind"] != "assistant":
        events.append({"kind": "assistant", "ts": ts, "parts": []})
    return events[-1]


model_pending = None
for line in main.open(encoding="utf-8"):
    o = json.loads(line)
    t, ts = o.get("type"), o.get("timestamp")
    if t == "assistant":
        for b in o["message"]["content"]:
            bt = b.get("type")
            raw[f"assistant:{bt}"] += 1
            if bt == "text" and b["text"].strip():
                raw_assistant_texts.append(b["text"])
                assistant_turn(ts)["parts"].append({"type": "text", "text": redact(b["text"])})
            elif bt == "tool_use":
                if b["name"] == "AskUserQuestion":
                    ask_ids.add(b["id"])
                name, desc = tool_line(b)
                turn = assistant_turn(ts)
                if turn["parts"] and turn["parts"][-1]["type"] == "tools":
                    turn["parts"][-1]["items"].append([name, desc])
                else:
                    turn["parts"].append({"type": "tools", "items": [[name, desc]]})
    elif t == "user":
        c = o["message"]["content"]
        if o.get("isCompactSummary"):
            raw["resumo_de_contexto"] += 1
            body = c if isinstance(c, str) else "\n".join(b.get("text", "") for b in c if b.get("type") == "text")
            push_system("Resumo automático de contexto: a conversa ficou longa e o histórico anterior foi resumido para o modelo "
                        "(o histórico completo continua neste export).", ts, redact(SR.sub("\n", body).strip()))
            continue
        blocks = [{"type": "text", "text": c}] if isinstance(c, str) else c
        for b in blocks:
            if b.get("type") == "tool_result":
                raw["user:tool_result"] += 1
                if b.get("tool_use_id") in ask_ids:
                    rc = b["content"] if isinstance(b["content"], str) else " ".join(x.get("text", "") for x in b["content"] if isinstance(x, dict))
                    pares = re.findall(r'"([^"]+)"="([^"]*)"', rc)
                    txt = "\n".join(f"- {q} → {a}" for q, a in pares) if pares else rc
                    raw_user_texts.append(txt)
                    events.append({"kind": "user", "ts": ts, "text": redact(txt), "origem": "respostas às perguntas de múltipla escolha"})
                    raw["respostas_de_multipla_escolha"] += 1
                continue
            if b.get("type") != "text":
                continue
            txt = b["text"]
            if o.get("isMeta"):
                m = re.search(r"<command-name>([^<]+)</command-name>", txt)
                if m:
                    push_system(f"Skill carregada: {m.group(1).strip().lstrip('/')}", ts)
                continue
            clean = SR.sub("\n", txt).strip()
            if not clean or clean.startswith("<local-command-caveat>"):
                continue
            if clean.startswith("<task-notification>"):
                raw["notificacoes"] += 1
                s = re.search(r"<summary>(.*?)</summary>", clean, re.S)
                push_system("Notificação de tarefa em segundo plano: " + " ".join((s.group(1) if s else "concluída").split())[:200], ts)
                continue
            if "<command-name>/model</command-name>" in clean:
                a = re.search(r"<command-args>([^<]*)</command-args>", clean)
                model_pending = a.group(1).strip() if a else ""
                continue
            if clean.startswith("<local-command-stdout>"):
                out = re.sub(r"</?local-command-stdout>", "", clean).strip()
                raw["troca_de_modelo"] += 1
                push_system(f"O Pedro trocou o modelo (/model {model_pending or ''}): {out}", ts)
                model_pending = None
                continue
            push_user(user_text(txt), ts, "mensagem")
    elif t == "attachment" and o["attachment"].get("type") == "queued_command":
        p = str(o["attachment"].get("prompt", ""))
        clean = SR.sub("\n", p).strip()
        if clean.startswith("<task-notification>"):
            raw["notificacoes"] += 1
            s = re.search(r"<summary>(.*?)</summary>", clean, re.S)
            push_system("Notificação de tarefa em segundo plano: " + " ".join((s.group(1) if s else "concluída").split())[:200], ts)
        elif clean:
            push_user(user_text(p), ts, "mensagem enviada durante um turno")

for e in events:
    if e["kind"] == "system" and e.get("n", 1) > 1:
        e["text"] = f"{e['base']} (×{e['n']}, de {hora(e['ts']):%H:%M} a {hora(e['fim']):%H:%M})"
users = [e for e in events if e["kind"] == "user"]
asst = [e for e in events if e["kind"] == "assistant"]
n_tools = sum(len(p["items"]) for e in asst for p in e["parts"] if p["type"] == "tools")
n_texts = sum(1 for e in asst for p in e["parts"] if p["type"] == "text")
inicio, fim = hora(events[0]["ts"]), hora(events[-1]["ts"])


# ------------------------------------------------------------------ conversa.md
CODE_SPAN = re.compile(r"(`+)(.+?)\1", re.S)
MD_SPECIAL = re.compile(r"([\\`*_\[\]])")


def md_user(text):
    """Texto do Pedro no .md: '<' vira '&lt;' fora de código (o GitHub esconde tags desconhecidas), '#' no início da
    linha vira '\\#' (não vira título) e cada quebra de linha é mantida."""
    partes, pos = [], 0
    for m in CODE_SPAN.finditer(text):
        partes.append(text[pos:m.start()].replace("<", "&lt;"))
        partes.append(m.group(0))
        pos = m.end()
    partes.append(text[pos:].replace("<", "&lt;"))
    t = re.sub(r"(?m)^(\s*)#", r"\1\\#", "".join(partes))
    return t.replace("\n", "  \n")


def md_tool(d):
    return MD_SPECIAL.sub(r"\\\1", d).replace("<", "&lt;")


def tools_md(items):
    cont = Counter(n for n, _ in items)
    resumo = ", ".join(f"{n} ×{k}" if k > 1 else n for n, k in cont.most_common())
    linhas = "\n".join(f"- `{n}` — {md_tool(d)}" for n, d in items)
    return f"<details><summary>🔧 {len(items)} {'chamada' if len(items) == 1 else 'chamadas'} de ferramenta: {resumo}</summary>\n\n{linhas}\n\n</details>"


md = [f"""# Conversa com o Claude Code — Challenge 002

Versão legível do export da sessão, gerada por [`gerar.py`](gerar.py). Critérios, conferência e o que ficou de fora:
[`README.md`](README.md).

| | |
|---|---|
| Sessão | `{meta.get('cliSessionId')}` (Claude Code, app desktop, aba Code) |
| Título no app | {meta.get('title')} |
| Período | {inicio:%d/%m/%Y %H:%M} a {fim:%d/%m/%Y %H:%M} (horário de Brasília) |
| Mensagens do Pedro | {len(users)} |
| Blocos de texto do assistente | {n_texts} |
| Chamadas de ferramenta | {n_tools} |

👤 Pedro · 🤖 Claude · ⚙️ evento do sistema

> **Nota da revisão do export (24/09):** na resposta de 24/09 às 19:43, o Claude diz que nenhuma chave do Gemini
> aparece na transcrição. Está errado: a busca só procurava chaves no formato antigo (`AIza…`). A chave aparece uma vez
> no zip bruto, na saída do comando que renomeou o `.env`. Não aparece nesta versão legível nem no repositório, e a
> recomendação é revogá-la. O texto da conversa foi mantido como foi dito.

---
"""]
for e in events:
    h = hora(e["ts"])
    if e["kind"] == "user":
        extra = "" if e["origem"] == "mensagem" else f" ({e['origem']})"
        md.append(f"## 👤 Pedro — {h:%d/%m %H:%M}{extra}\n\n{md_user(e['text'])}\n")
    elif e["kind"] == "assistant":
        md.append(f"## 🤖 Claude — {h:%d/%m %H:%M}\n")
        for p in e["parts"]:
            md.append(p["text"] + "\n" if p["type"] == "text" else tools_md(p["items"]) + "\n")
    else:
        if e.get("detalhe"):
            md.append(f"> ⚙️ {h:%d/%m %H:%M} — {e['text']}\n\n<details><summary>Texto do resumo</summary>\n\n"
                      f"{e['detalhe'].replace('<', '&lt;')}\n\n</details>\n")
        else:
            md.append(f"> ⚙️ {h:%d/%m %H:%M} — {e['text']}\n")
(OUT / "conversa.md").write_text("\n".join(md), encoding="utf-8")

# ------------------------------------------------------------------ conversa.json (campos do export do claude.ai)
chat = []
for i, e in enumerate(events):
    base = {"indice": i, "created_at": e["ts"]}
    if e["kind"] == "user":
        chat.append({**base, "sender": "human", "text": e["text"], "origem": e["origem"]})
    elif e["kind"] == "assistant":
        chat.append({**base, "sender": "assistant",
                     "text": "\n\n".join(p["text"] for p in e["parts"] if p["type"] == "text"),
                     "ferramentas": [{"nome": n, "proposito": d} for p in e["parts"] if p["type"] == "tools" for n, d in p["items"]]})
    else:
        chat.append({**base, "sender": "system", "text": e["text"]})
(OUT / "conversa.json").write_text(json.dumps({
    "uuid": meta.get("cliSessionId"), "name": meta.get("title"), "origem": "Claude Code (app desktop)",
    "created_at": events[0]["ts"], "updated_at": events[-1]["ts"], "chat_messages": chat,
}, ensure_ascii=False, indent=1), encoding="utf-8")

# ------------------------------------------------------------------ conversa.html (mesmo conteúdo, para ler e para os prints)
payload = json.dumps([{**e, "hora": f"{hora(e['ts']):%d/%m %H:%M}"} for e in events], ensure_ascii=False).replace("</", "<\\/")
(OUT / "conversa.html").write_text(f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Conversa com o Claude Code</title>
<style>
:root {{ --bg:#f6f6f3; --surface:#fff; --muted:#5d6167; --border:#e3e3de; --text:#17181a; --accent:#3547c8; --on-accent:#fff; --code:#f0f0ec; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#111214; --surface:#191a1d; --muted:#a3a7ad; --border:#2c2e33; --text:#ececea; --accent:#8b98ff; --on-accent:#111214; --code:#212226; }} }}
* {{ box-sizing: border-box; }}
body {{ margin:0; background:var(--bg); color:var(--text); font:15px/1.55 system-ui, "Segoe UI", sans-serif; }}
main {{ max-width: 920px; margin: 0 auto; padding: 24px 16px 64px; }}
header h1 {{ font-size: 1.35rem; margin: 0 0 4px; }}
header p {{ color: var(--muted); margin: 0 0 18px; font-size: .9rem; }}
.ev {{ margin: 14px 0; display:flex; flex-direction:column; }}
.who {{ font-size: .78rem; color: var(--muted); margin: 0 6px 4px; }}
.bubble {{ padding: 12px 16px; border-radius: 16px; overflow-wrap:anywhere; }}
.user {{ align-items: flex-end; }}
.user .bubble {{ background: var(--accent); color: var(--on-accent); max-width: 88%; white-space: pre-wrap; border-bottom-right-radius: 5px; }}
.assistant .bubble {{ background: var(--surface); border:1px solid var(--border); max-width: 100%; border-bottom-left-radius: 5px; }}
.assistant .bubble > :first-child {{ margin-top: 0; }} .assistant .bubble > :last-child {{ margin-bottom: 0; }}
.system {{ align-items: center; }} .system .bubble {{ font-size:.82rem; color: var(--muted); padding: 4px 10px; border:1px dashed var(--border); border-radius: 999px; }}
.tools {{ font-size: .8rem; color: var(--muted); margin: 8px 0; }} .tools li {{ margin: 2px 0; }}
pre, code {{ background: var(--code); border-radius: 6px; font-size: .85em; }} pre {{ padding: 10px; overflow-x: auto; }}
table {{ border-collapse: collapse; font-size: .85rem; display:block; overflow-x:auto; }} td, th {{ border:1px solid var(--border); padding: 4px 8px; }}
.clamp .assistant .bubble {{ max-height: 700px; overflow: hidden; position: relative; }}
.clamp .assistant .bubble.cortado::after {{ content:"… (continua em conversa.md)"; position:absolute; left:0; right:0; bottom:0; padding: 40px 16px 10px; background: linear-gradient(transparent, var(--surface) 60%); font-size:.8rem; color: var(--muted); }}
.clamp .user .bubble {{ max-height: 1500px; overflow: hidden; position: relative; }}
.clamp .user .bubble.cortado::after {{ content:"… (continua em conversa.md)"; position:absolute; left:0; right:0; bottom:0; padding: 40px 16px 10px; background: linear-gradient(transparent, var(--accent) 60%); font-size:.8rem; color: var(--on-accent); }}
</style></head>
<body><main><header><h1>Conversa com o Claude Code — Challenge 002</h1>
<p>Sessão <code>{meta.get('cliSessionId')}</code> · {inicio:%d/%m/%Y %H:%M} a {fim:%d/%m/%Y %H:%M} (Brasília) · {len(users)} mensagens do Pedro · {n_texts} blocos de texto do assistente · {n_tools} chamadas de ferramenta</p></header>
<div id="conversa"></div></main>
<script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js" integrity="sha384-/TQbtLCAerC3jgaim+N78RZSDYV7ryeoBCVqTuzRrFec2akfBkHS7ACQ3PQhvMVi" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/dompurify@3.1.6/dist/purify.min.js" integrity="sha384-+VfUPEb0PdtChMwmBcBmykRMDd+v6D/oFmB3rZM/puCMDYcIvF968OimRh4KQY9a" crossorigin="anonymous"></script>
<script>
const EVENTS = {payload};
const q = new URLSearchParams(location.search);
const de = Number(q.get('de') ?? 0), ate = Number(q.get('ate') ?? EVENTS.length - 1);
if (q.has('print')) document.body.classList.add('clamp');
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));
const md = (s) => window.marked && window.DOMPurify ? DOMPurify.sanitize(marked.parse(s)) : '<pre>' + esc(s) + '</pre>';
const out = [];
EVENTS.forEach((e, i) => {{
  if (i < de || i > ate) return;
  if (e.kind === 'user') out.push(`<div class="ev user" id="e${{i}}"><div class="who">👤 Pedro · ${{e.hora}}${{e.origem !== 'mensagem' ? ' · ' + esc(e.origem) : ''}}</div><div class="bubble">${{esc(e.text)}}</div></div>`);
  else if (e.kind === 'assistant') out.push(`<div class="ev assistant" id="e${{i}}"><div class="who">🤖 Claude · ${{e.hora}}</div><div class="bubble">${{e.parts.map((p) => p.type === 'text' ? md(p.text) : `<ul class="tools">${{p.items.map(([n, d]) => `<li>🔧 <code>${{esc(n)}}</code> — ${{esc(d)}}</li>`).join('')}}</ul>`).join('')}}</div></div>`);
  else out.push(`<div class="ev system" id="e${{i}}"><div class="bubble">⚙️ ${{e.hora}} — ${{esc(e.text)}}</div></div>`);
}});
document.getElementById('conversa').innerHTML = out.join('');
// no modo print, o aviso de corte só aparece no balão que de fato passou do limite
if (document.body.classList.contains('clamp')) document.querySelectorAll('.bubble').forEach((b) => {{ if (b.scrollHeight > b.clientHeight + 2) b.classList.add('cortado'); }});
</script></body></html>
""", encoding="utf-8")

# ------------------------------------------------------------------ subagentes.md
sub_rows, sub_check = [], Counter()
wf_dir = next((p for p in SRC.iterdir() if p.is_dir() and (p / "workflows").exists()), None)
workflows = {}
if wf_dir:
    for f in sorted((wf_dir / "workflows").glob("*.json")):
        w = json.loads(f.read_text(encoding="utf-8"))
        workflows[w["runId"]] = w
    for f in sorted((wf_dir / "subagents").rglob("*.jsonl")):
        if f.name == "journal.jsonl":  # diário do workflow, não é conversa de subagente
            sub_check["diarios_de_workflow"] += 1
            continue
        sub_check["arquivos"] += 1
        m = f.with_suffix(".meta.json")
        mj = json.loads(m.read_text(encoding="utf-8")) if m.exists() else {}
        n_msgs = n_tool = 0
        final = ""
        first_ts = last_ts = None
        for line in f.open(encoding="utf-8"):
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                sub_check["linhas_invalidas"] += 1
                continue
            if o.get("timestamp"):
                first_ts = first_ts or o["timestamp"]
                last_ts = o["timestamp"]
            if o.get("type") == "assistant":
                n_msgs += 1
                for b in o["message"]["content"]:
                    if b.get("type") == "tool_use":
                        n_tool += 1
                        if b["name"] == "StructuredOutput":
                            final = json.dumps(b.get("input", {}), ensure_ascii=False)
                    elif b.get("type") == "text" and b["text"].strip():
                        final = b["text"]
        sub_check["com_resposta_final"] += bool(final)
        sub_rows.append({"workflow": f.parent.name, "arquivo": f.stem, "rotulo": mj.get("description", f.stem), "fase": mj.get("workflowPhase", ""),
                         "inicio": first_ts, "fim": last_ts, "mensagens": n_msgs, "ferramentas": n_tool, "final_chars": len(final)})

sm = ["# Subagentes da conversa (índice)\n",
      "Cada workflow abaixo foi disparado pelo Claude Code dentro da conversa. As conversas dos subagentes estão completas no "
      "zip do export; aqui fica o índice, com o mesmo critério de conferência aplicado a todas (arquivo lido sem erro, "
      "resposta final presente). Horário de Brasília. \"Blocos do assistente\" conta as entradas do assistente no "
      "arquivo (uma por bloco de texto ou chamada de ferramenta), não as mensagens trocadas. Rótulos repetidos são "
      "refutadores de divergências diferentes do mesmo trecho; a coluna do arquivo liga cada linha ao zip.\n"]
for run, w in workflows.items():
    rows = [r for r in sub_rows if r["workflow"] == run]
    # "timestamp" é a hora em que o workflow terminou; o início é startTime (epoch em ms)
    ini = datetime.fromtimestamp(w["startTime"] / 1000, tz=timezone.utc).astimezone(BRT) if w.get("startTime") else hora(w["timestamp"])
    sm.append(f"## {w.get('workflowName') or run} (`{run}`)\n\n{redact(str(w.get('summary', '')))}\n\n"
              f"Início {ini:%d/%m %H:%M} · {w.get('agentCount', len(rows))} agentes · duração {round((w.get('durationMs') or 0) / 60000)} min · "
              f"status {w.get('status', '')}\n")
    for lg in w.get("logs", []) or []:
        sm.append(f"> {redact(str(lg))}\n")
    sm.append("| Agente | Arquivo no zip | Fase | Blocos do assistente | Chamadas de ferramenta | Resposta final (caracteres) |\n|---|---|---|---|---|---|")
    for r in sorted(rows, key=lambda r: r["inicio"] or ""):
        sm.append(f"| {r['rotulo']} | `{r['arquivo']}` | {r['fase']} | {r['mensagens']} | {r['ferramentas']} | {r['final_chars']} |")
    sm.append("")
(OUT / "subagentes.md").write_text("\n".join(sm), encoding="utf-8")

# ------------------------------------------------------------------ checagem.json
md_text = (OUT / "conversa.md").read_text(encoding="utf-8")
faltando_assist = [i for i, t in enumerate(raw_assistant_texts) if redact(t) not in md_text]
faltando_user = [i for i, t in enumerate(raw_user_texts) if md_user(redact(t)) not in md_text]
# As notificações de tarefa trazem a hora em que entraram na fila, não a da entrega: a ordem do arquivo é a da entrega.
conversa_ev = [e for e in events if e["kind"] != "system"]
ordem_ok = all(conversa_ev[i]["ts"] <= conversa_ev[i + 1]["ts"] for i in range(len(conversa_ev) - 1))
segredos_bruto = []
for n_linha, line in enumerate(main.open(encoding="utf-8"), 1):
    k = len(SECRET.findall(line))
    if k:
        segredos_bruto.append({"linha": n_linha, "ocorrencias": k})
grupos = [e for e in events if e["kind"] == "system" and e.get("n", 1) > 1]
saida = "".join((OUT / f).read_text(encoding="utf-8") for f in ("conversa.md", "conversa.html", "conversa.json", "subagentes.md"))
pii = [m.group(0) for m in EMAIL.finditer(saida) if not EMAIL_OK.search(m.group(0))] + PHONE.findall(saida)
mojibake = len(re.findall(r"Ã[\x80-\xbf]|â€", saida))
check = {
    "sessao": meta.get("cliSessionId"), "sessao_app": meta.get("sessionId"), "titulo": meta.get("title"),
    "periodo_brt": [f"{inicio:%d/%m/%Y %H:%M}", f"{fim:%d/%m/%Y %H:%M}"],
    "bruto": dict(raw),
    "exportado": {"mensagens_do_pedro": len(users), "blocos_de_texto_do_assistente": n_texts, "chamadas_de_ferramenta": n_tools,
                  "eventos_de_sistema": sum(e["kind"] == "system" for e in events)},
    "textos_do_assistente_ausentes_ou_alterados": faltando_assist,
    "mensagens_do_pedro_ausentes_ou_alteradas": faltando_user,
    "ferramentas_bruto_igual_exportado": raw["assistant:tool_use"] == n_tools,
    "textos_bruto_igual_exportado": len(raw_assistant_texts) == n_texts,
    "ordem_cronologica_pedro_e_claude": ordem_ok, "ordem_do_arquivo_preservada": True,
    "notificacoes_agrupadas": {"grupos": len(grupos), "notificacoes_nos_grupos": sum(e["n"] for e in grupos)},
    "redacoes": dict(redacoes), "dados_pessoais_na_saida": len(pii), "mojibake_na_saida": mojibake,
    "segredos_no_bruto": segredos_bruto, "segredos_na_saida": len(SECRET.findall(saida)),
    "subagentes": {**dict(sub_check), "workflows": len(workflows),
                   "agentes_declarados": sum(w.get("agentCount", 0) for w in workflows.values())},
}
(OUT / "checagem.json").write_text(json.dumps(check, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(check, ensure_ascii=False, indent=1))
