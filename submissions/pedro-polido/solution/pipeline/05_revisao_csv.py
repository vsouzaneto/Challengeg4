"""Revisão usando SÓ o CSV do Dataset 1: verificação do arquivo, automações avaliadas, o que não automatizar e ROI.

Toda afirmação sobre os dados sai de código deste script. Rótulos usados na página:
  FATO = medido no CSV · INFERÊNCIA = dedução a partir dos dados · PREMISSA = valor assumido por falta de dado.

Saída: app/data/revisao.json (consumido por app/revisao.html). Uso: python 05_revisao_csv.py
"""
import csv
import hashlib
import io
import re
import warnings
from collections import Counter

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline

from common import REPO_ROOT, SEED, TICKETS_CSV, br, save_json


def pct(x, d=1):
    return br(100 * x, d, "%")


def cramer_v(ct):
    chi2, p, _, _ = stats.chi2_contingency(ct)
    return p, float(np.sqrt(chi2 / (ct.values.sum() * (min(ct.shape) - 1))))


# ================================================================ Etapa 1 — verificação do arquivo
raw = TICKETS_CSV.read_bytes()
text = raw.decode("utf-8")  # estrito: levanta erro se o arquivo não for UTF-8 válido
rows = list(csv.reader(io.StringIO(text)))
df = pd.read_csv(TICKETS_CSV)
df_python = pd.read_csv(TICKETS_CSV, engine="python", quotechar='"', doublequote=True)
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    df_warn = pd.read_csv(TICKETS_CSV, engine="python", on_bad_lines="warn")
discarded = [str(w.message) for w in caught if "Skipping line" in str(w.message)]
with warnings.catch_warnings(record=True) as caught_nq:
    warnings.simplefilter("always")
    df_noquote = pd.read_csv(TICKETS_CSV, quoting=csv.QUOTE_NONE, engine="python", on_bad_lines="warn")
noquote_skipped = sum("Skipping line" in str(w.message) for w in caught_nq)
N = len(df)
desc = df["Ticket Description"]
embedded = int(desc.str.count("\n").sum())
multiline = desc.str.count("\n") > 0
ids = df["Ticket ID"]
purchase = pd.to_datetime(df["Date of Purchase"])
first_response = pd.to_datetime(df["First Response Time"])
resolution = pd.to_datetime(df["Time to Resolution"])
months = purchase.dt.to_period("M")
all_months = pd.period_range(months.min(), months.max(), freq="M")
all_days = pd.date_range(purchase.min(), purchase.max())

etapa1 = {
    "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
    "bom": raw[:3] == b"\xef\xbb\xbf", "nao_ascii": sum(b > 127 for b in raw), "substituicao": text.count("�"),
    "separador": csv.Sniffer().sniff(text[:20000], delimiters=",;\t|").delimiter,
    "fim_de_linha": "CRLF" if b"\r\n" in raw else "LF",
    "linhas_fisicas": text.count("\n"),
    "registros": {"csv_reader": len(rows) - 1, "pandas_padrao": N, "pandas_python_aspas": len(df_python),
                  "pandas_on_bad_lines_warn": len(df_warn), "descartadas": len(discarded),
                  "sem_respeitar_aspas": len(df_noquote), "sem_aspas_linhas_malformadas": noquote_skipped},
    "campos_por_registro": dict(Counter(len(r) for r in rows)),
    "iguais_padrao_python": bool(df.equals(df_python)),
    "quebras_dentro_de_campos": embedded, "coluna_das_quebras": [c for c in df.columns if df[c].astype(str).str.contains("\n").any()],
    "registros_multilinha": int(multiline.sum()), "registros_multilinha_pct": float(multiline.mean()),
    "max_quebras_num_registro": int(desc.str.count("\n").max()),
    "ids_unicos": int(ids.nunique()), "ids_duplicados": int(ids.duplicated().sum()), "id_min": int(ids.min()), "id_max": int(ids.max()),
    "ids_contiguos": sorted(ids) == list(range(1, N + 1)),
    "registros_vazios": int(df.isna().all(axis=1).sum()), "linhas_em_branco_fisicas": sum(1 for l in text.splitlines() if not l.strip()),
    "registros_repetidos": int(df.drop(columns="Ticket ID").duplicated().sum()),
    "compra": {"de": f"{purchase.min():%d/%m/%Y}", "ate": f"{purchase.max():%d/%m/%Y}", "meses": int(months.nunique()),
               "meses_no_intervalo": len(all_months), "dias_sem_registro": len(set(all_days.date) - set(purchase.dt.date)),
               "dias_no_intervalo": len(all_days), "por_mes_min": int(months.value_counts().min()),
               "por_mes_max": int(months.value_counts().max())},
    "primeira_resposta": {"de": f"{first_response.min():%d/%m/%Y %H:%M}", "ate": f"{first_response.max():%d/%m/%Y %H:%M}", "preenchidos": int(first_response.notna().sum())},
    "resolucao": {"de": f"{resolution.min():%d/%m/%Y %H:%M}", "ate": f"{resolution.max():%d/%m/%Y %H:%M}", "preenchidos": int(resolution.notna().sum())},
    "coluna_data_abertura": [c for c in df.columns if re.search(r"creat|open|submit", c, re.I)],
    "colunas": [{"coluna": c, "tipo": str(df[c].dtype), "nulos": int(df[c].isna().sum()), "pct": float(df[c].isna().mean())} for c in df.columns],
    "nulos_por_status": {s: {c: float(g[c].isna().mean()) for c in ["Resolution", "First Response Time", "Time to Resolution", "Customer Satisfaction Rating"]}
                         for s, g in df.groupby("Ticket Status")},
}
etapa1["faltam_para_30mil"] = 30000 - N

