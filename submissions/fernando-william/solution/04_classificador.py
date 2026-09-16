"""Classificador de Topic_group com deduplicação, abstenção e teste fora de domínio.

Uso:
    python solution/04_classificador.py              # relatório em solution/04_classificador.txt
    python solution/04_classificador.py --limiar X   # idem, e grava cobertura.json e modelo.joblib

Semente 42 em tudo que sorteia. Só imprime números; não interpreta.
"""

import argparse
import json
import re
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline

SEED = 42
AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "data"
DERIVADOS = DADOS / "derived"
SAIDA = AQUI / "04_classificador.txt"
RELATORIO_01 = AQUI / "01_auditoria_dados.txt"
LIMIAR_DEDUP = 0.9
LIMIARES = np.round(np.arange(0.50, 0.951, 0.05), 2)


class Tee:
    def __init__(self, caminho):
        self.arq = open(caminho, "w", encoding="utf-8")
        self.term = sys.stdout

    def write(self, s):
        self.arq.write(s)
        self.term.write(s)

    def flush(self):
        self.arq.flush()
        self.term.flush()


def secao(n, titulo):
    print(f"\n=== {n}. {titulo} ===")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limiar", type=float, default=None)
    args = parser.parse_args()

    sys.stdout = Tee(SAIDA)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 50)
    DERIVADOS.mkdir(exist_ok=True)

    tk = pd.read_csv(DADOS / "all_tickets_processed_improved_v3.csv")
    doc = tk["Document"].fillna("")
    rotulo = tk["Topic_group"]

    # ------------------------------------------------------------- 1. dedup
    secao(1, f"deduplicação por similaridade (cosseno TF-IDF > {LIMIAR_DEDUP}, vizinho mais próximo)")
    X_all = TfidfVectorizer().fit_transform(doc)
    nn = NearestNeighbors(n_neighbors=2, metric="cosine", n_jobs=-1).fit(X_all)
    dist, idx = nn.kneighbors(X_all)
    sim = 1 - dist[:, 1]
    viz = idx[:, 1]
    liga = sim > LIMIAR_DEDUP
    n = len(doc)
    grafo = coo_matrix((np.ones(liga.sum()), (np.where(liga)[0], viz[liga])), shape=(n, n))
    n_grupos, comp = connected_components(grafo, directed=False)
    tamanhos = np.bincount(comp)
    representante = pd.Series(np.arange(n)).groupby(comp).min().values
    manter = np.zeros(n, dtype=bool)
    manter[representante] = True
    print(f"linhas originais: {n}; documentos com vizinho > {LIMIAR_DEDUP}: {liga.sum()}")
    print(f"grupos (componentes conexos): {n_grupos}; grupos com mais de 1 documento: {(tamanhos > 1).sum()}; "
          f"maior grupo: {tamanhos.max()}")
    print(f"linhas removidas: {n - manter.sum()}; linhas mantidas: {manter.sum()}")
    grupos_mistos = pd.DataFrame({"comp": comp, "rotulo": rotulo}).groupby("comp")["rotulo"].nunique()
    print(f"grupos com mais de um rótulo: {(grupos_mistos > 1).sum()}")
    tk_d = tk[manter]
    doc_d = doc[manter]
    rot_d = rotulo[manter]
    print("classes após dedup:")
    print(pd.DataFrame({"antes": rotulo.value_counts(), "depois": rot_d.value_counts()}).to_string())

    # ------------------------------------------------------------- 2. split
    secao(2, "split estratificado 80/20 sobre o que sobrou")
    X_tr, X_te, y_tr, y_te = train_test_split(
        doc_d, rot_d, test_size=0.2, stratify=rot_d, random_state=SEED)
    arq_split = DERIVADOS / "split_teste.csv"
    arq_treino = DERIVADOS / "split_treino.csv"
    pd.DataFrame({"indice_original": X_te.index}).to_csv(arq_split, index=False)
    pd.DataFrame({"indice_original": X_tr.index}).to_csv(arq_treino, index=False)
    print(f"treino: {len(X_tr)}; teste: {len(X_te)}; índices em {arq_split.relative_to(AQUI.parent)} "
          f"e {arq_treino.relative_to(AQUI.parent)}")

    # ------------------------------------------------------------- 3. modelo
    secao(3, "TF-IDF (1-2gramas, min_df 2) + regressão logística")
    modelo = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2)),
        ("clf", LogisticRegression(max_iter=1000, random_state=SEED)),
    ])
    modelo.fit(X_tr, y_tr)
    classes = list(modelo.classes_)
    proba = modelo.predict_proba(X_te)
    pred = np.array(classes)[proba.argmax(axis=1)]
    prob_max = proba.max(axis=1)
    acc = accuracy_score(y_te, pred)
    maj = y_tr.value_counts().idxmax()
    print(f"vocabulário: {len(modelo.named_steps['tfidf'].vocabulary_)}")
    print(f"acurácia global: {acc:.4f}; classe majoritária '{maj}': {(y_te == maj).mean():.4f}")
    print(classification_report(y_te, pred, digits=4))
    cm = confusion_matrix(y_te, pred, labels=classes)
    print("matriz de confusão (linhas = real, colunas = previsto):")
    print(pd.DataFrame(cm, index=classes, columns=classes).to_string())
    acc_01 = None
    if RELATORIO_01.exists():
        m = re.search(r"acurácia global: ([0-9.]+)", RELATORIO_01.read_text(encoding="utf-8"))
        acc_01 = float(m.group(1)) if m else None
    if acc_01 is None:
        print("acurácia do script 01 sem dedup: não encontrada em 01_auditoria_dados.txt")
    else:
        print(f"acurácia do script 01 sem dedup: {acc_01:.4f}; com dedup: {acc:.4f}; "
              f"diferença: {acc - acc_01:+.4f}")

    # ------------------------------------------------------------- 4. abstenção
    secao(4, "abstenção por limiar de probabilidade máxima")
    y_te_v = y_te.values
    linhas = []
    for lim in LIMIARES:
        decide = prob_max >= lim
        linha = {"limiar": lim, "cobertura": decide.mean(),
                 "acuracia_decididos": accuracy_score(y_te_v[decide], pred[decide]) if decide.any() else np.nan}
        for c in classes:
            da_classe = y_te_v == c
            dec_c = da_classe & decide
            linha[f"acc_{c}"] = (pred[dec_c] == c).mean() if dec_c.any() else np.nan
            linha[f"fila_{c}"] = 1 - dec_c.sum() / da_classe.sum()
        linhas.append(linha)
    curva = pd.DataFrame(linhas)
    arq_curva = DERIVADOS / "curva_abstencao.csv"
    curva.to_csv(arq_curva, index=False)
    print("cobertura e acurácia sobre os decididos:")
    print(curva[["limiar", "cobertura", "acuracia_decididos"]].round(4).to_string(index=False))
    print("\nacurácia por classe sobre os decididos:")
    print(curva[["limiar"] + [f"acc_{c}" for c in classes]].round(4)
          .rename(columns=lambda c: c.replace("acc_", "")).to_string(index=False))
    print("\nfração de cada classe que vai para fila humana:")
    print(curva[["limiar"] + [f"fila_{c}" for c in classes]].round(4)
          .rename(columns=lambda c: c.replace("fila_", "")).to_string(index=False))
    print(f"curva salva em {arq_curva.relative_to(AQUI.parent)}")

    # ------------------------------------------------------------- 5. fora de domínio
    secao(5, "fora de domínio: Ticket Description do primeiro arquivo com placeholder substituído")
    cs = pd.read_csv(DADOS / "customer_support_tickets.csv")
    desc = [d.replace("{product_purchased}", p) for d, p in
            zip(cs["Ticket Description"].fillna(""), cs["Product Purchased"].fillna(""))]
    proba_ood = modelo.predict_proba(desc)
    pm_ood = proba_ood.max(axis=1)
    pred_ood = np.array(classes)[proba_ood.argmax(axis=1)]
    print(f"n={len(desc)}; probabilidade máxima: média {pm_ood.mean():.4f}, "
          + ", ".join(f"q{int(q*100)} {np.quantile(pm_ood, q):.4f}" for q in (0.05, 0.25, 0.5, 0.75, 0.95)))
    print(f"comparação, probabilidade máxima no teste em domínio: média {prob_max.mean():.4f}, "
          + ", ".join(f"q{int(q*100)} {np.quantile(prob_max, q):.4f}" for q in (0.05, 0.25, 0.5, 0.75, 0.95)))
    print("fração abaixo de cada limiar (fora de domínio vs. teste em domínio):")
    print(pd.DataFrame({
        "limiar": LIMIARES,
        "fora_dominio": [(pm_ood < lim).mean() for lim in LIMIARES],
        "teste_dominio": [(prob_max < lim).mean() for lim in LIMIARES],
    }).round(4).to_string(index=False))
    print("classe prevista fora de domínio:")
    print(pd.Series(pred_ood).value_counts().to_string())

    # ------------------------------------------------------------- 6. limiar escolhido
    if args.limiar is not None:
        secao(6, f"limiar escolhido: {args.limiar}")
        lim = args.limiar
        decide = prob_max >= lim
        cobertura = {
            "limiar": lim,
            "cobertura": float(decide.mean()),
            "acuracia": float(accuracy_score(y_te_v[decide], pred[decide])),
            "acuracia_por_classe": {
                c: float((pred[(y_te_v == c) & decide] == c).mean()) for c in classes
            },
            "n_teste": int(len(y_te_v)),
            "n_decididos": int(decide.sum()),
        }
        arq_cob = DERIVADOS / "cobertura.json"
        arq_cob.write_text(json.dumps(cobertura, ensure_ascii=False, indent=2), encoding="utf-8")
        arq_modelo = DERIVADOS / "modelo.joblib"
        joblib.dump(modelo, arq_modelo)
        print(json.dumps(cobertura, ensure_ascii=False, indent=2))
        print(f"gravados {arq_cob.relative_to(AQUI.parent)} e {arq_modelo.relative_to(AQUI.parent)}")

    print(f"\nsaída gravada em {SAIDA.relative_to(AQUI.parent)}")


if __name__ == "__main__":
    main()
