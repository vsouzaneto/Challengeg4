# Exports de conversa

Ao fim de cada sessão de trabalho no Claude Code, rode `/export` e salve aqui como `AAAA-MM-DD-claude-code-<tema>.txt`. O `/export` grava a conversa em texto puro.

Antes de versionar, rode a limpeza (a mesma para os exports finais):

```bash
node tools/limpar-exports.mjs --saida /tmp/exports-limpos process-log/chat-exports/*.txt   # confira com diff -u
node tools/limpar-exports.mjs process-log/chat-exports/*.txt                               # aplica no lugar
```

O que foi coberto nos exports de 09/10/2026 (D52), com o diff aprovado pelo Bruno:
- `/Users/<usuário>/` → `~/` (40 caminhos);
- caminhos temporários do Claude, com o ID da sessão → `[removido]` (6);
- a pasta do ai-memory → `[removido]` (4);
- o nome da organização → `[removido]` (1); os termos privados ficam em `tools/.termos-privados`, fora do git;
- o trecho do `~/.claude/settings.json` mostrado na sessão 1 → `[configuração pessoal removida]` (1).

Conferido e mantido: nenhuma chave ou token com valor; os nomes de variáveis do hook do Orca (`ORCA_AGENT_HOOK_TOKEN`, sem valor) e o script em base64 do mesmo hook, decodificado e sem segredo; nenhum e-mail.