# Descrições idênticas: "registros_repetidos" compara todas as colunas (zero); aqui compara só o texto.
# Apontado pela segunda opinião (process-log/validacao-cruzada), que minha checagem original não cobria.
dup_desc = desc[desc.duplicated(keep=False)]
dup_groups = df.loc[dup_desc.index].groupby(dup_desc)
etapa1["descricoes_identicas"] = {
    "tickets": len(dup_desc), "grupos": int(dup_desc.nunique()), "copias": len(dup_desc) - int(dup_desc.nunique()),
    "maior_grupo": int(dup_groups.size().max()),
    "grupos_mesmo_email": int((dup_groups["Customer Email"].nunique() == 1).sum()),
    "grupos_mesmo_assunto": int((dup_groups["Ticket Subject"].nunique() == 1).sum()),
}
# Tipos de ticket: o enunciado lista os tipos na tabela de colunas; o CSV tem outros
BRIEF = REPO_ROOT / "challenges" / "process-002-support" / "README.md"
m = re.search(r"`Ticket Type`\s*\|\s*Tipo \(([^)]*)\)", BRIEF.read_text(encoding="utf-8")) if BRIEF.exists() else None
tipos_brief = [t.strip() for t in m.group(1).split(",")] if m else []
fora = ~df["Ticket Type"].isin(tipos_brief)
etapa1["tipos"] = {"brief": tipos_brief, "csv": sorted(df["Ticket Type"].unique()),
                   "fora_do_brief": sorted(df.loc[fora, "Ticket Type"].unique()), "fora_do_brief_n": int(fora.sum()),
                   "fora_do_brief_pct": float(fora.mean())}
print(f"  descrições idênticas: {etapa1['descricoes_identicas']} | tipos fora do brief: {etapa1['tipos']['fora_do_brief']} ({int(fora.sum())})")
print(f"Etapa 1: {N} registros, {etapa1['linhas_fisicas']} linhas físicas, {embedded} quebras internas, "
      f"IDs contíguos: {etapa1['ids_contiguos']}")

