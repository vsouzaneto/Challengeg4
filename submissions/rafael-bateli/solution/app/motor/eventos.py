"""Registro append-only (JSONL) do que o agente faz: cada correção vira dado para a IA aprender."""

from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path

from . import config
from .logs import registrar

TIPOS = {"aprovar", "editar", "descartar", "fila_errada", "prioridade_alterada", "auditoria_certo", "auditoria_errado"}


class Registro:
    def __init__(self, caminho: Path | None = None):
        self.caminho = caminho or config.local_dir() / "eventos.jsonl"
        self.pendentes: list[dict] = []

    def gravar(self, tipo: str, **dados) -> bool:
        if tipo not in TIPOS:
            raise ValueError(f"tipo de evento desconhecido: {tipo}")
        self.pendentes.append({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "tipo": tipo, **dados})
        try:
            with open(self.caminho, "a", encoding="utf-8") as f:
                for e in self.pendentes:
                    f.write(json.dumps(e, ensure_ascii=False) + "\n")
            self.pendentes = []
            return True
        except OSError as e:
            registrar("ERROR", "eventos", "falha_eventos", motivo=type(e).__name__, pendentes=len(self.pendentes))
            return False

    def ler(self) -> list[dict]:
        if not Path(self.caminho).is_file():
            return []
        saida = []
        for linha in Path(self.caminho).read_text(encoding="utf-8").splitlines():
            try:
                saida.append(json.loads(linha))
            except json.JSONDecodeError:
                continue
        return saida


def _taxa(num: int, den: int) -> float | None:
    return round(num / den, 4) if den else None


def metricas(evs: list[dict]) -> dict:
    rev = [e for e in evs if e["tipo"] in ("aprovar", "editar", "descartar")]
    rev_llm = [e for e in rev if e.get("origem") == "llm"]
    aud = [e for e in evs if e["tipo"] in ("auditoria_certo", "auditoria_errado")]
    return {
        "revisados": len(rev),
        "aprovacao_sem_edicao": _taxa(sum(e["tipo"] == "aprovar" for e in rev), len(rev)),
        "aprovacao_sem_edicao_llm": _taxa(sum(e["tipo"] == "aprovar" for e in rev_llm), len(rev_llm)),
        "revisados_llm": len(rev_llm),
        "descartes": sum(e["tipo"] == "descartar" for e in rev),
        "devolucoes_por_classe": dict(Counter(e.get("classe_prevista") for e in evs if e["tipo"] == "fila_errada")),
        "prioridades_alteradas": sum(e["tipo"] == "prioridade_alterada" for e in evs),
        "auditoria_n": len(aud),
        "auditoria_acerto": _taxa(sum(e["tipo"] == "auditoria_certo" for e in aud), len(aud)),
    }
