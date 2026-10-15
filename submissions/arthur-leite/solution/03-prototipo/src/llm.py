"""
Camada opcional de LLM (Google Gemini): rascunho de resposta para o agente revisar.

Por que o LLM fica só aqui, e não na classificação: no benchmark (benchmark/outputs/benchmark.md),
o Gemini classificou bem pior que um modelo simples treinado no histórico da empresa. Onde o LLM
agrega é em REDIGIR, a partir de casos parecidos já resolvidos.

Sem GEMINI_API_KEY, ou com a API indisponível, a função devolve None e o app segue funcionando.

IMPORTANTE: passar o texto ORIGINAL do ticket, nunca o pré-processado. O pré-processamento
remove stopwords, incluindo "not", e isso já inverteu o sentido num teste ("monitor is not
detected" virou "monitor was detected" no rascunho).
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

MODELOS = ["gemini-3.5-flash-lite", "gemini-flash-lite-latest"]   # em ordem de preferência


def _chave() -> str | None:
    """Ordem: variável de ambiente / .env (local) → st.secrets (Streamlit Cloud)."""
    if os.getenv("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"]
    try:
        import streamlit as st
        return st.secrets.get("GEMINI_API_KEY")
    except Exception:
        return None


def disponivel() -> bool:
    return bool(_chave())


def rascunhar_resposta(ticket: str, categoria: str, similares: list[dict], alertas: list[str]) -> str | None:
    if not disponivel():
        return None
    from google import genai
    from google.genai import types

    casos = "\n".join(f"- [{s['categoria']}] {s['texto'][:400]}" for s in similares)
    prompt = f"""You are drafting a reply for an IT service desk AGENT to review before sending. Never claim an action was done.

Ticket (original text from the user): {ticket[:1500]}
Routed to queue: {categoria}
Sensitive-policy flags: {', '.join(alertas) or 'none'}
Similar past tickets in this company:
{casos}

Write in English, max 90 words:
1. One sentence acknowledging the request in plain language.
2. The concrete information the agent still needs from the user (bullet list, max 3).
3. Next step. If there is any policy flag, state that it requires approval/human handling.
Do not invent names, ticket numbers, links or deadlines."""
    cliente = genai.Client(api_key=_chave())
    cfg = types.GenerateContentConfig(temperature=0.2, max_output_tokens=300)
    for modelo in MODELOS:
        try:
            return cliente.models.generate_content(model=modelo, contents=prompt, config=cfg).text.strip()
        except Exception:
            continue
    return None