# ================================================================ 2.1 — candidatas a automação
status = df["Ticket Status"]
GENERIC_OPEN = "I'm having an issue with the {product_purchased}. Please assist."
generic = desc.str.startswith(GENERIC_OPEN, na=False)
err_placeholder = desc.str.contains("{error_message}", regex=False)
kept = {
    "abertos": int((status == "Open").sum()), "abertos_pct": float((status == "Open").mean()),
    "abertos_sem_resposta": int(((status == "Open") & first_response.isna()).sum()),
    "abertos_critical": int(((status == "Open") & (df["Ticket Priority"] == "Critical")).sum()),
    "pendentes": int((status == "Pending Customer Response").sum()), "pendentes_pct": float((status == "Pending Customer Response").mean()),
    "abertura_generica": int(generic.sum()), "abertura_generica_pct": float(generic.mean()),
    # A frase genérica NUNCA é a descrição inteira: todas continuam com mais texto (1ª versão tratou como "genérica")
    "so_abertura_generica": int((desc.str.strip() == GENERIC_OPEN).sum()),
    "palavras_apos_abertura_mediana": float(desc[generic].str[len(GENERIC_OPEN):].str.split().str.len().median()),
    "erro_vazio": int(err_placeholder.sum()), "erro_vazio_pct": float(err_placeholder.mean()),
}

cv = StratifiedKFold(5, shuffle=True, random_state=SEED)


def predictability(texts, target):
    model = make_pipeline(TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True), LogisticRegression(max_iter=2000))
    acc = cross_val_score(model, texts, target, cv=cv).mean()
    majority = cross_val_score(DummyClassifier(strategy="most_frequent"), texts, target, cv=cv).mean()
    return {"modelo": float(acc), "majoritaria": float(majority), "acaso": 1 / target.nunique(), "classes": int(target.nunique())}


subject_desc = df["Ticket Subject"] + " " + desc
pred = {
    "tipo": predictability(subject_desc, df["Ticket Type"]),
    "assunto": predictability(desc, df["Ticket Subject"]),
    "prioridade": predictability(subject_desc, df["Ticket Priority"]),
}
for k, v in pred.items():
    print(f"  prever {k}: {v['modelo']:.4f} (majoritária {v['majoritaria']:.4f}, acaso {v['acaso']:.4f})")

routing_cols = [c for c in df.columns if re.search(r"queue|team|agent|assign|owner|group|department", c, re.I)]
p_ts, v_ts = cramer_v(pd.crosstab(df["Ticket Subject"], df["Ticket Type"]))
named = df["Ticket Subject"].isin(df["Ticket Type"].unique())
agree = int((named & (df["Ticket Subject"] == df["Ticket Type"])).sum())

closed = df[status == "Closed"]
res = closed["Resolution"]
res_words = res.str.split().str.len()
SUPPORT_ACTIONS = r"refund|reset|updat|replac|install|password|softwar|firmwar|restart|reboot|driver|cable|setting"
tfv = TfidfVectorizer().fit(pd.concat([res, closed["Ticket Description"]]))
R, D = tfv.transform(res), tfv.transform(closed["Ticket Description"])
same = np.asarray(R.multiply(D).sum(axis=1)).ravel().mean()
rng = np.random.default_rng(SEED)
shuffled = np.mean([np.asarray(R.multiply(D[rng.permutation(len(closed))]).sum(axis=1)).ravel().mean() for _ in range(20)])

first_sentence = desc.str.split(r"(?<=[.?!])\s", n=1, regex=True).str[0]
top20 = first_sentence.where(first_sentence.isin(first_sentence.value_counts().head(20).index))
p_first_subject = stats.chi2_contingency(pd.crosstab(top20, df["Ticket Subject"]))[1]

URGENT_PHRASE = "I need assistance as soon as possible because it's affecting my work"
URGENT_WORDS = r"\burgent\b|\basap\b|\bimmediately\b|\bcritical\b|\bemergency\b|\bdata loss\b|\bcannot\b|\bunable\b|\bnot working\b"
urgent_phrase = desc.str.contains(URGENT_PHRASE, regex=False)
urgent_words = desc.str.contains(URGENT_WORDS, case=False, regex=True)
prio = df["Ticket Priority"]
p_phrase = stats.chi2_contingency(pd.crosstab(urgent_phrase, prio))[1]
p_words = stats.chi2_contingency(pd.crosstab(urgent_words, prio))[1]

