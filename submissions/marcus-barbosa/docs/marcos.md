# Marcos do projeto — Challenge 003 Lead Scorer

Definição de pronto: **todos os marcos abaixo em `[x]`**, banca de agentes revisores com nota 100/100 em cada entregável, e revisor final "impressionado". Cada marco tem critério de aceite verificável e a fonte de onde a exigência veio.

Legenda de fonte: `C003` = README do challenge · `GUIA` = submission-guide.md · `TPL` = template de submissão · `CONTRIB` = CONTRIBUTING.md · `ROOT` = README raiz · `REV` = rubrica real extraída das 176 reviews públicas · `VAGA` = descrição oficial da vaga · `MB` = exigência do Marcus.

## A. Solução funcional (obrigatório)

| ID | Marco | Fonte | Critério de aceite | Status |
|---|---|---|---|---|
| A1 | Roda seguindo as instruções, sem chave de API | C003, REV | `pip install -r requirements.txt && streamlit run app.py` em máquina limpa; LLM opcional com saída pré-gerada em cache | [ ] |
| A2 | Usa os 4 CSVs reais do Kaggle | C003, REV | Script de download + hash/contagem de linhas (8.800 oportunidades, 85 contas, 7 produtos, 35 vendedores) registrados | [ ] |
| A3 | Lógica de scoring que não é "ordenar por valor" | C003 | Score 0–100 com ≥4 fatores nomeados, cada um derivado de evidência do dataset | [ ] |
| A4 | Vendedor entende por quê | C003, REV | Breakdown por fator em português, com frase por fator e ação recomendada por deal | [ ] |
| A5 | Interface ajuda a decidir, não só mostra dados | C003 | Categorias de ação (Focar agora / Follow-up / Reengajar / Qualificar ou descartar) e "brief de segunda-feira" por vendedor | [ ] |
| A6 | Filtro por vendedor / manager / região (bonus) | C003 | Três filtros funcionais + visão de manager | [ ] |
| A7 | Código limpo para manutenção | C003 | Módulos separados (dados / scoring / app), funções puras testadas, docstrings | [ ] |
| A8 | Testes automatizados de invariantes | REV | `pytest` verde: score ∈ [0,100], determinístico, deal sem conta recebe score, alterar `close_value`/`close_date` de deal aberto não muda score, GTXPro normalizado, ref_date = max(close_date), win rate = Won/(Won+Lost) | [ ] |
| A9 | Backtest do score contra Won/Lost histórico | REV | Win rate monotônico por faixa de score, com corte temporal, tabela no README | [ ] |
| A10 | Deploy público (não bloqueador, diferencial) | REV | URL no Streamlit Cloud respondendo, screenshot | [ ] |

## B. Documentação mínima (obrigatório)

| ID | Marco | Fonte | Critério de aceite | Status |
|---|---|---|---|---|
| B1 | Setup: como rodar | C003, CONTRIB | Seção no README com dependências, comandos, URL; testada em ambiente limpo | [ ] |
| B2 | Lógica: critérios e por quê | C003 | Tabela fator → peso → evidência no dado → por que esse peso | [ ] |
| B3 | Limitações: o que não faz e o que precisa para escalar | C003, GUIA | Seção explícita com limites do dado, do modelo e do produto | [ ] |
| B4 | 2–3 sanity checks visíveis | REV | Distribuição do score, exemplos por faixa, top deals com breakdown | [ ] |
| B5 | Executive summary de 1 parágrafo, achados com número | GUIA, TPL, VAGA | Um C-level lê e decide em 5 minutos | [ ] |
| B6 | Recomendações priorizadas para a Head de RevOps | GUIA, TPL | Lista ordenada com impacto estimado e premissas declaradas | [ ] |

## C. Process log (obrigatório, eliminatório)

