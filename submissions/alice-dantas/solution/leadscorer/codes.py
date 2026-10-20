"""Códigos do contrato: o que a regra decidiu, como dado (plano do contrato, fase F2).

O núcleo entrega chaves, códigos e números; o texto de cada código é de quem
apresenta (a tela e a CLI). Um código novo precisa entrar aqui, no schema da API
(`api/schemas.py`) e nos catálogos de texto, ou os testes de contrato falham.
"""
from __future__ import annotations

CONTRACT_VERSION = 7  # 2: códigos ao lado dos textos (F2); 3: sem os campos de texto (F5);
                      # 4: /api/evidence, /api/rules e o resumo por vendedor na carteira da equipe;
                      # 5: regra A (ADR-006): grupo acompanhar, dois limites, só motivos que decidem;
                      # 6: Inteligência comercial (ADR-007): /api/intelligence e /api/intelligence/deals
                      # 7: orientação de verificação (ADR-008): ações check_*, `has_account` na ação e
                      #    `won_cycle_median_days` no meta

# Papel de cada motivo: o que ele decidiu na posição da oportunidade. Só entra motivo que decide.
ROLE_GROUP = "group"      # decidiu o grupo
ROLE_ORDER = "order"      # decidiu a ordem dentro do grupo
ROLES = (ROLE_GROUP, ROLE_ORDER)

# Motivos (item.reasons[].code)
AGE_WITHIN_WON_CYCLE = "age_within_won_cycle"    # focar: idade até L1
AGE_ABOVE_WON_CYCLE = "age_above_won_cycle"      # acompanhar: acima de L1, até L2
AGE_ABOVE_CYCLE_LIMIT = "age_above_cycle_limit"  # revisar: acima de L2
PROSPECTING_STAGE = "prospecting_stage"
MISSING_FIELD = "missing_field"
LIST_PRICE = "list_price"
NO_PRODUCT = "no_product"
NO_LIST_PRICE = "no_list_price"
REASON_CODES = (AGE_WITHIN_WON_CYCLE, AGE_ABOVE_WON_CYCLE, AGE_ABOVE_CYCLE_LIMIT, PROSPECTING_STAGE, MISSING_FIELD,
                LIST_PRICE, NO_PRODUCT, NO_LIST_PRICE)

# Orientação do que verificar (item.next_action.code e group.next_action.code). A ferramenta não vê
# atividades, estágio nem contatos (ADR-008): cada código é uma verificação no CRM, nunca uma ação comercial.
CHECK_STATUS = "check_status"                  # focar: consultar o andamento
CHECK_PROGRESS = "check_progress"              # acompanhar: consultar o último registro
CONFIRM_STILL_ACTIVE = "confirm_still_active"  # revisar: verificar se a negociação continua
CHECK_PROSPECTING = "check_prospecting"        # qualificar: verificar se já houve engajamento para registrar a data
FIX_MISSING_FIELD = "fix_missing_field"        # no item: cita o campo
FIX_MISSING_FIELDS = "fix_missing_fields"      # no grupo
# Os três primeiros levam `has_account` (a conta está registrada?); no grupo, `has_account` é nulo.
ACCOUNT_ACTION_CODES = (CHECK_STATUS, CHECK_PROGRESS, CONFIRM_STILL_ACTIVE)
ACTION_CODES = (CHECK_STATUS, CHECK_PROGRESS, CONFIRM_STILL_ACTIVE, CHECK_PROSPECTING,
                FIX_MISSING_FIELD, FIX_MISSING_FIELDS)

# Vazios (group.empty.code e empty.code do payload)
GROUP_EMPTY = "group_empty"
START_WITH_GROUP = "start_with_group"
NO_OPEN_FOR_SELLER = "no_open_for_seller"
NO_OPEN_FOR_FILTER = "no_open_for_filter"
EMPTY_CODES = (GROUP_EMPTY, START_WITH_GROUP, NO_OPEN_FOR_SELLER, NO_OPEN_FOR_FILTER)

# Critérios da ordem dentro do grupo (ordering.within_group), na ordem em que valem.
ORDER_VALUE_BAND = "value_band"
ORDER_SALES_PRICE_DESC = "sales_price_desc"
ORDER_OPPORTUNITY_ID = "opportunity_id"
ORDER_CRITERIA = (ORDER_VALUE_BAND, ORDER_SALES_PRICE_DESC, ORDER_OPPORTUNITY_ID)

