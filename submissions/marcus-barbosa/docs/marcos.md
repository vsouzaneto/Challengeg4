# Marcos do projeto — Challenge 003 Lead Scorer

Definição de pronto: **todos os marcos abaixo em `[x]`**, banca de agentes revisores com nota 100/100 em cada entregável, e revisor final "impressionado". Cada marco tem critério de aceite verificável e a fonte de onde a exigência veio. Estado em 2026-09-21, após a auditoria adversarial.

Legenda de fonte: `C003` = README do challenge · `GUIA` = submission-guide.md · `TPL` = template de submissão · `CONTRIB` = CONTRIBUTING.md · `ROOT` = README raiz · `REV` = rubrica real extraída das reviews públicas (`docs/rubrica-do-avaliador.md`) · `VAGA` = descrição oficial da vaga · `MB` = exigência do Marcus.

## A. Solução funcional (obrigatório)

| ID | Marco | Fonte | Critério de aceite | Status |
|---|---|---|---|---|
| A1 | Roda seguindo as instruções, sem chave de API | C003, REV | `99_clean_env_check.ps1` em venv novo: instalação, 24 testes, scripts e health check do app; log em `docs/clean_env_check.log` | [x] |
| A2 | Usa os 4 CSVs reais do Kaggle | C003, REV | SHA-256, bytes e linhas de cada arquivo em `docs/data_health_report.md` (8.800 oportunidades, 85 contas, 7 produtos, 35 vendedores) | [x] |
| A3 | Lógica de scoring que não é "ordenar por valor" | C003 | chance por faixa de idade (37% / 40% / 18% / 1%) × preço; correlação score × preço 0,74; o mesmo preço recebe scores diferentes conforme a idade (teste) | [x] |
| A4 | Vendedor entende por quê | C003, REV | explicação por deal com chance, intervalo, n, valor, percentil e próximo passo | [x] |
| A5 | Interface ajuda a decidir, não só mostra dados | C003 | seis blocos de ação com regra de precedência e pauta de segunda-feira com no máximo 7 itens | [x] |
| A6 | Filtro por vendedor / manager / região (bonus) | C003 | três filtros e presets por URL; visão de gerente e de RevOps | [x] |
| A7 | Código limpo para manutenção | C003 | `leadscorer/` com módulos data, audit, calibration, scoring, backtest, brief, manager; funções puras; docstrings com a hipótese por regra | [x] |
| A8 | Testes automatizados de invariantes | REV | 24 testes: faixa, determinismo, vendedor/setor/conta não mudam o score, anti-leakage, base truncada = base completa, janela limpa, agrupamento de faixas, intervalo por deal, categorias, brief, gerente | [x] |
| A9 | Backtest do score contra o histórico | REV | `docs/backtest.md`: walk-forward em 4 datas (2 principais sem sobreposição), prevista vs. observada por faixa, captura de valor com três comparadores, com o que não sustenta dito | [x] |
| A10 | Deploy público (não bloqueador, diferencial) | REV | não feito; app local com um comando, capturas em `process-log/screenshots/app/` | [ ] |

## B. Documentação mínima (obrigatório)

| ID | Marco | Fonte | Critério de aceite | Status |
|---|---|---|---|---|
| B1 | Setup: como rodar | C003, CONTRIB | README "Como rodar", comandos multiplataforma, validado em ambiente limpo | [x] |
| B2 | Lógica: critérios e por quê | C003 | tabela no README e `docs/methodology.md` §4-5 | [x] |
| B3 | Limitações: o que não faz e o que precisa para escalar | C003, GUIA | README "Limitações" e `methodology.md` §9 | [x] |
| B4 | 2–3 sanity checks visíveis | REV | contagem por bloco, calibração com intervalo e n, backtest no app (RevOps) e nos docs | [x] |
| B5 | Executive summary de 1 parágrafo, achados com número | GUIA, TPL, VAGA | README | [x] |
| B6 | Recomendações priorizadas para a Head de RevOps | GUIA, TPL | seis recomendações ordenadas com número, mais piloto com gate | [x] |

## C. Process log (obrigatório, eliminatório)

