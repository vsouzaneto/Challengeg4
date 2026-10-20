"""Text analysis of comments/captions: sentiment (VADER), distinctive keywords (log-odds) and topics (NMF)."""
import re
from collections import Counter

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

SEED = 42
TOKEN = re.compile(r"[a-z]{3,}")
_analyzer = SentimentIntensityAnalyzer()


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN.findall(text.lower()) if t not in ENGLISH_STOP_WORDS]


def sentiment(texts: pd.Series) -> pd.Series:
    """VADER compound score in [-1, 1]; empty text → NaN."""
    return texts.map(lambda t: _analyzer.polarity_scores(t)["compound"] if t.strip() else np.nan)


def sentiment_label(scores: pd.Series) -> pd.Series:
    return pd.cut(scores, [-1.01, -0.05, 0.05, 1.01], labels=["negativo", "neutro", "positivo"])


def compare_sentiment(scores: pd.Series, group: pd.Series) -> dict:
    """Mean sentiment per group and Mann-Whitney p-value (top vs. rest)."""
    a, b = scores[group].dropna(), scores[~group].dropna()
    return {"mean_top": a.mean(), "mean_rest": b.mean(), "diff": a.mean() - b.mean(),
            "p_value": stats.mannwhitneyu(a, b).pvalue}


def log_odds_keywords(texts_a: pd.Series, texts_b: pd.Series, top_n: int = 15, min_count: int = 20) -> pd.DataFrame:
    """Monroe et al. (2008) log-odds ratio with informative Dirichlet prior.

    z > 1.96 → word significantly more typical of group A; z < -1.96 → of group B.
    Better than raw frequency/TF-IDF because it controls for word rarity and sample size.
    """
    ca = Counter(t for text in texts_a for t in tokenize(text))
    cb = Counter(t for text in texts_b for t in tokenize(text))
    prior = ca + cb
    na, nb, n0 = sum(ca.values()), sum(cb.values()), sum(prior.values())
    rows = []
    for word, a0 in prior.items():
        if a0 < min_count:
            continue
        ya, yb = ca[word], cb[word]
        delta = np.log((ya + a0) / (na + n0 - ya - a0)) - np.log((yb + a0) / (nb + n0 - yb - a0))
        var = 1 / (ya + a0) + 1 / (yb + a0)
        rows.append({"word": word, "count_a": ya, "count_b": yb, "z": delta / np.sqrt(var)})
    table = pd.DataFrame(rows).sort_values("z", ascending=False, ignore_index=True)
    return pd.concat([table.head(top_n), table.tail(top_n)])


def topics(texts: pd.Series, n_topics: int = 6, top_words: int = 8) -> pd.DataFrame:
    """NMF topics over TF-IDF; returns the top words of each topic."""
    vectorizer = TfidfVectorizer(tokenizer=tokenize, lowercase=False, token_pattern=None, min_df=20, max_df=0.5)
    matrix = vectorizer.fit_transform(texts[texts.str.strip() != ""])
    model = NMF(n_components=n_topics, random_state=SEED, init="nndsvda", max_iter=400).fit(matrix)
    vocab = np.array(vectorizer.get_feature_names_out())
    return pd.DataFrame({f"tópico {i + 1}": vocab[row.argsort()[::-1][:top_words]] for i, row in enumerate(model.components_)})
