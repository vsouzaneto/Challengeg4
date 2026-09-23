# Sessão 5 — Entrega 2: proposta de automação

> Export da sessão do Claude Code (app desktop), de 23/09/2026 12:01 a 23/09/2026 12:20 (UTC). Conversão para leitura: ficam os prompts do Rafael, as respostas da IA, as perguntas de múltipla escolha com a resposta escolhida e uma linha por ação da IA. Foram removidos o raciocínio interno, a saída bruta das ferramentas, os lembretes de sistema, e-mails e chaves.


---

### 👤 Rafael

lembre-se do contexto "Você é o novo AI Master da área de Suporte ao Cliente de uma empresa de tecnologia. A operação atende ~30.000 tickets por ano via email, chat, telefone e redes sociais. O time está sobrecarregado, o tempo de resolução subiu, e a satisfação do cliente caiu.

O Diretor de Operações te chamou e disse:

"Quero que você olhe nossos dados de suporte e me diga três coisas: onde estamos perdendo tempo, o que pode ser automatizado com IA, e me mostre que funciona — não quero só um PowerPoint. Quero ver algo rodando."

Vamos dar continuidade no desafio fazendo o:

"2. Proposta de automação com IA (obrigatório)
Com base em ambos os datasets, proponha:

O que automatizar — Classificação automática, roteamento inteligente, respostas sugeridas, triagem de prioridade, detecção de duplicatas — o que fizer sentido com base nos dados.
O que NÃO automatizar — Nem tudo deve ser delegado para IA. Quais tipos de ticket exigem julgamento humano? Justifique com exemplos dos dados.
Como funcionaria na prática — Descreva o fluxo proposto: ticket entra → o que acontece em cada etapa → onde IA atua → onde humano intervém."

Estamos dando continuidade apos terminar a fase 1, caso seja necessario e o desafio peça explicitamente, use dados da fase 1.

Aqui vamos decidir o que automatizar ou não, o que da pra ser determinístico e o que da pra ser probalistico com a LLM, importante justificar com embasamento a melhor decisão, se foi por custo, por hora, por impacto x esforço, ou outra coisa.

E de exemplos como pediu.

- `Bash`: List commits and repo files

### 🤖 Claude

Phase 1 is in commit b5b88b9 on another branch. Let me look at it.

- `Bash`: Inspect phase 1 commit and challenge README

- `Bash`: Read phase 1 README, log and diagnosis

- `Read`: C:\Users\Rafael\.claude\projects\C--G4--claude-worktrees-support-ai-automation-proposal-e60717\e1704de9-08a1-4335-ab2e-e29a6c7aa087\tool-results\bfy014edz.txt

- `Bash`: Read root cause doc and triage script

- `Bash`: Locate worktrees, datasets and Python env

- `Bash`: Fast-forward to phase 1 branch and copy datasets

### 🤖 Claude

Trouxe a Fase 1 (branch `submission/rafael-bateli`) para esta worktree e copiei os datasets. Agora vou explorar os textos dos dois datasets para embasar cada decisão de automação com números.

- `Bash`: Explore Dataset 1 subjects and sentence templates

- `Bash`: Inspect description structure

- `Skill`: claude-api

- `Bash`: Identify closing sentence templates

- `Bash`: Explore Dataset 2 and phase 1 triage output

- `Bash`: Measure keyword-rule classifier on Dataset 2

- `Bash`: Confusion, near-duplicates and sensitive HR terms in Dataset 2

- `Bash`: Check repeat customers, purchase dates, alerts

- `Bash`: Inspect phase 1 results and extra keyword counts

- `Write`: C:\G4\.claude\worktrees\support-ai-automation-proposal-e60717\submissions\rafael-bateli\solution\automacao\automacao.py

- `Bash`: Run automation proposal script

### 🤖 Claude

Corrigindo um erro de serialização no script (chave de tabela cruzada) e rodando de novo.

- `Edit`: C:\G4\.claude\worktrees\support-ai-automation-proposal-e60717\submissions\rafael-bateli\solution\automacao\automacao.py

- `Bash`: Rerun automation script

- `Bash`: Show cost, impact and verification output

- `Edit`: C:\G4\.claude\worktrees\support-ai-automation-proposal-e60717\submissions\rafael-bateli\solution\automacao\automacao.py

- `Edit`: C:\G4\.claude\worktrees\support-ai-automation-proposal-e60717\submissions\rafael-bateli\solution\automacao\automacao.py

- `Bash`: Rerun and summarize routes and checks

### 🤖 Claude

