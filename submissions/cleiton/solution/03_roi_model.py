"""Illustrative capacity scenarios; costs of deployment and supervision excluded."""
from __future__ import annotations

import json
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent / "output"
METRICS_PATH = OUT_DIR / "classifier_metrics.json"
ROI_PATH = OUT_DIR / "roi_model.json"

# Explicit, stated assumptions (industry-typical, not measured in this data —
# the operational dataset has no "time spent classifying/routing" field).
ANNUAL_TICKET_VOLUME = 30_000  # per the brief's stated operation size
MANUAL_TRIAGE_MINUTES_PER_TICKET = 3.0  # time an agent spends reading, categorizing, routing before starting real work
HOURLY_LOADED_COST_BRL = 50.0
REWORK_MINUTES_AVOIDED_PER_MISROUTE_FIXED = 8.0  # extra time a misrouted ticket costs when it bounces between queues


def main() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    coverage = metrics["coverage_at_threshold"]
    acc_covered = metrics["accuracy_when_confidence_above_threshold"]

    eligible_share = 0.70  # illustrative; must be measured after all risk rules
    auto_routed_tickets = ANNUAL_TICKET_VOLUME * coverage * eligible_share
    correctly_auto_routed = auto_routed_tickets * acc_covered
    incorrectly_auto_routed = auto_routed_tickets * (1 - acc_covered)

    # Time saved: only the correctly-routed share converts triage time into
    # pure savings. The incorrectly-routed share still needs a human to
    # notice and re-route — modelled as a rework cost, not a saving.
    hours_saved_from_correct_routing = correctly_auto_routed * MANUAL_TRIAGE_MINUTES_PER_TICKET / 60
    hours_lost_to_rework_from_wrong_routing = incorrectly_auto_routed * REWORK_MINUTES_AVOIDED_PER_MISROUTE_FIXED / 60
    net_hours_saved = hours_saved_from_correct_routing - hours_lost_to_rework_from_wrong_routing
    net_cost_brl = net_hours_saved * HOURLY_LOADED_COST_BRL

    payload = {
        "grounded_in": "Cobertura e acurácia medidas no teste de TI. Transferência para suporte comercial não validada.",
        "assumptions": {
            "eligible_share_after_risk_rules": eligible_share,
            "annual_ticket_volume": ANNUAL_TICKET_VOLUME,
            "manual_triage_minutes_per_ticket": MANUAL_TRIAGE_MINUTES_PER_TICKET,
            "hourly_loaded_cost_brl": HOURLY_LOADED_COST_BRL,
            "rework_minutes_per_misroute": REWORK_MINUTES_AVOIDED_PER_MISROUTE_FIXED,
        },
        "measured_from_classifier": {
            "coverage_at_60pct_confidence": coverage,
            "accuracy_when_covered": acc_covered,
        },
        "calculation": {
            "auto_routed_tickets_per_year": round(auto_routed_tickets),
            "correctly_auto_routed_per_year": round(correctly_auto_routed),
            "incorrectly_auto_routed_per_year": round(incorrectly_auto_routed),
            "hours_saved_from_correct_routing": round(hours_saved_from_correct_routing),
            "hours_lost_to_rework_from_wrong_routing": round(hours_lost_to_rework_from_wrong_routing),
            "potential_capacity_hours_per_year": round(net_hours_saved),
            "potential_capacity_value_brl_per_year": round(net_cost_brl),
        },
        "caveat": (
            "Economia potencial de capacidade após retrabalho estimado e antes de implantação, "
            "manutenção e supervisão. Não mede desperdício atual nem garante economia de caixa. "
            "A elegibilidade de 70% após regras de risco, 3 minutos de triagem e 8 minutos de "
            "retrabalho são hipóteses. A acurácia de TI é mantida como hipótese após os filtros "
            "e na operação comercial; essa transferência precisa ser validada. Não é piso garantido."
        ),
        "pilot": [
            "Medir tempo ativo de triagem e retrabalho por canal, prioridade e tipo.",
            "Em modo de observação, medir elegibilidade após regras de risco e acerto no público elegível.",
            "Comparar com grupo de controle: transferências, reaberturas, tempo ativo e satisfação.",
            "Descontar implantação, manutenção e supervisão; comparar outras oportunidades antes de declarar o maior desperdício recuperável."
        ],
        "scenarios": []

    }

    for name, eligible, minutes, rework in [
        ("Menor benefício", 0.5, 1, 12),
        ("Referência ilustrativa", 0.7, 3, 8),
        ("Comparação histórica: sem desconto de risco", 1.0, 3, 8),
    ]:
        routed = ANNUAL_TICKET_VOLUME * coverage * eligible
        hours = routed * (acc_covered * minutes - (1-acc_covered) * rework) / 60
        payload["scenarios"].append({
            "name": name, "eligible_share": eligible, "triage_minutes": minutes,
            "rework_minutes": rework, "capacity_hours": round(hours),
            "capacity_value_brl": round(hours * HOURLY_LOADED_COST_BRL)
        })

    ROI_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {ROI_PATH}")
    print(f"Net hours saved/year: {net_hours_saved:.0f} | Net savings: R$ {net_cost_brl:,.0f}/ano")


if __name__ == "__main__":
    main()
