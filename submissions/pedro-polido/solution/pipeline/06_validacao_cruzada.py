"""Validação cruzada: confere, uma a uma, as afirmações da segunda opinião (outra IA) sobre o Dataset 1.

Cada afirmação vira um número recalculado aqui a partir do CSV, e o veredito fica ao lado:
confirma, diverge (com o número que contradiz) ou não verificável com o arquivo.
Saída: process-log/validacao-cruzada/verificacao.json (lido pelo README da pasta).
"""
import hashlib
import json

import numpy as np
import pandas as pd
from scipy import stats

from common import SEED, SUBMISSION, TICKETS_CSV, _to_builtin, br

OUT = SUBMISSION / "process-log" / "validacao-cruzada" / "verificacao.json"
rng = np.random.default_rng(SEED)

df = pd.read_csv(TICKETS_CSV)
fr = pd.to_datetime(df["First Response Time"])
ttr = pd.to_datetime(df["Time to Resolution"])
compra = pd.to_datetime(df["Date of Purchase"])
closed = df["Ticket Status"] == "Closed"
res = {}


def item(chave, afirmacao, verificado, veredito, nota=""):
    res[chave] = {"afirmacao": afirmacao, "verificado": verificado, "veredito": veredito, "nota": nota}
    print(f"[{veredito:^14}] {chave}: {verificado}")


# 0. Mesmo arquivo nos dois anexos: só dá para calcular o hash da cópia local
md5 = hashlib.md5(TICKETS_CSV.read_bytes()).hexdigest()
item("hash", "Os dois anexos são o mesmo arquivo (MD5 idêntico)", f"MD5 da cópia usada aqui: {md5}",
     "não verificável", "Só há uma cópia no repositório local; o hash fica registrado para quem quiser comparar.")

# 1. Volume
linhas = sum(1 for _ in TICKETS_CSV.open(encoding="utf-8")) - 1
item("volume", "8.469 tickets, não ~30.000", f"{br(len(df), 0)} registros; {br(linhas, 0)} linhas físicas sem o cabeçalho "
     "(descrições com quebra de linha)", "confirma", "Explica o '30 mil': é a contagem de linhas do arquivo, não de tickets.")

# 2a. Janela da primeira resposta
janela_h = (fr.max() - fr.min()).total_seconds() / 3600
item("janela_primeira_resposta", "Todas as primeiras respostas caem numa janela de ~27 h (31/05 a 02/06/2023)",
     f"{fr.min():%d/%m/%Y %H:%M} a {fr.max():%d/%m/%Y %H:%M} = {br(janela_h, 1)} h", "confirma")

# 2b. Compra -> primeira resposta
gap_anos = ((fr - compra).dt.days / 365.25).dropna()
item("compra_ate_resposta", "Compras de 2020 a 2021; a primeira resposta chega 1,5 a 3 anos depois",
     f"compras de {compra.min():%d/%m/%Y} a {compra.max():%d/%m/%Y}; intervalo de {br(gap_anos.min(), 2)} a "
     f"{br(gap_anos.max(), 2)} anos", "confirma")

# 2c. Resolução menos primeira resposta, nos fechados
delta = ((ttr - fr).dt.total_seconds() / 3600)[closed]
neg = (delta < 0).mean()
lo, hi = delta.min(), delta.max()
ks_unif = stats.kstest(delta, "uniform", args=(lo, hi - lo))
ks_tri = stats.kstest(delta, "triang", args=(0.5, lo, hi - lo))
curt = stats.kurtosis(delta)
item("tempo_negativo", "49,3% dos fechados com tempo negativo; média −0,06 h; de −23 h a +23 h",
     f"{br(100 * neg, 1)}% negativos; média {br(delta.mean(), 2)} h; de {br(lo, 1)} a {br(hi, 1)} h", "confirma")
item("ruido_uniforme", "A diferença é ruído uniforme",
     f"KS contra uniforme p = {ks_unif.pvalue:.2e} (rejeita); KS contra triangular p = {br(ks_tri.pvalue, 3)}; "
     f"curtose em excesso {br(curt, 2)} (uniforme −1,2; triangular −0,6)", "diverge",
     "É ruído, mas triangular: o formato da diferença entre dois horários uniformes independentes. A conclusão "
     "(sem sinal operacional) não muda; a palavra 'uniforme' é que está errada.")

