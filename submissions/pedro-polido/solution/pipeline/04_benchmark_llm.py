"""LLM (Gemini) × classificador linear na mesma amostra do conjunto de teste.

Pergunta: vale usar um LLM para classificar os tickets? Três formas de pedir, da mais barata à mais informada:
  nomes       só os nomes das 8 filas
  descricoes  nomes + a descrição de cada fila (a mesma mostrada no app)
  exemplos    descrições + 3 tickets de treino por fila (few-shot)
E, à parte, o LLM como terceira opinião nos 40 casos da auditoria de rótulos.

Modelos: gemini-3.5-flash-lite (o mesmo do app) nos três prompts; gemini-3.5-flash, sem raciocínio, no prompt mais
informado, para checar se um modelo maior muda a conclusão. Comparação pareada com o linear: teste de McNemar.
(gemini-2.5-flash, o padrão da 1ª versão deste script, devolve 404 para chaves novas.)

Requer GEMINI_API_KEY no .env da raiz do repositório.
Uso: python 04_benchmark_llm.py [n_amostra]      Saída: app/data/llm_benchmark.json
"""
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from statsmodels.stats.contingency_tables import mcnemar
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from common import IT_TICKETS_CSV, REPO_ROOT, SEED, SUBMISSION, load_env, save_json

load_env()
KEY = os.environ.get("GEMINI_API_KEY")
MAIN_MODEL = "gemini-3.5-flash-lite"
# Modelo maior para a checagem: o primeiro que responder. Os flash maiores alternam 503 (alta demanda) e 429 (cota).
STRONG_MODELS = [("gemini-3.5-flash", {"thinkingBudget": 0}), ("gemini-3.6-flash", {"thinkingLevel": "low"}),
                 ("gemini-flash-latest", {"thinkingBudget": 0})]
# Cada rodada concluída fica em cache: uma falha no meio não joga fora as rodadas anteriores.
# datasets/ já é ignorado pelo .gitignore do repositório.
CACHE = REPO_ROOT / "datasets" / ".cache_llm"
N_SAMPLE = int(sys.argv[1]) if len(sys.argv) > 1 else 240
BATCH = 20           # tickets por requisição
PAUSE_S = 4.0        # respeita o limite de requisições por minuto da camada gratuita
if not KEY:
    sys.exit("GEMINI_API_KEY não encontrada no .env")

QUEUES_EN = {
    "Access": "accounts, passwords, licenses and access to tools (Confluence, Git, access cards)",
    "Administrative rights": "installing or upgrading software that needs admin rights (Outlook, Windows)",
    "HR Support": "employee starters and leavers, vacation, leave and timesheets (Oracle)",
    "Hardware": "laptops, monitors, phones, meeting rooms, cables and peripherals",
    "Internal Project": "project codes, pipelines and internal project setup",
    "Miscellaneous": "approvals, groups, ownership changes and contracts",
    "Purchase": "purchase orders (PO), receiving and equipment allocation",
    "Storage": "folders, mailboxes, storage quotas and sharing permissions",
}
CLASSES = list(QUEUES_EN)

df = pd.read_csv(IT_TICKETS_CSV)
train, test = train_test_split(df, test_size=0.2, stratify=df["Topic_group"], random_state=SEED)
sample, _ = train_test_split(test, train_size=N_SAMPLE, stratify=test["Topic_group"], random_state=SEED)
sample = sample[sample["Document"].str.split().str.len() <= 150]  # tickets gigantes estouram o lote

# Classificador linear na mesma amostra (mesma configuração do 03)
vec = TfidfVectorizer(min_df=2, sublinear_tf=True)
clf = LogisticRegression(C=5.0, max_iter=3000).fit(vec.fit_transform(train["Document"]), train["Topic_group"])
linear_pred = clf.predict(vec.transform(sample["Document"]))

shots = "\n".join(
    f"- [{c}] {t[:300]}" for c in CLASSES
    for t in train.loc[(train["Topic_group"] == c) & train["Document"].str.split().str.len().between(8, 40), "Document"]
    .sample(3, random_state=SEED))

PROMPTS = {
    "nomes": "Classify each IT support ticket into exactly one queue: " + ", ".join(CLASSES) + ".",
    "descricoes": "Classify each IT support ticket into exactly one queue:\n"
                  + "\n".join(f"- {c}: {d}" for c, d in QUEUES_EN.items()),
}
PROMPTS["exemplos"] = PROMPTS["descricoes"] + "\n\nLabeled examples from this company's history:\n" + shots
SUFFIX = ("\n\nTickets are preprocessed (lowercase, no punctuation, stopwords removed). "
          "Answer with a JSON array with one queue name per ticket, in order.")


def gemini(model, thinking, system, tickets, attempts=6):
    config = {"temperature": 0, "responseMimeType": "application/json",
              "responseSchema": {"type": "ARRAY", "items": {"type": "STRING", "enum": CLASSES}}}
    if thinking:
        config["thinkingConfig"] = thinking
    body = {
        "systemInstruction": {"parts": [{"text": system + SUFFIX}]},
        "contents": [{"role": "user", "parts": [{"text": "\n".join(f"{i + 1}. {t}" for i, t in enumerate(tickets))}]}],
        "generationConfig": config,
    }
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": KEY})
    for attempt in range(attempts):
        try:
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.load(r)
            text = "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"])
            labels = json.loads(text)
            if len(labels) != len(tickets):
                raise ValueError(f"{len(labels)} rótulos para {len(tickets)} tickets")
            return labels, data.get("usageMetadata", {}), time.time() - t0
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as e:
            if attempt == attempts - 1:
                raise RuntimeError(f"{model} falhou {attempts} vezes seguidas: {str(e)[:80]}") from e
            wait = 15 * 2 ** attempt  # 503 de alta demanda e 429 de cota são transitórios
            print(f"   {model}: tentativa {attempt + 1} falhou ({str(e)[:80]}); nova em {wait}s", flush=True)
            time.sleep(wait)


