"""Painéis do challenge 002 — sem Topic_group e sem e-mail."""

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


def load_support_table(dados_dir: str | Path | None = None) -> pd.DataFrame:
    root = resolve_dados("notebook-process-002-support", dados_dir)
    tickets = pd.read_csv(root / "customer_support_tickets.csv")
    if "Topic_group" in tickets.columns:
        raise ValueError("Topic_group não faz parte do dump")
    return tickets


def build_support_panels(dados_dir: str | Path | None = None) -> DashboardPanels:
    tickets = load_support_table(dados_dir)
    closed = tickets[tickets["Ticket Status"] == "Closed"].copy()
    closed["hours"] = (
        pd.to_datetime(closed["Time to Resolution"], errors="coerce")
        - pd.to_datetime(closed["First Response Time"], errors="coerce")
    ).dt.total_seconds() / 3600.0

    ranking = (
        closed.dropna(subset=["hours"])
        .groupby("Ticket Channel", as_index=False)
        .agg(
            closed_tickets=("Ticket ID", "count"),
            p95_hours=("hours", lambda values: values.quantile(0.95)),
            avg_csat=("Customer Satisfaction Rating", "mean"),
        )
        .sort_values("p95_hours", ascending=False)
    )
    ranking["p95_hours"] = ranking["p95_hours"].round(2)
    ranking["avg_csat"] = ranking["avg_csat"].round(2)

    gallery = tickets.loc[
        tickets["Ticket Status"].isin(["Open", "Pending Customer Response"]),
        [
            "Ticket ID",
            "Ticket Type",
            "Ticket Priority",
            "Ticket Channel",
            "Ticket Status",
            "Ticket Subject",
        ],
    ].head(12)

    classification = (
        tickets.groupby("Ticket Type", as_index=False)
        .size()
        .rename(columns={"size": "tickets"})
        .sort_values("tickets", ascending=False)
    )

    segmentation = (
        closed.groupby(["Ticket Channel", "Ticket Priority", "Ticket Type"], as_index=False)
        .agg(
            closed=("Ticket ID", "count"),
            avg_csat=("Customer Satisfaction Rating", "mean"),
            avg_hours=("hours", "mean"),
        )
        .sort_values("avg_csat", ascending=True)
    )
    segmentation["avg_csat"] = segmentation["avg_csat"].round(2)
    segmentation["avg_hours"] = segmentation["avg_hours"].round(2)

    model_src = closed.dropna(subset=["Customer Satisfaction Rating", "hours"]).copy()
    model_src["csat_high"] = (model_src["Customer Satisfaction Rating"] >= 4).astype(int)
    model_src["description_len"] = model_src["Ticket Description"].fillna("").str.len()
    features = encode_categoricals(
        model_src, ["Ticket Channel", "Ticket Type", "Ticket Priority"]
    ).join(model_src[["hours", "description_len"]])
    fitted = fit_logistic_panels(features, model_src["csat_high"])

    panels = DashboardPanels("support")
    panels.panels["ranking"] = Panel(
        "ranking",
        "Ranking de benchmark",
        ranking,
        plot_bar(ranking, "Ticket Channel", "p95_hours", "Ranking — p95 horas por canal"),
        "Horas = TTR − FRT, só Closed.",
    )
    panels.panels["gallery"] = Panel(
        "gallery",
        "Galeria de entrada",
        gallery,
        plot_bar(
            gallery.groupby("Ticket Type", as_index=False).size().rename(columns={"size": "tickets"}),
            "Ticket Type",
            "tickets",
            "Galeria — fila aberta por tipo",
        ),
        "Sem Customer Name / Customer Email.",
    )
    panels.panels["classification"] = Panel(
        "classification",
        "Classificação",
        classification,
        plot_bar(classification, "Ticket Type", "tickets", "Classificação — Ticket Type"),
        "Cinco tipos do dump. Sem Topic_group.",
    )
    panels.panels["segmentation"] = Panel(
        "segmentation",
        "Segmentação",
        segmentation,
        plot_bar(
            segmentation.groupby("Ticket Channel", as_index=False)["avg_csat"]
            .mean()
            .sort_values("avg_csat"),
            "Ticket Channel",
            "avg_csat",
            "Segmentação — CSAT médio por canal",
        ),
    )
    panels.panels["image_segmentation"] = image_unavailable(
        "Tickets não têm imagem. Dataset 2 (Topic_group) ausente."
    )
    panels.panels["model_stats"] = Panel(
        "model_stats",
        "Estatísticas do modelo",
        fitted["stats"],
        plot_counters(fitted["stats"], "Baseline logístico — CSAT ≥ 4 (Closed)"),
        "Label = Customer Satisfaction Rating ≥ 4. Sem Topic_group.",
    )
    panels.panels["confusion_matrix"] = Panel(
        "confusion_matrix",
        "Matriz de confusão",
        pd.DataFrame(fitted["matrix"], index=fitted["labels"], columns=fitted["labels"]),
        plot_heatmap(fitted["matrix"], fitted["labels"], "Matriz de confusão — CSAT alto"),
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