# Duplicatas: similaridade de cosseno TF-IDF entre descrições, por blocos (evita a matriz densa 8.469 × 8.469)
X = TfidfVectorizer().fit_transform(desc)
emails = df["Customer Email"].str.lower().values
subjects = df["Ticket Subject"].values
pairs = same_email = same_subject = 0
involved = set()
for start in range(0, N, 1000):
    block = (X[start:start + 1000] @ X.T).toarray()
    rows_, cols_ = np.nonzero(block >= 0.8)
    rows_ += start
    keep = cols_ > rows_
    rows_, cols_ = rows_[keep], cols_[keep]
    pairs += len(rows_)
    involved.update(rows_.tolist())
    involved.update(cols_.tolist())
    same_email += int((emails[rows_] == emails[cols_]).sum())
    same_subject += int((subjects[rows_] == subjects[cols_]).sum())
subject_chance = float((df["Ticket Subject"].value_counts(normalize=True) ** 2).sum())

email_counts = df["Customer Email"].str.lower().value_counts()
repeated = email_counts[email_counts > 1]
groups = df[df["Customer Email"].str.lower().isin(repeated.index)].groupby(df["Customer Email"].str.lower())
multi_name = int((groups["Customer Name"].nunique() > 1).sum())

descartadas = {
    "predicao": pred, "colunas_de_roteamento": routing_cols, "total_colunas": len(df.columns),
    "tipo_x_assunto": {"p": p_ts, "v": v_ts, "assunto_com_nome_de_tipo": int(named.sum()), "concordam": agree},
    "resolucoes": {"n": len(res), "palavras_min": int(res_words.min()), "palavras_mediana": float(res_words.median()),
                   "palavras_max": int(res_words.max()), "distintas": int(res.nunique()),
                   "com_acao_tecnica": int(res.str.contains(SUPPORT_ACTIONS, case=False).sum()),
                   "similaridade_mesmo_ticket": float(same), "similaridade_aleatoria": float(shuffled)},
    "abertura_x_assunto_p": p_first_subject,
    "urgencia": {"frase": int(urgent_phrase.sum()), "frase_p": p_phrase,
                 "frase_low": float((prio[urgent_phrase] == "Low").mean()), "sem_frase_low": float((prio[~urgent_phrase] == "Low").mean()),
                 "palavras": int(urgent_words.sum()), "palavras_p": p_words, "palavras_low": int((urgent_words & (prio == "Low")).sum())},
    "duplicatas": {"pares_08": pairs, "tickets_envolvidos": len(involved), "por_mil": 1000 * pairs / N,
                   "mesmo_email": same_email, "mesmo_assunto": same_subject / pairs if pairs else 0.0, "assunto_acaso": subject_chance},
    "emails_repetidos": int(len(repeated)), "tickets_email_repetido": int(repeated.sum()), "grupos_nome_diferente": multi_name,
}
print(f"  duplicatas: {pairs} pares ≥ 0,8, {same_email} do mesmo e-mail | e-mails repetidos: {len(repeated)} ({multi_name} com nome diferente)")

# ================================================================ 2.2 — o que não automatizar
T, S = df["Ticket Type"], df["Ticket Subject"]
rx = lambda p: desc.str.contains(p, flags=re.IGNORECASE, regex=True)
DATA_LOSS = r"\bdata loss\b|\bdeleted important data\b|\blost all the data\b|\blost my data\b|\bdata (?:is|was) lost\b|\b(?:lost|stolen) data\b|\bdata was stolen\b"
ACCESS = r"\bunable to access my \{product_purchased\} account\b|\bforgotten my password\b|\bissues logging into my\b|\baccount is locked\b|\bregain access to my account\b"
SECURITY = r"(?<!/)\bhacked\b|\bidentity theft\b|\bsecurity breach\b|\b(?:data|password|credit card information|username/password) (?:was |were )?stolen\b"
SECURITY_TEMPLATE = r"\bconcerned about the security of my\b"
EMO = (r"\b(?:I'm|am|been) (?:very |really |quite |so )?(?:frustrated|annoyed|upset|angry|disappointed|furious)\b"
       r"|\b(?:it's|it is|this is|it really is) (?:very |really |so )?(?:frustrating|annoying|unacceptable|terrible|ridiculous)\b"
       r"|\bmy frustration\b|\bterrible experience\b|\bfed up\b")