def run(model, thinking, system, docs, attempts=6):
    key = hashlib.sha256(json.dumps([model, thinking, system, docs]).encode()).hexdigest()[:16]
    cache_file = CACHE / f"{model}_{key}.json"
    if cache_file.exists():
        c = json.loads(cache_file.read_text(encoding="utf-8"))
        return np.array(c["labels"]), c["tokens"], c["seconds"]
    labels, tokens, seconds = [], 0, 0.0
    for i in range(0, len(docs), BATCH):
        out, usage, dt = gemini(model, thinking, system, docs[i:i + BATCH], attempts)
        labels += out
        tokens += usage.get("totalTokenCount", 0)
        seconds += dt
        time.sleep(PAUSE_S)
    CACHE.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps({"labels": labels, "tokens": tokens, "seconds": seconds}), encoding="utf-8")
    return np.array(labels), tokens, seconds


def evaluate(model, name, pred, tokens, seconds):
    ok = pred == y
    # McNemar pareado: só importam os tickets em que um acerta e o outro erra
    table = [[int((ok & linear_ok).sum()), int((ok & ~linear_ok).sum())],
             [int((~ok & linear_ok).sum()), int((~ok & ~linear_ok).sum())]]
    r = {"modelo": model, "prompt": name, "acerto": float(ok.mean()), "tokens_por_ticket": tokens / len(docs),
         "segundos_por_ticket": seconds / len(docs), "p_mcnemar": float(mcnemar(table, exact=True).pvalue),
         "so_llm_acerta": table[0][1], "so_linear_acerta": table[1][0],
         "por_fila": {c: float(ok[y == c].mean()) for c in CLASSES},
         "concorda_com_linear": float((pred == linear_pred).mean())}
    print(f"  {model:22s} {name:10s} acerto {r['acerto']:.1%} (linear {linear_ok.mean():.1%}, McNemar p = {r['p_mcnemar']:.3f}) | "
          f"{r['tokens_por_ticket']:.0f} tokens/ticket | {r['segundos_por_ticket']:.2f} s/ticket", flush=True)
    return r


y = sample["Topic_group"].values
docs = sample["Document"].tolist()
linear_ok = linear_pred == y
results = {"n": len(sample), "linear": {"acerto": float(linear_ok.mean())}, "rodadas": []}
print(f"{len(sample)} tickets | classificador linear: {linear_ok.mean():.1%}", flush=True)
for name in PROMPTS:
    results["rodadas"].append(evaluate(MAIN_MODEL, name, *run(MAIN_MODEL, None, PROMPTS[name], docs)))

# Checagem com modelo maior, no prompt mais informado. Indisponibilidade vira registro, não queda do script.
failures = []
for model, thinking in STRONG_MODELS:
    try:
        # Modelo opcional: 3 tentativas bastam para saber se está disponível agora
        results["rodadas"].append(evaluate(model, "exemplos", *run(model, thinking, PROMPTS["exemplos"], docs, attempts=3)))
        break
    except RuntimeError as e:
        failures.append(model)
        print(f"  {model}: indisponível ({e}); tentando o próximo", flush=True)
results["modelos_indisponiveis"] = failures

# Terceira opinião nos 40 casos da auditoria de rótulos (o LLM não vê rótulo nem previsão do modelo)
audit_path = SUBMISSION / "process-log" / "auditoria-rotulos" / "candidatos.csv"
audit = pd.read_csv(audit_path, encoding="utf-8-sig")
llm_audit, _, _ = run(MAIN_MODEL, None, PROMPTS["descricoes"], audit["texto"].tolist())
audit["gemini"] = llm_audit
side = np.where(audit["gemini"] == audit["rotulo"], "rótulo", np.where(audit["gemini"] == audit["modelo"], "modelo", "outra fila"))
definite = audit["veredito_ia"].isin(["rótulo", "modelo"]).values  # onde o veredito do Claude foi categórico
results["auditoria"] = {"com_rotulo": float((side == "rótulo").mean()), "com_modelo": float((side == "modelo").mean()),
                        "outra": float((side == "outra fila").mean()), "n_categoricos": int(definite.sum()),
                        "concorda_com_claude": float((side[definite] == audit["veredito_ia"].values[definite]).mean())}
audit.to_csv(audit_path, index=False, encoding="utf-8-sig")
print(f"  auditoria: Gemini fica com o rótulo em {results['auditoria']['com_rotulo']:.0%}, com o modelo em "
      f"{results['auditoria']['com_modelo']:.0%}, outra fila em {results['auditoria']['outra']:.0%} | concorda com o "
      f"veredito do Claude em {results['auditoria']['concorda_com_claude']:.0%} dos {definite.sum()} casos categóricos")
save_json("llm_benchmark.json", results)
