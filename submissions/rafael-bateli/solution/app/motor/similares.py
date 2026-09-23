"""Tickets parecidos no histórico (treino do D2). TF-IDF já é normalizado: produto = cosseno."""

from __future__ import annotations

import numpy as np

from . import config


def vizinhos_lote(m, textos, k: int = 3, bloco: int = 500) -> list[list[dict]]:
    V = m.vec.transform(list(textos))
    saida = []
    for i in range(0, V.shape[0], bloco):
        S = (V[i:i + bloco] @ m.V_hist.T).toarray()
        top = np.argpartition(-S, k, axis=1)[:, :k]
        for linha, ids in zip(S, top):
            ids = ids[np.argsort(-linha[ids], kind="stable")]
            saida.append([{"texto": str(m.X_hist[j])[:200], "classe": str(m.y_hist[j]),
                           "similaridade": round(float(linha[j]), 3),
                           "duplicata": bool(linha[j] >= config.LIMIAR_DUPLICATA)} for j in ids])
    return saida
