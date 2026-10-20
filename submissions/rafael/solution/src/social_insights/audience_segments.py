"""Audience segmentation: clusters audience profiles (age × gender × country) by the content they consume.

Each profile is described by its consumption mix (share of posts by platform, format, theme, language and % sponsored).
Performance metrics are left out on purpose: the groups describe *who consumes what*, not who performs better.
Every result is checked against a shuffled baseline (profile labels assigned at random to posts) and split-half stability.
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler

PROFILE = ["audience_age_distribution", "audience_gender_distribution", "audience_location"]
MIX = ["platform", "content_type", "content_category", "language"]
FILTERS = ["platform", "content_type", "content_category"]
KS = range(2, 7)
MIN_POSTS = 20        # profiles with fewer posts have a mix too noisy to cluster
MIN_PROFILES = 12
MIN_TRAIT_SHARE = 0.15
N_NULL = 20
N_SPLITS = 5
SEED = 42


def _encode(df: pd.DataFrame) -> dict:
    prof_codes, profiles = pd.MultiIndex.from_frame(df[PROFILE]).factorize()
    mix = []
    for m in MIX:
        codes, levels = pd.factorize(df[m], sort=True)
        mix.append((m, codes, list(levels)))
    return {"prof": prof_codes, "profiles": profiles, "mix": mix, "sponsored": df["is_sponsored"].astype(str).eq("True").to_numpy(dtype=float)}  # bool or "True"/"False" (dashboard posts)


def _features(enc: dict, prof: np.ndarray, rows: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Consumption shares per profile (rows = profiles) and post counts; `rows` restricts to a subset of posts."""
    n = len(enc["profiles"])
    p = prof if rows is None else prof[rows]
    counts = np.bincount(p, minlength=n).astype(float)
    safe = np.maximum(counts, 1)[:, None]
    blocks = []
    for _, codes, levels in enc["mix"]:
        c = codes if rows is None else codes[rows]
        blocks.append(np.bincount(p * len(levels) + c, minlength=n * len(levels)).reshape(n, len(levels)) / safe)
    s = enc["sponsored"] if rows is None else enc["sponsored"][rows]
    blocks.append((np.bincount(p, weights=s, minlength=n) / safe[:, 0])[:, None])
    return np.hstack(blocks), counts


def _columns(enc: dict) -> list[dict]:
    return [{"campo": m, "valor": str(v)} for m, _, levels in enc["mix"] for v in levels] + [{"campo": "is_sponsored", "valor": "True"}]


def _cluster(X: np.ndarray, k: int, n_init: int = 10) -> tuple[np.ndarray, float]:
    Z = StandardScaler().fit_transform(X)
    labels = KMeans(k, n_init=n_init, random_state=SEED).fit_predict(Z)
    return labels, silhouette_score(Z, labels)


def _best(X: np.ndarray, ks, n_init: int = 10) -> tuple[int, np.ndarray, dict]:
    fits = {k: _cluster(X, k, n_init) for k in ks}
    k = max(fits, key=lambda kk: fits[kk][1])
    return k, fits[k][0], {kk: f[1] for kk, f in fits.items()}


def _reliability(sil: float, null_p95: float, ari: float) -> str:
    above, stable = sil > null_p95, ari >= 0.5
    return "consistente" if above and stable else "fraco" if above or stable else "nao_sustenta"


