"""Triagem de um ticket: categoria, confiança e destino.

Uso:
    python solution/06_triagem.py "texto do ticket"
    echo "texto" | python solution/06_triagem.py
    python solution/06_triagem.py --lote arquivo.csv      # coluna Document; grava triagem_lote.csv

Ordem de decisão: 1) regra de conteúdo manda para fila humana; 2) confiança acima do limiar
segue automático para a fila da categoria; 3) abaixo vai para fila humana com categoria sugerida.
Modelo: solution/data/derived/modelo.joblib; se ausente, treina pela lógica do script 04 com o
limiar de cobertura.json.
"""

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

import joblib
import pandas as pd

AQUI = Path(__file__).resolve().parent
DERIVADOS = AQUI / "data" / "derived"
ARQ_MODELO = DERIVADOS / "modelo.joblib"
ARQ_COBERTURA = DERIVADOS / "cobertura.json"
ARQ_LOTE = DERIVADOS / "triagem_lote.csv"
SCRIPT_04 = AQUI / "04_classificador.py"

# regras de conteúdo: qualquer termo presente manda para fila humana, antes de olhar a confiança
REGRAS_CONTEUDO = {
    "pessoa entrando ou saindo": ["leaver", "new starter", "maternity", "resignation"],
    "conta e privilégio": ["admin rights", "password reset for other", "disable account"],
    "auditoria ou incidente": ["audit", "security incident", "breach"],
    "segurança física": ["door", "alarm", "badge"],
    "urgência marcada": ["urgent", "asap", "importance high"],
}
PADROES = {
    grupo: [(t, re.compile(r"\b" + re.escape(t).replace(r"\ ", r"\s+") + r"\b", re.IGNORECASE)) for t in termos]
    for grupo, termos in REGRAS_CONTEUDO.items()
}


def carregar_limiar():
    if not ARQ_COBERTURA.exists():
        sys.exit(f"erro: {ARQ_COBERTURA.relative_to(AQUI.parent)} não existe; rode o script 04 com --limiar")
    return float(json.loads(ARQ_COBERTURA.read_text(encoding="utf-8"))["limiar"])


def carregar_modelo(limiar):
    if not ARQ_MODELO.exists():
        print(f"modelo ausente; treinando pelo script 04 com limiar {limiar}", file=sys.stderr)
        spec = importlib.util.spec_from_file_location("classificador", SCRIPT_04)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        argv, stdout = sys.argv, sys.stdout
        sys.argv = [str(SCRIPT_04), "--limiar", str(limiar)]
        try:
            mod.main()
        finally:
            sys.argv, sys.stdout = argv, stdout
    return joblib.load(ARQ_MODELO)


def regra_conteudo(texto):
    for grupo, padroes in PADROES.items():
        for termo, padrao in padroes:
            if padrao.search(texto):
                return grupo, termo
    return None, None


def triar(modelo, limiar, texto):
    proba = modelo.predict_proba([texto])[0]
    i = proba.argmax()
    categoria, confianca = str(modelo.classes_[i]), float(proba[i])
    grupo, termo = regra_conteudo(texto)
    if grupo:
        destino, regra = "fila humana", f"conteúdo: {grupo} ('{termo}')"
    elif confianca >= limiar:
        destino, regra = f"fila {categoria}", f"confiança {confianca:.3f} >= limiar {limiar}"
    else:
        destino, regra = "fila humana", f"confiança {confianca:.3f} < limiar {limiar}"
    return {"categoria": categoria, "confianca": round(confianca, 4), "destino": destino,
            "regra": regra, "termo": termo or ""}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("texto", nargs="?", help="texto do ticket; se omitido, lê stdin")
    parser.add_argument("--lote", help="CSV com coluna Document")
    args = parser.parse_args()

    limiar = carregar_limiar()
    modelo = carregar_modelo(limiar)

    if args.lote:
        lote = pd.read_csv(args.lote)
        if "Document" not in lote.columns:
            sys.exit("erro: o CSV precisa ter a coluna Document")
        decisoes = pd.DataFrame([triar(modelo, limiar, str(t)) for t in lote["Document"].fillna("")],
                                index=lote.index)
        decisoes.insert(0, "indice", lote.index)
        decisoes.to_csv(ARQ_LOTE, index=False)
        print(f"{len(decisoes)} tickets triados; decisões em {ARQ_LOTE.relative_to(AQUI.parent)}")
        print("destino:")
        print(decisoes["destino"].value_counts().to_string())
        print("regra que decidiu:")
        tipo = decisoes["regra"].str.replace(r"^conteúdo:.*", "conteúdo", regex=True)
        tipo = tipo.str.replace(r"^confiança [0-9.]+ >=.*", "confiança acima do limiar", regex=True)
        tipo = tipo.str.replace(r"^confiança [0-9.]+ <.*", "confiança abaixo do limiar", regex=True)
        print(tipo.value_counts().to_string())
        return

    texto = args.texto if args.texto is not None else sys.stdin.read()
    texto = texto.strip()
    if not texto:
        sys.exit("erro: texto vazio")
    d = triar(modelo, limiar, texto)
    print(f"categoria: {d['categoria']}")
    print(f"confiança: {d['confianca']:.4f}")
    print(f"destino: {d['destino']}")
    print(f"regra: {d['regra']}")


if __name__ == "__main__":
    main()
