"""
Classificador C: LLM (Gemini) classificando os tickets do Dataset 2 numa amostra do conjunto de teste.

Modos:
  zero-shot  só os nomes das categorias
  few-shot   nomes + 3 exemplos reais de treino por categoria
  rag        nomes + os 5 tickets de treino MAIS PARECIDOS com cada ticket, já rotulados
             (sugestão do agente juiz: o melhor cenário possível para o LLM)

As respostas brutas ficam em data/cache/llm_<modelo>_<modo>.jsonl. Assim o benchmark pode ser
reavaliado sem chamar a API de novo, e as respostas servem de evidência.

Uso: python llm_classify.py --modelo gemini-3.5-flash-lite --modo few-shot --n 400
"""
import argparse
import json
import os
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[3]
CACHE = ROOT / "data/cache"
CACHE.mkdir(parents=True, exist_ok=True)
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

CATEGORIAS = ["Hardware", "HR Support", "Access", "Miscellaneous", "Storage",
              "Purchase", "Internal Project", "Administrative rights"]
LOTE = 20  # tickets por chamada (no modo rag, 10: o prompt fica maior)


def carregar_split():
    d = pd.read_csv(ROOT / "data/ds2_it_tickets/all_tickets_processed_improved_v3.csv")
    return train_test_split(d, test_size=0.2, stratify=d["Topic_group"], random_state=42)


def amostra_teste(te: pd.DataFrame, n: int) -> pd.DataFrame:
    """Amostra estratificada (proporcional às classes) e determinística do conjunto de teste."""
    a, _ = train_test_split(te, train_size=n, stratify=te["Topic_group"], random_state=7)
    return a


def vizinhos_de_treino(tr: pd.DataFrame):
    """Para o modo rag: devolve uma função que acha os 5 tickets de treino mais parecidos (TF-IDF + cosseno)."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.neighbors import NearestNeighbors
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    nn = NearestNeighbors(n_neighbors=5, metric="cosine").fit(vec.fit_transform(tr["Document"]))
    return lambda textos: nn.kneighbors(vec.transform(textos))[1]


def montar_prompt(modo: str, tr: pd.DataFrame, lote: pd.DataFrame, vizinhos=None) -> str:
    p = ["You classify internal IT service desk tickets into exactly one category.",
         "Text is preprocessed: lowercase, no punctuation, stopwords and personal data removed.",
         f"Categories: {', '.join(CATEGORIAS)}.", ""]
    if modo == "few-shot":
        p.append("Labeled examples:")
        for cat in CATEGORIAS:
            for doc in tr[tr["Topic_group"] == cat]["Document"].sample(3, random_state=1):
                p.append(f"- [{cat}] {doc[:300]}")
        p.append("")
    p.append('Return a JSON list with one object per ticket: {"id": <id>, "category": <one of the categories>}.')
    if modo == "rag":
        p.append("For each ticket you get the 5 most similar PAST tickets from this company with their true category. "
                 "Categories follow internal company conventions, so the past examples are strong evidence.")
        for (i, doc), viz in zip(lote["Document"].items(), vizinhos(lote["Document"])):
            p.append(f"\n### Ticket id={i}: {doc[:1200]}\nSimilar past tickets:")
            p += [f"  - [{tr.iloc[j]['Topic_group']}] {tr.iloc[j]['Document'][:250]}" for j in viz]
        return "\n".join(p)
    p.append("Tickets:")
    for i, doc in lote["Document"].items():
        p.append(f"id={i}: {doc[:1200]}")
    return "\n".join(p)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default="gemini-3.5-flash-lite")
    ap.add_argument("--modo", choices=["zero-shot", "few-shot", "rag"], default="zero-shot")
    ap.add_argument("--n", type=int, default=400)
    args = ap.parse_args()

    tr, te = carregar_split()
    vizinhos = vizinhos_de_treino(tr) if args.modo == "rag" else None
    amostra = amostra_teste(te, args.n)
    saida = CACHE / f"llm_{args.modelo}_{args.modo}.jsonl"
    feitos = set()
    if saida.exists():
        feitos = {json.loads(l)["id"] for l in saida.read_text(encoding="utf-8").splitlines()}
    pendentes = amostra[~amostra.index.isin(feitos)]

    cliente = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    cfg = types.GenerateContentConfig(temperature=0, response_mime_type="application/json")
    with saida.open("a", encoding="utf-8") as f:
        tam = 10 if args.modo == "rag" else LOTE
        for ini in range(0, len(pendentes), tam):
            lote = pendentes.iloc[ini:ini + tam]
            for tentativa in range(5):
                try:
                    t = time.time()
                    r = cliente.models.generate_content(model=args.modelo, contents=montar_prompt(args.modo, tr, lote, vizinhos), config=cfg)
                    seg = time.time() - t
                    uso = r.usage_metadata
                    for item in json.loads(r.text):
                        f.write(json.dumps({"id": int(item["id"]), "pred": item["category"],
                                            "seg_lote": round(seg, 2), "n_lote": len(lote),
                                            "tok_in": uso.prompt_token_count, "tok_out": uso.candidates_token_count}) + "\n")
                    f.flush()
                    break
                except Exception as e:  # cota/erro transitório: espera e tenta de novo
                    print(f"  tentativa {tentativa + 1}: {type(e).__name__}: {str(e)[:120]}")
                    time.sleep(15 * (tentativa + 1))
            print(f"{min(ini + tam, len(pendentes))}/{len(pendentes)}")
            time.sleep(4)  # respeita o limite de requisições por minuto do plano gratuito


if __name__ == "__main__":
    main()
