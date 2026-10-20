# Verificação da explicabilidade na interface

- Data: 20/10/2026.
- Correção verificada: a ficha individual agora exibe os fatores calculados em `score_factors`, com contribuição numérica e descrição amigável do estágio comercial.
- Testes adicionados: dois testes em `tests/test_app_explainability.py`, cobrindo `Engaging` e `Prospecting`.
- Comandos executados:
  - `.\\.venv\\Scripts\\python.exe -m compileall -q app.py src`
  - `.\\.venv\\Scripts\\python.exe -m pytest -q -p no:cacheprovider --basetemp .pytest-tmp-explainability`
  - `.\\.venv\\Scripts\\python.exe -c "import app; print('app importado com sucesso')"`
- Resultado: `17 passed in 1.86s` e `app importado com sucesso`.
- Resultado funcional: o vendedor passa a ver, dentro do detalhe da oportunidade, por que ela recebeu aquela prioridade, sem exposição de jargão técnico sobre a implementação.
- Ressalva encerrada: a interface não depende mais da leitura do código ou somente do README para explicar a prioridade.
