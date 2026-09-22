"""Painéis do challenge 004 — taxa derivada; imagem = content_type, não máscara."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .common import (
    DashboardPanels,
    Panel,
    encode_categoricals,
    fit_logistic_panels,
    plot_bar,
    plot_counters,
    plot_heatmap,
    plot_line,
    resolve_dados,
)


SOCIAL_COLUMNS = [
    "platform",
    "content_type",
    "content_category",
    "views",
    "likes",
    "shares",
    "comments_count",
    "follower_count",
    "is_sponsored",
    "audience_age_distribution",
]


def load_social_table(dados_dir: str | Path | None = None) -> pd.DataFrame:
    root = resolve_dados("notebook-marketing-004-social", dados_dir)
    posts = pd.read_csv(root / "social_media_dataset.csv", usecols=SOCIAL_COLUMNS)
    if "engagement_rate" in posts.columns:
        raise ValueError("engagement_rate nativo não faz parte do dump")
    posts["eng_per_view"] = (
        posts["likes"] + posts["shares"] + posts["comments_count"]
    ) / posts["views"].replace(0, pd.NA)
    posts["creator_band"] = pd.cut(
        posts["follower_count"],
        bins=[-1, 9999, 49999, 199999, 10**12],
        labels=["lt_10k", "10k_50k", "50k_200k", "200k_plus"],
    ).astype(str)
    return posts


def build_social_panels(dados_dir: str | Path | None = None) -> DashboardPanels:
    posts = load_social_table(dados_dir)
    usable = posts.dropna(subset=["eng_per_view"])

    ranking = (
        usable.groupby(
            ["platform", "content_type", "content_category", "creator_band", "is_sponsored"],
            as_index=False,
        )
        .agg(posts=("views", "count"), eng_per_view=("eng_per_view", "mean"), avg_shares=("shares", "mean"))
    )
    ranking = ranking[ranking["posts"] >= 30].sort_values("eng_per_view", ascending=False)
    ranking["eng_per_view"] = ranking["eng_per_view"].round(4)
    ranking["avg_shares"] = ranking["avg_shares"].round(1)

    gallery = usable[
        [
            "platform",
            "content_type",
            "content_category",
            "creator_band",
            "is_sponsored",
            "views",
            "likes",
            "shares",
        ]
    ].head(12)

    classification = (
        usable.groupby("content_type", as_index=False)
        .size()
        .rename(columns={"size": "posts"})
        .sort_values("posts", ascending=False)
    )

    segmentation = (
        usable.groupby(["platform", "content_category"], as_index=False)
        .agg(posts=("views", "count"), eng_per_view=("eng_per_view", "mean"))
    )
    segmentation = segmentation[segmentation["posts"] >= 50].sort_values("eng_per_view")
    segmentation["eng_per_view"] = segmentation["eng_per_view"].round(4)

    image = (
        usable.groupby("content_type", as_index=False)
        .agg(posts=("views", "count"), eng_per_view=("eng_per_view", "mean"))
        .sort_values("posts", ascending=False)
    )
    image["eng_per_view"] = image["eng_per_view"].round(4)
    image.insert(0, "available", True)
    image.insert(1, "grain", "content_type")
    image_note = "Proxy: content_type (Image/Video/…). Sem pixels e sem máscara."

    sample = usable.sample(n=min(3500, len(usable)), random_state=21)
    median_eng = sample["eng_per_view"].median()
    sample["high_eng"] = (sample["eng_per_view"] > median_eng).astype(int)
    features = encode_categoricals(
        sample, ["platform", "content_type", "content_category", "creator_band"]
    ).join(sample[["is_sponsored"]].astype(int))
    fitted = fit_logistic_panels(features, sample["high_eng"])

    rank_chart = ranking.head(12).copy()
    rank_chart["cell"] = (
        rank_chart["platform"].astype(str)
        + " / "
        + rank_chart["content_type"].astype(str)
        + " / "
        + rank_chart["creator_band"].astype(str)
    )

    panels = DashboardPanels("social")
    panels.panels["ranking"] = Panel(
        "ranking",
        "Ranking de benchmark",
        ranking.head(15),
        plot_bar(rank_chart, "cell", "eng_per_view", "Ranking — taxa derivada controlada"),
        "Taxa = (likes+shares+comments)/views. Sem engagement_rate nativo.",
    )
    panels.panels["gallery"] = Panel(
        "gallery",
        "Galeria de entrada",
        gallery,
        plot_bar(
            gallery.groupby("platform", as_index=False).size().rename(columns={"size": "posts"}),
            "platform",
            "posts",
            "Galeria — amostra por plataforma",
        ),
    )
    panels.panels["classification"] = Panel(
        "classification",
        "Classificação",
        classification,
        plot_bar(classification, "content_type", "posts", "Classificação — content_type"),
    )
    panels.panels["segmentation"] = Panel(
        "segmentation",
        "Segmentação",
        segmentation.head(20),
        plot_bar(
            segmentation.groupby("platform", as_index=False)["eng_per_view"].mean(),
            "platform",
            "eng_per_view",
            "Segmentação — taxa média por plataforma",
        ),
    )
    panels.panels["image_segmentation"] = Panel(
        "image_segmentation",
        "Segmentação de imagem",
        image,
        plot_bar(image, "content_type", "posts", "Segmentação de imagem — content_type"),
        image_note,
    )
    panels.panels["model_stats"] = Panel(
        "model_stats",
        "Estatísticas do modelo",
        fitted["stats"],
        plot_counters(fitted["stats"], "Baseline logístico — taxa acima da mediana"),
        f"Label = eng_per_view > {median_eng:.4f} na amostra.",
    )
    panels.panels["confusion_matrix"] = Panel(
        "confusion_matrix",
        "Matriz de confusão",
        pd.DataFrame(fitted["matrix"], index=fitted["labels"], columns=fitted["labels"]),
        plot_heatmap(fitted["matrix"], fitted["labels"], "Matriz de confusão — alta taxa"),
    )
    panels.panels["learning_curve"] = Panel(
        "learning_curve",
        "Curva de aprendizado",
        fitted["curve"],
        plot_line(
            fitted["curve"],
            "train_size",
            ["train_accuracy", "test_accuracy"],
            "Curva de aprendizado",
        ),
    )
    panels.panels["bias_variance"] = Panel(
        "bias_variance",
        "Viés / variância",
        fitted["bias_variance"],
        plot_bar(
            pd.DataFrame(
                {
                    "corte": ["treino", "teste"],
                    "accuracy": [
                        fitted["bias_variance"].loc[0, "train_accuracy"],
                        fitted["bias_variance"].loc[0, "test_accuracy"],
                    ],
                }
            ),
            "corte",
            "accuracy",
            "Viés / variância — acurácia",
        ),
        str(fitted["bias_variance"].loc[0, "reading"]),
    )
    panels.require_complete()
    return panels
