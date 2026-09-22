"""Economics por procedimento: minutos humanos, sucesso e custo das exceções."""
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProcessAssumptions(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, allow_inf_nan=False)
    monthly_tickets: float = Field(default=2500, ge=0, le=1000000)
    autonomous_tickets: float = Field(default=50, ge=0, le=1000000)
    prepared_tickets: float = Field(default=1000, ge=0, le=1000000)
    adoption_pct: float = Field(default=80, ge=0, le=100)
    autonomous_before: float = Field(default=12, ge=0, le=240)
    autonomous_residual: float = Field(default=1, ge=0, le=240)
    success_pct: float = Field(default=80, ge=0, le=100)
    failure_extra: float = Field(default=2, ge=0, le=240)
    prepared_before: float = Field(default=12, ge=0, le=240)
    prepared_after: float = Field(default=7, ge=0, le=240)
    salary: float = Field(default=4000, ge=0, le=1000000)
    loaded_factor: float = Field(default=1.7, ge=1, le=10)
    productive_hours: float = Field(default=160, gt=0, le=744)
    realization_pct: float = Field(default=50, ge=0, le=100)
    monthly_cost: float = Field(default=500, ge=0, le=10000000)
    setup_cost: float = Field(default=6000, ge=0, le=100000000)

    @model_validator(mode='after')
    def disjoint_volumes(self):
        if self.autonomous_tickets + self.prepared_tickets > self.monthly_tickets:
            raise ValueError('A soma dos caminhos não pode ultrapassar o volume mensal. Conte cada ticket uma vez.')
        return self


def process_estimate(a: ProcessAssumptions):
    adoption = a.adoption_pct / 100
    success = a.success_pct / 100
    autonomous_net = success * (a.autonomous_before - a.autonomous_residual) - (1-success) * a.failure_extra
    prepared_net = a.prepared_before - a.prepared_after
    auto_hours = a.autonomous_tickets * adoption * autonomous_net / 60
    prepared_hours = a.prepared_tickets * adoption * prepared_net / 60
    total_hours = auto_hours + prepared_hours
    hourly_cost = a.salary * a.loaded_factor / a.productive_hours
    value = total_hours * hourly_cost
    expense = max(value, 0) * a.realization_pct / 100
    monthly_net = expense - a.monthly_cost
    costs = a.setup_cost + 12*a.monthly_cost
    hourly_cash = hourly_cost * a.realization_pct / 100
    return {
        'autonomous_expected_net_minutes': autonomous_net,
        'prepared_net_minutes': prepared_net,
        'autonomous_hours': auto_hours, 'prepared_hours': prepared_hours,
        'human_tickets': a.monthly_tickets-a.autonomous_tickets-a.prepared_tickets,
        'autonomous_completed_month': a.autonomous_tickets*adoption*success,
        'autonomous_failed_month': a.autonomous_tickets*adoption*(1-success),
        'hours_month': total_hours, 'capacity_value_month': value,
        'avoided_expense_month': expense, 'net_cash_month': monthly_net,
        'first_year_net_cash': 12*expense-costs,
        'roi_12m_pct': (12*expense-costs)/costs*100 if costs else None,
        'payback_months': a.setup_cost/monthly_net if monthly_net>0 else None,
        'break_even_hours_month': (a.monthly_cost+a.setup_cost/12)/hourly_cash if hourly_cash>0 else None,
        'additional_work_value_month': max(-value,0),
    }
