# Registro de etapa — M3: política e motor de regras

- Data/hora: 20/10/2026 (data da sessão; horário não registrado pelo ambiente)
- Módulo e objetivo: M3 — implementar a política de scoring aprovada, com explicações, avisos, corte temporal e ranking determinístico.
- Ferramenta/modelo efetivamente utilizado: Codex via ferramentas locais; edição por patch.
- Prompt enviado (texto ou caminho da evidência): instruções do usuário, `prompts/03-M3-scoring.md` e proposta `heuristic-v1` apresentada na conversa.
- Decisão humana e aprovação: usuário aprovou explicitamente a política `heuristic-v1` em 20/10/2026.
- Política aprovada: base 10; Engaging +60; Prospecting +30; score final 70 ou 40; idade desde `engage_date`, preço, conta, setor, porte, região e vendedor são contextuais; preço apenas no desempate; `opportunity_id` como desempate final; missing gera aviso neutro.
- Resultado produzido / arquivos alterados: `config/scoring_policy.json`, `src/scoring.py`, `tests/test_scoring.py` e atualização de `docs/DECISOES.md`.
- Verificações previstas: testes de pontuação somente em abertos, reconciliação de fatores, missing, estabilidade após embaralhamento e exclusão de campos futuros.
- Comandos de verificação realmente executados: `.\\.venv\\Scripts\\python.exe -m pytest -q`; execução real com `load_and_prepare()` e `score_open_opportunities()`.
- Saídas observadas: `10 passed in 0.92s`. Nos CSVs reais foram pontuadas 2.089 linhas, com 2.089 IDs únicos, scores entre 40 e 70, 2.089 posições únicas e distribuição de 1.589 scores 70 (Engaging) e 500 scores 40 (Prospecting). Houve avisos em 1.588 linhas; nenhum deal foi descartado.
- Pendências / limitações: o score é deliberadamente simples e heurístico; não comprova conversão futura. M4/Streamlit ainda não foi iniciado.
