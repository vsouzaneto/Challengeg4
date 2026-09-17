"""Etapa 5 — Renderiza docs/*.md a partir de docs/templates/*.md.tmpl e dos JSONs gerados.

A prosa é escrita à mão nos templates; todo número vem de um placeholder {{chave}} preenchido aqui.
Placeholder sem valor → erro (nenhum número digitado à mão nos documentos).
"""

from __future__ import annotations

import json
import re

from common import APP_DATA, HERE

DOCS = HERE.parents[1] / "docs"
TEMPLATES = DOCS / "templates"
# Cópias servidas pela UI: docs/ fica fora do Root Directory do app no deploy (pedido do Codex no HANDOFF).
PUBLIC_COPIES = {"automacao.md": APP_DATA.parent / "public" / "docs" / "automacao.md"}
PLACEHOLDER = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")

ROUTE_PT = {"auto": "Automático", "revisao_humana": "Revisão humana", "escalar": "Escalação"}
REASON_PT = {
    "auto": "Roteado automaticamente",
    "low_confidence": "Confiança abaixo do limiar",
    "out_of_domain": "Vocabulário fora do padrão (guarda de domínio)",
    "always_human": "Previsto como privilégio administrativo",
    "admin_rights_risk": "Probabilidade de privilégio acima do limiar",
    "escalation_terms": "Termo de risco/urgência",
}


def load(name: str) -> dict:
    return json.loads((APP_DATA / name).read_text(encoding="utf-8"))


def pct(x: float, digits: int = 1) -> str:
    return f"{x * 100:.{digits}f}%".replace(".", ",")


def dec(x: float, digits: int = 2) -> str:
    return f"{x:.{digits}f}".replace(".", ",")


def num(x: float) -> str:
    return f"{x:,.0f}".replace(",", ".")


def ci(interval: dict, digits: int = 1) -> str:
    return f"{pct(interval['low'], digits)}–{pct(interval['high'], digits)}"


