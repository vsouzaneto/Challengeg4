# Foco — especificação de negócio

Documento de negócio do case G4 003. Cada regra e cada critério apontam para o código ou teste que os comprova. Telas e filtros estão na [especificação funcional](functional-spec.md); arquitetura e cálculo, na [especificação técnica](technical-spec.md); verificação, no [plano de testes](test-plan.md).

## 1. Contexto

O [desafio 003 do G4](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/challenges/build-003-lead-scorer/README.md) pede uma ferramenta que ajude vendedores a escolher onde agir no pipeline. A base é o conjunto público *CRM Sales Predictive Analytics* (Kaggle, CC0): quatro tabelas (`sales_pipeline`, `accounts`, `products`, `sales_teams`) mais `metadata`. A empresa é fictícia e o registro mais recente é de 31/12/2017. Nada nesta entrega usa dado de cliente real.

## 2. Problema

Uma pessoa de vendas abre o pipeline e vê milhares de oportunidades abertas sem uma ordem de atenção. A pergunta prática vem do brief do G4: onde agir primeiro. O custo de não ter critério (tempo procurando por onde começar, conversas antigas sem confirmação nem encerramento) é a hipótese deste case; ele não foi medido.

Na base do case há 2.089 oportunidades abertas (1.589 `Engaging` e 500 `Prospecting`). Em 1.425 delas a conta está vazia, de modo que uma regra que dependa de dados da conta deixaria a maior parte da carteira sem orientação.

## 3. Proposta de valor

O Foco entrega, para cada oportunidade aberta, **uma fila, um índice de atenção de 0 a 100, os motivos da posição e uma próxima ação**. A hipótese de valor é reduzir o esforço para encontrar a próxima conversa útil. **Nenhum ganho de tempo, de produtividade ou de conversão foi medido**; a solução é um protótipo sobre dados históricos.

## 4. Usuários

| Perfil | Uso previsto | Estado |
| --- | --- | --- |
| Vendedor | Abre a fila, escolhe uma oportunidade, lê motivo e ação, registra anotação e andamento locais. | Usuário principal do protótipo. |
| Gerente | Filtra a própria equipe ou região, percorre a carteira por vendedor nos Painéis. | Leitura; sem perfil nem permissão real. |
| RevOps / liderança comercial | Validaria pesos e o prazo de 90 dias antes de qualquer piloto. | Papel futuro; ver [evoluções](product-roadmap.md). |

O protótipo não tem login. Qualquer pessoa que abra a aplicação vê toda a carteira; os filtros de vendedor e gerente são recortes de demonstração, não controle de acesso.

## 5. Decisões apoiadas

| Fila | Entram | Pergunta que responde | Próxima ação sugerida |
| --- | --- | --- | --- |
| **Avançar** | `Engaging` com até 90 dias desde o engajamento, ou sem data de engajamento | Quais conversas ainda estão recentes o bastante para avançar agora? | Retomar conversa e combinar próximo passo com data |
| **Revisar** | `Engaging` com mais de 90 dias | Quais oportunidades antigas precisam ser confirmadas, atualizadas ou encerradas? | Confirmar interesse; atualizar data do próximo passo ou encerrar |
| **Qualificar** | `Prospecting` | Quais oportunidades precisam de primeiro contato e cadastro completo? | Fazer primeiro contato e registrar resposta |

Os textos da última coluna são os de `next_action` em `scoring.py`; não são gerados por IA em tempo de uso.

## 6. Regras de negócio

