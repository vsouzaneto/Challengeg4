"""Temporal training frame for layer 2 (docs/specs/scoring-spec.md section 5).

For a cut ``T``: one block per month end ``m`` from ``FRAME_START`` to ``T - 1 month``. A block
has the deals open at ``m`` (gold features as of ``m``) whose outcome was known by ``T``
(``labels/as_of=m`` filtered on ``close_date <= T``). The last month of the frame is held out to
fit the isotonic calibrator; the earlier months train the logistic regression. No random split
anywhere: every row of the frame is strictly older than the evaluation cut.

Known bias (documented in the model card): recent months only contain deals that closed fast,
so the training Won rate is higher than the out-of-time rate.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass, field
from datetime import date, timedelta

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from lead_scorer.data import gold
from lead_scorer.ml.features import FEATURES, ID_COL, LABEL_COL, add_ml_features

FRAME_START = date(2017, 3, 31)
FRAME_MONTH_COL = "frame_month"


def month_end(year: int, month: int) -> date:
    return date(year, month, calendar.monthrange(year, month)[1])


def previous_month_end(d: date) -> date:
    """Last day of the month before ``d``'s month (2017-09-30 -> 2017-08-31)."""
    return d.replace(day=1) - timedelta(days=1)


def frame_months(cut: date, start: date = FRAME_START) -> list[date]:
    """Month ends ``m`` with ``start <= m <= cut - 1 month`` (the cut itself is excluded)."""
    out: list[date] = []
    y, m = start.year, start.month
    while True:
        me = month_end(y, m)
        if me >= cut:
            break
        # ``cut - 1 month``: the block must end at least one month before the cut.
        if me <= previous_month_end(cut):
            out.append(me)
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return out


@dataclass
class TrainingFrame:
    cut: date
    months: list[date]
    train: DataFrame
    calibration: DataFrame
    counts: dict[str, float] = field(default_factory=dict)

    @property
    def calibration_month(self) -> date:
        return self.months[-1]


class GoldCache:
    """Builds ``gold.build_gold`` once per month end and reuses it across cuts."""

    def __init__(self, opportunities: DataFrame, snapshot: date) -> None:
        self._opps = opportunities
        self._snapshot = snapshot
        self._cache: dict[date, gold.GoldBuild] = {}

    def get(self, as_of: date) -> gold.GoldBuild:
        if as_of not in self._cache:
            build = gold.build_gold(self._opps, as_of, self._snapshot)
            build.features.cache()
            build.labels.cache()
            self._cache[as_of] = build
        return self._cache[as_of]


def labelled_block(build: gold.GoldBuild, cut: date) -> DataFrame:
    """Open deals at ``build.as_of`` with outcome known by ``cut``: features + label."""
    labels = build.labels.filter(
        F.col("close_date") <= F.lit(cut)  # leakage-ok: training label gate at the cut
    ).select(ID_COL, F.col("label_won").cast("double").alias(LABEL_COL))
    feats = add_ml_features(build.features)
    return feats.join(labels, ID_COL, "inner").select(
        ID_COL, *FEATURES, LABEL_COL, F.lit(build.as_of).alias(FRAME_MONTH_COL)
    )


def build_training_frame(cache: GoldCache, cut: date, start: date = FRAME_START) -> TrainingFrame:
    months = frame_months(cut, start)
    if len(months) < 2:
        raise ValueError(f"cut {cut} leaves fewer than two frame months from {start}")
    blocks = [labelled_block(cache.get(m), cut) for m in months]
    train = blocks[0]
    for block in blocks[1:-1]:
        train = train.unionByName(block)
    calibration = blocks[-1]
    frame = TrainingFrame(cut=cut, months=months, train=train, calibration=calibration)
    frame.counts = {
        "train_rows": train.count(),
        "calibration_rows": calibration.count(),
        "train_positive_rate": _positive_rate(train),
    }
    return frame


def _positive_rate(df: DataFrame) -> float:
    row = df.agg(F.avg(LABEL_COL).alias("r")).first()
    return float(row["r"]) if row is not None and row["r"] is not None else float("nan")


__all__ = [
    "FRAME_MONTH_COL",
    "FRAME_START",
    "GoldCache",
    "TrainingFrame",
    "build_training_frame",
    "frame_months",
    "labelled_block",
    "month_end",
    "previous_month_end",
]
