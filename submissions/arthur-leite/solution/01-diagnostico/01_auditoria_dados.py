"""
Fase 1: auditoria de qualidade dos dados.

Pergunta: antes de diagnosticar a operação, os dados conseguem sustentar
um diagnóstico? Este script testa isso e grava o resultado em
outputs/auditoria.md.

Versão 2: incorpora o parecer do agente juiz (process-log/revisoes/fase1_auditoria_parecer.md).

Rodar a partir da pasta submissions/arthur-leite:
    python solution/01-diagnostico/01_auditoria_dados.py
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")  # Windows: evita erro de cp1252 com saída redirecionada
import itertools
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, chisquare, kruskal, norm, spearmanr
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

ROOT = Path(__file__).resolve().parents[2]
DS1 = ROOT / "data/ds1_customer_support/customer_support_tickets.csv"
DS2 = ROOT / "data/ds2_it_tickets/all_tickets_processed_improved_v3.csv"
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)

CSAT = "Customer Satisfaction Rating"
CATEGORICAS = ["Ticket Type", "Ticket Subject", "Ticket Priority",
               "Ticket Channel", "Product Purchased", "Customer Gender", "Ticket Status"]


def n(x: float, casas: int = 0) -> str:
    """Formata número no padrão brasileiro: 8.469 e 0,07."""
    s = f"{x:,.{casas}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def pct(x: float, casas: int = 0) -> str:
    return n(100 * x, casas) + "%"


def cramers_v_corrigido(a: pd.Series, b: pd.Series) -> tuple[float, float]:
    """Cramér's V com correção de viés (Bergsma, 2013) e p-valor do qui-quadrado.
    A correção evita que variáveis com muitas categorias (ex.: 42 produtos) inflem o V."""
    t = pd.crosstab(a, b)
    chi2, p, _, _ = chi2_contingency(t)
    N = t.values.sum()
    r, k = t.shape
    phi2 = max(0.0, chi2 / N - (k - 1) * (r - 1) / (N - 1))
    rc, kc = r - (r - 1) ** 2 / (N - 1), k - (k - 1) ** 2 / (N - 1)
    return float(np.sqrt(phi2 / max(1e-12, min(kc - 1, rc - 1)))), float(p)


def auditar_ds1(d: pd.DataFrame) -> list[str]:
    L = ["## Dataset 1: Customer Support Tickets", "",
         "### 1. O que o enunciado promete × o que os dados entregam", "",
         "| Enunciado do case | Dados reais |", "|---|---|"]
    frt = pd.to_datetime(d["First Response Time"])
    ttr = pd.to_datetime(d["Time to Resolution"])
    compra = pd.to_datetime(d["Date of Purchase"])
    placeholder = d["Ticket Description"].str.contains(r"\{[^}]*\}", regex=True)
    abertura = (d["Ticket Description"].str.replace(r"\{[^}]*\}", "<P>", regex=True)
                .str.split(r"(?<=[.?!])\s", n=1, regex=True).str[0])
    janela_h = (max(frt.max(), ttr.max()) - min(frt.min(), ttr.min())).total_seconds() / 3600
    L += [f"| ~30.000 tickets | **{n(len(d))}** |",
          f"| 3 tipos de ticket | **{d['Ticket Type'].nunique()}** tipos |",
          f"| Texto completo da reclamação | **{pct(placeholder.mean())}** com campo não preenchido (`{{product_purchased}}`); "
          f"só **{abertura.nunique()}** frases de abertura, a mais comum em {pct(abertura.value_counts(normalize=True).iloc[0])} |",
          f"| Texto da resolução aplicada | Frases sem sentido no estilo da biblioteca Faker (ex.: *\"Offer investment fish.\"*) |",
          f"| Tempo até 1ª resposta / até resolução | **Carimbos de data e hora**, todos numa janela de **{n(janela_h)} horas** "
          f"({frt.min():%d/%m/%Y} a {ttr.max():%d/%m/%Y}), para compras feitas entre {compra.min():%Y} e {compra.max():%Y} |",
          f"| Dados de cliente | E-mails todos em domínios `@example` |"]

    # 2. Sinais de que os dados foram gerados
    dur = (ttr - frt).dt.total_seconds() / 3600
    m_id = frt.notna()
    rho_id = spearmanr(d.loc[m_id, "Ticket ID"], frt[m_id].astype("int64"))
    status_ok = (
        d.loc[d["Ticket Status"] == "Open", ["First Response Time", "Time to Resolution", CSAT]].isna().all().all()
        and d.loc[d["Ticket Status"] == "Pending Customer Response", "Time to Resolution"].isna().all()
        and d.loc[d["Ticket Status"] == "Closed", ["First Response Time", "Time to Resolution", CSAT]].notna().all().all())
    notas = d[CSAT].dropna()
    dist = notas.value_counts().sort_index()
    status = d["Ticket Status"].value_counts()
    L += ["", "### 2. Evidências de que os dados são sintéticos", "",
          f"- Em **{pct((dur < 0).sum() / dur.notna().sum())}** dos tickets fechados ({n((dur < 0).sum())} de {n(dur.notna().sum())}) "
          "a resolução acontece **antes** da primeira resposta.",
          f"- Os carimbos de tempo acompanham a ordem do `Ticket ID` (Spearman ρ = {n(rho_id.statistic, 2)}, p < 0,001): "
          "cada linha recebe \"agora + sorteio de até 24 h\" enquanto o gerador avança, um rastro típico de geração automática.",
          f"- CSAT de 1 a 5 com frequências {' / '.join(n(v) for v in dist)}: estatisticamente uniforme (p = {n(chisquare(dist).pvalue, 2)}).",
          f"- Os 3 status também são equiprováveis ({', '.join(f'{k}: {n(v)}' for k, v in status.items())}; "
          f"p = {n(chisquare(status).pvalue, 2)}). **Os {pct(1 - status['Closed'] / len(d))} \"não fechados\" vêm de um sorteio de 1/3 "
          "por status, e não de um backlog real.**",
          f"- A única regra de processo consistente é a máquina de estados (Open sem resposta; Pending com resposta e sem resolução; "
          f"Closed completo): {'sem nenhuma exceção' if status_ok else 'COM exceções'}."]

    # 3. Independência entre variáveis
    pares = []
    for a, b in itertools.combinations(CATEGORICAS, 2):
        v, p = cramers_v_corrigido(d[a], d[b])
        pares.append((a, b, v, p))
    sig = [x for x in pares if x[3] < 0.05]
    L += ["", "### 3. As variáveis não se relacionam entre si", "",
          f"Dos **{len(pares)}** pares de variáveis categóricas, **{len(sig)}** têm associação estatisticamente significativa (p < 0,05). "
          f"Maior Cramér's V (corrigido para viés): **{n(max(x[2] for x in pares), 3)}**. "
          "Numa operação real, prioridade e canal, ou tipo e assunto, estariam claramente associados.", "",
          "| Par | V corrigido | p-valor |", "|---|---|---|"]
    L += [f"| {a} × {b} | {n(v, 3)} | {n(p, 2)} |" for a, b, v, p in pares]

    # Anti-exemplo: o texto da descrição não prevê o assunto nem o tipo
    L += ["", "**Teste com classificador:** se o texto da descrição fosse real, ele deveria prever o assunto e o tipo do ticket.", "",
          "| Alvo | Acurácia (validação cruzada, 5 dobras) | Chute da classe mais frequente |", "|---|---|---|"]
    X = TfidfVectorizer(min_df=2).fit_transform(d["Ticket Description"])
    for alvo in ["Ticket Subject", "Ticket Type", "Ticket Priority"]:
        acc = cross_val_score(LogisticRegression(max_iter=2000), X, d[alvo], cv=5).mean()
        L.append(f"| {alvo} | {pct(acc, 1)} | {pct(d[alvo].value_counts(normalize=True).iloc[0], 1)} |")

    # 4. O que explica o CSAT (com correção para múltiplas comparações)
    c = d[d[CSAT].notna()].assign(duracao_h=dur, hora_1a_resposta=frt.dt.hour + frt.dt.minute / 60,
                                  data_compra=compra.map(pd.Timestamp.toordinal))
    testes = []
    for col in CATEGORICAS[:-1]:
        testes.append((col, "Kruskal-Wallis", kruskal(*[g[CSAT] for _, g in c.groupby(col)]).pvalue))
    for col in ["duracao_h", "Customer Age", "hora_1a_resposta", "data_compra"]:
        m = c[[col, CSAT]].dropna()
        r = spearmanr(m[col], m[CSAT])
        testes.append((col, f"Spearman ρ = {n(r.statistic, 3)}", r.pvalue))
    bonf = 0.05 / len(testes)
    sd = notas.std()
    grupo = len(notas) / 4
    mde = (norm.ppf(0.975) + norm.ppf(0.8)) * sd * np.sqrt(2 / grupo)
    L += ["", "### 4. Nada explica a satisfação", "",
          f"{len(testes)} testes. Com correção de Bonferroni, o limiar de significância passa a ser p < {n(bonf, 4)}.", "",
          "| Variável | Teste | p-valor | Significativo após correção? |", "|---|---|---|---|"]
    L += [f"| {v} | {t} | {n(p, 3)} | {'sim' if p < bonf else 'não'} |" for v, t, p in testes]
    L += ["", f"- Os {sum(p < 0.05 for _, _, p in testes)} p-valores abaixo de 0,05 são compatíveis com o acaso em {len(testes)} testes; nenhum sobrevive à correção e os efeitos são desprezíveis (|ρ| < 0,05).",
          f"- **Poder estatístico:** com ~{n(grupo)} notas por grupo (desvio-padrão {n(sd, 2)}), os testes detectariam uma diferença de "
          f"**{n(mde, 2)} ponto** de CSAT entre dois grupos (80% de poder, α = 5%). Não detectar nada não é falta de amostra."]

    # 4b. A pergunta literal do Diretor: quais combinações geram os piores tempos?
    f = d[d["Ticket Status"] == "Closed"].assign(duracao_h=dur)
    chaves = ["Ticket Channel", "Ticket Priority", "Ticket Type"]
    g = f.groupby(chaves)["duracao_h"].agg(["mean", "std", "count"])
    g["ic"] = 1.96 * g["std"] / np.sqrt(g["count"])
    ordem = g.sort_values("mean", ascending=False)
    amplitude = ordem["mean"].iloc[0] - ordem["mean"].iloc[-1]
    rng = np.random.default_rng(0)
    amplitudes_acaso = []
    for _ in range(1000):  # embaralha as durações entre os tickets: quanto "gap" o puro acaso produz?
        emb = f.assign(duracao_h=rng.permutation(f["duracao_h"].values)).groupby(chaves)["duracao_h"].mean()
        amplitudes_acaso.append(emb.max() - emb.min())
    p_perm = (np.array(amplitudes_acaso) >= amplitude).mean()
    kw = kruskal(*[x["duracao_h"].values for _, x in f.groupby(chaves)]).pvalue

    def linha(idx, row):
        return f"| {' · '.join(idx)} | {n(row['mean'], 1)} h | {n(row['mean'] - row['ic'], 1)} a {n(row['mean'] + row['ic'], 1)} h | {int(row['count'])} |"

    L += ["", "### 4b. Onde o fluxo trava? A pergunta respondida ao pé da letra", "",
          f"Duração (resolução − 1ª resposta) dos {n(len(f))} tickets fechados, nas {len(g)} combinações de canal × prioridade × tipo.", "",
          "| As 3 \"piores\" combinações | Média | IC95% | Tickets |", "|---|---|---|---|"]
    L += [linha(i, r) for i, r in ordem.head(3).iterrows()]
    L += ["", "| As 3 \"melhores\" combinações | Média | IC95% | Tickets |", "|---|---|---|---|"]
    L += [linha(i, r) for i, r in ordem.tail(3).iloc[::-1].iterrows()]
    L += ["", f"- A \"pior\" combinação parece **{n(amplitude, 1)} h mais lenta** que a \"melhor\". Mas, embaralhando as durações "
          f"ao acaso entre os tickets, a diferença entre a pior e a melhor combinação fica em média em **{n(np.mean(amplitudes_acaso), 1)} h**: "
          f"o gap observado não supera o acaso (teste de permutação p = {n(p_perm, 2)}; Kruskal-Wallis entre as {len(g)} combinações p = {n(kw, 2)}).",
          "- Por que alguns intervalos das extremas não se sobrepõem e ainda assim é ruído: com 80 combinações, as mais extremas "
          "*sempre* parecem diferentes (comparações múltiplas). O teste certo compara o gap observado com o que o acaso produz, "
          "e ele não passa disso. Note também que as \"melhores\" têm duração média **negativa**, o que é impossível numa operação real.",
          "- **Resposta:** com estes dados, nenhuma combinação trava o fluxo de forma distinguível do ruído. "
          "Apontar \"X é o gargalo\" seria escolher um número sorteado."]

    L += ["", "### 5. Conclusão e o que ainda é aproveitável", "",
          "**O Dataset 1 é sintético, com variáveis geradas de forma independente.** Diferenças entre grupos (tempo por prioridade, "
          "CSAT por canal etc.) estão dentro do ruído e **não devem ser usadas para diagnóstico**: produziriam números com aparência "
          "real que levariam a decisões erradas.", "",
          "Ainda aproveitável, com essa ressalva explícita:",
          "- A **estrutura** da operação: a máquina de estados Open → Pending → Closed, canais, prioridades, tipos e assuntos.",
          "  Ela serve de molde para o fluxo proposto e para o plano de instrumentação.",
          "- As 16 frases-modelo como casos de teste de fumaça do protótipo (nunca para treino ou avaliação).",
          "- O mix de volume só como ilustração: ele é quase uniforme por construção."]
    return L


def auditar_ds2(d: pd.DataFrame) -> list[str]:
    palavras = d["Document"].str.split().str.len()
    dist = d["Topic_group"].value_counts()
    return ["", "## Dataset 2: IT Service Ticket Classification", "",
            f"- **{n(len(d))}** registros; nulos: {int(d.isna().sum().sum())}; textos duplicados: {d.duplicated('Document').sum()}.",
            "- Texto real de e-mails corporativos de TI, **parcialmente pré-processado**: minúsculas, sem pontuação e sem números, "
            "dados pessoais removidos e stopwords removidas do corpo (o assunto do e-mail ainda as mantém).",
            f"- Tamanho: mediana de {n(palavras.median())} palavras (75% até {n(palavras.quantile(.75))}; máximo {n(palavras.max())}).",
            f"- **8 classes desbalanceadas**: {dist.index[0]} {pct(dist.iloc[0] / len(d), 1)} × {dist.index[-1]} "
            f"{pct(dist.iloc[-1] / len(d), 1)}. Por isso a métrica principal é o **F1-macro**, e não só a acurácia.",
            "- **Ruído de rótulo:** numa amostra de 32 textos lida pelo agente juiz, cerca de 15 a 25% dos rótulos eram duvidosos ou ambíguos "
            "(ex.: pedido de acesso a fila rotulado como `Storage`). Isso coloca um teto natural na acurácia de qualquer modelo.",
            "- **Não tem** tempo, canal nem satisfação: serve para provar a automação de triagem, não para diagnóstico operacional."]


def main() -> None:
    d1, d2 = pd.read_csv(DS1), pd.read_csv(DS2)
    linhas = ["# Auditoria de qualidade dos dados", "",
              "_Gerado por `01_auditoria_dados.py`. Revisado por agente juiz independente "
              "(`process-log/revisoes/fase1_auditoria_parecer.md`)._", ""] + auditar_ds1(d1) + auditar_ds2(d2)
    (OUT / "auditoria.md").write_text("\n".join(linhas), encoding="utf-8")
    print("\n".join(linhas))


if __name__ == "__main__":
    main()
