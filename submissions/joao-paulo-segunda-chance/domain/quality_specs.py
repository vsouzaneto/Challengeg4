from datetime import date
from decimal import Decimal
from enum import Enum


class State(str, Enum):
    SATISFIED = 'satisfied'
    NOT_SATISFIED = 'not_satisfied'
    INDETERMINATE = 'indeterminate'


def evaluate_churn(flag: bool, has_churn: bool, has_reactivation: bool) -> State:
    """Confirma concordância sobre churn observado, nunca infere status atual.

    Histórico sem evento não prova ausência de churn. Reativação é outra
    ocorrência, não substitui o cancelamento faltante. Mesmo concordância
    positiva não fornece data ou receita de um cancelamento cadastral.
    """
    if flag and has_churn:
        return State.SATISFIED
    return State.INDETERMINATE


def compare_usage(current: Decimal | None, previous: Decimal | None,
                  sufficient_coverage: bool) -> Decimal | None:
    """Queda relativa em duas janelas de MESMA duração e cobertura confirmada."""
    if not sufficient_coverage or current is None or previous is None:
        return None
    if previous <= 0 or current < 0:
        return None
    return Decimal('1') - current / previous


def contract_interval(reference: date, start: date | None, end: date | None) -> State:
    """Convenção PROPOSTA: intervalo [início, término); revisar contrato da fonte.

    Término ausente é vínculo aberto segundo a fonte, não prova de atividade.
    """
    if start is None or (end is not None and end < start):
        return State.INDETERMINATE
    return State.SATISFIED if reference >= start and (end is None or reference < end) else State.NOT_SATISFIED
