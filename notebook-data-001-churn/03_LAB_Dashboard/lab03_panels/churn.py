"""Painéis do challenge 001 — label = evento em ravenstack_churn_events."""

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


def load_churn_tables(dados_dir: str | Path | None = None) -> dict[str, pd.DataFrame]:
    root = resolve_dados("notebook-data-001-churn", dados_dir)
    return {
        "accounts": pd.read_csv(root / "ravenstack_accounts.csv"),
        "events": pd.read_csv(root / "ravenstack_churn_events.csv"),
        "subscriptions": pd.read_csv(root / "ravenstack_subscriptions.csv"),
        "tickets": pd.read_csv(root / "ravenstack_support_tickets.csv"),
        "usage": pd.read_csv(root / "ravenstack_feature_usage.csv"),
    }


def build_churn_panels(dados_dir: str | Path | None = None) -> DashboardPanels:
    tables = load_churn_tables(dados_dir)
    accounts = tables["accounts"]
    events = tables["events"]
    subscriptions = tables["subscriptions"]
    tickets = tables["tickets"]
    usage = tables["usage"]

    labeled = accounts[["account_id", "industry", "country", "plan_tier", "seats", "is_trial"]].copy()
    labeled["has_event"] = labeled["account_id"].isin(events["account_id"]).astype(int)

    ranking = (
        labeled.groupby("country", as_index=False)
        .agg(accounts=("account_id", "count"), accounts_with_event=("has_event", "sum"))
        .sort_values("accounts_with_event", ascending=False)
    )
    ranking["event_rate"] = (ranking["accounts_with_event"] / ranking["accounts"]).round(3)

    gallery = (
        accounts.merge(
            events.sort_values("churn_date").drop_duplicates("account_id", keep="last"),
            on="account_id",
            how="inner",
        )[
            [
                "account_id",
                "account_name",
                "industry",
                "plan_tier",
                "country",
                "reason_code",
                "refund_amount_usd",
            ]
        ]
        .head(12)
    )

    classification = (
        events.groupby("reason_code", as_index=False)
        .size()
        .rename(columns={"size": "events"})
        .sort_values("events", ascending=False)
    )

    segmentation = (
        labeled.groupby(["industry", "plan_tier"], as_index=False)
        .agg(accounts=("account_id", "count"), with_event=("has_event", "sum"))
    )
    segmentation["event_rate"] = (segmentation["with_event"] / segmentation["accounts"]).round(3)
    segmentation = segmentation[segmentation["accounts"] >= 5].sort_values(
        "event_rate", ascending=False
    )

    usage_by_sub = usage.groupby("subscription_id", as_index=False).agg(
        avg_usage=("usage_count", "mean"),
        avg_errors=("error_count", "mean"),
    )
    sub_usage = subscriptions.merge(usage_by_sub, on="subscription_id", how="left")
    usage_by_account = sub_usage.groupby("account_id", as_index=False).agg(
        avg_usage=("avg_usage", "mean"),
        avg_errors=("avg_errors", "mean"),
        had_downgrade=("downgrade_flag", "max"),
    )
    csat = tickets.groupby("account_id", as_index=False).agg(
        avg_csat=("satisfaction_score", "mean"),
        avg_hours=("resolution_time_hours", "mean"),
    )
    model_src = labeled.merge(usage_by_account, on="account_id", how="left").merge(
        csat, on="account_id", how="left"
    )
    model_src["had_downgrade"] = model_src["had_downgrade"].fillna(False).astype(int)
    for column in ("avg_usage", "avg_errors", "avg_csat", "avg_hours", "seats"):
        model_src[column] = model_src[column].fillna(model_src[column].median())
    features = encode_categoricals(model_src, ["industry", "plan_tier"]).join(
        model_src[["seats", "avg_usage", "avg_errors", "avg_csat", "avg_hours", "had_downgrade"]]
    )
    fitted = fit_logistic_panels(features, model_src["has_event"])

    panels = DashboardPanels("churn")
    panels.panels["ranking"] = Panel(
        "ranking",
        "Ranking de benchmark",
        ranking,
        plot_bar(ranking.head(12), "country", "accounts_with_event", "Ranking — eventos por país"),
        "Ordenado por volume de eventos, não pela taxa.",
    )
    panels.panels["gallery"] = Panel(
        "gallery",
        "Galeria de entrada",
        gallery,
        plot_bar(
            gallery.groupby("reason_code", as_index=False).size().rename(columns={"size": "contas"}),
            "reason_code",
            "contas",
            "Galeria — amostra de contas com evento",
        ),
        "Amostra das contas com churn_event. churn_flag da conta não entra.",
    )
    panels.panels["classification"] = Panel(
        "classification",
        "Classificação",
        classification,
        plot_bar(classification, "reason_code", "events", "Classificação — reason_code"),
        "Classe = reason_code do evento.",
    )
    panels.panels["segmentation"] = Panel(
        "segmentation",
        "Segmentação",
        segmentation,
        plot_bar(
            segmentation.assign(segment=segmentation["industry"] + " / " + segmentation["plan_tier"]).head(12),
            "segment",
            "event_rate",
            "Segmentação — industry × plan_tier",
        ),
    )
    panels.panels["image_segmentation"] = image_unavailable(
        "RavenStack não tem pixels nem máscara. Grain = account_id."
    )
    panels.panels["model_stats"] = Panel(
        "model_stats",
        "Estatísticas do modelo",
        fitted["stats"],
        plot_counters(fitted["stats"], "Baseline logístico — evento de churn"),
        "Label = has_event em ravenstack_churn_events. Uma época = um fit.",
    )
    panels.panels["confusion_matrix"] = Panel(
        "confusion_matrix",
        "Matriz de confusão",
        pd.DataFrame(fitted["matrix"], index=fitted["labels"], columns=fitted["labels"]),
        plot_heatmap(fitted["matrix"], fitted["labels"], "Matriz de confusão — evento"),
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
