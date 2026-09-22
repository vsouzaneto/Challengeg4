"""Painéis do challenge 003 — Won/Lost no resolvido; pipe aberto sem close_value."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .common import (
    DashboardPanels,
    Panel,
    encode_categoricals,
    fit_logistic_panels,
    image_unavailable,
    plot_bar,
    plot_counters,
    plot_heatmap,
    plot_line,
    resolve_dados,
)


def load_crm_tables(dados_dir: str | Path | None = None) -> dict[str, pd.DataFrame]:
    root = resolve_dados("notebook-build-003-lead-scorer", dados_dir)
    return {
        "pipeline": pd.read_csv(root / "sales_pipeline.csv"),
        "accounts": pd.read_csv(root / "accounts.csv"),
        "products": pd.read_csv(root / "products.csv"),
        "teams": pd.read_csv(root / "sales_teams.csv"),
    }


def build_crm_panels(dados_dir: str | Path | None = None) -> DashboardPanels:
    tables = load_crm_tables(dados_dir)
    pipeline = tables["pipeline"]
    accounts = tables["accounts"]
    products = tables["products"]
    teams = tables["teams"]

    pipeline = pipeline.copy()
    pipeline["catalog_product"] = pipeline["product"].replace({"GTXPro": "GTX Pro"})
    resolved = pipeline[pipeline["deal_stage"].isin(["Won", "Lost"])].copy()
    resolved["won"] = (resolved["deal_stage"] == "Won").astype(int)
    open_pipe = pipeline[pipeline["deal_stage"].isin(["Prospecting", "Engaging"])].copy()

    ranking = (
        resolved.groupby("sales_agent", as_index=False)
        .agg(deals=("opportunity_id", "count"), wins=("won", "sum"))
    )
    ranking["win_rate"] = (ranking["wins"] / ranking["deals"]).round(3)
    ranking = ranking.sort_values(["win_rate", "deals"], ascending=[False, False])

    gallery = open_pipe.merge(teams, on="sales_agent", how="left").merge(
        accounts, on="account", how="left"
    )[
        [
            "opportunity_id",
            "sales_agent",
            "deal_stage",
            "product",
            "account",
            "sector",
            "engage_date",
        ]
    ].head(12)

    classification = (
        pipeline.groupby("deal_stage", as_index=False)
        .size()
        .rename(columns={"size": "opportunities"})
        .sort_values("opportunities", ascending=False)
    )

    segmentation = (
        resolved.merge(accounts, on="account", how="left")
        .groupby("sector", as_index=False)
        .agg(deals=("opportunity_id", "count"), wins=("won", "sum"))
    )
    segmentation["win_rate"] = (segmentation["wins"] / segmentation["deals"]).round(3)
    segmentation = segmentation.sort_values("win_rate", ascending=False)

    model_src = resolved.merge(accounts, on="account", how="left").merge(
        products, left_on="catalog_product", right_on="product", how="left", suffixes=("", "_cat")
    )
    model_src["has_account"] = model_src["account"].notna().astype(int)
    model_src["in_catalog"] = model_src["series"].notna().astype(int)
    model_src["sector"] = model_src["sector"].fillna("unknown")
    model_src["catalog_product"] = model_src["catalog_product"].fillna("unknown")
    features = encode_categoricals(model_src, ["catalog_product", "sector"]).join(
        model_src[["has_account", "in_catalog"]]
    )
    fitted = fit_logistic_panels(features, model_src["won"])

    panels = DashboardPanels("crm")
    panels.panels["ranking"] = Panel(
        "ranking",
        "Ranking de benchmark",
        ranking,
        plot_bar(ranking.head(12), "sales_agent", "win_rate", "Ranking — win rate do agente"),
        "Só Won/Lost. Pipe aberto não entra.",
    )
    panels.panels["gallery"] = Panel(
        "gallery",
        "Galeria de entrada",
        gallery,
        plot_bar(
            gallery.groupby("deal_stage", as_index=False).size().rename(columns={"size": "deals"}),
            "deal_stage",
            "deals",
            "Galeria — pipe aberto",
        ),
        "Amostra do pipe aberto. close_value não ordena.",
    )
    panels.panels["classification"] = Panel(
        "classification",
        "Classificação",
        classification,
        plot_bar(classification, "deal_stage", "opportunities", "Classificação — deal_stage"),
    )
    panels.panels["segmentation"] = Panel(
        "segmentation",
        "Segmentação",
        segmentation,
        plot_bar(segmentation.dropna(subset=["sector"]), "sector", "win_rate", "Segmentação — setor"),
    )
    panels.panels["image_segmentation"] = image_unavailable(
        "CRM não tem imagem. Grain = opportunity_id."
    )
    panels.panels["model_stats"] = Panel(
        "model_stats",
        "Estatísticas do modelo",
        fitted["stats"],
        plot_counters(fitted["stats"], "Baseline logístico — Won vs Lost"),
        "Sem close_value no X. Lab 04 já mostrou AUC perto do acaso.",
    )
    panels.panels["confusion_matrix"] = Panel(
        "confusion_matrix",
        "Matriz de confusão",
        pd.DataFrame(fitted["matrix"], index=fitted["labels"], columns=fitted["labels"]),
        plot_heatmap(fitted["matrix"], fitted["labels"], "Matriz de confusão — Won"),
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