LEGAL = r"\b(?:lawyers?|attorneys?|lawsuits?|sue|suing|legal action|litigation|small claims)\b"
COMPLAINT = r"\bmy (?:first |only |second )?complaint\b|\bcomplaint I have\b|\breport a complaint\b|\bfile a complaint\b"
REPEAT = "already contacted customer support multiple times"


def excerpt(ticket_id, pattern=None, words=18):
    """Trecho LITERAL da descrição: a frase que contém o padrão (ou o início), cortada em N palavras."""
    raw_desc = df.loc[df["Ticket ID"] == ticket_id, "Ticket Description"].iloc[0]
    line = raw_desc.split("\n")[0]
    if pattern:
        line = next(l for l in raw_desc.split("\n") if re.search(pattern, l, re.I))
        m = re.search(pattern, line, re.I)
        cut = line.rfind(". ", 0, m.start())
        line = line[cut + 2:] if cut >= 0 else line
    out = " ".join(line.split(" ")[:words]).strip()
    assert out in raw_desc, ticket_id
    return out


CATS = [  # código, nome, máscara, nível, critério legível, risco, exemplos escolhidos, padrão do trecho
    ("C1", "Reembolso", (T == "Refund request") | (S == "Refund request"), "🧑", "tipo ou assunto = \"Refund request\"",
     "Financeiro + ambiguidade: rótulo e texto divergem até quando tipo e assunto concordam", [70, 134], None),
    ("C2", "Cancelamento", (T == "Cancellation request") | (S == "Cancellation request"), "🧑", "tipo ou assunto = \"Cancellation request\"",
     "Receita e retenção; o texto não confirma o pedido", [30, 82], None),
    ("C3", "Cobrança / pagamento", (T == "Billing inquiry") | (S == "Payment issue"), "🧑", "tipo = \"Billing inquiry\" ou assunto = \"Payment issue\"",
     "Financeiro (estorno, disputa); o texto não traz dado da cobrança", [63, 195], None),
    ("C4", "Perda de dados", (S == "Data loss") | rx(DATA_LOSS), "🧑", "assunto = \"Data loss\" ou texto com data loss, deleted important data, lost all the data…",
     "Irreversível: um reset ou reinstalação automáticos podem destruir o que ainda dá para recuperar", [68, 55], DATA_LOSS),
    ("C5", "Sinal forte de invasão ou roubo", rx(SECURITY), "🧑", "texto com hacked, identity theft, security breach, (data|password|credit card information) stolen",
     "Jurídico e financeiro (fraude, privacidade); falso positivo custa pouco", [418, 3121], SECURITY),
    ("C6", "Emoção ou menção jurídica", rx(EMO) | rx(LEGAL) | rx(COMPLAINT), "🧑", "léxico explícito (frustrated, fed up, lawyer, attorney, \"my complaint\"…)",
     "Emocional, jurídico e reputacional; falso positivo custa pouco (só vai para uma pessoa)", [2993, 4278], EMO + "|" + LEGAL),
    ("C7", "Recuperação de acesso", (S == "Account access") | rx(ACCESS), "🤝", "assunto = \"Account access\" ou frases de login e senha",
     "Tomada de conta por terceiro: nunca liberar acesso sem verificação humana", [38, 7], ACCESS),
    ("C8", "Prioridade Critical", prio == "Critical", "🤝", "prioridade = Critical",
     "SLA; o rótulo não é previsível pelos dados, então o humano confirma", [1, 2], None),
    ("C9", "Reincidência declarada", desc.str.contains(REPEAT, regex=False), "🤝", f"frase \"{REPEAT}\"",
     "Reputacional; sem código de cliente não dá para confirmar a reincidência", [4, 239], REPEAT),
    ("C10", "Urgência declarada", urgent_phrase, "🤝", f"frase \"{URGENT_PHRASE}\"",
     "Reputacional; a prioridade atribuída acompanha o texto só fracamente", [33, 106], "as soon as possible"),
]
cats = []
for code, name, mask, level, crit, risk, examples, pattern in CATS:
    exs = []
    for tid in examples:
        row = df.loc[df["Ticket ID"] == tid].iloc[0]
        assert mask[row.name], (code, tid)
        exs.append({"id": tid, "tipo": row["Ticket Type"], "assunto": row["Ticket Subject"], "prioridade": row["Ticket Priority"],
                    "trecho": excerpt(tid, pattern)})
    cats.append({"codigo": code, "nome": name, "nivel": level, "criterio": crit, "risco": risk,
                 "volume": int(mask.sum()), "pct": float(mask.mean()), "exemplos": exs})
