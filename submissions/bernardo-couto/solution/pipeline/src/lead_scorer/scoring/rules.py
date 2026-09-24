"""Rules layer (layer 1) as pure Spark SQL column expressions. No Python UDFs.

Port of the pandas prototype ``analysis/rules.py`` following docs/specs/scoring-spec.md
section 3. Every function takes ``Column`` inputs and returns ``Column`` outputs, so the same
rule can be applied to a gold ``opportunity_features`` frame (jobs) or to a tiny synthetic
frame (tests). One rule emits exactly one reason (``ReasonCode``); reasons that do not change
``p_win`` are informative (direction ``i``, weight 0).

Unit of ``Reason.weight``: **points of ``priority_score`` (0-100 scale)** for every code, so
the UI shows the raw value with its sign and the score-carrying reasons add up to the score:
- ``PRODUCT_BASE_RATE`` (+): ``w_p * p_scaled(p_prod)`` -- the probability points before any
  zombie adjustment;
- ``ZOMBIE_RISK`` (-): ``w_p * (p_scaled(p_win) - p_scaled(p_prod))`` minus the points removed by
  the 49-point cap, so PRODUCT_BASE_RATE + ZOMBIE_RISK = ``score_breakdown.p_win_points``;
- ``HIGH_TICKET`` (+) / ``LOW_TICKET`` (-): ``w_v * value_norm`` = ``value_points`` (LOW_TICKET is
  negative in *direction* -- few points -- but the weight is the points the value axis adds);
- ``URGENCY_WINDOW`` (+): ``w_u * urgency`` = ``urgency_points``;
- informative reasons (agent, agent x product, sector, account, survival, load): 0.
Deals priced between the LOW and HIGH thresholds carry no ticket reason; their value points
are visible only in ``score_breakdown``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from pyspark.sql import Column
from pyspark.sql import functions as F

from lead_scorer.contracts import ReasonCode
from lead_scorer.scoring.weights import DEFAULT_WEIGHTS, Weights

REASON_FIELDS = ("code", "direction", "weight", "text_pt")
_ORD = "_ord"  # rule ordinal, used only to make the reason order deterministic on ties


@dataclass(frozen=True)
class RuleResult:
    """Output of a rule: the value it contributes (may be ``None``) and its reason column."""

    value: Column | None
    reason: Column


# --- formatting helpers (pt-BR, integers, no decimals) --------------------------------------------


def pct(col: Column) -> Column:
    """0.634 -> '63' (percentage as an integer string)."""
    return F.format_string("%d", F.round(col * 100).cast("int"))


def brl(col: Column) -> Column:
    """3412.4 -> '3.412' (currency without decimals, pt-BR thousands separator)."""
    return F.regexp_replace(F.format_number(F.round(col, 0), 0), ",", ".")


def days_int(col: Column) -> Column:
    return F.format_string("%d", col.cast("int"))


def _reason(
    code: ReasonCode, direction: Column | str, weight: Column, text: Column, ordinal: int
) -> Column:
    direction_col = F.lit(direction) if isinstance(direction, str) else direction
    return F.struct(
        F.lit(code.value).alias("code"),
        direction_col.alias("direction"),
        F.round(weight.cast("double"), 2).alias("weight"),
        text.alias("text_pt"),
        F.lit(ordinal).alias(_ORD),
    )


def _when(cond: Column, struct: Column) -> Column:
    """Conditional reason: ``null`` when the rule does not apply (filtered out later)."""
    return F.when(cond, struct)


def small_sample_note(n: Column, w: Weights = DEFAULT_WEIGHTS) -> Column:
    return F.when(n < F.lit(w.min_group_n), F.lit(", amostra pequena")).otherwise(F.lit(""))


# --- stage flags ----------------------------------------------------------------------------------


def is_prospecting(days_in_engaging: Column) -> Column:
    """Prospecting deals have no ``engage_date`` and therefore no age."""
    return days_in_engaging.isNull()


def is_zombie(days_in_engaging: Column, w: Weights = DEFAULT_WEIGHTS) -> Column:
    return days_in_engaging.isNotNull() & (days_in_engaging > F.lit(w.zombie_days))


def is_alive(days_in_engaging: Column, w: Weights = DEFAULT_WEIGHTS) -> Column:
    return days_in_engaging.isNotNull() & (days_in_engaging <= F.lit(w.zombie_days))


# --- 3.1 p_win ------------------------------------------------------------------------------------


def smooth(wins: Column, n: Column, p0: Column, w: Weights = DEFAULT_WEIGHTS) -> Column:
    """Bayesian shrinkage ``(wins + a*p0) / (n + a)``; equals ``p0`` when ``n`` is 0."""
    a = F.lit(w.prior_a)
    return (F.coalesce(wins, F.lit(0.0)) + a * p0) / (F.coalesce(n, F.lit(0.0)) + a)


def product_base_rate(
    product: Column,
    rate_product: Column,
    n_product: Column,
    p0: Column,
    w: Weights = DEFAULT_WEIGHTS,
) -> RuleResult:
    """``p_prod`` = smoothed Won rate of the product (falls back to ``p0`` for unseen products).

    ``rate_product`` is already smoothed in gold (``win_rate_product``). Weight = the probability
    points this rate is worth (``w_p * p_scaled``), direction ``+``.
    """
    p_prod = F.coalesce(rate_product, p0)
    n = F.coalesce(n_product, F.lit(0))
    points = F.lit(w.w_p) * p_scaled(p_prod, w)
    text = F.format_string(
        "%s fecha em %s%% dos casos (%s deals no histórico; média geral %s%%) → +%s pts.",
        product,
        pct(p_prod),
        F.format_string("%d", n.cast("int")),
        pct(p0),
        F.format_string("%.1f", points),
    )
    return RuleResult(p_prod, _reason(ReasonCode.PRODUCT_BASE_RATE, "+", points, text, 0))


def p_scaled(p_win: Column, w: Weights = DEFAULT_WEIGHTS) -> Column:
    """``clip((p_win - 0.30) / 0.50, 0, 1)``: the probability axis of the score."""
    return F.least(
        F.greatest((p_win - F.lit(w.p_scale_lo)) / F.lit(w.p_scale_hi - w.p_scale_lo), F.lit(0.0)),
        F.lit(1.0),
    )


def p_win_rules(p_prod: Column, zombie: Column, w: Weights = DEFAULT_WEIGHTS) -> Column:
    """``p_win = p_prod * ZOMBIE_P_FACTOR`` for zombies, ``p_prod`` otherwise."""
    return F.when(zombie, p_prod * F.lit(w.zombie_p_factor)).otherwise(p_prod)


def agent_track_record(
    rate_agent: Column, n_agent: Column, p0: Column, w: Weights = DEFAULT_WEIGHTS
) -> RuleResult:
    rate = F.coalesce(rate_agent, p0)
    n = F.coalesce(n_agent, F.lit(0))
    text = F.format_string(
        "Você fecha %s%% dos seus deals (%s fechados; time: %s%%). Isso não muda a ordem da sua "
        "fila — no passado não previu o fechamento.",
        pct(rate),
        F.format_string("%d", n.cast("int")),
        pct(p0),
    )
    return RuleResult(None, _reason(ReasonCode.AGENT_TRACK_RECORD, "i", F.lit(0.0), text, 1))


def agent_product_fit(
    product: Column,
    rate_agent_product: Column,
    n_agent_product: Column,
    rate_agent: Column,
    p0: Column,
    w: Weights = DEFAULT_WEIGHTS,
) -> RuleResult:
    rate = F.coalesce(rate_agent_product, rate_agent, p0)
    n = F.coalesce(n_agent_product, F.lit(0))
    text = F.format_string(
        "Você fecha %s%% dos %s (%s deals%s).",
        pct(rate),
        product,
        F.format_string("%d", n.cast("int")),
        small_sample_note(n, w),
    )
    return RuleResult(None, _reason(ReasonCode.AGENT_PRODUCT_FIT, "i", F.lit(0.0), text, 2))


def sector_fit(
    account_known: Column, sector: Column, rate_sector: Column, n_sector: Column, p0: Column
) -> RuleResult:
    rate = F.coalesce(rate_sector, p0)
    n = F.coalesce(n_sector, F.lit(0))
    text = F.format_string(
        "Setor %s: %s%% de fechamento (%s deals; média %s%%).",
        F.coalesce(sector, F.lit("não informado")),
        pct(rate),
        F.format_string("%d", n.cast("int")),
        pct(p0),
    )
    return RuleResult(
        None, _when(account_known, _reason(ReasonCode.SECTOR_FIT, "i", F.lit(0.0), text, 3))
    )


def account_size(account_known: Column, employees: Column, revenue: Column) -> RuleResult:
    text = F.format_string(
        "Conta com %s funcionários e receita de US$ %s mi. Serve para preparar a conversa; "
        "o porte não previu fechamento no histórico.",
        F.format_string("%d", F.coalesce(employees, F.lit(0)).cast("int")),
        F.format_string("%d", F.round(F.coalesce(revenue, F.lit(0.0))).cast("int")),
    )
    return RuleResult(
        None, _when(account_known, _reason(ReasonCode.ACCOUNT_SIZE, "i", F.lit(0.0), text, 4))
    )


def account_history(account_known: Column, n_account: Column, wins_account: Column) -> RuleResult:
    n = F.coalesce(n_account, F.lit(0))
    wins = F.coalesce(wins_account, F.lit(0))
    text = F.format_string(
        "%s ganhos e %s perdidos nesta conta até a data de referência.",
        F.format_string("%d", wins.cast("int")),
        F.format_string("%d", (n - wins).cast("int")),
    )
    cond = account_known & (n >= 1)
    reason = _reason(ReasonCode.ACCOUNT_HISTORY, "i", F.lit(0.0), text, 5)
    return RuleResult(None, _when(cond, reason))


def account_unknown(account_known: Column) -> RuleResult:
    """The team-level share of deals without account belongs to the manager view, not here."""
    text = F.lit(
        "Sem conta no CRM: não sabemos setor, porte nem histórico. Registre a conta antes do "
        "próximo contato — leva 1 minuto e libera confiança alta."
    )
    return RuleResult(
        None, _when(~account_known, _reason(ReasonCode.ACCOUNT_UNKNOWN, "i", F.lit(0.0), text, 6))
    )


def survival_positive(
    days_in_engaging: Column, rate_survival: Column, p0: Column, w: Weights = DEFAULT_WEIGHTS
) -> RuleResult:
    """Informative: P(Won | still open at this age) from history, plus the countdown to 138."""
    alive = is_alive(days_in_engaging, w)
    rate = F.coalesce(rate_survival, p0)
    remaining = F.lit(w.zombie_days) - days_in_engaging
    text = F.concat(
        F.format_string(
            "%s dias em Engaging. Deals que chegaram aqui fecharam em %s%% dos casos",
            days_int(days_in_engaging),
            pct(rate),
        ),
        F.when(
            days_in_engaging > F.lit(w.late_cycle_days),
            F.format_string(
                " — mas nenhum deal fechou depois de %d dias: faltam %s dias.",
                F.lit(w.zombie_days),
                days_int(remaining),
            ),
        ).otherwise(F.lit(".")),
    )
    return RuleResult(
        None, _when(alive, _reason(ReasonCode.SURVIVAL_POSITIVE, "i", F.lit(0.0), text, 7))
    )


def zombie_risk(
    days_in_engaging: Column,
    p_win: Column,
    p_prod: Column,
    cap_reduction: Column,
    w: Weights = DEFAULT_WEIGHTS,
) -> RuleResult:
    """Direction ``-``; weight = probability points lost by halving ``p_win`` minus the points
    removed by the 49-point cap (``cap_reduction``, 0 when the cap does not bind)."""
    zombie = is_zombie(days_in_engaging, w)
    delta = F.lit(w.w_p) * (p_scaled(p_win, w) - p_scaled(p_prod, w)) - cap_reduction
    text = F.format_string(
        "%s dias em Engaging: nenhum deal na história fechou depois de %d. Este deal saiu da sua "
        "fila de trabalho e está na fila 'Confirmar ou encerrar' (%s pts).",
        days_int(days_in_engaging),
        F.lit(w.zombie_days),
        F.format_string("%.1f", delta),
    )
    return RuleResult(None, _when(zombie, _reason(ReasonCode.ZOMBIE_RISK, "-", delta, text, 8)))


def prospecting_no_timeline(days_in_engaging: Column, w: Weights = DEFAULT_WEIGHTS) -> RuleResult:
    text = F.lit(
        "Em Prospecting, sem data de primeiro contato: não dá para medir urgência (fixada em "
        f"{int(round(w.prospecting_urgency * 100))}%); a posição na fila vem só do valor."
    )
    return RuleResult(
        None,
        _when(
            is_prospecting(days_in_engaging),
            _reason(ReasonCode.PROSPECTING_NO_TIMELINE, "i", F.lit(0.0), text, 9),
        ),
    )


def agent_overload(
    open_load: Column,
    threshold: Column,
    agent_zombies: Column,
    team_median_load: Column,
    w: Weights = DEFAULT_WEIGHTS,
) -> RuleResult:
    """Informative (H5 refuted): agent's open deals at/above the batch's 75th percentile.

    ``agent_zombies`` = the agent's deals older than ``zombie_days`` in the batch;
    ``team_median_load`` = median open load across agents in the batch.
    """
    load = F.coalesce(open_load, F.lit(0))
    text = F.format_string(
        "Você tem %s deals abertos, %s deles parados há mais de %d dias (time: mediana %s). "
        "Encerrar os parados libera agenda e forecast.",
        F.format_string("%d", load.cast("int")),
        F.format_string("%d", F.coalesce(agent_zombies, F.lit(0)).cast("int")),
        F.lit(w.zombie_days),
        F.format_string("%d", F.round(F.coalesce(team_median_load, F.lit(0.0))).cast("int")),
    )
    cond = (load >= threshold) & (load > 0)
    reason = _reason(ReasonCode.AGENT_OVERLOAD, "i", F.lit(0.0), text, 10)
    return RuleResult(None, _when(cond, reason))


# --- 3.2 expected value ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ValueResult:
    ev_gross: Column
    expected_value: Column
    value_norm: Column
    reason: Column  # HIGH_TICKET / LOW_TICKET or null


def expected_value(
    sales_price: Column,
    product: Column,
    value_ratio: Column,
    p_win: Column,
    p_prod: Column,
    w: Weights = DEFAULT_WEIGHTS,
) -> ValueResult:
    """``ev_gross = price * ratio``; ``ev = ev_gross * p_win``; ``value_norm`` in log scale.

    Both ticket reasons carry ``w_v * value_norm`` (= ``value_points``) as weight.
    """
    ratio = F.coalesce(value_ratio, F.lit(1.0))
    ev_gross = sales_price * ratio
    ev = ev_gross * p_win
    value_norm = F.log1p(ev_gross) / F.lit(math.log1p(w.max_list_price))
    points = F.lit(w.w_v) * value_norm
    high_text = F.format_string(
        "Ticket alto: R$ %s esperados se fechar (preço de tabela R$ %s; %s fecha em %s%% dos "
        "casos) → +%s pts.",
        brl(ev_gross),
        brl(sales_price),
        product,
        pct(p_prod),
        F.format_string("%.1f", points),
    )
    low_text = F.format_string(
        "Ticket baixo: %s vale R$ %s (só +%s pts de valor). Feche rápido ou deixe para depois "
        "dos deals maiores.",
        product,
        brl(sales_price),
        F.format_string("%.1f", points),
    )
    reason = F.when(
        sales_price >= F.lit(w.high_ticket_price),
        _reason(ReasonCode.HIGH_TICKET, "+", points, high_text, 11),
    ).when(
        sales_price <= F.lit(w.low_ticket_price),
        _reason(ReasonCode.LOW_TICKET, "-", points, low_text, 12),
    )
    return ValueResult(ev_gross, ev, value_norm, reason)


# --- 3.3 urgency ----------------------------------------------------------------------------------


def urgency(
    days_in_engaging: Column, hazard: Column, hazard_max: Column, w: Weights = DEFAULT_WEIGHTS
) -> Column:
    """Prospecting -> 0.5; zombie -> 0.2; alive -> ``hazard14[d] / max(hazard14)``."""
    alive_urgency = F.coalesce(hazard, F.lit(0.0)) / F.when(hazard_max > 0, hazard_max).otherwise(
        F.lit(1.0)
    )
    out = (
        F.when(is_prospecting(days_in_engaging), F.lit(w.prospecting_urgency))
        .when(is_zombie(days_in_engaging, w), F.lit(w.zombie_urgency))
        .otherwise(alive_urgency)
    )
    return F.least(F.greatest(out, F.lit(0.0)), F.lit(1.0))


def urgency_window(
    days_in_engaging: Column, urgency_col: Column, w: Weights = DEFAULT_WEIGHTS
) -> RuleResult:
    """Direction ``+``; weight = ``w_u * urgency`` (the urgency points of the score)."""
    points = F.lit(w.w_u) * urgency_col
    pts = F.format_string("%.1f", points)
    text = (
        F.when(
            is_prospecting(days_in_engaging),
            F.format_string("Sem data de engajamento: urgência padrão, +%s pts.", pts),
        )
        .when(
            is_zombie(days_in_engaging, w),
            F.format_string(
                "Sem histórico de fechamento nesta idade → urgência mínima, +%s pts.", pts
            ),
        )
        .otherwise(
            F.format_string(
                "Janela de decisão: %s%% de chance de desfecho nos próximos 14 dias nesta idade "
                "→ +%s pts.",
                pct(urgency_col),
                pts,
            )
        )
    )
    return RuleResult(points, _reason(ReasonCode.URGENCY_WINDOW, "+", points, text, 13))


# --- 3.4 priority score ---------------------------------------------------------------------------


def priority_score(
    p_win: Column,
    value_norm: Column,
    urgency_col: Column,
    zombie: Column,
    w: Weights = DEFAULT_WEIGHTS,
) -> Column:
    return F.least(
        F.greatest(capped_score(p_win, value_norm, urgency_col, zombie, w), F.lit(0.0)),
        F.lit(100.0),
    )


def raw_score(
    p_win: Column, value_norm: Column, urgency_col: Column, w: Weights = DEFAULT_WEIGHTS
) -> Column:
    """Additive score before the zombie cap and the 0-100 clip."""
    return (
        F.lit(w.w_p) * p_scaled(p_win, w) + F.lit(w.w_v) * value_norm + F.lit(w.w_u) * urgency_col
    )


def capped_score(
    p_win: Column,
    value_norm: Column,
    urgency_col: Column,
    zombie: Column,
    w: Weights = DEFAULT_WEIGHTS,
) -> Column:
    score = raw_score(p_win, value_norm, urgency_col, w)
    return F.when(zombie, F.least(score, F.lit(w.zombie_score_cap))).otherwise(score)


# --- 3.5 / 3.6 confidence and tier ----------------------------------------------------------------


def confidence(
    account_known: Column,
    days_in_engaging: Column,
    n_agent: Column,
    n_product: Column,
    w: Weights = DEFAULT_WEIGHTS,
) -> Column:
    prospecting = is_prospecting(days_in_engaging)
    small = (F.coalesce(n_agent, F.lit(0)) < F.lit(w.min_group_n)) | (
        F.coalesce(n_product, F.lit(0)) < F.lit(w.min_group_n)
    )
    low = is_zombie(days_in_engaging, w) | (prospecting & ~account_known) | small
    return (
        F.when(low, F.lit("baixa"))
        .when(~account_known | prospecting, F.lit("media"))
        .otherwise(F.lit("alta"))
    )


def tier(score: Column, confidence_col: Column, w: Weights = DEFAULT_WEIGHTS) -> Column:
    """Absolute tiers; tier A additionally requires confidence != baixa."""
    raw = (
        F.when(score >= F.lit(w.tier_a), F.lit("A"))
        .when(score >= F.lit(w.tier_b), F.lit("B"))
        .when(score >= F.lit(w.tier_c), F.lit("C"))
        .otherwise(F.lit("D"))
    )
    return F.when((raw == "A") & (confidence_col == "baixa"), F.lit("B")).otherwise(raw)


# --- 3.7 next action ------------------------------------------------------------------------------

ACTION_CALL = "Ligar esta semana e propor data de fechamento."
ACTION_FOLLOW_UP = "Fazer um contato de acompanhamento e registrar o próximo passo no CRM."
ACTION_LATE = "Faltam %s dias do ciclo máximo: fechar ou desistir esta semana."
ACTION_ZOMBIE = "Confirmar com o cliente ou encerrar no CRM."
ACTION_PROSPECTING_NO_ACCOUNT = "Registrar conta e data de engajamento no CRM antes de priorizar."
ACTION_PROSPECTING = "Agendar primeiro contato e registrar engage_date."


def next_action(
    days_in_engaging: Column, account_known: Column, tier_col: Column, w: Weights = DEFAULT_WEIGHTS
) -> Column:
    remaining = F.lit(w.zombie_days) - days_in_engaging
    return (
        F.when(
            is_prospecting(days_in_engaging),
            F.when(account_known, F.lit(ACTION_PROSPECTING)).otherwise(
                F.lit(ACTION_PROSPECTING_NO_ACCOUNT)
            ),
        )
        .when(is_zombie(days_in_engaging, w), F.lit(ACTION_ZOMBIE))
        .when(
            days_in_engaging > F.lit(w.late_action_days),
            F.format_string(ACTION_LATE, days_int(remaining)),
        )
        .when(tier_col.isin("A", "B"), F.lit(ACTION_CALL))
        .otherwise(F.lit(ACTION_FOLLOW_UP))
    )


# --- reasons assembly -----------------------------------------------------------------------------


def _sort_key(reason: Column) -> Column:
    """|weight| in score points (same unit for every code)."""
    return F.abs(reason["weight"])


def assemble_reasons(*reasons: Column) -> Column:
    """Drop null reasons, order by |weight| desc (ties: rule order) and strip the ordinal."""
    arr = F.filter(F.array(*reasons), lambda r: r.isNotNull())

    def cmp(left: Column, right: Column) -> Column:
        kl, kr = _sort_key(left), _sort_key(right)
        return (
            F.when(kl > kr, F.lit(-1))
            .when(kl < kr, F.lit(1))
            .when(left[_ORD] < right[_ORD], F.lit(-1))
            .when(left[_ORD] > right[_ORD], F.lit(1))
            .otherwise(F.lit(0))
        )

    ordered = F.array_sort(arr, cmp)
    return F.transform(
        ordered,
        lambda r: F.struct(*[r[f].alias(f) for f in REASON_FIELDS]),
    )


__all__ = [
    "ACTION_CALL",
    "ACTION_ZOMBIE",
    "REASON_FIELDS",
    "RuleResult",
    "ValueResult",
    "account_history",
    "account_size",
    "account_unknown",
    "agent_overload",
    "agent_product_fit",
    "agent_track_record",
    "assemble_reasons",
    "confidence",
    "expected_value",
    "is_alive",
    "is_prospecting",
    "is_zombie",
    "next_action",
    "p_scaled",
    "p_win_rules",
    "priority_score",
    "raw_score",
    "capped_score",
    "urgency_window",
    "product_base_rate",
    "prospecting_no_timeline",
    "sector_fit",
    "smooth",
    "survival_positive",
    "tier",
    "urgency",
    "zombie_risk",
]
