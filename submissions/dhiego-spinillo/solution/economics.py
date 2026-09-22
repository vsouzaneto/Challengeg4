"""Cenários de capacidade e despesa evitada; nenhuma entrada vem da avaliação ML."""
from pydantic import BaseModel, ConfigDict, Field


class Assumptions(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, allow_inf_nan=False)
    annual_tickets: float = Field(default=30000, ge=0, le=100000000)
    eligible_pct: float = Field(default=40, ge=0, le=100)
    adoption_pct: float = Field(default=80, ge=0, le=100)
    net_minutes: float = Field(default=4, ge=-120, le=120)
    salary: float = Field(default=4000, ge=0, le=1000000)
    loaded_factor: float = Field(default=1.7, ge=1, le=10)
    productive_hours: float = Field(default=160, gt=0, le=744)
    realization_pct: float = Field(default=50, ge=0, le=100)
    monthly_cost: float = Field(default=500, ge=0, le=10000000)
    setup_cost: float = Field(default=6000, ge=0, le=100000000)


PRESETS = {
    'conservador': {'eligible_pct': 20, 'adoption_pct': 60, 'net_minutes': 2},
    'base': {'eligible_pct': 40, 'adoption_pct': 80, 'net_minutes': 4},
    'otimista': {'eligible_pct': 60, 'adoption_pct': 90, 'net_minutes': 6},
}


def estimate(a: Assumptions):
    tickets = a.annual_tickets / 12 * a.eligible_pct / 100 * a.adoption_pct / 100
    hours = tickets * a.net_minutes / 60
    hourly_cost = a.salary * a.loaded_factor / a.productive_hours
    capacity_value = hours * hourly_cost
    avoided_expense = max(capacity_value, 0) * a.realization_pct / 100
    # Trabalho adicional continua sendo custo econômico, mesmo sem desembolso.
    additional_work_value = max(-capacity_value, 0)
    net_cash = avoided_expense - a.monthly_cost
    total_cost = a.setup_cost + 12 * a.monthly_cost
    cash_per_minute = tickets / 60 * hourly_cost * a.realization_pct / 100
    return {
        'effective_tickets_month': tickets,
        'hours_month': hours, 'fte_capacity': hours / a.productive_hours,
        'hourly_cost': hourly_cost, 'capacity_value_month': capacity_value,
        'avoided_expense_month': avoided_expense,
        'additional_work_value_month': additional_work_value,
        'net_cash_month': net_cash,
        'first_year_net_cash': 12 * avoided_expense - total_cost,
        'roi_12m_pct': (12 * avoided_expense - total_cost) / total_cost * 100 if total_cost else None,
        'payback_months': a.setup_cost / net_cash if net_cash > 0 else None,
        'break_even_minutes_12m': (a.monthly_cost + a.setup_cost / 12) / cash_per_minute if cash_per_minute > 0 else None,
    }
