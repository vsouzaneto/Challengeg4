# Onde a IA errou e como foi corrigido

Cada item traz o que a IA fez, como foi percebido, a correção e a evidência. Itens marcados **(humano)** foram pegos pelo Bernardo; **(verificação)** foram pegos por teste, comando ou revisão cruzada disparada pela própria sessão.

<a id="e1"></a>
## E1 — Regras de permissão com sintaxe não documentada (verificação)
- **O que fez:** primeira versão do `settings.json` usava `Edit(../../.gitignore)` para proteger arquivos da raiz.
- **Como percebeu:** o relatório do `claude-code-guide` não listava caminhos `../` como suportados em regras de permissão.
- **Correção:** regras removidas; proteção movida para o hook `guard_paths.py`, testado com payloads simulados (deny fora da pasta, deny em `data/raw`, allow dentro).
- **Evidência:** decision log 2026-09-22 23:25; chat export, bloco "Simulate hook payloads".

<a id="e2"></a>
## E2 — `git mv -k` silencioso ao renomear agente (verificação)
- **O que fez:** `git mv -k app-engineer.md application-engineer.md || mv …`. Como o arquivo não era rastreado, `-k` ignorou o erro e retornou 0; o `mv` de fallback nunca rodou.
- **Como percebeu:** o `ls` seguinte ainda mostrava `app-engineer.md`.
- **Correção:** `mv` direto e busca por referências residuais com `grep -r`.
- **Evidência:** chat export, blocos "Rename agent files" e "Complete the agent file rename".

<a id="e3"></a>
## E3 — Mensagem do hook de sessão com nome do JDK errado (verificação)
- **O que fez:** `session_start.py` extraía o nome do JDK padrão com `rsplit` e imprimia "JavaVirtualMachines" em vez de "openjdk-23.0.1".
- **Como percebeu:** saída do teste do hook.
- **Correção:** parsing pelo segmento após `/JavaVirtualMachines/`; saída verificada.
- **Evidência:** chat export, bloco "Fix session hook JDK message".

<a id="e4"></a>
## E4 — Achados do dataset tratados como diferencial (verificação)
- **O que fez:** CLAUDE.md e a rubrica interna apresentavam "68% sem conta, GTXPro, 14 vs 57 dias" como diferenciais da entrega.
- **Como percebeu:** revisão crítica com o `g4-evaluator` em mente: são achados que qualquer análise cuidadosa produz; o diferencial é o que se faz com eles (backtest com baselines, testes anti-leakage, as-of na UI).
- **Correção:** seção "O que é baseline e o que é diferencial" no CLAUDE.md; rubrica recalibrada.
- **Evidência:** decision log 2026-09-23 00:40.

<a id="e5"></a>
## E5 — Diagrama de arquitetura em ASCII ilegível (humano)
- **O que fez:** visão geral em caixas ASCII em `docs/solution-architecture.md`.
- **Como percebeu:** o Bernardo apontou que estava ruim.
- **Correção:** todos os diagramas em Mermaid; regra "sempre Mermaid" no CLAUDE.md, na skill `api-documentation` e no `/pr-check`.
- **Evidência:** `docs/solution-architecture.md`.

<a id="e6"></a>
## E6 — Streamlit escolhido cedo demais (humano)
- **O que fez:** a arquitetura inicial assumiu Streamlit por rapidez, sem API nem design system.
- **Como percebeu:** o Bernardo definiu Python + React, Docker, Swagger e documentação navegável.
- **Correção:** ADR 0002 (FastAPI + React), agentes `backend-engineer` e `application-engineer` reescritos, skill `api-documentation`.
- **Evidência:** decision log 2026-09-23 10:30.

<a id="e7"></a>
## E7 — Script de staging que arrastava 45 mil arquivos (verificação)
- **O que fez:** primeira versão de `tools/git-stage.sh` fazia `git add -f` na pasta inteira e depois tentava remover o que o `.gitignore` local listava, arquivo a arquivo. Resultado: 45.236 arquivos no índice (node_modules, .venv) e execução travada por minutos.
- **Como percebeu:** timeout do comando e `git diff --cached | wc -l` no índice.
- **Correção:** processo interrompido, índice zerado, script reescrito para listar os não-rastreados com exclusões explícitas e forçar só essa lista (`--pathspec-from-file`). Nova execução: 155 arquivos em 0,1 s, com validação automática de "gerados = 0" e "fora da pasta = 0". Hook `guard_bash.py` passou a bloquear `git add -f` direto.
- **Evidência:** chat export (blocos "safe git staging script"); `tools/git-stage.sh`.

<a id="e10"></a>
## E10 — Premissas de scoring escritas antes do backtest (verificação)
- **O que fez:** a skill afirmava que idade em Engaging era sinal positivo até ~90 dias e que "mais novo primeiro" seria um baseline forte.
- **Como percebeu:** backtest temporal do `data-scientist` (dois cortes, ICs por bootstrap): idade não discrimina entre deals vivos (AUC-ROC 0,50); "mais novo primeiro" só ganha quando censurados contam como Lost. Sete de onze hipóteses registradas antes da análise foram refutadas.
- **Correção:** skills reescritas; p_win reduzido à taxa-base por produto; sinais sem poder preditivo viraram reason codes informativos; posicionamento do produto mudou para "valor × timing + higiene".
- **Evidência:** `solution/pipeline/analysis/00_hypotheses.md`, `docs/figures/10_backtest.md`, decision log 2026-09-23 14:30.

<a id="e8"></a>
## E8 — Objeção técnica registrada e decidida pelo humano (não é erro, é julgamento)
- **O que fez:** questionou Spark para 8.800 linhas.
- **Resolução:** o Bernardo manteve Spark como decisão de arquitetura (pipeline reexecutável, escalável); a IA documentou a justificativa honesta em vez de vender como necessidade de escala (ADR 0001).
