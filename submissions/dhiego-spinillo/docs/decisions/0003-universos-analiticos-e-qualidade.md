# ADR 0003 — Qualidade dos dados por pergunta de negócio

**Data:** 15/09/2026

**Status:** método de análise adotado após provocação de Dhiego; verificações implementadas em script de análise.

## Contexto

Dhiego pediu que a exploração evidencie inconsistências e separe o universo utilizável do suspeito, evitando conclusões sobre sujeira do dataset. A origem em Kaggle não comprova nem invalida a qualidade de um dado. O dicionário do D1 declara emails com domínio de exemplo por privacidade e notas 1–5 para tickets fechados; não demonstra como todas as colunas foram geradas.

## Decisão

Preservar os arquivos originais e definir admissibilidade por pergunta. Separar: erro formal verificável, ambiguidade de identidade, suspeita semântica, ausência esperada e informação estruturalmente inexistente. Aplicar filtros apenas à análise pertinente e documentar denominador antes/depois. Não corrigir classificação, imputar nota, inventar data nem escolher o subconjunto que favoreça a narrativa.

- Identidade ambígua impede concluir uma jornada por email; não invalida automaticamente uma contagem de tickets.
- Nota ausente em ticket aberto/pendente não deve eliminar esse ticket do retrato da operação.
- Ordem temporal não negativa não torna um par apto a medir SLA: continua faltando abertura e validação da semântica.
- Pedido explícito de urgência com prioridade baixa é candidato à revisão, não uma linha a apagar por contrariar a expectativa.
- Texto com artefatos pode ser inspecionado para gerar hipóteses, mas não é convertido em conversa autêntica pela remoção do placeholder.
- D2 passa verificações formais iniciais; isso não valida todos os rótulos nem resolve quase duplicatas.

## Consequências

Entregar regras reproduzíveis e quantidades agregadas por dimensão, com análise de sensibilidade quando cabível. Não afirmar que existe uma única base totalmente limpa. Os filtros podem se sobrepor e não devem ser somados como exclusões independentes.

Implementação: [auditar_coortes.py](../../solution/auditar_coortes.py). Resultados: [coortes-qualidade.json](../../solution/reports/coortes-qualidade.json). Interpretação: [qualidade por pergunta](../../solution/qualidade-por-pergunta.md).

## Autoria

Dhiego definiu a necessidade de separar qualidade de dados de sinais operacionais. Codex propôs as regras por finalidade, executou a contagem e documentou os limites. Nenhuma limpeza foi usada para criar uma alegação de desempenho do produto.
