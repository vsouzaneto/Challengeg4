"""
Avaliação final do motor de triagem do protótipo: a fonte dos números citados no relatório.

Diferente de benchmark.py (que compara abordagens), aqui se mede o motor COMO ELE RODA no app:
limiar por categoria + travas de domínio + política.

    python benchmark/avaliar_motor.py      (a partir de solution/03-prototipo)
Saída: benchmark/outputs/motor_final.md
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")  # Windows: evita erro de cp1252 com saída redirecionada
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROTO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROTO))
from src.politica import ROTULOS, avaliar  # noqa: E402
from src.triagem import DADOS, RAIZ, MotorTriagem, dividir, preparar  # noqa: E402

OUT = Path(__file__).resolve().parent / "outputs"


def pct(x: float, casas: int = 1) -> str:
    return f"{100 * x:.{casas}f}%".replace(".", ",")


def bootstrap_ic(acertos: np.ndarray, n: int = 2000, seed: int = 0) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    medias = [rng.choice(acertos, len(acertos)).mean() for _ in range(n)]
    return float(np.quantile(medias, 0.025)), float(np.quantile(medias, 0.975))


def main() -> None:
    m = MotorTriagem.carregar()
    _, _, te = dividir(pd.read_csv(DADOS))
    r = m.classificar_lote(te["Document"])
    r["real"] = te["Topic_group"]
    r["ok"] = r["categoria"] == r["real"]
    r["ok2"] = (r["top2_a"] == r["real"]) | (r["top2_b"] == r["real"])

    L = ["# Motor de triagem final: avaliação no conjunto de teste", "",
         f"_{len(r):,} tickets reais do Dataset 2 que o modelo nunca viu. Gerado por `benchmark/avaliar_motor.py`._".replace(",", "."), "",
         "## 1. Faixas de automação", "",
         "| Faixa | % dos tickets | Acerto da 1ª opção | Certa entre as 2 primeiras |", "|---|---|---|---|"]
    for f, nome in [("auto", "Automático"), ("sugere", "Sugestão (humano escolhe entre 2)"), ("humano", "Humano")]:
        g = r[r["faixa"] == f]
        L.append(f"| {nome} | {pct(len(g) / len(r))} | {pct(g['ok'].mean())} | {pct(g['ok2'].mean())} |")
    hum = r[r["faixa"] == "humano"]
    L += ["", "**Por que um ticket vai para humano:**", "", "| Motivo | % de todos os tickets | O modelo acertaria | Sem as travas, iria para |",
          "|---|---|---|---|"]
    for mot, g in hum.groupby("motivo_humano"):
        destino = ", ".join(f"{k} {pct(v)}" for k, v in g["faixa_sem_travas"].value_counts(normalize=True).items())
        L.append(f"| {mot} | {pct(len(g) / len(r))} | {pct(g['ok'].mean())} | {destino} |")
    L += ["", "A trava de domínio troca cobertura por segurança: ela também barra tickets normais, porém atípicos "
          "(pouco parecidos com o histórico), que o modelo acertaria na maioria das vezes. É o custo de não deixar "
          "passar tickets de outro domínio (seção 3)."]
    lo, hi = bootstrap_ic(r.loc[r["faixa"] == "auto", "ok"].values.astype(float))
    L += ["", f"Intervalo de confiança de 95% (bootstrap) para o acerto da faixa automática: **{pct(lo)} a {pct(hi)}**.", "",
          f"Para comparar: o modelo sem as travas acerta {pct(r['ok'].mean())} no geral.", "",
          "## 2. Faixa automática por categoria prevista", "",
          "| Categoria | Limiar | Origem do limiar | Tickets automáticos | Acerto | IC95% (bootstrap) |", "|---|---|---|---|---|---|"]
    auto = r[r["faixa"] == "auto"]
    global_auto = min(m.limiares.values())
    for c, g in auto.groupby("categoria"):
        lo_c, hi_c = bootstrap_ic(g["ok"].to_numpy(dtype=float))
        origem = "próprio da categoria" if m.limiares[c] > global_auto + 1e-9 else "global (validação)"
        L.append(f"| {c} | {m.limiares[c]:.2f}".replace(".", ",") + f" | {origem} | {len(g)} | {pct(g['ok'].mean())} | {pct(lo_c)} a {pct(hi_c)} |")
    L += ["", "Só as categorias que ficariam abaixo de 95% com o limiar global (Hardware e Miscellaneous) ganharam limiar próprio. "
          "As demais usam o global; categorias com menos de 150 casos na validação usam o global por estabilidade. "
          "Os acertos por categoria são estimativas pontuais: Hardware, no limite, tem intervalo que passa abaixo de 95%."]

    # Para onde vão sozinhos os tickets de cada categoria real (erros da faixa automática)
    err = auto[~auto["ok"]].groupby(["real", "categoria"]).size().sort_values(ascending=False).head(5)
    L += ["", "**Principais erros automáticos (real → previsto):** " +
          "; ".join(f"{a} → {b}: {v}" for (a, b), v in err.items())]

    # Fora do domínio: tickets de cliente (Dataset 1) com o mesmo pré-processamento
    d1 = pd.read_csv(RAIZ / "data/ds1_customer_support/customer_support_tickets.csv")
    x1 = d1["Ticket Description"].str.replace(r"\{[^}]*\}", " ", regex=True).map(preparar)
    r1 = m.classificar_lote(x1)
    L += ["", "## 3. Teste fora do domínio (tickets de cliente do Dataset 1)", "",
          "Um modelo de TI interna recebendo tickets de clientes de produto deveria perceber que não sabe.", "",
          "| Faixa | % dos 8.469 tickets |", "|---|---|"]
    L += [f"| {f} | {pct((r1['faixa'] == f).mean())} |" for f in ["auto", "sugere", "humano"]]
    so_conf = (r1["confianca"] >= pd.Series([m.limiares[c] for c in r1["categoria"]], index=r1.index)).mean()
    L += ["", f"Sem as travas de domínio, **{pct(so_conf)}** desses tickets teriam ido para a faixa automática."]

    # Sensibilidade da trava de similaridade: medida na VALIDAÇÃO (dentro do domínio) e no Dataset 1 (fora)
    from src.triagem import SIMILARIDADE_MINIMA
    _, va, _ = dividir(pd.read_csv(DADOS))
    sim_va = m.classificar_lote(va["Document"])["similaridade"].to_numpy()
    sim_d1 = r1["similaridade"].to_numpy()
    L += ["", "### Sensibilidade da trava de similaridade", "",
          f"O limiar {SIMILARIDADE_MINIMA:.2f}".replace(".", ",") + " foi escolhido por inspeção das duas distribuições, e não por otimização. "
          "Como o Dataset 1 foi usado para escolhê-lo, o resultado fora do domínio é otimista. A tabela mostra a sensibilidade:", "",
          "| Limiar | Tickets normais barrados (validação) | Tickets de outro domínio barrados (Dataset 1) |", "|---|---|---|"]
    for t in [0.15, 0.20, 0.25]:
        L.append(f"| {t:.2f}".replace(".", ",") + f" | {pct((sim_va < t).mean())} | {pct((sim_d1 < t).mean())} |")

    # Política no teste
    pol = te["Document"].map(avaliar)
    alertas = pd.Series([a for p in pol for a in p.alertas]).map(ROTULOS).value_counts()
    L += ["", "## 4. Política no conjunto de teste", "",
          f"- {pct(pol.map(lambda p: p.exige_humano_para_executar).mean())} dos tickets têm uma ação que exige humano",
          f"- {pct((~pol.map(lambda p: p.pode_gerar_rascunho)).mean())} bloqueiam o rascunho por LLM",
          f"- {pct(pol.map(lambda p: p.escalar).mean())} são escalados", "",
          "| Regra | Tickets |", "|---|---|"] + [f"| {k} | {v} |" for k, v in alertas.items()]

    OUT.mkdir(exist_ok=True)
    (OUT / "motor_final.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
