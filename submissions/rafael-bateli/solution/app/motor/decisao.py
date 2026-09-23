"""A decisão sobre um ticket e o rastro de cada etapa (o que a tela explica)."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field


@dataclass
class Etapa:
    nome: str
    resultado: str
    motivo: str
    ms: float


@dataclass
class Decisao:
    operacao: str                      # "d1" (suporte ao cliente) | "d2" (service desk)
    ticket_id: str
    rota: str = ""                     # D1: 1A, 1B, 2, 3 · D2: auto, triagem, sensivel, detalhes
    rota_rotulo: str = ""
    motivo: str = ""
    prioridade: str | None = None
    prioridade_declarada: str | None = None
    sla_horas: float | None = None
    classe: str | None = None
    confianca: float | None = None
    top3: list = field(default_factory=list)
    similares: list = field(default_factory=list)
    marcacoes: list = field(default_factory=list)
    gatilhos: list = field(default_factory=list)
    permite_rascunho: bool = False
    permite_dossie: bool = False
    motivo_permissao: str = ""
    rastro: list = field(default_factory=list)
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

    def registrar(self, nome: str, resultado: str, motivo: str, t0: float) -> None:
        self.etapa(nome, resultado, motivo, (time.perf_counter() - t0) * 1000)

    def etapa(self, nome: str, resultado: str, motivo: str, ms: float) -> None:
        self.rastro.append(Etapa(nome, resultado, motivo, round(ms, 3)))
