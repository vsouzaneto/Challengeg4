# Contratos de dados de cada módulo

O **contrato** é a lista de campos que cada módulo entende. Qualquer base (a do desafio ou de outra empresa) entra ligando as colunas dela a esses campos (De/Para).
🔴 = obrigatório para rodar · ⚪ = opcional (se faltar, a parte que depende dele é desligada e o sistema avisa)

## Retenção (001)
| Tabela | Campo do contrato | Coluna no desafio | |
|---|---|---|---|
| Clientes | id_cliente | account_id | 🔴 |
| | segmento (1..n) | industry, country, referral_source, plan_tier | ⚪ |
| | data_entrada | signup_date | ⚪ |
| | cancelou | churn_flag | 🔴 |
| Contratos | id_contrato, id_cliente | subscription_id, account_id | 🔴 |
| | receita_mensal | mrr_amount | 🔴 |
| | inicio, fim | start_date, end_date | ⚪ |
| | plano, assentos, upgrade, downgrade, cobrança | plan_tier, seats, upgrade_flag, downgrade_flag, billing_frequency | ⚪ |
| Uso | id_contrato, data, quantidade | subscription_id, usage_date, usage_count | ⚪ (tabela inteira) |
| | erros, é_beta, funcionalidade | error_count, is_beta_feature, feature_name | ⚪ |
| Chamados | id_cliente, prioridade, 1ª resposta (min), resolução (h), satisfação, escalado | account_id, priority, first_response_time_minutes, resolution_time_hours, satisfaction_score, escalation_flag | ⚪ (tabela inteira) |
| Cancelamentos | id_cliente, data, motivo | account_id, churn_date, reason_code | 🔴 |
| | reembolso, reativação, texto | refund_amount_usd, is_reactivation, feedback_text | ⚪ |

## Suporte (002)
| Tabela | Campo | Coluna no desafio (DS1) | |
|---|---|---|---|
| Chamados | id_chamado | Ticket ID | 🔴 |
| | canal, prioridade, tipo | Ticket Channel, Ticket Priority, Ticket Type | 🔴 (pelo menos um) |
| | status | Ticket Status | ⚪ |
| | tempo_1a_resposta, tempo_resolução | *derivados* de First Response Time / Time to Resolution (ver `06-achados`) **ou** colunas de duração direta | 🔴 (pelo menos um) |
| | satisfação | Customer Satisfaction Rating | ⚪ |
| | texto, assunto, resolução_texto | Ticket Description, Ticket Subject, Resolution | ⚪ (liga o classificador) |
| | id_cliente, produto | Customer Email, Product Purchased | ⚪ (liga o cruzamento Suporte → Churn) |
| Base de treino do classificador | texto, categoria | DS2: Document, Topic_group | 🔴 para o classificador |

**Entrada via cruzamento Churn → Suporte:** tickets da RavenStack (sem texto) → id_chamado = ticket_id, prioridade = priority, tempo_1a_resposta = first_response_time_minutes, tempo_resolução = resolution_time_hours, satisfação = satisfaction_score, escalado = escalation_flag, id_cliente = account_id. **Tipo e canal não existem** → a análise de gargalos usa prioridade e escalonamento.

## Vendas / Leads (003)
| Tabela | Campo | Coluna no desafio | |
|---|---|---|---|
| Oportunidades | id, vendedor, produto, estágio | opportunity_id, sales_agent, product, deal_stage | 🔴 |
| | conta, data_início, data_fechamento, valor_fechado | account, engage_date, close_date, close_value | ⚪ |
| | mapeamento de estágio → aberto/ganho/perdido | Prospecting, Engaging → aberto; Won; Lost | 🔴 (configurável) |
| Vendedores | vendedor, gestor, região | sales_agent, manager, regional_office | ⚪ (liga os filtros) |
| Produtos | produto, preço, série | product, sales_price, series | ⚪ |
| Contas | conta, setor, receita, funcionários, local, matriz | account, sector, revenue, employees, office_location, subsidiary_of | ⚪ |

**Entrada via cruzamento Churn → Leads:** clientes RavenStack → modo **"valor da conta"** (receita, assentos, plano, tempo de casa, upgrades) em vez de pipeline.

## Mídia (004)
| Campo | Coluna no desafio | |
|---|---|---|
| id_post, plataforma, data | content_id, platform, post_date | 🔴 |
| alcance (views), curtidas, compartilhamentos, comentários | views, likes, shares, comments_count | 🔴 (views + pelo menos uma interação) |
| tipo, categoria, duração/tamanho, hashtags, idioma | content_type, content_category, content_length, hashtags, language | ⚪ |
| id_criador, seguidores | creator_id, follower_count | ⚪ (liga a análise por tamanho de criador) |
| patrocinado, patrocinador, categoria do patrocinador, divulgação | is_sponsored, sponsor_name, sponsor_category, disclosure_type, disclosure_location | ⚪ (liga a aba Patrocínio) |
| audiência (idade, gênero, local) | audience_age_distribution, audience_gender_distribution, audience_location | ⚪ (liga a aba Audiência) |
| custo do post/patrocínio | **não existe no dataset** | ⚪ → "custo implícito" calculado por premissa editável (ex.: custo por mil seguidores) |

## Normalizações conhecidas (dados do desafio)
- 003: `GTXPro` → `GTX Pro`; `technolgy` → `technology`.
- 002: definição de durações (ver `06-achados_iniciais_dos_dados.md`), documentada na tela.
- 004: `post_date` no formato `m/d/aa h:mm AM/PM`.
