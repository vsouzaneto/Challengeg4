# Datasets: inventário e status

Todos são públicos no Kaggle (é preciso estar logado para baixar). Pasta de destino sugerida: `02/dados/<desafio>/`.

| # | Desafio | Dataset (Kaggle) | Licença | Arquivos | Volume | Status |
|---|---|---|---|---|---|---|
| 1 | 001 Churn | [SaaS Subscription & Churn Analytics](https://www.kaggle.com/datasets/rivalytics/saas-subscription-and-churn-analytics-dataset) | MIT (creditar *River @ Rivalytics*) | `ravenstack_accounts`, `_subscriptions`, `_feature_usage`, `_support_tickets`, `_churn_events` (.csv) | 500 / 5.000 / 25.000 / 2.000 / 600 linhas | ✅ `02/dados/001-churn/` |
| 2 | 002 Suporte (DS1) | [Customer Support Ticket Dataset](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset) | CC0 | 1 CSV (a confirmar) | **8.469** tickets (o README diz ~30 mil) | ✅ `customer_support_tickets.csv` |
| 3 | 002 Suporte (DS2) | [IT Service Ticket Classification](https://www.kaggle.com/datasets/adisongoh/it-service-ticket-classification-dataset) | CC0 | 1 CSV (a confirmar) | ~48 mil textos | ⬜ **FALTA BAIXAR** (obrigatório) |
| 4 | 003 Lead Scorer | [CRM Sales Predictive Analytics](https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics) | CC0 | `accounts`, `products`, `sales_teams`, `sales_pipeline` (.csv) | 85 / 7 / 35 / 8.800 (+ `metadata.csv`) | ✅ |
| 5 | 004 Social | [Social Media Sponsorship & Engagement](https://www.kaggle.com/datasets/omenkj/social-media-sponsorship-and-engagement-dataset) | MIT | a confirmar | 52.214 posts, 27 colunas | ✅ `social_media_dataset.csv` |

**Como baixar:** entrar no link → botão **Download** (canto superior direito) → salvar o `.zip` em `02/dados/<desafio>/` e extrair. Qualidade e achados de cada base: ver [`06-achados_iniciais_dos_dados.md`](06-achados_iniciais_dos_dados.md).

---

## Esquemas

### 001: RavenStack (confirmado nos arquivos)

| Tabela | Colunas |
|---|---|
| accounts | account_id, account_name, industry, country, signup_date, referral_source, plan_tier, seats, is_trial, churn_flag |
| subscriptions | subscription_id, account_id, start_date, end_date, plan_tier, seats, mrr_amount, arr_amount, is_trial, upgrade_flag, downgrade_flag, churn_flag, billing_frequency, auto_renew_flag |
| feature_usage | usage_id, subscription_id, usage_date, feature_name, usage_count, usage_duration_secs, error_count, is_beta_feature |
| support_tickets | ticket_id, account_id, submitted_at, closed_at, resolution_time_hours, priority, first_response_time_minutes, satisfaction_score, escalation_flag |
| churn_events | churn_event_id, account_id, churn_date, reason_code, refund_amount_usd, preceding_upgrade_flag, preceding_downgrade_flag, is_reactivation, feedback_text |

Ligações: `accounts` ← `subscriptions` ← `feature_usage`; `accounts` ← `support_tickets`; `accounts` ← `churn_events`. Dados sintéticos, com reativações e nulos propositais.

⚠️ `support_tickets` da RavenStack **não tem texto**, só métricas. Isso importa para o cruzamento Churn → Suporte.

### 002: Suporte (DS1 confirmado; DS2 falta)
- **DS1:** Ticket ID, Customer Name, Customer Email, Customer Age, Customer Gender, Product Purchased, Date of Purchase*, Ticket Type, Ticket Subject, **Ticket Description**, Ticket Status, **Resolution**, Ticket Priority, Ticket Channel, First Response Time, Time to Resolution, Customer Satisfaction Rating (Date of Purchase existe; 5 tipos de ticket)
- **DS2:** **Document** (texto), **Topic_group** (8 categorias: Hardware, HR Support, Access, Storage, Purchase…)



### 003: CRM (confirmado)
- `sales_pipeline`: opportunity_id, sales_agent, product, account, deal_stage (Prospecting/Engaging/Won/Lost), engage_date, close_date, close_value
- `accounts`: account, sector, year_established, revenue (milhões USD), employees, office_location, subsidiary_of
- `products`: product, series, sales_price
- `sales_teams`: sales_agent, manager, regional_office

### 004: Social (confirmado)
id, platform, content_id, creator_id, creator_name, content_url, content_type, content_category, post_date, language, content_length, content_description, hashtags, views, likes, shares, comments_count, comments_text, follower_count, is_sponsored, disclosure_type, sponsor_name, sponsor_category, disclosure_location, audience_age_distribution, audience_gender_distribution, audience_location.
**Não há coluna de engagement rate** (calculamos) **nem de custo**.

---

## Não existe chave em comum entre os datasets
Os datasets são de 4 empresas diferentes, então os cruzamentos entre eles seguem os selos 🟢/🟡/🔵 (ver [`02-cruzamentos_entre_modulos.md`](02-cruzamentos_entre_modulos.md)).
