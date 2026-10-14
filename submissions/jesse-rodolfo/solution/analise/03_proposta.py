"""Bloco 3: contagens do dataset 1 para o 'nao automatizar' e ROI em faixa da fase 1.
Rodar da raiz da submissao: .venv/bin/python -I solution/analise/03_proposta.py
"""
from pathlib import Path
import pandas as pd

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
d1 = pd.read_csv(RAW / "customer_support_tickets.csv")
N = len(d1)
def h(t): print(f"\n=== {t} ===")
def pct(m): return f"{m.sum()} ({m.mean()*100:.1f}%)"

FIN_TIPO = ["Refund request", "Billing inquiry", "Cancellation request"]
FIN_ASSUNTO = ["Refund request", "Payment issue", "Cancellation request"]
fin = d1["Ticket Type"].isin(FIN_TIPO) | d1["Ticket Subject"].isin(FIN_ASSUNTO)
crit = d1["Ticket Priority"] == "Critical"
pend = d1["Ticket Status"] == "Pending Customer Response"

h("Portoes humanos no D1")
for t in FIN_TIPO: print(f"tipo {t}: {pct(d1['Ticket Type'] == t)}")
for a in FIN_ASSUNTO: print(f"assunto {a}: {pct(d1['Ticket Subject'] == a)}")
print("disputa financeira (tipo OU assunto):", pct(fin))
print("Critical:", pct(crit))
for a in ["Data loss", "Account access"]: print(f"assunto {a}: {pct(d1['Ticket Subject'] == a)}")
print("CSAT 1 ou 2 entre fechados:", (d1["Customer Satisfaction Rating"] <= 2).sum(), "de", d1["Customer Satisfaction Rating"].notna().sum())
print("qualquer portao (fin OU critical OU data loss OU account access):",
      pct(fin | crit | d1["Ticket Subject"].isin(["Data loss", "Account access"])))

h("Canal do piloto: pendentes por canal")
ct = pd.crosstab(d1["Ticket Channel"], pend)
print(ct.assign(share_canal=(d1["Ticket Channel"].value_counts() / N * 100).round(1)))
em = d1["Ticket Channel"] == "Email"
print("Email pendentes:", (em & pend).sum(), "| Email pendentes sem portao financeiro/critico:", (em & pend & ~fin & ~crit).sum())
print("share de pendentes sem fin nem critico (todos canais):", f"{(pend & ~fin & ~crit).sum() / pend.sum() * 100:.1f}%")

# ---------- ROI fase 1: cobranca automatica ----------
TICKETS_ANO = 30_000
SHARE_EMAIL = em.mean()
ELEGIVEL = (pend & ~fin & ~crit).sum() / pend.sum()  # pendentes que podem ser encerrados automaticamente
# (conservador, base, otimista). Mesmas premissas do diagnostico + 4 novas da IA (nao medidas)
P = {
    "pendente_pct":   (0.25, 0.34, 0.45),   # diagnostico
    "followups":      (1, 2, 3),            # diagnostico, NAO MEDIDA
    "followup_min":   (3, 5, 8),            # diagnostico, NAO MEDIDA
    "custo_hora":     (30, 50, 70),         # diagnostico, operacao do Jesse
    "substituido":    (0.50, 0.70, 0.90),   # NOVA: % das cobrancas manuais que o lembrete automatico substitui
    "encerrado_pct":  (0.50, 0.35, 0.20),   # NOVA: % dos pendentes elegiveis que chegam ao prazo sem resposta e sao encerrados
    "reabre_pct":     (0.20, 0.10, 0.05),   # NOVA: % dos encerrados automaticamente que o cliente reabre
    "reabertura_min": (30, 20, 10),         # diagnostico: min de retrabalho por reabertura
    "implantacao_h":  (40, 30, 20),         # Jesse: 20 a 40 h, da experiencia montando lembrete e encerramento automatico
}
cen = ["conservador", "base", "otimista"]
rows = {}
for i, c in enumerate(cen):
    p = {k: v[i] for k, v in P.items()}
    cobranca_h = TICKETS_ANO * p["pendente_pct"] * p["followups"] * p["followup_min"] / 60
    recuperado_h = cobranca_h * p["substituido"]
    encerrados = TICKETS_ANO * p["pendente_pct"] * ELEGIVEL * p["encerrado_pct"]
    retrabalho_h = encerrados * p["reabre_pct"] * p["reabertura_min"] / 60
    liquido_h = recuperado_h - retrabalho_h
    rows[c] = {
        "cobranca manual h/ano (todos canais)": cobranca_h,
        "recuperado h/ano": recuperado_h,
        "encerrados auto/ano": encerrados,
        "reabertos apos encerramento/ano": encerrados * p["reabre_pct"],
        "retrabalho h/ano": retrabalho_h,
        "liquido h/ano (todos canais)": liquido_h,
        "liquido R$/ano (todos canais)": liquido_h * p["custo_hora"],
        "liquido h/ano (so Email, piloto)": liquido_h * SHARE_EMAIL,
        "liquido R$/ano (so Email, piloto)": liquido_h * SHARE_EMAIL * p["custo_hora"],
        "implantacao R$": p["implantacao_h"] * p["custo_hora"],
        "payback meses (so Email)": p["implantacao_h"] * p["custo_hora"] / (liquido_h * SHARE_EMAIL * p["custo_hora"] / 12),
    }
