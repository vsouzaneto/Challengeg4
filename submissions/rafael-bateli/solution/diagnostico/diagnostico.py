"""Diagnóstico operacional — Challenge 002 (Dataset 1: Customer Support Tickets).

Responde às três perguntas do Diretor de Operações:
  1. Onde o fluxo trava?
  2. O que impacta a satisfação (CSAT)?
  3. Quanto estamos desperdiçando?

Antes de responder, audita a integridade do dado. Tudo o que o dado não sustenta
é reportado como falha de captura, e não como achado.

Uso:
    python diagnostico.py                      # lê ../data/support_tickets.csv
    python diagnostico.py --data caminho.csv   # outro caminho

Saídas em ./outputs: resultados.json, tabelas .csv e gráficos .png.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
SEED = 42

# ---------------------------------------------------------------------------
# Premissas do modelo de desperdício. NÃO vêm do dataset — são parâmetros de
# trabalho, explícitos para serem trocados pelos números reais da operação.
# Cada uma tem cenário baixo / base / alto.
# ---------------------------------------------------------------------------
PREMISSAS = {
    "tickets_ano": 30_000,  # volume anual informado pelo Diretor (contexto do desafio)
    "aht_min": {"baixo": 8, "base": 12, "alto": 18},  # tempo médio de atendimento por contato
    "retriagem_min": {"baixo": 3, "base": 5, "alto": 10},  # reclassificar + transferir 1 ticket
    "contatos_extras_repeticao": {"baixo": 1, "base": 2, "alto": 3},  # por ticket que diz "já contatei várias vezes"
    "followup_min_pendente": {"baixo": 2, "base": 4, "alto": 8},  # cobrar o cliente em ticket pendente
    "deflexao_l1": {"baixo": 0.20, "base": 0.40, "alto": 0.60},  # fração do L1 repetitivo resolvível sem agente
    "custo_hora_rs": {"baixo": 25, "base": 35, "alto": 55},  # custo carregado de 1h de agente (R$)
}

# Assunto -> tipos coerentes. Mapa "generoso": aceita toda leitura plausível,
# para que a taxa de incoerência seja um piso, não um teto.
COERENCIA_GENEROSA = {
    "Refund request": {"Refund request"},
    "Cancellation request": {"Cancellation request"},
    "Payment issue": {"Billing inquiry", "Refund request"},
    "Product recommendation": {"Product inquiry"},
    "Delivery problem": {"Product inquiry", "Refund request", "Cancellation request"},
    "Account access": {"Technical issue", "Billing inquiry"},
    "Product compatibility": {"Technical issue", "Product inquiry"},
    "Peripheral compatibility": {"Technical issue", "Product inquiry"},
    "Installation support": {"Technical issue", "Product inquiry"},
    "Product setup": {"Technical issue", "Product inquiry"},
    "Hardware issue": {"Technical issue", "Refund request"},
    "Display issue": {"Technical issue", "Refund request"},
    "Battery life": {"Technical issue", "Refund request"},
    "Software bug": {"Technical issue"},
    "Network problem": {"Technical issue"},
    "Data loss": {"Technical issue"},
}
# Mapa "estrito": um assunto, um tipo natural.
COERENCIA_ESTRITA = {
    s: ({"Technical issue"} if "Technical issue" in t else {sorted(t)[0]})
    for s, t in COERENCIA_GENEROSA.items()
}
COERENCIA_ESTRITA.update({
    "Payment issue": {"Billing inquiry"},
    "Delivery problem": {"Product inquiry"},
})

# Temas detectáveis no texto da descrição (para checar se o Subject bate).
TEMAS_DESCRICAO = {
    "Account access": r"account|log ?in|password|credential|locked",
    "Network problem": r"network|wi-?fi|internet|connect(?:ion)? ",
    "Data loss": r"data loss|deleted|files|recover",
    "Software bug": r"software bug|crash|glitch|freez",
    "Hardware issue": r"hardware|screen|noise|not turning on|flicker",
    "Battery life": r"battery",
    "Display issue": r"display|screen|flicker",
    "Payment issue": r"payment|charge|billing|refund|invoice",
}
ABERTURA_GENERICA = r"I'm having an issue with the \{product_purchased\}\. Please assist\."

SINAIS_TEXTO = {
    "contato_repetido": r"already contacted customer support|contacted .*multiple times",
    "l1_conta_senha": r"password|account is locked|Invalid Credentials|regain access|recover my account|unable to access my",
    "l1_passo_a_passo": r"guide me through the steps|What steps should I take|How can I (?:resolve|troubleshoot|fix)",
}

# Paleta de referência (dataviz skill, modo claro).
AZUL, LARANJA, CINZA, TEXTO, TEXTO_2, SUPERFICIE = (
    "#2a78d6", "#eb6834", "#b8b7b0", "#0b0b0b", "#52514e", "#fcfcfb")


def carregar(caminho: Path) -> pd.DataFrame:
    df = pd.read_csv(caminho)
    df["frt_ts"] = pd.to_datetime(df["First Response Time"])
    df["ttr_ts"] = pd.to_datetime(df["Time to Resolution"])
    df["delta_h"] = (df["ttr_ts"] - df["frt_ts"]).dt.total_seconds() / 3600
    df["delta_mod24_h"] = df["delta_h"] % 24
    df["csat"] = df["Customer Satisfaction Rating"]
    for nome, padrao in SINAIS_TEXTO.items():
        df[nome] = df["Ticket Description"].str.contains(padrao, case=False, regex=True)
    df["l1_repetitivo"] = df["l1_conta_senha"] | df["l1_passo_a_passo"]
    return df


# ---------------------------------------------------------------------------
# Etapa 0 — integridade do dado
# ---------------------------------------------------------------------------
def auditar(df: pd.DataFrame, caminho: Path) -> dict:
    linhas_fisicas = sum(1 for _ in open(caminho, encoding="utf-8")) - 1
    fechados = df[df["Ticket Status"] == "Closed"]
    desc = df["Ticket Description"]
    outros_placeholders = (
        desc.str.findall(r"\{[a-z_]+\}").explode().dropna()
        .loc[lambda s: s != "{product_purchased}"]
    )
    ts = pd.concat([df["frt_ts"], df["ttr_ts"]]).dropna()
    ks = stats.kstest(fechados["delta_mod24_h"] / 24, "uniform")
    csat_uniforme = stats.chisquare(fechados["csat"].value_counts().sort_index().values)

    # O Subject bate com o texto da descrição?
    def temas(texto: str) -> list[str]:
        texto = re.sub(ABERTURA_GENERICA, "", texto)
        return [t for t, p in TEMAS_DESCRICAO.items() if re.search(p, texto, re.I)]

    df_t = df.assign(temas=desc.map(temas))
    df_t = df_t[(df_t["temas"].str.len() > 0) & df_t["Ticket Subject"].isin(TEMAS_DESCRICAO)]
    bate = df_t.apply(lambda r: r["Ticket Subject"] in r["temas"], axis=1)
    acaso = df_t["temas"].str.len().mean() / len(TEMAS_DESCRICAO)

    tipo_x_assunto = pd.crosstab(df["Ticket Subject"], df["Ticket Type"])
    tipo_x_assunto.to_csv(OUT / "tipo_x_assunto.csv")

    def incoerencia(mapa: dict) -> float:
        ok = df.apply(lambda r: r["Ticket Type"] in mapa[r["Ticket Subject"]], axis=1)
        return float(1 - ok.mean())

    return {
        "registros": len(df),
        "linhas_fisicas_csv": linhas_fisicas,
        "status": df["Ticket Status"].value_counts().to_dict(),
        "nulos": {
            "First Response Time": int(df["First Response Time"].isna().sum()),
            "Time to Resolution": int(df["Time to Resolution"].isna().sum()),
            "Customer Satisfaction Rating": int(df["csat"].isna().sum()),
            "Resolution": int(df["Resolution"].isna().sum()),
        },
        "tem_coluna_criacao_ticket": any(c.lower().startswith(("created", "date of ticket", "open")) for c in df.columns),
        "janela_timestamps": [str(ts.min()), str(ts.max())],
        "janela_horas": round((ts.max() - ts.min()).total_seconds() / 3600, 1),
        "fechados_resolucao_antes_da_1a_resposta": int((fechados["delta_h"] < 0).sum()),
        "fechados_total": len(fechados),
        "pct_resolucao_antes_da_1a_resposta": round(float((fechados["delta_h"] < 0).mean()), 4),
        "ks_delta_mod24_vs_uniforme_p": round(float(ks.pvalue), 4),
        "csat_cobertura": round(float(df["csat"].notna().mean()), 4),
        "csat_distribuicao": fechados["csat"].value_counts().sort_index().to_dict(),
        "csat_uniforme_chi2_p": round(float(csat_uniforme.pvalue), 4),
        "placeholder_product_purchased_pct": round(float(desc.str.contains(r"\{product_purchased\}").mean()), 4),
        "outros_placeholders_tickets": int(desc.str.contains(r"\{(?!product_purchased)[a-z_]+\}").sum()),
        "outros_placeholders_distintos": int(outros_placeholders.nunique()),
        "resolution_exemplos": fechados["Resolution"].sample(3, random_state=SEED).tolist(),
        "tipo_x_assunto_chi2_p": round(float(stats.chi2_contingency(tipo_x_assunto).pvalue), 4),
        "incoerencia_tipo_assunto_generosa": round(incoerencia(COERENCIA_GENEROSA), 4),
        "incoerencia_tipo_assunto_estrita": round(incoerencia(COERENCIA_ESTRITA), 4),
        "assunto_bate_descricao": round(float(bate.mean()), 4),
        "assunto_bate_descricao_acaso": round(float(acaso), 4),
        "assunto_bate_descricao_n": int(len(df_t)),
        "compra_ate_ticket_dias_min": int((df["frt_ts"] - pd.to_datetime(df["Date of Purchase"])).dt.days.min()),
        "emails_repetidos": int(df["Customer Email"].duplicated().sum()),
    }


# ---------------------------------------------------------------------------
# Etapa 1 — onde o fluxo trava
# ---------------------------------------------------------------------------
def teste_permutacao_combos(fechados: pd.DataFrame, coluna: str, n: int = 2000) -> dict:
    """A amplitude entre as 80 combinações canal×prioridade×tipo é maior que a do acaso?"""
    chaves = ["Ticket Channel", "Ticket Priority", "Ticket Type"]
    grupos = fechados.groupby(chaves).ngroup().to_numpy()
    valores = fechados[coluna].to_numpy()
    contagem = np.bincount(grupos)

    def amplitude(v: np.ndarray) -> float:
        medias = np.bincount(grupos, weights=v) / contagem
        return float(medias.max() - medias.min())

    rng = np.random.default_rng(SEED)
    observada = amplitude(valores)
    nula = np.array([amplitude(rng.permutation(valores)) for _ in range(n)])
    return {
        "amplitude_observada": round(observada, 3),
        "amplitude_nula_p50": round(float(np.median(nula)), 3),
        "amplitude_nula_p95": round(float(np.quantile(nula, 0.95)), 3),
        "p_valor": round(float((nula >= observada).mean()), 4),
        "_nula": nula,
    }


def gargalos(df: pd.DataFrame) -> dict:
    fechados = df[df["Ticket Status"] == "Closed"]
    dims = ["Ticket Channel", "Ticket Priority", "Ticket Type"]

    por_dim = {}
    for d in dims:
        status = pd.crosstab(df[d], df["Ticket Status"])
        grupos_t = [g["delta_mod24_h"].to_numpy() for _, g in fechados.groupby(d)]
        por_dim[d] = {
            "pct_open_sem_1a_resposta": (status["Open"] / status.sum(axis=1)).round(4).to_dict(),
            "status_chi2_p": round(float(stats.chi2_contingency(status).pvalue), 4),
            "tempo_proxy_mediana_h": fechados.groupby(d)["delta_mod24_h"].median().round(2).to_dict(),
            "tempo_proxy_kruskal_p": round(float(stats.kruskal(*grupos_t).pvalue), 4),
        }

    combos = (
        fechados.groupby(dims)
        .agg(n=("delta_mod24_h", "size"), tempo_medio_h=("delta_mod24_h", "mean"), csat_medio=("csat", "mean"))
        .round(2).sort_values("tempo_medio_h", ascending=False)
    )
    combos.to_csv(OUT / "combos_canal_prioridade_tipo.csv")
    perm = teste_permutacao_combos(fechados, "delta_mod24_h")

    status = df["Ticket Status"].value_counts(normalize=True).round(4).to_dict()
    return {
        "status_pct": status,
        "por_dimensao": por_dim,
        "combos_top5_proxy": combos.head(5).reset_index().to_dict("records"),
        "combos_n_min_max": [int(combos["n"].min()), int(combos["n"].max())],
        "permutacao_tempo": {k: v for k, v in perm.items() if not k.startswith("_")},
        "_nula": perm["_nula"],
    }


# ---------------------------------------------------------------------------
# Etapa 2 — o que impacta CSAT
# ---------------------------------------------------------------------------
def drivers_csat(df: pd.DataFrame) -> dict:
    f = df[df["Ticket Status"] == "Closed"].copy()
    cat = ["Ticket Channel", "Ticket Priority", "Ticket Type", "Ticket Subject",
           "Product Purchased", "Customer Gender"]
    num = ["Customer Age", "delta_mod24_h"]
    bools = ["contato_repetido", "l1_conta_senha", "l1_passo_a_passo"]

    univariado = {}
    for c in cat:
        grupos = [g["csat"].to_numpy() for _, g in f.groupby(c)]
        medias = f.groupby(c)["csat"].mean()
        univariado[c] = {"teste": "Kruskal-Wallis", "p": round(float(stats.kruskal(*grupos).pvalue), 4),
                         "amplitude_medias": round(float(medias.max() - medias.min()), 3)}
    for c in num:
        r = stats.spearmanr(f[c], f["csat"])
        univariado[c] = {"teste": "Spearman", "rho": round(float(r.statistic), 4), "p": round(float(r.pvalue), 4)}
    for c in bools:
        a, b = f.loc[f[c], "csat"], f.loc[~f[c], "csat"]
        univariado[c] = {"teste": "Mann-Whitney", "p": round(float(stats.mannwhitneyu(a, b).pvalue), 4),
                         "csat_com": round(float(a.mean()), 3), "csat_sem": round(float(b.mean()), 3), "n_com": int(len(a))}

    X = f[cat + num + bools].copy()
    X[bools] = X[bools].astype(int)
    prep = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), cat)], remainder="passthrough")
    y_cls = f["csat"].astype(int)
    rf_cls = make_pipeline(prep, RandomForestClassifier(n_estimators=300, min_samples_leaf=5, random_state=SEED, n_jobs=-1))
    rf_reg = make_pipeline(prep, RandomForestRegressor(n_estimators=300, min_samples_leaf=5, random_state=SEED, n_jobs=-1))
    acc = cross_val_score(rf_cls, X, y_cls, cv=5, scoring="accuracy")
    acc_base = cross_val_score(DummyClassifier(strategy="most_frequent"), X, y_cls, cv=5, scoring="accuracy")
    r2 = cross_val_score(rf_reg, X, f["csat"], cv=5, scoring="r2")
    r2_base = cross_val_score(DummyRegressor(), X, f["csat"], cv=5, scoring="r2")

    ic = {}
    for c in ["Ticket Channel", "Ticket Priority", "Ticket Type"]:
        g = f.groupby(c)["csat"].agg(["mean", "std", "count"])
        g["ic95"] = 1.96 * g["std"] / np.sqrt(g["count"])
        ic[c] = g[["mean", "ic95", "count"]].round(3)

    return {
        "n_com_csat": len(f),
        "csat_medio": round(float(f["csat"].mean()), 3),
        "univariado": univariado,
        "modelo_rf": {
            "acuracia_cv": round(float(acc.mean()), 4),
            "acuracia_baseline_classe_majoritaria": round(float(acc_base.mean()), 4),
            "acuracia_acaso_5_classes": 0.2,
            "r2_cv": round(float(r2.mean()), 4),
            "r2_baseline": round(float(r2_base.mean()), 4),
        },
        "_ic": ic,
    }


# ---------------------------------------------------------------------------
# Etapa 3 — desperdício
# ---------------------------------------------------------------------------
def desperdicio(df: pd.DataFrame, auditoria: dict) -> dict:
    n = PREMISSAS["tickets_ano"]
    taxas = {
        "incoerencia_classificacao": auditoria["incoerencia_tipo_assunto_generosa"],
        "contato_repetido": float(df["contato_repetido"].mean()),
        "pendente_cliente": float((df["Ticket Status"] == "Pending Customer Response").mean()),
        "l1_repetitivo": float(df["l1_repetitivo"].mean()),
        "open_sem_resposta": float((df["Ticket Status"] == "Open").mean()),
    }

    cenarios = {}
    for c in ["baixo", "base", "alto"]:
        p = {k: (v[c] if isinstance(v, dict) else v) for k, v in PREMISSAS.items()}
        horas = {
            "Retriagem por classificação errada": n * taxas["incoerencia_classificacao"] * p["retriagem_min"] / 60,
            "Recontato (cliente volta a pedir)": n * taxas["contato_repetido"] * p["contatos_extras_repeticao"] * p["aht_min"] / 60,
            "Cobrança de pendentes do cliente": n * taxas["pendente_cliente"] * p["followup_min_pendente"] / 60,
            "L1 repetitivo feito por humano": n * taxas["l1_repetitivo"] * p["deflexao_l1"] * p["aht_min"] / 60,
        }
        total = sum(horas.values())
        cenarios[c] = {
            "horas": {k: round(v) for k, v in horas.items()},
            "horas_total": round(total),
            "custo_total_rs": round(total * p["custo_hora_rs"]),
            "fte_equivalente": round(total / (8 * 21 * 12), 2),
            # Não é desperdício, é capacidade em falta: atender quem nunca foi respondido.
            "divida_capacidade_open_h": round(n * taxas["open_sem_resposta"] * p["aht_min"] / 60),
        }
    return {"taxas_observadas": {k: round(v, 4) for k, v in taxas.items()},
            "premissas": PREMISSAS, "cenarios": cenarios}


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------
def _estilo(ax, titulo: str, subtitulo: str | None = None):
    ax.set_facecolor(SUPERFICIE)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(CINZA)
    ax.tick_params(colors=TEXTO_2, labelsize=9, length=0)
    ax.grid(axis="x", color="#e6e5e0", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_title(titulo, loc="left", fontsize=12, color=TEXTO, fontweight="bold", pad=22 if subtitulo else 8)
    if subtitulo:
        ax.text(0, 1.02, subtitulo, transform=ax.transAxes, fontsize=9, color=TEXTO_2)


def graficos(df: pd.DataFrame, g: dict, c: dict, w: dict) -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": SUPERFICIE})
    fechados = df[df["Ticket Status"] == "Closed"]

    # 1. Resolução antes da primeira resposta
    fig, ax = plt.subplots(figsize=(8, 3.6))
    bins = np.arange(-24, 25, 2)
    neg = fechados["delta_h"][fechados["delta_h"] < 0]
    pos = fechados["delta_h"][fechados["delta_h"] >= 0]
    ax.hist(neg, bins=bins, color=LARANJA, edgecolor=SUPERFICIE, linewidth=2,
            label=f"Impossível: resolvido antes de responder ({len(neg):,})".replace(",", "."))
    ax.hist(pos, bins=bins, color=AZUL, edgecolor=SUPERFICIE, linewidth=2,
            label=f"Plausível ({len(pos):,})".replace(",", "."))
    ax.axvline(0, color=TEXTO, linewidth=1)
    ax.set_ylim(0, ax.get_ylim()[1] * 1.25)
    ax.grid(axis="x", visible=False); ax.grid(axis="y", color="#e6e5e0")
    ax.set_xlabel("Time to Resolution − First Response Time (horas)", color=TEXTO_2, fontsize=9)
    ax.set_ylabel("tickets fechados", color=TEXTO_2, fontsize=9)
    ax.legend(frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(0, 1.0))
    _estilo(ax, "49% dos tickets fechados foram 'resolvidos' antes da 1ª resposta",
            "Os campos de tempo são horários soltos, não durações — e não existe horário de abertura do ticket")
    ax.grid(axis="x", visible=False)
    fig.tight_layout(); fig.savefig(OUT / "01_tempo_negativo.png", dpi=160); plt.close(fig)

    # 2. Amplitude das combinações vs acaso
    fig, ax = plt.subplots(figsize=(8, 3.6))
    nula = g["_nula"]; obs = g["permutacao_tempo"]["amplitude_observada"]
    ax.hist(nula, bins=40, color=CINZA, edgecolor=SUPERFICIE, linewidth=1)
    ax.axvline(obs, color=LARANJA, linewidth=2)
    rotulo = f"  observado: {obs:.1f} h\n  p = {g['permutacao_tempo']['p_valor']:.2f}".replace(".", ",")
    ax.text(obs, ax.get_ylim()[1] * 0.92, rotulo, color=TEXTO, fontsize=9, va="top")
    ax.set_xlabel("Diferença entre a pior e a melhor combinação canal × prioridade × tipo (horas)", color=TEXTO_2, fontsize=9)
    ax.set_ylabel("simulações (rótulos embaralhados)", color=TEXTO_2, fontsize=9)
    ax.grid(axis="x", visible=False); ax.grid(axis="y", color="#e6e5e0")
    _estilo(ax, "O 'pior gargalo' é do tamanho que o acaso produz",
            "2.000 embaralhamentos aleatórios: a amplitude real fica no meio da distribuição do acaso")
    ax.grid(axis="x", visible=False)
    fig.tight_layout(); fig.savefig(OUT / "02_combos_vs_acaso.png", dpi=160); plt.close(fig)

    # 3. Status: onde o ticket está parado, por prioridade
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ordem = ["Critical", "High", "Medium", "Low"]
    ct = pd.crosstab(df["Ticket Priority"], df["Ticket Status"], normalize="index").loc[ordem[::-1]]
    esquerda = np.zeros(len(ct))
    cores = {"Open": LARANJA, "Pending Customer Response": "#eda100", "Closed": AZUL}
    nomes = {"Open": "Aberto sem 1ª resposta", "Pending Customer Response": "Aguardando cliente", "Closed": "Fechado"}
    for s in ["Open", "Pending Customer Response", "Closed"]:
        ax.barh(ct.index, ct[s], left=esquerda, color=cores[s], edgecolor=SUPERFICIE, linewidth=2, height=0.6, label=nomes[s])
        for i, v in enumerate(ct[s]):
            ax.text(esquerda[i] + v / 2, i, f"{v:.0%}", ha="center", va="center", fontsize=9,
                    color=TEXTO if s == "Pending Customer Response" else "white")
        esquerda += ct[s].to_numpy()
    ax.set_xlim(0, 1); ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.legend(frameon=False, fontsize=9, ncol=3, loc="lower left", bbox_to_anchor=(0, -0.32))
    _estilo(ax, "Ticket Critical fica parado na mesma proporção que Low",
            "2 em cada 3 tickets não estão fechados; a prioridade não muda o destino do ticket")
    fig.tight_layout(); fig.savefig(OUT / "03_status_por_prioridade.png", dpi=160); plt.close(fig)

    # 4. CSAT por dimensão com IC 95%
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.4), sharex=True)
    rotulos = {"Ticket Channel": "Canal", "Ticket Priority": "Prioridade", "Ticket Type": "Tipo"}
    for ax, (dim, tab) in zip(axes, c["_ic"].items()):
        tab = tab.sort_values("mean")
        y = np.arange(len(tab))
        ax.errorbar(tab["mean"], y, xerr=tab["ic95"], fmt="o", color=AZUL, ecolor=CINZA, elinewidth=2, capsize=0, markersize=7)
        ax.axvline(c["csat_medio"], color=TEXTO_2, linewidth=1, linestyle=":")
        ax.set_yticks(y, tab.index)
        ax.set_xlim(2.6, 3.4)
        _estilo(ax, rotulos[dim])
        ax.set_title(f"{rotulos[dim]}  (p = {c['univariado'][dim]['p']:.2f})", loc="left", fontsize=10, color=TEXTO)
    fig.suptitle("CSAT médio com IC 95%: todos os intervalos se cruzam na média geral (3,0)",
                 x=0.01, ha="left", fontsize=12, fontweight="bold", color=TEXTO)
    fig.tight_layout(); fig.savefig(OUT / "04_csat_por_dimensao.png", dpi=160); plt.close(fig)

    # 5. Desperdício (cenário base, faixa baixo–alto)
    fig, ax = plt.subplots(figsize=(8, 3.4))
    base = w["cenarios"]["base"]["horas"]; baixo = w["cenarios"]["baixo"]["horas"]; alto = w["cenarios"]["alto"]["horas"]
    itens = sorted(base, key=base.get)
    vals = [base[i] for i in itens]
    ax.barh(itens, vals, color=AZUL, height=0.55, edgecolor=SUPERFICIE, linewidth=2)
    ax.hlines(range(len(itens)), [baixo[i] for i in itens], [alto[i] for i in itens], color=TEXTO_2, linewidth=1.5)
    for i, it in enumerate(itens):
        ax.text(alto[it], i, f"  {base[it]:,.0f} h  ({baixo[it]:,.0f}–{alto[it]:,.0f})".replace(",", "."),
                va="center", fontsize=9, color=TEXTO)
    ax.set_xlim(0, max(alto.values()) * 1.45)
    ax.set_xlabel("horas de agente por ano (cenário base; traço = faixa baixo–alto)", color=TEXTO_2, fontsize=9)
    _estilo(ax, f"≈ {w['cenarios']['base']['horas_total']:,.0f} h/ano recuperáveis no cenário base".replace(",", "."),
            "Taxas medidas no dataset × premissas explícitas (trocáveis no topo do script)")
    fig.tight_layout(); fig.savefig(OUT / "05_desperdicio_horas.png", dpi=160); plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=HERE.parent / "data" / "support_tickets.csv")
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)

    sys.stdout.reconfigure(encoding="utf-8")
    df = carregar(args.data)
    auditoria = auditar(df, args.data)
    g = gargalos(df)
    c = drivers_csat(df)
    w = desperdicio(df, auditoria)
    graficos(df, g, c, w)

    resultado = {
        "etapa0_integridade": auditoria,
        "etapa1_gargalos": {k: v for k, v in g.items() if not k.startswith("_")},
        "etapa2_csat": {k: v for k, v in c.items() if not k.startswith("_")},
        "etapa3_desperdicio": w,
    }
    (OUT / "resultados.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps(resultado, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
