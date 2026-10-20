"""Contrato tipado das respostas da API (plano do contrato, fases F1, F2 e F5; v4 na fase U5; v5 na regra A;
v6 na Inteligência comercial).

Espelha o payload de `views`. Os modelos proíbem campos extras: um campo novo em
`views` sem par aqui quebra a resposta e os testes, em vez de passar sem contrato.

O back entrega chaves, códigos e números (`leadscorer/codes.py`); quem apresenta
(tela e CLI) escreve o texto. O payload não leva texto pronto para a tela.
"""
from __future__ import annotations

from datetime import date
from typing import Annotated, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from leadscorer import codes, policy

# Literal com uma tupla equivale a listar os valores: as constantes do núcleo continuam a fonte.
StateKey = Literal[policy.STATES]
OpenStage = Literal[policy.OPEN_STAGES]
ValueBand = Literal[tuple(label for label, _ in policy.VALUE_BANDS)]
MissingField = Literal[tuple(policy.MISSING_FIELDS)]
OrderCriterion = Literal[codes.ORDER_CRITERIA]
ErrorCode = Literal[codes.ERROR_CODES]
RankerCode = Literal[codes.RANKER_CODES]
VerdictCode = Literal[codes.VERDICT_CODES]
# Ações vindas da política: a de cada grupo e a do grupo nao_pontuavel. As que citam a conta levam `has_account`.
AccountActionCode = Literal[codes.ACCOUNT_ACTION_CODES]
SimpleActionCode = Literal[tuple(code for code in dict.fromkeys([*policy.NEXT_ACTIONS.values(), codes.FIX_MISSING_FIELDS])
                                 if code not in codes.ACCOUNT_ACTION_CODES)]
StartActionCode = Literal[tuple(dict.fromkeys(policy.START_ACTION_CODES.values()))]
# Inteligência comercial (ADR-007).
Dimension = Literal[codes.DIMENSIONS]
SegmentOrder = Literal[codes.SEGMENT_ORDERS]
DealOutcome = Literal[codes.OUTCOMES]
ChanceVerdict = Literal[codes.CHANCE_VERDICTS]
Driver = Literal[codes.DRIVERS]
DealStage = Literal[policy.OPEN_STAGES + policy.CLOSED_STAGES]
Month = Annotated[str, Field(pattern=r"^\d{4}-\d{2}$", description="Mês, AAAA-MM.")]

class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class NoParams(Contract):
    """Código sem parâmetros."""


# Motivos: o que decidiu o grupo (role "group") e a ordem dentro dele ("order"). Só entra o que decide.
class WonCycleParams(Contract):
    age_days: int = Field(description="Dias corridos desde engage_date até o as_of.")
    won_cycle_limit_days: int = Field(description="L1: piso do P90 do ciclo das ganhas até o as_of.")
    percentile: int = Field(description="Percentil do ciclo das ganhas que define L1.")


class AgeWithinWonCycle(Contract):
    """Engaging com idade até L1: grupo focar."""
    code: Literal[codes.AGE_WITHIN_WON_CYCLE]
    role: Literal[codes.ROLE_GROUP]
    params: WonCycleParams


class BetweenLimitsParams(Contract):
    age_days: int
    won_cycle_limit_days: int = Field(description="L1: piso do P90 do ciclo das ganhas até o as_of.")
    cycle_limit_days: int = Field(description="L2: maior ciclo entre as fechadas até o as_of.")
    percentile: int


class AgeAboveWonCycle(Contract):
    """Engaging com idade acima de L1 e até L2: grupo acompanhar."""
    code: Literal[codes.AGE_ABOVE_WON_CYCLE]
    role: Literal[codes.ROLE_GROUP]
    params: BetweenLimitsParams


class LongestCycleParams(Contract):
    age_days: int
    cycle_limit_days: int = Field(description="L2: maior ciclo entre as fechadas até o as_of.")


class AgeAboveCycleLimit(Contract):
    """Engaging com idade acima de L2: grupo revisar."""
    code: Literal[codes.AGE_ABOVE_CYCLE_LIMIT]
    role: Literal[codes.ROLE_GROUP]
    params: LongestCycleParams


