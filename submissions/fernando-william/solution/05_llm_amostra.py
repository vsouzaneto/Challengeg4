"""Mede gemini-3.1-flash-lite como classificador de Topic_group numa amostra do teste.

Sem argumento: zero-shot. Com --exemplos N: N tickets por classe sorteados do treino (semente 42)
entram no prompt como exemplos rotulados; cache e saída ganham o sufixo _fewshotN.

REST com requests, sem SDK. Chave lida como no script 00 (ambiente ou .env acima deste arquivo);
nunca gravada em cache, log ou saída. Respostas cacheadas em solution/cache/<modelo>.jsonl.
Saída em solution/05_llm_amostra.txt. Só imprime números; não interpreta.
"""

import argparse
import hashlib
import importlib.util
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import requests
from scipy import stats
from sklearn.metrics import confusion_matrix

# ---------------------------------------------------------------- premissas
MODELO = "gemini-3.1-flash-lite"
# benchmark: ai.google.dev/gemini-api/docs/pricing, consultado em 16/09/2026
PRECO_ENTRADA_USD_POR_MILHAO = 0.25
PRECO_SAIDA_USD_POR_MILHAO = 1.50
# premissa minha: câmbio
CAMBIO_BRL_POR_USD = 5.50
# premissa minha (mesma do script 02, cenário base): triagem humana
MIN_TRIAGEM_HUMANA = 5
CUSTO_HORA_HUMANO_BRL = 35.0
# premissa minha: custo marginal de inferência do TF-IDF local é desprezível
CUSTO_TFIDF_POR_MIL_BRL = 0.0

SEED = 42
N_POR_CLASSE = 40
TEMPERATURA = 0
MAX_TOKENS_SAIDA = 16
PAUSA_S = 0.5
BACKOFF_S = [2, 4, 8, 16]
MAX_TENTATIVAS = 5
TIMEOUT_S = 60
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "data"
DERIVADOS = DADOS / "derived"
CACHE = AQUI / "cache" / f"{MODELO}.jsonl"          # redefinido em main() se --exemplos
SAIDA = AQUI / "05_llm_amostra.txt"                    # idem

CATEGORIAS = {
    "Access": "account access, logins, passwords, licenses, permissions to systems or repositories",
    "Administrative rights": "elevated or admin privileges to install, upgrade or update software on a machine",
    "HR Support": "HR processes: new starters, leavers, leave requests, timecards, payroll or HR system errors",
    "Hardware": "physical equipment: laptops, monitors, phones, cables, meeting-room devices, connectivity",
    "Internal Project": "internal project codes, project setup, pipelines and project tracking",
    "Miscellaneous": "requests that fit none of the others: change approvals, mailing lists, group membership, ticket administration",
    "Purchase": "purchase orders, buying devices or items, receipts and allocation of purchased goods",
    "Storage": "folders, shared drives, mailbox size, file permissions, archiving and storage increases",
}


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


