"""Classificador do D2 com a MESMA configuração que gerou 73,2% / 95,1% na proposta
(automacao.parte_b e triagem_ia.parte_a): 200 mil variáveis, C=5, max_iter=2000,
limiar escolhido na validação com passo de 0,01. Usa modelo.py para dividir e treinar."""

from __future__ import annotations

import hashlib
import pickle
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegression

from . import config
from .logs import registrar
import modelo as mo  # solution/automacao/modelo.py (no sys.path via config)

MAX_FEATURES = 200_000
LIMIARES = np.round(np.arange(0.30, 0.99, 0.01), 2)  # grade da Entrega 1


@dataclass
class Modelo:
    vec: object
    clf: object
    limiar: float
    classes: np.ndarray
    V_hist: object
    X_hist: np.ndarray
    y_hist: np.ndarray
    X_te: np.ndarray
    y_te: np.ndarray
    sklearn: str
    hash_csv: str


@dataclass
class Previsao:
    classe: str
    confianca: float
    top3: list


def _hash(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()[:16]


def escolher_limiar(conf, prev, y, alvo: float = mo.ALVO) -> float:
    for t in LIMIARES:
        m = conf >= t
        if m.any() and (prev[m] == y[m]).mean() >= alvo:
            return float(t)
    return float(LIMIARES[-1])


def treinar(caminho_csv: Path | None = None) -> Modelo:
    caminho_csv = caminho_csv or config.csv_d2()
    X_tr, X_va, X_te, y_tr, y_va, y_te = mo.dividir(caminho_csv)
    vec, clf = mo.treinar(X_tr, y_tr, max_features=MAX_FEATURES, clf=LogisticRegression(max_iter=2000, C=5))
    if hasattr(vec, "stop_words_"):
        vec.stop_words_ = None  # termos cortados: não servem para prever e incham o .pkl
    pv, cv, _, _ = mo.prever((vec, clf), X_va)
    return Modelo(vec, clf, escolher_limiar(cv, pv, y_va), clf.classes_, vec.transform(X_tr), X_tr, y_tr,
                  X_te, y_te, sklearn.__version__, _hash(caminho_csv))


def carregar_ou_treinar(caminho_pkl: Path | None = None, caminho_csv: Path | None = None) -> tuple[Modelo, str]:
    caminho_pkl = caminho_pkl or config.local_dir() / "modelo_d2.pkl"
    caminho_csv = caminho_csv or config.csv_d2()
    evento = "treinado"
    if caminho_pkl.exists():
        try:
            with open(caminho_pkl, "rb") as f:
                m = pickle.load(f)
            atual = _hash(caminho_csv) if caminho_csv.exists() else m.hash_csv
            if m.sklearn == sklearn.__version__ and m.hash_csv == atual:
                return m, "carregado"
            registrar("WARNING", "classificador", "modelo_invalido", motivo="versão do scikit-learn ou dados mudaram")
        except Exception as e:  # pickle corrompido, classe mudou, etc.
            registrar("WARNING", "classificador", "modelo_invalido", motivo=type(e).__name__)
        evento = "retreinado"
    m = treinar(caminho_csv)
    caminho_pkl.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho_pkl, "wb") as f:
        pickle.dump(m, f, protocol=pickle.HIGHEST_PROTOCOL)
    return m, evento


def prever(m: Modelo, textos) -> list[Previsao]:
    P = m.clf.predict_proba(m.vec.transform(list(textos)))
    ordem = np.argsort(-P, axis=1, kind="stable")[:, :3]  # "stable" = mesmo desempate do argmax
    return [Previsao(str(m.classes[o[0]]), float(p[o[0]]), [(str(m.classes[j]), round(float(p[j]), 4)) for j in o])
            for p, o in zip(P, ordem)]


def avaliar_teste(m: Modelo) -> dict:
    ps = prever(m, m.X_te)
    prev = np.array([p.classe for p in ps])
    conf = np.array([p.confianca for p in ps])
    auto = conf >= m.limiar
    certo = prev == m.y_te
    return {"n": int(len(prev)), "limiar": m.limiar, "cobertura": float(auto.mean()),
            "acerto": float(certo[auto].mean()), "acerto_geral": float(certo.mean()),
            "acerto_abaixo_do_limiar": float(certo[~auto].mean()), "prev": prev, "conf": conf}