class ProspectingParams(Contract):
    deal_stage: Literal["Prospecting"]


class ProspectingStage(Contract):
    """Estágio Prospecting: grupo qualificar (a regra é o estágio, não a falta de data)."""
    code: Literal[codes.PROSPECTING_STAGE]
    role: Literal[codes.ROLE_GROUP]
    params: ProspectingParams


class FieldParams(Contract):
    field: MissingField


class MissingFieldReason(Contract):
    """Falta um campo necessário: grupo nao_pontuavel."""
    code: Literal[codes.MISSING_FIELD]
    role: Literal[codes.ROLE_GROUP]
    params: FieldParams


class ListPriceParams(Contract):
    product: str
    sales_price: int = Field(description="Preço de tabela (catálogo, não valor negociado).")
    value_band: ValueBand


class ListPrice(Contract):
    """Faixa e preço de tabela: ordenam dentro do grupo."""
    code: Literal[codes.LIST_PRICE]
    role: Literal[codes.ROLE_ORDER]
    params: ListPriceParams


class NoProduct(Contract):
    """Sem produto, não há preço para ordenar."""
    code: Literal[codes.NO_PRODUCT]
    role: Literal[codes.ROLE_ORDER]
    params: NoParams


class ProductParams(Contract):
    product: str


class NoListPrice(Contract):
    """O produto não tem preço no catálogo."""
    code: Literal[codes.NO_LIST_PRICE]
    role: Literal[codes.ROLE_ORDER]
    params: ProductParams


Reason = Annotated[Union[AgeWithinWonCycle, AgeAboveWonCycle, AgeAboveCycleLimit, ProspectingStage,
                         MissingFieldReason, ListPrice, NoProduct, NoListPrice],
                   Field(discriminator="code")]


# Ação sugerida pela regra.
class SimpleAction(Contract):
    code: SimpleActionCode
    params: NoParams


class AccountParams(Contract):
    has_account: Optional[bool] = Field(description="A conta da oportunidade está registrada? Nulo na ação do grupo, "
                                                    "que não é de uma oportunidade só.")


class AccountAction(Contract):
    """Verificação no CRM que muda conforme a conta: registrada ou não (ADR-008)."""
    code: AccountActionCode
    params: AccountParams


class FixFieldAction(Contract):
    code: Literal[codes.FIX_MISSING_FIELD]
    params: FieldParams


NextAction = Annotated[Union[SimpleAction, AccountAction, FixFieldAction], Field(discriminator="code")]


# Vazios.
class GroupEmpty(Contract):
    code: Literal[codes.GROUP_EMPTY]
    params: NoParams


class StartWithParams(Contract):
    group: StateKey = Field(description="Primeiro grupo seguinte que tem oportunidades.")
    action: StartActionCode
    has_engaging: bool = Field(description="Há negociações em andamento (Engaging) acima de L1 na carteira? Define o "
                                           "porquê de Focar estar vazio quando o grupo indicado é Qualificar.")
    won_cycle_limit_days: int = Field(description="L1, o limite que deixou o grupo focar vazio.")
    cycle_limit_days: int = Field(description="L2, o limite de acompanhar.")


class StartWithGroup(Contract):
    """O grupo focar está vazio: comece pelo grupo indicado."""
    code: Literal[codes.START_WITH_GROUP]
    params: StartWithParams


GroupEmptyState = Annotated[Union[GroupEmpty, StartWithGroup], Field(discriminator="code")]


class PipelineEmpty(Contract):
    code: Literal[codes.NO_OPEN_FOR_SELLER, codes.NO_OPEN_FOR_FILTER]
    params: NoParams


class Ordering(Contract):
    """A ordem da lista como dado, para quem apresenta explicar a ordem."""
    group_order: List[StateKey]
    within_group: List[OrderCriterion] = Field(description="Critérios dentro do grupo, na ordem em que valem.")
    age_affects_order: bool


