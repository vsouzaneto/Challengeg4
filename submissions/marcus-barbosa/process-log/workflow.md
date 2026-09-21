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
