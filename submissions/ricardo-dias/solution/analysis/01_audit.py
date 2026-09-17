"""Etapa 1 — Auditoria dos dados antes de qualquer conclusão.

Cada achado sai com a evidência numérica que o sustenta, para a UI e os docs
citarem sem reinterpretar. Saída: app/data/audit.json
"""

from __future__ import annotations

import pandas as pd
from scipy import stats
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline

from common import SEED, load_d1, load_d2, r, write_json


def pct(x: float) -> str:
    return f"{x * 100:.1f}%".replace(".", ",")


def thousands(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def fmt_p(p: float) -> str:
    return "p < 0,001" if p < 0.001 else f"p = {p:.2f}".replace(".", ",")


def audit_d1(d1: pd.DataFrame) -> tuple[dict, list[dict]]:
    findings: list[dict] = []
    n = len(d1)

    findings.append({
        "id": "d1-volume",
        "dataset": "D1",
        "title": "Volume menor que o descrito",
        "evidence": f"{thousands(n)} tickets no arquivo, contra ~30.000 no enunciado.",
        "metric": n,
        "implication": "Números anuais são projetados para 30 mil tickets com premissa explícita, não medidos.",
        "severity": "alerta",
    })

    uniform = {c: stats.chisquare(d1[c].value_counts()).pvalue
               for c in ["Ticket Type", "Ticket Priority", "Ticket Channel", "Ticket Status"]}
    closed = d1[d1["Ticket Status"] == "Closed"].copy()
    uniform["CSAT"] = stats.chisquare(closed["Customer Satisfaction Rating"].value_counts()).pvalue
    findings.append({
        "id": "d1-uniform",
        "dataset": "D1",
        "title": "Distribuições uniformes: padrão de dado sintético",
        "evidence": "Tipo, prioridade, canal, status e nota de CSAT têm frequências estatisticamente iguais "
                    f"(qui-quadrado, menor {fmt_p(min(uniform.values()))}).",
        "metric": r(min(uniform.values()), 3),
        "implication": "É improvável que uma operação real tenha ~25% dos tickets em cada prioridade e canal. "
                       "Tratamos os mixes como artefato do gerador, não como retrato de uma operação.",
        "severity": "bloqueante",
    })

    frt = pd.to_datetime(d1["First Response Time"])
    ttr = pd.to_datetime(d1["Time to Resolution"])
    hours = (ttr - frt).dt.total_seconds() / 3600
    closed_hours = hours[d1["Ticket Status"] == "Closed"]
    neg = int((closed_hours < 0).sum())
    span_h = (max(frt.max(), ttr.max()) - min(frt.min(), ttr.min())).total_seconds() / 3600
    findings.append({
        "id": "d1-times",
        "dataset": "D1",
        "title": "Tempos de resposta e resolução não são utilizáveis",
        "evidence": f"Os campos são timestamps (não durações), todos numa janela de {span_h:.0f}h, sem horário de abertura. "
                    f"Em {pct(neg / len(closed_hours))} dos fechados ({thousands(neg)} de {thousands(len(closed_hours))}) a resolução é anterior à 1ª resposta.",
        "metric": r(neg / len(closed_hours)),
        "implication": "Não dá para medir gargalo de tempo por canal/prioridade com honestidade. O diagnóstico usa backlog e pendências.",
        "severity": "bloqueante",
    })

    drivers = {}
    for c in ["Ticket Type", "Ticket Priority", "Ticket Channel", "Customer Gender", "Product Purchased"]:
        groups = [g["Customer Satisfaction Rating"].to_numpy() for _, g in closed.groupby(c)]
        drivers[c] = stats.kruskal(*groups).pvalue
    closed["hours"] = closed_hours
    drivers["duração"] = stats.spearmanr(closed["Customer Satisfaction Rating"], closed["hours"]).pvalue
    drivers["idade"] = stats.spearmanr(closed["Customer Satisfaction Rating"], closed["Customer Age"]).pvalue
    findings.append({
        "id": "d1-csat",
        "dataset": "D1",
        "title": "Não detectamos associação entre CSAT e as variáveis testadas",
        "evidence": f"Kruskal-Wallis (tipo, prioridade, canal, gênero, produto) e Spearman (duração, idade) nos "
                    f"{thousands(len(closed))} tickets fechados: menor {fmt_p(min(drivers.values()))}.",
        "metric": r(min(drivers.values()), 3),
        "implication": "Não temos base para apontar um 'driver de satisfação' com estes dados. Isso não prova ausência de "
                       "efeito numa operação real; efeitos pequenos podem não ser detectáveis (ver diagnóstico).",
        "severity": "bloqueante",
    })

    desc = d1["Ticket Description"]
    placeholder = desc.str.contains(r"\{product_purchased\}").mean()
    # Vetorizador dentro da Pipeline: vocabulário e idf são ajustados só no fold de treino (sem vazamento).
    pipeline = make_pipeline(TfidfVectorizer(min_df=2, ngram_range=(1, 2), sublinear_tf=True),
                             LogisticRegression(max_iter=2000))
    y = d1["Ticket Type"]
    acc = cross_val_score(pipeline, d1["Ticket Subject"] + " " + desc, y,
                          cv=StratifiedKFold(5, shuffle=True, random_state=SEED)).mean()
    chance = y.value_counts(normalize=True).max()
    findings.append({
        "id": "d1-text",
        "dataset": "D1",
        "title": "Não detectamos sinal no texto para prever o tipo do ticket",
        "evidence": f"Placeholder literal {{product_purchased}} em {pct(placeholder)} das descrições; resoluções são frases aleatórias. "
                    f"TF-IDF + regressão logística (validação cruzada de 5 folds, vetorizador ajustado dentro de cada fold) "
                    f"acerta o tipo em {pct(acc)}, contra {pct(chance)} chutando a classe mais comum.",
        "metric": r(acc),
        "implication": "O classificador do protótipo é treinado e avaliado no Dataset 2, que tem texto real.",
        "severity": "bloqueante",
    })

    subj_type_p = stats.chi2_contingency(pd.crosstab(d1["Ticket Subject"], d1["Ticket Type"])).pvalue
    findings.append({
        "id": "d1-subject",
        "dataset": "D1",
        "title": "Assunto e tipo do ticket são independentes",
        "evidence": f"'Refund request' aparece como assunto de tickets técnicos na mesma proporção que de reembolso ({fmt_p(subj_type_p)}).",
        "metric": r(subj_type_p, 3),
        "implication": "Os rótulos foram sorteados de forma independente. Não usar assunto × tipo como regra de roteamento.",
        "severity": "alerta",
    })

    status_counts = d1["Ticket Status"].value_counts()
    open_frt = d1.loc[d1["Ticket Status"] == "Open", "First Response Time"].isna().mean()
    findings.append({
        "id": "d1-backlog",
        "dataset": "D1",
        "title": "Status dos tickets no arquivo (descritivo)",
        "evidence": f"{pct(1 - status_counts['Closed'] / n)} dos registros não estão fechados: "
                    f"{pct(status_counts['Open'] / n)} abertos ({pct(open_frt)} deles sem registro de 1ª resposta) "
                    f"e {pct(status_counts['Pending Customer Response'] / n)} aguardando o cliente.",
        "metric": r(1 - status_counts["Closed"] / n),
        "implication": "Contagem do arquivo, não evidência de gargalo: o mix de status também é uniforme e não há datas "
                       "de abertura para medir envelhecimento da fila.",
        "severity": "info",
    })

    status_mix = [{"status": s, "n": int(c), "share": r(c / n)} for s, c in status_counts.items()]
    return {"rows": n, "columns": d1.shape[1], "statusMix": status_mix}, findings


def audit_d2(d2: pd.DataFrame) -> tuple[dict, list[dict]]:
    n = len(d2)
    counts = d2["Topic_group"].value_counts()
    words = d2["Document"].str.split().str.len()
    dups = int(d2["Document"].duplicated().sum())
    lowercase = not d2["Document"].str.contains("[A-Z]").any()
    no_digits = not d2["Document"].str.contains(r"\d").any()
    tokens = d2["Document"].str.split().explode()
    stop_share = tokens.isin(ENGLISH_STOP_WORDS).mean()
    findings = [
        {
            "id": "d2-quality",
            "dataset": "D2",
            "title": "Dataset 2 é adequado para treinar o classificador",
            "evidence": f"{thousands(n)} tickets, 8 categorias, {dups} duplicatas, mediana de {int(words.median())} palavras.",
            "metric": n,
            "implication": "Base do protótipo: treino e teste com holdout estratificado.",
            "severity": "info",
        },
        {
            "id": "d2-imbalance",
            "dataset": "D2",
            "title": "Categorias desbalanceadas",
            "evidence": f"{counts.index[0]} tem {pct(counts.iloc[0] / n)} dos tickets; {counts.index[-1]} tem {pct(counts.iloc[-1] / n)}.",
            "metric": r(counts.iloc[0] / counts.iloc[-1], 2),
            "implication": "Avaliar por F1 macro e por classe, não só acurácia. As classes pequenas são as de maior risco.",
            "severity": "alerta",
        },
        {
            "id": "d2-preprocessed",
            "dataset": "D2",
            "title": "Texto já vem parcialmente pré-processado",
            "evidence": f"{'Tudo' if lowercase else 'Nem tudo'} em minúsculas, {'nenhum' if no_digits else 'há'} dígito, "
                        f"nomes anonimizados; stopwords mantidas ({pct(stop_share)} dos tokens).",
            "metric": r(stop_share),
            "implication": "Textos novos passam pela mesma normalização (minúsculas, sem dígitos/pontuação) antes de classificar. "
                           "A acurácia em texto cru de outra empresa tende a ser menor.",
            "severity": "alerta",
        },
    ]
    classes = [{"label": k, "n": int(v), "share": r(v / n)} for k, v in counts.items()]
    return {"rows": n, "classes": classes}, findings


def main() -> None:
    d1_summary, d1_findings = audit_d1(load_d1())
    d2_summary, d2_findings = audit_d2(load_d2())
    order = {"bloqueante": 0, "alerta": 1, "info": 2}
    findings = sorted(d1_findings + d2_findings, key=lambda f: (f["dataset"], order[f["severity"]]))
    write_json("audit.json", {"d1": d1_summary, "d2": d2_summary, "findings": findings})
    for f in findings:
        print(f"[{f['severity']:>10}] {f['dataset']} {f['title']}: {f['evidence']}")


if __name__ == "__main__":
    main()
