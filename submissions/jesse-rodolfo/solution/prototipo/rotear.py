"""Roteia um texto: categoria, confiança e rota (automático ou humano).
Uso: .venv/bin/python -I solution/prototipo/rotear.py "texto do ticket"
"""
import sys
from pathlib import Path

import joblib

sys.path.insert(0, str(Path(__file__).resolve().parent))
from treinar import MODELO, limpar, treinar_e_salvar  # noqa: E402

LIMIAR = 0.7
# Categorias do dataset 2 que exigem autoridade humana (proposta do Bloco 3: dinheiro e direitos de acesso).
PORTOES = {"Purchase", "Administrative rights"}


def carregar():
    if not MODELO.exists():
        treinar_e_salvar(verbose=False)
    return joblib.load(MODELO)


def rotear(texto, modelo=None, limiar=LIMIAR, portoes=PORTOES):
    limpo = limpar(texto or "")
    if not limpo:
        return {"categoria": None, "confianca": 0.0, "rota": "humano", "motivo": "texto vazio"}
    modelo = modelo or carregar()
    proba = modelo.predict_proba([limpo])[0]
    i = proba.argmax()
    categoria, conf = str(modelo.classes_[i]), float(proba[i])
    if conf < limiar:
        rota, motivo = "humano", "confiança abaixo do limiar"
    elif categoria in portoes:
        rota, motivo = "humano", "portão de autoridade"
    else:
        rota, motivo = "automático", "acima do limiar e fora dos portões"
    return {"categoria": categoria, "confianca": round(conf, 4), "rota": rota, "motivo": motivo}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('uso: rotear.py "texto do ticket"')
    print(rotear(sys.argv[1]))
