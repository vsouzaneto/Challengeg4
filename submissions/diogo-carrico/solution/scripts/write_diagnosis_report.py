"""Write docs/diagnostico.md (pt-BR) from outputs/diagnosis/diagnosis.json and outputs/audit/audit_d1.json.

Every number comes from the JSON; none is typed by hand.
Run from the solution folder:  uv run python scripts/write_diagnosis_report.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from support_triage.fmt import brl, d, n, pct, pp, pv, seg
from support_triage.paths import OUTPUTS_DIR, SOLUTION_DIR

REPORT = SOLUTION_DIR.parent / "docs" / "diagnostico.md"

CUT_PT = {
    "channel": "Canal",
    "priority": "Prioridade",
    "type": "Tipo",
    "subject": "Assunto",
    "product": "Produto",
    "channel_x_priority": "Canal × prioridade",
    "channel_x_type": "Canal × tipo",
    "priority_x_type": "Prioridade × tipo",
    "channel_x_priority_x_type": "Canal × prioridade × tipo",
}
METRIC_PT = {
    "unresolved": "Tickets sem solução (Open ou Pending), todos os tickets",
    "never_answered": "Tickets nunca respondidos (Open), todos os tickets",
    "csat": "Nota média de satisfação (1 a 5), tickets fechados",
    "resolution_hours_as_recorded": "Horas entre primeira resposta e resolução, como registradas, tickets fechados",
}
METRIC_SHORT = {
    "unresolved": "tickets sem solução",
    "never_answered": "tickets nunca respondidos",
    "csat": "nota de satisfação",
    "resolution_hours_as_recorded": "horas até a resolução",
}
VAR_PT = {
    "Ticket Channel": "Canal",
    "Ticket Priority": "Prioridade",
    "Ticket Type": "Tipo",
    "Ticket Subject": "Assunto",
    "Product Purchased": "Produto",
    "Customer Gender": "Gênero",
    "Customer Age": "Idade",
    "resolution_hours_as_recorded": "Horas até a resolução (como registradas)",
}
ASSUMPTION_PT = {
    "tickets_per_month": "Tickets por mês",
    "auto_route_share": "Parcela roteada automaticamente",
    "triage_minutes": "Minutos de triagem manual por ticket",
    "misroute_rate": "Parcela roteada errado pela IA",
    "rework_minutes": "Minutos de retrabalho por erro",
    "hourly_cost_brl": "Custo por hora de um agente",
}


def effect(metric: str, x: float) -> str:
    if metric in ("unresolved", "never_answered"):
        return pp(x)
    if metric == "csat":
        return ("+" if x >= 0 else "−") + d(abs(x), 2) + " ponto"
    return ("+" if x >= 0 else "−") + d(abs(x), 1) + " h"


def magnitude(metric: str, x: float) -> str:
    return effect(metric, x).lstrip("+−")


def value(metric: str, x: float) -> str:
    if metric in ("unresolved", "never_answered"):
        return pct(x)
    if metric == "csat":
        return d(x, 2)
    return d(x, 2) + " h"


def assumption_value(key: str, x: float) -> str:
    if key in ("auto_route_share", "misroute_rate"):
        return pct(x, 0)
    if key == "hourly_cost_brl":
        return brl(x)
    return n(x)


def bottleneck_table(metric: str, tests: dict) -> str:
    rows = [
        "| Corte | Segmentos (mediana de tickets) | Segmento mais distante da média | Diferença | Limite do acaso (95%) | p da família | Menor efeito detectável |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for cut, t in tests.items():
        rows.append(
            f"| {CUT_PT[cut]} | {t['n_segments']} ({n(t['segment_size_median'])}) | {seg(t['largest_deviation_segment'])} "
            f"| {effect(metric, t['largest_deviation'])} | {magnitude(metric, t['null_95pct_of_largest_deviation'])} "
            f"| {d(t['familywise_p_value'], 3)} | {magnitude(metric, t['minimum_detectable_deviation'])} |"
        )
    return "\n".join(rows)


def main() -> None:
    r = json.loads(
        (OUTPUTS_DIR / "diagnosis" / "diagnosis.json").read_text(encoding="utf-8")
    )
    audit = json.loads(
        (OUTPUTS_DIR / "audit" / "audit_d1.json").read_text(encoding="utf-8")
    )
    b, c, w = r["bottlenecks"], r["csat_drivers"], r["waste"]
    summary = b["_summary"]

    metrics = [m for m in b if not m.startswith("_")]
    tests = [(m, cut, t) for m in metrics for cut, t in b[m].items()]
    nominal_m, nominal_cut, nominal = min(
        tests, key=lambda x: x[2]["familywise_p_value"]
    )
    unres = b["unresolved"]
    combo = unres["channel_x_priority_x_type"]
    channel_mde = unres["channel"]["minimum_detectable_deviation"]
    max_q = max(t["q_value_bh"] for t in c["tests"])
    m = c["model"]
    base, pess, opt = (
        w["scenarios"]["base"],
        w["scenarios"]["pessimistic"],
        w["scenarios"]["optimistic"],
    )
    driver = w["sensitivity"][0]
    inverted = audit["timestamps"]["share_resolution_before_first_response"]

    csat_rows = [
        "| Variável | Teste | p | q (BH) | Médias por grupo |",
        "| --- | --- | --- | --- | --- |",
    ]
    for t in c["tests"]:
        means = (
            f"{d(t['mean_range'][0], 2)} a {d(t['mean_range'][1], 2)}"
            if t["test"] == "kruskal"
            else f"ρ = {d(t['statistic'], 3)}"
        )
        test_name = "Kruskal-Wallis" if t["test"] == "kruskal" else "Spearman"
        csat_rows.append(
            f"| {VAR_PT[t['variable']]} | {test_name} | {d(t['p_value'], 2)} | {d(t['q_value_bh'], 2)} | {means} |"
        )

    assumption_rows = [
        "| Premissa | Baixo | Base | Alto | Fonte |",
        "| --- | --- | --- | --- | --- |",
    ]
    for key, a in w["assumptions"].items():
        assumption_rows.append(
            f"| {ASSUMPTION_PT[key]} ({a['unit']}) | {assumption_value(key, a['low'])} | {assumption_value(key, a['base'])} "
            f"| {assumption_value(key, a['high'])} | {a['source']} |"
        )

    scenario_rows = [
        "| Cenário | Horas por mês | R$ por mês | Pessoas em tempo integral |",
        "| --- | --- | --- | --- |",
    ]
    for name, label in (
        ("pessimistic", "Pessimista"),
        ("base", "Base"),
        ("optimistic", "Otimista"),
    ):
        s = w["scenarios"][name]
        scenario_rows.append(
            f"| {label} | {n(s['hours_per_month'])} | {brl(s['brl_per_month'])} | {d(s['fte_at_160_hours'], 2)} |"
        )

    sens_rows = [
        "| Premissa | R$/mês no valor baixo | R$/mês no valor alto | Variação |",
        "| --- | --- | --- | --- |",
    ]
    for s in w["sensitivity"]:
        sens_rows.append(
            f"| {ASSUMPTION_PT[s['assumption']]} | {brl(s['brl_at_low'])} | {brl(s['brl_at_high'])} | {brl(s['swing_brl'])} |"
        )

    md = f"""# Diagnóstico operacional

