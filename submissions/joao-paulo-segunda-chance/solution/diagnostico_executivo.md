# RavenStack — diagnóstico para decisão

Referência dos fatos: **31/12/2024**. As duas versões publicadas conservam os mesmos fatos; a segunda comprova o ciclo de atualização por Excel. O recebimento em outubro de 2026 não transforma a base em dados atuais.

## O que o CEO deve saber

Não é possível atribuir uma causa raiz do churn com confiança usando apenas estas tabelas. É possível demonstrar por que os indicadores aparentam discordar: o cadastro, o histórico de eventos, os contratos e as medidas de uso/satisfação têm definições e elegibilidades diferentes. A primeira decisão recomendada é reconciliar essas diferenças, antes de direcionar uma campanha de retenção. O site transforma essa investigação em decisões com responsável, prazo e evidência preservada.

## Três afirmações que precisam ser separadas

| Pergunta | Evidência observada | Consequência para a decisão |
|---|---|---|
| “O churn aumentou?” | 110/500 contas têm flag cadastral, sem data de mudança. Há 539 cancelamentos históricos em 339 contas e 61 reativações. | 22% é proporção cadastral, não taxa mensal. Contar eventos não mede sozinho aumento de churn ou perda de contas. |
| “O uso cresceu?” | 19.142/25.000 registros são anteriores ao início da assinatura; 21 IDs de uso repetidos envolvem 42 linhas. | Crescimento do total bruto pode incluir registros temporalmente incoerentes. Nas janelas qualificadas, o total observado passa de 7.090 para 8.756 (+23,5%), mas as contas com observação passam de 340 para 389. Mudança de composição/cobertura impede interpretar o aumento como evolução do engajamento de toda a carteira. |
| “A satisfação está boa?” | Na janela elegível de 30 dias, média 3,85/5 em 53 notas para 88 tickets fechados: cobertura 60,2%. Em toda a fonte, 825/2.000 tickets não têm nota e 1.077 antecedem o cadastro. | A média descreve os respondentes observados. Não permite concluir satisfação de todos os clientes, nem explicar causalmente o churn. |

As contagens de qualidade podem se sobrepor. Não somá-las como se fossem linhas defeituosas distintas. Uma divergência pode refletir histórico, semântica ou extração; não é automaticamente erro do negócio.

## A lacuna mais direta: cadastro versus cancelamento

Das 110 flags de churn, **35 não possuem qualquer evento e uma possui apenas reativação**. Assim, 36/110 (32,7%) não têm cancelamento histórico registrado. Nesses casos, a data, o motivo e a perda associada são indeterminados. Além disso, todas as 110 contas marcadas têm ao menos um contrato aberto segundo os intervalos fornecidos. Isso exige reconciliação, não substituição arbitrária de uma definição por outra.

Também existem 265 contas sem flag que têm cancelamento histórico. Reativação, múltiplos contratos ou outra definição podem explicar parte da diferença; não se pode tratá-las automaticamente como clientes perdidos no corte.

## Quem investigar primeiro, com critério explícito

Critério recomendado: **contas com flag de churn sem cancelamento registrado, ordenadas pelo MRR contratual observado**. É prioridade de investigação por exposição contratual, não probabilidade de churn nem estimativa de receita perdida.

| Setor | Contas no setor | Flags cadastrais | Contas sem cancelamento registrado entre as flags | MRR contratual dessas contas |
|---|---:|---:|---:|---:|
| FinTech | 112 | 25 | 12 | 222.217 |
| HealthTech | 96 | 21 | 8 | 196.732 |
| Cybersecurity | 100 | 16 | 5 | 106.166 |
| DevTools | 113 | 35 | 8 | 92.685 |
| EdTech | 79 | 13 | 3 | 67.115 |
| Total | 500 | 110 | 36 | 684.915 |

A unidade monetária de MRR não está documentada. MRR soma contratos abertos no corte e exclui trials. Não é caixa recebido. FinTech e HealthTech concentram 20 desses 36 casos e 61,2% da exposição contratual dessa população. Esse é um ponto de partida defendível para investigar; não demonstra maior risco futuro desses setores.

**Contas específicas:** no site, abra **Contas**, filtre **Flag sem cancelamento registrado** e ordene **Maior MRR contratual**. O filtro combina as 35 contas sem evento e a conta com apenas reativação. Setor e país podem refinar o recorte. Cada conta mostra ID, contratos, eventos, tickets de suporte com elegibilidade para satisfação e ressalvas; a decisão fica vinculada ao snapshot usado. As fontes e a listagem por conta não são duplicadas no repositório.

## Motivos declarados: pistas para investigação

