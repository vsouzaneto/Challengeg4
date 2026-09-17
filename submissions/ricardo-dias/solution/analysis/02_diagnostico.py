"""Etapa 2 — Diagnóstico operacional (Dataset 1) com a força de conclusão que os dados permitem.

A auditoria (01) mostrou que tempos e CSAT do Dataset 1 não carregam sinal detectável. A saída separa:
  observations  contagens descritivas do arquivo (não são, por si, evidência de gargalo)
  tests         testes de associação, com incerteza e tamanho de diferença detectável
  limitations   o que estes dados não permitem afirmar
  scenario      estimativa de desperdício: premissas explícitas + cobertura MEDIDA do roteamento real (routing_eval.json)

A fórmula do cenário é espelhada em app/lib/waste.ts (calculadora da UI); tests/waste.test.ts garante igualdade.
Saída: app/data/diagnostico.json
"""

from __future__ import annotations

import json
import math

import numpy as np
import pandas as pd
from scipy import stats

from common import APP_DATA, load_d1, r, write_json

ANNUAL_VOLUME = 30_000
ALPHA = 0.05
Z = 1.96
FTE_HOURS_PER_YEAR = 1_760


def br_int(x: float) -> str:
    return f"{x:,.0f}".replace(",", ".")


def br_dec(x: float, digits: int = 1) -> str:
    return f"{x:.{digits}f}".replace(".", ",")


def br_pct(x: float, digits: int = 1) -> str:
    return f"{br_dec(x * 100, digits)}%"


def br_p(p: float) -> str:
    return "p < 0,001" if p < 0.001 else f"p = {br_dec(p, 2)}"


def wilson(k: int, n: int) -> dict:
    if n == 0:
        return {"low": 0.0, "high": 0.0}
    phat = k / n
    denom = 1 + Z**2 / n
    center = (phat + Z**2 / (2 * n)) / denom
    half = Z * math.sqrt(phat * (1 - phat) / n + Z**2 / (4 * n**2)) / denom
    return {"low": r(center - half), "high": r(center + half)}


def segment_test(d1: pd.DataFrame, col: str, label: str) -> dict:
    p = stats.chi2_contingency(pd.crosstab(d1[col], d1["Ticket Status"])).pvalue
    significant = bool(p < ALPHA)
    conclusion = (f"Status varia por {label} ({br_p(p)})." if significant else
                  f"Não detectamos associação entre status e {label} ({br_p(p)}).")
    return {"variable": label, "test": "qui-quadrado de independência", "pValue": r(p),
            "significant": significant, "conclusion": conclusion}


def csat_driver(closed: pd.DataFrame, col: str, label: str) -> dict:
    groups = {k: g["Customer Satisfaction Rating"].to_numpy(dtype=float) for k, g in closed.groupby(col)}
    h, p = stats.kruskal(*groups.values())
    eps2 = h / (len(closed) - 1)  # ε² de Kruskal-Wallis
    pooled_sd = math.sqrt(np.mean([v.var(ddof=1) for v in groups.values()]))
    n_typical = np.mean([len(v) for v in groups.values()])
    detectable = Z * pooled_sd * math.sqrt(2 / n_typical)  # meia-largura do IC da diferença entre dois grupos típicos
    out_groups = []
    for k, v in groups.items():
        half = Z * v.std(ddof=1) / math.sqrt(len(v))
        out_groups.append({"label": k, "mean": r(v.mean(), 2), "n": int(len(v)),
                           "ci": {"low": r(v.mean() - half, 2), "high": r(v.mean() + half, 2)}})
    conclusion = (
        f"Associação detectada ({br_p(p)}, ε² = {br_dec(eps2, 4)})." if p < ALPHA else
        f"Não detectamos associação nos testes realizados ({br_p(p)}, ε² = {br_dec(eps2, 4)}). Diferenças de até "
        f"±{br_dec(detectable, 2)} ponto entre dois grupos não seriam distinguíveis do acaso com este volume."
    )
    return {"variable": label, "test": "Kruskal-Wallis", "pValue": r(p), "effectSize": r(eps2),
            "detectableDiff": r(detectable, 3), "conclusion": conclusion,
            "groups": sorted(out_groups, key=lambda g: g["mean"])}


