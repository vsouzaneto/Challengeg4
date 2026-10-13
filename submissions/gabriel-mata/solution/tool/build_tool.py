"""OS-08 - Monta o decisor.html: le o CSV, embute os dados compactos e junta
template.html + engine.js + ui.js num arquivo unico e autossuficiente."""

import json
import os
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
DATA_PATH = Path(os.environ.get("DATA_PATH", REPO_ROOT / "datasets" / "social_media_dataset.csv"))
SRC = SCRIPT_DIR / "src"
SAIDA = SCRIPT_DIR / "decisor.html"

# colunas da secao 2 da OS
COLS_OBRIG = ["post_date", "platform", "content_type", "content_category",
              "follower_count", "is_sponsored", "views", "likes", "shares", "comments_count"]
COLS_PUBLICO = ["audience_age_distribution", "audience_gender_distribution", "audience_location"]
# opcionais da OS-09 parte 1: entram se existirem no CSV
COLS_EXTRA = ["clicks", "conversions", "cost"]

NOME_BASE = "base do desafio"


def codificar(serie):
    """Coluna categorica -> codigos inteiros + rotulos ordenados (igual ao engine.js)."""
    s = serie.astype(str).str.strip()
    rotulos = sorted(s.unique())
    ordem = {v: i for i, v in enumerate(rotulos)}
    return {"cod": s.map(ordem).tolist(), "rotulos": rotulos}


def main():
    df = pd.read_csv(DATA_PATH)
    print(f"Base: {len(df)} linhas (origem: {DATA_PATH})")

    faltando = [c for c in COLS_OBRIG if c not in df.columns]
    if faltando:
        raise SystemExit(f"CSV sem as colunas obrigatorias: {faltando}")

    # colunas extras sao ignoradas; as de publico entram se existirem
    tem_publico = all(c in df.columns for c in COLS_PUBLICO)
    print(f"Colunas de publico presentes: {tem_publico}")

    data = pd.to_datetime(df["post_date"], format="%m/%d/%y %I:%M %p")
    sponsored = df["is_sponsored"].astype(str).str.strip().str.lower().map(
        {"true": 1, "false": 0, "1": 1, "0": 0, "sim": 1, "nao": 0, "não": 0})
    if sponsored.isna().any():
        raise SystemExit("is_sponsored com valores nao reconhecidos")

    compacto = {
        "nome": NOME_BASE,
        "n": int(len(df)),
        # epoch em ms, UTC (o engine trata as datas em UTC)
        "data": (data.astype("int64") // 10**6).tolist(),
        "seg": df["follower_count"].astype(int).tolist(),
        "pat": sponsored.astype(int).tolist(),
        "views": df["views"].astype(int).tolist(),
        "likes": df["likes"].astype(int).tolist(),
        "shares": df["shares"].astype(int).tolist(),
        "coment": df["comments_count"].astype(int).tolist(),
        "plat": codificar(df["platform"]),
        "tipo": codificar(df["content_type"]),
        "cat": codificar(df["content_category"]),
    }
    if tem_publico:
        compacto["idade"] = codificar(df["audience_age_distribution"])
        compacto["genero"] = codificar(df["audience_gender_distribution"])
        compacto["pais"] = codificar(df["audience_location"])
    for c in COLS_EXTRA:
        if c in df.columns:
            compacto[c] = df[c].fillna(0).astype(float).tolist()
            print(f"Coluna opcional embutida: {c}")

    dados_json = json.dumps(compacto, separators=(",", ":"), ensure_ascii=False)
    print(f"JSON dos dados: {len(dados_json.encode('utf-8')) / 1e6:.2f} MB")

    template = (SRC / "template.html").read_text(encoding="utf-8")
    engine = (SRC / "engine.js").read_text(encoding="utf-8")
    ui = (SRC / "ui.js").read_text(encoding="utf-8")

    # </script> dentro do JSON fecharia a tag antes da hora
    dados_json = dados_json.replace("</", "<\\/")

    html = template
    for marca, conteudo in [("__DADOS__", dados_json), ("__ENGINE__", engine), ("__UI__", ui)]:
        if marca not in html:
            raise SystemExit(f"template.html sem a marca {marca}")
        html = html.replace(marca, conteudo)

    SAIDA.write_text(html, encoding="utf-8")
    tam = SAIDA.stat().st_size
    print(f"-> {SAIDA} ({tam / 1e6:.2f} MB)")
    if tam > 6e6:
        print(f"ATENCAO: passou da meta de 6 MB ({tam / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