def table(header: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join(lines)


EXAMPLE_WORDS = (10, 40)
EXAMPLE_CHARS = 170


def data_examples() -> str:
    """Tickets reais do TESTE que ilustram cada caso "não automatizar".

    Regra fixa, sem escolha manual: em cada situação, o ticket de menor id com 10–40 palavras
    (ou o de menor id, se nenhum couber na faixa). Rotas e previsões vêm de python_predictions.json,
    que concorda 100% com a política TypeScript da API.
    """
    artifacts = HERE / "artifacts"
    tickets = json.loads((artifacts / "test_split.json").read_text(encoding="utf-8"))["items"]
    preds = {p["id"]: p for p in json.loads((artifacts / "python_predictions.json").read_text(encoding="utf-8"))["test"]}
    rules = json.loads((APP_DATA.parent / "lib" / "policy-rules.json").read_text(encoding="utf-8"))
    admin = rules["adminRightsCategory"]
    situations = [
        ("Termo de risco/urgência", lambda t, p: p["reasonCode"] == "escalation_terms",
         "Escalado para atendente sênior, sem rascunho de IA."),
        ("Pedido de privilégio pego pela regra de risco", lambda t, p: p["reasonCode"] == "admin_rights_risk" and t["label"] == admin,
         "O modelo previu outra categoria, mas a probabilidade de privilégio passou do limiar: aprovação humana."),
        ("Pedido de privilégio que escapou", lambda t, p: t["label"] == admin and p["route"] == "auto",
         "Exemplo do vazamento residual: por isso conceder acesso nunca é automático, mesmo após o roteamento."),
        ("Texto fora do padrão do treino", lambda t, p: p["reasonCode"] == "out_of_domain",
         "Vocabulário pouco conhecido pelo modelo: triagem humana."),
        ("Baixa confiança", lambda t, p: p["reasonCode"] == "low_confidence",
         "O modelo não tem certeza suficiente: triagem humana confirma a categoria."),
    ]
    rows = []
    for name, match, why in situations:
        candidates = sorted((t for t in tickets if match(t, preds[t["id"]])), key=lambda t: t["id"])
        if not candidates:
            raise SystemExit(f"sem exemplo para: {name}")
        in_range = [t for t in candidates if EXAMPLE_WORDS[0] <= len(t["text"].split()) <= EXAMPLE_WORDS[1]]
        t = (in_range or candidates)[0]
        p = preds[t["id"]]
        text = t["text"] if len(t["text"]) <= EXAMPLE_CHARS else t["text"][:EXAMPLE_CHARS].rsplit(" ", 1)[0] + "…"
        if p["reasonCode"] == "escalation_terms":
            tokens = set(re.findall(r"\b[a-z]{2,}\b", re.sub(r"[^a-z]+", " ", t["text"].lower())))
            hits = [w for w in rules["escalationTerms"] if w in tokens]
            why = f"Termo(s) detectado(s): {', '.join(hits)}. " + why
        rows.append([f"**{name}**", f"#{t['id']}: _{text}_", f"{t['label']} → {p['label']}",
                     pct(p["confidence"]), why])
    return table(["Situação", "Ticket real (teste, texto já pré-processado)", "Real → previsto", "Confiança", "Tratamento"], rows)


def build_context() -> dict[str, str]:
    audit, metrics, routing, diag = load("audit.json"), load("model_metrics.json"), load("routing_eval.json"), load("diagnostico.json")
    t, sel, rt, rv = metrics["test"], metrics["selection"], routing["test"], routing["validation"]
    sc, a = diag["scenario"], {x["id"]: x for x in diag["scenario"]["assumptions"]}
    routes = {x["route"]: x for x in rt["routes"]}
    reasons = {x["reasonCode"]: x for x in rt["reasons"]}
    waste = {w["id"]: w for w in sc["waste"]}
    obs = {o["id"]: o for o in diag["observations"]}
    splits = {s["name"]: s for s in metrics["splits"]}
    findings = {f["id"]: f for f in audit["findings"]}
    exp = metrics["exploratory"]
    cd = metrics["crossDomain"]
    d1_routes = {x["route"]: x["share"] for x in cd["routes"]}
    csat = {c["variable"]: c for c in diag["tests"]["csatDrivers"]}
    seg = {s["variable"]: s for s in diag["tests"]["segmentTests"]}

    ctx: dict[str, str] = {
        # auditoria
        "d1_rows": num(audit["d1"]["rows"]),
        "d2_rows": num(audit["d2"]["rows"]),
        "audit_times": findings["d1-times"]["evidence"],
        "audit_uniform": findings["d1-uniform"]["evidence"],
        "audit_csat": findings["d1-csat"]["evidence"],
        "audit_text": findings["d1-text"]["evidence"],
        # partições e seleção
        "n_train": num(splits["treino"]["n"]), "n_val": num(splits["validacao"]["n"]), "n_test": num(splits["teste"]["n"]),
        "sel_C": str(sel["C"]), "sel_eps": dec(sel["coefEps"], 2),
        "sel_conf": pct(sel["confidenceThreshold"], 0), "sel_ood": pct(sel["oodThreshold"], 0),
        "sel_admin": pct(sel["adminRightsThreshold"], 0) if sel["adminRightsThreshold"] is not None else "não usada",
        "sel_criteria": "\n".join(f"- {c}" for c in sel["criteria"]),
        "table_candidates": table(["Modelo (validação)", "Acurácia", "F1 macro"],
                                  [[c["name"], pct(c["accuracy"]), dec(c["macroF1"], 3)] for c in sel["candidates"]]),
        # teste do modelo
        "test_acc": pct(t["accuracy"]), "test_acc_ci": ci(t["accuracyCI"]),
        "test_f1": dec(t["macroF1"], 3), "test_f1_ci": f"{dec(t['macroF1CI']['low'], 3)}–{dec(t['macroF1CI']['high'], 3)}",
        "test_baseline": pct(t["baselineAccuracy"]),
        "table_per_class": table(["Categoria", "Precisão", "Recall", "F1", "Tickets no teste"],
                                 [[c["label"], pct(c["precision"]), pct(c["recall"]), dec(c["f1"], 3), num(c["support"])] for c in t["perClass"]]),
        "ar_recall": pct(next(c["recall"] for c in t["perClass"] if c["label"] == "Administrative rights")),
        # histórico exploratório
        "exp_acc": pct(exp["accuracy"]), "exp_f1": dec(exp["macroF1"], 3),
        "exp_auto": pct(exp["autoCoverage"]), "exp_auto_acc": pct(exp["autoAccuracy"]),
        # roteamento (teste, política completa)
        "rt_n": num(rt["n"]),
        "rt_auto": pct(routes["auto"]["share"]), "rt_auto_n": num(routes["auto"]["n"]), "rt_auto_ci": ci(rt["auto"]["shareCI"]),
        "rt_auto_acc": pct(rt["auto"]["accuracy"]), "rt_auto_acc_ci": ci(rt["auto"]["accuracyCI"]), "rt_auto_errors": num(rt["auto"]["errors"]),
        "rt_human": pct(routes["revisao_humana"]["share"]), "rt_human_n": num(routes["revisao_humana"]["n"]),
        "rt_escal": pct(routes["escalar"]["share"]), "rt_escal_n": num(routes["escalar"]["n"]),
        "rv_auto": pct(rv["auto"]["share"]), "rv_auto_acc": pct(rv["auto"]["accuracy"]),
        "table_routes": table(["Destino", "Tickets", "Proporção"],
                              [[ROUTE_PT[x["route"]], num(x["n"]), pct(x["share"])] for x in rt["routes"]]),
        "table_reasons": table(["Motivo", "Tickets", "Proporção"],
                               [[REASON_PT[x["reasonCode"]], num(x["n"]), pct(x["share"])] for x in rt["reasons"]]),
        "table_by_category": table(
            ["Categoria real", "Tickets", "Automático", "Revisão humana", "Escalação", "Acerto nos automáticos"],
            [[c["label"], num(c["n"]), num(c["auto"]), num(c["revisao_humana"]), num(c["escalar"]),
              pct(c["autoAccuracy"]) if c["autoAccuracy"] is not None else "—"] for c in rt["byTrueCategory"]]),
        "ar_total": num(rt["adminRightsLeak"]["trueAdminRights"]), "ar_leak_n": num(rt["adminRightsLeak"]["autoRoutedElsewhere"]),
        "ar_leak": pct(rt["adminRightsLeak"]["share"]),
        "ar_leak_queues": ", ".join(f"{q['label']} ({q['n']})" for q in rt["adminRightsLeak"]["toQueues"]) or "nenhuma",
        "ar_leak_val": pct(rv["adminRightsLeak"]["share"]),
        "reason_admin_n": num(reasons["admin_rights_risk"]["n"]), "reason_always_n": num(reasons["always_human"]["n"]),
        "reason_ood": pct(reasons["out_of_domain"]["share"]), "reason_lowconf": pct(reasons["low_confidence"]["share"]),
        "py_agreement": pct(rt["pythonAgreement"]["route"], 0),
        # cruzamento com D1
        "cd_confident": pct(cd["confidentShare"]), "cd_hw": pct(cd["confidentPredictedHardware"], 0),
        "cd_ood": pct(cd["oodFlagged"]), "cd_ood_in": pct(cd["inDomainOodFlagged"]),
        "cd_auto": pct(d1_routes["auto"]), "cd_human": pct(d1_routes["revisao_humana"]), "cd_escal": pct(d1_routes["escalar"]),
        # diagnóstico
        "obs_not_closed": obs["not_closed"]["value"], "obs_not_closed_detail": obs["not_closed"]["detail"],
        "obs_open_no_frt": obs["open_no_frt"]["value"], "obs_pending": obs["pending"]["value"],
        "seg_channel": seg["canal"]["conclusion"], "seg_priority": seg["prioridade"]["conclusion"],
        "seg_type": seg["tipo"]["conclusion"], "seg_combo": seg["canal × prioridade"]["conclusion"],
        "table_csat": table(["Variável", "Teste", "p", "ε²", "Diferença não detectável até"],
                            [[c["variable"], c["test"], dec(c["pValue"], 2), dec(c["effectSize"], 4), f"±{dec(c['detectableDiff'], 2)} ponto"]
                             for c in diag["tests"]["csatDrivers"]]),
        "csat_channel_groups": "; ".join(f"{g['label']} {dec(g['mean'])} (IC {dec(g['ci']['low'])}–{dec(g['ci']['high'])})"
                                         for g in csat["canal"]["groups"]),
        "limitations": "\n".join(f"- {x['text']}" for x in diag["limitations"]),
        # cenário
        "sc_note": sc["note"],
        "sc_total_hours": num(sc["totals"]["hoursPerYear"]), "sc_recoverable": num(sc["totals"]["recoverableHoursPerYear"]),
        "sc_fte": dec(sc["totals"]["fte"], 1), "sc_cost": num(sc["totals"]["recoverableCost"]),
        "table_waste": table(["Etapa", "Horas/ano (hoje)", "Recuperável/ano", "Como foi calculado"],
                             [[w["step"], num(w["hoursPerYear"]), num(w["recoverableHoursPerYear"]), w["rationale"]] for w in sc["waste"]]),
        "table_assumptions": table(["Premissa", "Valor", "Tipo", "Fonte / como validar"],
                                   [[x["label"], f"{dec(x['value'], 4).rstrip('0').rstrip(',')} {x['unit']}", x["kind"], x["source"]]
                                    for x in sc["assumptions"]]),
        "table_sensitivity": table(["Roteamento automático", "Economia líquida com rascunho", "Horas recuperáveis/ano"],
                                   [[pct(s["autoShare"]), pct(s["draftSaving"], 0), num(s["recoverableHoursPerYear"])] for s in sc["sensitivity"]]),
        "w_triage": num(waste["triage"]["recoverableHoursPerYear"]), "w_rework": num(waste["rework"]["recoverableHoursPerYear"]),
        "w_followup": num(waste["followup"]["recoverableHoursPerYear"]), "w_drafting": num(waste["drafting"]["recoverableHoursPerYear"]),
        "sens_low": num(min(s["recoverableHoursPerYear"] for s in sc["sensitivity"])),
        "hourly_cost": num(a["hourly_cost"]["value"]), "annual_volume": num(a["annual_volume"]["value"]),
        "table_examples": data_examples(),
    }
    return ctx


def render(template: str, ctx: dict[str, str], name: str) -> str:
    missing = sorted({m for m in PLACEHOLDER.findall(template) if m not in ctx})
    if missing:
        raise SystemExit(f"{name}: placeholders sem valor: {missing}")
    header = f"<!-- Gerado por solution/analysis/05_report.py a partir de docs/templates/{name}. Não edite à mão. -->\n\n"
    return header + PLACEHOLDER.sub(lambda m: ctx[m.group(1)], template)


def main() -> None:
    ctx = build_context()
    for tmpl in sorted(TEMPLATES.glob("*.md.tmpl")):
        # README.md vai para a raiz da submissão; os demais para docs/.
        out = (DOCS.parent if tmpl.name == "README.md.tmpl" else DOCS) / tmpl.name.removesuffix(".tmpl")
        rendered = render(tmpl.read_text(encoding="utf-8"), ctx, tmpl.name)
        out.write_text(rendered, encoding="utf-8")
        print(f"→ {out.relative_to(DOCS.parent)}")
        if out.name in PUBLIC_COPIES:
            copy = PUBLIC_COPIES[out.name]
            copy.parent.mkdir(parents=True, exist_ok=True)
            copy.write_text(rendered, encoding="utf-8")
            print(f"→ {copy.relative_to(HERE.parents[1])}")


if __name__ == "__main__":
    main()
