"""
Motor de triagem: classifica, explica e decide o nível de automação de cada ticket.

Decisão em camadas (a ordem importa):
  1. Trava de domínio: se o ticket não se parece com nada do histórico OU se o modelo não
     reconhece a maior parte das palavras dele, vai para humano, mesmo que o classificador diga
     ter "certeza". Medido: sem as travas, 34,1% dos tickets de outro domínio (Dataset 1) iriam para o automático; com elas, 10,8%.
     A checagem de vocabulário foi incluída depois que um ticket em português, com uma única
     palavra conhecida ("status"), passou pela checagem de similaridade.
  2. Faixa de confiança por categoria, com limiares calibrados na VALIDAÇÃO:
       auto   -> roteia sozinho (precisão >= 95% na validação)
       sugere -> mostra as 2 categorias mais prováveis; o humano escolhe com 1 clique
       humano -> classificação manual
  3. Política de ação (politica.py): rotear ≠ executar. Algumas categorias podem ser roteadas
     automaticamente, mas a AÇÃO pedida sempre exige aprovação humana.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestNeighbors

RAIZ = Path(__file__).resolve().parents[3]          # submissions/arthur-leite
DADOS = RAIZ / "data/ds2_it_tickets/all_tickets_processed_improved_v3.csv"
MODELO = RAIZ / "data/cache/motor_triagem.joblib"

PRECISAO_AUTO = 0.95
TOP2_SUGERE = 0.90
MIN_VALIDACAO_POR_CLASSE = 150   # abaixo disso o limiar da classe é instável: usa o global
SIMILARIDADE_MINIMA = 0.20       # trava de domínio (cosseno com o vizinho mais próximo do histórico)
COBERTURA_MINIMA = 0.50          # trava de domínio: fração das palavras do ticket que o modelo conhece


def preparar(texto: str) -> str:
    """Aplica ao texto novo o mesmo pré-processamento do Dataset 2 (minúsculas, só letras, sem stopwords)."""
    palavras = "".join(c if c.isalpha() or c.isspace() else " " for c in texto.lower()).split()
    return " ".join(p for p in palavras if p not in ENGLISH_STOP_WORDS)


def dividir(d: pd.DataFrame):
    """Mesma divisão do benchmark: 20% de teste, e o resto em treino/validação (seed 42)."""
    resto, te = train_test_split(d, test_size=0.2, stratify=d["Topic_group"], random_state=42)
    tr, va = train_test_split(resto, test_size=0.125, stratify=resto["Topic_group"], random_state=42)
    return tr, va, te


def _limiar(conf: np.ndarray, acerto: np.ndarray, alvo: float, teto: float = np.inf) -> float:
    """Menor limiar t tal que os tickets com confiança em [t, teto) tenham taxa de acerto >= alvo."""
    m = conf < teto
    c, a = conf[m], acerto[m]
    ordem = np.argsort(-c)
    prec = np.cumsum(a[ordem]) / np.arange(1, len(c) + 1)
    ok = np.where(prec >= alvo)[0]
    return float(c[ordem][ok.max()]) if len(ok) else float(min(teto, 1.01))


@dataclass
class Resultado:
    categoria: str
    confianca: float
    top2: list[tuple[str, float]]
    faixa: str                      # auto | sugere | humano
    motivo: str
    palavras_chave: list[tuple[str, float]] = field(default_factory=list)
    similares: list[dict] = field(default_factory=list)
    similaridade: float = 0.0
    cobertura_vocab: float = 0.0


class MotorTriagem:
    def __init__(self, vec, clf, nn, base_vizinhos, limiares, limiar_sugere):
        self.vec, self.clf, self.nn = vec, clf, nn
        self.base_vizinhos = base_vizinhos
        self.limiares = limiares          # {categoria: limiar auto}
        self.limiar_sugere = limiar_sugere

    # ---------- treino ----------
    @classmethod
    def treinar(cls) -> "MotorTriagem":
        d = pd.read_csv(DADOS)
        tr, va, _ = dividir(d)
        vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
        Xtr = vec.fit_transform(tr["Document"])
        clf = LogisticRegression(max_iter=3000, C=5).fit(Xtr, tr["Topic_group"])

        P = clf.predict_proba(vec.transform(va["Document"]))
        conf, pred = P.max(1), clf.classes_[P.argmax(1)]
        # to_numpy(dtype=object): no pandas 3, colunas de texto são Arrow e .values não aceita [:, None]
        y_va = va["Topic_group"].to_numpy(dtype=object)
        acerto = (pred == y_va).astype(float)
        top2 = (clf.classes_[np.argsort(-P, 1)[:, :2]] == y_va[:, None]).any(1).astype(float)

        global_auto = _limiar(conf, acerto, PRECISAO_AUTO)
        limiares = {}
        for c in clf.classes_:
            m = pred == c
            limiares[c] = (max(global_auto, _limiar(conf[m], acerto[m], PRECISAO_AUTO))
                           if m.sum() >= MIN_VALIDACAO_POR_CLASSE else global_auto)
        limiar_sugere = _limiar(conf, top2, TOP2_SUGERE, teto=global_auto)

        nn = NearestNeighbors(n_neighbors=3, metric="cosine").fit(Xtr)
        base = tr[["Document", "Topic_group"]].reset_index(drop=True)
        motor = cls(vec, clf, nn, base, limiares, limiar_sugere)
        MODELO.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(motor, MODELO, compress=3)
        return motor

    @classmethod
    def carregar(cls) -> "MotorTriagem":
        return joblib.load(MODELO) if MODELO.exists() else cls.treinar()

    # ---------- inferência ----------
    def cobertura_vocab(self, texto_preparado: str) -> float:
        palavras = texto_preparado.split()
        return sum(p in self.vec.vocabulary_ for p in palavras) / len(palavras) if palavras else 0.0

    def explicar(self, x, categoria: str, k: int = 6) -> list[tuple[str, float]]:
        """Palavras do ticket que mais empurraram para a categoria escolhida (peso × presença)."""
        i = list(self.clf.classes_).index(categoria)
        contrib = x.multiply(self.clf.coef_[i]).tocsr()
        idx = contrib.indices[np.argsort(-contrib.data)][:k]
        termos = self.vec.get_feature_names_out()
        return [(termos[j], float(contrib[0, j])) for j in idx if contrib[0, j] > 0]

    def classificar(self, texto: str, ja_preparado: bool = False) -> Resultado:
        texto_p = texto if ja_preparado else preparar(texto)
        x = self.vec.transform([texto_p])
        cob = self.cobertura_vocab(texto_p)
        p = self.clf.predict_proba(x)[0]
        ordem = np.argsort(-p)
        cat, conf = self.clf.classes_[ordem[0]], float(p[ordem[0]])
        top2 = [(self.clf.classes_[j], float(p[j])) for j in ordem[:2]]

        dist, viz = self.nn.kneighbors(x)
        sim = float(1 - dist[0][0])
        similares = [{"texto": self.base_vizinhos.loc[j, "Document"], "categoria": self.base_vizinhos.loc[j, "Topic_group"],
                      "similaridade": float(1 - dd)} for j, dd in zip(viz[0], dist[0])]

        if x.nnz == 0 or cob < COBERTURA_MINIMA:
            faixa, motivo = "humano", (f"O modelo só reconhece {cob:.0%} das palavras deste ticket (mínimo {COBERTURA_MINIMA:.0%}): "
                                       "idioma ou assunto fora do que ele aprendeu.")
        elif sim < SIMILARIDADE_MINIMA:
            faixa, motivo = "humano", (f"Ticket diferente de tudo no histórico (similaridade {sim:.2f} < {SIMILARIDADE_MINIMA}). "
                                       "A confiança do modelo não é confiável fora do domínio.")
        elif conf >= self.limiares[cat]:
            faixa, motivo = "auto", f"Confiança {conf:.0%} ≥ limiar de {cat} ({self.limiares[cat]:.0%})."
        elif conf >= self.limiar_sugere:
            faixa, motivo = "sugere", f"Confiança {conf:.0%}: entre as 2 opções, a certa aparece em ≥ 90% dos casos."
        else:
            faixa, motivo = "humano", f"Confiança {conf:.0%} abaixo de {self.limiar_sugere:.0%}: o modelo não sabe."

        return Resultado(cat, conf, top2, faixa, motivo, self.explicar(x, cat) if x.nnz else [], similares, sim, cob)

    def classificar_lote(self, textos: pd.Series) -> pd.DataFrame:
        """Versão vetorizada para filas grandes (textos já no formato do Dataset 2)."""
        X = self.vec.transform(textos)
        P = self.clf.predict_proba(X)
        cat = self.clf.classes_[P.argmax(1)]
        conf = P.max(1)
        sim = 1 - self.nn.kneighbors(X, n_neighbors=1)[0].ravel()
        cob = textos.map(self.cobertura_vocab).to_numpy(dtype=float)
        lim = np.array([self.limiares[c] for c in cat])
        barrado = (sim < SIMILARIDADE_MINIMA) | (cob < COBERTURA_MINIMA)
        faixa_modelo = np.where(conf >= lim, "auto", np.where(conf >= self.limiar_sugere, "sugere", "humano"))
        faixa = np.where(barrado, "humano", faixa_modelo)
        motivo = np.where(barrado, "trava de domínio", np.where(faixa == "humano", "confiança baixa", ""))
        top2 = self.clf.classes_[np.argsort(-P, 1)[:, :2]]
        return pd.DataFrame({"categoria": cat, "confianca": conf, "faixa": faixa, "motivo_humano": motivo,
                             "faixa_sem_travas": faixa_modelo, "similaridade": sim,
                             "top2_a": top2[:, 0], "top2_b": top2[:, 1]}, index=textos.index)


if __name__ == "__main__":
    m = MotorTriagem.treinar()
    print("Limiar auto por categoria:", {k: round(v, 3) for k, v in m.limiares.items()})
    print("Limiar sugere:", round(m.limiar_sugere, 3))


# ---------- decisão final: classificador + política ----------
FILA_SEGURANCA = "Segurança da Informação"


@dataclass
class Decisao:
    fila: str
    modo: str              # "Roteado automaticamente" | "Sugestão: humano confirma" | "Humano classifica"
    executar: str          # quem executa a ação pedida
    escalar: bool
    pode_rascunho: bool
    explicacao: list[str]


def decidir(r: Resultado, pol) -> Decisao:
    """Combina a faixa do classificador com a política. A política SEMPRE vence."""
    modo = {"auto": "Roteado automaticamente", "sugere": "Sugestão: humano confirma",
            "humano": "Humano classifica"}[r.faixa]
    fila = r.categoria if r.faixa != "humano" else "Triagem humana"
    explic = [r.motivo]
    if "seguranca" in pol.alertas:
        fila, modo = FILA_SEGURANCA, "Escalado pela política (sobrepõe o classificador)"
        explic.append(f"O classificador sugeriu {r.categoria}, mas há sinal de incidente de segurança.")
    executar = "Humano, com aprovação" if pol.exige_humano_para_executar else "Agente da fila (fluxo normal)"
    return Decisao(fila, modo, executar, pol.escalar, pol.pode_gerar_rascunho and r.faixa != "humano", explic + pol.descrever())