class Item(Contract):
    opportunity_id: str
    sales_agent: str
    product: Optional[str]
    account: Optional[str] = Field(description="Nulo quando a oportunidade não tem conta registrada.")
    sales_price: Optional[int] = Field(description="Preço de tabela do produto (catálogo, não valor negociado).")
    value_band: Optional[ValueBand]
    engage_date: Optional[date]
    age_days: Optional[int] = Field(description="Dias corridos de engage_date até o as_of.")
    group: StateKey
    deal_stage: OpenStage
    missing_field: Optional[MissingField]
    tie_size: int = Field(description="Quantas oportunidades do mesmo grupo e produto (mesmo preço) há na carteira.")
    reasons: List[Reason] = Field(description="Exatamente dois: o que decidiu o grupo e o que decidiu a ordem.")
    next_action: NextAction


class Group(Contract):
    state: StateKey
    count: int
    empty: Optional[GroupEmptyState] = Field(description="Nulo quando o grupo tem oportunidades.")
    next_action: Optional[NextAction] = Field(description="Nulo quando o grupo está vazio.")
    items: List[Item] = Field(description="Na ordem de prioridade decidida pelo núcleo.")


class Summary(Contract):
    total: int
    focar: int
    acompanhar: int
    revisar: int
    qualificar: int
    nao_pontuavel: int
    without_account: int = Field(description="Oportunidades sem conta registrada.")


class Meta(Contract):
    as_of: date
    won_cycle_median_days: int = Field(description="Mediana do ciclo das ganhas até o as_of: contexto da idade, "
                                                   "não decide grupo nem ordem.")
    won_cycle_limit_days: int = Field(description="L1: piso do P90 do ciclo das ganhas até o as_of.")
    cycle_limit_days: int = Field(description="L2: maior ciclo entre as fechadas até o as_of.")
    cycle_percentile: int = Field(description="Percentil do ciclo das ganhas que define L1.")
    audited: bool = Field(description="Os CSVs são a versão auditada (hash).")
    contract_version: Literal[codes.CONTRACT_VERSION]


class SellerPipeline(Contract):
    seller: str
    meta: Meta
    ordering: Ordering
    summary: Summary
    empty: Optional[PipelineEmpty] = Field(description="Nulo quando há oportunidades abertas.")
    groups: List[Group] = Field(description="Na ordem de `ordering.group_order`.")


class TeamFilter(Contract):
    manager: Optional[str]
    office: Optional[str]


class SellerSummary(Contract):
    """Resumo da carteira aberta de um vendedor do filtro."""
    seller: str
    total: int
    focar: int
    acompanhar: int
    revisar: int
    qualificar: int
    nao_pontuavel: int
    without_account: int


class TeamPipeline(Contract):
    filter: TeamFilter
    meta: Meta
    ordering: Ordering
    summary: Summary
    empty: Optional[PipelineEmpty] = Field(description="Nulo quando há oportunidades abertas.")
    groups: List[Group] = Field(description="Na ordem de `ordering.group_order`.")
    by_seller: List[SellerSummary] = Field(
        description="Todo vendedor do filtro, inclusive com zero abertas, em ordem alfabética: nunca um ranking.")


# Regras (página Como funciona).
class ValueBandRule(Contract):
    band: ValueBand
    min_price: int = Field(description="Preço de tabela mínimo da faixa, inclusive.")
    max_price: Optional[int] = Field(description="Preço de tabela máximo, inclusive; nulo na faixa de cima.")


class Rules(Contract):
    """A política que monta a lista, como dado."""
    meta: Meta
    ordering: Ordering
    value_bands: List[ValueBandRule] = Field(description="Da faixa de cima para a de baixo.")


# Evidência (página Evidência): resultado de scripts/backtest.py, sem a armadilha de vazamento.
class EvidenceDesign(Contract):
    cuts: List[date] = Field(description="Datas de corte T; em cada uma, a carteira aberta em T.")
    horizon_days: int = Field(description="Desfecho: ganhou em até este número de dias depois de T.")
    top_k: int = Field(description="Tamanho da lista de cada vendedor.")
    observations: int = Field(description="Pares oportunidade × corte (os cortes se sobrepõem).")
    unique_opportunities: int
    n_boot_sellers: int = Field(description="Reamostragens de vendedores no IC das diferenças.")
    audited_data: bool = Field(description="O backtest rodou sobre os CSVs auditados.")


