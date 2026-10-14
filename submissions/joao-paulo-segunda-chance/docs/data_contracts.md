# Contrato inicial e dicionário das fontes

Este dicionário descreve as colunas efetivamente recebidas. Tipos propostos precisam de validação na importação; não alteram a fonte. Flags comerciais/cadastrais não têm histórico de mudança. Money em subscriptions tem unidade monetária a confirmar na documentação; refund identifica USD explicitamente.

| Fonte | Coluna | Tipo proposto | Observação |
|---|---|---|---|
| ravenstack_accounts.csv | `account_id` | text | ID externo de conta; relacionamento versionado. |
| ravenstack_accounts.csv | `account_name` | text | Preservar valor e semântica de origem. |
| ravenstack_accounts.csv | `industry` | text | Preservar valor e semântica de origem. |
| ravenstack_accounts.csv | `country` | text | Preservar valor e semântica de origem. |
| ravenstack_accounts.csv | `signup_date` | date | Preservar valor e semântica de origem. |
| ravenstack_accounts.csv | `referral_source` | text | Preservar valor e semântica de origem. |
| ravenstack_accounts.csv | `plan_tier` | text | Preservar valor e semântica de origem. |
| ravenstack_accounts.csv | `seats` | integer | Preservar valor e semântica de origem. |
| ravenstack_accounts.csv | `is_trial` | boolean | Preservar valor e semântica de origem. |
| ravenstack_accounts.csv | `churn_flag` | boolean | Flag recebida; não substituir evento ou status contratual. |
| ravenstack_subscriptions.csv | `subscription_id` | text | ID externo de assinatura; não presente em churn_events. |
| ravenstack_subscriptions.csv | `account_id` | text | ID externo de conta; relacionamento versionado. |
| ravenstack_subscriptions.csv | `start_date` | date | Preservar valor e semântica de origem. |
| ravenstack_subscriptions.csv | `end_date` | date | Ausente significa término não informado; não prova atividade real. |
| ravenstack_subscriptions.csv | `plan_tier` | text | Preservar valor e semântica de origem. |
| ravenstack_subscriptions.csv | `seats` | integer | Preservar valor e semântica de origem. |
| ravenstack_subscriptions.csv | `mrr_amount` | numeric | Valor contratual mensal recorrente; não caixa nem perda por evento. |
| ravenstack_subscriptions.csv | `arr_amount` | numeric | Valor anualizado; reconciliar com MRR. |
| ravenstack_subscriptions.csv | `is_trial` | boolean | Preservar valor e semântica de origem. |
| ravenstack_subscriptions.csv | `upgrade_flag` | boolean | Sem data individual da alteração. |
| ravenstack_subscriptions.csv | `downgrade_flag` | boolean | Sem data individual da alteração. |
| ravenstack_subscriptions.csv | `churn_flag` | boolean | Flag recebida; não substituir evento ou status contratual. |
| ravenstack_subscriptions.csv | `billing_frequency` | text | Preservar valor e semântica de origem. |
| ravenstack_subscriptions.csv | `auto_renew_flag` | boolean | Preservar valor e semântica de origem. |
| ravenstack_feature_usage.csv | `usage_id` | text | ID de origem sujeito a validação de unicidade; não presumir PK única. |
| ravenstack_feature_usage.csv | `subscription_id` | text | ID externo de assinatura; não presente em churn_events. |
| ravenstack_feature_usage.csv | `usage_date` | date | Preservar valor e semântica de origem. |
| ravenstack_feature_usage.csv | `feature_name` | text | Preservar valor e semântica de origem. |
| ravenstack_feature_usage.csv | `usage_count` | integer | Preservar valor e semântica de origem. |
| ravenstack_feature_usage.csv | `usage_duration_secs` | integer | Preservar valor e semântica de origem. |
| ravenstack_feature_usage.csv | `error_count` | integer | Não presumir subconjunto de usage_count sem contrato. |
| ravenstack_feature_usage.csv | `is_beta_feature` | boolean | Preservar valor e semântica de origem. |
| ravenstack_support_tickets.csv | `ticket_id` | text | Preservar valor e semântica de origem. |
| ravenstack_support_tickets.csv | `account_id` | text | ID externo de conta; relacionamento versionado. |
| ravenstack_support_tickets.csv | `submitted_at` | timestamp (fuso não informado) | Preservar valor e semântica de origem. |
| ravenstack_support_tickets.csv | `closed_at` | timestamp (fuso não informado) | Permite disponibilidade conservadora da resolução. |
| ravenstack_support_tickets.csv | `resolution_time_hours` | numeric | Preservar valor e semântica de origem. |
| ravenstack_support_tickets.csv | `priority` | text | Preservar valor e semântica de origem. |
| ravenstack_support_tickets.csv | `first_response_time_minutes` | integer | Não há timestamp próprio da resposta. |
| ravenstack_support_tickets.csv | `satisfaction_score` | numeric | Nulo significa não observado; confirmar escala. |
| ravenstack_support_tickets.csv | `escalation_flag` | boolean | Preservar valor e semântica de origem. |
| ravenstack_churn_events.csv | `churn_event_id` | text | Preservar valor e semântica de origem. |
| ravenstack_churn_events.csv | `account_id` | text | ID externo de conta; relacionamento versionado. |
| ravenstack_churn_events.csv | `churn_date` | date | Preservar valor e semântica de origem. |
| ravenstack_churn_events.csv | `reason_code` | text | Preservar valor e semântica de origem. |
| ravenstack_churn_events.csv | `refund_amount_usd` | numeric | Reembolso informado em USD; não equivale a MRR perdido. |
| ravenstack_churn_events.csv | `preceding_upgrade_flag` | boolean | Sem data individual da alteração. |
| ravenstack_churn_events.csv | `preceding_downgrade_flag` | boolean | Sem data individual da alteração. |
| ravenstack_churn_events.csv | `is_reactivation` | boolean | Distinguir reativação de cancelamento. |
| ravenstack_churn_events.csv | `feedback_text` | text | Texto declarado, não causa comprovada. |

## Campos de rastreabilidade a acrescentar na persistência

`source_file_id`, `source_row_number`, `source_record_hash`, `source_version_id`, `imported_at` e contrato de origem. Datas de fato mantidas separadas da data de ingestão. Não fabricar data de alteração para atributo sem histórico.

## Exemplos de relacionamentos

subscriptions.account_id → accounts.account_id; feature_usage.subscription_id → subscriptions.subscription_id; support_tickets.account_id e churn_events.account_id → accounts.account_id. Foreign keys devem respeitar a versão das fontes. Agregar cada fato antes de cruzar medidas financeiras.