def compute_waste(a: dict[str, float]) -> list[dict]:
    """Espelho exato de app/lib/waste.ts. Horas por ano, já descontado o trabalho residual."""
    v, auto = a["annual_volume"], a["auto_share"]

    triage = v * a["triage_minutes"] / 60
    triage_rec = v * auto * (a["triage_minutes"] - a["auto_check_minutes"]) / 60

    rework = v * a["misroute_rate"] * a["rework_minutes"] / 60
    rework_after = v * ((1 - auto) * a["misroute_rate"] + auto * (1 - a["auto_accuracy"])) * a["rework_minutes"] / 60

    followup = v * a["pending_share"] * a["followups_per_pending"] * a["followup_minutes"] / 60
    followup_rec = followup * a["followup_automation"]

    drafting = v * a["draft_minutes"] / 60
    eligible = max(0.0, 1 - a["human_only_share"] - a["escalation_share"])
    drafting_rec = v * eligible * a["draft_minutes"] * a["draft_net_saving"] / 60

    lines = [
        ("triage", "Triagem manual (ler, classificar, rotear)", triage, triage_rec,
         "Só nos tickets roteados automaticamente, descontando a conferência rápida que continua existindo."),
        ("rework", "Retrabalho por roteamento errado", rework, rework - rework_after,
         "Nos automáticos, a taxa de erro manual é trocada pelo erro medido do roteamento; o restante continua manual. "
         "Fica negativo se o erro automático superar o manual."),
        ("followup", "Follow-up de tickets aguardando o cliente", followup, followup_rec,
         "Lembretes e fechamento por inatividade. Cenário sem evidência nos dados: validar em piloto."),
        ("drafting", "Redação de respostas", drafting, drafting_rec,
         "Economia líquida (já descontada a revisão) apenas nos tickets elegíveis a rascunho: exclui casos só-humanos e escalações."),
    ]
    return [{"id": i, "step": s, "hoursPerYear": r(h, 1), "recoverableHoursPerYear": r(rec, 1), "rationale": why}
            for i, s, h, rec, why in lines]


def totals(waste: list[dict], a: dict[str, float]) -> dict:
    hours = sum(w["hoursPerYear"] for w in waste)
    rec = sum(w["recoverableHoursPerYear"] for w in waste)
    return {"hoursPerYear": r(hours, 1), "recoverableHoursPerYear": r(rec, 1),
            "recoverableCost": r(rec * a["hourly_cost"], 0), "fte": r(rec / FTE_HOURS_PER_YEAR, 2)}