class Delta(Contract):
    value: float
    low: float = Field(description="Limite inferior do IC95%.")
    high: float = Field(description="Limite superior do IC95%.")


class RankerResult(Contract):
    code: RankerCode
    auc_mean: float = Field(description="AUC média entre os cortes; 0,5 é o acaso.")
    auc_min: float
    auc_max: float
    cuts_auc_above_chance: Optional[int] = Field(
        description="Cortes com o IC95% da AUC acima de 0,5; nulo quando não calculado.")
    p_at_k: float = Field(description="Ganhas nas top_k de cada vendedor ÷ top_k.")
    lift_at_k: float = Field(description="Ganhas nas top_k ÷ ganhas esperadas ao acaso.")
    val_at_k: float = Field(
        description="Valor ganho nas top_k ÷ valor ganho nas top_k melhores sabendo o futuro (o oráculo).")
    delta_val: Optional[Delta] = Field(
        description="val_at_k menos o da referência, com IC95% por bootstrap de vendedores; nulo na referência.")
    cuts_val_above_reference: Optional[int] = Field(description="Cortes com val_at_k acima da referência.")


class EvidenceVerdict(Contract):
    """Como fica a regra servida contra as alternativas, pelo IC95% de cada diferença."""
    code: VerdictCode
    ranker: Optional[RankerCode] = Field(description="A alternativa que decidiu o veredito; nulo se inconclusivo.")
    delta: Optional[Delta] = Field(description="A diferença dessa alternativa contra a servida.")


class Evidence(Contract):
    design: EvidenceDesign
    reference: RankerCode = Field(description="A regra servida hoje, base das diferenças.")
    rankers: List[RankerResult] = Field(description="Estratégias na ordem do relatório.")
    without_no_outcome: List[RankerResult] = Field(
        description="As mesmas medidas sem as oportunidades que nunca fecham na base.")
    without_no_outcome_verdict: EvidenceVerdict = Field(
        description="A regra servida sem as que nunca fecham: a limitação principal da evidência.")


# Inteligência comercial (página Inteligência, ADR-007): o histórico descrito, sem previsão.
class IntelligenceFilter(Contract):
    """O recorte pedido. Valor inexistente dá recorte vazio, nunca erro."""
    product: Optional[str]
    seller: Optional[str]
    manager: Optional[str]
    office: Optional[str] = Field(description="Escritório do vendedor (regional_office), não a sede do cliente.")
    sector: Optional[str]
    account: Optional[str]
    size: Optional[str] = Field(description="Porte do cliente: a chave de `options.sizes`.")


class AccountOption(Contract):
    name: str
    sector: Optional[str]
    location: Optional[str] = Field(description="Sede do cliente (office_location).")
    size: Optional[str]


class SizeBand(Contract):
    """Porte do cliente: quantil da receita anual entre os clientes cadastrados."""
    key: str = Field(description="1 é o menor porte.")
    low: float = Field(description="Receita anual mínima do porte, em US$ milhões.")
    high: float = Field(description="Receita anual máxima do porte, em US$ milhões.")
    accounts: int


class IntelligenceOptions(Contract):
    """Valores dos filtros que não vêm de /api/sellers (vendedor, gerente e escritório vêm de lá)."""
    products: List[str]
    sectors: List[str]
    accounts: List[AccountOption]
    sizes: List[SizeBand]


class WinRate(Contract):
    value: float = Field(description="Ganhas ÷ fechadas.")
    low: float = Field(description="Faixa provável (Wilson, 95%): limite inferior.")
    high: float = Field(description="Faixa provável (Wilson, 95%): limite superior.")


