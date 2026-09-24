"""Assemble the rules layer into ``ScoredDeal`` rows (DataFrame -> DataFrame, no IO).

``score_frame(features, history)`` takes the two gold tables of one ``as_of`` partition and
returns exactly the ``ScoredDeal`` columns, ordered ``priority_score DESC, days_in_engaging ASC``
(inside the zombie queue the newest zombie comes first: it is the most likely to still exist).

Layer 2 (Spark ML) enters only through ``p_model``: an optional ``(opportunity_id, p_model)``
frame blended with ``BLEND_MODEL_WEIGHT`` (0 in shadow mode, so the output is rules-only).
"""

from __future__ import annotations

from datetime import date

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from lead_scorer.contracts import ReasonCode
from lead_scorer.data.gold import DIM_ACCOUNT, DIM_HAZARD14
from lead_scorer.scoring import rules
from lead_scorer.scoring.weights import DEFAULT_WEIGHTS, Weights

#: Output columns, in contract order (``ScoredDeal`` fields; ``sales_price`` = list price).
SCORED_DEAL_COLUMNS: tuple[str, ...] = (
    "opportunity_id",
    "sales_agent",
    "manager",
    "regional_office",
    "product",
    "sales_price",
    "account",
    "deal_stage",
    "days_in_engaging",
    "priority_score",
    "tier",
    "p_win",
    "expected_value",
    "urgency",
    "confidence",
    "score_breakdown",
    "reasons",
    "next_action",
    "as_of",
    "model_version",
)

#: Columns of ``opportunity_features`` the rules read (anything else is ignored).
FEATURE_INPUTS: tuple[str, ...] = (
    "opportunity_id",
    "sales_agent",
    "manager",
    "regional_office",
    "product",
    "account",
    "account_known",
    "sector",
    "revenue",
    "employees",
    "deal_stage",
    "sales_price",
    "days_in_engaging",
    "global_win_rate",
    "win_rate_product",
    "n_product",
    "value_ratio_product",
    "win_rate_agent",
    "n_agent",
    "win_rate_agent_product",
    "n_agent_product",
    "win_rate_sector",
    "n_sector",
    "n_account",
    "win_rate_survival",
    "open_deals_agent",
)


def order_by() -> list[Column]:
    """``priority_score DESC, days_in_engaging ASC NULLS LAST, opportunity_id`` (spec section 4)."""
    return [
        F.col("priority_score").desc(),
        F.col("days_in_engaging").asc_nulls_last(),
        F.col("opportunity_id").asc(),
    ]


def _hazard_table(history: DataFrame) -> DataFrame:
    return history.filter(F.col("dimension") == DIM_HAZARD14).select(
        F.col("key").cast("int").alias("_hazard_d"), F.col("win_rate").alias("_hazard")
    )


def _account_wins(history: DataFrame) -> DataFrame:
    return history.filter(F.col("dimension") == DIM_ACCOUNT).select(
        F.col("key").alias("_account_key"), F.col("wins").alias("_wins_account")
    )


def _with_batch_context(df: DataFrame, w: Weights) -> DataFrame:
    """Batch-level scalars (1-row cross join) and per-agent zombie counts."""
    load_by_agent = df.select("sales_agent", "open_deals_agent").distinct()
    scalars = df.agg(
        F.expr(f"percentile(open_deals_agent, {w.overload_quantile})").alias("_overload_thr")
    ).crossJoin(
        load_by_agent.agg(F.expr("percentile(open_deals_agent, 0.5)").alias("_team_median_load"))
    )
    agent_window = Window.partitionBy("sales_agent")
    zombie_flag = rules.is_zombie(F.col("days_in_engaging"), w).cast("int")
    return df.crossJoin(F.broadcast(scalars)).withColumn(
        "_agent_zombies", F.sum(zombie_flag).over(agent_window)
    )


