"""Dublês de HTTP para testar a cadeia de LLM sem rede."""

import requests


def ok(texto: str, tokens: int = 50) -> dict:
    return {"choices": [{"message": {"content": texto}}], "usage": {"total_tokens": tokens}}


class RespostaFalsa:
    def __init__(self, status: int, corpo=None, headers=None):
        self.status_code, self._corpo, self.headers = status, corpo, headers or {}

    def json(self):
        if isinstance(self._corpo, Exception):
            raise self._corpo
        return self._corpo


class SessaoFalsa:
    """roteiro: {"groq": [RespostaFalsa | Exception, ...], "googleapis": [...]} consumidos em ordem."""

    def __init__(self, roteiro: dict):
        self.roteiro = {k: list(v) for k, v in roteiro.items()}
        self.chamadas: list[str] = []

    def post(self, url, headers=None, json=None, timeout=None):
        chave = next(k for k in self.roteiro if k in url)
        self.chamadas.append(chave)
        item = self.roteiro[chave].pop(0)
        if isinstance(item, Exception):
            raise item
        return item


TIMEOUT = requests.Timeout("simulado")
