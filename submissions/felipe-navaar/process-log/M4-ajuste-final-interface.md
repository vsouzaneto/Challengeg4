# Ajuste final de interface — modo escuro e foco na carteira

- Data: 20/10/2026.
- Decisão humana: remover da interface qualquer explicação sobre heurística, probabilidade, política ou composição da prioridade; priorizar informações e funcionalidades do dashboard.
- Alterações: tema escuro aplicado a tela, filtros, cards e gráficos; cards reduzidos para quatro informações principais, com tipografia responsiva para evitar truncamento; visualizações e ficha do deal reorientadas para carteira, prioridade e dados disponíveis; detalhes técnicos convertidos em pendências de informação compreensíveis; exportação mantém os nomes amigáveis.
- Regra preservada: nenhuma alteração foi feita em ingestão, filtros, política de priorização, ranking ou dados de origem; a mudança é exclusivamente de apresentação.
- Verificação: `.\\.venv\\Scripts\\python.exe -m compileall -q app.py src`, `.\\.venv\\Scripts\\python.exe -m pytest -q -p no:cacheprovider --basetemp .pytest-tmp-dark-ui` e `.\\.venv\\Scripts\\python.exe -c "import app; print('app importado com sucesso')"` terminaram com `15 passed in 1.03s` e `app importado com sucesso`.
- Observação: os avisos de execução fora do runtime Streamlit apareceram apenas no teste de importação e são esperados nesse modo.

## Correção posterior de explicabilidade

A simplificação inicial retirou explicações técnicas da tela, mas a revisão do challenge exigiu que o vendedor entendesse a prioridade. A decisão foi corrigida: a ficha da oportunidade passou a exibir os fatores calculados pelo backend em linguagem comercial, sem duplicar a regra de scoring na interface. A correção está detalhada em `M4-explainability-correction.md` e verificada em `M4-explainability-verification.md`.
