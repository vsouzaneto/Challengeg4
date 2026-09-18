"""Regras de decisão do ciclo TO-BE (docs/process/03-to-be.md).

Funções puras, sem I/O, usadas pela estratégia (G5) e pelo Decision Gate (G6).
"""

from dataclasses import dataclass
from math import ceil, sqrt

from scipy import stats

SESOI_PP = 1.0  # régua do Douglas: ±1 p.p. de taxa de engajamento
MIN_COMPLETENESS = 0.95

REQUIRED_CONTRACT_FIELDS = (
    "campaign_id", "crm_deal_id", "creator_id", "custo_total", "objetivo", "hypothesis_id",
    "metrica_primaria", "regua", "break_even", "grupo_comparacao", "cupom", "utm",
    "aprovado_por", "aprovado_em",
)


def break_even_fee(incremental_sales: float, unit_margin: float, production_cost: float = 0.0) -> float:
    """Fee máximo que um contrato pode custar sem dar prejuízo.

    fee_max = vendas incrementais × margem unitária − custo de produção.
    Todos os insumos vêm do pré-registro, com procedência declarada; nenhum é inventado aqui.
    """
    if incremental_sales < 0 or unit_margin < 0 or production_cost < 0:
        raise ValueError("insumos do break-even não podem ser negativos")
    return incremental_sales * unit_margin - production_cost


def sales_to_break_even(fee: float, unit_margin: float, production_cost: float = 0.0) -> float:
    """Vendas incrementais necessárias para o contrato empatar: (fee + produção) / margem unitária."""
    if unit_margin <= 0:
        raise ValueError("a margem unitária precisa ser positiva")
    if fee < 0 or production_cost < 0:
        raise ValueError("fee e produção não podem ser negativos")
    return (fee + production_cost) / unit_margin


def engagement_value_ceiling(views_per_post: float, lift_pp: float, value_per_interaction: float,
                             posts: int = 1) -> float:
    """Valor máximo gerado pelo aumento de engajamento: views × lift × valor de cada interação."""
    return views_per_post * (lift_pp / 100) * value_per_interaction * posts


def sample_size_per_arm(sd_pp: float, delta_pp: float = SESOI_PP, alpha: float = 0.05, power: float = 0.80) -> int:
    """Posts por braço para detectar `delta_pp` numa comparação de duas médias (bicaudal)."""
    if sd_pp <= 0 or delta_pp <= 0:
        raise ValueError("desvio e delta precisam ser positivos")
    z = stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(power)
    return ceil(2 * (z * sd_pp / delta_pp) ** 2)


@dataclass(frozen=True)
class CycleResult:
    effect_pp: float
    ci95_low: float
    ci95_high: float
    execution_ok: bool = True
    completeness: float = 1.0
    return_over_break_even: float | None = None  # None quando o teste não tem custo (ex.: formato)


def cycle_decision(r: CycleResult, sesoi: float = SESOI_PP) -> tuple[str, str]:
    """Decisão do fechamento de 30 dias: Escalar, Replicar, Iterar ou Parar, com o motivo."""
    if not r.execution_ok or r.completeness < MIN_COMPLETENESS:
        return "Iterar", "execução ou completude do dado abaixo do mínimo; o resultado não é confiável"
    pays = r.return_over_break_even is None or r.return_over_break_even > 0
    if r.ci95_low > -sesoi and r.ci95_high < sesoi:
        return "Parar", f"efeito equivalente a zero (IC 95% dentro de ±{sesoi:g} p.p.)"
    if r.return_over_break_even is not None and r.return_over_break_even <= 0:
        return "Parar", "retorno abaixo do break-even"
    if r.ci95_high <= -sesoi:
        return "Parar", "efeito negativo relevante"
    if r.ci95_high < sesoi:
        return "Parar", f"ganho relevante descartado (IC 95% não alcança +{sesoi:g} p.p.)"
    if r.ci95_low >= sesoi and pays:
        money = ("teste sem custo adicional" if r.return_over_break_even is None
                 else "retorno acima do break-even")
        return "Escalar", f"efeito acima da régua (IC 95% ≥ +{sesoi:g} p.p.); {money}"
    return "Replicar", "resultado promissor, mas o intervalo ainda cruza a régua"


def contract_gaps(contract: dict) -> list[str]:
    """Campos obrigatórios ausentes ou vazios num contrato (Gate 1)."""
    return [f for f in REQUIRED_CONTRACT_FIELDS if contract.get(f) in (None, "", [])]


def ci_from_arms(mean_a: float, sd_a: float, n_a: int, mean_b: float, sd_b: float, n_b: int) -> tuple[float, float, float]:
    """Diferença A−B e IC 95% (aproximação normal)."""
    diff = mean_a - mean_b
    se = sqrt(sd_a**2 / n_a + sd_b**2 / n_b)
    z = stats.norm.ppf(0.975)
    return diff, diff - z * se, diff + z * se
