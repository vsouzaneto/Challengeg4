# Workflow cronológico

## Iteração 0 — 2026-09-21 — Entendimento e blindagem
1. Clone do repositório e leitura integral dos 11 arquivos.
2. Auditoria de segurança (unicode invisível, injeção de prompt, hooks, histórico, branch alternativo): nada malicioso.
3. Coleta das 176 reviews públicas do avaliador nos 100 PRs de candidatos; extração da rubrica real e das armadilhas (documentado fora da pasta, em `_auditoria/`, e resumido em `docs/marcos.md`).
4. Painel de 4 juízes + 3 céticos (agentes) para escolher o challenge: empate 002 × 003; decisão do Marcus: 003.
5. Fork, branch `submission/marcus-barbosa`, identidade git local, esqueleto da pasta, checklist de marcos.
6. Geração de 3 baselines a partir do brief verbatim (em `baselines/`).
7. Síntese dos baselines: 16 lacunas comuns (ninguém abre o CSV, ninguém executa o backtest, leakage nas win rates, faixas fixas sem ver a distribuição, empates em Prospecting).
8. Rubrica de diferenciação D1–D16 escrita antes de qualquer código (`differentiation-rubric.md`).
9. Download do dataset pela sessão do Marcus no Kaggle (Chrome), após fila de uso da interface da máquina.

## Iteração 1 — 2026-09-21 — Base de código antes dos dados
10. Painel de arquitetura (3 designs independentes + 3 juízes + síntese) e varredura sobre o G4 (produtos, liderança, design system, tom de voz) lançados em paralelo.
11. Código de base escrito sem os CSVs, a partir do schema publicado no Kaggle: `requirements.txt` com versões fixas, `download_data.py`, `leadscorer/data.py` (validação de schema, normalização GTXPro→GTX Pro, data de referência = max(close_date) dos fechados, joins que preservam linhas), `leadscorer/audit.py` (relatório de saúde dos dados) e `01_audit.py`.
12. Fixture sintética pequena só para testes unitários (`tests/conftest.py`), com casos de borda deliberados; 5 testes verdes.
13. Erro da IA #1: `git add -f` arrastou caches para o commit; corrigido e regra de add ajustada (ver `ai-errors.md`).

## Iteração 2 — 2026-09-21 — Dados reais e auditoria
14. Download do zip (archive.zip, 145.926 bytes) pela sessão do Marcus no Kaggle; extração com `download_data.py --zip`; 4 CSVs + `metadata.csv`; hashes registrados no relatório.
15. `01_audit.py` sobre os dados reais → `docs/data_health_report.md`. Achados que mudam o desenho: (a) 1.425 deals abertos sem conta = 68,2% dos abertos, nenhum fechado sem conta; (b) win rate por produto, setor, região e manager varia de 1,4 a 4,8 pp, por vendedor 15,4 pp; (c) data de referência 2017-12-31, ciclo mediano 45 dias, mas Engaging tem idade mediana de 165 dias (1.558 de 1.589 acima do ciclo mediano); (d) 0 datas inconsistentes, 0 chaves órfãs após normalizar GTXPro; (e) preço de catálogo varia 487x.

## Iteração 3 — 2026-09-21 — Hipóteses contra os dados
16. `02_explore.py` com 25 hipóteses registradas por decorator, cada uma com métrica, número e veredito automático; saída em `docs/exploration_results.*`.
17. Primeira rodada (19 hipóteses): vendedor × produto confirmada, sazonalidade confirmada, conta recorrente com sinal invertido.
18. Revisão humana dos números levantou duas suspeitas: ruído binomial em grupos pequenos e bordas temporais da base. Rodada de robustez (H2b, H8b, H12b, H13b, H20) e depois (H21, H12c, H10b).
19. Resultado: sinal real só em idade do deal (quem morre, morre cedo), valor e estrutura do pipeline (81% além do suporte histórico, 68% sem conta). Erros da IA #2 e #3 registrados.

## Iteração 4 — 2026-09-21 — Motor de scoring e backtest
20. Painel de arquitetura (3 designs, 3 juízes, síntese) concluído; salvo em `docs/design-panel.md`. Adotado: calibração por painel de snapshots, backtest walk-forward, testes de invariância, brief em camadas. Descartado: fatores de vendedor×produto e conta (refutados pelos dados).
21. Motor v1: chance condicionada a fechar × preço; 15 testes verdes. Backtest revelou superestimativa (erro da IA #4).
22. Diagnóstico por snapshot: sem conta = 0% de fechamento (n=2.531 linhas); com conta, chance de fechar cai com a idade (86% até 90 dias, 14% entre 121 e 138). Conta tratada como higiene (decisão 13).
23. Motor v2: painel de snapshots com horizonte de 90 dias, faixas fixas, IC de Wilson, fusão de faixas pequenas, fallback declarado; 18 testes; backtest walk-forward com comparador 'só preço no pipeline inteiro'.

## Iteração 5 — 2026-09-21 — App, capturas e validação
24. App Streamlit em três papéis (vendedor, gerente, RevOps) com data de referência, filtros e presets por URL; identidade visual a partir do CSS público do G4.
25. Capturas do app com Playwright (`04_screenshots.py`); capturas da janela do Claude Code por PrintWindow sem ativar a janela, com a barra lateral (outras sessões do usuário) recortada por privacidade.
26. Validação em ambiente limpo (`99_clean_env_check.ps1`): venv novo, 21 testes, auditoria, exploração, backtest e health check do app, tudo verde.
27. README no template oficial e `docs/methodology.md` número-a-script. Auditoria adversarial por agentes lançada.