def carregar_chave():
    spec = importlib.util.spec_from_file_location("teste_chave", AQUI / "00_teste_chave_gemini.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.carregar_chave()


def montar_prompt(texto, exemplos=()):
    linhas = ["Classify the IT support ticket below into exactly one of these categories:", ""]
    for nome, definicao in CATEGORIAS.items():
        linhas.append(f"- {nome}: {definicao}")
    if exemplos:
        linhas += ["", "Labeled examples:"]
        for texto_ex, rotulo_ex in exemplos:
            linhas += ["", "Ticket:", texto_ex.strip(), f"Category: {rotulo_ex}"]
        linhas += ["", "Now classify this ticket."]
    linhas += ["", "Ticket:", texto.strip(), "",
               "Answer with the category name only, nothing else."]
    return "\n".join(linhas)


def sortear_exemplos(tk, idx_treino, n_por_classe):
    """N exemplos por classe, só do treino, semente fixa, ordem embaralhada com a mesma semente."""
    treino = tk.loc[idx_treino]
    partes = [treino[treino["Topic_group"] == c].sample(n_por_classe, random_state=SEED) for c in CATEGORIAS]
    ex = pd.concat(partes).sample(frac=1, random_state=SEED)
    return ex


def ler_cache():
    cache = {}
    if CACHE.exists():
        for linha in CACHE.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                reg = json.loads(linha)
                cache[(reg["indice"], reg["sha256_prompt"])] = reg
    return cache


def gravar_cache(reg):
    with open(CACHE, "a", encoding="utf-8") as f:
        f.write(json.dumps(reg, ensure_ascii=False) + "\n")


def chamar(chave, prompt):
    """Devolve (registro_parcial, erro). Nunca inclui header ou chave no registro."""
    corpo = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": TEMPERATURA, "maxOutputTokens": MAX_TOKENS_SAIDA},
    }
    ultimo_erro = None
    for tentativa in range(MAX_TENTATIVAS):
        if tentativa > 0:
            time.sleep(BACKOFF_S[min(tentativa - 1, len(BACKOFF_S) - 1)])
        try:
            resp = requests.post(
                f"{BASE_URL}/models/{MODELO}:generateContent",
                headers={"x-goog-api-key": chave, "Content-Type": "application/json"},
                json=corpo, timeout=TIMEOUT_S)
        except requests.RequestException as e:
            ultimo_erro = f"exceção: {type(e).__name__}"
            continue
        if resp.status_code == 429 or resp.status_code >= 500:
            ultimo_erro = f"HTTP {resp.status_code}"
            continue
        if not resp.ok:
            try:
                msg = resp.json().get("error", {}).get("message", "")[:200]
            except ValueError:
                msg = ""
            return None, f"HTTP {resp.status_code}: {msg}"
        dados = resp.json()
        uso = dados.get("usageMetadata", {})
        partes = dados.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        texto = "".join(p.get("text", "") for p in partes)
        return {
            "resposta": texto,
            "finishReason": dados.get("candidates", [{}])[0].get("finishReason"),
            "promptTokenCount": uso.get("promptTokenCount"),
            "candidatesTokenCount": uso.get("candidatesTokenCount"),
            "thoughtsTokenCount": uso.get("thoughtsTokenCount"),
            "totalTokenCount": uso.get("totalTokenCount"),
        }, None
    return None, f"falha após {MAX_TENTATIVAS} tentativas: {ultimo_erro}"


def normalizar(resposta):
    if resposta is None:
        return "INVALIDA"
    r = resposta.strip().strip(".:\"'`*").strip().lower()
    for nome in CATEGORIAS:
        if r == nome.lower():
            return nome
    for nome in CATEGORIAS:
        if nome.lower() in r:
            return nome
    return "INVALIDA"


def acuracias(y, pred, pesos_classe):
    por_classe = {c: float((pred[y == c] == c).mean()) for c in CATEGORIAS}
    balanceada = float(np.mean(list(por_classe.values())))
    ponderada = float(sum(pesos_classe[c] * por_classe[c] for c in CATEGORIAS))
    return por_classe, balanceada, ponderada


