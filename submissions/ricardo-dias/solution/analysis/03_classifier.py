"""Etapa 3 — Classificador de tickets (Dataset 2) com seleção na validação e avaliação final no teste.

Protocolo:
  treino (70%)     → ajuste do vetorizador e dos modelos
  validação (15%)  → TODAS as escolhas: modelo, C, poda, limiares de confiança, guarda de domínio e privilégio
  teste (15%)      → avaliado uma única vez, depois de congelar `selection`

Saídas:
  app/data/model_metrics.json        seleção (validação), métricas de teste com IC, histórico exploratório
  app/data/model.json                modelo v2 para lib/classifier.ts
  app/data/holdout.json              amostra do TESTE para /api/sample
  app/data/neighbors.json            amostra do TREINO para "tickets similares"
  analysis/artifacts/{val,test}_split.json   textos para avaliação/paridade sem Kaggle
  analysis/artifacts/python_predictions.json rótulo, confiança e rota do Python (paridade com o TS)

O roteamento publicado é medido em TypeScript (app/scripts/evaluate-routing.ts), com as funções da API.
"""

from __future__ import annotations

import json
import re
import unicodedata

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import ComplementNB
from sklearn.svm import LinearSVC

import policy
from common import HERE, SEED, load_d1, load_d2, r, write_json

MODEL_VERSION = 2
MAX_FEATURES = 40_000
C_GRID = [1, 4, 10]
EPS_GRID = [0.0, 0.05, 0.1, 0.2, 0.3]
MAX_F1_DROP = 0.002  # poda aceita se o F1 macro de validação cair no máximo 0,2 ponto
OOD_QUANTILE = 0.05  # guarda de domínio: aceita-se mandar ~5% dos tickets do próprio domínio para humano
MIN_AUTO_ACCURACY = 0.95  # acerto mínimo nos tickets roteados automaticamente
MAX_ADMIN_LEAK = 0.02  # no máximo 2% dos pedidos de privilégio podem ir para outra fila automaticamente
CONF_GRID = np.round(np.arange(0.50, 0.951, 0.01), 2)
ADMIN_GRID = [None, 0.5, 0.4, 0.3, 0.25, 0.2, 0.15, 0.1, 0.05]
BOOTSTRAP = 1_000
HOLDOUT_EXPORT = 2_000
NEIGHBORS_EXPORT = 4_000
ARTIFACTS = HERE / "artifacts"

# Medidos em 2026-09-16 no mesmo conjunto usado para ajustar parâmetros (commit 679477f).
EXPLORATORY = {
    "note": "Números da primeira versão: medidos no mesmo conjunto (20%) usado para escolher modelo, poda e limiares. "
            "Orientaram decisões de desenho e por isso não valem como teste. Substituídos pelo protocolo treino/validação/teste.",
    "accuracy": 0.8638, "macroF1": 0.8649, "autoCoverage": 0.6967, "autoAccuracy": 0.9574,
}


def normalize(text: str) -> str:
    """Mesma normalização de lib/classifier.ts: minúsculas, sem acento, só letras a-z."""
    text = unicodedata.normalize("NFKD", str(text).lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z]+", " ", text)).strip()


def make_vectorizer() -> TfidfVectorizer:
    # token_pattern restrito a [a-z]{2,} para ser reproduzível em JS
    return TfidfVectorizer(preprocessor=normalize, token_pattern=r"\b[a-z]{2,}\b", ngram_range=(1, 2),
                           min_df=2, sublinear_tf=True, max_features=MAX_FEATURES)


