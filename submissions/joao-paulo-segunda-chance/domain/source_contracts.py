"""Contratos de fonte sem acesso a arquivos, pandas, rede ou banco."""
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation


class ContractError(ValueError):
    pass


@dataclass(frozen=True)
class Field:
    kind: str = 'text'
    nullable: bool = False


def fields(text='', integer='', numeric='', boolean='', dates='', timestamps='', nullable=''):
    output = {}
    optional = set(nullable.split())
    for kind, names in [('text', text), ('integer', integer), ('numeric', numeric), ('boolean', boolean),
                        ('date', dates), ('timestamp', timestamps)]:
        for name in names.split(): output[name] = Field(kind, name in optional)
    return output


CONTRACT_VERSION = '1.0.0'
CONTRACTS = {
    'accounts': fields(text='account_id account_name industry country referral_source plan_tier',
                       integer='seats', boolean='is_trial churn_flag', dates='signup_date'),
    'subscriptions': fields(text='subscription_id account_id plan_tier billing_frequency', integer='seats',
                            numeric='mrr_amount arr_amount', boolean='is_trial upgrade_flag downgrade_flag churn_flag auto_renew_flag',
                            dates='start_date end_date', nullable='end_date'),
    'usage': fields(text='usage_id subscription_id feature_name', integer='usage_count usage_duration_secs error_count',
                    boolean='is_beta_feature', dates='usage_date'),
    'support': fields(text='ticket_id account_id priority', numeric='resolution_time_hours satisfaction_score',
                      integer='first_response_time_minutes', boolean='escalation_flag',
                      timestamps='submitted_at closed_at', nullable='closed_at resolution_time_hours satisfaction_score'),
    'churn': fields(text='churn_event_id account_id reason_code feedback_text', numeric='refund_amount_usd',
                    boolean='preceding_upgrade_flag preceding_downgrade_flag is_reactivation', dates='churn_date', nullable='feedback_text'),
}


def parse_record(source_type: str, raw: dict) -> dict:
    contract = CONTRACTS[source_type]
    missing = set(contract) - set(raw)
    extra = set(raw) - set(contract)
    if missing or extra: raise ContractError(f'Colunas ausentes={sorted(missing)} extras={sorted(extra)}')
    result = {}
    for name, field in contract.items():
        value = '' if raw[name] is None else str(raw[name]).strip()
        if value == '':
            if field.nullable: result[name] = None; continue
            raise ContractError(f'{name}: valor obrigatório ausente')
        try:
            if field.kind == 'text': parsed = value
            elif field.kind == 'boolean':
                if value.lower() not in ('true', 'false'): raise ValueError('booleano inválido')
                parsed = value.lower() == 'true'
            elif field.kind == 'integer':
                number = Decimal(value)
                if not number.is_finite() or number != number.to_integral_value() or number < 0:
                    raise ValueError('inteiro não negativo esperado')
                parsed = int(number)
            elif field.kind == 'numeric':
                parsed = Decimal(value)
                if not parsed.is_finite() or parsed < 0: raise ValueError('número não negativo finito esperado')
            elif field.kind == 'date': parsed = date.fromisoformat(value)
            else: parsed = datetime.fromisoformat(value)
        except (ValueError, InvalidOperation) as exc:
            raise ContractError(f'{name}: {exc}') from exc
        result[name] = parsed
    return result
