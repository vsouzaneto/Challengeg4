# Suporte: diagnóstico, intervenção e decisão

**Dhiego Spinillo · G4 AI Master · Challenge 002**

## Recomendação ao diretor

Instrumentar a operação e evoluir para autosserviço, atendimento preparado e investigação humana, com autonomia condicionada ao procedimento. O protótipo demonstra classificação e preparação do atendimento; o impacto depende de contexto real e ainda não foi medido.

**Cenário do desafio:** cerca de 30 mil tickets/ano, sobrecarga, resolução mais lenta e satisfação em queda. Os arquivos fornecidos não permitem confirmar essa evolução temporal nem quantificar suas causas.

## O que os dados mostram

| Evidência observada | Consequência para a decisão |
|---|---|
| **1.365 de 2.769 pares temporais invertidos (49,3%)**, sem abertura do chamado no D1. | Não calcular duração corrigindo o sinal nem apontar um canal como gargalo temporal. Registrar eventos confiáveis. |
| **2.881 de 8.469 tickets (34%)** aguardam resposta do cliente. | Investigar se a espera é por informação, evidência ou confirmação. O status sozinho não mede retrabalho. |
| **78 de 165 textos com `urgently` (47,3%)** têm prioridade Low/Medium. | Revisar exemplos com prazo e impacto reais. É sinal textual em dados padronizados, não prova de erro de prioridade. |

As notas de satisfação cobrem **32,7% da base**, somente tickets fechados. Não medem a queda de satisfação do cenário. Emails inconsistentes impedem reconstruir jornadas confiáveis. [Diagnóstico e fontes](../solution/analise-preliminar-cx.md).

## O que foi demonstrado

**Classificação no D2:** o modelo local treinado acertou **86%** dos rótulos de 800 tickets reservados; Jev, por definições sem treino específico, **45,25%**. O limiar escolhido na validação teve **6,69% de erro no teste**, acima da meta de 5%: confirmação humana mantida. Isso não demonstra desempenho no domínio do D1. [Comparação](../solution/comparacao.md).

**Protótipo funcional:** texto → categoria sugerida → conferências declaradas pelo atendente → orientação e rascunho por regras → revisão e registro. Relato de possível incidente fica separado da categoria, sem causa presumida. **165 testes** verificam contratos e comportamento; não medem utilidade operacional.

**Limite material:** não há consulta a outros tickets, notas, sistemas ou logs. Recap por LLM continua experimental: o revisor automatizado aprovou fidelidade em **6 de 15 saídas válidas**, sem referência humana completa. [Avaliação](../solution/avaliacao-recap.md).

## Próximo investimento proposto

1. **Instrumentar:** abertura, resposta, motivo e duração das esperas, transferências, responsável, vínculo entre tickets e prazo real de urgência.
2. **Validar em operação:** comparar trabalho ativo total, perguntas repetidas, encaminhamentos e reaberturas com/sem assistência. Descontar preenchimento da ficha e revisão dos rascunhos.
3. **Decidir:** ampliar apenas se o ganho medido justificar implantação/manutenção com qualidade preservada; simplificar ou encerrar se a ajuda acrescentar esforço. [Plano do piloto](piloto-operacional.md).

**Impacto pretendido:** menos perguntas repetidas e encaminhamentos incompletos. É hipótese a testar; não há ROI, horas recuperadas ou redução de churn comprovados.

## Autonomia e economics propostos

Evoluir para três caminhos: autosserviço em procedimentos elegíveis, atendimento preparado com contexto e investigação humana nas exceções. Reset de senha é um candidato encontrado nos textos; não há integração autônoma atual. [Mapa e evidências](tres-velocidades.md).

Cenário base ilustrativo: 800 tickets/mês × 4 minutos líquidos → **53,33 horas/mês**. Salário R$ 4 mil, fator de custo 1,7, 160 horas produtivas; conversão de 50% em despesa evitada, R$ 6 mil de implantação e R$ 500/mês de operação → **ROI de 13,33% no primeiro ano**. O cenário conservador é negativo. [Premissas e sensibilidade](economics.md).
