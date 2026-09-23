"""Economia e aprendizado — Challenge 002, Entrega 2 (aprofundamento).

Responde duas perguntas com medição no Dataset 2 (47.837 tickets reais rotulados):

  Onde economizar sem perder eficiência?
  O que medir para a IA aprender com os erros e os acertos?

  B1  Ciclo de aprendizado: 12 meses de operação simulada. O modelo começa com
      3.000 rótulos (gold set) e aprende, ou não, com o que os humanos fazem.
  B2  Monitor de categoria nova: o limiar NÃO protege contra uma categoria que o
      modelo nunca viu (harness A6). Mede qual sinal de população detecta a novidade.
  B3  Revisão humana com 3 sugestões: a classe certa está entre elas?
  B4  Como proteger pedidos de permissão: limiar próprio × gatilho de palavra × controle na ação.
  B5  Tamanho da auditoria: quantos acertos conferir por mês para ver uma queda de acurácia.
  B6  Economias: o que dá para cortar ou trocar sem perder acerto ou segurança.

Uso:
    python aprendizado.py --data2 ../data/it_tickets.csv      # ≈ 5 min
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

import modelo as mo

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
RNG = np.random.default_rng(mo.SEED)

# Premissas (não vêm do dataset; trocáveis)
GOLD_SET = 3_000
TICKETS_MES = 2_500                 # 30 mil/ano
P_TRANSFERENCIA = 0.8               # chance de o agente da fila errada devolver o ticket ("não é meu")
AUDITORIA = 0.10                    # fração dos automáticos conferida por humano (B5: 10% vê a queda de acerto no mês)
SEMANA = 600                        # tickets por semana (30 mil / 50)
CLASSE_NOVA = "Administrative rights"  # pior caso do harness A6
MIN_RASCUNHO = {"baixo": 1, "base": 3, "alto": 5}   # minutos economizados por rascunho aprovado
MIN_REVISAO = {"hoje": 1.0, "top3": 0.5}             # triagem humana: 8 classes × escolher entre 3
MIN_ROTULO = 1.0                    # minutos para rotular 1 ticket num projeto de rotulagem
ROTA1A_TICKETS_D1, D1_TICKETS = 1_267, 8_469        # rota 1 só por hardware/reparo/recontato (automacao.py)


def _estilo(ax, fig):
    fig.patch.set_facecolor("#fcfcfb"); ax.set_facecolor("#fcfcfb")
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.grid(color="#e6e5e0", linewidth=0.8); ax.set_axisbelow(True)
    ax.tick_params(colors="#52514e", labelsize=9, length=0)


# ---------------------------------------------------------------------------
def b1_ciclo(X_tr, X_va, X_te, y_tr, y_va, y_te) -> dict:
    ordem = RNG.permutation(len(X_tr))
    gold, fluxo = ordem[:GOLD_SET], ordem[GOLD_SET:]
    meses = [fluxo[i:i + TICKETS_MES] for i in range(0, len(fluxo), TICKETS_MES)][:11]
    estrategias = {
        "congelado": "não aprende: fica com o gold set",
        "triagem": "aprende com os tickets que o humano triou (abaixo do limiar)",
        "completo": "triagem + tickets devolvidos pela fila errada + auditoria de 10% dos automáticos",
        "autotreino": "triagem + as próprias previsões automáticas como rótulo",
    }
    rng = np.random.default_rng(mo.SEED)
    saida = {}
    for nome in estrategias:
        idx = list(gold)
        rotulo = list(y_tr[gold])
        m = mo.treinar(X_tr[idx], np.array(rotulo))
        caminho = []
        for k in range(len(meses) + 1):
            pv, cv, _, _ = mo.prever(m, X_va)
            t = mo.escolher_limiar(cv, pv, y_va)
            cob, acc = mo.cobertura_e_acerto(m, t, X_te, y_te)
            caminho.append({"mes": k, "cobertura": round(cob, 4), "acerto": round(acc, 4), "rotulos": len(idx)})
            print(f"  B1 {nome:10s} mês {k:2d}: cobertura {cob:.3f} acerto {acc:.3f} rótulos {len(idx)}", flush=True)
            if k == len(meses) or nome == "congelado":
                if nome == "congelado":
                    caminho = [dict(caminho[0], mes=j) for j in range(len(meses) + 1)]
                    break
                continue
            lote = meses[k]
            p, c, _, _ = mo.prever(m, X_tr[lote])
            auto, verdade = c >= t, y_tr[lote]
            novo, novo_y = list(lote[~auto]), list(verdade[~auto])
            if nome == "completo":
                errado = auto & (p != verdade) & (rng.random(len(lote)) < P_TRANSFERENCIA)
                auditado = auto & ~errado & (rng.random(len(lote)) < AUDITORIA)
                novo += list(lote[errado | auditado]); novo_y += list(verdade[errado | auditado])
            if nome == "autotreino":
                novo += list(lote[auto]); novo_y += list(p[auto])
            idx += novo; rotulo += novo_y
            m = mo.treinar(X_tr[idx], np.array(rotulo))
        horas_ano1 = float(np.mean([mo.horas_retriagem(x["cobertura"], x["acerto"]) for x in caminho[:12]]))
        saida[nome] = {"descricao": estrategias[nome], "caminho": caminho, "horas_ano1": round(horas_ano1),
                       "horas_regime": round(mo.horas_retriagem(caminho[-1]["cobertura"], caminho[-1]["acerto"])),
                       "cobertura_final": caminho[-1]["cobertura"], "rotulos_finais": caminho[-1]["rotulos"]}
    saida["horas_se_73pct_desde_o_dia_1"] = round(mo.horas_retriagem(0.732, 0.951))
    _grafico_ciclo(saida)
    return saida


def _grafico_ciclo(s: dict) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    _estilo(ax, fig)
    cores = {"congelado": "#b8b7b0", "triagem": "#7c4dcc", "completo": "#2a78d6", "autotreino": "#eb6834"}
    rotulos = {"congelado": "congelado (não aprende)", "triagem": "aprende com a triagem humana",
               "completo": "triagem + devoluções + auditoria de acertos", "autotreino": "autotreino (usa as próprias previsões)"}
    for nome, cor in cores.items():
        c = s[nome]["caminho"]
        ax.plot([x["mes"] for x in c], [x["cobertura"] for x in c], color=cor, linewidth=2.2 if nome == "completo" else 1.6,
                label=rotulos[nome], marker="o", markersize=3)
    ax.axhline(0.732, color="#0b0b0b", linestyle=":", linewidth=1)
    ax.text(0.2, 0.737, "com os 28.701 rótulos do treino: 73%", fontsize=8, color="#52514e")
    ax.set_ylim(0.4, 0.8); ax.set_xlim(0, 11)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.set_xlabel("meses de operação", fontsize=9, color="#52514e")
    ax.set_ylabel("tickets decididos sozinhos com ≥ 95% de acerto", fontsize=9, color="#52514e")
    ini, fim = s["completo"]["caminho"][0]["cobertura"], s["completo"]["cobertura_final"]
    ax.set_title(f"Aprendendo com o trabalho humano: de {ini:.0%} para {fim:.0%} em 11 meses", loc="left",
                 fontsize=11.5, fontweight="bold", color="#0b0b0b", pad=20)
    ax.text(0, 1.03, "Dataset 2. Início com 3.000 rótulos; 2.500 tickets por mês; acerto mantido em ≈ 95% em todas as curvas",
            transform=ax.transAxes, fontsize=8.5, color="#52514e")
    ax.legend(loc="lower right", bbox_to_anchor=(1, 0.27), fontsize=8, frameon=False)
    fig.tight_layout(); fig.savefig(OUT / "10_ciclo_aprendizado.png", dpi=160); plt.close(fig)


# ---------------------------------------------------------------------------
def b2_monitor(X_tr, X_va, X_te, y_tr, y_va, y_te) -> dict:
    conhecido_tr, conhecido_va = y_tr != CLASSE_NOVA, y_va != CLASSE_NOVA
    m = mo.treinar(X_tr[conhecido_tr], y_tr[conhecido_tr])
    pv, cv, _, classes = mo.prever(m, X_va[conhecido_va])
    yv = y_va[conhecido_va]
    t = mo.escolher_limiar(cv, pv, yv)
    # Linha de base, medida na validação (só categorias conhecidas)
    base_mix = pd.Series(pv).value_counts(normalize=True).reindex(classes, fill_value=0).to_numpy()
    base_abaixo = float((cv < t).mean())
    base_devolvido = float(((cv >= t) & (pv != yv)).mean() * P_TRANSFERENCIA)

    pt, ct, _, _ = mo.prever(m, X_te)
    novo = y_te == CLASSE_NOVA
    idx_conh, idx_novo = np.where(~novo)[0], np.where(novo)[0]
    novos_auto_errados = float((ct[novo] >= t).mean())
    rng = np.random.default_rng(mo.SEED)

    def poder(fracao: float, n: int, sims: int = 400) -> dict:
        hits = {"mistura_de_classes": 0, "fila_de_triagem": 0, "devolucoes": 0}
        for _ in range(sims):
            k = rng.binomial(n, fracao)
            amostra = np.concatenate([rng.choice(idx_conh, n - k), rng.choice(idx_novo, k)])
            p, c, y = pt[amostra], ct[amostra], y_te[amostra]
            cont = pd.Series(p).value_counts().reindex(classes, fill_value=0).to_numpy()
            if stats.chisquare(cont, base_mix * n).pvalue < 0.01:
                hits["mistura_de_classes"] += 1
            if stats.binomtest(int((c < t).sum()), n, base_abaixo, alternative="greater").pvalue < 0.01:
                hits["fila_de_triagem"] += 1
            devolvidos = int((((c >= t) & (p != y)) & (rng.random(n) < P_TRANSFERENCIA)).sum())
            if stats.binomtest(devolvidos, n, base_devolvido, alternative="greater").pvalue < 0.01:
                hits["devolucoes"] += 1
        return {k: round(v / sims, 3) for k, v in hits.items()}

    resultado = {}
    for fr in (0.0, 0.02, 0.05, 0.10):
        resultado[f"{fr:.0%}"] = {"1_semana": poder(fr, SEMANA), "4_semanas": poder(fr, 4 * SEMANA)}
        print(f"  B2 categoria nova {fr:.0%}: {resultado[f'{fr:.0%}']}", flush=True)
    _grafico_monitor(resultado)
    return {"classe_nova_simulada": CLASSE_NOVA, "limiar": t, "novos_classificados_errado_com_confianca": round(novos_auto_errados, 3),
            "linha_de_base": {"fila_de_triagem": round(base_abaixo, 4), "devolucoes": round(base_devolvido, 4)},
            "poder_de_deteccao_p<0,01": resultado,
            "leitura": "0% = taxa de alarme falso; demais = chance de o monitor disparar"}


def _grafico_monitor(r: dict) -> None:
    fig, ax = plt.subplots(figsize=(8, 3.8))
    _estilo(ax, fig)
    monitores = [("devolucoes", "devoluções da fila errada", "#2a78d6"),
                 ("mistura_de_classes", "mistura de classes previstas", "#7c4dcc"),
                 ("fila_de_triagem", "tamanho da fila de triagem", "#eb6834")]
    fracoes = ["0%", "2%", "5%", "10%"]
    x = np.arange(len(fracoes))
    for i, (k, rot, cor) in enumerate(monitores):
        ax.bar(x + (i - 1) * 0.26, [r[f]["1_semana"][k] for f in fracoes], width=0.25, color=cor, label=rot)
    ax.set_xticks(x, [f"{f} do volume" if f != "0%" else "sem categoria nova\n(alarme falso)" for f in fracoes])
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("chance de disparar em 1 semana", fontsize=9, color="#52514e")
    ax.set_title("Categoria nova: contar as devoluções detecta; olhar o ticket sozinho não", loc="left",
                 fontsize=11.5, fontweight="bold", color="#0b0b0b", pad=20)
    ax.text(0, 1.03, f"Dataset 2, modelo treinado sem '{CLASSE_NOVA}'. {SEMANA} tickets/semana, p < 0,01",
            transform=ax.transAxes, fontsize=8.5, color="#52514e")
    ax.legend(loc="upper left", fontsize=8, frameon=False)
    fig.tight_layout(); fig.savefig(OUT / "11_monitor_categoria_nova.png", dpi=160); plt.close(fig)


# ---------------------------------------------------------------------------
def b3_b4(m, X_va, X_te, y_va, y_te) -> tuple[dict, dict]:
    pv, cv, _, _ = mo.prever(m, X_va)
    t = mo.escolher_limiar(cv, pv, y_va)
    pt, ct, P, classes = mo.prever(m, X_te)
    abaixo = ct < t
    ordem = classes[np.argsort(-P, 1)]
    topk = {f"top{k}": round(float((ordem[abaixo, :k] == y_te[abaixo, None]).any(1).mean()), 4) for k in (1, 2, 3)}
    cob = float((~abaixo).mean())
    horas_rev = {k: round(30_000 * (1 - cob) * v / 60) for k, v in MIN_REVISAO.items()}
    b3 = {"limiar": t, "fila_humana": round(1 - cob, 4), "classe_certa_entre_as_sugestoes": topk,
          "horas_revisao_ano": horas_rev, "economia_h_ano": horas_rev["hoje"] - horas_rev["top3"]}

    # B4: como proteger pedidos de permissão (a classe de risco)?
    # Opção 1: limiar próprio para quando o modelo PREVÊ a classe de risco.
    risco = pv == CLASSE_NOVA
    t_risco = max(t, mo.escolher_limiar(cv[risco], pv[risco], y_va[risco]))
    real, auto = y_te == CLASSE_NOVA, ~abaixo
    mal_roteado = real & auto & (pt != y_te)
    # Opção 2: gatilho de palavra que manda para humano qualquer ticket que pareça pedido de permissão.
    padroes = {"estreito": r"\badmin|\brights\b|\bpermission|\bprivilege",
               "amplo": r"\badmin|\brights\b|\bpermission|\binstall|\bupgrad|\bprivilege|\bwindows\b|\boutlook\b"}
    gatilho = {}
    for nome, pad in padroes.items():
        hit = pd.Series(X_te).str.contains(pad, regex=True).to_numpy()
        gatilho[nome] = {"pega_os_mal_roteados": round(float((hit & mal_roteado).sum() / max(mal_roteado.sum(), 1)), 3),
                         "tickets_automaticos_que_viram_humano": round(float((hit & auto & ~real).mean()), 4)}
    b4 = {"pedidos_de_permissao_decididos_sozinhos": int((real & auto).sum()),
          "mal_roteados": int(mal_roteado.sum()),
          "para_onde_vao": pd.Series(pt[mal_roteado]).value_counts().to_dict(),
          "acerto_quando_o_modelo_diz_permissao": round(float((pt == y_te)[(pt == CLASSE_NOVA) & auto].mean()), 4),
          "opcao1_limiar_proprio": {"limiar_global": t, "limiar_proprio": t_risco,
                                    "muda_algo": bool(t_risco > t)},
          "opcao2_gatilho_de_palavra": gatilho,
          "leitura": "O risco não é o modelo dizer 'permissão' e errar; é um pedido de permissão ir para Hardware. "
                     "Limiar próprio não muda nada e gatilho de palavra custa caro: a proteção certa é na AÇÃO "
                     "(nenhuma concessão de acesso sem aprovação humana no sistema de identidade)."}
    return b3, b4


# ---------------------------------------------------------------------------
def b5_auditoria(acerto_base: float = 0.95, acerto_ruim: float = 0.90) -> dict:
    """Poder de detectar a queda de acurácia em 1 mês, por tamanho de amostra auditada."""
    auto_mes = int(TICKETS_MES * 0.73)
    out = {}
    for taxa in (0.01, 0.02, 0.05, 0.10):
        n = int(auto_mes * taxa)
        corte = stats.binom.ppf(0.05, n, acerto_base)  # alarme se acertos <= corte (alarme falso ≈ 5%)
        out[f"{taxa:.0%}"] = {"tickets_auditados_mes": n,
                              "poder_detectar_queda_95_para_90": round(float(stats.binom.cdf(corte, n, acerto_ruim)), 3),
                              "horas_mes_a_0,5_min": round(n * 0.5 / 60, 1)}
    return {"tickets_automaticos_mes": auto_mes, "por_taxa": out}


# ---------------------------------------------------------------------------
def b6_economias(b1: dict, b2: dict, b3: dict, X_tr, X_va, X_te, y_tr, y_va, y_te) -> dict:
    # Rota 1A: a IA rascunha, o humano decide (hardware, reparo, recontato)
    tickets_1a = ROTA1A_TICKETS_D1 / D1_TICKETS * 30_000
    rota1a = {k: round(tickets_1a * v / 60) for k, v in MIN_RASCUNHO.items()}
    # Rótulos que o trabalho normal produz: não precisa de projeto de rotulagem
    rot_gratis = b1["completo"]["rotulos_finais"] - GOLD_SET
    # Tamanho do gold set: 1.000 contra 3.000 rótulos
    ordem = np.random.default_rng(mo.SEED).permutation(len(X_tr))
    gold = {}
    for n in (1_000, 3_000):
        m = mo.treinar(X_tr[ordem[:n]], y_tr[ordem[:n]])
        pv, cv, _, _ = mo.prever(m, X_va)
        cob, acc = mo.cobertura_e_acerto(m, mo.escolher_limiar(cv, pv, y_va), X_te, y_te)
        gold[n] = {"cobertura": round(cob, 4), "horas_ano": round(mo.horas_retriagem(cob, acc))}
    diff_h_mes = (gold[3_000]["horas_ano"] - gold[1_000]["horas_ano"]) / 12
    custo_2000 = 2_000 * MIN_ROTULO / 60
    return {
        "rota_1A_ia_rascunha_humano_decide": {"tickets_ano": round(tickets_1a), "horas_ano": rota1a},
        "revisao_com_3_sugestoes": {"horas_ano": b3["economia_h_ano"]},
        "rotulos_do_trabalho_normal": {"rotulos_em_11_meses": rot_gratis,
                                       "horas_de_rotulagem_evitadas": round(rot_gratis * MIN_ROTULO / 60)},
        "gold_set_1000_vs_3000": {**{str(k): v for k, v in gold.items()},
                                  "custo_extra_de_2000_rotulos_h": round(custo_2000),
                                  "paga_em_meses": round(custo_2000 / diff_h_mes, 1) if diff_h_mes > 0 else None},
        "ano_1_com_aprendizado_vs_premissa_da_proposta": {
            "premissa_73pct_desde_o_dia_1": b1["horas_se_73pct_desde_o_dia_1"],
            "congelado": b1["congelado"]["horas_ano1"], "completo": b1["completo"]["horas_ano1"]},
    }


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--data2", type=Path, default=HERE.parent / "data" / "it_tickets.csv")
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    X_tr, X_va, X_te, y_tr, y_va, y_te = mo.dividir(args.data2)
    print("B1 ciclo de aprendizado (≈ 4 min)")
    b1 = b1_ciclo(X_tr, X_va, X_te, y_tr, y_va, y_te)
    print("B2 monitor de categoria nova")
    b2 = b2_monitor(X_tr, X_va, X_te, y_tr, y_va, y_te)
    m = mo.treinar(X_tr, y_tr)
    b3, b4 = b3_b4(m, X_va, X_te, y_va, y_te)
    b5 = b5_auditoria()
    b6 = b6_economias(b1, b2, b3, X_tr, X_va, X_te, y_tr, y_va, y_te)
    r = {"B1_ciclo_de_aprendizado": b1, "B2_monitor_categoria_nova": b2, "B3_revisao_top3": b3,
         "B4_protecao_permissao": b4, "B5_tamanho_da_auditoria": b5, "B6_economias": b6}
    (OUT / "aprendizado.json").write_text(json.dumps(r, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in r.items() if k != "B1_ciclo_de_aprendizado"}, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
