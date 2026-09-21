# Workflow cronológico

## Iteração 0 — 2026-09-21 — Entendimento e blindagem
1. Clone do repositório e leitura integral dos 11 arquivos.
2. Auditoria de segurança (unicode invisível, injeção de prompt, hooks, histórico, branch alternativo): nada malicioso.
3. Coleta das 176 reviews públicas do avaliador nos 100 PRs de candidatos; extração da rubrica real e das armadilhas (documentado fora da pasta, em `_auditoria/`, e resumido em `docs/marcos.md`).
4. Painel de 4 juízes + 3 céticos (agentes) para escolher o challenge: empate 002 × 003; decisão do Marcus: 003.
5. Fork, branch `submission/marcus-barbosa`, identidade git local, esqueleto da pasta, checklist de marcos.
6. Geração de 3 baselines a partir do brief verbatim (em `baselines/`).
