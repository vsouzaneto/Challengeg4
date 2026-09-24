#!/usr/bin/env python3
"""PreToolUse (Bash): block destructive or rule-breaking shell commands.

Denies force pushes, history rewrites, mass deletes, hook bypass, sudo, piping
remote scripts into a shell, and git operations that would stage files outside
the submission folder or edit the root .gitignore.
"""
import re

from _common import deny, read_payload

payload = read_payload()
cmd = (payload.get("tool_input") or {}).get("command") or ""
flat = " ".join(cmd.split())

RULES = [
    (r"\bgit\b(\s+-C\s+\S+|\s+--git-dir=\S+|\s+--work-tree=\S+|\s+-c\s+\S+)*\s+push\b.*(\s--force\b|\s-f\b|\s--force-with-lease\b|\s\+\S+)", "git push --force (ou refspec com '+') reescreve histórico; o git history é evidência de processo."),
    (r"\bgit\b(\s+-C\s+\S+|\s+-c\s+\S+)*\s+(commit|push)\b.*--no-verify", "--no-verify pula hooks. Corrija a causa em vez de pular."),
    (r"\bgit\b(\s+-C\s+\S+|\s+-c\s+\S+)*\s+reset\s+--hard\b", "git reset --hard descarta trabalho. Use git stash ou um branch."),
    (r"\bgit\s+clean\s+-[a-zA-Z]*f", "git clean -f apaga arquivos não rastreados (a pasta de submissão é ignorada pelo .gitignore da raiz!)."),
    (r"\bgit\s+checkout\s+--\s+\.|\bgit\s+restore\s+\.\s*$", "Descarta todas as alterações locais de uma vez. Restaure arquivos específicos."),
    (r"\bgit\s+rebase\s+-i\b|\bgit\s+filter-branch\b", "Reescrita de histórico não é permitida neste projeto."),
    (r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f?\s+(/|~|\$HOME|\.\.|\*|\.)(\s|$)", "rm -rf em raiz/home/pai/cwd. Aponte para um caminho específico."),
    (r"\bsudo\b", "sudo não é necessário neste projeto."),
    (r"(curl|wget)\b[^|]*\|\s*(ba|z|)sh\b", "Pipe de download direto para shell é inseguro."),
    (r"\bchmod\s+(-R\s+)?777\b", "chmod 777 não é aceitável."),
    (r"\bpip3?\s+install\b", "Use uv (uv add / uv run) para manter o lock reproduzível."),
    (r"\bgit\s+add\b.*(\s-A\b|\s--all\b|\s\.\s*$|\s\.\s)", "git add -A/. pode capturar arquivos fora de submissions/bernardo-couto/ ou lixo. Use tools/git-stage.sh."),
    (r"\bgit\s+add\s+(-f|--force)\b(?!.*pathspec-from-file)", "git add -f direto ignora TODOS os .gitignore (arrasta node_modules/.venv). Use tools/git-stage.sh."),
    (r"(>|>>|tee)\s*\S*(^|/)\.gitignore(\s|$)|\bsed\b.*\.gitignore", "Editar .gitignore da raiz viola a regra do PR. O de dentro da pasta de submissão pode ser editado com Edit/Write."),
    (r"\bkaggle\b.*\b(datasets|competitions)\s+download\b", "Os dados já estão em solution/data/raw (CC0, com checksums). Não é preciso baixar de novo."),
]

for pattern, why in RULES:
    if re.search(pattern, flat):
        deny(f"Bloqueado pelo guardrail do projeto: {why}\nComando: {flat[:200]}")

raise SystemExit(0)