class ClosedMetrics(Contract):
    """O histórico de fechadas até o as_of de um recorte."""
    closed: int
    won: int
    lost: int
    win_rate: Optional[WinRate] = Field(description="Nula sem fechadas. Não é a chance de uma oportunidade.")
    revenue: int = Field(description="Σ close_value das ganhas: receita realizada.")
    won_without_value: int = Field(description="Ganhas sem close_value (contam como 0 na receita).")
    ticket: Optional[float] = Field(description="Receita ÷ ganhas.")
    revenue_per_closed: Optional[float] = Field(description="Receita ÷ fechadas.")
    median_won_cycle_days: Optional[int] = Field(description="Mediana de close − engage das ganhas, em dias.")
    median_lost_cycle_days: Optional[int] = Field(description="Mediana de close − engage das fechadas sem venda.")
    without_account: int


class OpenSnapshot(Contract):
    """A carteira aberta do recorte no as_of, com os grupos da regra (os mesmos da Equipe)."""
    summary: Summary
    list_value: int = Field(description="Σ preço de tabela das abertas. Não é receita e não se soma a ela.")
    without_list_price: int
    excluded_without_account: Optional[int] = Field(
        description="Abertas sem cliente que saíram do recorte por filtro de setor, cliente ou porte; "
                    "nulo sem esses filtros.")
    empty: Optional[PipelineEmpty]


class AccountProfile(Contract):
    sector: Optional[str]
    location: Optional[str]
    size: Optional[str]
    products_bought: int = Field(description="Produtos diferentes já ganhos com o cliente no recorte.")
    products_total: int = Field(description="Produtos negociados no catálogo.")
    sellers: int = Field(description="Vendedores diferentes com fechadas no cliente no recorte.")


class Segment(Contract):
    key: Optional[str] = Field(description="Nulo: oportunidades sem esse dado (ex.: sem cliente registrado).")
    history: ClosedMetrics
    revenue_share: Optional[float] = Field(description="Fatia da receita do recorte.")
    open: int = Field(description="Abertas do segmento no as_of.")
    profile: Optional[AccountProfile] = Field(description="Só na dimensão account.")


class ChanceTest(Contract):
    """A taxa de ganho difere entre os segmentos mais do que o acaso explicaria (qui-quadrado)?"""
    verdict: ChanceVerdict
    segments_tested: int = Field(description="Segmentos com fechadas suficientes para o teste.")
    segments_small: int = Field(description="Segmentos fora do teste por terem poucas fechadas.")
    closed_tested: int
    min_win_rate: Optional[float]
    max_win_rate: Optional[float]
    p_value: Optional[float]
    alpha: float = Field(description="Nível do teste já dividido pelas dimensões (Bonferroni).")


class RevenueDrivers(Contract):
    """Quanto da diferença de receita entre segmentos vem do volume, da conversão e do ticket."""
    segments_used: int
    spread_ratio: float = Field(description="Maior receita ÷ menor receita entre os segmentos.")
    volume_share: float
    conversion_share: float
    ticket_share: float
    main: List[Driver] = Field(description="Fatores que explicam boa parte da diferença.")
    negligible: List[Driver] = Field(description="Fatores que quase não explicam a diferença.")


class Breakdown(Contract):
    dimension: Dimension
    order: SegmentOrder = Field(description="Pessoas em ordem alfabética (nunca um ranking); o resto por receita.")
    segments: List[Segment]
    chance: ChanceTest
    drivers: Optional[RevenueDrivers] = Field(description="Nulo com poucos segmentos.")


class MatrixCell(Contract):
    product: str
    closed: int
    mix_share: Optional[float] = Field(description="Fatia do produto nas fechadas do vendedor.")


class MatrixRow(Contract):
    seller: str
    closed: int
    cells: List[MatrixCell]


class SellerProductMatrix(Contract):
    """O mix de cada vendedor, em ordem alfabética. Sem taxa por célula."""
    products: List[str] = Field(description="Do maior preço de tabela para o menor.")
    rows: List[MatrixRow]


class CrosstabCell(Contract):
    key: str
    closed: int
    share: Optional[float] = Field(description="Fatia desta coluna nas fechadas da linha.")


class CrosstabRow(Contract):
    key: str
    closed: int
    cells: List[CrosstabCell]