def score_frame(
    features: DataFrame,
    history: DataFrame,
    *,
    as_of: date,
    model_version: str,
    weights: Weights = DEFAULT_WEIGHTS,
    p_model: DataFrame | None = None,
) -> DataFrame:
    """Apply every rule and return the ``ScoredDeal`` frame (see module docstring)."""
    w = weights
    df = features.select(*FEATURE_INPUTS)
    df = _with_batch_context(df, w)

    hazard = _hazard_table(history)
    hazard_max = hazard.agg(F.max("_hazard").alias("_hazard_max"))
    df = df.join(hazard, df["days_in_engaging"] == hazard["_hazard_d"], "left").drop("_hazard_d")
    df = df.crossJoin(F.broadcast(hazard_max))
    df = df.join(_account_wins(history), df["account"] == F.col("_account_key"), "left").drop(
        "_account_key"
    )

    p0 = F.col("global_win_rate")
    days = F.col("days_in_engaging")
    known = F.col("account_known")
    zombie = rules.is_zombie(days, w)

    base = rules.product_base_rate(
        F.col("product"), F.col("win_rate_product"), F.col("n_product"), p0, w
    )
    assert base.value is not None
    p_prod = base.value
    p_rules = rules.p_win_rules(p_prod, zombie, w)

    if p_model is not None and w.blend_model_weight > 0:
        df = df.join(p_model.select("opportunity_id", "p_model"), "opportunity_id", "left")
        p_win = F.lit(1.0 - w.blend_model_weight) * p_rules + F.lit(
            w.blend_model_weight
        ) * F.coalesce(F.col("p_model"), p_rules)
        delta_points = F.lit(w.w_p) * (rules.p_scaled(p_win, w) - rules.p_scaled(p_rules, w))
        model_reason = F.struct(
            F.lit(ReasonCode.MODEL_CONTRIBUTION.value).alias("code"),
            F.when(delta_points > 0.5, F.lit("+"))
            .when(delta_points < -0.5, F.lit("-"))
            .otherwise(F.lit("i"))
            .alias("direction"),
            delta_points.cast("double").alias("weight"),
            F.format_string(
                "Ajuste do modelo: %s pontos. Veja em Qualidade por que ele foi ativado.",
                F.format_string("%+d", F.round(delta_points).cast("int")),
            ).alias("text_pt"),
            F.lit(13).alias("_ord"),
        )
    else:
        p_win = p_rules
        model_reason = None

    value = rules.expected_value(
        F.col("sales_price"), F.col("product"), F.col("value_ratio_product"), p_win, p_prod, w
    )
    urg = rules.urgency(days, F.col("_hazard"), F.col("_hazard_max"), w)
    score = rules.priority_score(p_win, value.value_norm, urg, zombie, w)
    # Points removed by the zombie cap (0 unless the cap binds); attributed to ZOMBIE_RISK.
    cap_reduction = rules.raw_score(p_win, value.value_norm, urg, w) - rules.capped_score(
        p_win, value.value_norm, urg, zombie, w
    )
    value_points = F.lit(w.w_v) * value.value_norm
    urgency_points = F.lit(w.w_u) * urg
    p_win_points = F.lit(w.w_p) * rules.p_scaled(p_win, w) - cap_reduction
    conf = rules.confidence(known, days, F.col("n_agent"), F.col("n_product"), w)
    tier_col = rules.tier(score, conf, w)
    breakdown = F.struct(
        F.round(p_win_points, 4).cast("double").alias("p_win_points"),
        F.round(value_points, 4).cast("double").alias("value_points"),
        F.round(urgency_points, 4).cast("double").alias("urgency_points"),
    )

    reason_columns = [
        base.reason,
        rules.agent_track_record(F.col("win_rate_agent"), F.col("n_agent"), p0, w).reason,
        rules.agent_product_fit(
            F.col("product"),
            F.col("win_rate_agent_product"),
            F.col("n_agent_product"),
            F.col("win_rate_agent"),
            p0,
            w,
        ).reason,
        rules.sector_fit(
            known, F.col("sector"), F.col("win_rate_sector"), F.col("n_sector"), p0
        ).reason,
        rules.account_size(known, F.col("employees"), F.col("revenue")).reason,
        rules.account_history(known, F.col("n_account"), F.col("_wins_account")).reason,
        rules.account_unknown(known).reason,
        rules.survival_positive(days, F.col("win_rate_survival"), p0, w).reason,
        rules.zombie_risk(days, p_win, p_prod, cap_reduction, w).reason,
        rules.urgency_window(days, urg, w).reason,
        rules.prospecting_no_timeline(days, w).reason,
        rules.agent_overload(
            F.col("open_deals_agent"),
            F.col("_overload_thr"),
            F.col("_agent_zombies"),
            F.col("_team_median_load"),
            w,
        ).reason,
        value.reason,
    ]
    if model_reason is not None:
        reason_columns.append(model_reason)
    reasons = rules.assemble_reasons(*reason_columns)

    scored = df.select(
        F.col("opportunity_id"),
        F.col("sales_agent"),
        F.col("manager"),
        F.col("regional_office"),
        F.col("product"),
        F.col("sales_price").cast("double").alias("sales_price"),
        F.col("account"),
        F.col("deal_stage"),
        days.cast("int").alias("days_in_engaging"),
        F.round(score, 4).cast("double").alias("priority_score"),
        tier_col.alias("tier"),
        F.round(p_win, 6).cast("double").alias("p_win"),
        F.round(value.expected_value, 2).cast("double").alias("expected_value"),
        F.round(urg, 6).cast("double").alias("urgency"),
        conf.alias("confidence"),
        breakdown.alias("score_breakdown"),
        reasons.alias("reasons"),
        rules.next_action(days, known, tier_col, w).alias("next_action"),
        F.lit(as_of).alias("as_of"),
        F.lit(model_version).alias("model_version"),
    )
    return scored.orderBy(*order_by()).select(*SCORED_DEAL_COLUMNS)


def zombie_flag(scored: DataFrame, weights: Weights = DEFAULT_WEIGHTS) -> DataFrame:
    """Convenience for summaries: adds ``is_zombie`` to a scored frame."""
    return scored.withColumn("is_zombie", rules.is_zombie(F.col("days_in_engaging"), weights))


__all__ = ["FEATURE_INPUTS", "SCORED_DEAL_COLUMNS", "order_by", "score_frame", "zombie_flag"]
