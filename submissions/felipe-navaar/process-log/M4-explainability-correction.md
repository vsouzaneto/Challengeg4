# Correção de explicabilidade — ficha da oportunidade

- Data: 20/10/2026.
- Ressalva recebida: o challenge exige que o vendedor entenda por que cada oportunidade tem aquela prioridade; os fatores existiam no backend, mas não estavam visíveis na interface final.
- Diagnóstico: a simplificação visual removeu também a explicação necessária para a jornada de seleção → fila → detalhe → entendimento da prioridade.
- Correção: a ficha individual passou a mostrar “Por que esta oportunidade tem esta prioridade?”, usando `score_factors` calculado pelo backend. Os fatores são apresentados com rótulos comerciais, contribuição numérica e descrição do estágio atual.
- Decisão: manter a interface sem jargões técnicos sobre heurística, probabilidade ou política, mas preservar a explicação comercial mínima exigida pelo challenge.
- Testes adicionados: `tests/test_app_explainability.py`, cobrindo a tradução dos fatores `Engaging` e `Prospecting`.
- Verificação prevista após a alteração: suíte completa, compilação e importação do app.
