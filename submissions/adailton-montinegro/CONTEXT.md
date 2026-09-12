# Contexto canônico

Glossário da submissão do Challenge 001. Cada termo possui um único significado operacional.

## Termos analíticos

- **Conta:** entidade identificada por `account_id` em `accounts`.
- **Assinatura:** registro identificado por `subscription_id`; não equivale automaticamente a uma conta ou produto.
- **Snapshot declarado de churn:** estado informado por `accounts.churn_flag`, sem presunção de coerência com eventos ou assinaturas.
- **Evento histórico de churn:** registro datado em `churn_events`; não representa automaticamente o estado atual da conta.
- **Encerramento de assinatura:** assinatura com `end_date` preenchida e `subscriptions.churn_flag = true`; não representa automaticamente logo churn.
- **Logo churn:** saída completa de uma conta da base pagante. Não será calculado como fato até existir uma state machine reconciliada.
- **MRR observado:** `mrr_amount` no grão da assinatura, sem agregação automática por conta.
- **MRR proxy:** estimativa dependente de uma regra explícita para assinaturas simultâneas.
- **Universo analítico:** conjunto de registros elegíveis para uma pergunta específica após aplicação documentada das regras de qualidade.
- **Cobertura analítica:** registros elegíveis divididos pelos registros brutos do universo da métrica.
- **Quarentena:** registros preservados, porém excluídos de uma análise por violarem uma regra de qualidade.
- **Associação:** relação estatística observada que não demonstra causalidade.
- **Índice de triagem:** score explicável para ordenar contas; não é probabilidade de churn.
- **Exposição:** receita potencialmente afetada segundo um cenário explícito; não equivale a perda realizada.
- **Impacto simulado:** resultado de um cenário hipotético; não equivale a ROI observado.
- **Raw:** arquivos originais imutáveis e seus metadados de ingestão.
- **Stage:** dados tipados, padronizados, classificados por qualidade e separados entre elegíveis e quarentena.
- **Gold:** fatos, dimensões, métricas e conjuntos analíticos derivados de regras de negócio documentadas.

## Estados de confiabilidade

- **Observado:** suportado diretamente por registros válidos da fonte.
- **Derivado:** calculado a partir de regras reproduzíveis sobre dados observados.
- **Condicional:** depende de uma premissa ou cenário explícito.
- **Indisponível:** não identificável de forma defensável com os dados atuais.