| ID | Marco | Fonte | Critério de aceite | Status |
|---|---|---|---|---|
| C1 | Ferramentas de IA usadas e para quê | GUIA, TPL | Tabela preenchida no README | [ ] |
| C2 | Decomposição do problema antes de promptar | GUIA, REV | `hypotheses.md` com hipóteses do Marcus escritas antes de olhar os dados, e resultado (confirmada / refutada, com número) | [ ] |
| C3 | Onde a IA errou e como foi corrigido | GUIA, TPL, REV | `ai-errors.md` com ≥5 erros reais, cada um com detecção, causa raiz e correção | [ ] |
| C4 | O que o humano adicionou que a IA sozinha não faria | GUIA, TPL, VAGA | `decisions.md` com ledger "decisão do Marcus / consenso / sugestão da IA" e contagem | [ ] |
| C5 | Quantas iterações foram necessárias | GUIA | `workflow.md` cronológico com iterações numeradas | [ ] |
| C6 | Baselines "brief colado na IA" documentados | ROOT, REV | `baselines/` com prompt usado + saída bruta de 3 variantes + síntese do que é comum | [ ] |
| C7 | Rubrica de diferenciação escrita antes de codar | REV | `differentiation-rubric.md` com diferenciadores mensuráveis vs. baselines | [ ] |
| C8 | Auditoria adversarial por agente independente | REV | `critique-synthesis.md` com o que caiu e o que foi corrigido | [ ] |
| C9 | Setup do Claude Code com humano no loop | REV | Registro de que a edição automática ficou desligada e de que cada mudança foi revisada | [ ] |

## D. Evidências

| ID | Marco | Fonte | Critério de aceite | Status |
|---|---|---|---|---|
| D1 | Screenshots das sessões com a IA (não só do app) | GUIA, REV | ≥10 capturas em `process-log/screenshots/` cobrindo o arco do trabalho | [ ] |
| D2 | Screenshots do app rodando | REV | ≥5 capturas (brief, pipeline, breakdown, manager, filtros) | [ ] |
| D3 | Chat export em texto dentro do repo | GUIA, REV | Transcript exportado em Markdown/JSONL em `process-log/chat-exports/` | [ ] |
| D4 | Git history incremental com autoria do candidato | GUIA, REV | ≥10 commits semânticos, author "Marcus Barbosa", ordem real do trabalho | [ ] |
| D5 | Screen recording (opcional) | GUIA | Link ou arquivo curto do app em uso | [ ] |

## E. Estrutura e regras do PR

| ID | Marco | Fonte | Critério de aceite | Status |
|---|---|---|---|---|
| E1 | Fork + branch `submission/marcus-barbosa` | CONTRIB | Existe em `marcusbarbosa92/ai-master-challenge` | [x] |
| E2 | Pasta `submissions/marcus-barbosa/` (plural) com `solution/`, `process-log/`, `docs/` | CONTRIB, REV | Estrutura presente | [x] |
| E3 | README segue o template oficial, todas as seções preenchidas | CONTRIB, TPL, REV | Nenhum placeholder do template sobrando | [ ] |
| E4 | Nenhum arquivo fora da pasta modificado | CONTRIB, REV | `git diff upstream/main --stat` só lista `submissions/marcus-barbosa/` | [ ] |
| E5 | Sem node_modules / venv / dados brutos / .pkl no PR | REV | `git ls-files` da pasta inspecionado antes do push | [ ] |
| E6 | Título do PR `[Submission] Marcus Barbosa — Challenge 003` | CONTRIB | Conferido no PR | [ ] |
| E7 | Inscrição na vaga no ATS feita pelo Marcus | VAGA, REV | Confirmação do Marcus | [ ] |

## F. Qualidade final (definição de pronto do Marcus)

| ID | Marco | Fonte | Critério de aceite | Status |
|---|---|---|---|---|
| F1 | Banca de agentes revisores com a rubrica real dá 100/100 em cada entregável (A–E) | MB, REV | Workflow de revisão executado; nenhum item abaixo de 100; achados corrigidos e re-avaliados | [ ] |
| F2 | Revisor final independente declara-se impressionado | MB | Parecer final registrado em `docs/banca-final.md` | [ ] |
| F3 | Supera substancialmente os baselines | ROOT | Cada diferenciador da rubrica C7 comprovado com evidência | [ ] |