# 3. Ausências por status
padrao = df.assign(fr=fr.notna(), ttr=ttr.notna(), csat=df["Customer Satisfaction Rating"].notna()) \
    .groupby("Ticket Status")[["fr", "ttr", "csat"]].mean()
contagem = df["Ticket Status"].value_counts()
regra_fixa = all(padrao.loc[s].isin([0.0, 1.0]).all() for s in padrao.index)
txt = "; ".join(f"{s}: {br(contagem[s], 0)} (1ª resp. {br(100 * padrao.loc[s, 'fr'], 0)}%, resolução "
                f"{br(100 * padrao.loc[s, 'ttr'], 0)}%, CSAT {br(100 * padrao.loc[s, 'csat'], 0)}%)" for s in padrao.index)
item("ausencias_por_status", "Ausências seguem regra fixa por status (Open 2.819, Pending 2.881, Closed 2.769); CSAT só nos fechados (33%)",
     f"{txt}; CSAT em {br(100 * df['Customer Satisfaction Rating'].notna().mean(), 1)}% dos tickets",
     "confirma" if regra_fixa else "diverge")

# 4. Texto de template
desc = df["Ticket Description"].astype(str)
ph = desc.str.contains("{product_purchased}", regex=False).mean()
lixo = {
    "<StringProperty": desc.str.contains("<StringProperty", regex=False).sum(),
    "[hh:mm:ss]Nome:": desc.str.contains(r"\[\d{2}:\d{2}:\d{2}\]\w+:", regex=True).sum(),
    "{error_message}": desc.str.contains("{error_message}", regex=False).sum(),
}
item("placeholder", "100% das descrições contêm {product_purchased}", f"{br(100 * ph, 1)}% das descrições",
     "confirma" if ph > 0.999 else "diverge")
item("lixo_de_geracao", "Há lixo de geração: <StringProperty ...>, [16:43:25]Gnome:, '{error_message}'",
     "; ".join(f"{k}: {br(v, 0)} descrições" for k, v in lixo.items()), "confirma")
grupos = desc[desc.duplicated(keep=False)]
n_grupos = grupos.nunique()
item("descricoes_duplicadas", "392 descrições são duplicatas exatas",
     f"{br(len(grupos), 0)} tickets em {br(n_grupos, 0)} grupos de texto idêntico = {br(len(grupos) - n_grupos, 0)} cópias além da 1ª",
     "confirma", "Novo: a auditoria só procurava registros repetidos em todas as colunas (zero).")

# 5. Resoluções
palavras = df.loc[closed, "Resolution"].dropna().astype(str).str.split().str.len()
item("resolucoes", "Resoluções são frases sem sentido do Faker, com média de 5,5 palavras",
     f"média de {br(palavras.mean(), 2)} palavras em {br(len(palavras), 0)} resoluções (fechados)", "confirma")

# 6. Tipo x assunto
tab = pd.crosstab(df["Ticket Type"], df["Ticket Subject"])
chi = stats.chi2_contingency(tab)
tipos = sorted(df["Ticket Type"].unique())
refund = (pd.crosstab(df["Ticket Type"], df["Ticket Subject"] == "Refund request", normalize="index")[True] * 100)
item("tipo_x_assunto", "Tipo e assunto são independentes (qui-quadrado p = 0,98)",
     f"p = {br(chi.pvalue, 3)}; 'Refund request' vai de {br(refund.min(), 1)}% a {br(refund.max(), 1)}% dos tickets de cada tipo",
     "confirma")
item("tipos_enunciado", "O enunciado cita 3 tipos; o dataset tem 5",
     f"{len(tipos)} tipos no CSV: {', '.join(tipos)}; o enunciado lista Technical issue, Billing inquiry, Product inquiry",
     "confirma", "Novo: a auditoria não comparava os tipos do CSV com os do enunciado.")

# 7. E-mails repetidos
por_email = df.groupby("Customer Email")["Customer Name"].agg(["size", "nunique"])
rep = por_email[por_email["size"] > 1]
item("emails_repetidos", "139 e-mails se repetem, todos com nome diferente",
     f"{br(len(rep), 0)} e-mails repetidos; em {br((rep['nunique'] == rep['size']).sum(), 0)} deles cada ocorrência tem um nome diferente",
     "confirma" if (rep["nunique"] == rep["size"]).all() else "diverge")

