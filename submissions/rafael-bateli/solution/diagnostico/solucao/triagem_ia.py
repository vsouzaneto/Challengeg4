"""Triagem por IA — prova de viabilidade + contorno imediato do backlog.

A) Dataset 2 (48 mil tickets reais rotulados): classificador de texto com política
   de confiança. O limiar é escolhido na VALIDAÇÃO (acurácia ≥ 95%) e medido no
   TESTE, que o modelo nunca viu. Acima do limiar, a IA decide; abaixo, vai para humano.
B) ROI: recalcula a retriagem recuperável com a cobertura e a acurácia MEDIDAS.
C) Dataset 1: os rótulos atuais são aleatórios (harness H5), então não servem para
   treinar nada. Até existir o modelo, o backlog de tickets sem resposta é
   repriorizado por regras transparentes sobre o texto.

Uso:
    python triagem_ia.py --data ../../data/support_tickets.csv --data2 ../../data/it_tickets.csv
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
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "outputs"
SEED = 42
ACURACIA_ALVO = 0.95

# Premissas do ROI (mesmas do diagnóstico, mais duas da operação com IA).
TICKETS_ANO, RETRIAGEM_MIN, CUSTO_HORA = 30_000, 5, 35
INCOERENCIA_HOJE = 0.654          # medida no diagnóstico (mapa generoso)
ACURACIA_HUMANO_REVISANDO = 0.90  # premissa: humano revisando com sugestão da IA
REVISAO_MIN = 1.0                 # premissa: minutos para revisar 1 sugestão

SINAIS = {
    "perda_de_dados": (r"data loss|deleted|disappeared|lost (?:all|my)|recover", 3),
    "acesso_bloqueado": (r"account is locked|unable to access|regain access|Invalid Credentials|password reset option is not working", 3),
    "nao_liga": (r"not turning on|doesn't respond", 3),
    "cobranca": (r"charged|payment|billing|invoice|refund", 2),
    "falha_software": (r"software bug|crash|glitch|freez", 2),
    "rede": (r"network|wi-?fi|internet connection|disconnect", 2),
    "hardware_tela": (r"hardware|screen|flicker|noise|display", 2),
    "bateria": (r"battery", 1),
    "duvida_uso": (r"guide me through|what steps should i take|how can i|recommend", 1),
}
URGENCIA = r"as soon as possible|affecting my work|urgent|immediately"
RECONTATO = r"already contacted customer support|contacted .*multiple times"
PESO_PRIORIDADE = {"Critical": 3, "High": 2, "Medium": 1, "Low": 0}


# ---------------------------------------------------------------------------
def parte_a(caminho2: Path) -> dict:
    d = pd.read_csv(caminho2)
    X_tmp, X_te, y_tmp, y_te = train_test_split(d["Document"], d["Topic_group"], test_size=0.2,
                                                random_state=SEED, stratify=d["Topic_group"])
    X_tr, X_va, y_tr, y_va = train_test_split(X_tmp, y_tmp, test_size=0.25, random_state=SEED, stratify=y_tmp)

    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, max_features=200_000)
    clf = LogisticRegression(max_iter=2000, C=5).fit(vec.fit_transform(X_tr), y_tr)

    def prever(textos):
        p = clf.predict_proba(vec.transform(textos))
        return clf.classes_[p.argmax(1)], p.max(1)

    pv, cv = prever(X_va)
    limiares = np.round(np.arange(0.30, 0.99, 0.01), 2)
    limiar = next(t for t in limiares if (pv[cv >= t] == y_va.to_numpy()[cv >= t]).mean() >= ACURACIA_ALVO)

    pt, ct = prever(X_te)
    certo = pt == y_te.to_numpy()
    auto = ct >= limiar
    por_classe = (pd.DataFrame({"classe": y_te.to_numpy(), "auto": auto, "certo": certo})
                  .groupby("classe").agg(tickets=("auto", "size"), pct_automatico=("auto", "mean"),
                                         acuracia_automatico=("certo", lambda s: s[auto[s.index]].mean()))
                  .round(3).sort_values("pct_automatico"))
    por_classe.to_csv(OUT / "triagem_por_classe.csv", encoding="utf-8-sig")

    curva = pd.DataFrame([{"limiar": t, "cobertura": (ct >= t).mean(), "acuracia": certo[ct >= t].mean()}
                          for t in limiares if (ct >= t).any()])
    _grafico_curva(curva, limiar, auto.mean(), certo[auto].mean())

    exemplos = pd.DataFrame({"texto": X_te.str[:90], "real": y_te, "previsto": pt, "confianca": ct.round(2),
                             "rota": np.where(auto, "IA decide", "humano revisa")}).sample(6, random_state=3)
    return {
        "n_treino": len(X_tr), "n_validacao": len(X_va), "n_teste": len(X_te),
        "acuracia_geral_teste": round(float(certo.mean()), 4),
        "limiar_escolhido_na_validacao": float(limiar),
        "teste_cobertura_automatica": round(float(auto.mean()), 4),
        "teste_acuracia_automatica": round(float(certo[auto].mean()), 4),
        "teste_acuracia_fila_humana_sem_revisao": round(float(certo[~auto].mean()), 4),
        "classe_mais_dificil": por_classe.index[0],
        "por_classe": por_classe.reset_index().to_dict("records"),
        "exemplos": exemplos.to_dict("records"),
    }


def _grafico_curva(curva: pd.DataFrame, limiar: float, cob: float, acc: float) -> None:
    fig, ax = plt.subplots(figsize=(8, 3.8))
    fig.patch.set_facecolor("#fcfcfb"); ax.set_facecolor("#fcfcfb")
    ax.plot(curva["cobertura"], curva["acuracia"], color="#2a78d6", linewidth=2)
    ax.scatter([cob], [acc], color="#eb6834", s=70, zorder=3)
    ax.annotate(f"limiar {limiar:.2f}: IA decide {cob:.0%} dos tickets\ncom {acc:.1%} de acerto".replace(".", ","),
                (cob, acc), xytext=(-230, -40), textcoords="offset points", fontsize=9, color="#0b0b0b",
                arrowprops=dict(arrowstyle="-", color="#52514e"))
    ax.axhline(0.183, color="#b8b7b0", linestyle=":", linewidth=1.5)
    ax.text(0.02, 0.2, "triagem atual: 18,3% (= acaso)", fontsize=9, color="#52514e")
    ax.set_xlim(0, 1.02); ax.set_ylim(0, 1.02)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.set_xlabel("% dos tickets que a IA classifica sozinha", fontsize=9, color="#52514e")
    ax.set_ylabel("acerto nesses tickets", fontsize=9, color="#52514e")
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.grid(color="#e6e5e0", linewidth=0.8); ax.set_axisbelow(True)
    ax.tick_params(colors="#52514e", labelsize=9, length=0)
    ax.set_title("Quanto mais a IA assume, menos ela acerta: o limiar decide o ponto", loc="left",
                 fontsize=12, fontweight="bold", color="#0b0b0b", pad=20)
    ax.text(0, 1.03, "Dataset 2, 9.568 tickets de teste nunca vistos no treino", transform=ax.transAxes,
            fontsize=9, color="#52514e")
    fig.tight_layout(); fig.savefig(OUT / "06_triagem_ia_cobertura.png", dpi=160); plt.close(fig)


# ---------------------------------------------------------------------------
def parte_b(a: dict) -> dict:
    cob, acc_auto = a["teste_cobertura_automatica"], a["teste_acuracia_automatica"]
    erro_residual = cob * (1 - acc_auto) + (1 - cob) * (1 - ACURACIA_HUMANO_REVISANDO)
    horas_hoje = TICKETS_ANO * INCOERENCIA_HOJE * RETRIAGEM_MIN / 60
    horas_depois = TICKETS_ANO * erro_residual * RETRIAGEM_MIN / 60
    horas_revisao = TICKETS_ANO * (1 - cob) * REVISAO_MIN / 60
    liquido = horas_hoje - horas_depois - horas_revisao
    return {
        "erro_de_classificacao_hoje": INCOERENCIA_HOJE,
        "erro_de_classificacao_com_ia": round(erro_residual, 4),
        "horas_retriagem_hoje": round(horas_hoje),
        "horas_retriagem_com_ia": round(horas_depois),
        "horas_revisao_humana_nova": round(horas_revisao),
        "horas_liquidas_recuperadas": round(liquido),
        "pct_da_retriagem_recuperada": round(liquido / horas_hoje, 3),
        "rs_ano": round(liquido * CUSTO_HORA),
        "premissas": {"acuracia_humano_revisando": ACURACIA_HUMANO_REVISANDO, "revisao_min": REVISAO_MIN,
                      "retriagem_min": RETRIAGEM_MIN, "custo_hora_rs": CUSTO_HORA},
    }


# ---------------------------------------------------------------------------
def parte_c(caminho1: Path) -> dict:
    df = pd.read_csv(caminho1)
    fila = df[df["Ticket Status"] == "Open"].copy()
    texto = fila["Ticket Description"]
    for nome, (padrao, _) in SINAIS.items():
        fila[nome] = texto.str.contains(padrao, case=False, regex=True)
    fila["urgencia"] = texto.str.contains(URGENCIA, case=False, regex=True)
    fila["recontato"] = texto.str.contains(RECONTATO, case=False, regex=True)
    fila["severidade"] = fila[list(SINAIS)].mul([p for _, p in SINAIS.values()]).max(axis=1)
    fila["motivos"] = fila[list(SINAIS) + ["urgencia", "recontato"]].apply(
        lambda r: ", ".join(k for k, v in r.items() if v), axis=1)

    def sugerir(r):
        if r["severidade"] == 0 and not r["urgencia"]:
            return "Revisão humana"  # texto sem sinal claro: não adivinhar
        pontos = r["severidade"] + 2 * r["urgencia"] + r["recontato"]
        return "Critical" if pontos >= 5 else "High" if pontos >= 3 else "Medium" if pontos >= 2 else "Low"

    fila["prioridade_sugerida"] = fila.apply(sugerir, axis=1)
    ordem = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Revisão humana": 4}
    fila["ordem"] = fila["prioridade_sugerida"].map(ordem)
    fila["peso_declarado"] = fila["Ticket Priority"].map(PESO_PRIORIDADE)
    fila = fila.sort_values(["ordem", "peso_declarado", "Ticket ID"], ascending=[True, False, True])
    saida = fila[["Ticket ID", "Ticket Channel", "Ticket Priority", "prioridade_sugerida", "motivos",
                  "Ticket Subject", "Ticket Description"]].rename(columns={"Ticket Priority": "prioridade_declarada"})
    saida.to_csv(OUT / "fila_backlog_reprocessada.csv", index=False, encoding="utf-8-sig")

    alta = fila["prioridade_sugerida"].isin(["Critical", "High"])
    declarada_alta = fila["Ticket Priority"].isin(["Critical", "High"])
    return {
        "tickets_sem_resposta": len(fila),
        "prioridade_sugerida": fila["prioridade_sugerida"].value_counts().to_dict(),
        "cruzamento_declarada_x_sugerida": pd.crosstab(fila["Ticket Priority"], fila["prioridade_sugerida"]).to_dict(),
        "subpriorizados": int((alta & ~declarada_alta).sum()),
        "superpriorizados": int((~alta & declarada_alta & (fila["prioridade_sugerida"] != "Revisão humana")).sum()),
        "pct_vai_para_humano": round(float((fila["prioridade_sugerida"] == "Revisão humana").mean()), 4),
        "top5": saida.head(5)[["Ticket ID", "prioridade_declarada", "prioridade_sugerida", "motivos"]].to_dict("records"),
    }


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=HERE.parents[1] / "data" / "support_tickets.csv")
    ap.add_argument("--data2", type=Path, default=HERE.parents[1] / "data" / "it_tickets.csv")
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    a = parte_a(args.data2)
    b = parte_b(a)
    c = parte_c(args.data)
    r = {"A_viabilidade_dataset2": a, "B_roi_retriagem": b, "C_backlog_dataset1": c}
    (OUT / "triagem_ia.json").write_text(json.dumps(r, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ("por_classe", "exemplos", "cruzamento_declarada_x_sugerida")}
                      for k, v in r.items()}, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