> Gerado por `solution/scripts/write_diagnosis_report.py` a partir de `solution/outputs/diagnosis/diagnosis.json`.
> Não editar à mão: rode `uv run python scripts/run_diagnosis.py` e depois este script.

Nesta base não há gargalo nem fator de satisfação detectável, e o desperdício não pode ser medido. A estimativa paramétrica dá {n(base["hours_per_month"])} horas de triagem recuperáveis por mês ({brl(base["brl_per_month"])}) no cenário base. O maior desperdício de uma operação real, transferências e espera, não está registrado nos dados.

## As três perguntas do Diretor

**1. Onde o fluxo trava?** Em nenhum ponto detectável. Foram {summary["n_tests"]} testes: {len(metrics)} indicadores em {len(b["unresolved"])} cortes. Só um se destacou dentro do próprio corte: {seg(nominal["largest_deviation_segment"])}, em “{CUT_PT[nominal_cut].lower()}”, com {effect(nominal_m, nominal["largest_deviation"])} de {METRIC_SHORT[nominal_m]} (p {pv(nominal["familywise_p_value"])}). Corrigido para os {summary["n_tests"]} testes, o p vira {d(summary["smallest_p_after_bonferroni_across_tests"], 2)}: é o que se espera do acaso quando se testa tanto. A “pior combinação” de canal, prioridade e tipo ({seg(combo["largest_deviation_segment"])}, {effect("unresolved", combo["largest_deviation"])} de tickets sem solução) fica dentro do que o sorteio produz ({magnitude("unresolved", combo["null_95pct_of_largest_deviation"])} em 95% dos sorteios). Os testes teriam detectado um canal com {magnitude("unresolved", channel_mde)} a mais de tickets sem solução.

**2. O que impacta a satisfação?** Nada que se possa medir aqui. Nenhuma das {len(c["tests"])} variáveis se associa à nota (o maior q é {d(max_q, 2)}). Um modelo com todas as variáveis erra mais do que chutar a média ({d(m["mae_model"], 2)} contra {d(m["mae_predicting_the_average"], 2)} pontos de erro médio). Uma diferença de {d(c["minimum_detectable_difference_between_two_channels"], 2)} ponto entre dois canais teria sido detectada.