Rotas fechadas: 33% humano decide, 12% copiloto, 55% coleta automática. Todas as 5 verificações passam. Agora vou puxar exemplos reais (Ticket ID + texto) para cada rota.

- `Bash`: Sample real ticket examples per route

- `Bash`: Print Dataset 2 examples for human-only cases

### 🤖 Claude

Exemplos coletados. Vou conferir os 3 gráficos gerados antes de escrever o documento.

- `Read`: C:\G4\.claude\worktrees\support-ai-automation-proposal-e60717\submissions\rafael-bateli\solution\automacao\outputs\07_regras_vs_modelo.png

- `Read`: C:\G4\.claude\worktrees\support-ai-automation-proposal-e60717\submissions\rafael-bateli\solution\automacao\outputs\08_rotas.png

- `Read`: C:\G4\.claude\worktrees\support-ai-automation-proposal-e60717\submissions\rafael-bateli\solution\automacao\outputs\09_impacto_esforco.png

- `Bash`: Fix chart layouts and rerun

### 🤖 Claude

A substituição em lote falhou antes de gravar (escape do `\n`). O arquivo não mudou. Vou aplicar as mesmas correções com o Edit.

- `Edit`: C:\G4\.claude\worktrees\support-ai-automation-proposal-e60717\submissions\rafael-bateli\solution\automacao\automacao.py

- `Edit`: C:\G4\.claude\worktrees\support-ai-automation-proposal-e60717\submissions\rafael-bateli\solution\automacao\automacao.py

- `Edit`: C:\G4\.claude\worktrees\support-ai-automation-proposal-e60717\submissions\rafael-bateli\solution\automacao\automacao.py

- `Edit`: C:\G4\.claude\worktrees\support-ai-automation-proposal-e60717\submissions\rafael-bateli\solution\automacao\automacao.py

- `Edit`: C:\G4\.claude\worktrees\support-ai-automation-proposal-e60717\submissions\rafael-bateli\solution\automacao\automacao.py

- `Bash`: Rerun script after chart fixes

- `Read`: C:\G4\.claude\worktrees\support-ai-automation-proposal-e60717\submissions\rafael-bateli\solution\automacao\outputs\09_impacto_esforco.png

- `Read`: C:\G4\.claude\worktrees\support-ai-automation-proposal-e60717\submissions\rafael-bateli\solution\automacao\outputs\08_rotas.png

- `Read`: C:\G4\.claude\worktrees\support-ai-automation-proposal-e60717\submissions\rafael-bateli\solution\automacao\outputs\07_regras_vs_modelo.png

- `Bash`: Nudge annotation and rerun

### 🤖 Claude

Gráficos corrigidos e verificações passando. Agora escrevo o documento principal da proposta.

- `Bash`: Remove unused import and read final cost numbers

- `Write`: C:\G4\.claude\worktrees\support-ai-automation-proposal-e60717\submissions\rafael-bateli\solution\automacao\PROPOSTA_AUTOMACAO.md

- `Bash`: Verify union counts and phase 1 priority of cited tickets

- `Bash`: Show phase 1 suggested priority for ticket 7971

- `Edit`: C:\G4\.claude\worktrees\support-ai-automation-proposal-e60717\submissions\rafael-bateli\solution\automacao\automacao.py

- `Edit`: C:\G4\.claude\worktrees\support-ai-automation-proposal-e60717\submissions\rafael-bateli\solution\automacao\automacao.py

- `Edit`: C:\G4\.claude\worktrees\support-ai-automation-proposal-e60717\submissions\rafael-bateli\solution\automacao\automacao.py

- `Edit`: C:\G4\.claude\worktrees\support-ai-automation-proposal-e60717\submissions\rafael-bateli\solution\automacao\automacao.py

- `Bash`: Rerun with latency and union metrics

### 🤖 Claude

Now the doc edits.

- `Bash`: Apply number and diagram fixes to proposal

- `Bash`: Fix section reference and wording

### 🤖 Claude

Vou validar que o diagrama Mermaid renderiza, abrindo-o no navegador embutido.

- `Bash`: Extract mermaid diagram into test HTML

- `mcp__Claude_Browser__preview_start`: file:///C:/Users/Rafael/AppData/Local/Temp/claude/C--G4--claude-worktrees-support-ai-automation-proposal-e60717/e1704de9-08a1-4335-ab2e-e29a6c7aa087/scratchpad/

- `mcp__Claude_Browser__computer`: 

- `Bash`: Convert mermaid edge labels to pipe syntax

- `Bash`: Show current mermaid block