Nos **539 eventos de cancelamento** históricos, os motivos são: funcionalidades (`features`) 101, suporte (`support`) 98, orçamento (`budget`) 92, desconhecido (`unknown`) 86, preço (`pricing`) 82 e concorrente (`competitor`) 80. Não incluir as 61 reativações nesse denominador. Os textos de feedback dos cancelamentos se distribuem em “too expensive” 140, “missing features” 140, “switched competitor” 125 e 134 ausentes. Código e texto são campos distintos; não assumir equivalência sem investigação.

| Setor cadastral recebido | Orçamento | Concorrente | Funcionalidades | Preço | Suporte | Desconhecido | Total de eventos |
|---|---:|---:|---:|---:|---:|---:|---:|
| Cybersecurity | 21 | 13 | 20 | 12 | 18 | 25 | 109 |
| DevTools | 23 | 24 | 23 | 19 | 26 | 14 | 129 |
| EdTech | 11 | 9 | 20 | 15 | 14 | 16 | 85 |
| FinTech | 20 | 17 | 17 | 15 | 24 | 23 | 116 |
| HealthTech | 17 | 17 | 21 | 21 | 16 | 8 | 100 |
| Total | 92 | 80 | 101 | 82 | 98 | 86 | 539 |

Essas frequências priorizam entrevistas e conferência dos tickets: Produto pode começar pelos relatos de funcionalidades; CS pelos relatos de suporte e pelos motivos desconhecidos. Não são taxas setoriais, causas comprovadas ou contas distintas: uma conta pode ter múltiplos eventos e o setor é o atributo recebido, sem histórico de mudanças. Os 98 relatos de suporte não provam que um ticket específico causou o cancelamento. Atribuição a assinatura, perda financeira e efeito de uma intervenção continuam indeterminados.

## Ações priorizadas e impacto estimado

| Prioridade | Ação / responsável proposto | Critério de conclusão | Impacto defendível |
|---|---|---|---|
| 1 | Dados + Financeiro: reconciliar as 36 flags sem cancelamento, começando por maior exposição contratual; documentar conta versus assinatura, cancelamento, término e reativação. | Os 36 casos com evidência da origem ou motivo explícito de indeterminação; nenhuma data inventada. | Até 36 lacunas esclarecidas; 684.915 de MRR contratual sob investigação. Não estimável como receita recuperável. |
| 2 | Engenharia de Dados + Produto: validar os 21 IDs repetidos, os vínculos temporais e a cobertura da telemetria. | Regras e contratos confirmados, relatório de seleção e cobertura publicado em nova versão. | Até 42 linhas com conflito de ID investigadas e regra temporal verificada sobre 25.000 registros. Não equivale a engajamento recuperado. |
| 3 | CS + Dados: revisar os denominadores de satisfação, tickets sem nota e datas de abertura/fechamento; selecionar investigações individuais a partir de evidência. | Respondentes, elegibilidade e disponibilidade temporal documentados; cada ação concluída com resultado. | Melhor interpretação dos 35 tickets fechados elegíveis sem nota no corte; 825 notas ausentes na fonte inteira. Não preencher ausente com zero. |

**Cenário de capacidade, não compromisso:** se a equipe conseguir verificar dez contas por dia útil, a prioridade 1 requer aproximadamente quatro dias úteis. Com cinco por dia, oito dias. O volume é observado; a capacidade é uma hipótese de planejamento. Ganho financeiro e redução de churn permanecem não estimáveis sem confirmar vínculos, causas e eficácia das ações.

## O que ainda seria necessário para explicar causas

- História de mudanças de cadastro/plano e vinculação dos cancelamentos a assinaturas.
- Garantia de cobertura por período e semântica das contagens de uso/erros.
- Histórico completo de episódios de cancelamento/reativação e disponibilidade das notas de satisfação.
- Investigação com CS/clientes e avaliação de intervenções com grupos/períodos comparáveis.

Uma sequência “ação → melhora” não comprova causalidade. Esta entrega preserva o estado indeterminado quando a evidência não sustenta uma conclusão.

## Como reproduzir e agir

[Abrir mesa de decisão](https://challenge-g4-ravenstack.early-hake-5665.chatgpt.site). As cinco fontes foram cruzadas com chaves e granularidades preservadas. Ver [contratos](../docs/data_contracts.md), [auditor Python](../scripts/audit_data.py), [auditor web](../web/domain/import.mjs), [status operacional](../docs/web_status.md) e [Process Log](../process-log/acceptance_2026-10-12.md).

A auditoria web reproduz os 89 resultados de referência do auditor Python. As regras de diagnóstico foram preservadas na atualização efetiva. Isso comprova consistência do processamento, não completude ou causalidade das fontes.
