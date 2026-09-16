"""Curva de aprendizado do classificador do script 04 em fatias do treino.

Mesmo split (split_treino.csv / split_teste.csv), mesmo TF-IDF e regressão logística, semente 42.
Só imprime; saída em solution/08_curva_aprendizado.txt. Nenhum CSV gravado.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

SEED = 42
FRACOES = [0.10, 0.20, 0.40, 0.60, 0.80, 1.00]
CLASSE_FOCO = "Administrative rights"
VOLUME_ANUAL = 30_000        # enunciado
SEMANAS_POR_ANO = 52         # premissa minha
AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "data"
DERIVADOS = DADOS / "derived"
SAIDA = AQUI / "08_curva_aprendizado.txt"


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


def main():
    sys.stdout = Tee(SAIDA)
    pd.set_option("display.width", 200)

    print("AVISO: exemplo sorteado do treino não equivale a correção de erro em produção. Reversão humana chega "
          "concentrada nos casos em que o modelo errou ou absteve, e rótulo de fila operacional tem ruído que o "
          "dataset de treino não tem. A conversão em semanas supõe que toda reversão vira rótulo e que rótulo novo "
          "vale o mesmo que exemplo sorteado; a estimativa é piso, não previsão.\n")

    tk = pd.read_csv(DADOS / "all_tickets_processed_improved_v3.csv")
    idx_tr = pd.read_csv(DERIVADOS / "split_treino.csv")["indice_original"].values
    idx_te = pd.read_csv(DERIVADOS / "split_teste.csv")["indice_original"].values
    X_tr_full, y_tr_full = tk.loc[idx_tr, "Document"].fillna(""), tk.loc[idx_tr, "Topic_group"]
    X_te, y_te = tk.loc[idx_te, "Document"].fillna(""), tk.loc[idx_te, "Topic_group"]
    fracao_classe = (tk["Topic_group"] == CLASSE_FOCO).mean()   # dataset
    print(f"treino completo: {len(X_tr_full)}; teste: {len(X_te)}; "
          f"{CLASSE_FOCO} no treino completo: {(y_tr_full == CLASSE_FOCO).sum()}, no teste: {(y_te == CLASSE_FOCO).sum()}")

    linhas = []
    for frac in FRACOES:
        if frac < 1.0:
            X_f, _, y_f, _ = train_test_split(X_tr_full, y_tr_full, train_size=frac,
                                              stratify=y_tr_full, random_state=SEED)
        else:
            X_f, y_f = X_tr_full, y_tr_full
        modelo = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2)),
            ("clf", LogisticRegression(max_iter=1000, random_state=SEED)),
        ]).fit(X_f, y_f)
        pred = modelo.predict(X_te)
        linhas.append({
            "fração": frac,
            "n treino": len(X_f),
            f"n {CLASSE_FOCO}": int((y_f == CLASSE_FOCO).sum()),
            "acurácia": accuracy_score(y_te, pred),
            "F1 macro": f1_score(y_te, pred, average="macro"),
            f"recall {CLASSE_FOCO}": recall_score(y_te, pred, labels=[CLASSE_FOCO], average=None)[0],
            f"F1 {CLASSE_FOCO}": f1_score(y_te, pred, labels=[CLASSE_FOCO], average=None)[0],
        })
        print(f"  fatia {frac:.0%} treinada", file=sys.stderr)
    tab = pd.DataFrame(linhas)
    print("\ncurva de aprendizado (fatias estratificadas independentes do treino, semente 42; métricas no teste):")
    print(tab.round(4).to_string(index=False))

    print(f"\nestimativa a partir dos dois últimos pontos ({FRACOES[-2]:.0%} e {FRACOES[-1]:.0%}):")
    a, b = tab.iloc[-2], tab.iloc[-1]
    d_n = b[f"n {CLASSE_FOCO}"] - a[f"n {CLASSE_FOCO}"]
    d_recall_pontos = (b[f"recall {CLASSE_FOCO}"] - a[f"recall {CLASSE_FOCO}"]) * 100
    print(f"exemplos adicionais de {CLASSE_FOCO}: {d_n}; variação de recall: {d_recall_pontos:+.2f} pontos")
    volume_classe_ano = fracao_classe * VOLUME_ANUAL
    volume_classe_semana = volume_classe_ano / SEMANAS_POR_ANO
    print(f"volume da classe: fração {fracao_classe:.4f} no dataset × {VOLUME_ANUAL} tickets/ano (enunciado) "
          f"= {volume_classe_ano:.0f}/ano = {volume_classe_semana:.1f}/semana")
    if d_recall_pontos > 0:
        ex_por_ponto = d_n / d_recall_pontos
        semanas = ex_por_ponto / volume_classe_semana
        print(f"exemplos por ponto de recall: {ex_por_ponto:.0f}; "
              f"semanas por ponto de recall se toda reversão humana virar rótulo: {semanas:.1f} (piso)")
    else:
        print("variação de recall não positiva entre os dois últimos pontos; exemplos por ponto de recall "
              "não é definido neste trecho da curva")

    print(f"\nsaída gravada em {SAIDA.relative_to(AQUI.parent)}")


if __name__ == "__main__":
    main()
