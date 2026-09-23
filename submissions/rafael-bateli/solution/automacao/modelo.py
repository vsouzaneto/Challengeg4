"""Código comum de classificação, usado por aprendizado.py e harness_automacao.py.

Uma fonte só para divisão dos dados, treino, previsão e escolha do limiar
(lição da Entrega 1: dois códigos para o mesmo número geram dois números).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

SEED = 42
ALVO = 0.95  # acurácia mínima exigida acima do limiar
LIMIARES = np.round(np.arange(0.30, 0.995, 0.005), 3)
# 50 mil variáveis: mesmo resultado das 200 mil da Entrega 1 com metade do tempo
# de treino (medido no harness A3). É o tamanho usado nas simulações.
MAX_FEATURES = 50_000


def dividir(caminho2: Path, seed: int = SEED):
    """Treino 60% / validação 20% / teste 20%, estratificado (mesma divisão da Entrega 1)."""
    d = pd.read_csv(caminho2)
    X_tmp, X_te, y_tmp, y_te = train_test_split(d["Document"], d["Topic_group"], test_size=0.2,
                                                random_state=seed, stratify=d["Topic_group"])
    X_tr, X_va, y_tr, y_va = train_test_split(X_tmp, y_tmp, test_size=0.25, random_state=seed, stratify=y_tmp)
    return (X_tr.to_numpy(), X_va.to_numpy(), X_te.to_numpy(),
            y_tr.to_numpy(), y_va.to_numpy(), y_te.to_numpy())


def treinar(X, y, max_features: int = MAX_FEATURES, clf=None):
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, max_features=max_features)
    clf = clf if clf is not None else LogisticRegression(max_iter=1000, C=5)
    clf.fit(vec.fit_transform(X), y)
    return vec, clf


def prever(modelo, X):
    """Devolve (classe prevista, confiança, matriz de probabilidades, classes)."""
    vec, clf = modelo
    P = clf.predict_proba(vec.transform(X))
    return clf.classes_[P.argmax(1)], P.max(1), P, clf.classes_


def escolher_limiar(conf, prev, y, alvo: float = ALVO) -> float:
    """Menor limiar em que a acurácia acima dele atinge o alvo. Escolhido sempre na VALIDAÇÃO."""
    for t in LIMIARES:
        m = conf >= t
        if m.any() and (prev[m] == y[m]).mean() >= alvo:
            return float(t)
    return float(LIMIARES[-1])


def cobertura_e_acerto(modelo, limiar, X, y) -> tuple[float, float]:
    prev, conf, _, _ = prever(modelo, X)
    auto = conf >= limiar
    return float(auto.mean()), float((prev[auto] == y[auto]).mean())


def horas_retriagem(cobertura: float, acerto_auto: float) -> float:
    """Horas/ano líquidas recuperadas na retriagem: mesma fórmula e premissas de triagem_ia.py (Entrega 1)."""
    tickets, incoerencia_hoje, retriagem_min = 30_000, 0.654, 5
    acerto_humano_revisando, revisao_min = 0.90, 1.0
    erro = cobertura * (1 - acerto_auto) + (1 - cobertura) * (1 - acerto_humano_revisando)
    hoje = tickets * incoerencia_hoje * retriagem_min / 60
    depois = tickets * erro * retriagem_min / 60
    revisao = tickets * (1 - cobertura) * revisao_min / 60
    return hoje - depois - revisao
