"""Erros com mensagem para o usuário. A API traduz cada classe em um status HTTP."""
from __future__ import annotations

from typing import Any


class LeadScorerError(Exception):
    """Base: a mensagem é exibida como está, na CLI e na API. `code` e `params`
    são o mesmo erro como dado (`codes.ERROR_CODES`), para quem apresenta."""

    def __init__(self, message: str, *, code: str, **params: Any) -> None:
        super().__init__(message)
        self.code = code
        self.params = params


class DataError(LeadScorerError):
    """Arquivo ausente, inválido ou com rótulo desconhecido (API: 503)."""


class PolicyError(LeadScorerError):
    """Parâmetro inválido, como o as_of (API: 422)."""


class NotFoundError(LeadScorerError):
    """Vendedor ou oportunidade inexistente (API: 404)."""