**3. Quanto estamos desperdiçando?** A base não permite medir: não há data de abertura, e em {pct(inverted)} dos tickets fechados a resolução vem antes da primeira resposta. A estimativa paramétrica do tempo de triagem que a IA pode recuperar vai de {n(pess["hours_per_month"])} a {n(opt["hours_per_month"])} horas por mês ({brl(pess["brl_per_month"])} a {brl(opt["brl_per_month"])}), com {n(base["hours_per_month"])} horas ({brl(base["brl_per_month"])}, {d(base["fte_at_160_hours"], 2)} pessoa em tempo integral) no cenário base. A premissa que mais pesa é “{ASSUMPTION_PT[driver["assumption"]].lower()}”, que nunca foi medida. Triagem é uma parte pequena do problema: na experiência do Diogo (hipótese 0.2), o tempo some em transferências, falta de contexto e espera por autorização.

## Como ler os testes

Para cada corte, o teste embaralha os rótulos dos segmentos 5.000 vezes e registra a maior diferença em relação à média que o sorteio produz. Se o segmento mais distante dos dados reais não passa desse limite, a diferença é compatível com o acaso. O “p da família” já considera todos os segmentos do corte. O “menor efeito detectável” é a diferença que o teste encontraria com 80% de chance, corrigida para o número de segmentos.

## Gargalos

### {METRIC_PT["unresolved"]}

Média geral: {pct(unres["channel"]["overall"])}.

{bottleneck_table("unresolved", b["unresolved"])}

### {METRIC_PT["never_answered"]}

Média geral: {pct(b["never_answered"]["channel"]["overall"])}.

{bottleneck_table("never_answered", b["never_answered"])}

### {METRIC_PT["csat"]}

Média geral: {d(b["csat"]["channel"]["overall"], 2)}.

{bottleneck_table("csat", b["csat"])}

### {METRIC_PT["resolution_hours_as_recorded"]}

Medida inválida (resolução antes da primeira resposta em {pct(inverted)} dos casos), mostrada só para registrar que nem tomada ao pé da letra ela revela um padrão. Média geral: {value("resolution_hours_as_recorded", b["resolution_hours_as_recorded"]["channel"]["overall"])}.

{bottleneck_table("resolution_hours_as_recorded", b["resolution_hours_as_recorded"])}

## Satisfação

{n(c["n_closed"])} tickets fechados, nota média {d(c["csat_mean"], 2)} (desvio padrão {d(c["csat_sd"], 2)}). q (BH) é o p corrigido para os {len(c["tests"])} testes pelo método de Benjamini-Hochberg.

{chr(10).join(csat_rows)}

Modelo: floresta aleatória com todas as variáveis, validação cruzada em 5 partes. Erro médio de {d(m["mae_model"], 3)} ponto, contra {d(m["mae_predicting_the_average"], 3)} chutando sempre a média.

## Desperdício: estimativa paramétrica

Horas recuperadas por mês = tickets × parcela roteada pela IA × minutos de triagem ÷ 60 − tickets roteados × parcela roteada errado × minutos de retrabalho ÷ 60. O custo multiplica as horas pelo custo por hora. O cenário pessimista combina todos os valores que reduzem a economia; o otimista, todos os que a aumentam.

{chr(10).join(assumption_rows)}

{chr(10).join(scenario_rows)}

Sensibilidade: cada premissa variada sozinha, com as outras no valor base ({brl(w["base_brl_per_month"])} por mês).

{chr(10).join(sens_rows)}

Fora da conta, por falta de dados: redução de transferências quando o primeiro roteamento acerta, tempo de espera e retrabalho por falta de contexto. Na hipótese 0.2 do Diogo, é aí que está o maior desperdício.

## O que medir numa operação real

Lista da hipótese 1.3 do Diogo, comparada com o que o Dataset 1 traz.

| O que medir | No Dataset 1 | Por quê |
| --- | --- | --- |
| Abertura do ticket (data e hora) | Não existe | Sem ela não há tempo de primeira resposta nem de resolução |
| Primeira resposta | Só um carimbo, sem abertura para comparar | Mede quanto o cliente espera pelo primeiro contato |
| Transferências: quantas e por quê | Não existe | É onde o tempo some, segundo a experiência do Diogo |
| Tempo parado esperando o cliente ou outra equipe | Não existe | Separa espera de esforço |
| Tempo de trabalho do agente | Não existe | Base do custo real por ticket |
| Resolução e reabertura | Resolução contraditória em {pct(inverted)} dos fechados; reabertura não existe | Mostra se o problema foi resolvido de fato |
| Motivo do contato | Tipo e assunto existem, mas não têm relação com o texto | Base para classificar e rotear |
| Taxa de resposta à pesquisa de satisfação | Não existe; só há a nota dos fechados | Sem ela não se sabe quem a nota representa |
"""
    REPORT.write_text(md, encoding="utf-8")
    print(f"wrote {REPORT}")


if __name__ == "__main__":
    main()
