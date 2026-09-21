"""Visão do gerente e achados de RevOps. Funções puras sobre o pipeline pontuado.

O que entra aqui e não entra no score do deal (decisão 10): carga de deals abertos por
vendedor (H3: correlação negativa com conversão), share de deals sem conta por vendedor
(H17) e taxa histórica do vendedor com n, mostrada como contexto, nunca como nota.
"""
from __future__ import annotations

import pandas as pd

from .calibration import WINDOW_START
from .scoring import CAT_ALIVE, CAT_CRITICAL, CAT_FOCUS, CAT_QUALIFY, SUPPORT_OK


def agent_history(enriched: pd.DataFrame, as_of: pd.Timestamp) -> pd.DataFrame:
    """Won/(Won+Lost) por vendedor na janela limpa até as_of, com n. Contexto, não fator."""
    c = enriched[enriched["deal_stage"].isin(("Won", "Lost")) & (enriched["close_date"] <= as_of) & (enriched["engage_date"] >= WINDOW_START)]
    g = c.assign(won=c["deal_stage"].eq("Won")).groupby("sales_agent")["won"].agg(hist_n="size", hist_win_rate="mean")
    return g


def agent_table(scored: pd.DataFrame, enriched: pd.DataFrame, as_of: pd.Timestamp) -> pd.DataFrame:
    teams = enriched[["sales_agent", "manager", "regional_office"]].drop_duplicates("sales_agent").set_index("sales_agent")
    g = scored.groupby("sales_agent").agg(
        abertos=("opportunity_id", "size"),
        acionaveis=("support", lambda s: int((s == SUPPORT_OK).sum())),
        focar=("category", lambda s: int((s == CAT_FOCUS).sum())),
        duas_semanas=("category", lambda s: int((s == CAT_CRITICAL).sum())),
        confirmar_vivo=("category", lambda s: int((s == CAT_ALIVE).sum())),
        qualificar=("category", lambda s: int((s == CAT_QUALIFY).sum())),
        sem_conta_pct=("needs_account", "mean"),
        valor_lista=("list_value", "sum"),
        valor_esperado=("expected_value", "sum"),
    )
    g = g.join(teams, how="left").join(agent_history(enriched, as_of), how="left")
    g["sem_conta_pct"] = (100 * g["sem_conta_pct"]).round(0)
    g["hist_win_rate"] = (100 * g["hist_win_rate"]).round(0)
    p75 = g["abertos"].quantile(0.75)
    g["sobrecarga"] = g["abertos"] > p75
    g["fora_do_padrao_pct"] = (100 * g["confirmar_vivo"] / g["abertos"]).round(0)
    return g.sort_values("valor_esperado", ascending=False)


def team_table(agents: pd.DataFrame) -> pd.DataFrame:
    cols = {"abertos": "sum", "acionaveis": "sum", "focar": "sum", "confirmar_vivo": "sum", "valor_lista": "sum", "valor_esperado": "sum", "sem_conta_pct": "mean"}
    t = agents.groupby(["regional_office", "manager"]).agg(cols)
    t["sem_conta_pct"] = t["sem_conta_pct"].round(0)
    return t.sort_values("valor_esperado", ascending=False)


def manager_must_acts(agents: pd.DataFrame, scored: pd.DataFrame, max_items: int = 5) -> list[dict]:
    """O que o gerente faz na segunda: sobrecarga, pipeline fora do padrão, cadastro."""
    acts: list[dict] = []
    over = agents[agents["sobrecarga"]].sort_values("abertos", ascending=False)
    for agent, r in over.head(2).iterrows():
        acts.append({"tipo": "Redistribuir ou proteger agenda", "quem": agent,
                     "porque": f"{int(r['abertos'])} deals abertos, acima do P75 do time; no histórico, vendedores com mais deals abertos convertem menos (ρ=−0,45).",
                     "acao": f"Revisar com {agent} os {int(r['confirmar_vivo'])} deals fora do padrão histórico antes de aceitar novos."})
    stale = agents.sort_values("fora_do_padrao_pct", ascending=False)
    for agent, r in stale.head(2).iterrows():
        if r["confirmar_vivo"] >= 10:
            acts.append({"tipo": "Limpar pipeline", "quem": agent,
                         "porque": f"{int(r['confirmar_vivo'])} de {int(r['abertos'])} deals ({int(r['fora_do_padrao_pct'])}%) estão além de 138 dias; nenhum deal na história fechou depois disso.",
                         "acao": "Pedir confirmação cliente a cliente nesta semana e encerrar como Lost o que não responder."})
    low_fill = agents.sort_values("sem_conta_pct", ascending=False)
    for agent, r in low_fill.head(1).iterrows():
        acts.append({"tipo": "Cadastro de conta", "quem": agent,
                     "porque": f"{int(r['sem_conta_pct'])}% dos deals abertos sem conta; nos dados, nenhum deal fechou sem conta.",
                     "acao": "Cadastrar a conta dos deals acionáveis antes do próximo Comitê de Receita."})
    return acts[:max_items]


def revops_findings(scored: pd.DataFrame, agents: pd.DataFrame) -> dict:
    total_list = float(scored["list_value"].sum())
    beyond = scored[scored["category"] == CAT_ALIVE]
    ok = scored[scored["support"] == SUPPORT_OK]
    return {
        "deals_abertos": int(len(scored)),
        "valor_lista_total": total_list,
        "deals_alem_138": int(len(beyond)),
        "valor_alem_138": float(beyond["list_value"].sum()),
        "pct_valor_alem_138": round(100 * float(beyond["list_value"].sum()) / total_list, 1) if total_list else None,
        "deals_acionaveis": int(len(ok)),
        "valor_esperado_acionavel": float(ok["expected_value"].sum()),
        "valor_lista_acionavel": float(ok["list_value"].sum()),
        "deals_sem_conta": int(scored["needs_account"].sum()),
        "pct_sem_conta": round(100 * float(scored["needs_account"].mean()), 1),
        "prospecting": int((scored["category"] == CAT_QUALIFY).sum()),
        "vendedores_sobrecarga": int(agents["sobrecarga"].sum()),
        "vendedores_sem_historico": int(agents["hist_n"].isna().sum()),
    }