def segment(df: pd.DataFrame, filtros: dict[str, str] | None = None, k: int | None = None) -> dict:
    """Cluster the audience profiles of the posts matching `filtros` ({field: value}); `k=None` picks k by silhouette."""
    filtros = {f: v for f, v in (filtros or {}).items() if v}
    unknown = set(filtros) - set(FILTERS)
    if unknown:
        raise ValueError(f"filtro desconhecido: {sorted(unknown)}")
    sub = df
    for f, v in filtros.items():
        sub = sub[sub[f].astype(str) == str(v)]
    base = {"filtros": filtros, "posts": int(len(sub)), "min_posts": MIN_POSTS}
    if sub.empty:
        return base | {"erro": "Nenhum post com esses filtros."}
    enc = _encode(sub)
    F, counts = _features(enc, enc["prof"])
    keep = counts >= MIN_POSTS
    if keep.sum() < MIN_PROFILES:
        return base | {"erro": f"Poucos perfis com pelo menos {MIN_POSTS} posts ({int(keep.sum())}). Remova um filtro."}
    varies = F[keep].std(axis=0) > 0  # a filtered field (e.g. one platform) is constant and says nothing
    X = F[keep][:, varies]
    ks = [k] if k else list(KS)
    k, labels, sils = _best(X, ks)

    rng = np.random.default_rng(SEED)
    null = np.array([max(_best(_features(enc, rng.permutation(enc["prof"]))[0][keep][:, varies], ks, n_init=3)[2].values())
                     for _ in range(N_NULL)])
    aris = []
    for _ in range(N_SPLITS):
        idx = rng.permutation(len(sub))
        halves = [_features(enc, enc["prof"], np.sort(h))[0][keep][:, varies] for h in (idx[: len(idx) // 2], idx[len(idx) // 2:])]
        aris.append(adjusted_rand_score(_cluster(halves[0], k)[0], _cluster(halves[1], k)[0]))
    ari, null_p95 = float(np.mean(aris)), float(np.percentile(null, 95))

    # Biggest group first, so "Grupo A" is always the largest.
    post_counts = counts[keep]
    order = np.argsort([-post_counts[labels == s].sum() for s in range(k)])
    labels = np.argsort(order)[labels]

    profiles = enc["profiles"][keep]
    prof_df = pd.DataFrame(list(profiles), columns=PROFILE).assign(posts=post_counts.astype(int), grupo=labels)
    cols = [c for c, v in zip(_columns(enc), varies) if v]
    mean_all = X.mean(axis=0)
    coords = PCA(2, random_state=SEED).fit_transform(StandardScaler().fit_transform(X))
    prof_df["x"], prof_df["y"] = coords[:, 0], coords[:, 1]

    groups = []
    for s in range(k):
        members = prof_df[prof_df.grupo == s]
        mix = X[labels == s].mean(axis=0)
        lift = np.where(mean_all > 0, mix / np.where(mean_all > 0, mean_all, 1) - 1, 0)
        consumo = sorted(({**c, "share": float(m), "media": float(a), "lift": float(l)} for c, m, a, l in zip(cols, mix, mean_all, lift)),
                         key=lambda r: -r["lift"])
        publico = {}
        traits = []
        for field in PROFILE:
            seg_share = members.groupby(field).posts.sum() / members.posts.sum()
            all_share = prof_df.groupby(field).posts.sum() / prof_df.posts.sum()
            rows = [{"valor": str(v), "share": float(seg_share.get(v, 0)), "lift": float(seg_share.get(v, 0) / all_share[v] - 1)}
                    for v in all_share.index]
            publico[field] = sorted(rows, key=lambda r: -r["share"])
            traits += [{"campo": field, **r} for r in rows if r["share"] >= MIN_TRAIT_SHARE]
        traco = max(traits, key=lambda r: r["lift"]) if traits else None
        groups.append({"grupo": s, "perfis": int(len(members)), "posts": int(members.posts.sum()),
                       "share_posts": float(members.posts.sum() / prof_df.posts.sum()), "traco": traco,
                       "publico": publico, "consumo": consumo})

    return base | {
        "k": int(k), "silhouette": float(sils[k]), "silhouette_por_k": {str(kk): float(v) for kk, v in sils.items()},
        "acaso_media": float(null.mean()), "acaso_p95": null_p95, "estabilidade": ari,
        "confiabilidade": _reliability(sils[k], null_p95, ari),
        "perfis": int(keep.sum()), "perfis_fora": int((~keep & (counts > 0)).sum()), "posts_usados": int(post_counts.sum()),
        "colunas": cols, "grupos": groups, "mapa": prof_df.to_dict("records"),
    }