masks = {c[0]: c[2] for c in CATS}
human = pd.concat([masks[f"C{i}"] for i in range(1, 7)], axis=1).any(axis=1)
assist = pd.concat([masks[f"C{i}"] for i in range(7, 11)], axis=1).any(axis=1)
security_cases = [{"id": int(t), "trecho": excerpt(int(t), SECURITY, 14)} for t in df.loc[masks["C5"], "Ticket ID"]]
labels_only = pd.concat([masks[f"C{i}"] for i in range(1, 4)], axis=1).any(axis=1)
text_only_extra = human & ~labels_only
tmpl = rx(SECURITY_TEMPLATE)
tmpl_p = {col: stats.chi2_contingency(pd.crosstab(tmpl, df[col]))[1] for col in ["Ticket Subject", "Ticket Type", "Ticket Priority"]}
nao_automatizar = {
    "categorias": cats, "uniao_humano": int(human.sum()), "uniao_humano_pct": float(human.mean()),
    "so_assistido": int((assist & ~human).sum()), "so_assistido_pct": float((assist & ~human).mean()),
    "nenhuma": int((~human & ~assist).sum()), "nenhuma_pct": float((~human & ~assist).mean()),
    "c4_assunto": int((S == "Data loss").sum()), "c4_texto": int(rx(DATA_LOSS).sum()), "c4_ambos": int(((S == "Data loss") & rx(DATA_LOSS)).sum()),
    "so_por_rotulo_c1_c3": int(labels_only.sum()), "so_por_rotulo_pct": float(labels_only.mean()),
    "texto_acrescenta": int(text_only_extra.sum()),
    "c5_casos": security_cases, "frase_template_seguranca": int(tmpl.sum()), "frase_template_p": tmpl_p,
    # Leitura dos 19 casos de C6 (INFERÊNCIA, feita lendo o texto de cada um)
    "c6_leitura": {"emoção": [1701, 1754, 2993, 4084, 4283, 4363, 4565, 5379, 5385], "queixa": [2667, 4074, 5903],
                   "jurídico": [4278, 6158, 6610], "falso positivo": [286, 3847, 5502, 7234]},
    # Leitura dos 5 casos de C5 (INFERÊNCIA, feita lendo o texto): relato em 1ª pessoa × texto informativo × ambíguo
    "c5_leitura": {"418": "relato", "3121": "relato", "5047": "ambíguo", "4458": "informativo", "7730": "informativo"},
}
print(f"  não automatizar: 🧑 {human.sum()} ({human.mean():.2%}) | só 🤝 {(assist & ~human).sum()} | nenhuma {(~human & ~assist).sum()}")

# ================================================================ Etapa 3 — ROI
VOL_MES = N / etapa1["compra"]["meses"]  # INFERÊNCIA: não há data de abertura; proxy = registros ÷ meses de compra
# Elegibilidade coerente com o fluxo: o pedido de detalhes só roda para quem não caiu em C1–C6 (esses vão direto para
# uma pessoa). O lembrete vale para qualquer ticket aguardando o cliente, em qualquer caminho do fluxo.
ELIG = {"acuse": 1.0, "lembrete": kept["pendentes_pct"], "pedir_detalhes": float((err_placeholder & ~human).mean())}
kept["pedir_detalhes_fluxo"] = int((err_placeholder & ~human).sum())
kept["erro_vazio_em_c1_c6"] = int((err_placeholder & human).sum())
PREMISSAS = {  # (conservador, provável, otimista) — todas PREMISSA
    "custo_hora": (35.0, 45.0, 55.0),
    "impl_horas": (120, 80, 50),
    "impl_custo_hora": (150.0, 120.0, 100.0),
    "manut_horas_mes": (8, 6, 4),
    "api_reais_por_rascunho": (0.01, 0.005, 0.002),
}
AUTOMACOES = {
    "acuse": {"min": (0.5, 1.0, 1.5), "acerto": (0.99, 0.99, 0.99), "revisao": (0.0, 0.0, 0.0), "llm": False},
    "lembrete": {"min": (2.0, 3.0, 4.0), "acerto": (0.95, 0.97, 0.99), "revisao": (0.0, 0.0, 0.0), "llm": False},
    "pedir_detalhes": {"min": (2.0, 3.0, 4.0), "acerto": (0.70, 0.80, 0.90), "revisao": (1.0, 0.5, 0.25), "llm": True},
}


