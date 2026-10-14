"""Preparação determinística de registros; nenhuma dependência do banco."""
import json
from datetime import date, datetime
from decimal import Decimal
from domain.source_contracts import parse_record, ContractError


def json_value(value):
    if isinstance(value, (date, datetime)): return value.isoformat()
    if isinstance(value, Decimal): return str(value)
    raise TypeError(type(value).__name__)


def prepare_row(source_type, row_number, raw):
    errors = []
    normalized = None
    try:
        normalized = json.loads(json.dumps(parse_record(source_type, raw), default=json_value))
    except ContractError as exc:
        errors.append(str(exc))
    # The storage adapter computes a canonical JSON hash; exact file bytes
    # retain their independent SHA-256 and are not reconstructed from rows.
    return dict(row_number=row_number,content=raw,normalized_content=normalized,
                validation_errors=errors)