class Crosstab(Contract):
    """Quem compra o quê e quem atende quem: fechadas por linha e coluna. Sem taxa por célula."""
    id: Literal["account_product", "sector_product", "seller_sector", "sector_office", "location_office"]
    row_dimension: Literal["account", "sector", "seller", "location"]
    column_dimension: Literal["product", "sector", "office"]
    columns: List[str] = Field(description="Produtos do maior preço ao menor; setores e escritórios em ordem alfabética.")
    rows: List[CrosstabRow] = Field(description="Vendedores em ordem alfabética (nunca um ranking); o resto por fechadas.")


class CycleBand(Contract):
    low: int
    high: int = Field(description="As duas últimas bordas são L1 e L2 do meta.")
    won: int
    lost: int
    win_rate: Optional[float]


class MonthPoint(Contract):
    month: Month
    engaged: int = Field(description="Novas negociações (engage_date no mês).")
    won: int
    lost: int


# Diagnósticos do processo.
class EngagingBeyondParams(Contract):
    group: StateKey = Field(description="O grupo da regra que reúne essas negociações.")
    count: int
    engaging: int
    share: Optional[float]
    cycle_limit_days: int = Field(description="L2: maior ciclo fechado até o as_of.")


class EngagingBeyondLongestCycle(Contract):
    code: Literal[codes.DIAG_ENGAGING_BEYOND_LONGEST_CYCLE]
    params: EngagingBeyondParams


class OpenWithoutAccountParams(Contract):
    count: int
    open: int
    share: Optional[float]
    closed_without_account: int
    closed: int


class OpenWithoutAccount(Contract):
    code: Literal[codes.DIAG_OPEN_WITHOUT_ACCOUNT]
    params: OpenWithoutAccountParams


class ProspectingWithoutDateParams(Contract):
    group: StateKey = Field(description="O grupo da regra que reúne essas oportunidades.")
    count: int
    prospecting: int


class ProspectingWithoutEngageDate(Contract):
    code: Literal[codes.DIAG_PROSPECTING_WITHOUT_ENGAGE_DATE]
    params: ProspectingWithoutDateParams


class SellersWithoutOpportunitiesParams(Contract):
    count: int
    team: int
    sellers: List[str] = Field(description="Em ordem alfabética.")


class SellersWithoutOpportunities(Contract):
    code: Literal[codes.DIAG_SELLERS_WITHOUT_OPPORTUNITIES]
    params: SellersWithoutOpportunitiesParams


class QuarterEndParams(Contract):
    quarter_end_closed: int
    quarter_end_win_rate: float
    other_closed: int
    other_win_rate: float


class QuarterEndOutcomeMix(Contract):
    """Higiene de registro: nunca um sinal para prever (RJ-02)."""
    code: Literal[codes.DIAG_QUARTER_END_OUTCOME_MIX]
    params: QuarterEndParams


class MonthCount(Contract):
    month: Month
    engaged: int


class InflowDropParams(Contract):
    recent: List[MonthCount]
    base_average: float
    base_first_month: Month
    base_last_month: Month


class EngagementInflowDrop(Contract):
    code: Literal[codes.DIAG_ENGAGEMENT_INFLOW_DROP]
    params: InflowDropParams


class SharedAccountsParams(Contract):
    median_sellers: int
    max_sellers: int
    accounts: int


class AccountsSharedBySellers(Contract):
    code: Literal[codes.DIAG_ACCOUNTS_SHARED_BY_SELLERS]
    params: SharedAccountsParams


Diagnostic = Annotated[Union[EngagingBeyondLongestCycle, OpenWithoutAccount, ProspectingWithoutEngageDate,
                             SellersWithoutOpportunities, QuarterEndOutcomeMix, EngagementInflowDrop,
                             AccountsSharedBySellers], Field(discriminator="code")]


# Descobertas.
class WithinChanceParams(Contract):
    dimensions: List[Dimension]
    closed: int


class WinRateWithinChance(Contract):
    code: Literal[codes.FIND_WIN_RATE_WITHIN_CHANCE]
    params: WithinChanceParams


class BeyondChanceParams(Contract):
    dimension: Dimension
    chance: ChanceTest


class WinRateBeyondChance(Contract):
    code: Literal[codes.FIND_WIN_RATE_BEYOND_CHANCE]
    params: BeyondChanceParams