| ID | Regra | Onde está no código | Teste que a comprova |
| --- | --- | --- | --- |
| RN-01 | Só entram oportunidades `Prospecting` e `Engaging`. `Won` e `Lost` nunca são priorizadas. | `scoring.rank_open`, `prioritize` | `test_open_deals_only_and_deterministic_order`, `test_closed_deals_are_rejected_and_skipped` |
| RN-02 | `Engaging` com até 90 dias desde o engajamento entra em Avançar; com 91 dias ou mais, em Revisar. | `prioritize` (`age_days > 90`) | `test_ninety_day_limit_splits_advance_from_review` |
| RN-03 | `Prospecting` entra sempre em Qualificar, qualquer que seja a idade. | `prioritize` | `test_prospecting_ignores_engagement_age` |
| RN-04 | `Engaging` sem data de engajamento entra em Avançar, sem bônus de tempo, com a razão “Ainda sem data de engajamento”. | `prioritize` | `test_engaging_without_date_enters_advance_without_time_bonus` |
| RN-05 | Pontos-base: Avançar 65, Revisar 50, Qualificar 35. | `prioritize` | `test_highest_index_per_queue_stays_below_the_cap` |
| RN-06 | +10 se a conta está identificada. | `prioritize` (`account_bonus`) | `test_missing_account_loses_bonus_and_is_explained` |
| RN-07 | +10 se o preço de catálogo é de pelo menos US$ 4.000. | `prioritize` (`price_bonus`) | `test_catalog_price_bonus_starts_at_four_thousand` |
| RN-08 | +10 em Avançar com até 30 dias; +10 em Revisar com 180 dias ou mais. | `prioritize` (`timing_bonus`) | `test_recent_bonus_applies_up_to_thirty_days_in_advance_only`, `test_old_bonus_applies_from_one_hundred_eighty_days_in_review_only` |
| RN-09 | O índice é limitado a 100. Com os pesos atuais os máximos alcançáveis são 95 (Avançar), 80 (Revisar) e 55 (Qualificar). | `prioritize` (`min(100, …)`) | `test_highest_index_per_queue_stays_below_the_cap` |
| RN-10 | A lista é ordenada por fila (Avançar, Revisar, Qualificar), depois índice decrescente, depois ID crescente. O índice só compara oportunidades da mesma fila. | `rank_open` | `test_queue_order_beats_index_order`, `test_missing_engagement_date_and_stable_tie` |
| RN-11 | `Won`/`Lost`, `close_value` e `close_date` não entram na pontuação de oportunidade aberta. | `prioritize` não lê esses campos | `test_closed_outcome_does_not_affect_open_priority`, `test_outcome_dates_do_not_change_snapshot_or_ranking` |
| RN-12 | A data de referência é fixa em 31/12/2017 e não é derivada de `close_date`. | `scoring.DATASET_AS_OF` | `test_open_deals_only_and_deterministic_order`, `test_outcome_dates_do_not_change_snapshot_or_ranking`, `test_missing_engagement_date_and_stable_tie` |
| RN-13 | `GTXPro` é tratado como `GTX Pro` (única equivalência de nome). | `scoring.PRODUCT_ALIASES` | `test_catalog_alias_is_only_the_documented_one`, `test_real_data_joins_and_alias` |
| RN-14 | Conta vazia não elimina a oportunidade: aparece como “Conta não informada”, com a razão “Conta ausente: preencher antes de avançar”. | `prioritize` | `test_missing_account_still_has_action_and_explanation` |
| RN-15 | Vendas históricas por vendedor (ganhas, perdidas, soma de `close_value` dos ganhos) são contexto e não alteram fila nem índice. | `app.summarize_sales` | `test_closed_history_changes_context_without_changing_open_score` |
| RN-16 | Anotações e andamento ficam só no navegador e não alteram fila nem índice. | `static/annotations.js` | `status e anotação sobrevivem à releitura local, sem tocar no score` |
| RN-17 | Preço é preço de catálogo em USD, nunca valor de fechamento. A soma por carteira não é receita potencial. | `static/panels.js` (textos), `scoring.prioritize` (razões) | Sem teste automatizado; conferido por leitura |
| RN-18 | O índice não é probabilidade de fechamento nem previsão de receita. | Textos em `index.html`, `method.html`, detalhe | Sem teste automatizado; conferido por leitura |

Consequências que valem registrar, porque derivam do código e não de uma escolha explícita de negócio:

- Como todos os bônus valem 10, o índice só assume valores em degraus de 10: 65, 75, 85, 95 em Avançar; 50, 60, 70, 80 em Revisar; 35, 45, 55 em Qualificar. Muitas oportunidades empatam e o desempate é pelo ID.
- Uma oportunidade em Avançar com índice 65 aparece **acima** de uma em Revisar com 80: a fila vem antes do índice.
- O teto de 100 hoje não é atingido; ele só passa a valer se os pesos mudarem.

## 7. Glossário

| Termo | Significado neste case |
| --- | --- |
| Oportunidade | Linha de `sales_pipeline`, identificada por `opportunity_id`. |
| Carteira | Conjunto de oportunidades abertas de um recorte (vendedor, gerente, região). |
| Fila | Avançar, Revisar ou Qualificar; define a próxima ação. |
| Índice operacional | Número de 0 a 100 que ordena atenção dentro da fila. Não é probabilidade. |
| Preço de catálogo | `sales_price` do produto em `products.csv`, em USD. Proxy de impacto. |
| Referência histórica | 31/12/2017, data usada para contar dias desde o engajamento. |
| Vendas históricas | Negócios `Won`/`Lost` do vendedor no conjunto; mostradas só como contexto. |
| Região | Valor de `regional_office` do vendedor em `sales_teams.csv`. |

