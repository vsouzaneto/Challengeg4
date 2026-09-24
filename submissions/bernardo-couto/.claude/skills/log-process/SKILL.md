---
name: log-process
description: Registra uma entrada datada no process log da submissão (`process-log/decisions.md`) — decisão tomada, alternativas, erro da IA corrigido ou insight humano. Use ao concluir qualquer decisão não óbvia, ao corrigir um erro da IA ou quando o Bernardo pedir `/log-process <resumo>`.
argument-hint: "[tipo: decisao|erro-ia|insight|marco] <resumo curto>"
allowed-tools: Read, Edit, Write, Bash(git log *), Bash(git status *), Bash(date *)
---

Registre uma entrada em `${CLAUDE_PROJECT_DIR}/process-log/decisions.md` (crie o arquivo com o cabeçalho abaixo se não existir).

Argumentos recebidos: `$ARGUMENTS`

Contexto atual do git (para referenciar commits):
!`git -C "${CLAUDE_PROJECT_DIR}" log --oneline -5 2>/dev/null || echo "(sem commits ainda)"`

## Formato da entrada (append no final do arquivo)

```markdown
## [YYYY-MM-DD HH:MM] <tipo> — <título curto>

**Contexto:** o que estava sendo feito e por quê.
**O que a IA propôs / fez:** literal quando relevante (prompt ou trecho).
**O que estava errado ou incompleto:** (obrigatório para tipo `erro-ia`; "n/a" caso contrário).
**Decisão humana:** o que o Bernardo decidiu e o julgamento por trás.
**Alternativas descartadas:** e por quê.
**Evidência:** arquivo:linha, commit, saída de comando ou screenshot em `process-log/screenshots/`.
**Impacto na entrega:** o que mudou no produto/docs por causa disso.
```

Cabeçalho do arquivo, se novo:

```markdown
# Decision log — Lead Scorer (Challenge 003)

Registro cronológico de decisões, erros da IA corrigidos e insights humanos. Cada entrada aponta para evidência verificável. Este arquivo alimenta as seções "Onde a IA errou e como corrigi" e "O que eu adicionei que a IA sozinha não faria" do README da submissão.
```

## Regras

- Use a data/hora real (`date "+%Y-%m-%d %H:%M"`). Nunca invente evidência; se não houver, escreva "evidência pendente: <o que falta>".
- Entradas do tipo `erro-ia` devem citar o que a IA disse **e** o que os dados/código mostraram.
- Uma entrada por decisão. Curta: 8–15 linhas. Se o Bernardo deu o resumo em `$ARGUMENTS`, preserve as palavras dele na "Decisão humana".
- Não edite entradas anteriores; se algo mudou, adicione uma nova entrada referenciando a antiga.