class ConcentratedParams(Contract):
    dimension: Dimension
    top: int
    of: int
    share: float
    keys: List[str]


class RevenueConcentrated(Contract):
    code: Literal[codes.FIND_REVENUE_CONCENTRATED]
    params: ConcentratedParams


class DriversParams(Contract):
    dimension: Dimension
    drivers: RevenueDrivers


class RevenueGapDrivers(Contract):
    code: Literal[codes.FIND_REVENUE_GAP_DRIVERS]
    params: DriversParams


class FastLossesParams(Contract):
    median_lost_cycle_days: int
    median_won_cycle_days: int
    lost: int
    won: int


class FastLosses(Contract):
    code: Literal[codes.FIND_FAST_LOSSES]
    params: FastLossesParams


class CoverageCount(Contract):
    bought: int = Field(description="Quantos produtos diferentes o cliente já comprou.")
    accounts: int


class CoverageParams(Contract):
    accounts: int
    products: int
    distribution: List[CoverageCount]
    most_missing: Optional[str] = Field(description="O produto que mais clientes nunca compraram.")
    most_missing_accounts: int


class AccountProductCoverage(Contract):
    code: Literal[codes.FIND_ACCOUNT_PRODUCT_COVERAGE]
    params: CoverageParams


Finding = Annotated[Union[WinRateWithinChance, WinRateBeyondChance, RevenueConcentrated, RevenueGapDrivers,
                          FastLosses, AccountProductCoverage], Field(discriminator="code")]


class HistoryEmpty(Contract):
    code: Literal[codes.NO_CLOSED_FOR_FILTER]
    params: NoParams


class Intelligence(Contract):
    meta: Meta
    ordering: Ordering
    filter: IntelligenceFilter
    options: IntelligenceOptions
    history: ClosedMetrics
    history_empty: Optional[HistoryEmpty] = Field(description="Nulo quando o recorte tem fechadas.")
    open: OpenSnapshot
    diagnostics: List[Diagnostic] = Field(description="Só os que valem no recorte, na ordem da tela.")
    findings: List[Finding] = Field(description="Só as que valem no recorte, na ordem da tela.")
    breakdowns: List[Breakdown] = Field(description="Um por dimensão, na ordem das dimensões.")
    matrix: SellerProductMatrix
    crosstabs: List[Crosstab]
    cycle_bands: List[CycleBand]
    monthly: List[MonthPoint]


class Deal(Contract):
    opportunity_id: str
    sales_agent: str
    manager: Optional[str]
    office: Optional[str]
    product: Optional[str]
    account: Optional[str]
    sector: Optional[str]
    deal_stage: DealStage
    engage_date: Optional[date]
    close_date: Optional[date]
    close_value: Optional[int] = Field(description="Valor fechado; nas sem venda, 0 por convenção do CRM.")
    sales_price: Optional[int] = Field(description="Preço de tabela (catálogo, não valor negociado).")
    cycle_days: Optional[int] = Field(description="Só nas fechadas.")
    age_days: Optional[int] = Field(description="Só nas abertas.")
    group: Optional[StateKey] = Field(description="Só nas abertas: o grupo da regra.")


class DealsEmpty(Contract):
    code: Literal[codes.NO_DEALS_FOR_FILTER]
    params: NoParams


class IntelligenceDeals(Contract):
    meta: Meta
    filter: IntelligenceFilter
    outcome: DealOutcome
    group: Optional[StateKey]
    total: int
    deals: List[Deal] = Field(description="Abertas na ordem da regra; fechadas da mais recente para a mais antiga.")
    empty: Optional[DealsEmpty]


class Seller(Contract):
    name: str
    manager: str
    office: str


class SellerList(Contract):
    sellers: List[Seller] = Field(description="Em ordem alfabética, sem métricas.")


class ErrorBody(Contract):
    detail: str = Field(description="Mensagem do núcleo, a mesma da CLI.")
    code: ErrorCode
    params: Dict[str, Union[int, str, List[str]]] = Field(description="Valores citados pelo erro, por código.")
