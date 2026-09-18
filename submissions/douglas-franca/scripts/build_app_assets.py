"""Gera os exemplos fictícios que o Decision Gate usa (app/assets/).

O dataset do challenge NÃO é versionado: o app o carrega por src/app_data.py
(data/raw/ local ou download do Kaggle na primeira abertura).

1. exemplo_sintetico_contrato_de_dados.csv: dado FICTÍCIO no formato do contrato de dados (G4),
   gerado com variação realista (cauda longa, zeros, likes acompanhando views). Serve só para
   mostrar que o Gate 0 aprova um arquivo bem instrumentado. Não é dado real.
2. exemplo_sintetico_resultado_teste.csv: resultado FICTÍCIO de um teste de 30 dias (dois braços).

Uso: uv run python scripts/build_app_assets.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "app" / "assets"
PLATFORMS = ["Instagram", "TikTok", "YouTube"]


def build_contract_example(rng: np.random.Generator, n: int = 3_000) -> pd.DataFrame:
    creators = pd.DataFrame({
        "creator_id": [f"CR{i:04d}" for i in range(150)],
        "creator_name": [f"creator_ficticio_{i:03d}" for i in range(150)],
        "follower_count": rng.lognormal(mean=11, sigma=1.3, size=150).astype(int),
    })
    idx = rng.integers(0, len(creators), n)
    posts = creators.iloc[idx].reset_index(drop=True)
    reach = rng.lognormal(mean=np.log(0.08), sigma=1.0, size=n)
    mean_views = np.maximum(posts.follower_count * reach, 1)
    views = rng.negative_binomial(n=1.2, p=1.2 / (1.2 + mean_views))
    er = rng.beta(2, 30, size=n)
    likes = rng.binomial(views, er * 0.8)
    shares = rng.binomial(views, er * 0.1)
    comments = rng.binomial(views, er * 0.1)
    sponsored = rng.random(n) < 0.3
    published = pd.Timestamp("2026-06-01", tz="America/Sao_Paulo") + pd.to_timedelta(rng.integers(0, 90 * 24 * 60, n), unit="min")
    campaign = np.where(sponsored, [f"CRM-{i:05d}" for i in rng.integers(0, 60, n)], None)
    return pd.DataFrame({
        "post_id": [f"P{i:06d}" for i in range(n)],
        "creator_id": posts.creator_id,
        "creator_name": posts.creator_name,
        "platform": rng.choice(PLATFORMS, n),
        "published_at": published.map(lambda t: t.isoformat()),
        "format": rng.choice(["video", "imagem", "carrossel"], n, p=[0.5, 0.25, 0.25]),
        "is_sponsored": sponsored,
        "campaign_id": campaign,
        "custo_total": np.where(sponsored, rng.choice([500, 1_200, 3_000, 15_000], n), np.nan),
        "views": views,
        "likes": likes,
        "shares": shares,
        "comments": comments,
        "source_system": "api_da_plataforma_ficticia",
        "extracted_at": "2026-09-01T08:00:00-03:00",
    })


def build_experiment_example(rng: np.random.Generator, n_per_arm: int = 400) -> pd.DataFrame:
    control = np.clip(rng.normal(8.0, 5.0, n_per_arm), 0, None)
    treatment = np.clip(rng.normal(9.8, 5.0, n_per_arm), 0, None)
    return pd.DataFrame({
        "test_arm": ["comparacao"] * n_per_arm + ["tratamento"] * n_per_arm,
        "engagement_rate_pp": np.concatenate([control, treatment]).round(3),
    })


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(2026)
    build_contract_example(rng).to_csv(ASSETS / "exemplo_sintetico_contrato_de_dados.csv", index=False)
    build_experiment_example(rng).to_csv(ASSETS / "exemplo_sintetico_resultado_teste.csv", index=False)
    for f in sorted(ASSETS.iterdir()):
        print(f"{f.name}: {f.stat().st_size / 1e3:,.0f} KB")


if __name__ == "__main__":
    main()