def main() -> None:
    d1 = load_d1()
    n = len(d1)
    routing = json.loads((APP_DATA / "routing_eval.json").read_text(encoding="utf-8"))["test"]
    closed = d1[d1["Ticket Status"] == "Closed"]
    status = d1["Ticket Status"].value_counts()
    d1["canal × prioridade"] = d1["Ticket Channel"] + " × " + d1["Ticket Priority"]

    observations = [
        {"id": "volume", "label": "Tickets no arquivo", "value": br_int(n),
         "detail": f"O enunciado fala em ~{br_int(ANNUAL_VOLUME)}/ano; valores anuais abaixo são projeção para esse volume."},
        {"id": "not_closed", "label": "Registros não fechados", "value": br_pct(1 - status["Closed"] / n),
         "detail": f"{br_pct(status['Open'] / n)} abertos e {br_pct(status['Pending Customer Response'] / n)} aguardando o cliente. "
                   "Contagem descritiva: sem datas de abertura não dá para medir envelhecimento da fila."},
        {"id": "open_no_frt", "label": "Abertos sem registro de 1ª resposta",
         "value": br_pct(d1.loc[d1["Ticket Status"] == "Open", "First Response Time"].isna().mean(), 0),
         "detail": "Pode ser só a definição de 'Open' no gerador do dataset. Primeira métrica a medir com dados reais."},
        {"id": "pending", "label": "Aguardando resposta do cliente", "value": br_pct(status["Pending Customer Response"] / n),
         "detail": "Fatia que depende do cliente, não do time. Base do cenário de follow-up automático."},
    ]

    segments = []
    for (ch, pr), g in d1.groupby(["Ticket Channel", "Ticket Priority"]):
        k = int((g["Ticket Status"] != "Closed").sum())
        cs = g.loc[g["Ticket Status"] == "Closed", "Customer Satisfaction Rating"]
        segments.append({"channel": ch, "priority": pr, "n": int(len(g)), "backlogShare": r(k / len(g)),
                         "backlogCI": wilson(k, len(g)),
                         "pendingCustomerShare": r((g["Ticket Status"] == "Pending Customer Response").mean()),
                         "csatMean": r(cs.mean(), 2) if len(cs) else None})

    segment_tests = [segment_test(d1, c, lbl) for c, lbl in [("Ticket Channel", "canal"), ("Ticket Priority", "prioridade"),
                                                             ("Ticket Type", "tipo"), ("canal × prioridade", "canal × prioridade")]]
    csat = [csat_driver(closed, c, lbl) for c, lbl in [("Ticket Channel", "canal"), ("Ticket Priority", "prioridade"),
                                                       ("Ticket Type", "tipo"), ("Customer Gender", "gênero")]]
    for t in segment_tests + csat:
        print("-", t["conclusion"])

    limitations = [
        {"id": "synthetic", "text": "O Dataset 1 tem padrão de dado sintético (distribuições uniformes, placeholders no texto, resoluções aleatórias)."},
        {"id": "times", "text": "Tempos de resposta/resolução não são utilizáveis (49% das resoluções antes da 1ª resposta; sem data de abertura). "
                                "Não medimos gargalo de tempo por canal ou prioridade."},
        {"id": "no_association", "text": "Não detectar associação não prova ausência de efeito: diferenças pequenas podem não ser detectáveis com este volume."},
        {"id": "domain", "text": "O roteamento foi medido em tickets de TI interna (Dataset 2). Aplicado aos tickets do Dataset 1 ele quase não roteia "
                                 "automaticamente (o guarda de domínio barra o texto). Em produção, re-treinar com o histórico da operação."},
        {"id": "assumptions", "text": "Minutos por tarefa, taxa de roteamento errado, custo/hora e automação de follow-up são premissas a validar, não medições."},
    ]

    auto = routing["auto"]
    escal = next(x["share"] for x in routing["routes"] if x["route"] == "escalar")
    assumptions = [
        {"id": "annual_volume", "label": "Volume anual de tickets", "value": ANNUAL_VOLUME, "unit": "tickets/ano", "kind": "premissa",
         "source": "Enunciado do desafio (o arquivo tem 8.469 tickets).", "editable": True},
        {"id": "hourly_cost", "label": "Custo carregado por hora de agente", "value": 45, "unit": "R$/h", "kind": "premissa",
         "source": "Validar com RH/financeiro.", "editable": True},
        {"id": "triage_minutes", "label": "Triagem manual por ticket", "value": 3, "unit": "min", "kind": "premissa",
         "source": "Validar cronometrando ~50 triagens.", "editable": True},
        {"id": "auto_check_minutes", "label": "Conferência residual por ticket roteado automaticamente", "value": 0.5, "unit": "min",
         "kind": "premissa", "source": "O agente ainda bate o olho na categoria ao abrir o ticket.", "editable": True},
        {"id": "auto_share", "label": "Tickets roteados automaticamente", "value": auto["share"], "unit": "fração", "kind": "referencia",
         "source": f"Medido no teste ({routing['n']} tickets de TI interna) com a política completa da API. "
                   "Pressupõe re-treino com o histórico da operação.", "editable": True},
        {"id": "auto_accuracy", "label": "Acerto nos roteados automaticamente", "value": auto["accuracy"], "unit": "fração",
         "kind": "referencia", "source": f"Medido no teste; IC 95% {br_pct(auto['accuracyCI']['low'])}–{br_pct(auto['accuracyCI']['high'])}.",
         "editable": True},
        {"id": "misroute_rate", "label": "Roteamento errado na triagem manual", "value": 0.15, "unit": "fração", "kind": "premissa",
         "source": "Medir por reatribuições no helpdesk.", "editable": True},
        {"id": "rework_minutes", "label": "Retrabalho por ticket mal roteado", "value": 15, "unit": "min", "kind": "premissa",
         "source": "Inclui reler, reatribuir e retomar o contexto.", "editable": True},
        {"id": "pending_share", "label": "Tickets aguardando o cliente", "value": r(status["Pending Customer Response"] / n),
         "unit": "fração", "kind": "medido", "source": "Contagem do Dataset 1 (mix sintético).", "editable": True},
        {"id": "followups_per_pending", "label": "Follow-ups manuais por ticket pendente", "value": 2, "unit": "follow-ups",
         "kind": "premissa", "source": "Validar no histórico do helpdesk.", "editable": True},
        {"id": "followup_minutes", "label": "Tempo por follow-up", "value": 4, "unit": "min", "kind": "premissa",
         "source": "Validar no histórico do helpdesk.", "editable": True},
        {"id": "followup_automation", "label": "Follow-ups automatizáveis (líquido)", "value": 0.6, "unit": "fração", "kind": "premissa",
         "source": "Sem evidência nos dados; parte dos clientes exige contato humano. Validar em piloto.", "editable": True},
        {"id": "draft_minutes", "label": "Redação de uma resposta", "value": 6, "unit": "min", "kind": "premissa",
         "source": "Validar cronometrando respostas.", "editable": True},
        {"id": "draft_net_saving", "label": "Economia líquida com rascunho (já descontada a revisão)", "value": 0.25, "unit": "fração",
         "kind": "premissa", "source": "Conservadora; o agente lê, ajusta e aprova. Validar em piloto A/B.", "editable": True},
        {"id": "human_only_share", "label": "Casos só-humanos (reembolso e cancelamento)",
         "value": r(d1["Ticket Type"].isin(["Refund request", "Cancellation request"]).mean()), "unit": "fração", "kind": "medido",
         "source": "Contagem do Dataset 1 (mix sintético).", "editable": True},
        {"id": "escalation_share", "label": "Tickets escalados por sinal de risco", "value": escal, "unit": "fração", "kind": "referencia",
         "source": "Medido no teste com a política da API. Pode sobrepor-se aos casos só-humanos (desconto conservador).", "editable": True},
    ]
    a = {x["id"]: x["value"] for x in assumptions}
    waste = compute_waste(a)
    tot = totals(waste, a)
    sensitivity = [{"autoShare": s, "draftSaving": d,
                    "recoverableHoursPerYear": totals(compute_waste({**a, "auto_share": s, "draft_net_saving": d}), a)["recoverableHoursPerYear"]}
                   for s in [0.3, 0.5, a["auto_share"]] for d in [0.15, 0.25]]
    print(f"cenário: {tot}")

    write_json("diagnostico.json", {
        "nTickets": n,
        "observations": observations,
        "segments": segments,
        "tests": {"segmentTests": segment_tests, "csatDrivers": csat},
        "limitations": limitations,
        "scenario": {
            "note": (f"Estimativa para {br_int(ANNUAL_VOLUME)} tickets/ano. Combina referências medidas no teste do roteamento com "
                     "premissas a validar; não é medição da operação. Economias já descontam conferência, revisão e erros residuais."),
            "assumptions": assumptions, "waste": waste, "totals": tot, "sensitivity": sensitivity,
        },
    })


if __name__ == "__main__":
    main()
