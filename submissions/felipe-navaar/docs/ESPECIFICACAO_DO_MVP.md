# Especificação do MVP — LeadScore G4

## Problema e público

O vendedor precisa decidir quais oportunidades abertas revisar primeiro. Manager e RevOps precisam consultar uma carteira filtrada. O MVP oferece fila priorizada, filtros e informações para apoiar a revisão humana.

## Escopo e módulos

1. **M1 — Ingestão:** validar quatro tabelas, normalizar aliases e preservar todas as oportunidades nos joins.
2. **M2 — Análise:** produzir diagnóstico descritivo com corte histórico declarado.
3. **M3 — Prioridade:** aplicar política versionada somente às oportunidades abertas.
4. **M4 — Interface:** mostrar carteira, filtros, visualizações, avisos e detalhes.
5. **M5 — Validação:** testar os contratos e revisar a experiência integrada.
6. **M6 — Documentação:** preparar setup, lógica, limitações e process log.

O Streamlit apresenta o resultado. Ingestão, análise, prioridade e filtros permanecem em módulos Python independentes. Filtros não recalculam score.

## Regras e limites

A política registrada `heuristic-v1` define score 70 para `Engaging` e 40 para `Prospecting`. É uma regra heurística, não probabilidade. Preço de catálogo serve para desempate, não representa receita esperada. Ausências geram avisos; oportunidades sem conta permanecem na fila. A data `2017-12-31` é uma referência demonstrativa, não um snapshot oficial.

O MVP lê CSVs locais, sem CRM, API de IA ou automação comercial. A solução não demonstra aumento de conversão ou receita.

## Critérios de entrega

Usar dados reais; reconciliar as oportunidades; manter uma saída por deal aberto; ordenar com desempate estável; preservar score ao filtrar; fornecer instruções reproduzíveis e registrar as verificações realmente executadas.
