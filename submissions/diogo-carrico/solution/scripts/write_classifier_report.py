"""Write docs/classificador.md (pt-BR) from outputs/classifier/metrics.json and confusion_matrix.csv.

Every number comes from the files written by train_classifier.py; none is typed by hand.
Run from the solution folder:  uv run python scripts/write_classifier_report.py
"""

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from support_triage.fmt import d, n, pct
from support_triage.paths import OUTPUTS_DIR, SOLUTION_DIR

REPORT = SOLUTION_DIR.parent / "docs" / "classificador.md"
MODEL_PT = {
    "tfidf_logreg": "TF-IDF + regressão logística",
    "tfidf_linearsvc": "TF-IDF + SVM linear",
    "tfidf_complementnb": "TF-IDF + Naive Bayes complementar",
}


def model_name(key: str) -> str:
    base, param = key.rsplit("_", 1)
    return f"{MODEL_PT[base]} ({param.replace('a', 'alfa ').replace('C', 'C = ').replace('.', ',')})"


def ci(pair: list[float]) -> str:
    return f"{pct(pair[0])} a {pct(pair[1])}"


def main() -> None:
    r = json.loads(
        (OUTPUTS_DIR / "classifier" / "metrics.json").read_text(encoding="utf-8")
    )
    cm = pd.read_csv(OUTPUTS_DIR / "classifier" / "confusion_matrix.csv", index_col=0)
    data, sel, test, cal, th, dom = (
        r["data"],
        r["model_selection"],
        r["test"],
        r["calibration"],
        r["thresholds"],
        r["domain_shift_dataset1"],
    )
    full = r["end_to_end_dataset2_test"]
    enabled = full["enabled_classes"]
    nd, sizes = data["near_duplicates"], data["split_sizes"]
    pcq = th["test_at_per_class_thresholds"]
    single = th["test_at_precision_threshold"]
    costq = th["test_at_cost_threshold"]
    worst = min(test["per_class"].items(), key=lambda kv: kv[1]["f1"])
    never = [c for c, t in th["per_class_thresholds"].items() if t >= 1.0]
    weak_single = {
        c: v
        for c, v in th["test_per_class_at_precision_threshold"].items()
        if v["routed"] and v["precision"] < th["target_precision"]
    }

    sel_rows = ["| Modelo | Macro-F1 na validação |", "| --- | --- |"]
    for k, v in sorted(sel["validation_macro_f1"].items(), key=lambda kv: -kv[1]):
        mark = " (escolhido)" if k == sel["chosen"] else ""
        sel_rows.append(f"| {model_name(k)}{mark} | {pct(v)} |")

    class_rows = [
        "| Classe | Precisão | Recall | F1 | Tickets no teste |",
        "| --- | --- | --- | --- | --- |",
    ]
    for c, v in sorted(test["per_class"].items(), key=lambda kv: kv[1]["f1"]):
        class_rows.append(
            f"| {c} | {pct(v['precision'])} | {pct(v['recall'])} | {pct(v['f1'])} | {n(v['support'])} |"
        )

    cm_rows = [
        "| Real \\ Previsto | " + " | ".join(cm.columns) + " |",
        "| --- |" + " --- |" * len(cm.columns),
    ]
    for real, row in cm.iterrows():
        cm_rows.append(
            f"| **{real}** | "
            + " | ".join(
                f"**{n(v)}**" if real == col else n(v) for col, v in row.items()
            )
            + " |"
        )

    rule_rows = [
        "| Regra | Limiar | Cobertura | Precisão (IC 95%) | Ponto fraco |",
        "| --- | --- | --- | --- | --- |",
        f"| Limiar único escolhido para 95% de precisão | {d(th['precision_threshold'], 3)} | {pct(single['coverage'])} | {pct(single['precision'])} ({ci(single['precision_ci95'])}) | "
        + "; ".join(f"{c} com {pct(v['precision'])}" for c, v in weak_single.items())
        + " |",
        f"| Limiares por classe, só o classificador | um por classe | {pct(pcq['coverage'])} | {pct(pcq['precision'])} ({ci(pcq['precision_ci95'])}) | Três classes sem prova de 95% no teste |",
        f"| **Fluxo completo da demo** (adotado) | um por classe | **{pct(full['coverage'])}** | **{pct(full['precision'])}** ({ci(full['precision_ci95'])}) | Só {len(enabled)} classes roteiam sozinhas até o piloto |",
        f"| Limiar pelo custo do erro ({th['cost_threshold_inputs']['triage_minutes']} min de triagem contra {th['cost_threshold_inputs']['rework_minutes']} min de retrabalho) | {d(th['cost_threshold'], 2)} | {pct(costq['coverage'])} | {pct(costq['precision'])} ({ci(costq['precision_ci95'])}) | Abaixo dos 95% exigidos |",
    ]

    thr_rows = [
        "| Classe | Limiar | Previstos | Acima do limiar | Precisão (IC 95%) | Na demo |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for c, v in th["test_per_class_at_per_class_thresholds"].items():
        t = th["per_class_thresholds"][c]
        prec = (
            "não roteado"
            if not v["routed"]
            else f"{pct(v['precision'])} ({ci(v['precision_ci95'])})"
        )
        status = (
            "nunca roteada"
            if t >= 1.0
            else "roteia sozinha"
            if c in enabled
            else "em piloto"
        )
        thr_rows.append(
            f"| {c} | {'—' if t >= 1.0 else d(t, 2)} | {n(v['predicted'])} | {n(v['routed'])} | {prec} | {status} |"
        )

    e2e = dom["end_to_end"]
    routed_classes = ", ".join(f"{c} {n(k)}" for c, k in e2e["routed_by_class"].items())
    shares = ", ".join(
        f"{c} {pct(v)}" for c, v in list(dom["predicted_class_shares"].items())[:3]
    )
    pilot = [
        c
        for c, v in th["test_per_class_at_per_class_thresholds"].items()
        if v["routed"] and c not in enabled
    ]
    below_note = (
        f"\n\nA validação garantia {pct(th['target_precision'], 0)} para todas as classes, mas no teste o limite inferior ficou abaixo do alvo em "
        + ", ".join(
            f"{c} ({pct(th['test_per_class_at_per_class_thresholds'][c]['precision_ci95'][0])})"
            for c in pilot
        )
        + ". Essas classes ficam **em piloto**: a demo manda os tickets delas para a triagem humana, mesmo acima do limiar, "
        "até o piloto provar a precisão com tickets novos. Como o teste escolheu as classes habilitadas, o piloto também precisa confirmá-las."
    )

    full_rows = [
        "| Classe | Roteados sozinhos | Precisão (IC 95%) |",
        "| --- | --- | --- |",
    ] + [
        f"| {c} | {n(v['routed'])} | {pct(v['precision'])} ({ci(v['precision_ci95'])}) |"
        for c, v in full["routed_by_class"].items()
    ]
    reason_rows = ["| Por que foi para uma pessoa | Tickets |", "| --- | --- |"] + [
        f"| {k} | {n(v)} |" for k, v in full["to_people_by_reason"].items()
    ]
    adm = full["administrative_rights_routed_elsewhere"]
    adm_queues = ", ".join(f"{q} {n(k)}" for q, k in adm["by_queue"].items())
    adm_texts = "\n".join(f"- “{t[:160]}”" for t in adm["texts"])
    if_all = full["if_every_class_is_enabled"]

    md = f"""# Classificador de tickets

> Gerado por `solution/scripts/write_classifier_report.py` a partir de `solution/outputs/classifier/`.
> Não editar à mão: rode `uv run python scripts/train_classifier.py` e depois este script.

Um classificador TF-IDF + SVM linear acerta {pct(test["accuracy"])} dos tickets de TI do Dataset 2 (macro-F1 {pct(test["macro_f1"])}). A demo completa (política, guarda de domínio, limiar por classe e só as classes que provaram 95% de precisão no teste) roteia sozinha {pct(full["coverage"])} dos tickets de teste com {pct(full["precision"])} de precisão (IC 95% {ci(full["precision_ci95"])}), e o resto vai para a triagem humana. Nos tickets do Dataset 1, de outra operação, ele não serve: a política, o guarda de vocabulário e os limiares mandam {pct(1 - dom["end_to_end"]["share_routed"])} deles para humanos.

## Dados e divisão

- {n(data["rows"])} tickets em {len(data["classes"])} classes.
- Quase-duplicatas (similaridade de cosseno TF-IDF de pelo menos {d(nd["similarity_threshold"], 1)}): {n(nd["groups_with_more_than_one_ticket"])} grupos com {n(nd["tickets_in_those_groups"])} tickets. Cada grupo fica inteiro de um lado da divisão, para o teste não ver textos quase iguais aos do treino.
- {n(nd["groups_with_conflicting_labels"])} desses grupos ({n(nd["tickets_in_conflicting_groups"])} tickets) têm rótulos diferentes para textos quase iguais. É a primeira evidência de ruído de rótulo (X1); a lista está em `solution/outputs/classifier/near_duplicate_conflicts.csv`.
- Divisão estratificada: treino {n(sizes["train"])}, calibração {n(sizes["calibration"])}, escolha de limiar {n(sizes["validation"])} e teste {n(sizes["test"])}. O teste foi usado uma única vez, no fim; ele também decidiu quais classes roteiam sozinhas, então o piloto precisa confirmá-las.

## Escolha do modelo

{chr(10).join(sel_rows)}

## Resultado no teste

Acurácia {pct(test["accuracy"])} (IC 95% {ci(test["accuracy_ci95"])}); macro-F1 {pct(test["macro_f1"])} (IC 95% {ci(test["macro_f1_ci95"])}). A classe mais difícil é {worst[0]}, com F1 de {pct(worst[1]["f1"])}.

{chr(10).join(class_rows)}

Matriz de confusão do teste (linhas: classe real; colunas: classe prevista). Hardware é o destino mais comum dos erros.

{chr(10).join(cm_rows)}

## Calibração

Probabilidades calibradas pelo método sigmoide, ajustado só na parte de calibração. Erro de calibração esperado no teste: {pct(cal["ece_test_after"])}.

## Regras de roteamento

O alvo é o da hipótese 3.2 do Diogo: pelo menos 95% de precisão nos tickets que a IA roteia sozinha, olhando por categoria. Cada limiar foi escolhido na parte de validação de modo que o limite inferior do intervalo de 95% da precisão fique acima do alvo.

{chr(10).join(rule_rows)}

Limiares por classe, medidos no teste:

{chr(10).join(thr_rows)}{below_note}

## Fluxo completo da demo no teste

Cada um dos {n(sizes["test"])} tickets de teste passou pela mesma função da demo (`support_triage.triage`): política, guarda, classificador, limiar e classes habilitadas. É esse o número que vale para a proposta. O texto do Dataset 2 já vem pré-processado, então a política roda sobre ele como está.

Roteados sozinhos: {n(full["routed"])} ({pct(full["coverage"])}), com {pct(full["precision"])} de precisão (IC 95% {ci(full["precision_ci95"])}).

{chr(10).join(full_rows)}

{chr(10).join(reason_rows)}

Se o piloto comprovar todas as classes menos {", ".join(never)}, o mesmo fluxo roteia {pct(if_all["coverage"])} com {pct(if_all["precision"])} de precisão (IC 95% {ci(if_all["precision_ci95"])}).

**Pedidos de privilégio fora da classe Administrative rights.** Bloquear a classe prevista não basta: um pedido de privilégio previsto como outra classe seria roteado sozinho. No teste, {n(adm["routed_on_their_own"])} dos {n(adm["true_administrative_rights"])} tickets rotulados como Administrative rights foram roteados sozinhos ({adm_queues}). Os textos estão abaixo; lidos um a um, relatam falhas (patch, atualização do Windows, boot, monitor, publicação de vagas), sem pedido de acesso ou de privilégio, o que sugere ruído de rótulo (X1). Ainda assim, no piloto todo ticket roteado sozinho que um agente reclassificar como pedido de privilégio conta como violação da política.

{adm_texts}

## Desvio de domínio: o modelo nos tickets do Dataset 1

O modelo aprendeu com tickets de TI e não com suporte ao cliente. Aplicado às {n(dom["tickets"])} descrições do Dataset 1, ele prevê {shares}, com confiança mediana de {pct(dom["median_confidence"])}. Sem proteção, {pct(dom["share_above_precision_threshold"])} passariam do limiar único e {pct(dom["share_above_per_class_thresholds"])} dos limiares por classe: confiança alta não garante que o ticket seja do domínio.

O guarda mede quanto das palavras de conteúdo do ticket o modelo viu no treino; palavras gramaticais como “my” ou “the” não contam, porque o pré-processamento do Dataset 2 removeu umas e manteve outras. Na validação, a mediana é {pct(dom["vocabulary_coverage_median_dataset2_validation"], 0)}; no Dataset 1, {pct(dom["vocabulary_coverage_median_dataset1"])}. Com o corte em {pct(dom["guard_threshold_vocabulary_coverage"])} (o 1º percentil da validação), o guarda manda para humanos {pct(dom["share_of_dataset1_stopped_by_guard"])} dos tickets do Dataset 1 e só {pct(dom["share_of_dataset2_test_stopped_by_guard"])} dos tickets de teste do Dataset 2.

De ponta a ponta (política, guarda, classificador e limiares), {n(e2e["routed"])} dos {n(dom["tickets"])} tickets do Dataset 1 ({pct(e2e["share_routed"])}) ainda seriam roteados sozinhos: {routed_classes}. São em geral textos genéricos com palavras de TI, como “suspeito de um problema de hardware”. A fila escolhida não é absurda, mas é a de outra operação: por isso o modelo precisa ser retreinado com os tickets da própria operação antes de qualquer uso real.
"""
    REPORT.write_text(md, encoding="utf-8")
    print(f"wrote {REPORT}")


if __name__ == "__main__":
    main()
