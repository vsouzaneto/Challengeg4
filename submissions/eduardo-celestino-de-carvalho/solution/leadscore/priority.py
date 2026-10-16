"""Regras de negócio do Lead Kanban.

Os atributos fixos (produto, setor, vendedor) quase não separam ganhos de
perdas (ver G2). O sinal que o histórico sustenta é o tempo em ``Engaging``:
perdas se decidem cedo e nenhum negócio concluído levou mais que o **prazo
máximo histórico**. A regra usa isso para separar três colunas:

* **negociar** — ``Engaging`` dentro do prazo máximo, ordenado pelo valor
  potencial (preço de catálogo) e, no empate, pelo negócio mais recente;
* **qualificar** — ``Prospecting``, sem data de entrada no dataset;
* **encerrar** — ``Engaging`` com prazo excedido: confirmar ou encerrar.

Uma variante que multiplicava o preço pela taxa de ganho por idade foi testada
e descartada: a taxa usa só negócios concluídos e ignora os que travam
(``evaluate_focus.py``). Desfechos dos negócios avaliados nunca entram na regra.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from statistics import median

from .data import CLOSED_STAGES, Dataset, OPEN_STAGES, Opportunity


SNAPSHOT_DATE = date(2017, 12, 31)
START_PHASE_DAYS = 15      # 0–14 dias: Início
NEAR_LIMIT_DAYS = 90       # 90 dias até o prazo máximo: Perto do limite
LANES = ("negociar", "qualificar", "encerrar")
PHASE_START = "Início"
PHASE_RUNNING = "Em andamento"
PHASE_NEAR_LIMIT = "Perto do limite"
PHASE_EXCEEDED = "Prazo excedido"
PHASE_QUALIFY = "Sem data"


@dataclass(frozen=True)
class CycleReference:
    as_of: date
    closed: int
    won: int
    max_cycle_days: int
    median_won_days: int
    median_lost_days: int

    @property
    def base_rate(self) -> Decimal:
        return Decimal(self.won) / Decimal(self.closed)


@dataclass(frozen=True)
class Reason:
    label: str
    value: str
    detail: str


@dataclass(frozen=True)
class PriorityItem:
    opportunity: Opportunity
    manager: str
    regional_office: str
    catalog_price: Decimal
    days_in_engaging: int | None
    lane: str
    phase: str
    days_beyond_cycle: int | None
    next_action: str
    actions: tuple[str, ...]
    reasons: tuple[Reason, ...]

    @property
    def account_missing(self) -> bool:
        return self.opportunity.account is None


def _int(value: float) -> int:
    return int(Decimal(str(value)).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def _num(value: Decimal | int) -> str:
    return f"{_int(float(value)):,}".replace(",", ".")


def build_reference(dataset: Dataset, as_of: date = SNAPSHOT_DATE) -> CycleReference:
    """Prazos de negócios concluídos até ``as_of``; nada posterior entra."""
    closed = [((deal.close_date - deal.engage_date).days, deal.deal_stage == "Won")
              for deal in dataset.opportunities
              if deal.deal_stage in CLOSED_STAGES and deal.close_date <= as_of]
    if not closed:
        raise ValueError("Sem negócios concluídos até a data de referência")
    max_cycle = max(days for days, _ in closed)
    won_days = [days for days, won in closed if won]
    lost_days = [days for days, won in closed if not won]
    return CycleReference(
        as_of=as_of, closed=len(closed), won=len(won_days), max_cycle_days=max_cycle,
        median_won_days=_int(median(won_days)) if won_days else 0,
        median_lost_days=_int(median(lost_days)) if lost_days else 0,
    )


def _validate(dataset: Dataset, opportunity: Opportunity, as_of: date) -> None:
    if opportunity.deal_stage not in OPEN_STAGES:
        raise ValueError("A fila aceita apenas Prospecting ou Engaging")
    if opportunity.close_date is not None or opportunity.close_value is not None:
        raise ValueError("Oportunidade aberta contém informação de desfecho")
    if opportunity.deal_stage == "Engaging" and opportunity.engage_date is None:
        raise ValueError("Engaging precisa da data de entrada na etapa")
    if opportunity.engage_date is not None and opportunity.engage_date > as_of:
        raise ValueError("A data da etapa está após a data de referência")
    if opportunity.product not in dataset.products:
        raise ValueError("Produto ausente do catálogo")
    if opportunity.sales_agent not in dataset.sales_agents:
        raise ValueError("Vendedor ausente do cadastro")


def score_opportunity(dataset: Dataset, opportunity: Opportunity,
                      reference: CycleReference,
                      as_of: date = SNAPSHOT_DATE) -> PriorityItem:
    """Classifica um negócio aberto em uma coluna e explica o motivo."""
    _validate(dataset, opportunity, as_of)
    price = dataset.products[opportunity.product].sales_price
    limit = reference.max_cycle_days
    value_reason = Reason("Valor potencial", _num(price),
                          "Preço de tabela do produto. Define a ordem na coluna.")
    beyond = None

    if opportunity.deal_stage == "Prospecting":
        days = None
        lane, phase = "qualificar", PHASE_QUALIFY
        next_action = "Confirmar necessidade, decisor e prazo para decidir se avança para negociação."
        actions = ["Confirmar a necessidade do cliente", "Identificar o decisor",
                   "Definir o prazo de decisão", "Decidir se avança para negociação"]
        reasons = [
            Reason("Em prospecção", "sem negociação",
                   "A negociação ainda não começou; primeiro é preciso qualificar."),
            value_reason,
        ]
    else:
        days = (as_of - opportunity.engage_date).days  # validado acima
        if days > limit:
            beyond = days - limit
            lane, phase = "encerrar", PHASE_EXCEEDED
            next_action = ("Confirmar com o cliente se o negócio segue vivo e atualizar a etapa "
                           "no CRM; sem resposta, registrar como perdido.")
            actions = ["Contatar o cliente para confirmar interesse",
                       "Atualizar a etapa no CRM (seguir, ganho ou perdido)",
                       "Se seguir, registrar o próximo compromisso com data"]
            reasons = [
                Reason("Prazo excedido", f"+{beyond} dias",
                       f"Nenhuma das {_num(reference.closed)} vendas concluídas levou mais de "
                       f"{limit} dias. Este negócio está há {days}."),
                Reason("Valor parado", _num(price),
                       "Ainda conta no pipeline. Confirmar ou encerrar deixa a previsão realista."),
            ]
        else:
            lane = "negociar"
            reasons = [
                Reason("Dentro do prazo", f"faltam {limit - days} dias",
                       f"Todas as vendas fecharam em até {limit} dias. Este negócio está há {days}."),
                value_reason,
            ]
            if days < START_PHASE_DAYS:
                phase = PHASE_START
                next_action = "Confirmar interesse e decisor nesta semana: é quando a maioria das perdas acontece."
                actions = ["Confirmar interesse do cliente", "Confirmar o decisor",
                           "Marcar o próximo passo com data"]
                reasons.append(Reason(
                    PHASE_START, f"{days} dias",
                    f"Metade das vendas perdidas se decide em até {reference.median_lost_days} dias."))
            elif days < NEAR_LIMIT_DAYS:
                phase = PHASE_RUNNING
                next_action = "Definir o próximo marco com data e registrar no CRM."
                actions = ["Confirmar o próximo marco com o cliente",
                           "Registrar o plano de contato no CRM"]
                reasons.append(Reason(
                    PHASE_RUNNING, f"{days} dias",
                    "Já passou da fase em que mais se perde. Manter o ritmo."))
            else:
                phase = PHASE_NEAR_LIMIT
                remaining = limit - days
                next_action = ("Buscar a decisão agora: proposta final, objeções restantes e data "
                               "de fechamento. Negócios nesta fase costumam travar.")
                actions = ["Enviar ou revisar a proposta final", "Tratar as objeções restantes",
                           "Combinar a data de decisão com o cliente"]
                reasons.append(Reason(
                    PHASE_NEAR_LIMIT, f"{days} dias",
                    f"Faltam {remaining} dias para o prazo máximo. Nesta fase os negócios costumam travar."))

    if opportunity.account is None:
        actions.append("Identificar e registrar a conta relacionada")
        reasons.append(Reason(
            "Conta pendente", "sem cadastro",
            "Sem empresa cadastrada no CRM: cadastrar. Não muda a ordem."))

    agent = dataset.sales_agents[opportunity.sales_agent]
    return PriorityItem(
        opportunity=opportunity, manager=agent.manager, regional_office=agent.regional_office,
        catalog_price=price, days_in_engaging=days, lane=lane, phase=phase,
        days_beyond_cycle=beyond, next_action=next_action,
        actions=tuple(actions), reasons=tuple(reasons),
    )


def _order(item: PriorityItem) -> tuple:
    # Valor potencial primeiro. Em "negociar", o empate favorece o negócio mais
    # recente: no backtest, negócios novos resolveram mais e os antigos travaram.
    days = item.days_in_engaging or 0
    tie = days if item.lane == "negociar" else -days
    return (LANES.index(item.lane), -item.catalog_price, tie, item.opportunity.opportunity_id)


def build_queue(dataset: Dataset, as_of: date = SNAPSHOT_DATE,
                reference: CycleReference | None = None) -> tuple[PriorityItem, ...]:
    """Negociar, qualificar e encerrar, cada coluna ordenada pelo valor potencial."""
    reference = reference or build_reference(dataset, as_of)
    items = [score_opportunity(dataset, opportunity, reference, as_of)
             for opportunity in dataset.opportunities
             if opportunity.deal_stage in OPEN_STAGES]
    return tuple(sorted(items, key=_order))


def filter_queue(items: tuple[PriorityItem, ...], *, regional_office: str | None = None,
                 manager: str | None = None, sales_agent: str | None = None,
                 lanes: frozenset[str] | None = None,
                 account_missing: bool | None = None,
                 search: str = "") -> tuple[PriorityItem, ...]:
    """Filtra mantendo a ordem calculada sobre a carteira inteira."""
    term = search.casefold().strip()
    return tuple(item for item in items
                 if (regional_office is None or item.regional_office == regional_office)
                 and (manager is None or item.manager == manager)
                 and (sales_agent is None or item.opportunity.sales_agent == sales_agent)
                 and (lanes is None or item.lane in lanes)
                 and (account_missing is None or item.account_missing == account_missing)
                 and (not term or any(term in value.casefold() for value in (
                     item.opportunity.opportunity_id,
                     item.opportunity.product,
                     item.opportunity.account or "",
                     item.opportunity.sales_agent,
                 ))))
