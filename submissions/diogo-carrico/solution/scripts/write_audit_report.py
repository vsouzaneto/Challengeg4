"""Write docs/auditoria-dados.md (pt-BR) from outputs/audit/*.json.

Every number in the report comes from the JSON produced by run_audit.py; none is typed by hand.
Run from the solution folder:  uv run python scripts/write_audit_report.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from support_triage.fmt import d, n, pct, pv
from support_triage.paths import OUTPUTS_DIR, SOLUTION_DIR

AUDIT = OUTPUTS_DIR / "audit"
REPORT = SOLUTION_DIR.parent / "docs" / "auditoria-dados.md"


def main() -> None:
    a = json.loads((AUDIT / "audit_d1.json").read_text(encoding="utf-8"))
    b = json.loads((AUDIT / "audit_d2.json").read_text(encoding="utf-8"))

    c, cat, ts, csat, txt = (
        a["counts"],
        a["categoricals"],
        a["timestamps"],
        a["csat"],
        a["text_signal"],
    )
    types = cat["Ticket Type"]["shares"]
    status = cat["Ticket Status"]["shares"]
    refund_cancel = types["Refund request"] + types["Cancellation request"]
    closed = ts["closed_with_both_timestamps"]
    rho_all = csat["spearman_resolution_hours_vs_csat_all_valid_pairs"]
    rho_pos = csat["spearman_resolution_hours_vs_csat_nonnegative_only"]
    top = a["description_text"]["top_sentences"]
    examples = "; ".join(f"“{e}”" for e in a["resolution_text"]["random_examples"][:3])
    t_start, t_end = ts["response_and_resolution_range"]
    p_start, p_end = ts["purchase_range"]
    n_placeholders = len(a["description_text"]["other_curly_placeholders"])

    def p(name: str) -> str:
        return pv(cat[name]["p_value_vs_uniform"])

    ty, sj, pr = (
        txt["description_predicts_type"],
        txt["description_predicts_subject"],
        txt["description_predicts_priority"],
    )
    bc, cls, tok, form = (
        b["counts"],
        b["classes"],
        b["tokens_per_document"],
        b["text_form"],
    )
    # most_common_tokens[2:5] are the e-mail greetings and sign-offs quoted in the verdict; fail loudly if that changes.
    assert form["most_common_tokens"][2:5] == ["hi", "regards", "thank"], form[
        "most_common_tokens"
    ][:6]
    class_list = ", ".join(f"{k} {pct(v)}" for k, v in cls["shares"].items())

    md = f"""# Auditoria dos dados

> Gerado por `solution/scripts/write_audit_report.py` a partir de `solution/outputs/audit/*.json`.
> Não editar à mão: rode `uv run python scripts/run_audit.py` e depois este script.

## Veredito

**Dataset 1 (tickets de suporte) é sintético.** Oito sinais, vindos de cinco partes diferentes da base (descrições, resoluções, e-mails, horários e distribuições), apontam na mesma direção. A base não sustenta diagnóstico de tempo nem de satisfação: serve para demonstrar o método e o fluxo, não para medir uma operação.

**Dataset 2 (tickets de TI) traz texto de e-mails de suporte, já pré-processado** (“{form["most_common_tokens"][2]}”, “{form["most_common_tokens"][3]}” e “{form["most_common_tokens"][4]}” estão entre as palavras mais comuns), com {cls["n_categories"]} classes desbalanceadas. É a base para treinar e avaliar o classificador.

## O que o brief diz e o que os dados mostram

| O brief diz | Os dados mostram |
| --- | --- |
| ~30.000 tickets | {n(c["parsed_records"])} registros. O arquivo tem {n(c["physical_lines"])} linhas físicas porque {n(c["records_with_line_breaks_in_description"])} descrições contêm quebras de linha |
| 3 tipos de ticket (Technical, Billing, Product inquiry) | 5 tipos. Refund request e Cancellation request somam {pct(refund_cancel)} do volume |
| First Response Time = tempo até a primeira resposta | É um carimbo de data e hora, não uma duração. Sem a data de abertura do ticket, o tempo de resposta não pode ser calculado |
| Time to Resolution = tempo total até a resolução | Também é um carimbo. Em {pct(ts["share_resolution_before_first_response"])} dos {n(closed)} tickets fechados, a resolução acontece antes da primeira resposta |
| Nota de satisfação do cliente | Existe só nos {n(csat["present"])} tickets fechados ({pct(status["Closed"])} da base) |

## Sinais de dados sintéticos no Dataset 1