# Estratégias do backtest (evidence.rankers[].code), na ordem do relatório. O código descreve a
# regra, não o papel: qual delas é servida diz `SERVED_RANKER` (e `evidence.reference`).
RANKER_GLOBAL_RATE = "global_rate"
RANKER_PRODUCT_RATE = "product_rate"
RANKER_RANDOM = "random"
RANKER_LIST_PRICE_ONLY = "list_price_only"
RANKER_AGE_NEWEST_FIRST = "age_newest_first"
RANKER_AGE_MAX_CYCLE_ONLY = "age_max_cycle_only"          # só o maior ciclo → preço (regra até a v4)
RANKER_AGE_P90_THEN_MAX_CYCLE = "age_p90_then_max_cycle"  # regra A: P90 das ganhas → maior ciclo → preço
RANKER_CODES = (RANKER_GLOBAL_RATE, RANKER_PRODUCT_RATE, RANKER_RANDOM, RANKER_LIST_PRICE_ONLY,
                RANKER_AGE_NEWEST_FIRST, RANKER_AGE_MAX_CYCLE_ONLY, RANKER_AGE_P90_THEN_MAX_CYCLE)
SERVED_RANKER = RANKER_AGE_P90_THEN_MAX_CYCLE  # a regra que triage.py serve: referência das diferenças
# Só no relatório do backtest, nunca na API: a armadilha usa o desfecho (vazamento).
RANKER_LEAK_QUARTER_END = "leak_quarter_end_close"

# O que acontece com a regra servida sem as negociações que nunca fecham (evidence.without_no_outcome_verdict).
VERDICT_REFERENCE_BEHIND = "reference_behind"  # alguma alternativa fica à frente, com IC acima de zero
VERDICT_INCONCLUSIVE = "inconclusive"
VERDICT_REFERENCE_AHEAD = "reference_ahead"    # todas ficam atrás, com IC abaixo de zero
VERDICT_CODES = (VERDICT_REFERENCE_BEHIND, VERDICT_INCONCLUSIVE, VERDICT_REFERENCE_AHEAD)

# Inteligência comercial (ADR-007). Dimensões dos recortes, na ordem da tela; as de pessoas
# (e o escritório, que é de pessoas) ficam em ordem alfabética e sem gráfico (RD-06, AC-2.9).
DIM_PRODUCT, DIM_SELLER, DIM_MANAGER, DIM_OFFICE = "product", "seller", "manager", "office"
DIM_SECTOR, DIM_ACCOUNT, DIM_SIZE = "sector", "account", "size"
DIMENSIONS = (DIM_PRODUCT, DIM_SELLER, DIM_MANAGER, DIM_OFFICE, DIM_SECTOR, DIM_ACCOUNT, DIM_SIZE)
PEOPLE_DIMENSIONS = (DIM_SELLER, DIM_MANAGER, DIM_OFFICE)
ORDER_ALPHABETICAL, ORDER_REVENUE_DESC = "alphabetical", "revenue_desc"
SEGMENT_ORDERS = (ORDER_ALPHABETICAL, ORDER_REVENUE_DESC)
OUTCOME_WON, OUTCOME_LOST, OUTCOME_OPEN = "won", "lost", "open"
OUTCOMES = (OUTCOME_WON, OUTCOME_LOST, OUTCOME_OPEN)
# Veredito do teste de acaso da taxa de ganho entre os segmentos de uma dimensão.
CHANCE_BEYOND, CHANCE_WITHIN, CHANCE_TOO_FEW = "beyond_chance", "within_chance", "too_few_closed"
CHANCE_VERDICTS = (CHANCE_BEYOND, CHANCE_WITHIN, CHANCE_TOO_FEW)
# Fatores da receita de um segmento: receita = fechadas × taxa de ganho × ticket.
DRIVER_VOLUME, DRIVER_CONVERSION, DRIVER_TICKET = "volume", "conversion", "ticket"
DRIVERS = (DRIVER_VOLUME, DRIVER_CONVERSION, DRIVER_TICKET)
# Diagnósticos do processo (o que RevOps pode mudar), na ordem da tela.
DIAG_ENGAGING_BEYOND_LONGEST_CYCLE = "engaging_beyond_longest_cycle"
DIAG_OPEN_WITHOUT_ACCOUNT = "open_without_account"
DIAG_PROSPECTING_WITHOUT_ENGAGE_DATE = "prospecting_without_engage_date"
DIAG_SELLERS_WITHOUT_OPPORTUNITIES = "sellers_without_opportunities"
DIAG_QUARTER_END_OUTCOME_MIX = "quarter_end_outcome_mix"  # higiene de registro, nunca sinal (RJ-02)
DIAG_ENGAGEMENT_INFLOW_DROP = "engagement_inflow_drop"
DIAG_ACCOUNTS_SHARED_BY_SELLERS = "accounts_shared_by_sellers"
DIAGNOSTIC_CODES = (DIAG_ENGAGING_BEYOND_LONGEST_CYCLE, DIAG_OPEN_WITHOUT_ACCOUNT,
                    DIAG_PROSPECTING_WITHOUT_ENGAGE_DATE, DIAG_SELLERS_WITHOUT_OPPORTUNITIES,
                    DIAG_QUARTER_END_OUTCOME_MIX, DIAG_ENGAGEMENT_INFLOW_DROP, DIAG_ACCOUNTS_SHARED_BY_SELLERS)