### 🤖 Claude

O diagrama já foi gravado com a sintaxe nova (o erro foi só no `print` do console). Agora escrevo o process log da Entrega 2 e atualizo o README da submissão.

- `Write`: C:\G4\.claude\worktrees\support-ai-automation-proposal-e60717\submissions\rafael-bateli\process-log\02-proposta-automacao.md

### 🤖 Claude

Now the README.

- `Bash`: Update submission README for delivery 2

- `Bash`: Review recommendations section

- `Bash`: Merge overlapping roadmap steps in README

- `Bash`: Show untracked files and output sizes

- `Bash`: Find which ignore rule hides new files

- `Bash`: Trim CSV text and final rerun

### 🤖 Claude

A Entrega 2 está pronta: o documento da proposta, um script que gera todos os números e o process log. O script roda do início ao fim e as 5 verificações passam. Ainda não commitei nada. A raiz do repositório ignora `submissions/` (a Fase 1 entrou com `git add -f`), então os arquivos novos precisam do `-f` quando você quiser commitar.

## A proposta em uma frase

O custo do token não decide nada: toda a LLM da proposta custa cerca de **R$ 270/ano**, o equivalente a 8 horas de agente. O que decide é **o tipo de entrada e o custo do erro**.

Isso vira quatro perguntas, nesta ordem:

| Pergunta | Se sim | Número que sustenta |
|---|---|---|
| O erro é caro ou irreversível? | Humano decide, a IA só prepara | 33% dos tickets: perda de dados, segurança, dinheiro, recontato, hardware |
| A regra pode ser escrita por inteiro? | Determinístico | 149 alertas de máquina idênticos caíram em 5 filas diferentes; uma regra resolve |
| É texto livre com rótulo fechado? | Modelo supervisionado | Regras de palavra-chave param em 80% de acerto; o modelo chega a 98% na mesma fatia de tickets |
| A saída é texto aberto? | LLM, com humano aprovando | Respostas sugeridas e resumo do ticket para o agente |

## O que os dados mudaram

- **O que automatizar:** três regras fixas, sem IA, entregam **40% do ganho em 2 semanas**: lembrete e fechamento de pendentes, resposta automática que pede os dados que faltam, e prioridade por sinais de risco. O total das seis frentes é **cerca de 3.470 h/ano (R$ 122 mil)**. A maior automação virou **coleta de dados**, e não "a IA resolve", porque 69% dos tickets só dizem "estou com problema no {produto}".
- **O que NÃO automatizar**, cada caso com um ticket real: perda de dados (#7971, hoje marcado como *Medium*), conta bloqueada (#1711), reembolso (#3011), cliente que já reclamou várias vezes (#7000) e reparo de hardware (#7019). No Dataset 2 entram permissão de administrador (a IA acerta só 80% ali) e RH com dado de salário, licença ou desligamento.
- **Automações "óbvias" que os dados derrubam:**
  - Mandar o link de redefinição de senha: 186 clientes dizem que a redefinição não funciona.
  - Mandar o roteiro básico de suporte: 34% dos clientes já fizeram tudo isso.
  - Deduplicar por e-mail: todos os e-mails repetidos são de pessoas diferentes.
- **Como funciona na prática:** um fluxograma com 7 etapas e 3 rotas, a tabela "onde o humano entra" em cada etapa, e três tickets reais atravessando o fluxo. Há também um critério para uma automação ganhar mais autonomia; os tickets de risco nunca sobem de nível.

## O que não está medido

- **A acurácia da LLM não foi medida.** Não há chave de API neste ambiente. Por isso toda LLM da proposta começa com humano aprovando, e o protótipo (Entrega 3) é o lugar de medir.
- **O esforço em semanas é premissa**, assim como os 50% de recontato evitado pela detecção de duplicatas.
- **O fluxograma não foi visualizado.** O navegador embutido não abre arquivo local, e não mandei o diagrama para um serviço externo. Usei a sintaxe mais segura do Mermaid, mas vale conferir no GitHub.

Posso commitar e abrir o PR, ou seguir para o protótipo da Entrega 3.

Arquivos:
- [PROPOSTA_AUTOMACAO.md](submissions/rafael-bateli/solution/automacao/PROPOSTA_AUTOMACAO.md)
- [automacao.py](submissions/rafael-bateli/solution/automacao/automacao.py)
- [02-proposta-automacao.md](submissions/rafael-bateli/process-log/02-proposta-automacao.md)
- [README.md](submissions/rafael-bateli/README.md) (atualizado)