| # | Sinal | Evidência |
| --- | --- | --- |
| 1 | Placeholder de template não preenchido | `{{product_purchased}}` em {pct(a["description_text"]["share_with_placeholder"], 0)} das descrições, mais {n_placeholders} variações (`{{order_id}}`, `{{product_price}}`...). Nenhuma descrição cita o produto comprado ({pct(a["description_text"]["share_mentioning_actual_product"], 0)}) |
| 2 | Texto repetido | “{top[1]["sentence"]}” aparece {n(top[1]["count"])} vezes e “{top[0]["sentence"]}” {n(top[0]["count"])} vezes em {n(c["parsed_records"])} descrições |
| 3 | Resoluções sem sentido | {n(a["resolution_text"]["present"])} resoluções, todas diferentes, com {d(a["resolution_text"]["mean_words"], 1)} palavras em média. Exemplos sorteados: {examples} |
| 4 | E-mails de exemplo | {pct(a["emails"]["share_reserved_example_domains"], 0)} em example.com, .org ou .net, domínios reservados para documentação (RFC 2606) |
| 5 | Janela de tempo impossível | Todas as respostas e resoluções cabem em {d(ts["response_and_resolution_span_hours"], 1)} horas ({t_start} a {t_end}), enquanto as compras vão de {p_start} a {p_end} |
| 6 | Timestamps contraditórios | {pct(ts["share_resolution_before_first_response"])} dos tickets fechados são resolvidos antes da primeira resposta |
| 7 | Distribuições de sorteio | Tipo (p {p("Ticket Type")}), prioridade (p {p("Ticket Priority")}), canal (p {p("Ticket Channel")}), status (p {p("Ticket Status")}), {cat["Product Purchased"]["n_categories"]} produtos (p {p("Product Purchased")}), CSAT (p = {d(csat["distribution"]["p_value_vs_uniform"], 2)}) e idade de {a["age"]["min"]} a {a["age"]["max"]} anos (p = {d(a["age"]["p_value_vs_uniform"], 2)}) são indistinguíveis de partes iguais (qui-quadrado). Gênero (p {p("Customer Gender")}) e assunto (p {p("Ticket Subject")}) se afastam um pouco, com no máximo {d(max(cat["Customer Gender"]["max_min_share_ratio"], cat["Ticket Subject"]["max_min_share_ratio"]), 1)}× de diferença entre categorias; “Other” em {pct(cat["Customer Gender"]["shares"]["Other"])} dos clientes é improvável numa base real |
| 8 | Nada se relaciona com nada | Assunto × tipo: V de Cramér {d(a["associations"]["subject_vs_type"]["cramers_v"], 2)} (p = {d(a["associations"]["subject_vs_type"]["p_value"], 2)}). Um modelo TF-IDF + regressão logística prevê o tipo pela descrição com {pct(ty["accuracy_mean"])} de acurácia, contra {pct(ty["chance_uniform"])} de chance; assunto {pct(sj["accuracy_mean"])} contra {pct(sj["chance_uniform"])}; prioridade {pct(pr["accuracy_mean"])} contra {pct(pr["chance_uniform"])} |

## Satisfação e tempo de resolução

Correlação de Spearman entre horas de resolução e CSAT: ρ = {d(rho_all["rho"], 3)} (p de permutação {d(rho_all["permutation_p_value"], 2)}; faixa nula de 95%: {d(rho_all["null_95pct_band"][0], 3)} a {d(rho_all["null_95pct_band"][1], 3)}; n = {n(rho_all["n"])}). Só com durações não negativas: ρ = {d(rho_pos["rho"], 3)} (p = {d(rho_pos["permutation_p_value"], 2)}; n = {n(rho_pos["n"])}).

Uma correlação perto de zero, sozinha, não provaria nada; aqui ela é coerente com os outros oito sinais.

## Estrutura por status

| Status | Tickets | Primeira resposta | Resolução e CSAT |
| --- | --- | --- | --- |
| Open | {n(a["missing_by_status"]["Open"]["First Response Time"])} ({pct(status["Open"])}) | Nenhuma | Nenhuma |
| Pending Customer Response | {n(ts["first_response_present_by_status"]["Pending Customer Response"])} ({pct(status["Pending Customer Response"])}) | Todas | Nenhuma |
| Closed | {n(closed)} ({pct(status["Closed"])}) | Todas | Todas |

## Dataset 2

- {n(bc["rows"])} tickets em {cls["n_categories"]} classes: {class_list}. A maior classe é {d(cls["max_min_share_ratio"], 1)}× a menor, então a acurácia sozinha engana: reportamos também macro-F1.
- Texto pré-processado: {pct(form["share_lowercase_only"], 0)} em minúsculas, nenhum dígito ({pct(form["share_documents_with_digits"], 0)}), pontuação em {pct(form["share_documents_with_punctuation"], 2)} dos documentos. Stopwords ainda são {pct(form["share_tokens_that_are_english_stopwords"])} dos tokens, então não foram removidas por completo. Uma comparação com modelos de linguagem precisa levar isso em conta, porque eles foram treinados com texto natural.
- {n(form["vocabulary_size"])} palavras distintas; mediana de {d(tok["median"], 0)} tokens por documento (p95 {d(tok["p95"], 0)}, máximo {n(tok["max"])}); {n(bc["documents_under_5_tokens"])} documentos com menos de 5 tokens.
- Nenhum texto duplicado exatamente ({n(bc["exact_duplicate_rows"])}), portanto nenhum conflito de rótulo entre duplicatas exatas. A estimativa de ruído de rótulo (X1) vai depender de quase-duplicatas e de revisão manual.

## O que isso muda no plano

- **Diagnóstico (D1):** gargalos e drivers de satisfação não podem ser medidos nesta base. O tempo de resposta não existe, o CSAT é uniforme e nenhuma variável se associa a outra. Entregamos o teste nulo e a lista do que medir numa operação real.
- **Ligação entre os datasets:** aplicar o modelo do Dataset 2 às descrições do Dataset 1 mede o desvio de domínio, não o desempenho.
- **Rascunhos de resposta (X2):** ancorados numa base de conhecimento própria, nunca nas resoluções do Dataset 1.
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(md, encoding="utf-8")
    print(f"wrote {REPORT}")


if __name__ == "__main__":
    main()
