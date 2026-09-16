# Modelo escolhido para o protótipo: gemini-3.1-flash-lite.
# Motivo: mais barato disponível nesta conta em 16/09/2026 (US$ 0,25 entrada e
# US$ 1,50 saída por milhão de tokens, tabela pública em ai.google.dev).
# Desligamento anunciado para 07/05/2027; a data vai declarada no relatório.
# gemini-2.5-flash-lite aparece na listagem mas devolve 404 para contas novas.

"""Teste de acesso à API Gemini por REST, sem SDK.

Uso:
    python solution/00_teste_chave_gemini.py            # lista modelos Flash com generateContent
    python solution/00_teste_chave_gemini.py <modelo>   # chamada curta e contagem de tokens

A chave vem de GEMINI_API_KEY no ambiente. Se ausente, procura um arquivo .env
subindo diretórios a partir deste arquivo. A chave nunca é impressa nem aceita
por argumento.
"""

import os
import sys
from pathlib import Path

import requests

BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
TIMEOUT = 30
ENV_VAR = "GEMINI_API_KEY"


def _ler_env_arquivo(caminho: Path) -> str | None:
    """Lê só a variável de interesse de um .env, sem exportar nada."""
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        if linha.startswith("export "):
            linha = linha[len("export "):].lstrip()
        if "=" not in linha:
            continue
        nome, valor = linha.split("=", 1)
        if nome.strip() != ENV_VAR:
            continue
        valor = valor.strip()
        if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
            valor = valor[1:-1]
        return valor or None
    return None


def carregar_chave() -> str:
    chave = os.environ.get(ENV_VAR)
    if chave:
        return chave
    for pasta in [Path(__file__).resolve().parent, *Path(__file__).resolve().parents]:
        candidato = pasta / ".env"
        if candidato.is_file():
            chave = _ler_env_arquivo(candidato)
            if chave:
                return chave
    sys.exit(f"erro: {ENV_VAR} não encontrada no ambiente nem em nenhum .env acima deste arquivo")


def _erro_http(resp: requests.Response) -> None:
    """Imprime só status e mensagem de erro da API, nunca a URL (ela carrega a chave)."""
    try:
        msg = resp.json().get("error", {}).get("message", "")
    except ValueError:
        msg = resp.text[:200]
    sys.exit(f"status HTTP: {resp.status_code}\nerro: {msg}")


def listar_modelos_flash(chave: str) -> None:
    modelos = []
    params = {"pageSize": 100}
    while True:
        resp = requests.get(
            f"{BASE_URL}/models",
            params=params,
            headers={"x-goog-api-key": chave},
            timeout=TIMEOUT,
        )
        if not resp.ok:
            _erro_http(resp)
        corpo = resp.json()
        modelos.extend(corpo.get("models", []))
        token = corpo.get("nextPageToken")
        if not token:
            break
        params["pageToken"] = token

    print(f"status HTTP: {resp.status_code}")
    flash = [
        m for m in modelos
        if "flash" in m.get("name", "").lower()
        and "generateContent" in m.get("supportedGenerationMethods", [])
    ]
    print(f"modelos listados: {len(modelos)}; Flash com generateContent: {len(flash)}")
    for m in sorted(flash, key=lambda m: m["name"]):
        print(m["name"].removeprefix("models/"))


def testar_modelo(chave: str, modelo: str) -> None:
    modelo = modelo.removeprefix("models/")
    resp = requests.post(
        f"{BASE_URL}/models/{modelo}:generateContent",
        headers={"x-goog-api-key": chave, "Content-Type": "application/json"},
        json={
            "contents": [{"parts": [{"text": "Responda apenas: ok"}]}],
            "generationConfig": {"maxOutputTokens": 5},
        },
        timeout=TIMEOUT,
    )
    if not resp.ok:
        _erro_http(resp)
    uso = resp.json().get("usageMetadata", {})
    print(f"status HTTP: {resp.status_code}")
    for campo in ("promptTokenCount", "candidatesTokenCount", "totalTokenCount"):
        print(f"{campo}: {uso.get(campo)}")


def main(argv: list[str]) -> None:
    if len(argv) > 2:
        sys.exit("uso: 00_teste_chave_gemini.py [modelo]")
    chave = carregar_chave()
    if len(argv) == 2:
        testar_modelo(chave, argv[1])
    else:
        listar_modelos_flash(chave)


if __name__ == "__main__":
    main(sys.argv)
