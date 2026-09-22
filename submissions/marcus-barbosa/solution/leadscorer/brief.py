"""Brief de segunda-feira do vendedor: poucos itens, cada um com o porquê e o próximo passo.

Orçamento de atenção (decisão de produto): no máximo 7 itens, na ordem
1. Focar agora (até 3, por score),
2. Primeiras duas semanas (até 2, por valor),
3. Última janela (até 1, por valor),
4. Confirmar se está vivo (até 1, o de maior valor),
5. Cadastrar conta (até 1, o acionável de maior valor esperado sem conta, com ação própria),
6. Qualificar ou descartar (até 1, por valor).
Se sobrar espaço, completa com Manter follow-up e depois com mais itens de Qualificar.
Um deal só entra uma vez: os blocos seguintes ignoram os já escolhidos.
"""
from __future__ import annotations

import pandas as pd

from .scoring import CAT_ALIVE, CAT_CRITICAL, CAT_FOCUS, CAT_FOLLOW, CAT_LAST, CAT_QUALIFY, SUPPORT_OK, money

MAX_ITEMS = 7
ACAO_CADASTRO = "Cadastrar a conta no CRM hoje; o deal volta para a fila com score."


def _items(df: pd.DataFrame, tipo: str, n: int, chosen: set, acao: str | None = None) -> list[dict]:
    out = []
    for _, r in df[~df["opportunity_id"].isin(chosen)].head(n).iterrows():
        chosen.add(r["opportunity_id"])
        out.append({"tipo": tipo, "deal": r["opportunity_id"], "conta": r["account"] if isinstance(r["account"], str) else "(sem conta)",
                    "produto": r["product"], "valor": r["list_value"], "score": None if pd.isna(r["score"]) else int(r["score"]),
                    "idade": None if pd.isna(r["age_days"]) else int(r["age_days"]), "porque": r["explanation"], "acao": acao or r["next_step"]})
    return out


def seller_brief(scored_agent: pd.DataFrame) -> dict:
    s = scored_agent
    ok = s[s["support"] == SUPPORT_OK]
    chosen: set = set()
    items: list[dict] = []
    items += _items(s[s["category"] == CAT_FOCUS].sort_values("score", ascending=False), "Focar agora", 3, chosen)
    items += _items(s[s["category"] == CAT_CRITICAL].sort_values("list_value", ascending=False), "Primeiras duas semanas", 2, chosen)
    items += _items(s[s["category"] == CAT_LAST].sort_values("list_value", ascending=False), "Última janela", 1, chosen)
    items += _items(s[s["category"] == CAT_ALIVE].sort_values("list_value", ascending=False), "Confirmar se está vivo", 1, chosen)
    items += _items(ok[ok["needs_account"]].sort_values("expected_value", ascending=False), "Cadastrar conta", 1, chosen, ACAO_CADASTRO)
    items += _items(s[s["category"] == CAT_QUALIFY].sort_values("list_value", ascending=False), "Qualificar ou descartar", 1, chosen)
    if len(items) < MAX_ITEMS:
        items += _items(s[s["category"] == CAT_FOLLOW].sort_values("score", ascending=False), "Manter follow-up", MAX_ITEMS - len(items), chosen)
    if len(items) < MAX_ITEMS:
        items += _items(s[s["category"] == CAT_QUALIFY].sort_values("list_value", ascending=False), "Qualificar ou descartar", MAX_ITEMS - len(items), chosen)
    resumo = {
        "abertos": int(len(s)), "acionaveis": int(len(ok)), "focar": int((s["category"] == CAT_FOCUS).sum()),
        "ultima_janela": int((s["category"] == CAT_LAST).sum()), "confirmar_vivo": int((s["category"] == CAT_ALIVE).sum()),
        "sem_conta": int(s["needs_account"].sum()), "valor_esperado": float(ok["expected_value"].sum()), "valor_lista_acionavel": float(ok["list_value"].sum()),
    }
    abertura = (f"{resumo['abertos']} deals abertos, {resumo['acionaveis']} com chance estimável somando {money(resumo['valor_esperado'])} de valor esperado em 90 dias. "
                f"{resumo['confirmar_vivo']} estão além de 138 dias e precisam de confirmação antes de qualquer esforço; {resumo['sem_conta']} não têm conta no CRM.")
    return {"resumo": resumo, "abertura": abertura, "itens": items[:MAX_ITEMS]}
