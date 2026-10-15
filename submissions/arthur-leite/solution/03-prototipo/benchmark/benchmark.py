"""
Benchmark dos classificadores no Dataset 2 + definição das faixas de automação.

  A  TF-IDF (1-2 gramas) + regressão logística
  B  embeddings MiniLM + regressão logística   (requer data/cache/ds2_minilm.npy -> embed_ds2.py)
  C  LLM Gemini zero-shot / few-shot           (requer data/cache/llm_*.jsonl     -> llm_classify.py)

Divisão: os mesmos 20% de teste usados em todo o projeto (random_state=42). Os 80% restantes
viram treino (70% do total) e validação (10% do total). Os limiares de confiança são escolhidos
na VALIDAÇÃO e medidos no TESTE, para não superestimar o resultado.

Saídas em outputs/: benchmark.md, faixas.json e a curva cobertura × precisão (csv).
Uso: python benchmark.py
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")  # Windows: evita erro de cp1252 com saída redirecionada
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[3]
CACHE = ROOT / "data/cache"
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)

# Faixas de automação: precisão mínima exigida em cada faixa (decisão de negócio, não técnica)
PRECISAO_AUTO = 0.95      # roteia sozinho: erra no máximo 1 em 20
TOP2_SUGERE = 0.90        # mostra as 2 categorias mais prováveis; humano escolhe com 1 clique


def dividir():
    d = pd.read_csv(ROOT / "data/ds2_it_tickets/all_tickets_processed_improved_v3.csv")
    resto, te = train_test_split(d, test_size=0.2, stratify=d["Topic_group"], random_state=42)
    tr, va = train_test_split(resto, test_size=0.125, stratify=resto["Topic_group"], random_state=42)
    return d, tr, va, te


def limiar_para_precisao(conf: np.ndarray, acerto: np.ndarray, alvo: float) -> float:
    """Menor limiar de confiança cujos tickets acima dele têm precisão >= alvo (na validação)."""
    ordem = np.argsort(-conf)
    prec_acum = np.cumsum(acerto[ordem]) / np.arange(1, len(conf) + 1)
    ok = np.where(prec_acum >= alvo)[0]
    if len(ok) == 0:
        return 1.01
    return float(conf[ordem][ok.max()])


def limiar_faixa_media(conf: np.ndarray, acerto: np.ndarray, teto: float, alvo: float) -> float:
    """Menor limiar t tal que os tickets com confiança em [t, teto) tenham precisão >= alvo.
    Mede a precisão DENTRO da faixa: a acumulada seria inflada pelos tickets de alta confiança."""
    dentro = conf < teto
    c, a = conf[dentro], acerto[dentro]
    ordem = np.argsort(-c)
    prec_acum = np.cumsum(a[ordem]) / np.arange(1, len(c) + 1)
    ok = np.where(prec_acum >= alvo)[0]
    return float(c[ordem][ok.max()]) if len(ok) else teto


def faixas(conf_va, acerto_va, top2_va, conf_te, acerto_te, top2_te) -> dict:
    t_auto = limiar_para_precisao(conf_va, acerto_va, PRECISAO_AUTO)
    t_sug = limiar_faixa_media(conf_va, top2_va, t_auto, TOP2_SUGERE)
    r = {"limiar_auto": round(t_auto, 4), "limiar_sugere": round(t_sug, 4)}
    for nome, m in [("auto", conf_te >= t_auto),
                    ("sugere", (conf_te >= t_sug) & (conf_te < t_auto)),
                    ("humano", conf_te < t_sug)]:
        r[nome] = {"cobertura": round(float(m.mean()), 4),
                   "precisao": round(float(acerto_te[m].mean()), 4) if m.any() else None,
                   "top2": round(float(top2_te[m].mean()), 4) if m.any() else None}
    return r


def curva(conf, acerto) -> pd.DataFrame:
    linhas = []
    for t in np.linspace(0, 0.99, 100):
        m = conf >= t
        linhas.append({"limiar": round(t, 2), "cobertura": m.mean(),
                       "precisao": acerto[m].mean() if m.any() else np.nan})
    return pd.DataFrame(linhas)


def pt_br(linhas: list[str]) -> list[str]:
    """Números no padrão brasileiro (33.485 e 0,860), sem tocar em nomes como gemini-3.5-flash nem em blocos de código."""
    import re
    milhar = re.compile(r"(?<=\d),(?=\d{3}(?!\d))")
    decimal = re.compile(r"(?<![\w\-.])(\d+)\.(\d+)(?![\w\-])")
    saida, em_codigo = [], False
    for linha in linhas:
        for parte in linha.split("\n"):
            if parte.startswith("```"):
                em_codigo = not em_codigo
        if not em_codigo and not linha.startswith("```"):
            linha = decimal.sub(r"\1,\2", milhar.sub("§", linha)).replace("§", ".")
        saida.append(linha)
    return saida


def main() -> None:
    d, tr, va, te = dividir()
    res, md = {}, ["# Benchmark de classificadores — Dataset 2", "",
                   f"Treino {len(tr):,} · Validação {len(va):,} · Teste {len(te):,} (estratificado, seed 42)", ""]

    # --- A: TF-IDF + LogReg ---
    t = time.time()
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    clf_a = LogisticRegression(max_iter=3000, C=5).fit(vec.fit_transform(tr["Document"]), tr["Topic_group"])
    treino_a = time.time() - t
    t = time.time()
    proba_te_a = clf_a.predict_proba(vec.transform(te["Document"]))
    lat_a = (time.time() - t) / len(te) * 1000
    proba_va_a = clf_a.predict_proba(vec.transform(va["Document"]))
    res["A"] = {"nome": "TF-IDF + Regressão Logística", "pred": clf_a.classes_[proba_te_a.argmax(1)],
                "conf_te": proba_te_a.max(1), "conf_va": proba_va_a.max(1),
                "pred_va": clf_a.classes_[proba_va_a.argmax(1)], "treino_s": treino_a, "lat_ms": lat_a,
                "top2": clf_a.classes_[np.argsort(-proba_te_a, 1)[:, :2]],
                "top2_va": clf_a.classes_[np.argsort(-proba_va_a, 1)[:, :2]]}

    # --- B: embeddings + LogReg ---
    emb_path = CACHE / "ds2_minilm.npy"
    if emb_path.exists():
        E = np.load(emb_path)
        t = time.time()
        clf_b = LogisticRegression(max_iter=3000, C=10).fit(E[tr.index], tr["Topic_group"])
        treino_b = time.time() - t
        proba_te_b = clf_b.predict_proba(E[te.index])
        proba_va_b = clf_b.predict_proba(E[va.index])
        res["B"] = {"nome": "Embeddings MiniLM + Regressão Logística", "pred": clf_b.classes_[proba_te_b.argmax(1)],
                    "conf_te": proba_te_b.max(1), "conf_va": proba_va_b.max(1),
                    "pred_va": clf_b.classes_[proba_va_b.argmax(1)], "treino_s": treino_b, "lat_ms": None,
                    "top2": clf_b.classes_[np.argsort(-proba_te_b, 1)[:, :2]],
                    "top2_va": clf_b.classes_[np.argsort(-proba_va_b, 1)[:, :2]]}

    # --- Tabela geral (teste completo) ---
    md += ["## 1. Teste completo", "", "| Modelo | Acurácia | F1-macro | Treino | Latência/ticket |", "|---|---|---|---|---|"]
    for k, r in res.items():
        lat = f"{r['lat_ms']:.2f} ms" if r["lat_ms"] else "ver nota"
        md.append(f"| {k}. {r['nome']} | {accuracy_score(te['Topic_group'], r['pred']):.3f} | "
                  f"{f1_score(te['Topic_group'], r['pred'], average='macro'):.3f} | {r['treino_s']:.0f} s | {lat} |")

    # --- C: LLM na amostra de 400 (comparação justa com A e B na MESMA amostra) ---
    md += ["", "## 2. Amostra de 400 tickets do teste (comparação com LLM)", "",
           "| Modelo | n | Acurácia | F1-macro | Tokens/ticket (entrada+saída) | Segundos/ticket |", "|---|---|---|---|---|---|"]
    # Respostas do LLM: as versionadas (evidência) têm prioridade; o cache local só complementa
    respostas = {a.name: a for a in sorted(CACHE.glob("llm_*.jsonl"))}
    respostas.update({a.name: a for a in sorted((OUT / "llm_respostas").glob("llm_*.jsonl"))})
    for arq in respostas.values():
        L = pd.DataFrame([json.loads(l) for l in arq.read_text(encoding="utf-8").splitlines()]).drop_duplicates("id").set_index("id")
        ids = L.index.intersection(te.index)
        y = te.loc[ids, "Topic_group"]
        validas = L.loc[ids, "pred"].isin(clf_a.classes_).mean()
        tok = ((L["tok_in"] + L["tok_out"]) / L["n_lote"]).mean()
        seg = (L["seg_lote"] / L["n_lote"]).mean()
        nome = arq.stem.replace("llm_", "C. ")
        md.append(f"| {nome} | {len(ids)} | {accuracy_score(y, L.loc[ids, 'pred']):.3f} | "
                  f"{f1_score(y, L.loc[ids, 'pred'], average='macro'):.3f} | {tok:.0f} | {seg:.2f} |")
        for k, r in res.items():
            pos = te.index.get_indexer(ids)
            md.append(f"| {k} na mesma amostra | {len(ids)} | {accuracy_score(y, r['pred'][pos]):.3f} | "
                      f"{f1_score(y, r['pred'][pos], average='macro'):.3f} | 0 | <0,01 |")
        if validas < 1:
            md.append(f"| ↳ respostas fora das categorias válidas | | {1 - validas:.1%} | | | |")

    # --- Referência sem LLM: voto dos 5 vizinhos mais parecidos do treino (o mesmo contexto que o modo rag recebe) ---
    from sklearn.neighbors import NearestNeighbors
    amostra, _ = train_test_split(te, train_size=400, stratify=te["Topic_group"], random_state=7)
    vec_k = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    tr_k = pd.concat([tr, va])  # o modo rag busca vizinhos em todo o conjunto não-teste
    nn = NearestNeighbors(n_neighbors=5, metric="cosine").fit(vec_k.fit_transform(tr_k["Document"]))
    viz = nn.kneighbors(vec_k.transform(amostra["Document"]))[1]
    def votar(rotulos: list[str]) -> str:
        """Maioria; empate resolvido pelo vizinho MAIS PRÓXIMO (a v1 usava ordem alfabética: 73,3% → 76,0%)."""
        contagem = pd.Series(rotulos).value_counts()
        empatados = set(contagem[contagem == contagem.max()].index)
        return next(r for r in rotulos if r in empatados)

    voto = [votar(list(tr_k["Topic_group"].iloc[v])) for v in viz]
    md.append(f"| kNN-5 (voto dos 5 mais parecidos, sem LLM) | {len(amostra)} | {accuracy_score(amostra['Topic_group'], voto):.3f} | "
              f"{f1_score(amostra['Topic_group'], voto, average='macro'):.3f} | 0 | <0,01 |")
    md += ["", "**Notas de método (revisadas pelo agente juiz):**",
           "- O teste do LLM favorece o modelo local: texto já pré-processado (sem sintaxe), categorias dadas só pelo nome e plano gratuito do Gemini.",
           "- `rag` = cada ticket vai ao LLM com os 5 tickets de treino mais parecidos, já rotulados (o melhor cenário testado para o LLM). "
           "Num lote, o LLM devolveu um id truncado (973 em vez de, provavelmente, 9735); a resposta foi descartada (399/400). O LLM não garante devolver os ids intactos.",
           "- O kNN-5 desempata pelo vizinho mais próximo. Ele fica praticamente empatado com o LLM + RAG: o LLM, recebendo o histórico, quase nada acrescenta ao próprio histórico.",
           "- `gemini-3.8-flash` (o modelo mais forte disponível) parou em 200 tickets por cota diária do plano gratuito; o modelo A foi comparado nos mesmos 200.",
           "- Diferenças pareadas (teste de McNemar, mesmos tickets): A × rag → A acerta 53 que o LLM erra e erra 21 que o LLM acerta (p = 0,0003); "
           "A × 3.8-flash → 70 × 7 (p < 10⁻¹³). Os 21 acertos exclusivos do rag sugerem testar o LLM como 'segunda opinião' na faixa de sugestão (não testado).",
           "- As respostas brutas do LLM estão em `outputs/llm_respostas/`."]

    # --- Faixas de automação ---
    md += ["", "## 3. Faixas de automação (limiares escolhidos na validação, medidos no teste)", "",
           "> Esta seção compara A × B com um **limiar global e sem travas**. O motor que roda no protótipo usa limiar por "
           "categoria e travas de domínio: os **números oficiais** (65,5% automático com 96,4% de acerto) estão em `motor_final.md`.", "",
           f"Regra: **auto** quando a 1ª categoria acerta ≥ {PRECISAO_AUTO:.0%}; **sugere** (humano escolhe entre 2) quando a certa está entre as 2 primeiras ≥ {TOP2_SUGERE:.0%}; abaixo disso, **humano** classifica do zero.", "",
           "| Modelo | Limiares (auto / sugere) | Auto: cobertura · precisão | Sugere: cobertura · precisão · top-2 | Humano: cobertura · precisão do modelo |",
           "|---|---|---|---|---|"]
    todas_faixas = {}
    for k, r in res.items():
        y_te, y_va = te["Topic_group"].to_numpy(dtype=object), va["Topic_group"].to_numpy(dtype=object)
        top2 = (r["top2"] == y_te[:, None]).any(1).astype(float)
        top2_va = (r["top2_va"] == y_va[:, None]).any(1).astype(float)
        f = faixas(r["conf_va"], (r["pred_va"] == y_va).astype(float), top2_va,
                   r["conf_te"], (r["pred"] == y_te).astype(float), top2)
        todas_faixas[k] = f
        md.append(f"| {k} | {f['limiar_auto']:.2f} / {f['limiar_sugere']:.2f} | {f['auto']['cobertura']:.1%} · {f['auto']['precisao']:.1%} | "
                  f"{f['sugere']['cobertura']:.1%} · {f['sugere']['precisao']:.1%} · {f['sugere']['top2']:.1%} | "
                  f"{f['humano']['cobertura']:.1%} · {f['humano']['precisao']:.1%} |")
        curva(r["conf_te"], (r["pred"] == y_te).astype(float)).to_csv(OUT / f"curva_{k}.csv", index=False)

    # --- Por classe (melhor modelo local) ---
    melhor = max(res, key=lambda k: f1_score(te["Topic_group"], res[k]["pred"], average="macro"))
    md += ["", f"## 4. Desempenho por categoria — modelo {melhor}", "", "```",
           classification_report(te["Topic_group"], res[melhor]["pred"], digits=3), "```"]
    cm = pd.crosstab(te["Topic_group"], res[melhor]["pred"], rownames=["real"], colnames=["previsto"])
    md += ["", "### Matriz de confusão", "", cm.to_markdown()]

    md = pt_br(md)
    # Não sobrescreve a evidência oficial com uma rodada incompleta (ex.: sem embeddings)
    completo = "B" in res and len(respostas) >= 4
    destino = OUT / ("benchmark.md" if completo else "benchmark_parcial.md")
    if not completo:
        md.insert(1, "> ⚠️ Rodada PARCIAL (faltam embeddings ou respostas do LLM). O resultado oficial está em `benchmark.md`.\n")
    destino.write_text("\n".join(md), encoding="utf-8")
    if completo:
        (OUT / "faixas.json").write_text(json.dumps(todas_faixas, indent=2), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
