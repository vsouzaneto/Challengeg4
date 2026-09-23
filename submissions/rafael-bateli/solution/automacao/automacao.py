"""Proposta de automação — Challenge 002, Entrega 2.

Gera todos os números da PROPOSTA_AUTOMACAO.md a partir dos dois datasets:

  A) Dataset 1: que problema o cliente descreve e que sinais de risco o texto traz.
     Cada ticket recebe UMA rota (humano decide / IA sugere e humano aprova /
     automático com saída para humano), com o motivo registrado.
  B) Dataset 2: determinístico × probabilístico na classificação. Regras de
     palavra-chave no MELHOR caso (aprendidas no próprio treino) contra o modelo
     supervisionado com limiar da Entrega 1. Mede também duplicatas, alertas de
     máquina repetidos e onde o modelo erra.
  C) Custo: tokens de LLM por caso de uso × preço, contra as horas devolvidas.
  D) Impacto × esforço de cada automação proposta.
  V) Verificações: partição das rotas, sensibilidade do limiar de duplicata e
     do custo de LLM.

Uso:
    python automacao.py --data ../data/support_tickets.csv --data2 ../data/it_tickets.csv
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
DIAG = HERE.parent / "diagnostico" / "outputs"
SEED = 42
LIMIAR_IA = 0.71  # escolhido na validação da Entrega 1 (triagem_ia.json)

# ---------------------------------------------------------------------------
# Dataset 1 — o texto é montado por templates. Cada frase-template vira um
# problema (abertura) ou um sinal de contexto (fechamento). Por ser template,
# a regra exata reconhece o problema sem ambiguidade; em texto livre isso não
# vale (parte B), e em produção o reconhecimento passa a ser do modelo.
# ---------------------------------------------------------------------------
PROBLEMAS = {
    "perda_de_dados": r"deleted important data|data loss issue|lost all the data|causing data loss",
    "conta_bloqueada": r"account is locked",
    "credencial_invalida": r"Invalid Credentials",
    "senha_reset_quebrado": r"password reset option is not working",
    "hardware": r"strange noises|screen is flickering|is not turning on",
    "rede": r"stable internet connection|fails to connect to any available networks|home Wi-Fi network",
    "software_bug": r"encountering a software bug|glitch in the \{product_purchased\} software",
}
GENERICO = r"^I'm having an issue with the \{product_purchased\}\. Please assist\."

SINAIS = {
    # risco: tiram o ticket da automação
    "seguranca": r"concerned about the security",
    "recontato": r"already contacted customer support multiple times",
    "dinheiro": r"\b(?:refund|charged|invoice|payment|billing|cancel)",
    "reparo_troca": r"might require repair or replacement|not charging",
    # prioridade
    "urgencia": r"as soon as possible because it's affecting my work|rely heavily on my|need them urgently",
    # incidente em massa
    "incidente": r"multiple devices of the same model|others have reported similar|after the recent software update|updated the firmware",
    # o cliente já fez o básico: não mandar o roteiro L1
    "ja_tentou_o_basico": (r"factory reset|checked for (?:any available )?software updates|tried different settings|"
                           r"different cables|user manual|clearing the cache|online tutorials|official support website|"
                           r"checked the device settings"),
}
RISCO = ["perda_de_dados", "seguranca", "conta_bloqueada", "recontato", "dinheiro", "hardware", "reparo_troca"]
TECNICO = ["credencial_invalida", "senha_reset_quebrado", "rede", "software_bug"]

ROTA_HUMANO = "1. Humano decide (IA prepara o dossiê)"
ROTA_COPILOTO = "2. IA sugere, humano aprova"
ROTA_AUTO = "3. Automático, com saída para humano"

# ---------------------------------------------------------------------------
# Premissas de custo e esforço (não vêm do dataset; trocáveis).
# Preços por 1M de tokens (API Anthropic, set/2026). Câmbio é premissa.
# ---------------------------------------------------------------------------
TICKETS_ANO = 30_000
CUSTO_HORA_RS = 35
USD_BRL = 5.40
PRECO = {"haiku-4.5": (1.00, 5.00), "sonnet-5": (2.00, 10.00)}  # (entrada, saída) US$/1M
CACHE_LEITURA = 0.10  # leitura de cache custa ~10% da entrada
CHARS_POR_TOKEN = 4
PRIMEIRO_TOQUE_MIN = {"baixo": 1, "base": 2, "alto": 3}  # agente lê e pede os dados que faltam


def _rx(serie: pd.Series, padrao: str) -> pd.Series:
    return serie.str.contains(padrao, case=False, regex=True)


# ---------------------------------------------------------------------------
def parte_a(caminho: Path) -> tuple[dict, pd.DataFrame]:
    df = pd.read_csv(caminho)
    txt = df["Ticket Description"].fillna("").str.replace("\n", " ")
    f = pd.DataFrame({"Ticket ID": df["Ticket ID"], "canal": df["Ticket Channel"]})
    for nome, p in {**PROBLEMAS, **SINAIS}.items():
        f[nome] = _rx(txt, p)
    f["generico"] = txt.str.contains(GENERICO, regex=True) & ~f[list(PROBLEMAS)].any(axis=1)

    def rota(r) -> tuple[str, str]:
        risco = [k for k in RISCO if r[k]]
        if risco:
            return ROTA_HUMANO, ", ".join(risco)
        # "já tentou o básico" e "incidente" não mudam a rota: viram marcação
        # (pular o roteiro L1 / vincular ao incidente) na rota em que o ticket cair.
        extra = [k for k in ("ja_tentou_o_basico", "incidente") if r[k]]
        tec = [k for k in TECNICO if r[k]]
        if tec:
            return ROTA_COPILOTO, ", ".join(tec + extra)
        base = "sem problema descrito" if r["generico"] else "sem sinal de risco"
        return ROTA_AUTO, ", ".join([base] + extra)

    f[["rota", "motivo"]] = f.apply(lambda r: pd.Series(rota(r)), axis=1)
    f["urgente"] = f["urgencia"]
    f["publico"] = f["canal"].eq("Social media")
    f["texto"] = txt.str.slice(0, 250)
    f[["Ticket ID", "canal", "rota", "motivo", "urgente", "publico", "texto"]].to_csv(
        OUT / "rotas_dataset1.csv", index=False, encoding="utf-8-sig")

    n = len(f)
    por_motivo_humano = {k: int(f.loc[f["rota"] == ROTA_HUMANO, k].sum()) for k in RISCO}
    repetidos = df[df["Customer Email"].duplicated(keep=False)]
    por_email = repetidos.groupby("Customer Email").agg(tickets=("Ticket ID", "size"),
                                                        nomes=("Customer Name", "nunique"),
                                                        produtos=("Product Purchased", "nunique"))
    return {
        "tickets": n,
        "seguranca_ou_conta_bloqueada": int((f["seguranca"] | f["conta_bloqueada"]).sum()),
        "hardware_ou_reparo": int((f["hardware"] | f["reparo_troca"]).sum()),
        "rotas": f["rota"].value_counts().sort_index().to_dict(),
        "rotas_pct": f["rota"].value_counts(normalize=True).sort_index().round(4).to_dict(),
        "problema_descrito": {k: int(f[k].sum()) for k in PROBLEMAS},
        "generico_sem_problema": int(f["generico"].sum()),
        "generico_pct": round(float(f["generico"].mean()), 4),
        "sinais": {k: int(f[k].sum()) for k in SINAIS},
        "humano_por_motivo": por_motivo_humano,
        "ja_tentou_o_basico_pct": round(float(f["ja_tentou_o_basico"].mean()), 4),
        "urgentes_por_rota": f[f["urgente"]]["rota"].value_counts().sort_index().to_dict(),
        "social_media_por_rota": f[f["publico"]]["rota"].value_counts().sort_index().to_dict(),
        "senha_reset_quebrado": int(f["senha_reset_quebrado"].sum()),
        "duplicata_por_email": {
            "emails_repetidos": int(por_email.shape[0]),
            "tickets": int(por_email["tickets"].sum()),
            "pct_emails_com_nomes_diferentes": round(float((por_email["nomes"] == por_email["tickets"]).mean()), 4),
            "pct_emails_com_produtos_diferentes": round(float((por_email["produtos"] == por_email["tickets"]).mean()), 4),
            "exemplo": repetidos[repetidos["Customer Email"] == por_email["tickets"].idxmax()][
                ["Ticket ID", "Customer Name", "Product Purchased", "Ticket Subject"]].to_dict("records"),
        },
        "texto_medio_tokens": round(float(txt.str.len().mean() / CHARS_POR_TOKEN)),
    }, f


# ---------------------------------------------------------------------------
def parte_b(caminho2: Path) -> dict:
    d = pd.read_csv(caminho2)
    X_tmp, X_te, y_tmp, y_te = train_test_split(d["Document"], d["Topic_group"], test_size=0.2,
                                                random_state=SEED, stratify=d["Topic_group"])
    X_tr, _, y_tr, _ = train_test_split(X_tmp, y_tmp, test_size=0.25, random_state=SEED, stratify=y_tmp)
    yt, ytr = y_te.to_numpy(), y_tr.to_numpy()

    # B1. Regras determinísticas no melhor caso: as K palavras mais precisas e
    # frequentes de cada classe, escolhidas olhando o treino. Um analista
    # escrevendo regras à mão dificilmente faz melhor que isso.
    cv = CountVectorizer(binary=True, min_df=20)
    B = cv.fit_transform(X_tr)
    vocab = np.array(cv.get_feature_names_out())
    freq = np.asarray(B.sum(0)).ravel()
    classes = sorted(set(ytr))
    Bte = cv.transform(X_te)
    col = {w: i for i, w in enumerate(vocab)}
    regras = {}
    for k in (5, 10, 20):
        palavras = {}
        for c in classes:
            dentro = np.asarray(B[ytr == c].sum(0)).ravel()
            palavras[c] = vocab[np.argsort(-(dentro / freq) * np.log1p(dentro))[:k]]
        hits = np.stack([np.asarray(Bte[:, [col[w] for w in palavras[c]]].sum(1)).ravel() for c in classes], 1)
        decide = (hits.max(1) > 0) & ((hits == hits.max(1, keepdims=True)).sum(1) == 1)
        prev = np.array(classes)[hits.argmax(1)]
        regras[f"K{k}"] = {"cobertura": round(float(decide.mean()), 4),
                           "acuracia": round(float((prev[decide] == yt[decide]).mean()), 4)}
        # Exigir margem (a classe vencedora com N palavras a mais que a 2ª) troca cobertura por acerto.
        s2 = np.sort(hits, 1)
        for mg in (2, 3):
            ok = (s2[:, -1] - s2[:, -2]) >= mg
            regras.setdefault("com_margem", []).append({"palavras": k, "margem": mg, "cobertura": round(float(ok.mean()), 4),
                                                        "acuracia": round(float((prev[ok] == yt[ok]).mean()), 4)})
        if k == 10:
            regras["palavras_K10"] = {c: list(palavras[c]) for c in classes}

    # B2. Modelo supervisionado com limiar (mesmo da Entrega 1).
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, max_features=200_000)
    Vtr = vec.fit_transform(X_tr)
    clf = LogisticRegression(max_iter=2000, C=5).fit(Vtr, y_tr)
    t0 = time.perf_counter()
    Vte = vec.transform(X_te)
    P = clf.predict_proba(Vte)
    ms_por_ticket = (time.perf_counter() - t0) / len(X_te) * 1000
    prev, conf = clf.classes_[P.argmax(1)], P.max(1)
    auto = conf >= LIMIAR_IA
    curva = pd.DataFrame([{"limiar": t, "cobertura": (conf >= t).mean(), "acuracia": (prev == yt)[conf >= t].mean()}
                          for t in np.round(np.arange(0.30, 0.99, 0.01), 2)])

    erros_auto = pd.crosstab(pd.Series(yt[auto & (prev != yt)], name="real"),
                             pd.Series(prev[auto & (prev != yt)], name="previsto"))
    adm = yt == "Administrative rights"
    Xa = X_te.to_numpy()
    exemplos_adm = [{"texto": Xa[i][:140], "previsto": prev[i], "confianca": round(float(conf[i]), 2)}
                    for i in np.where(adm & ~auto)[0][:5]]

    # B3. Duplicatas: ticket novo (teste) × histórico (treino), similaridade de cosseno.
    ytr_arr = ytr
    melhor, rotulo = np.zeros(Vte.shape[0]), np.empty(Vte.shape[0], dtype=object)
    for i in range(0, Vte.shape[0], 2000):
        S = (Vte[i:i + 2000] @ Vtr.T).toarray()
        melhor[i:i + 2000], rotulo[i:i + 2000] = S.max(1), ytr_arr[S.argmax(1)]
    dup = {str(t): {"pct_com_quase_duplicata": round(float((melhor >= t).mean()), 4),
                    "mesma_classe_da_duplicata": round(float((rotulo[melhor >= t] == yt[melhor >= t]).mean()), 4)}
           for t in (0.8, 0.9, 0.95)}

    # B4. Alertas de máquina: o mesmo alerta de monitoramento, espalhado em filas.
    alerta = d["Document"].str.contains("critical alert")
    # B5. Temas sensíveis em HR Support (dado pessoal/trabalhista).
    hr = d.loc[d["Topic_group"] == "HR Support", "Document"]
    sensiveis = {w: int(hr.str.contains(rf"\b{w}", regex=True).sum())
                 for w in ("salary", "payroll", "termination", "resign", "sick", "maternity")}

    _grafico_regras_vs_modelo(curva, regras, auto.mean(), (prev == yt)[auto].mean())
    return {
        "n_teste": int(len(yt)),
        "regras_melhor_caso": regras,
        "modelo": {"limiar": LIMIAR_IA, "cobertura": round(float(auto.mean()), 4),
                   "acuracia": round(float((prev == yt)[auto].mean()), 4),
                   "ms_por_ticket": round(ms_por_ticket, 3),
                   "acuracia_na_mesma_cobertura_das_regras_K10": round(float(
                       (prev == yt)[conf >= np.quantile(conf, 1 - regras["K10"]["cobertura"])].mean()), 4)},
        "erros_do_modelo_acima_do_limiar": int((auto & (prev != yt)).sum()),
        "para_onde_vao_os_erros": {f"{r} → {p}": int(n) for (r, p), n in
                                   erros_auto.stack().loc[lambda s: s > 0].sort_values(ascending=False).head(6).items()},
        "administrative_rights": {"pct_automatico": round(float(auto[adm].mean()), 4),
                                  "acuracia_automatico": round(float((prev == yt)[adm & auto].mean()), 4),
                                  "exemplos_abaixo_do_limiar": exemplos_adm},
        "duplicatas": dup,
        "alertas_de_maquina": {"tickets": int(alerta.sum()),
                               "classes_diferentes": int(d.loc[alerta, "Topic_group"].nunique()),
                               "por_classe": d.loc[alerta, "Topic_group"].value_counts().to_dict()},
        "hr_temas_sensiveis": sensiveis,
    }


def _estilo(ax, fig):
    fig.patch.set_facecolor("#fcfcfb"); ax.set_facecolor("#fcfcfb")
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.grid(color="#e6e5e0", linewidth=0.8); ax.set_axisbelow(True)
    ax.tick_params(colors="#52514e", labelsize=9, length=0)


def _grafico_regras_vs_modelo(curva, regras, cob, acc):
    fig, ax = plt.subplots(figsize=(8, 4))
    _estilo(ax, fig)
    ax.plot(curva["cobertura"], curva["acuracia"], color="#2a78d6", linewidth=2, label="modelo supervisionado (probabilístico)")
    for k, dy in (("K5", -16), ("K10", 10), ("K20", -16)):
        ax.scatter(regras[k]["cobertura"], regras[k]["acuracia"], color="#eb6834", s=55, zorder=3)
        ax.annotate(f"{k[1:]} palavras/classe", (regras[k]["cobertura"], regras[k]["acuracia"]),
                    xytext=(-30, dy), textcoords="offset points", fontsize=8, color="#52514e")
    ax.scatter([], [], color="#eb6834", s=55, label="regras de palavra-chave (determinístico)")
    for r in regras["com_margem"]:
        ax.scatter(r["cobertura"], r["acuracia"], facecolor="none", edgecolor="#eb6834", s=55, zorder=3)
    ax.scatter([], [], facecolor="none", edgecolor="#eb6834", s=55, label="regras exigindo margem de 2–3 palavras")
    a95 = [r["cobertura"] for r in regras["com_margem"] if r["acuracia"] >= 0.95]
    melhor_regra = max(a95) if a95 else 0.0
    ax.scatter([cob], [acc], color="#2a78d6", s=70, zorder=3, edgecolor="#0b0b0b")
    ax.annotate(f"limiar {LIMIAR_IA}: {cob:.0%} com {acc:.1%}".replace(".", ","), (cob, acc),
                xytext=(-200, -40), textcoords="offset points", fontsize=9, color="#0b0b0b")
    ax.set_xlim(0, 1.02); ax.set_ylim(0.6, 1.0)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.set_xlabel("% dos tickets que o método classifica sozinho", fontsize=9, color="#52514e")
    ax.set_ylabel("acerto nesses tickets", fontsize=9, color="#52514e")
    ax.set_title(f"Para acertar 95%, regras cobrem até {melhor_regra:.0%} dos tickets; o modelo, {cob:.0%}", loc="left",
                 fontsize=12, fontweight="bold", color="#0b0b0b", pad=20)
    ax.text(0, 1.03, "Dataset 2, 9.568 tickets de teste. Regras no melhor caso: palavras escolhidas olhando o treino",
            transform=ax.transAxes, fontsize=9, color="#52514e")
    ax.legend(loc="lower left", fontsize=8, frameon=False)
    fig.tight_layout(); fig.savefig(OUT / "07_regras_vs_modelo.png", dpi=160); plt.close(fig)


# ---------------------------------------------------------------------------
def parte_c(a: dict) -> dict:
    """Custo anual de LLM por caso de uso. Só entram os usos onde a proposta usa LLM."""
    pct = a["rotas_pct"]
    t_ticket = a["texto_medio_tokens"]
    usos = {
        # (tickets/ano, modelo, tokens fixos cacheáveis, tokens variáveis, tokens de saída)
        "Resposta sugerida (rota 2)": (TICKETS_ANO * pct[ROTA_COPILOTO], "sonnet-5", 3000, t_ticket + 1500, 350),
        "Dossiê para o humano (rota 1)": (TICKETS_ANO * pct[ROTA_HUMANO], "haiku-4.5", 1000, t_ticket + 500, 250),
        "Gold set: rotular 3.000 tickets (uma vez)": (3000, "sonnet-5", 2000, t_ticket, 60),
    }

    def custo(n, modelo, fixo, var, saida, mult=1.0):
        pin, pout = PRECO[modelo]
        entrada = (fixo * CACHE_LEITURA + var) * mult * pin
        return n * (entrada + saida * mult * pout) / 1e6

    linhas = {k: {"tickets": round(v[0]), "modelo": v[1], "usd_ano": round(custo(*v), 2),
                  "usd_ano_tokens_x10": round(custo(*v, mult=10), 2)} for k, v in usos.items()}
    total = sum(r["usd_ano"] for r in linhas.values())
    total10 = sum(r["usd_ano_tokens_x10"] for r in linhas.values())
    return {"por_uso": linhas, "usd_ano": round(total, 2), "rs_ano": round(total * USD_BRL),
            "rs_ano_tokens_x10": round(total10 * USD_BRL),
            "equivale_a_horas_de_agente": round(total * USD_BRL / CUSTO_HORA_RS, 1),
            "premissas": {"usd_brl": USD_BRL, "precos_usd_por_1M": PRECO, "cache_leitura": CACHE_LEITURA}}


# ---------------------------------------------------------------------------
def parte_d(a: dict) -> dict:
    """Impacto (h/ano) × esforço (semanas-pessoa, premissa) de cada automação."""
    desp = json.loads((DIAG / "resultados.json").read_text(encoding="utf-8"))["etapa3_desperdicio"]
    h = {k.split(" ")[0]: v for k, v in desp["cenarios"]["base"]["horas"].items()}
    triagem = json.loads((DIAG / "triagem_ia.json").read_text(encoding="utf-8"))["B_roi_retriagem"]
    generico = a["generico_pct"]
    toque = {k: round(TICKETS_ANO * generico * m / 60) for k, m in PRIMEIRO_TOQUE_MIN.items()}
    itens = [
        # nome, tipo, h/ano, esforço (semanas), dependência
        ("Política de pendentes (lembretes D+2/D+5, fecha D+7)", "Determinístico", h["Cobrança"], 1, "nenhuma"),
        ("Resposta de recebimento que pede os dados que faltam", "Determinístico", toque["base"], 1, "nenhuma"),
        ("Prioridade por sinais de risco + SLA na fila", "Determinístico", None, 2, "nenhuma"),
        ("Classificação + roteamento com limiar", "ML supervisionado", triagem["horas_liquidas_recuperadas"], 6,
         "gold set (LLM + validação humana)"),
        ("Duplicata / recontato (customer_id + similaridade)", "Determinístico + similaridade", h["Recontato"] * 0.5, 3,
         "customer_id do CRM (P8)"),
        ("Resposta sugerida ao agente (copiloto)", "LLM + base de conhecimento", h["L1"], 8,
         "base de conhecimento curada (P7)"),
    ]
    tabela = [{"automacao": n, "tipo": t, "horas_ano": (round(x) if x is not None else None),
               "rs_ano": (round(x * CUSTO_HORA_RS) if x is not None else None),
               "esforco_semanas": e, "depende_de": dep} for n, t, x, e, dep in itens]
    _grafico_impacto_esforco(tabela)
    return {"itens": tabela, "primeiro_toque_faixa_h": toque,
            "total_horas_base": round(sum(r["horas_ano"] or 0 for r in tabela)),
            "nota": "Prioridade por sinais não tem horas próprias: o ganho é de risco (Critical sem resposta), não de tempo."}


def _grafico_impacto_esforco(tabela):
    fig, ax = plt.subplots(figsize=(8, 4.4))
    _estilo(ax, fig)
    cores = {"Determinístico": "#2a78d6", "ML supervisionado": "#7c4dcc", "LLM + base de conhecimento": "#eb6834",
             "Determinístico + similaridade": "#1f9e89"}
    curtos = [("Pendentes", (12, -16)), ("Recebimento + coleta", (12, 6)), ("Prioridade + SLA", (12, -4)),
              ("Classificação + roteamento", (-60, 14)), ("Duplicata / recontato", (12, -4)),
              ("Copiloto de resposta", (-40, 14))]
    for r, (nome, off) in zip(tabela, curtos):
        y = r["horas_ano"] if r["horas_ano"] is not None else 150
        ax.scatter(r["esforco_semanas"], y, s=200, color=cores[r["tipo"]], alpha=0.85,
                   marker="o" if r["horas_ano"] is not None else "D", edgecolor="#0b0b0b", linewidth=0.6)
        ax.annotate(nome, (r["esforco_semanas"], y), xytext=off, textcoords="offset points",
                    fontsize=8, color="#0b0b0b")
    for tipo, c in cores.items():
        ax.scatter([], [], color=c, s=60, label=tipo)
    ax.legend(loc="center right", fontsize=8, frameon=False)
    fixo = sum(r["horas_ano"] for r in tabela if r["tipo"] == "Determinístico" and r["horas_ano"])
    total = sum(r["horas_ano"] or 0 for r in tabela)
    ax.set_xlim(0, 10); ax.set_ylim(0, 1600)
    ax.set_xlabel("esforço (semanas-pessoa, premissa)", fontsize=9, color="#52514e")
    ax.set_ylabel("horas de agente devolvidas por ano", fontsize=9, color="#52514e")
    ax.set_title(f"Regras fixas: {fixo / total:.0%} do ganho com 2 semanas de esforço", loc="left",
                 fontsize=12, fontweight="bold", color="#0b0b0b", pad=20)
    ax.text(0, 1.03, "Horas: cenário base da Entrega 1. ◆ = ganho de risco, sem horas próprias",
            transform=ax.transAxes, fontsize=9, color="#52514e")
    fig.tight_layout(); fig.savefig(OUT / "09_impacto_esforco.png", dpi=160); plt.close(fig)


def grafico_rotas(a: dict, f: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 3.2))
    _estilo(ax, fig)
    rotas = [ROTA_HUMANO, ROTA_COPILOTO, ROTA_AUTO]
    cores = ["#eb6834", "#7c4dcc", "#2a78d6"]
    esq = 0.0
    for r, c in zip(rotas, cores):
        p = a["rotas_pct"][r]
        ax.barh([0], [p], left=esq, color=c, height=0.5)
        ax.text(esq + p / 2, 0, f"{p:.0%}", ha="center", va="center", color="white", fontsize=12, fontweight="bold")
        rotulo = r.split(" ", 1)[1].replace(", ", ",\n").replace(" (", "\n(")
        ax.text(esq + p / 2, -0.35, rotulo, ha="center", va="top", fontsize=8.5, color="#0b0b0b")
        esq += p
    ax.set_xlim(0, 1); ax.set_ylim(-0.7, 0.55); ax.axis("off")
    ax.set_title("Um terço vai direto para humano; a IA não decide sozinha nada de risco", loc="left",
                 fontsize=12, fontweight="bold", color="#0b0b0b")
    ax.text(0, 0.42, "Dataset 1, 8.469 tickets. A rota 3 automatiza a coleta de dados, não a solução.",
            fontsize=9, color="#52514e")
    fig.tight_layout(); fig.savefig(OUT / "08_rotas.png", dpi=160); plt.close(fig)


# ---------------------------------------------------------------------------
def verificacoes(a: dict, b: dict, c: dict, d: dict, f: pd.DataFrame) -> dict:
    v = {}
    v["V1_particao"] = {"ok": bool(f["rota"].notna().all() and sum(a["rotas"].values()) == a["tickets"]),
                        "leitura": "cada ticket tem exatamente uma rota"}
    risco = f[RISCO].any(axis=1)
    v["V2_risco_nunca_automatico"] = {"ok": bool((f.loc[risco, "rota"] == ROTA_HUMANO).all()),
                                      "tickets_com_risco": int(risco.sum()),
                                      "leitura": "todo ticket com sinal de risco cai na rota 1"}
    k10, m = b["regras_melhor_caso"]["K10"], b["modelo"]
    v["V3_regras_vs_modelo_mesma_cobertura"] = {
        "ok": m["acuracia_na_mesma_cobertura_das_regras_K10"] > k10["acuracia"],
        "regras": k10, "modelo_na_mesma_cobertura": m["acuracia_na_mesma_cobertura_das_regras_K10"],
        "leitura": "comparação justa: mesma fatia de tickets decidida sozinha"}
    v["V4_duplicata_estavel"] = {"ok": all(x["mesma_classe_da_duplicata"] >= 0.9 for x in b["duplicatas"].values()),
                                 "leitura": "a classe da quase-duplicata acerta >= 90% em todos os limiares"}
    valor_llm = next(r["rs_ano"] for r in d["itens"] if r["tipo"].startswith("LLM"))
    v["V5_custo_llm_menor_que_o_ganho"] = {
        "ok": c["rs_ano_tokens_x10"] < valor_llm, "rs_ano": c["rs_ano"], "rs_ano_tokens_x10": c["rs_ano_tokens_x10"],
        "valor_das_horas_do_copiloto_rs": valor_llm,
        "pct_do_ganho": round(c["rs_ano"] / valor_llm, 3), "pct_do_ganho_tokens_x10": round(c["rs_ano_tokens_x10"] / valor_llm, 3),
        "leitura": "mesmo com 10x os tokens estimados, a LLM custa menos que as horas que o copiloto devolve"}
    return v


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=HERE.parent / "data" / "support_tickets.csv")
    ap.add_argument("--data2", type=Path, default=HERE.parent / "data" / "it_tickets.csv")
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    a, f = parte_a(args.data)
    b = parte_b(args.data2)
    c = parte_c(a)
    d = parte_d(a)
    grafico_rotas(a, f)
    v = verificacoes(a, b, c, d, f)
    r = {"A_rotas_dataset1": a, "B_classificacao_dataset2": b, "C_custo_llm": c, "D_impacto_esforco": d,
         "V_verificacoes": v}
    (OUT / "automacao.json").write_text(json.dumps(r, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps(r, ensure_ascii=False, indent=2, default=str))
    falhas = [k for k, x in v.items() if not x["ok"]]
    print("\nVerificações:", "todas OK" if not falhas else f"FALHARAM {falhas}")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