# Descobertas sobre os resultados, na ordem da tela.
FIND_WIN_RATE_WITHIN_CHANCE = "win_rate_within_chance"
FIND_WIN_RATE_BEYOND_CHANCE = "win_rate_beyond_chance"
FIND_REVENUE_CONCENTRATED = "revenue_concentrated"
FIND_REVENUE_GAP_DRIVERS = "revenue_gap_drivers"
FIND_FAST_LOSSES = "fast_losses"
FIND_ACCOUNT_PRODUCT_COVERAGE = "account_product_coverage"
FINDING_CODES = (FIND_WIN_RATE_WITHIN_CHANCE, FIND_WIN_RATE_BEYOND_CHANCE, FIND_REVENUE_CONCENTRATED,
                 FIND_REVENUE_GAP_DRIVERS, FIND_FAST_LOSSES, FIND_ACCOUNT_PRODUCT_COVERAGE)
# Vazios da Inteligência: fora de EMPTY_CODES, que são os da carteira.
NO_CLOSED_FOR_FILTER = "no_closed_for_filter"
NO_DEALS_FOR_FILTER = "no_deals_for_filter"
INTELLIGENCE_EMPTY_CODES = (NO_CLOSED_FOR_FILTER, NO_DEALS_FOR_FILTER)

# Erros (corpo de erro da API: code)
DATA_FILE_MISSING = "data_file_missing"
DATA_FILE_EMPTY = "data_file_empty"
DATA_FILE_INVALID = "data_file_invalid"
DATA_COLUMNS_MISSING = "data_columns_missing"
DATA_UNKNOWN_LABEL = "data_unknown_label"
DATA_BAD_DATE = "data_bad_date"
DATA_DUPLICATE_KEY = "data_duplicate_key"
DATA_BAD_PRICE = "data_bad_price"
INVALID_AS_OF_FORMAT = "invalid_as_of_format"
AS_OF_BEFORE_LAST_CLOSE = "as_of_before_last_close"
SELLER_NOT_FOUND = "seller_not_found"
OPPORTUNITY_NOT_FOUND = "opportunity_not_found"
EVIDENCE_UNAVAILABLE = "evidence_unavailable"  # resultado do backtest ausente, inválido ou de outra regra
NO_WON_HISTORY = "no_won_history"  # nenhuma venda ganha até o as_of: não há o primeiro limite de idade
DATA_BAD_NUMBER = "data_bad_number"  # close_value ou receita do cliente que não é número válido
INVALID_PARAMETER = "invalid_parameter"  # parâmetro da Inteligência fora dos valores aceitos
ERROR_CODES = (DATA_FILE_MISSING, DATA_FILE_EMPTY, DATA_FILE_INVALID, DATA_COLUMNS_MISSING, DATA_UNKNOWN_LABEL,
               DATA_BAD_DATE, DATA_DUPLICATE_KEY, DATA_BAD_PRICE, INVALID_AS_OF_FORMAT, AS_OF_BEFORE_LAST_CLOSE,
               SELLER_NOT_FOUND, OPPORTUNITY_NOT_FOUND, EVIDENCE_UNAVAILABLE, NO_WON_HISTORY, DATA_BAD_NUMBER,
               INVALID_PARAMETER)