## 8. Escopo

**Dentro:** fila explicável das oportunidades abertas; filtros por vendedor, gerente, região e busca; três leituras visuais; painéis por gerente, vendedor, região e preço; anotação e andamento locais; auditoria dos dados; hipótese histórica avaliada e descartada; documentação e testes reproduzíveis.

**Fora (e por quê):**

| Item | Motivo |
| --- | --- |
| Probabilidade de fechamento ou previsão de receita | A afinidade histórica testada teve AUC de 0,4854; não há base para alegar poder preditivo. |
| Escrita no CRM, mudança de etapa ou proprietário | Não há integração; o protótipo só lê CSVs. |
| Notas, tarefas ou status compartilhados | Exigem persistência, autoria e permissões. |
| Mapa geográfico real, rotas | O dataset não traz coordenadas; o mapa é ilustrativo. |
| Preço negociado, desconto | O dataset só traz preço de catálogo. |
| Autenticação e permissão por carteira | Fora do alcance do protótipo local. |

## 9. Premissas e restrições

- Roda localmente, sem custo, sem serviço externo e sem enviar dados para fora da máquina durante o uso.
- Usa somente os dados públicos indicados pelo desafio.
- O limite de 90 dias, o limite de US$ 4.000 e os pesos são **premissas operacionais do autor**, sem calibração. O dataset não registra histórico de estágios nem de atividades, então esses valores não podem ser validados retrospectivamente.
- O produto precisa funcionar com conta vazia, data de engajamento vazia e nomes de produto divergentes.

## 10. Riscos

| Risco | Mitigação no case | Resíduo |
| --- | --- | --- |
| Usuário ler o índice como chance de venda | Texto em detalhe, rodapé e Método; razões explícitas | Depende de leitura do texto |
| Pesos e prazo arbitrários | Regra e valores documentados, sem alegar acurácia | Precisa de calibração com vendedores |
| Preço de catálogo tratado como receita | Rótulos “catálogo” e “não representa vendas realizadas” | Soma por carteira pode ser mal interpretada |
| Dataset fictício e antigo | Data de referência exibida em todas as telas | Não há como medir efeito real |
| Anotação perdida ao trocar de navegador | Aviso “Salvo apenas neste navegador” | Sem sincronização |

## 11. Critérios de aceite do case e rastreabilidade

| Critério | Onde se verifica | Situação |
| --- | --- | --- |
| Executa localmente com os CSVs indicados, sem pacote pago nem serviço de inferência | `app.py` usa só biblioteca padrão; [operação](operations.md) | Conferido por leitura do código; execução completa registrada em rodada anterior ([plano de testes](test-plan.md)) |
| Usa dados reais, com `GTXPro` normalizado | RN-13 | Teste automatizado |
| Mostra só `Prospecting` e `Engaging`, explica prioridade e dá próxima ação | RN-01, RN-14 | Teste automatizado |
| Busca e filtros por vendedor, gerente e região, com três leituras | `filter.js`; `app.js` | Filtros: teste Node. Leituras visuais: capturas, sem teste automatizado |
| Não usa desfecho na pontuação de aberta | RN-11 | Teste automatizado |
| Instruções, lógica, limites, registro de processo e verificação reproduzível | `README.md`, `docs/`, `PROCESS_LOG.md` | Este conjunto de documentos |

## 12. Medidas propostas para um piloto

Não foram medidas. Seriam necessárias em dados atuais: tempo até a primeira ação sobre uma oportunidade de Avançar; proporção de oportunidades de Revisar atualizadas ou encerradas num prazo; avanço de etapa depois da ação sugerida; e comparação com um grupo que não use a fila. Só com essas medidas seria legítimo falar em ganho.

## 13. Hipótese rejeitada

Antes do produto, uma afinidade histórica suavizada por produto e setor foi avaliada em corte cronológico (5.343 negócios para ajuste, 1.368 para teste, a partir de 03/11/2017). O AUC foi **0,4854** e o quartil de maior afinidade teve **63,45%** de `Won`, contra **64,84%** no teste inteiro. O resultado não separa ganhos de perdas e por isso a taxa não participa da fila. Detalhes e comandos em [auditoria dos dados](data-audit.md).
