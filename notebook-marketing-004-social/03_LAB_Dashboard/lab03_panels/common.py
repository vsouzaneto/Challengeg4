"""Painéis gráficos do Lab 03 — métricas e figuras a partir de colunas reais."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import learning_curve, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

NAVY = "#32445A"
STEEL = "#466381"
SLATE = "#9CA5AC"
ICE = "#E3EAF2"
REQUIRED_SECTIONS = (
    "ranking",
    "gallery",
    "classification",
    "segmentation",
    "image_segmentation",
    "model_stats",
    "confusion_matrix",
    "learning_curve",
    "bias_variance",
)


@dataclass
class Panel:
    key: str
    title: str
    frame: pd.DataFrame
    figure: plt.Figure | None = None
    note: str = ""


@dataclass
class DashboardPanels:
    project: str
    panels: dict[str, Panel] = field(default_factory=dict)

    def require_complete(self) -> None:
        missing = [key for key in REQUIRED_SECTIONS if key not in self.panels]
        if missing:
            raise ValueError(f"seções ausentes em {self.project}: {missing}")

    def close_figures(self) -> None:
        for panel in self.panels.values():
            if panel.figure is not None:
                plt.close(panel.figure)


def resolve_dados(pack_name: str, dados_dir: str | Path | None = None) -> Path:
    if dados_dir is not None:
        return Path(dados_dir)
    here = Path(__file__).resolve()
    candidates = [
        here.parents[2] / "dados",
        here.parents[2] / pack_name / "dados",
        Path.cwd() / "dados",
        Path.cwd().parent / "dados",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError("pasta dados/ não encontrada para " + pack_name)


def image_unavailable(reason: str) -> Panel:
    frame = pd.DataFrame(
        [
            {
                "available": False,
                "grain": None,
                "reason": reason,
            }
        ]
    )
    fig, ax = plt.subplots(figsize=(8, 2.4))
    ax.set_axis_off()
    ax.text(
        0.5,
        0.5,
        "Segmentação de imagem indisponível\n" + reason,
        ha="center",
        va="center",
        color=NAVY,
        fontsize=11,
    )
    fig.patch.set_facecolor(ICE)
    return Panel(
        "image_segmentation",
        "Segmentação de imagem",
        frame,
        fig,
        reason,
    )


def style_axes(ax, title: str) -> None:
    ax.set_title(title, color=NAVY, loc="left", fontsize=12)
    ax.tick_params(colors=STEEL)
    for spine in ax.spines.values():
        spine.set_color(SLATE)
    ax.set_facecolor("white")
    ax.figure.patch.set_facecolor(ICE)


def plot_bar(frame: pd.DataFrame, x: str, y: str, title: str, color: str = NAVY) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(9, 4.2))
    labels = frame[x].astype(str).tolist()
    ax.bar(labels, frame[y].tolist(), color=color)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.tick_params(axis="x", rotation=30)
    style_axes(ax, title)
    fig.tight_layout()
    return fig


def plot_heatmap(matrix: np.ndarray, labels: list[str], title: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(5.5, 4.6))
    image = ax.imshow(matrix, cmap="Blues")
    ax.set_xticks(range(len(labels)), labels, rotation=30, ha="right")
    ax.set_yticks(range(len(labels)), labels)
    ax.set_xlabel("previsto")
    ax.set_ylabel("real")
    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            ax.text(col, row, int(matrix[row, col]), ha="center", va="center", color=NAVY)
    fig.colorbar(image, ax=ax, fraction=0.046)
    style_axes(ax, title)
    fig.tight_layout()
    return fig


def plot_line(frame: pd.DataFrame, x: str, ys: list[str], title: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 4))
    palette = [NAVY, STEEL, SLATE]
    for index, column in enumerate(ys):
        ax.plot(frame[x], frame[column], marker="o", color=palette[index % 3], label=column)
    ax.legend(frameon=False)
    ax.set_xlabel(x)
    style_axes(ax, title)
    fig.tight_layout()
    return fig


def plot_counters(frame: pd.DataFrame, title: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 3.2))
    ax.set_axis_off()
    style_axes(ax, title)
    items = list(frame.iloc[0].items())
    width = 1 / max(len(items), 1)
    for index, (name, value) in enumerate(items):
        ax.text(
            (index + 0.5) * width,
            0.55,
            _format_metric(value),
            ha="center",
            va="center",
            fontsize=14,
            color=NAVY,
            transform=ax.transAxes,
        )
        ax.text(
            (index + 0.5) * width,
            0.22,
            str(name),
            ha="center",
            va="center",
            fontsize=8,
            color=STEEL,
            transform=ax.transAxes,
        )
    fig.tight_layout()
    return fig


def _format_metric(value) -> str:
    if pd.isna(value):
        return "n/d"
    if isinstance(value, (float, np.floating)):
        return f"{value:.3f}"
    return str(value)


def encode_categoricals(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    return pd.get_dummies(frame[columns], dummy_na=True)


def fit_logistic_panels(
    features: pd.DataFrame,
    labels: pd.Series,
    *,
    random_state: int = 21,
    max_samples: int = 4000,
) -> dict[str, pd.DataFrame | np.ndarray | float | int]:
    aligned = features.loc[labels.index].copy()
    y = labels.loc[aligned.index].astype(int)
    if len(aligned) > max_samples:
        aligned = aligned.sample(n=max_samples, random_state=random_state)
        y = y.loc[aligned.index]
    if y.nunique() < 2 or len(aligned) < 40:
        raise ValueError("amostra insuficiente para o baseline")

    x_train, x_test, y_train, y_test = train_test_split(
        aligned,
        y,
        test_size=0.25,
        random_state=random_state,
        stratify=y,
    )
    model = Pipeline(
        [
            ("scale", StandardScaler()),
            ("clf", LogisticRegression(max_iter=400, solver="lbfgs")),
        ]
    )
    started = time.perf_counter()
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    latency_ms = (time.perf_counter() - started) * 1000 / max(len(x_test), 1)
    y_proba = model.predict_proba(x_test)[:, 1] if y.nunique() == 2 else None
    train_pred = model.predict(x_train)
    clf = model.named_steps["clf"]

    stats = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        "roc_auc": (
            round(float(roc_auc_score(y_test, y_proba)), 4)
            if y_proba is not None
            else None
        ),
        "latency_ms": round(float(latency_ms), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "parameters": int(clf.coef_.size + clf.intercept_.size),
        "epochs": 1,
    }
    matrix = confusion_matrix(y_test, y_pred, labels=[0, 1])
    sizes, train_scores, test_scores = learning_curve(
        Pipeline(
            [
                ("scale", StandardScaler()),
                ("clf", LogisticRegression(max_iter=400, solver="lbfgs")),
            ]
        ),
        aligned,
        y,
        cv=3,
        train_sizes=np.linspace(0.25, 1.0, 4),
        scoring="accuracy",
        shuffle=True,
        random_state=random_state,
    )
    curve = pd.DataFrame(
        {
            "train_size": sizes,
            "train_accuracy": train_scores.mean(axis=1).round(4),
            "test_accuracy": test_scores.mean(axis=1).round(4),
        }
    )
    train_acc = float(accuracy_score(y_train, train_pred))
    test_acc = float(accuracy_score(y_test, y_pred))
    bias_var = pd.DataFrame(
        [
            {
                "train_accuracy": round(train_acc, 4),
                "test_accuracy": round(test_acc, 4),
                "gap": round(train_acc - test_acc, 4),
                "reading": _bias_reading(train_acc, test_acc),
            }
        ]
    )
    return {
        "stats": pd.DataFrame([stats]),
        "matrix": matrix,
        "curve": curve,
        "bias_variance": bias_var,
        "labels": ["negativo", "positivo"],
    }


def _bias_reading(train_acc: float, test_acc: float) -> str:
    gap = train_acc - test_acc
    if train_acc < 0.62 and test_acc < 0.62:
        return "alto viés — baseline fraco nos dois cortes"
    if gap > 0.08:
        return "alta variância — treino bem acima do teste"
    return "gap moderado entre treino e teste"