| ID | Marco | Fonte | Critério de aceite | Status |
|---|---|---|---|---|
| C1 | Ferramentas de IA usadas e para quê | GUIA, TPL | tabela no README | [x] |
| C2 | Decomposição do problema antes de promptar | GUIA, REV | 27 hipóteses com veredito e número em `hypotheses.md`; origem IA declarada, regra do método do Marcus | [x] |
| C3 | Onde a IA errou e como foi corrigido | GUIA, TPL, REV | 7 erros em `ai-errors.md`, cada um com detecção, causa raiz e correção | [x] |
| C4 | O que o humano adicionou que a IA sozinha não faria | GUIA, TPL, VAGA | seção no README e ledger com 24 decisões e origem | [x] |
| C5 | Quantas iterações foram necessárias | GUIA | `workflow.md` com 6 iterações numeradas | [x] |
| C6 | Baselines "brief colado na IA" documentados | ROOT, REV | `baselines/` com 3 variantes e síntese | [x] |
| C7 | Rubrica de diferenciação escrita antes de codar | REV | `differentiation-rubric.md` com status final por item | [x] |
| C8 | Auditoria adversarial por agente independente | REV | `critique-synthesis.md`: 46 achados, 45 verificados sobre o código corrigido, estado e correção por item | [x] |
| C9 | Setup do Claude Code com humano no loop | REV | registrado no README e no process-log/README | [x] |

## D. Evidências

| ID | Marco | Fonte | Critério de aceite | Status |
|---|---|---|---|---|
| D1 | Screenshots das sessões com a IA | GUIA, REV | `process-log/screenshots/sessoes/` (capturas da janela do Claude Code, barra lateral recortada) | [x] |
| D2 | Screenshots do app rodando | REV | 6 capturas em `process-log/screenshots/app/` | [x] |
| D3 | Chat export em texto dentro do repo | GUIA, REV | `process-log/chat-exports/transcript-sessao.md` (1.028 mensagens, token e e-mail removidos) | [x] |
| D4 | Git history incremental com autoria do candidato | GUIA, REV | commits semânticos, author Marcus Barbosa, trailer Co-Authored-By declarando a IA | [x] |
| D5 | Screen recording (opcional) | GUIA | não feito | [ ] |

## E. Estrutura e regras do PR

| ID | Marco | Fonte | Critério de aceite | Status |
|---|---|---|---|---|
| E1 | Fork + branch `submission/marcus-barbosa` | CONTRIB | existe em `marcusbarbosa92/ai-master-challenge` | [x] |
| E2 | Pasta `submissions/marcus-barbosa/` (plural) com `solution/`, `process-log/`, `docs/` | CONTRIB, REV | estrutura presente | [x] |
| E3 | README segue o template oficial, todas as seções preenchidas | CONTRIB, TPL, REV | todas as seções preenchidas, LinkedIn incluído | [x] |
| E4 | Nenhum arquivo fora da pasta modificado | CONTRIB, REV | `05_check_repo.py` confere `git diff upstream/main` | [x] |
| E5 | Sem node_modules / venv / dados brutos / .pkl no PR | REV | `05_check_repo.py` confere `git ls-files` | [x] |
| E6 | Título do PR `[Submission] Marcus Barbosa — Challenge 003` | CONTRIB | ao abrir o PR | [ ] |
| E7 | Inscrição na vaga no ATS feita pelo Marcus | VAGA, REV | confirmação do Marcus | [ ] |

## F. Qualidade final (definição de pronto do Marcus)

| ID | Marco | Fonte | Critério de aceite | Status |
|---|---|---|---|---|
| F1 | Banca de agentes revisores com a rubrica real dá 100/100 em cada entregável (A–E) | MB, REV | `docs/banca-final.md` | [ ] |
| F2 | Revisor final independente declara-se impressionado | MB | parecer em `docs/banca-final.md` | [ ] |
| F3 | Supera substancialmente os baselines | ROOT | status por item em `differentiation-rubric.md` | [x] |
| F4 | Tudo explicável: metodologia documentada de ponta a ponta | MB, VAGA | `docs/methodology.md` | [x] |
| F5 | Papel do Marcus vs. papel da IA explícito | VAGA, TPL | seção no README com ledger contado | [x] |