def softmax(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def br(share: float) -> str:
    return f"{share * 100:.1f}%".replace(".", ",")


def prune(coef: np.ndarray, eps: float) -> np.ndarray:
    return np.where(np.abs(coef) < eps, 0.0, coef).round(3)


def scores(y_true, y_pred) -> dict:
    return {"accuracy": r(accuracy_score(y_true, y_pred)), "macroF1": r(f1_score(y_true, y_pred, average="macro"))}


def bootstrap_ci(y_true: np.ndarray, y_pred: np.ndarray, rng: np.random.Generator) -> tuple[dict, dict]:
    n = len(y_true)
    acc, f1 = [], []
    for _ in range(BOOTSTRAP):
        i = rng.integers(0, n, n)
        acc.append(accuracy_score(y_true[i], y_pred[i]))
        f1.append(f1_score(y_true[i], y_pred[i], average="macro"))
    ci = lambda v: {"low": r(np.quantile(v, 0.025)), "high": r(np.quantile(v, 0.975))}  # noqa: E731
    return ci(acc), ci(f1)


class Scored:
    """Predições de uma partição com tudo o que a política precisa."""

    def __init__(self, texts, labels, vec, coef, intercept, classes, vocab, rules):
        self.labels = labels
        proba = softmax(vec.transform(texts) @ coef.T + intercept)
        self.pred = classes[proba.argmax(1)]
        self.conf = proba.max(1)
        self.p_admin = proba[:, list(classes).index(rules["adminRightsCategory"])]
        tokens = [policy.tokens_of(normalize(t)) for t in texts]
        self.known = policy.known_share(tokens, vocab)
        self.escalate = policy.escalation_hits(tokens, rules)

    def routes(self, conf_t, ood_t, admin_t, rules):
        return policy.decide_routes(pred=self.pred, conf=self.conf, p_admin=self.p_admin, known=self.known,
                                    escalate=self.escalate, confidence=conf_t, ood=ood_t,
                                    admin_rights=admin_t, rules=rules)


def main() -> None:
    rules = policy.load_rules()
    d2 = load_d2()
    X, y = d2["Document"].to_numpy(), d2["Topic_group"].to_numpy()
    idx = np.arange(len(d2))
    tr, rest = train_test_split(idx, test_size=0.30, stratify=y, random_state=SEED)
    va, te = train_test_split(rest, test_size=0.50, stratify=y[rest], random_state=SEED)
    splits = [
        {"name": "treino", "n": int(len(tr)), "share": r(len(tr) / len(idx)),
         "purpose": "Ajuste do vetorizador TF-IDF e dos modelos."},
        {"name": "validacao", "n": int(len(va)), "share": r(len(va) / len(idx)),
         "purpose": "Todas as escolhas: modelo, C, poda, limiar de confiança, guarda de domínio e regra de privilégio."},
        {"name": "teste", "n": int(len(te)), "share": r(len(te) / len(idx)),
         "purpose": "Avaliação final única, depois de congelar as escolhas. Fonte dos números publicados."},
    ]
    print("partições:", {s["name"]: s["n"] for s in splits})

    # ---------------- seleção (só validação) ----------------
    vec = make_vectorizer()
    Xtr = vec.fit_transform(X[tr])
    Xva = vec.transform(X[va])
    candidates = [{"name": "Baseline: sempre a classe mais comum",
                   **scores(y[va], DummyClassifier(strategy="most_frequent").fit(Xtr, y[tr]).predict(Xva))},
                  {"name": "TF-IDF + Complement Naive Bayes", **scores(y[va], ComplementNB(alpha=0.3).fit(Xtr, y[tr]).predict(Xva))},
                  {"name": "TF-IDF + Linear SVM (sem probabilidade)", **scores(y[va], LinearSVC(C=0.5).fit(Xtr, y[tr]).predict(Xva))}]
    lr_by_c = {}
    for c in C_GRID:
        lr_by_c[c] = LogisticRegression(C=c, max_iter=3000).fit(Xtr, y[tr])
        candidates.append({"name": f"TF-IDF + Regressão Logística (C={c})", **scores(y[va], lr_by_c[c].predict(Xva))})
    for cand in candidates:
        print(f"  [validação] {cand['name']:<45} acc={cand['accuracy']:.4f} F1={cand['macroF1']:.4f}")

    best_c = max(C_GRID, key=lambda c: next(x["macroF1"] for x in candidates if x["name"].endswith(f"(C={c})")))
    lr = lr_by_c[best_c]
    classes = lr.classes_

    f1_by_eps = {eps: f1_score(y[va], classes[(Xva @ prune(lr.coef_, eps).T + lr.intercept_).argmax(1)], average="macro")
                 for eps in EPS_GRID}
    coef_eps = max(e for e in EPS_GRID if f1_by_eps[0.0] - f1_by_eps[e] <= MAX_F1_DROP)
    coef = prune(lr.coef_, coef_eps)
    intercept = lr.intercept_.round(4)
    print(f"C={best_c}; F1 por ε: { {e: round(v, 4) for e, v in f1_by_eps.items()} } → ε={coef_eps}")

    vocab = set(vec.vocabulary_)
    sv = Scored(X[va], y[va], vec, coef, intercept, classes, vocab, rules)
    ood_t = float(np.floor(np.quantile(sv.known, OOD_QUANTILE) * 100) / 100)

    best = None
    is_admin = sv.labels == rules["adminRightsCategory"]
    for admin_t in ADMIN_GRID:
        for conf_t in CONF_GRID:
            route, _ = sv.routes(float(conf_t), ood_t, admin_t, rules)
            auto = route == "auto"
            if not auto.any():
                continue
            acc = (sv.pred[auto] == sv.labels[auto]).mean()
            leak = (auto & is_admin).sum() / is_admin.sum()
            if acc < MIN_AUTO_ACCURACY or leak > MAX_ADMIN_LEAK:
                continue
            key = (auto.mean(), admin_t is None, admin_t or 0, conf_t)
            if best is None or key > best[0]:
                best = (key, float(conf_t), admin_t, acc, leak)
    if best is None:
        raise SystemExit("nenhuma combinação de limiares atende aos critérios na validação")
    _, conf_t, admin_t, va_auto_acc, va_leak = best
    print(f"[validação] limiares: confiança={conf_t} guarda={ood_t} privilégio={admin_t} "
          f"→ auto={best[0][0]:.4f} acerto={va_auto_acc:.4f} vazamento AR={va_leak:.4f}")

    selection = {
        "model": f"TF-IDF (1-2 gramas, {MAX_FEATURES // 1000}k termos) + Regressão Logística",
        "C": best_c,
        "coefEps": coef_eps,
        "confidenceThreshold": conf_t,
        "oodThreshold": ood_t,
        "adminRightsThreshold": admin_t,
        "criteria": [
            "Modelo: maior F1 macro na validação entre modelos com probabilidade (necessária para limiar e fila humana).",
            f"Poda: maior ε com queda de F1 macro de validação ≤ {MAX_F1_DROP * 100:.1f} ponto.",
            f"Guarda de domínio: quantil {OOD_QUANTILE * 100:.0f}% da fração de palavras conhecidas na validação.",
            f"Limiares de confiança e privilégio: maior cobertura automática com a política completa, sujeita a acerto "
            f"≥ {MIN_AUTO_ACCURACY * 100:.0f}% nos automáticos e vazamento ≤ {MAX_ADMIN_LEAK * 100:.0f}% dos pedidos de privilégio.",
        ],
        "candidates": candidates,
    }
    # Congela a seleção antes de tocar no teste.
    frozen = json.dumps(selection, sort_keys=True)

    # ---------------- avaliação final (teste, uma vez) ----------------
    st = Scored(X[te], y[te], vec, coef, intercept, classes, vocab, rules)
    assert json.dumps(selection, sort_keys=True) == frozen
    rng = np.random.default_rng(SEED)
    acc_ci, f1_ci = bootstrap_ci(y[te], st.pred, rng)
    p, rc, f, s = precision_recall_fscore_support(y[te], st.pred, labels=classes)
    order = pd.Series(s, index=classes).sort_values(ascending=False).index.tolist()
    per_class = [{"label": c, "precision": r(p[i]), "recall": r(rc[i]), "f1": r(f[i]), "support": int(s[i])}
                 for c in order for i in [list(classes).index(c)]]
    test = {**scores(y[te], st.pred), "accuracyCI": acc_ci, "macroF1CI": f1_ci,
            "baselineAccuracy": r((y[te] == pd.Series(y[tr]).mode()[0]).mean()),
            "perClass": per_class,
            "confusion": {"labels": order, "matrix": confusion_matrix(y[te], st.pred, labels=order).tolist()}}
    print(f"[teste] acc={test['accuracy']} {acc_ci} F1={test['macroF1']} {f1_ci}")

    # ---------------- cruzamento com o Dataset 1 (fora de qualquer seleção) ----------------
    d1 = load_d1()
    d1_text = (d1["Ticket Subject"] + " " + d1.apply(
        lambda row: row["Ticket Description"].replace("{product_purchased}", row["Product Purchased"]), axis=1)).to_numpy()
    sd = Scored(d1_text, np.array([""] * len(d1)), vec, coef, intercept, classes, vocab, rules)
    d1_route, _ = sd.routes(conf_t, ood_t, admin_t, rules)
    confident = sd.conf >= conf_t
    hw = float((sd.pred[confident] == "Hardware").mean())
    d1_ood, te_ood = float((sd.known < ood_t).mean()), float((st.known < ood_t).mean())
    cross = {
        "note": (f"Aplicado aos {len(d1)} tickets do Dataset 1 (e-commerce), o modelo de TI interna passa do limiar de "
                 f"confiança em {br(confident.mean())} dos casos, e {hw * 100:.0f}% deles viram 'Hardware', inclusive "
                 f"pedidos de pagamento. Confiança alta não protege contra outro domínio. O guarda de vocabulário barra "
                 f"{br(d1_ood)} desses tickets e {br(te_ood)} do teste do próprio domínio."),
        "n": int(len(d1)), "confidentShare": r(confident.mean()), "confidentPredictedHardware": r(hw),
        "oodFlagged": r(d1_ood), "inDomainOodFlagged": r(te_ood),
        "routes": [{"route": k, "share": r((d1_route == k).mean())} for k in ["auto", "revisao_humana", "escalar"]],
    }
    print("[D1]", cross["routes"], "barrado pelo guarda:", cross["oodFlagged"])

    write_json("model_metrics.json", {"seed": SEED, "splits": splits, "selection": selection, "test": test,
                                      "exploratory": EXPLORATORY, "crossDomain": cross})

    # ---------------- exports ----------------
    terms = [t for t, _ in sorted(vec.vocabulary_.items(), key=lambda kv: kv[1])]
    weights = {t: [float(v) for v in coef[:, j]] for j, t in enumerate(terms) if np.any(coef[:, j])}
    model = {
        "version": MODEL_VERSION,
        "classes": list(classes),
        "thresholds": {"confidence": conf_t, "ood": ood_t, "adminRights": admin_t},
        "stopWords": sorted(ENGLISH_STOP_WORDS),
        "idf": {t: round(float(vec.idf_[j]), 5) for j, t in enumerate(terms)},
        "weights": weights,
        "intercept": [float(v) for v in intercept],
    }
    path = write_json("model.json", model, generated=False, compact=True)
    print(f"model.json: {path.stat().st_size / 1e6:.2f} MB")

    rng = np.random.default_rng(SEED)
    items = lambda ids: [{"id": int(i), "text": X[i], "label": y[i]} for i in ids]  # noqa: E731
    write_json("holdout.json", {"note": "Amostra aleatória do conjunto de TESTE (nunca usado em treino ou seleção).",
                                "items": items(rng.choice(te, HOLDOUT_EXPORT, replace=False))})
    write_json("neighbors.json", {"note": "Amostra do TREINO usada para mostrar tickets similares.",
                                  "items": items(rng.choice(tr, NEIGHBORS_EXPORT, replace=False))})

    ARTIFACTS.mkdir(exist_ok=True)
    dump = lambda name, obj: (ARTIFACTS / name).write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")),  # noqa: E731
                                                           encoding="utf-8")
    dump("val_split.json", {"items": items(va)})
    dump("test_split.json", {"items": items(te)})
    preds = {}
    for name, ids, sc in [("validation", va, sv), ("test", te, st)]:
        route, reason = sc.routes(conf_t, ood_t, admin_t, rules)
        preds[name] = [{"id": int(i), "label": sc.pred[k], "confidence": round(float(sc.conf[k]), 6),
                        "route": route[k], "reasonCode": reason[k]} for k, i in enumerate(ids)]
    dump("python_predictions.json", preds)
    print("artefatos:", sorted(p.name for p in ARTIFACTS.iterdir()))


if __name__ == "__main__":
    main()
