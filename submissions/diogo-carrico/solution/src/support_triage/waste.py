"""Parametric estimate of the triage time automation could recover.

The dataset cannot measure waste: there is no ticket creation time, the resolution timestamps
contradict the response ones, and satisfaction is uniform. So the estimate is a formula whose
every input is labelled with its source and given a low, base and high value.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Assumption:
    low: float
    base: float
    high: float
    unit: str
    source: str


# "Pessimistic" takes the side of each range that lowers the saving; for misroutes and rework that is the high side.
LOWERS_SAVING_WHEN_HIGH = {"misroute_rate", "rework_minutes"}

ASSUMPTIONS: dict[str, Assumption] = {
    "tickets_per_month": Assumption(
        706,
        2500,
        2500,
        "tickets/mês",
        "Brief: 30.000/ano. Baixo: os 8.469 registros do Dataset 1 tratados como um ano",
    ),
    "auto_route_share": Assumption(
        0.40,
        0.50,
        0.70,
        "fração",
        "Previsão P5 do Diogo (50%); será trocada pela cobertura medida no classificador (fase 5)",
    ),
    "triage_minutes": Assumption(
        2,
        4,
        6,
        "min/ticket",
        "Premissa: tempo de ler, classificar e encaminhar um ticket. Não medido; validar cronometrando uma semana de triagem",
    ),
    "misroute_rate": Assumption(
        0.02,
        0.05,
        0.08,
        "fração",
        "Premissa ligada ao alvo de precisão de 95% (hipótese 3.2 do Diogo)",
    ),
    "rework_minutes": Assumption(
        5,
        10,
        20,
        "min/erro",
        "Premissa: retriagem e transferência de um ticket mal roteado",
    ),
    "hourly_cost_brl": Assumption(
        35,
        45,
        60,
        "R$/hora",
        "Premissa: custo por hora de um agente, com encargos. Validar com RH",
    ),
}


def with_measured_routing(
    metrics: dict, assumptions: dict[str, Assumption] = ASSUMPTIONS
) -> dict[str, Assumption]:
    """Replace the assumed routing share and misroute rate with what the full triage flow measured on the
    test set (policy, guard, classifier, thresholds, enabled classes). The high side is the same flow if the
    pilot confirms every class; the low side keeps the original premise."""
    e2e = metrics["end_to_end_dataset2_test"]
    lo_prec, hi_prec = e2e["precision_ci95"]
    out = dict(assumptions)
    out["auto_route_share"] = Assumption(
        min(assumptions["auto_route_share"].low, e2e["coverage"]),
        e2e["coverage"],
        e2e["if_every_class_is_enabled"]["coverage"],
        "fração",
        "Medido no Dataset 2 (tickets de TI): fluxo completo da demo no teste, só com as classes que provaram 95% "
        "de precisão. Numa operação de suporte ao cliente só vale depois de treinar com os tickets dela. "
        "Baixo: premissa original. Alto: o mesmo fluxo se o piloto comprovar as classes que faltam",
    )
    out["misroute_rate"] = Assumption(
        1 - hi_prec,
        1 - e2e["precision"],
        1 - lo_prec,
        "fração",
        "Medido no Dataset 2: 1 − precisão dos tickets roteados pelo fluxo completo no teste, com o intervalo de 95%",
    )
    return out


def hours_saved(p: dict[str, float]) -> float:
    """Triage hours saved per month, net of the rework that misrouted tickets cause."""
    routed = p["tickets_per_month"] * p["auto_route_share"]
    saved = routed * p["triage_minutes"] / 60
    rework = routed * p["misroute_rate"] * p["rework_minutes"] / 60
    return saved - rework


def scenario(
    side: str, assumptions: dict[str, Assumption] = ASSUMPTIONS
) -> dict[str, float]:
    if side == "base":
        return {k: a.base for k, a in assumptions.items()}
    low_side = side == "pessimistic"
    return {
        k: (a.high if (k in LOWERS_SAVING_WHEN_HIGH) == low_side else a.low)
        for k, a in assumptions.items()
    }


def estimate(assumptions: dict[str, Assumption] = ASSUMPTIONS) -> dict:
    out: dict = {
        "assumptions": {k: asdict(a) for k, a in assumptions.items()},
        "scenarios": {},
        "sensitivity": [],
    }
    for side in ("pessimistic", "base", "optimistic"):
        p = scenario(side, assumptions)
        h = hours_saved(p)
        out["scenarios"][side] = {
            "hours_per_month": h,
            "brl_per_month": h * p["hourly_cost_brl"],
            "fte_at_160_hours": h / 160,
        }
    base = scenario("base", assumptions)
    base_brl = hours_saved(base) * base["hourly_cost_brl"]
    for k, a in assumptions.items():
        values = []
        for v in (a.low, a.high):
            p = {**base, k: v}
            values.append(hours_saved(p) * p["hourly_cost_brl"])
        out["sensitivity"].append(
            {
                "assumption": k,
                "brl_at_low": values[0],
                "brl_at_high": values[1],
                "swing_brl": abs(values[1] - values[0]),
            }
        )
    out["sensitivity"].sort(key=lambda s: s["swing_brl"], reverse=True)
    out["base_brl_per_month"] = base_brl
    return out