def scenario(i, vol=VOL_MES, over=None):
    """horas = volume elegível × minutos poupados ÷ 60 × taxa de acerto; ROI 12m e payback como descritos na página."""
    g = lambda k: (over or {}).get(k, PREMISSAS[k][i])
    horas, revisao_h, api = {}, 0.0, 0.0
    for k, a in AUTOMACOES.items():
        v = vol * ELIG[k]
        horas[k] = v * (over or {}).get(f"{k}.min", a["min"][i]) / 60 * (over or {}).get(f"{k}.acerto", a["acerto"][i])
        revisao_h += v * a["revisao"][i] / 60
        api += v * g("api_reais_por_rascunho") if a["llm"] else 0.0
    beneficio = sum(horas.values()) * g("custo_hora")
    manutencao = g("manut_horas_mes") * g("impl_custo_hora")
    custo_mes = manutencao + api + revisao_h * g("custo_hora")
    impl = g("impl_horas") * g("impl_custo_hora")
    custo_12 = impl + 12 * custo_mes
    liquido = beneficio - custo_mes
    return {"horas": horas, "horas_total": sum(horas.values()), "beneficio_mes": beneficio, "manutencao_mes": manutencao,
            "revisao_mes": revisao_h * g("custo_hora"), "api_mes": api, "custo_mes": custo_mes, "implantacao": impl,
            "roi_12m": (12 * beneficio - custo_12) / custo_12, "payback_meses": impl / liquido if liquido > 0 else None}


def breakeven(i):
    lo, hi = 1.0, 1e6
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if scenario(i, vol=mid)["roi_12m"] >= 0 else (mid, hi)
    return hi


NOMES = ["conservador", "provável", "otimista"]
cenarios = {n: {**scenario(i), "equilibrio": breakeven(i), "com_2500": scenario(i, vol=2500.0)} for i, n in enumerate(NOMES)}
sens = []
for k, vals in PREMISSAS.items():
    sens.append({"premissa": k, "pior": scenario(1, over={k: vals[0]})["roi_12m"], "melhor": scenario(1, over={k: vals[2]})["roi_12m"]})
for a, spec in AUTOMACOES.items():
    for f in ("min", "acerto"):
        sens.append({"premissa": f"{a}.{f}", "pior": scenario(1, over={f"{a}.{f}": spec[f][0]})["roi_12m"],
                     "melhor": scenario(1, over={f"{a}.{f}": spec[f][2]})["roi_12m"]})
sens.append({"premissa": "volume", "pior": scenario(1, vol=VOL_MES / 2)["roi_12m"], "melhor": scenario(1, vol=VOL_MES * 2)["roi_12m"]})
sens.sort(key=lambda s: -abs(s["melhor"] - s["pior"]))
ttr_h = (resolution - first_response).dt.total_seconds()[status == "Closed"] / 3600
roi = {"volume_mes": VOL_MES, "meses": etapa1["compra"]["meses"], "tempo_negativo_pct": float((ttr_h < 0).mean()),
       "elegivel": ELIG, "premissas": PREMISSAS,
       "automacoes": AUTOMACOES, "cenarios": cenarios, "sensibilidade": sens}
for n, c in cenarios.items():
    print(f"  ROI {n}: {c['roi_12m']:.1%} | payback {c['payback_meses']} | equilíbrio {c['equilibrio']:.0f}/mês")

save_json("revisao.json", {"etapa1": etapa1, "automatizar": kept, "descartadas": descartadas,
                           "nao_automatizar": nao_automatizar, "roi": roi})