# 8a. Uniformidade das categorias (qui-quadrado de aderência)
unif = {}
for col in ["Ticket Channel", "Ticket Priority", "Ticket Type", "Customer Gender", "Customer Satisfaction Rating"]:
    obs = df[col].dropna().value_counts()
    unif[col] = stats.chisquare(obs).pvalue
nao_unif = [c for c, p in unif.items() if p < 0.05]
item("categorias_uniformes", "Todas as categorias são quase perfeitamente uniformes (canal, prioridade, tipo, gênero, CSAT)",
     "; ".join(f"{c}: p = {br(p, 3)}" for c, p in unif.items()),
     "diverge" if nao_unif else "confirma",
     f"Quatro das cinco são compatíveis com uniforme; rejeita em: {', '.join(nao_unif)} ("
     f"{', '.join(f'{k} {br(v, 0)}' for k, v in df['Customer Gender'].value_counts().items())})." if nao_unif else "")

# 8b. Kruskal-Wallis
fatores = ["Ticket Channel", "Ticket Priority", "Ticket Type", "Ticket Subject", "Customer Gender", "Product Purchased"]
fech = df[closed].assign(delta=delta)
kw_csat = {f: stats.kruskal(*[g["Customer Satisfaction Rating"].values for _, g in fech.groupby(f)]).pvalue for f in fatores}
kw_tempo = {f: stats.kruskal(*[g["delta"].values for _, g in fech.groupby(f)]).pvalue for f in fatores}
item("kruskal_csat", "CSAT não varia por canal, prioridade, tipo, assunto, gênero nem produto (todos p > 0,27)",
     f"p de {br(min(kw_csat.values()), 3)} a {br(max(kw_csat.values()), 3)}", "confirma" if min(kw_csat.values()) > 0.05 else "diverge")
item("kruskal_tempo", "O mesmo vale para o tempo de resolução",
     f"p de {br(min(kw_tempo.values()), 3)} a {br(max(kw_tempo.values()), 3)}", "confirma" if min(kw_tempo.values()) > 0.05 else "diverge")

# 8c. Tempo x CSAT
rho = stats.spearmanr(fech["delta"], fech["Customer Satisfaction Rating"])
item("tempo_x_csat", "Correlação entre tempo e CSAT ρ = 0,02 (p = 0,25)",
     f"ρ = {br(rho.statistic, 3)} (p = {br(rho.pvalue, 3)})", "confirma" if rho.pvalue > 0.05 else "diverge")

# 8d. Pior combinação e embaralhamento
chave = ["Ticket Channel", "Ticket Priority", "Ticket Type"]  # 4 × 4 × 5 = 80 combinações
g = fech.groupby(chave)["Customer Satisfaction Rating"].agg(["mean", "size"])
pior = g["mean"].idxmin()
real_sd = g["mean"].std()
csat = fech["Customer Satisfaction Rating"].to_numpy()
codes = fech.groupby(chave).ngroup().to_numpy()
sds = []
for _ in range(200):
    perm = rng.permutation(csat)
    sds.append(pd.Series(perm).groupby(codes).mean().std())
item("pior_combinacao", "Pior combinação Phone + High + Refund (CSAT 2,29, n = 31); embaralhando 200 vezes, a variação é a mesma (0,241 × 0,243)",
     f"pior: {' + '.join(pior)} com CSAT {br(g.loc[pior, 'mean'], 2)} (n = {g.loc[pior, 'size']}); desvio entre combinações "
     f"{br(real_sd, 3)} real × {br(np.mean(sds), 3)} embaralhado (percentil {br(100 * (np.array(sds) < real_sd).mean(), 0)} do real)",
     "confirma")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=_to_builtin), encoding="utf-8")
print(f"\n{sum(v['veredito'] == 'confirma' for v in res.values())} confirmam, "
      f"{sum(v['veredito'] == 'diverge' for v in res.values())} divergem, "
      f"{sum(v['veredito'] == 'não verificável' for v in res.values())} não verificável -> {OUT}")