def main():
    global CACHE, SAIDA
    parser = argparse.ArgumentParser()
    parser.add_argument("--exemplos", type=int, default=0, help="exemplos rotulados por classe, do treino")
    args = parser.parse_args()
    if args.exemplos > 0:
        CACHE = AQUI / "cache" / f"{MODELO}_fewshot{args.exemplos}.jsonl"
        SAIDA = AQUI / f"05_llm_amostra_fewshot{args.exemplos}.txt"
    sys.stdout = Tee(SAIDA)
    pd.set_option("display.width", 250)

    tk = pd.read_csv(DADOS / "all_tickets_processed_improved_v3.csv")
    idx_teste = pd.read_csv(DERIVADOS / "split_teste.csv")["indice_original"].values
    teste = tk.loc[idx_teste]
    prevalencia = teste["Topic_group"].value_counts(normalize=True)
    amostra = pd.concat([
        teste[teste["Topic_group"] == c].sample(N_POR_CLASSE, random_state=SEED) for c in CATEGORIAS
    ]).sort_index()
    assert set(amostra.index) <= set(idx_teste)
    exemplos = ()
    print("=== 1. amostra ===")
    print(f"teste: {len(teste)} tickets; amostra: {len(amostra)} ({N_POR_CLASSE} por classe, semente {SEED})")
    if args.exemplos > 0:
        idx_treino = pd.read_csv(DERIVADOS / "split_treino.csv")["indice_original"].values
        assert not set(idx_treino) & set(idx_teste)
        ex = sortear_exemplos(tk, idx_treino, args.exemplos)
        assert not set(ex.index) & set(idx_teste)
        exemplos = tuple(zip(ex["Document"].fillna(""), ex["Topic_group"]))
        print(f"exemplos no prompt: {len(ex)} ({args.exemplos} por classe, só do treino, semente {SEED}); "
              f"índices: {sorted(int(i) for i in ex.index)}")
        print(f"palavras nos exemplos: total {sum(len(t.split()) for t, _ in exemplos)}, "
              f"máximo {max(len(t.split()) for t, _ in exemplos)}")
    else:
        print("exemplos no prompt: 0 (zero-shot)")
    print("prevalência das classes no teste (peso da acurácia ponderada):")
    print(prevalencia.round(4).to_string())

    # ------------------------------------------------------------ chamadas
    chave = None  # carregada só na primeira chamada nova; com cache completo o script roda sem chave
    cache = ler_cache()
    n_cache, n_chamadas, n_erros = 0, 0, 0
    registros = {}
    for indice, linha in amostra.iterrows():
        prompt = montar_prompt(linha["Document"], exemplos)
        h = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        reg = cache.get((int(indice), h))
        if reg is not None and not reg.get("erro"):
            n_cache += 1
            registros[indice] = reg
            continue
        if chave is None:
            chave = carregar_chave()
        parcial, erro = chamar(chave, prompt)
        n_chamadas += 1
        reg = {"indice": int(indice), "sha256_prompt": h,
               "hora_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        if erro:
            n_erros += 1
            reg["erro"] = erro
        else:
            reg.update(parcial)
        gravar_cache(reg)
        registros[indice] = reg
        print(f"  chamada {n_chamadas}: índice {indice} {'ERRO ' + erro if erro else 'ok'}", file=sys.stderr)
        time.sleep(PAUSA_S)
    print(f"\n=== 2. chamadas ===")
    print(f"reutilizadas do cache: {n_cache}; chamadas feitas agora: {n_chamadas}; falhas definitivas: {n_erros}; "
          f"chave de API {'carregada' if chave else 'não carregada'}")
    print(f"cache em {CACHE.relative_to(AQUI.parent)}")

    # ------------------------------------------------------------ resultado
    y = amostra["Topic_group"].values
    pred_llm = np.array([normalizar(registros[i].get("resposta")) for i in amostra.index])
    invalidas = (pred_llm == "INVALIDA").sum()
    finish = pd.Series([registros[i].get("finishReason") for i in amostra.index]).value_counts(dropna=False)
    print("\n=== 3. LLM na amostra ===")
    print(f"respostas sem categoria reconhecível (contadas como erro): {invalidas}")
    print("finishReason: " + ", ".join(f"{k}={v}" for k, v in finish.items()))
    pc_llm, bal_llm, pond_llm = acuracias(y, pred_llm, prevalencia)
    print(f"acurácia balanceada: {bal_llm:.4f}; ponderada pela prevalência no teste: {pond_llm:.4f}")
    print("acurácia por classe:")
    print(pd.Series(pc_llm).round(4).to_string())
    rotulos = list(CATEGORIAS) + ["INVALIDA"]
    cm = confusion_matrix(y, pred_llm, labels=rotulos)
    print("matriz de confusão (linhas = real, colunas = previsto pelo LLM):")
    print(pd.DataFrame(cm, index=rotulos, columns=rotulos).iloc[:-1].to_string())

    print("\n=== 4. TF-IDF nos mesmos tickets ===")
    modelo = joblib.load(DERIVADOS / "modelo.joblib")
    proba = modelo.predict_proba(amostra["Document"].fillna(""))
    pred_tfidf = modelo.classes_[proba.argmax(axis=1)]
    prob_max = proba.max(axis=1)
    pc_tf, bal_tf, pond_tf = acuracias(y, pred_tfidf, prevalencia)
    print(f"acurácia balanceada: {bal_tf:.4f}; ponderada: {pond_tf:.4f}")
    print("acurácia por classe:")
    print(pd.Series(pc_tf).round(4).to_string())

    print("\n=== 5. McNemar LLM vs TF-IDF ===")
    ok_llm, ok_tf = pred_llm == y, pred_tfidf == y
    b = int((ok_llm & ~ok_tf).sum())   # só o LLM acerta
    c = int((~ok_llm & ok_tf).sum())   # só o TF-IDF acerta
    ambos = int((ok_llm & ok_tf).sum())
    nenhum = int((~ok_llm & ~ok_tf).sum())
    p_exato = stats.binomtest(min(b, c), b + c, 0.5).pvalue if b + c > 0 else float("nan")
    chi2_cc = (abs(b - c) - 1) ** 2 / (b + c) if b + c > 0 else float("nan")
    p_chi2 = 1 - stats.chi2.cdf(chi2_cc, 1) if b + c > 0 else float("nan")
    print(f"ambos acertam {ambos}; só LLM acerta {b}; só TF-IDF acerta {c}; nenhum {nenhum}")
    print(f"McNemar exato (binomial): p={p_exato:.4g}; com correção de continuidade: chi2={chi2_cc:.3f}, p={p_chi2:.4g}")

    cob = json.loads((DERIVADOS / "cobertura.json").read_text(encoding="utf-8"))
    limiar = cob["limiar"]
    abstem = prob_max < limiar
    print(f"\n=== 6. LLM onde o TF-IDF abstém (limiar {limiar} de cobertura.json) ===")
    print(f"tickets da amostra em que o TF-IDF abstém: {abstem.sum()} de {len(y)} (fração {abstem.mean():.4f}); "
          f"fração de abstenção no teste inteiro: {1 - cob['cobertura']:.4f}")
    if abstem.any():
        print(f"acurácia do LLM nesses tickets: {ok_llm[abstem].mean():.4f}; "
              f"do TF-IDF (se forçado a decidir): {ok_tf[abstem].mean():.4f}")
        print(f"acurácia do TF-IDF nos decididos: {ok_tf[~abstem].mean():.4f} (n={int((~abstem).sum())})")
    pred_cascata = np.where(abstem, pred_llm, pred_tfidf)
    pc_cas, bal_cas, pond_cas = acuracias(y, pred_cascata, prevalencia)

    print("\n=== 7. custo ===")
    validos = [registros[i] for i in amostra.index if not registros[i].get("erro")]
    tok_in = sum(r.get("promptTokenCount") or 0 for r in validos)
    tok_out = sum((r.get("candidatesTokenCount") or 0) + (r.get("thoughtsTokenCount") or 0) for r in validos)
    tok_thoughts = sum(r.get("thoughtsTokenCount") or 0 for r in validos)
    n_val = len(validos)
    custo_total_usd = (tok_in * PRECO_ENTRADA_USD_POR_MILHAO + tok_out * PRECO_SAIDA_USD_POR_MILHAO) / 1e6
    custo_chamada_usd = custo_total_usd / n_val if n_val else float("nan")
    custo_mil_usd = custo_chamada_usd * 1000
    custo_mil_brl = custo_mil_usd * CAMBIO_BRL_POR_USD
    print(f"chamadas válidas: {n_val}; tokens de entrada: {tok_in} (média {tok_in / n_val:.1f}); "
          f"tokens de saída: {tok_out} (média {tok_out / n_val:.1f}; dos quais de raciocínio: {tok_thoughts})")
    print(f"custo total da amostra: US$ {custo_total_usd:.4f}; por chamada: US$ {custo_chamada_usd:.6f}")
    print(f"custo por mil tickets: US$ {custo_mil_usd:.4f} = R$ {custo_mil_brl:.4f} (câmbio {CAMBIO_BRL_POR_USD})")
    custo_humano_mil_brl = 1000 * MIN_TRIAGEM_HUMANA / 60 * CUSTO_HORA_HUMANO_BRL
    frac_llm = float(abstem.mean())

    tabela = pd.DataFrame([
        {"opção": "TF-IDF (decide 100%)", "acurácia balanceada": bal_tf, "acurácia ponderada": pond_tf,
         "custo/mil R$": CUSTO_TFIDF_POR_MIL_BRL, "custo/mil US$": CUSTO_TFIDF_POR_MIL_BRL / CAMBIO_BRL_POR_USD},
        {"opção": f"LLM {MODELO} {args.exemplos}-shot (100%)", "acurácia balanceada": bal_llm, "acurácia ponderada": pond_llm,
         "custo/mil R$": custo_mil_brl, "custo/mil US$": custo_mil_usd},
        {"opção": f"humano ({MIN_TRIAGEM_HUMANA} min a R$ {CUSTO_HORA_HUMANO_BRL:.0f}/h)",
         "acurácia balanceada": np.nan, "acurácia ponderada": np.nan,
         "custo/mil R$": custo_humano_mil_brl, "custo/mil US$": custo_humano_mil_brl / CAMBIO_BRL_POR_USD},
        {"opção": "cascata: LLM em 100% dos tickets", "acurácia balanceada": bal_llm, "acurácia ponderada": pond_llm,
         "custo/mil R$": custo_mil_brl, "custo/mil US$": custo_mil_usd},
        {"opção": f"cascata: TF-IDF decide, LLM só nos {frac_llm:.1%} em que abstém",
         "acurácia balanceada": bal_cas, "acurácia ponderada": pond_cas,
         "custo/mil R$": custo_mil_brl * frac_llm, "custo/mil US$": custo_mil_usd * frac_llm},
    ]).set_index("opção")
    print("\n=== 8. tabela final (acurácia medida nos mesmos 320; humano não medido) ===")
    print(tabela.round(4).to_string())
    print(f"\nsaída gravada em {SAIDA.relative_to(AQUI.parent)}")


if __name__ == "__main__":
    main()
