# Suporte: diagnóstico, intervenção e decisão

**Dhiego Spinillo · G4 AI Master · Challenge 002**

## Recomendação ao diretor

Reduzir trabalho de busca e reconstrução de contexto, resolver procedimentos elegíveis pelo autosserviço e reservar investigação para exceções. A entrega demonstra esses três caminhos com IA e regras; consultas e ações usam sistemas fictícios explicitamente identificados. Impacto operacional ainda precisa de piloto.

**Contexto do desafio:** cerca de 30 mil tickets/ano, sobrecarga, resolução mais lenta e satisfação em queda. Os arquivos não confirmam essa evolução nem permitem quantificar suas causas.

## O que os dados mostram

| Evidência | Decisão |
|---|---|
| D1: **1.365/2.769 pares temporais invertidos (49,3%)**, sem abertura. | Não calcular duração corrigindo sinal. Instrumentar eventos confiáveis. |
| **2.881/8.469 (34%)** aguardam cliente. | Investigar se falta informação, evidência ou confirmação; status não mede desperdício. |
| D2: **685/47.837 menções a reset (1,43%)**. Exemplos incluem instrução simples e tentativas frustradas. | Separar procedimento de exceção; menção não é elegibilidade nem projeção de volume anual. |

Notas de satisfação cobrem 32,7% do D1, somente fechados. Emails inconsistentes impedem jornadas confiáveis. [Análise](../solution/analise-preliminar-cx.md) · [oportunidades](tres-velocidades.md).

## O que funciona na demonstração

- **Autosserviço:** pedido curto → contexto consultado → escolha do cliente → token de uso único → conclusão no provedor simulado. Falha transfere histórico ao suporte.
- **Preparação:** consulta automática de tickets/notas/estado → evidências e rascunho por regra → revisão. Pedidos múltiplos impedem resposta única presumidamente completa.
- **Investigação:** relato sensível, conta restrita ou fonte indisponível → contexto e evidências para humano. Nenhuma causa ou resolução presumida.

A IA extrai intenção, tentativas e sinais com citações verificadas. Regras controlam procedimentos; nenhum score autoriza alteração de conta. **204 testes** verificam comportamento. Sete cenários conhecidos foram exercitados com IA: seis extrações aceitas e um fallback; isso não mede acurácia de produção. [Processos, iterações e limites](valor-por-processo.md).

Comparação anterior preservada: classificador local **86%**, Jev **45,25%** em 800 tickets. O limiar não atingiu a meta de erro; segue assistido. Recap livre continua experimental, separado da execução. [Comparação](../solution/comparacao.md) · [recap](../solution/avaliacao-recap.md).

## Valor e próximo investimento

O autosserviço isolado tem baixa contribuição no cenário ilustrativo. A principal hipótese é poupar busca, leitura e preparação no atendimento humano. O economics agora decompõe antes/depois, revisão, sucesso e falhas, sem contar um ticket duas vezes.

Exemplo, não previsão: 50 tickets/mês elegíveis ao autosserviço e 1.000 à preparação, adoção 80%, tempos e custos declarados → **72,27 h/mês**, **53,57% de ROI no primeiro ano**. Sob os custos assumidos, são necessárias **47,06 h/mês** para pagar o primeiro ano. Não há saving comprovado. [Premissas e condição de equilíbrio](valor-por-processo.md).

**Decisão proposta:** validar elegibilidade e trabalho ativo, integrar fontes reais e comparar ganho líquido com qualidade/recontatos. Ampliar somente se o ganho medido pagar implantação/manutenção. [Piloto](piloto-operacional.md).
