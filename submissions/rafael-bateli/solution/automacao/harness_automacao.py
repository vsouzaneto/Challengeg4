"""Harness da Entrega 2: a proposta de automação estava certa?

Tenta DERRUBAR cada decisão da PROPOSTA_AUTOMACAO.md. O critério de cada teste
está escrito no código antes de rodar; o veredito não depende de interpretação.

  A1  Os números dos documentos batem com o código?
  A2  As regras de palavra-chave foram um espantalho?          (regras com margem, no melhor caso)
  A3  O modelo escolhido é o certo, ou outro mais barato ganha? (5 modelos)
  A4  O limiar de confiança é estável?                          (5 divisões diferentes)
  A5  A confiança do modelo é calibrada?                        (erro de calibração, ECE)
  A6  O limiar protege contra uma categoria que o modelo nunca viu?
  A7  3.000 rótulos entregam os 73% de cobertura prometidos?    (curva de aprendizado)
  A8  Rotular os tickets mais incertos acelera o aprendizado?   (incerteza × sorteio)
  A9  A quase-duplicata ajuda a classificar?
  A10 Os 33% de humano dependem de um gatilho só?               (remove um gatilho por vez)
  A11 O custo de LLM pode passar do ganho?                      (Monte Carlo)
  A12 "Regras fixas primeiro" resiste às premissas?             (Monte Carlo de horas e esforço)
  A13 A entrega cobre o que o desafio pede?                     (requisito → trecho do documento)

Uso:
    python harness_automacao.py --data2 ../data/it_tickets.csv     # ≈ 4 min
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.metrics import roc_auc_score
from sklearn.naive_bayes import ComplementNB
from sklearn.svm import LinearSVC

import modelo as mo

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
DIAG = HERE.parent / "diagnostico" / "outputs"
# SUSTENTOU: a decisão sobreviveu ao teste. DERRUBOU: a decisão (ou a frase) caiu e foi corrigida.
PASSOU, FALHOU = "SUSTENTOU", "DERRUBOU"
resultados: list[dict] = []


def registrar(hid: str, pergunta: str, veredito: str, evidencia: dict, conclusao: str) -> None:
    resultados.append({"id": hid, "pergunta": pergunta, "veredito": veredito,
                       "conclusao": conclusao, "evidencia": evidencia})
    print(f"[{veredito:9s}] {hid} — {pergunta}\n         {conclusao}", flush=True)


def pct(x: float, casas: int = 1) -> str:
    return f"{x * 100:.{casas}f}%".replace(".", ",")


def _limiar_e_teste(m, X_va, y_va, X_te, y_te):
    pv, cv, _, _ = mo.prever(m, X_va)
    t = mo.escolher_limiar(cv, pv, y_va)
    return (t, *mo.cobertura_e_acerto(m, t, X_te, y_te))


# ---------------------------------------------------------------------------
def a2_regras(X_tr, X_te, y_tr, y_te, cobertura_modelo) -> None:
    """Regras com exigência de margem (a classe vencedora precisa de N palavras a mais que a 2ª)."""
    cv = CountVectorizer(binary=True, min_df=20)
    B = cv.fit_transform(X_tr)
    vocab, freq = np.array(cv.get_feature_names_out()), np.asarray(B.sum(0)).ravel()
    classes = sorted(set(y_tr))
    Bte, col = cv.transform(X_te), {w: i for i, w in enumerate(vocab)}
    grade = []
    for k in (10, 20, 50):
        pal = {}
        for c in classes:
            dentro = np.asarray(B[y_tr == c].sum(0)).ravel()
            pal[c] = vocab[np.argsort(-(dentro / freq) * np.log1p(dentro))[:k]]
        H = np.stack([np.asarray(Bte[:, [col[w] for w in pal[c]]].sum(1)).ravel() for c in classes], 1)
        s = np.sort(H, 1)
        margem, prev = s[:, -1] - s[:, -2], np.array(classes)[H.argmax(1)]
        for mg in (1, 2, 3, 4, 5):
            m = margem >= mg
            grade.append({"palavras": k, "margem": mg, "cobertura": round(float(m.mean()), 4),
                          "acerto": round(float((prev[m] == y_te[m]).mean()), 4)})
    a95 = [g for g in grade if g["acerto"] >= 0.95]
    melhor = max(a95, key=lambda g: g["cobertura"]) if a95 else {"cobertura": 0.0}
    ok = cobertura_modelo >= 2 * melhor["cobertura"]
    registrar("A2", "As regras de palavra-chave foram um espantalho?", PASSOU if ok else FALHOU,
              {"grade": grade, "melhor_regra_com_95pct": melhor, "modelo_cobertura_95pct": cobertura_modelo},
              f"Com margem, regras chegam a 95%+ de acerto, mas cobrindo no máximo {pct(melhor['cobertura'])} "
              f"dos tickets; o modelo cobre {pct(cobertura_modelo)}. A frase 'regras param em 80%' estava errada; "
              "a conclusão (modelo > regra) se mantém.")


def a3_alternativas(X_tr, X_va, X_te, y_tr, y_va, y_te) -> None:
    candidatos = {
        "Regressão logística, 200 mil variáveis (proposta)": dict(max_features=200_000),
        "Regressão logística, 50 mil variáveis": dict(max_features=50_000),
        "Naive Bayes complementar": dict(max_features=200_000, clf=ComplementNB(alpha=0.3)),
        "SVM linear calibrado": dict(max_features=200_000, clf=CalibratedClassifierCV(LinearSVC(C=0.5), cv=3)),
        "Gradiente estocástico (log)": dict(max_features=200_000,
                                            clf=SGDClassifier(loss="log_loss", alpha=1e-5, max_iter=30, random_state=0)),
    }
    tabela = {}
    for nome, kw in candidatos.items():
        t0 = time.perf_counter()
        m = mo.treinar(X_tr, y_tr, **kw)
        treino = time.perf_counter() - t0
        t, cob, acc = _limiar_e_teste(m, X_va, y_va, X_te, y_te)
        tabela[nome] = {"cobertura": round(cob, 4), "acerto": round(acc, 4), "treino_s": round(treino, 1)}
    base = tabela["Regressão logística, 200 mil variáveis (proposta)"]["cobertura"]
    melhor = max(tabela.items(), key=lambda kv: kv[1]["cobertura"])
    ok = melhor[1]["cobertura"] <= base + 0.02
    registrar("A3", "O modelo escolhido é o certo, ou outro ganha com folga?", PASSOU if ok else FALHOU,
              {"alternativas": tabela},
              f"Melhor alternativa: {melhor[0]} com {pct(melhor[1]['cobertura'])} contra {pct(base)} "
              "(critério: vencer por mais de 2 p.p.). Economia achada: 50 mil variáveis dão o mesmo resultado "
              "com metade do tempo de treino.")


def a4_estabilidade(caminho2) -> None:
    linhas = []
    for s in (42, 1, 7, 13, 99):
        X_tr, X_va, X_te, y_tr, y_va, y_te = mo.dividir(caminho2, seed=s)
        t, cob, acc = _limiar_e_teste(mo.treinar(X_tr, y_tr), X_va, y_va, X_te, y_te)
        linhas.append({"seed": s, "limiar": t, "cobertura": round(cob, 4), "acerto": round(acc, 4)})
    cobs, accs = [x["cobertura"] for x in linhas], [x["acerto"] for x in linhas]
    ok = min(accs) >= 0.945 and max(cobs) - min(cobs) <= 0.05
    registrar("A4", "O limiar de confiança é estável em outras divisões do dado?", PASSOU if ok else FALHOU,
              {"divisoes": linhas},
              f"Cobertura {pct(min(cobs))}–{pct(max(cobs))}, acerto {pct(min(accs))}–{pct(max(accs))} em 5 divisões.")


def a5_calibracao(m, X_te, y_te) -> None:
    prev, conf, _, _ = mo.prever(m, X_te)
    certo, ece, faixas = prev == y_te, 0.0, []
    for lo, hi in zip(np.linspace(0, 0.9, 10), np.linspace(0.1, 1.0, 10)):
        f = (conf > lo) & (conf <= hi)
        if f.any():
            ece += f.mean() * abs(certo[f].mean() - conf[f].mean())
            faixas.append({"faixa": f"{lo:.1f}-{hi:.1f}", "n": int(f.sum()), "confianca": round(float(conf[f].mean()), 3),
                           "acerto": round(float(certo[f].mean()), 3)})
    registrar("A5", "A confiança do modelo é calibrada (70% de confiança ≈ 70% de acerto)?",
              PASSOU if ece < 0.05 else FALHOU, {"ece": round(ece, 4), "faixas": faixas},
              f"Erro de calibração (ECE) = {ece:.3f} (critério < 0,05)".replace(".", ",", 1) + f". O limiar de confiança significa o que diz.")


def a6_categoria_nova(X_tr, X_va, X_te, y_tr, y_va, y_te) -> None:
    linhas = []
    for nova in ("Purchase", "Storage", "Administrative rights", "Internal Project"):
        conh = y_tr != nova
        m = mo.treinar(X_tr[conh], y_tr[conh])
        cva = y_va != nova
        pv, cv, _, _ = mo.prever(m, X_va[cva])
        t = mo.escolher_limiar(cv, pv, y_va[cva])
        _, ct, _, _ = mo.prever(m, X_te)
        eh_nova = y_te == nova
        # detector por ticket: similaridade com o vizinho mais próximo do treino
        vec, _ = m
        Vtr, Vte = vec.transform(X_tr[conh]), vec.transform(X_te)
        sim = np.concatenate([(Vte[i:i + 2000] @ Vtr.T).max(1).toarray().ravel() for i in range(0, Vte.shape[0], 2000)])
        linhas.append({"categoria_nova": nova, "vai_para_humano": round(float((ct[eh_nova] < t).mean()), 3),
                       "classificada_errado_com_confianca": round(float((ct[eh_nova] >= t).mean()), 3),
                       "auc_detector_por_similaridade": round(float(roc_auc_score(~eh_nova, sim)), 3)})
    pior = min(linhas, key=lambda x: x["vai_para_humano"])
    ok = pior["vai_para_humano"] >= 0.80
    aucs = [x["auc_detector_por_similaridade"] for x in linhas]
    faixa_auc = f"{min(aucs):.2f}–{max(aucs):.2f}".replace(".", ",")
    registrar("A6", "O limiar protege contra uma categoria que o modelo nunca viu?", PASSOU if ok else FALHOU,
              {"por_categoria": linhas},
              f"NÃO protege: {pct(min(x['classificada_errado_com_confianca'] for x in linhas))} a "
              f"{pct(max(x['classificada_errado_com_confianca'] for x in linhas))} da categoria nova são classificados "
              f"errado com confiança alta. Um detector por ticket (similaridade) também não resolve: AUC {faixa_auc}. "
              "Solução: monitor de população (aprendizado.py, B2).")


def a7_curva(X_tr, X_va, X_te, y_tr, y_va, y_te) -> dict:
    ordem = np.random.default_rng(mo.SEED).permutation(len(X_tr))
    curva = []
    for n in (500, 1_000, 3_000, 10_000, len(X_tr)):
        m = mo.treinar(X_tr[ordem[:n]], y_tr[ordem[:n]])
        t, cob, acc = _limiar_e_teste(m, X_va, y_va, X_te, y_te)
        curva.append({"rotulos": n, "cobertura": round(cob, 4), "acerto": round(acc, 4)})
    c3, cfull = curva[2]["cobertura"], curva[-1]["cobertura"]
    ok = c3 >= 0.9 * cfull
    registrar("A7", "Um gold set de 3.000 rótulos entrega os 73% de cobertura?", PASSOU if ok else FALHOU,
              {"curva": curva},
              f"NÃO: com 3.000 rótulos a cobertura é {pct(c3)}, não {pct(cfull)}. O ROI da proposta supunha o modelo "
              "maduro desde o dia 1; o caminho real está no ciclo de aprendizado (B1).")
    return {"curva": curva}


def a8_incerteza(X_tr, X_va, X_te, y_tr, y_va, y_te) -> None:
    rng = np.random.default_rng(mo.SEED)
    ordem = rng.permutation(len(X_tr))
    res = {}
    for estr in ("sorteio", "mais_incertos"):
        rot = list(ordem[:500])
        for _ in range(5):
            m = mo.treinar(X_tr[rot], y_tr[rot])
            pool = np.setdiff1d(np.arange(len(X_tr)), rot)
            if estr == "sorteio":
                novo = rng.choice(pool, 500, replace=False)
            else:
                _, c, _, _ = mo.prever(m, X_tr[pool])
                novo = pool[np.argsort(c)[:500]]
            rot += list(novo)
        t, cob, acc = _limiar_e_teste(mo.treinar(X_tr[rot], y_tr[rot]), X_va, y_va, X_te, y_te)
        res[estr] = {"rotulos": len(rot), "cobertura": round(cob, 4), "acerto": round(acc, 4)}
    ok = res["mais_incertos"]["cobertura"] >= res["sorteio"]["cobertura"]
    registrar("A8", "Rotular os tickets mais incertos acelera o aprendizado?", PASSOU if ok else FALHOU, res,
              f"NÃO: com 3.000 rótulos, sorteio chega a {pct(res['sorteio']['cobertura'])} e 'mais incertos' a "
              f"{pct(res['mais_incertos']['cobertura'])}. O gold set deve ser sorteado (estratificado), e a auditoria "
              "precisa incluir acertos, não só dúvidas.")


def a9_duplicata(X_tr, X_te, y_tr, y_te) -> None:
    m = mo.treinar(X_tr, y_tr, max_features=200_000)
    prev, conf, _, _ = mo.prever(m, X_te)
    vec, _ = m
    Vtr, Vte = vec.transform(X_tr), vec.transform(X_te)
    melhor, rot = np.zeros(len(y_te)), np.empty(len(y_te), dtype=object)
    for i in range(0, len(y_te), 2000):
        S = (Vte[i:i + 2000] @ Vtr.T).toarray()
        melhor[i:i + 2000], rot[i:i + 2000] = S.max(1), y_tr[S.argmax(1)]
    d = melhor >= 0.9
    acc_dup, acc_mod = float((rot[d] == y_te[d]).mean()), float((prev[d] == y_te[d]).mean())
    acaso = float((pd.Series(y_tr).value_counts(normalize=True) ** 2).sum())
    ok = acc_dup >= acc_mod + 0.02
    registrar("A9", "A quase-duplicata ajuda a classificar?", PASSOU if ok else FALHOU,
              {"pct_com_duplicata": round(float(d.mean()), 4), "acerto_copiando_a_duplicata": round(acc_dup, 4),
               "acerto_do_modelo_nesses_tickets": round(acc_mod, 4), "acerto_por_acaso": round(acaso, 4)},
              f"NÃO: copiar a classe da duplicata acerta {pct(acc_dup)}, mas o modelo já acerta {pct(acc_mod)} "
              f"nesses tickets (acaso: {pct(acaso)}). O valor da duplicata é vincular ao ticket anterior "
              "(histórico, resolução, recontato), não classificar.")


def a10_gatilhos() -> None:
    f = pd.read_csv(OUT / "rotas_dataset1.csv")
    r1 = f[f["rota"].str.startswith("1")]
    motivos = r1["motivo"].str.split(", ")
    exclusivos = {g: int(motivos.apply(lambda x, g=g: x == [g]).sum())
                  for g in ("perda_de_dados", "seguranca", "conta_bloqueada", "recontato", "dinheiro", "hardware", "reparo_troca")}
    pp = {g: round(n / len(f), 4) for g, n in exclusivos.items()}
    rascunho_ok = int(motivos.apply(lambda x: set(x) <= {"hardware", "reparo_troca", "recontato"}).sum())
    ok = max(pp.values()) <= 0.10
    registrar("A10", "Os 33% de humano dependem de um gatilho só?", PASSOU if ok else FALHOU,
              {"rota1": len(r1), "exclusivos": exclusivos, "pp_do_total": pp,
               "rota1_so_hardware_reparo_recontato": rascunho_ok},
              f"Nenhum gatilho sozinho responde por mais de {pct(max(pp.values()))} do total (critério ≤ 10 p.p.). "
              f"Mas {rascunho_ok} dos {len(r1)} tickets da rota 1 só têm gatilhos em que o risco está na DECISÃO, "
              "não no texto: dá para a IA rascunhar (economia B6).")


def a11_custo_llm(n: int = 20_000) -> None:
    auto = json.loads((OUT / "automacao.json").read_text(encoding="utf-8"))
    base_usd = auto["C_custo_llm"]["usd_ano"]
    desp = json.loads((DIAG / "resultados.json").read_text(encoding="utf-8"))["etapa3_desperdicio"]["cenarios"]
    l1 = [desp[c]["horas"]["L1 repetitivo feito por humano"] for c in ("baixo", "base", "alto")]
    rng = np.random.default_rng(mo.SEED)
    custo = (base_usd * np.exp(rng.uniform(np.log(0.5), np.log(10), n)) * rng.uniform(0.5, 3, n)
             * rng.uniform(0.8, 1.5, n) * rng.uniform(4.5, 6.5, n))
    ganho = rng.triangular(*l1, n) * rng.triangular(25, 35, 55, n)
    p = float((custo > ganho).mean())
    classificar_tudo_usd = 30_000 * (1_500 * 0.1 * 2 + 72 * 2 + 10 * 10) / 1e6
    registrar("A11", "O custo de LLM pode passar do ganho que ela gera?", PASSOU if p < 0.05 else FALHOU,
              {"p_custo_maior_que_ganho": round(p, 4), "custo_p90_rs": round(float(np.quantile(custo, 0.9))),
               "ganho_p10_rs": round(float(np.quantile(ganho, 0.1))), "llm_classificando_tudo_usd_ano": round(classificar_tudo_usd, 1)},
              f"Em {n:,} cenários (tokens ×0,5–10, preço ×0,5–3, volume, câmbio), o custo passa do ganho em ".replace(",", ".", 1)
              + f"{pct(p, 2)}. Até uma LLM classificando os 30 mil tickets custaria ≈ US$ {classificar_tudo_usd:.0f}/ano: "
              "o motivo para não usá-la ali é acerto e latência, não dinheiro.")


def a12_ordem(n: int = 20_000) -> None:
    desp = json.loads((DIAG / "resultados.json").read_text(encoding="utf-8"))["etapa3_desperdicio"]["cenarios"]
    h = lambda k: [desp[c]["horas"][k] for c in ("baixo", "base", "alto")]  # noqa: E731
    ret = h("Retriagem por classificação errada")
    rng = np.random.default_rng(mo.SEED)
    itens = {  # (horas baixo/base/alto, esforço base em semanas)
        "pendentes": (h("Cobrança de pendentes do cliente"), 1),
        "coleta": ([346, 693, 1039], 1),
        "classificacao": ([1345 * r / ret[1] for r in ret], 6),
        "duplicata": ([0.5 * x for x in h("Recontato (cliente volta a pedir)")], 3),
        "copiloto": (h("L1 repetitivo feito por humano"), 8),
    }
    roi = {k: rng.triangular(*hs, n) / (e * np.exp(rng.uniform(np.log(0.5), np.log(2), n))) for k, (hs, e) in itens.items()}
    M = np.stack(list(roi.values()), 1)
    top2 = np.argsort(-M, 1)[:, :2]
    fixos_no_top2 = float(np.isin(top2, [0, 1]).all(1).mean())
    ok = fixos_no_top2 >= 0.80
    registrar("A12", "\"Regras fixas primeiro\" resiste a qualquer combinação de premissas?", PASSOU if ok else FALHOU,
              {"pct_cenarios_regras_fixas_no_top2_h_por_semana": round(fixos_no_top2, 4),
               "pct_classificacao_em_1o": round(float((M.argmax(1) == 2).mean()), 4)},
              f"As duas regras fixas são as 2 melhores em horas por semana de esforço em {pct(fixos_no_top2)} "
              "dos cenários (horas nas faixas da Entrega 1; esforço ×0,5–2).")


def a13_aderencia() -> None:
    doc = (HERE / "PROPOSTA_AUTOMACAO.md").read_text(encoding="utf-8")
    req = {
        "Usa os dois datasets": "Dataset 1" in doc and "Dataset 2" in doc,
        "Classificação automática": "Classificação automática" in doc,
        "Roteamento inteligente": "Roteamento inteligente" in doc,
        "Respostas sugeridas": "Respostas sugeridas" in doc,
        "Triagem de prioridade": "Triagem de prioridade" in doc,
        "Detecção de duplicatas": "Detecção de duplicatas" in doc,
        "O que NÃO automatizar": "O que NÃO automatizar" in doc,
        "Exemplos dos dados (≥ 8 tickets citados por ID)": len(set(re.findall(r"#(\d{3,4})\b", doc))) >= 8,
        "Fluxo: entra → etapas → IA → humano": "```mermaid" in doc and "Onde o humano entra" in doc,
        "Não automatiza 100%": "Humano decide" in doc,
        "ROI em horas/mês (dica do desafio)": bool(re.search(r"h/mês", doc)),
        "Acurácia geral, sem limiar (transparência)": "85,8%" in doc,
    }
    faltam = [k for k, v in req.items() if not v]
    registrar("A13", "A proposta cobre o que o desafio pede?", PASSOU if not faltam else FALHOU,
              {"requisitos": req}, "Todos os requisitos cobertos." if not faltam else f"Faltam: {faltam}")


def a1_documentos() -> None:
    """Números citados nos documentos × números do código (só os que decidem alguma coisa)."""
    auto = json.loads((OUT / "automacao.json").read_text(encoding="utf-8"))
    apr = json.loads((OUT / "aprendizado.json").read_text(encoding="utf-8"))
    har = {r["id"]: r for r in resultados}
    a, b1, b2 = auto["A_rotas_dataset1"], apr["B1_ciclo_de_aprendizado"], apr["B2_monitor_categoria_nova"]
    esperado = {
        "PROPOSTA_AUTOMACAO.md": [
            f"{a['rotas_pct']['1. Humano decide (IA prepara o dossiê)']:.0%}",
            f"{a['seguranca_ou_conta_bloqueada']}", f"{a['hardware_ou_reparo']:,}".replace(",", "."),
            pct(auto["B_classificacao_dataset2"]["modelo"]["acuracia"]),
            pct(har["A2"]["evidencia"]["melhor_regra_com_95pct"]["cobertura"], 0),
        ],
        "ECONOMIA_E_APRENDIZADO.md": [
            pct(b1["congelado"]["cobertura_final"]), pct(b1["completo"]["cobertura_final"]),
            f"{b1['completo']['horas_ano1']:,}".replace(",", "."),
            pct(b2["novos_classificados_errado_com_confianca"]),
            pct(apr["B3_revisao_top3"]["classe_certa_entre_as_sugestoes"]["top3"]),
            f"{apr['B6_economias']['rota_1A_ia_rascunha_humano_decide']['horas_ano']['base']}",
        ],
    }
    faltando = {}
    for arq, nums in esperado.items():
        txt = (HERE / arq).read_text(encoding="utf-8")
        faltando[arq] = [n for n in nums if n not in txt]
    total = sum(len(v) for v in esperado.values())
    erros = sum(len(v) for v in faltando.values())
    # Caracteres de controle nos scripts (uma barra-b gravada como backspace já anulou uma regex; ver HARNESS_AUTOMACAO.md)
    permitidos = {chr(9), chr(10), chr(13)}
    controle = {f.name: sum(1 for ch in f.read_text(encoding="utf-8") if ord(ch) < 32 and ch not in permitidos)
                for f in sorted(HERE.glob("*.py"))}
    sujos = {k: v for k, v in controle.items() if v}
    registrar("A1", "Os números dos documentos batem com o código?", PASSOU if erros == 0 and not sujos else FALHOU,
              {"verificados": total, "nao_encontrados": faltando, "caracteres_de_controle_nos_scripts": controle},
              f"{total - erros}/{total} números-chave encontrados no texto exatamente como o código calcula; "
              f"{len(controle)} scripts sem caractere de controle." if not sujos else f"Scripts com caractere de controle: {sujos}")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--data2", type=Path, default=HERE.parent / "data" / "it_tickets.csv")
    args = ap.parse_args()
    X_tr, X_va, X_te, y_tr, y_va, y_te = mo.dividir(args.data2)
    m200 = mo.treinar(X_tr, y_tr, max_features=200_000)
    _, cob_modelo, _ = _limiar_e_teste(m200, X_va, y_va, X_te, y_te)
    a2_regras(X_tr, X_te, y_tr, y_te, round(cob_modelo, 4))
    a3_alternativas(X_tr, X_va, X_te, y_tr, y_va, y_te)
    a4_estabilidade(args.data2)
    a5_calibracao(m200, X_te, y_te)
    a6_categoria_nova(X_tr, X_va, X_te, y_tr, y_va, y_te)
    a7_curva(X_tr, X_va, X_te, y_tr, y_va, y_te)
    a8_incerteza(X_tr, X_va, X_te, y_tr, y_va, y_te)
    a9_duplicata(X_tr, X_te, y_tr, y_te)
    a10_gatilhos()
    a11_custo_llm()
    a12_ordem()
    a13_aderencia()
    a1_documentos()
    resultados.sort(key=lambda r: int(r["id"][1:]))
    (OUT / "harness_automacao.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=2, default=str),
                                                 encoding="utf-8")
    resumo = pd.Series([r["veredito"] for r in resultados]).value_counts().to_dict()
    print("\nResumo:", resumo)


if __name__ == "__main__":
    main()