h(f"ROI fase 1 (share Email {SHARE_EMAIL*100:.1f}%, pendentes elegiveis a encerramento {ELEGIVEL*100:.1f}%)")
print(pd.DataFrame(rows).round(1).to_string())

h("Volume do piloto (Email, escala 30 mil/ano, base)")
pend_email_sem = TICKETS_ANO * SHARE_EMAIL * P["pendente_pct"][1] / 52
eleg_sem = pend_email_sem * ELEGIVEL
enc_sem = eleg_sem * P["encerrado_pct"][1]
print(f"pendentes Email/semana: {pend_email_sem:.1f} | elegiveis a encerramento/semana: {eleg_sem:.1f} | encerrados auto/semana: {enc_sem:.1f}")
print(f"lembretes/semana (2 por pendente): {pend_email_sem*2:.0f}")
for sem in (4, 8):
    print(f"{sem} semanas: {enc_sem*sem:.0f} encerrados, ~{enc_sem*sem*P['reabre_pct'][1]:.0f} reabertos esperados a 10%")

h("Portao por autoridade (financeiro OU critical), sem acesso e perda de dados")
print("fin OU critical:", pct(fin | crit))

h("Resolution nos fechados")
cl = d1[d1["Ticket Status"] == "Closed"]
print("fechados:", len(cl), "| textos de Resolution unicos:", cl["Resolution"].nunique())
rep = cl.groupby("Resolution")["Ticket Subject"].agg(["size", "nunique"])
print("textos que se repetem:", (rep["size"] > 1).sum(), "| repetidos dentro do mesmo assunto:", cl.duplicated(["Ticket Subject", "Resolution"]).sum())

h("Dataset 2: residuo de assinatura ou ausencia no texto")
d2 = pd.read_csv(RAW / "all_tickets_processed_improved_v3.csv")
doc = d2["Document"].astype(str).str.lower()
termos = {"regards": r"\bregards\b", "thanks/thank": r"\bthanks?\b", "best": r"\bbest\b",
          "annual leave": r"\bannual leave\b", "out of office": r"\bout of (?:the )?office\b"}
m = {}
for k, rx in termos.items():
    m[k] = doc.str.contains(rx, regex=True)
    print(f"{k}: {m[k].sum()} ({m[k].mean()*100:.1f}%)")
qualquer = pd.concat(m, axis=1).any(axis=1)
sem_best = pd.concat({k: v for k, v in m.items() if k != "best"}, axis=1).any(axis=1)
print(f"qualquer termo: {qualquer.sum()} de {len(doc)} ({qualquer.mean()*100:.1f}%)")
print(f"qualquer termo sem 'best' (ambiguo): {sem_best.sum()} ({sem_best.mean()*100:.1f}%)")
print("'best' sem 'best regards':", doc.str.contains(r"\bbest\b(?! regards)", regex=True).sum())
