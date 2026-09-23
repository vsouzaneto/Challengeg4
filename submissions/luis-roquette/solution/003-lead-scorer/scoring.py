"""Frozen temporal evidence and stage-specific presentation contracts.

Input records are injected: this module imports neither data nor the UI. Estimators
are fitted once on training history, calibrated later, and never refitted on test.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, fields, is_dataclass
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import subprocess
from types import MappingProxyType
from typing import Any, Mapping
import warnings


def serialize(value):
    """JSON-safe copy, including immutable mappings and explicit score variants."""
    if isinstance(value, ScoreResult):
        return value.to_dict()
    if is_dataclass(value):
        return {field.name: serialize(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, Mapping):
        return {str(key): serialize(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [serialize(item) for item in value]
    if isinstance(value, date):
        return value.isoformat()
    return value


def digest(value):
    return hashlib.sha256(json.dumps(serialize(value), sort_keys=True,
        separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def diagnostic(code, reason, correction, *, field=None, opportunity_id=None, scope="route"):
    return MappingProxyType(dict(code=code, scope=scope, file=None,
        opportunity_id=opportunity_id, field=field, reason=reason, correction=correction))


class ScoringValidationError(ValueError):
    def __init__(self, code, reason):
        self.diagnostics = (diagnostic(code, reason,
            "Forneça histórico fechado com três períodos cronológicos utilizáveis", scope="global"),)
        super().__init__(f"{code}: {reason}")


@dataclass(frozen=True)
class ScoringConfig:
    version: str = "temporal-v1"
    feature_version: str = "product-series-founded-v1"
    playbook_version: str = "v1"
    dependency_digest: str = "43a420f22b5e31ceadf0946434689dca39359c7a69d358e4636ee6c0fb344843"
    fallback_features: tuple[str, ...] = ("product", "series")
    full_features: tuple[str, ...] = ("product", "series", "year_established")
    train_fraction: float = .60
    calibration_fraction: float = .80
    min_train: int = 200
    min_calibration: int = 100
    min_test: int = 100
    min_class: int = 20
    band_edges: tuple[float, float] = (.40, .70)
    min_band: int = 30
    band_tolerance: float = .10
    min_populated_bands: int = 2
    comparison_epsilon: float = 1e-12
    log_clip: float = 1e-15
    top_fractions: tuple[float, float] = (.10, .20)
    seed: int = 42
    logistic_c: float = 1.
    logistic_max_iter: int = 1000
    boosting_estimators: int = 100
    boosting_learning_rate: float = .05
    boosting_depth: int = 2
    boosting_min_leaf: int = 20
    prior_strength: float = 20.
    min_group: int = 20
    relative_delta: float = .05
    margin_quantiles: tuple[float, float] = (1/3, 2/3)
    explanation_tolerance: float = 1e-8

    def __post_init__(self):
        # Only the declared provenance allowlist may become prediction inputs.
        if self.fallback_features != ("product", "series") or self.full_features != (
                "product", "series", "year_established"):
            raise ValueError("feature_provenance: prediction allowlists cannot include other fields")
        if not 0 < self.train_fraction < self.calibration_fraction < 1:
            raise ValueError("Invalid chronological fractions")
        if not 0 < self.band_edges[0] < self.band_edges[1] < 1:
            raise ValueError("Invalid probability bands")
        if self.prior_strength <= 0 or self.min_group < 1:
            raise ValueError("Positive smoothing support required")

    @property
    def fingerprint(self):
        return digest(self)


DEFAULT_CONFIG = ScoringConfig()
FEATURE_PROVENANCE = MappingProxyType({
    "product": ("product",), "series": ("series",),
    "year_established": ("year_established",),
})
LIMITATIONS = (
    "Estimativa de Won versus Lost entre oportunidades engajadas que se resolveram; sem horizonte de fechamento.",
    "Aplicação a oportunidades abertas pressupõe transportabilidade; há censura e metadados estáticos.",
    "Seleção fixa entre candidatos no teste final gera otimismo pós-seleção; requer evidência prospectiva nova.",
    "Reutilizar o teste após mudar a política é exploratório, não validação em novo holdout.",
)


@dataclass(frozen=True)
class Factor:
    field: str
    observed_value: str | int | float | None
    contribution: float
    direction: str
    reference: str
    actionable: bool


@dataclass(frozen=True)
class ScoreResult:
    opportunity_id: str
    stage: str
    sales_agent: str | None = None
    manager: str | None = None
    regional_office: str | None = None
    product: str | None = None
    account: str | None = None
    state: str = "insufficient_data"
    route: str | None = None
    origin: str | None = None
    band: str | None = None
    band_kind: str | None = None
    potential_revenue: float | None = None
    probability: float | None = None
    expected_revenue: float | None = None
    relative_index: float | None = None
    evaluation_id: str | None = None
    fingerprint: str = ""
    observed_n: int = 0
    prior_strength: float = 0.
    effective_support: float = 0.
    evidence_strength: str = "indisponivel"
    backoff_path: tuple[str, ...] = ()
    diagnostics: tuple = ()
    explanation_scale: str | None = None
    base_value: float | None = None
    factors: tuple[Factor, ...] = ()
    next_action: str = "Sem ação recomendada com os dados atuais"

    def __post_init__(self):
        if self.stage not in ("Engaging", "Prospecting") or not self.opportunity_id:
            raise ValueError("Invalid active identity/stage")
        if self.observed_n < 0 or self.prior_strength < 0 or self.effective_support < 0:
            raise ValueError("Negative support")
        if self.potential_revenue is not None and not (
                math.isfinite(self.potential_revenue) and self.potential_revenue > 0):
            raise ValueError("Invalid potential revenue")
        if self.state == "calibrated":
            if self.stage != "Engaging" or self.route not in ("full", "fallback"):
                raise ValueError("Only Engaging model routes support probabilities")
            validate_probabilities((self.probability,))
            if self.potential_revenue is None or self.expected_revenue is None or not math.isclose(
                    self.expected_revenue, self.probability * self.potential_revenue,
                    rel_tol=1e-12, abs_tol=1e-12):
                raise ValueError("Expected revenue must equal probability times catalog price")
            if self.band_kind != "probability" or self.band not in ("baixa", "media", "alta") or not self.evaluation_id:
                raise ValueError("Calibrated score needs probability-band evaluation provenance")
            if self.relative_index is not None:
                raise ValueError("Calibrated score cannot own a relative index")
        elif self.state in ("relative", "insufficient_data"):
            if self.probability is not None or self.expected_revenue is not None:
                raise ValueError("Unvalidated states cannot own probabilistic values")
            if self.state == "relative":
                if self.relative_index is None or not math.isfinite(self.relative_index):
                    raise ValueError("Relative state needs a finite index")
                if self.band_kind != "relative" or self.band not in ("baixa", "media", "alta"):
                    raise ValueError("Relative state needs its own band")
            elif any(item is not None for item in (self.band, self.band_kind, self.relative_index, self.base_value)) or self.factors:
                raise ValueError("Insufficient state cannot invent a score or factors")
        else:
            raise ValueError("Unknown score state")

    def to_dict(self):
        result = {field.name: serialize(getattr(self, field.name)) for field in fields(self)}
        if self.state != "calibrated":
            result.pop("probability")
            result.pop("expected_revenue")
        if self.state != "relative":
            result.pop("relative_index")
        return result


@dataclass(frozen=True)
class PeriodEvidence:
    period: str
    ids: tuple[str, ...]
    wins: int
    losses: int
    global_count: int
    excluded: tuple[tuple[str, tuple[str, ...]], ...]

    @property
    def count(self):
        return len(self.ids)


@dataclass(frozen=True)
class BandEvidence:
    band: str
    count: int
    mean_probability: float | None
    observed_rate: float | None
    supported: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class TopKMetric:
    fraction: float
    k: int
    precision: float
    realized_value_share: float | None
    financial_unavailable_reason: str | None


@dataclass(frozen=True)
class SegmentEvidence:
    field: str
    value: str
    count: int
    observed_rate: float
    mean_probability: float
    brier: float
    log_loss: float


@dataclass(frozen=True)
class CandidateEvaluation:
    evaluation_id: str
    candidate: str
    route: str
    status: str
    config_fingerprint: str
    split_fingerprint: str
    feature_fingerprint: str
    feature_names: tuple[str, ...]
    periods: tuple[PeriodEvidence, ...]
    train_boundary: str
    calibration_boundary: str
    baseline_rate: float | None
    brier: float | None
    log_loss: float | None
    baseline_brier: float | None
    baseline_log_loss: float | None
    bands: tuple[BandEvidence, ...]
    top_k: tuple[TopKMetric, ...]
    segments: tuple[SegmentEvidence, ...]
    reasons: tuple[str, ...]
    unavailable_reasons: tuple[str, ...]
    natural_missing_account_count: int
    financial_valid_count: int
    limitations: tuple[str, ...] = LIMITATIONS

    @property
    def test_ids(self):
        return self.periods[2].ids


@dataclass(frozen=True)
class RouteSelection:
    route: str
    candidate: str | None
    evaluation_id: str | None
    reason: str


@dataclass(frozen=True)
class ScoringBundle:
    fingerprint: str
    config_version: str
    candidate_evaluations: tuple[CandidateEvaluation, ...]
    selected_routes: tuple[RouteSelection, ...]
    scores: tuple[ScoreResult, ...]
    input_diagnostics: tuple
    source_identity: Mapping

    def __post_init__(self):
        expected = {(candidate, route) for candidate in ("logistic", "boosting") for route in ("full", "fallback")}
        if len(self.candidate_evaluations) != 4 or {
                (item.candidate, item.route) for item in self.candidate_evaluations} != expected:
            raise ValueError("Bundle publication requires all four route outcomes")
        object.__setattr__(self, "source_identity", MappingProxyType(dict(self.source_identity)))

    def to_dict(self):
        return serialize(self)


@dataclass(frozen=True)
class TemporalSplit:
    train: tuple[Mapping, ...]
    calibration: tuple[Mapping, ...]
    test: tuple[Mapping, ...]
    train_boundary: date
    calibration_boundary: date

    @property
    def fingerprint(self):
        return digest({"boundaries": (self.train_boundary, self.calibration_boundary),
            "ids": tuple(tuple(row["opportunity_id"] for row in period)
                for period in (self.train, self.calibration, self.test))})


@dataclass(frozen=True)
class FeatureSupport:
    route: str
    products: tuple[str, ...]
    series: tuple[str, ...]
    year_min: int | None
    year_max: int | None


@dataclass(frozen=True)
class CandidateFit:
    candidate: str
    route: str
    support: FeatureSupport
    periods: tuple[tuple[Mapping, ...], ...]
    evidence: tuple[PeriodEvidence, ...]
    pipeline: Any
    calibrated: Any
    feature_names: tuple[str, ...]
    fit_reasons: tuple[str, ...]
    failed: bool
    config_fingerprint: str


def _records(records):
    return records.to_dict("records") if hasattr(records, "to_dict") else records


def split_closed_history(records, config=DEFAULT_CONFIG):
    history = [dict(row) for row in _records(records)
        if row.get("eligible_history") and row.get("deal_stage") in ("Won", "Lost")]
    for row in history:
        value = row.get("close_date")
        if not isinstance(value, date):
            raise ScoringValidationError("invalid_history_date", "Histórico elegível contém close_date inválido")
    history.sort(key=lambda row: (row["close_date"], row["opportunity_id"]))
    if len({row["opportunity_id"] for row in history}) != len(history):
        raise ScoringValidationError("duplicate_history_id", "Histórico contém oportunidade duplicada")
    counts = {}
    for row in history:
        counts[row["close_date"]] = counts.get(row["close_date"], 0) + 1
    cumulative, first, second = 0, None, None
    for day, count in counts.items():
        cumulative += count
        if first is None and cumulative >= math.ceil(config.train_fraction * len(history)):
            first = day
        elif first is not None and second is None and cumulative >= math.ceil(config.calibration_fraction * len(history)):
            second = day
    if first is None or second is None:
        raise ScoringValidationError("insufficient_temporal_periods", "Não há três períodos cronológicos")
    periods = tuple(tuple(MappingProxyType(row) for row in history if predicate(row["close_date"]))
        for predicate in (lambda day: day <= first, lambda day: first < day <= second, lambda day: day > second))
    if not all(periods):
        raise ScoringValidationError("insufficient_temporal_periods", "Uma divisão cronológica está vazia")
    return TemporalSplit(*periods, first, second)


def feature_record(row, route, config=DEFAULT_CONFIG):
    if route not in ("full", "fallback"):
        raise ValueError("Unknown account route")
    names = config.full_features if route == "full" else config.fallback_features
    return {name: row.get(name) for name in names}


def support_reasons(row, route, support=None):
    reasons = []
    if not row.get("product") or not row.get("series"):
        reasons.append("missing_product_or_series")
    price = row.get("sales_price")
    if not isinstance(price, (int, float)) or not math.isfinite(price) or price <= 0:
        reasons.append("invalid_price")
    if row.get("product_match") != "both":
        reasons.append("unmatched_product")
    if row.get("seller_match") != "both":
        reasons.append("unmatched_seller")
    if route == "full":
        year = row.get("year_established")
        if row.get("account_match") != "both" or not isinstance(year, (int, float)) or not math.isfinite(year) or year <= 0 or int(year) != year:
            reasons.append("unsupported_account_year")
        elif support and (support.year_min is None or not support.year_min <= year <= support.year_max):
            reasons.append("year_outside_training_support")
    if support:
        if row.get("product") not in support.products:
            reasons.append("unseen_product")
        if row.get("series") not in support.series:
            reasons.append("unseen_series")
    return tuple(reasons)


def _route_periods(split, route):
    train = [row for row in split.train if not support_reasons(row, route)]
    years = [row["year_established"] for row in train] if route == "full" else []
    support = FeatureSupport(route, tuple(sorted({row["product"] for row in train})),
        tuple(sorted({row["series"] for row in train})), min(years) if years else None,
        max(years) if years else None)
    periods, evidence = [], []
    for name, rows in zip(("train", "calibration", "test"), (split.train, split.calibration, split.test)):
        eligible, excluded = [], []
        for row in rows:
            reasons = support_reasons(row, route, support)
            if reasons:
                excluded.append((row["opportunity_id"], reasons))
            else:
                eligible.append(row)
        periods.append(tuple(eligible))
        wins = sum(row["deal_stage"] == "Won" for row in eligible)
        evidence.append(PeriodEvidence(name, tuple(row["opportunity_id"] for row in eligible),
            wins, len(eligible)-wins, len(rows), tuple(excluded)))
    return support, tuple(periods), tuple(evidence)


def feature_frame(records, route, config=DEFAULT_CONFIG):
    import pandas as pd
    columns = config.full_features if route == "full" else config.fallback_features
    return pd.DataFrame([feature_record(row, route, config) for row in records], columns=columns,
        index=[row["opportunity_id"] for row in records])


def fit_candidate(split, candidate, route, config=DEFAULT_CONFIG):
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.exceptions import ConvergenceWarning
    from sklearn.frozen import FrozenEstimator
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    if candidate not in ("logistic", "boosting") or route not in ("full", "fallback"):
        raise ValueError("Unknown candidate or route")
    support, periods, evidence = _route_periods(split, route)
    pipeline = calibrated = None
    reasons, names, failed = [], (), False
    train, calibration, _ = periods
    if not train or len({row["deal_stage"] for row in train}) != 2:
        reasons.append("training_requires_both_classes")
    else:
        transforms = [("categorical", OneHotEncoder(drop=None, sparse_output=False,
            handle_unknown="error"), ["product", "series"])]
        if route == "full":
            transforms.append(("numeric", StandardScaler(), ["year_established"]))
        estimator = (LogisticRegression(l1_ratio=0, C=config.logistic_c, solver="lbfgs",
            max_iter=config.logistic_max_iter, random_state=config.seed) if candidate == "logistic"
            else GradientBoostingClassifier(loss="log_loss", n_estimators=config.boosting_estimators,
                learning_rate=config.boosting_learning_rate, max_depth=config.boosting_depth,
                min_samples_leaf=config.boosting_min_leaf, subsample=1., random_state=config.seed,
                n_iter_no_change=None))
        training_complete = False
        try:
            pipeline = Pipeline((("preprocessor", ColumnTransformer(transforms)), ("estimator", estimator)))
            with warnings.catch_warnings():
                warnings.simplefilter("error", ConvergenceWarning)
                pipeline.fit(feature_frame(train, route, config), [int(row["deal_stage"] == "Won") for row in train])
            training_complete = True
            names = tuple(pipeline.named_steps["preprocessor"].get_feature_names_out())
            if not calibration or len({row["deal_stage"] for row in calibration}) != 2:
                reasons.append("calibration_requires_both_classes")
            else:
                calibrated = CalibratedClassifierCV(FrozenEstimator(pipeline), method="sigmoid", ensemble=False)
                with warnings.catch_warnings():
                    warnings.simplefilter("error", ConvergenceWarning)
                    calibrated.fit(feature_frame(calibration, route, config),
                        [int(row["deal_stage"] == "Won") for row in calibration])
        except (ValueError, RuntimeError, FloatingPointError, ConvergenceWarning) as exc:
            # A failed calibrator may leave a fitted raw model for later relative use.
            failed = True
            calibrated = None
            if not training_complete:
                pipeline = None
            reasons.append(f"fit_failed:{type(exc).__name__}:{exc}")
    return CandidateFit(candidate, route, support, periods, evidence, pipeline,
        calibrated, names, tuple(reasons), failed, config.fingerprint)


def validate_probabilities(probabilities):
    if any(not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1
           for value in probabilities):
        raise ValueError("invalid_probability: values must be finite in [0,1]")


def probability_band(probability, config=DEFAULT_CONFIG):
    validate_probabilities((probability,))
    return "baixa" if probability < config.band_edges[0] else "media" if probability < config.band_edges[1] else "alta"


def probability_losses(labels, probabilities, config=DEFAULT_CONFIG):
    if not labels or len(labels) != len(probabilities) or any(label not in (0, 1) for label in labels):
        raise ValueError("Invalid probability evaluation cohort")
    validate_probabilities(probabilities)
    brier = sum((probability-label)**2 for label, probability in zip(labels, probabilities)) / len(labels)
    loss = -sum(label*math.log(max(config.log_clip, min(1-config.log_clip, probability)))
        + (1-label)*math.log(1-max(config.log_clip, min(1-config.log_clip, probability)))
        for label, probability in zip(labels, probabilities)) / len(labels)
    return brier, loss


def band_evidence(labels, probabilities, config=DEFAULT_CONFIG):
    if len(labels) != len(probabilities):
        raise ValueError("Band cohort mismatch")
    validate_probabilities(probabilities)
    output = []
    for band in ("baixa", "media", "alta"):
        pairs = [(label, probability) for label, probability in zip(labels, probabilities)
            if probability_band(probability, config) == band]
        if not pairs:
            output.append(BandEvidence(band, 0, None, None, False, ("empty_band",)))
            continue
        predicted = sum(pair[1] for pair in pairs) / len(pairs)
        observed = sum(pair[0] for pair in pairs) / len(pairs)
        reasons = []
        if len(pairs) < config.min_band:
            reasons.append("insufficient_band_support")
        # isclose absorbs representation of the fixed boundary, not a policy tolerance.
        difference = abs(predicted-observed)
        if difference > config.band_tolerance and not math.isclose(difference, config.band_tolerance, rel_tol=0, abs_tol=1e-15):
            reasons.append("incoherent_band")
        output.append(BandEvidence(band, len(pairs), predicted, observed, not reasons, tuple(reasons)))
    return tuple(output)


def publication_reasons(periods, brier, loss, baseline_brier, baseline_loss, bands, config=DEFAULT_CONFIG):
    reasons = []
    for period, minimum in zip(periods, (config.min_train, config.min_calibration, config.min_test)):
        if period.count < minimum:
            reasons.append(f"{period.period}_support_below_{minimum}")
        if min(period.wins, period.losses) < config.min_class:
            reasons.append(f"{period.period}_class_support_below_{config.min_class}")
    if not baseline_brier-brier > config.comparison_epsilon:
        reasons.append("brier_not_strictly_better")
    if not baseline_loss-loss > config.comparison_epsilon:
        reasons.append("log_loss_not_strictly_better")
    populated = [band for band in bands if band.count]
    if any(not band.supported for band in populated):
        reasons.append("populated_band_failed")
    if sum(band.supported for band in populated) < config.min_populated_bands:
        reasons.append("fewer_than_two_supported_bands")
    if any(left.observed_rate > right.observed_rate for left, right in zip(populated, populated[1:])):
        reasons.append("nonmonotonic_observed_bands")
    return tuple(reasons)


def ranking_metrics(rows, probabilities, config=DEFAULT_CONFIG):
    if not rows or len(rows) != len(probabilities):
        raise ValueError("Invalid ranking cohort")
    validate_probabilities(probabilities)
    band_rank = {"baixa": 0, "media": 1, "alta": 2}
    ranked = sorted(zip(rows, probabilities), key=lambda pair: (
        -band_rank[probability_band(pair[1], config)], -pair[1]*pair[0]["sales_price"], pair[0]["opportunity_id"]))
    valid_financial = all(row.get("financial_eligible") and isinstance(row.get("close_value"), (int, float))
        and math.isfinite(row["close_value"]) and row["close_value"] >= 0
        and (row["deal_stage"] == "Won" or row["close_value"] == 0) for row in rows)
    total = sum(row["close_value"] for row in rows if row["deal_stage"] == "Won") if valid_financial else None
    unavailable = "incomplete_financial_labels" if not valid_financial else "no_positive_realized_total" if total <= 0 else None
    result = []
    for fraction in config.top_fractions:
        k = math.ceil(fraction*len(rows))
        top = [pair[0] for pair in ranked[:k]]
        precision = sum(row["deal_stage"] == "Won" for row in top) / k
        share = None if unavailable else sum(row["close_value"] for row in top if row["deal_stage"] == "Won") / total
        result.append(TopKMetric(fraction, k, precision, share, unavailable))
    return tuple(result)


def _segments(rows, probabilities, config):
    result = []
    for field in ("sales_agent", "manager", "regional_office"):
        groups = {}
        for row, probability in zip(rows, probabilities):
            groups.setdefault(str(row.get(field) or "Não informado"), []).append((int(row["deal_stage"] == "Won"), probability))
        for value, pairs in sorted(groups.items()):
            labels, predicted = zip(*pairs)
            brier, loss = probability_losses(labels, predicted, config)
            result.append(SegmentEvidence(field, value, len(pairs), sum(labels)/len(pairs),
                sum(predicted)/len(pairs), brier, loss))
    return tuple(result)


def evaluate_candidate(fitted, split, config=DEFAULT_CONFIG):
    if fitted.config_fingerprint != config.fingerprint:
        raise ValueError("Policy changed between fit and evaluation")
    train, _, test = fitted.periods
    baseline = sum(row["deal_stage"] == "Won" for row in train)/len(train) if train else None
    reasons = list(fitted.fit_reasons)
    unavailable = []
    brier = loss = base_brier = base_loss = None
    bands, top, segments = (), (), ()
    failed = fitted.failed
    if fitted.calibrated is None or not test:
        unavailable.append("probability_metrics_unavailable:unfitted_calibrator_or_empty_test")
        reasons.extend(publication_reasons(fitted.evidence, 0, 0, 1, 1, (), config))
    else:
        try:
            probabilities = tuple(float(value) for value in fitted.calibrated.predict_proba(feature_frame(test, fitted.route, config))[:, 1])
            labels = tuple(int(row["deal_stage"] == "Won") for row in test)
            brier, loss = probability_losses(labels, probabilities, config)
            base_brier, base_loss = probability_losses(labels, (baseline,)*len(test), config)
            bands = band_evidence(labels, probabilities, config)
            reasons.extend(publication_reasons(fitted.evidence, brier, loss, base_brier, base_loss, bands, config))
            top = ranking_metrics(test, probabilities, config)
            segments = _segments(test, probabilities, config)
            unavailable.extend(sorted({item.financial_unavailable_reason for item in top if item.financial_unavailable_reason}))
        except (ValueError, RuntimeError, FloatingPointError) as exc:
            failed = True
            reasons.append(f"evaluation_failed:{type(exc).__name__}:{exc}")
            unavailable.append("probability_metrics_unavailable:invalid_prediction")
            brier = loss = base_brier = base_loss = None
            bands, top, segments = (), (), ()
    feature_identity = digest({"names": fitted.feature_names, "support": fitted.support,
        "provenance": FEATURE_PROVENANCE, "policy": config.feature_version})
    consumed_history = tuple(tuple({"features": feature_record(row, fitted.route, config),
        **{key: row.get(key) for key in ("opportunity_id", "deal_stage", "close_date", "close_value",
            "financial_eligible", "sales_price", "sales_agent", "manager", "regional_office")}}
        for row in period) for period in fitted.periods)
    evaluation_id = digest((config.fingerprint, split.fingerprint, feature_identity,
        fitted.candidate, fitted.route, consumed_history))
    natural_missing = sum(row.get("account_match") != "both" for period in (split.train, split.calibration, split.test) for row in period)
    limitations = LIMITATIONS + (("Nenhuma conta naturalmente ausente no histórico fechado: fallback validado por remoção intencional de atributos.",) if not natural_missing else ())
    return CandidateEvaluation(evaluation_id, fitted.candidate, fitted.route,
        "failed" if failed else "rejected" if reasons else "passed", config.fingerprint,
        split.fingerprint, feature_identity, fitted.feature_names, fitted.evidence,
        split.train_boundary.isoformat(), split.calibration_boundary.isoformat(), baseline,
        brier, loss, base_brier, base_loss, bands, top, segments,
        tuple(dict.fromkeys(reasons)), tuple(unavailable), natural_missing,
        sum(bool(row.get("financial_eligible")) for row in test), limitations)


def select_route(evaluations, route, config=DEFAULT_CONFIG):
    candidates = {item.candidate: item for item in evaluations if item.route == route}
    if set(candidates) != {"logistic", "boosting"}:
        raise ValueError("Selection requires both route candidates")
    passed = {name: item for name, item in candidates.items() if item.status == "passed"}
    if not passed:
        return RouteSelection(route, None, None, "no_validated_candidate")
    if len(passed) == 1:
        winner = next(iter(passed.values()))
        return RouteSelection(route, winner.candidate, winner.evaluation_id, "only_validated_candidate")
    logistic, boosting = passed["logistic"], passed["boosting"]
    winner, reason = logistic, "logistic_default_inconsistent_gains"
    if logistic.test_ids != boosting.test_ids or logistic.split_fingerprint != boosting.split_fingerprint:
        reason = "incomparable_test_cohorts"
    elif any(item.financial_unavailable_reason for candidate in (logistic, boosting) for item in candidate.top_k):
        reason = "financial_comparison_unavailable"
    elif (tuple(item.fraction for item in logistic.top_k) != config.top_fractions or
          tuple(item.fraction for item in boosting.top_k) != config.top_fractions or
          any(a.k != b.k or a.k != math.ceil(a.fraction*len(logistic.test_ids))
              for a, b in zip(logistic.top_k, boosting.top_k))):
        reason = "incomparable_top_k"
    elif all(value is not None and math.isfinite(value) for candidate in (logistic, boosting)
             for value in (candidate.brier, candidate.log_loss)) and all(
             b.precision-a.precision > config.comparison_epsilon and
             a.realized_value_share is not None and b.realized_value_share is not None and
             b.realized_value_share-a.realized_value_share > config.comparison_epsilon
             for a, b in zip(logistic.top_k, boosting.top_k)) and (
             boosting.brier-logistic.brier <= config.comparison_epsilon and
             boosting.log_loss-logistic.log_loss <= config.comparison_epsilon):
        winner, reason = boosting, "consistent_boosting_gains"
    return RouteSelection(route, winner.candidate, winner.evaluation_id, reason)


def evaluate_history(records, config=DEFAULT_CONFIG):
    """One fixed pass yields all four outcomes, including controlled rejections."""
    split = split_closed_history(records, config)
    fitted = tuple(fit_candidate(split, candidate, route, config)
        for candidate in ("logistic", "boosting") for route in ("full", "fallback"))
    evaluations = tuple(evaluate_candidate(model, split, config) for model in fitted)
    selections = tuple(select_route(evaluations, route, config) for route in ("full", "fallback"))
    return split, fitted, evaluations, selections


def build_scoring_bundle(dataset, config=DEFAULT_CONFIG, identity=None):
    """Fit the frozen policy once and publish every active row in an honest state."""
    required = ("opportunities", "data_fingerprint", "diagnostics")
    if any(not hasattr(dataset, name) for name in required):
        raise ValueError("dataset must provide opportunities, diagnostics and data_fingerprint")
    records = tuple(dict(row) for row in _records(dataset.opportunities))
    _, fitted, evaluations, selections = evaluate_history(records, config)
    source = source_identity() if identity is None else MappingProxyType(dict(identity))
    if set(source) != {"revision", "source_digest"} or not source["source_digest"]:
        raise ValueError("Source identity requires revision and source_digest")
    fingerprint = digest((dataset.data_fingerprint, config.fingerprint, source["source_digest"]))
    scores = score_active(records, fitted, evaluations, selections, fingerprint,
                          dataset.diagnostics, config)
    return ScoringBundle(fingerprint, config.version, evaluations, selections, scores,
                         tuple(_copy_diagnostic(item) for item in dataset.diagnostics), source)


def source_identity(root=None):
    """Identify source bytes without assuming Git metadata exists in Cloud."""
    root = Path(root).resolve() if root is not None else Path(__file__).resolve().parent
    file_hashes = {}
    for name in ("app.py", "data.py", "scoring.py", "requirements.txt"):
        path = root / name
        file_hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "missing"
    try:
        revision = subprocess.run(("git", "rev-parse", "HEAD"), cwd=root, check=True,
            text=True, capture_output=True, timeout=5).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        revision = None
    return MappingProxyType({"revision": revision, "source_digest": digest(file_hashes)})


def _copy_diagnostic(item):
    if isinstance(item, Mapping):
        values = dict(item)
    elif is_dataclass(item):
        values = asdict(item)
    else:
        values = {name: getattr(item, name) for name in
                  ("code", "scope", "file", "opportunity_id", "field", "reason", "correction")}
    return MappingProxyType(values)


def _identity(row):
    return dict(opportunity_id=str(row.get("opportunity_id") or ""),
        stage=row.get("deal_stage"), sales_agent=row.get("sales_agent"),
        manager=row.get("manager"), regional_office=row.get("regional_office"),
        product=row.get("product"), account=row.get("account"))


def evidence_strength(observed_n):
    if observed_n < 0:
        raise ValueError("observed support cannot be negative")
    return ("forte" if observed_n >= 100 else "moderada" if observed_n >= 30 else
            "fraca" if observed_n else "indisponivel")


def smoothed_rate(wins, count, parent_rate, prior_strength):
    if any(not isinstance(value, int) for value in (wins, count)) or count < 0 or not 0 <= wins <= count:
        raise ValueError("counts must be nonnegative integers with wins <= count")
    if not isinstance(prior_strength, (int, float)) or not math.isfinite(prior_strength) or prior_strength <= 0:
        raise ValueError("prior strength must be finite and positive")
    if not isinstance(parent_rate, (int, float)) or not math.isfinite(parent_rate) or not 0 <= parent_rate <= 1:
        raise ValueError("parent rate must be finite in [0,1]")
    return (wins + prior_strength * parent_rate) / (count + prior_strength)


def _direction(value):
    return "favoravel" if value > 1e-12 else "desfavoravel" if value < -1e-12 else "neutro"


def _relative_band(value, global_rate, config):
    delta = value - global_rate
    return "baixa" if delta < -config.relative_delta else "media" if delta < config.relative_delta else "alta"


def _history(records):
    return tuple(row for row in records if row.get("eligible_history") and
                 row.get("deal_stage") in ("Won", "Lost") and isinstance(row.get("close_date"), date))


def _group_counts(history, row, keys):
    if any(row.get(key) is None for key in keys):
        return None
    members = [item for item in history if all(item.get(key) == row.get(key) for key in keys)]
    return sum(item["deal_stage"] == "Won" for item in members), len(members)


def _relative_evidence(row, history, levels, config):
    total = len(history)
    if not total:
        return None
    global_rate = sum(item["deal_stage"] == "Won" for item in history) / total
    selected_rate, selected_n = global_rate, total
    selected_prior, effective = 0., float(total)
    factors, path = [], []
    for name, keys in levels:
        counts = _group_counts(history, row, keys)
        if counts is None:
            path.append(f"{name}:missing_key")
            continue
        wins, count = counts
        if count < config.min_group:
            path.append(f"{name}:observed_n={count}<{config.min_group}")
            continue
        child = smoothed_rate(wins, count, selected_rate, config.prior_strength)
        contribution = child - selected_rate
        observed = " + ".join(str(row.get(key)) for key in keys)
        factors.append(Factor(name, observed, contribution, _direction(contribution),
            f"Associação histórica; {count} observações e prior {config.prior_strength:g}",
            "product" in keys))
        selected_rate, selected_n = child, count
        selected_prior, effective = config.prior_strength, count + config.prior_strength
        path.append(f"eligible:{name}:observed_n={count}")
    selected = next((entry.split(":", 2)[1] for entry in reversed(path)
                     if entry.startswith("eligible:")), "global")
    path.append(f"selected:{selected}")
    return (selected_rate, global_rate, tuple(factors), selected_n, selected_prior,
            float(effective), tuple(path), global_rate)


def score_prospecting(row, history, fingerprint, config=DEFAULT_CONFIG):
    evidence = _relative_evidence(row, _history(history), (
        ("product", ("product",)),
        ("product+seller", ("product", "sales_agent")),
        ("product+seller+account", ("product", "sales_agent", "account"))), config)
    if evidence is None:
        return _insufficient(row, fingerprint, (diagnostic("empty_history",
            "Não há histórico fechado para sustentar a prioridade",
            "Forneça histórico Won/Lost datado", opportunity_id=row.get("opportunity_id")),))
    value, base, factors, observed_n, prior, effective, path, global_rate = evidence
    action = recommend_action("Prospecting", factors)
    return ScoreResult(**_identity(row), state="relative", route="prospecting",
        origin="historical_evidence", band=_relative_band(value, global_rate, config),
        band_kind="relative", potential_revenue=_price(row), relative_index=value,
        fingerprint=fingerprint, observed_n=observed_n, prior_strength=prior,
        effective_support=effective, evidence_strength=evidence_strength(observed_n),
        backoff_path=path, explanation_scale="relative_index", base_value=base,
        factors=factors, next_action=action)


def _price(row):
    value = row.get("sales_price")
    return float(value) if isinstance(value, (int, float)) and math.isfinite(value) and value > 0 else None


def _insufficient(row, fingerprint, diagnostics):
    return ScoreResult(**_identity(row), state="insufficient_data", fingerprint=fingerprint,
        diagnostics=tuple(_copy_diagnostic(item) for item in diagnostics))


def _feature_field(name):
    transformed = name.split("__", 1)[-1]
    for field in ("product", "series", "year_established"):
        if transformed == field or transformed.startswith(field + "_"):
            return field
    raise ValueError(f"Unsupported transformed feature: {name}")


def _factors(names, values, row, reference):
    grouped = {field: 0. for field in ("product", "series", "year_established")}
    for name, value in zip(names, values):
        grouped[_feature_field(name)] += float(value)
    return tuple(Factor(field, row.get(field), contribution, _direction(contribution), reference,
                        field in ("product", "series"))
                 for field, contribution in grouped.items()
                 if field in row and row.get(field) is not None)


def _tree_explanation(estimator, transformed):
    initial = float(estimator._raw_predict_init(transformed)[0, 0])
    contributions = [0.] * transformed.shape[1]
    base = initial
    for stage in estimator.estimators_:
        tree = stage[0].tree_
        value = lambda node: float(tree.value[node].reshape(-1)[0])
        node = 0
        base += estimator.learning_rate * value(node)
        while tree.children_left[node] != tree.children_right[node]:
            feature = int(tree.feature[node])
            child = (tree.children_left[node] if transformed[0, feature] <= tree.threshold[node]
                     else tree.children_right[node])
            contributions[feature] += estimator.learning_rate * (value(child) - value(node))
            node = child
    return base, tuple(contributions)


def _calibration_coefficients(calibrated):
    try:
        classifiers = calibrated.calibrated_classifiers_
        calibrators = classifiers[0].calibrators
        if len(classifiers) != 1 or len(calibrators) != 1:
            raise ValueError("Expected one binary sigmoid calibrator")
        return float(calibrators[0].a_), float(calibrators[0].b_)
    except (AttributeError, IndexError, TypeError) as exc:
        raise ValueError("Unsupported pinned sigmoid calibration internals") from exc


def apply_calibration_explanation(base, factors, slope, intercept):
    if not all(math.isfinite(value) for value in (base, slope, intercept)):
        raise ValueError("Calibration explanation requires finite values")
    transformed = tuple(Factor(item.field, item.observed_value, -slope * item.contribution,
        _direction(-slope * item.contribution), f"{item.reference}; log-odds calibrado", item.actionable)
        for item in factors)
    return -slope * base - intercept, transformed


def _expit(value):
    if value >= 0:
        return 1 / (1 + math.exp(-value))
    exponential = math.exp(value)
    return exponential / (1 + exponential)


def explain_score(fitted, row, *, calibrated=False, config=DEFAULT_CONFIG):
    if fitted.pipeline is None:
        raise ValueError("Cannot explain an unfitted candidate")
    frame = feature_frame((row,), fitted.route, config)
    transformed = fitted.pipeline.named_steps["preprocessor"].transform(frame)
    estimator = fitted.pipeline.named_steps["estimator"]
    if fitted.candidate == "logistic":
        base = float(estimator.intercept_[0])
        raw = tuple(float(value) for value in transformed[0] * estimator.coef_[0])
    elif fitted.candidate == "boosting":
        base, raw = _tree_explanation(estimator, transformed)
    else:
        raise ValueError("Unknown fitted candidate")
    factors = _factors(fitted.feature_names, raw, row,
                       "Contribuição local no margin bruto do modelo")
    margin = float(fitted.pipeline.decision_function(frame)[0])
    if not math.isclose(base + sum(item.contribution for item in factors), margin,
                        rel_tol=config.explanation_tolerance, abs_tol=config.explanation_tolerance):
        raise ValueError("Raw explanation does not reconstruct model margin")
    if not calibrated:
        return "raw_margin", base, factors
    if fitted.calibrated is None:
        raise ValueError("Cannot explain unavailable calibration")
    slope, intercept = _calibration_coefficients(fitted.calibrated)
    base, factors = apply_calibration_explanation(base, factors, slope, intercept)
    probability = float(fitted.calibrated.predict_proba(frame)[0, 1])
    if not math.isclose(_expit(base + sum(item.contribution for item in factors)), probability,
                        rel_tol=config.explanation_tolerance, abs_tol=config.explanation_tolerance):
        raise ValueError("Calibrated explanation does not reconstruct probability")
    return "calibrated_log_odds", base, factors


def summarize_factors(factors, limit=2):
    positive = tuple(sorted((item for item in factors if item.contribution > 1e-12),
                            key=lambda item: (-item.contribution, item.field))[:limit])
    negative = tuple(sorted((item for item in factors if item.contribution < -1e-12),
                            key=lambda item: (item.contribution, item.field))[:limit])
    return MappingProxyType({"favoraveis": positive, "desfavoraveis": negative,
        "mensagem_favoravel": None if positive else "Sem fator favorável sustentado",
        "mensagem_desfavoravel": None if negative else "Sem fator desfavorável sustentado"})


def recommend_action(stage, factors, playbook_version="v1"):
    if playbook_version != "v1" or stage not in ("Engaging", "Prospecting"):
        raise ValueError("Unknown playbook version or stage")
    actionable = [item for item in factors if item.actionable and
                  abs(item.contribution) > 1e-12 and
                  (item.field in ("product", "series") or item.field.startswith("product+"))]
    if not actionable:
        return "Sem ação recomendada com os dados atuais"
    chosen = min(actionable, key=lambda item: (-abs(item.contribution), item.field))
    del chosen
    return ("Confirmar com a conta se o produto atende à necessidade e combinar o próximo passo comercial"
            if stage == "Engaging" else
            "Validar a necessidade para este produto antes de avançar para engajamento")


def _fit_lookup(fitted):
    return {(item.candidate, item.route): item for item in fitted}


def _evaluation_lookup(evaluations):
    return {(item.candidate, item.route): item for item in evaluations}


def _route_for_active(row, fitted, config):
    fits = _fit_lookup(fitted)
    desired = row.get("route") if row.get("route") in ("full", "fallback") else "fallback"
    routes = ("full", "fallback") if desired == "full" else ("fallback",)
    diagnostics = []
    for route in routes:
        representative = fits.get(("logistic", route)) or fits.get(("boosting", route))
        if representative and not support_reasons(row, route, representative.support):
            if desired == "full" and route == "fallback":
                diagnostics.append(diagnostic("full_route_unsupported",
                    "Atributos da conta estão fora do suporte aprendido; usada rota sem conta",
                    "Confira account e year_established", field="year_established",
                    opportunity_id=row.get("opportunity_id")))
            return route, tuple(diagnostics)
    reasons = support_reasons(row, desired)
    diagnostics.append(diagnostic("unsupported_active_features", ", ".join(reasons) or
        "Nenhuma rota treinada suporta a oportunidade", "Corrija produto, série, preço ou conta",
        opportunity_id=row.get("opportunity_id"), scope="row"))
    return None, tuple(diagnostics)


def _margin_band(margin, training_margins, config):
    import numpy as np
    if not training_margins or not all(math.isfinite(value) for value in training_margins):
        raise ValueError("Training margins unavailable")
    lower, upper = (float(value) for value in np.quantile(training_margins,
        config.margin_quantiles, method="linear"))
    if math.isclose(lower, upper, rel_tol=0, abs_tol=config.explanation_tolerance):
        return "media"
    return "baixa" if margin < lower else "media" if margin < upper else "alta"


def _suppression_diagnostic(row, route, evaluations):
    reasons = tuple(dict.fromkeys(reason for item in evaluations if item.route == route
                                  for reason in item.reasons))
    return diagnostic("probability_suppressed",
        "Probabilidade não publicada: " + (", ".join(reasons) if reasons else "banda ativa não validada"),
        "Use a prioridade relativa e colete novos resultados para recalibrar",
        opportunity_id=row.get("opportunity_id"))


def _historical_engaging(row, history, fingerprint, route, diagnostics, config):
    evidence = _relative_evidence(row, history, (("product", ("product",)),), config)
    if evidence is None:
        return _insufficient(row, fingerprint, diagnostics + (diagnostic("empty_history",
            "Nenhum modelo ou histórico sustenta a prioridade",
            "Forneça histórico Won/Lost datado", opportunity_id=row.get("opportunity_id")),))
    value, base, factors, observed_n, prior, effective, path, global_rate = evidence
    return ScoreResult(**_identity(row), state="relative", route=route,
        origin="historical_evidence", band=_relative_band(value, global_rate, config),
        band_kind="relative", potential_revenue=_price(row), relative_index=value,
        fingerprint=fingerprint, observed_n=observed_n, prior_strength=prior,
        effective_support=effective, evidence_strength=evidence_strength(observed_n),
        backoff_path=path, diagnostics=diagnostics, explanation_scale="relative_index",
        base_value=base, factors=factors, next_action=recommend_action("Engaging", factors))


def _score_engaging(row, history, fitted, evaluations, selections, fingerprint, config):
    route, route_diagnostics = _route_for_active(row, fitted, config)
    if route is None:
        return _insufficient(row, fingerprint, route_diagnostics)
    fits, evidence = _fit_lookup(fitted), _evaluation_lookup(evaluations)
    selection = next((item for item in selections if item.route == route), None)
    if selection and selection.candidate:
        model = fits[(selection.candidate, route)]
        evaluation = evidence[(selection.candidate, route)]
        probability = float(model.calibrated.predict_proba(feature_frame((row,), route, config))[0, 1])
        validate_probabilities((probability,))
        band = probability_band(probability, config)
        band_record = next(item for item in evaluation.bands if item.band == band)
        if evaluation.status == "passed" and band_record.supported:
            scale, base, factors = explain_score(model, row, calibrated=True, config=config)
            return ScoreResult(**_identity(row), state="calibrated", route=route,
                origin=selection.candidate, band=band, band_kind="probability",
                potential_revenue=_price(row), probability=probability,
                expected_revenue=probability * _price(row), evaluation_id=evaluation.evaluation_id,
                fingerprint=fingerprint, observed_n=band_record.count,
                effective_support=float(band_record.count),
                evidence_strength=evidence_strength(band_record.count),
                diagnostics=route_diagnostics, explanation_scale=scale, base_value=base,
                factors=factors, next_action=recommend_action("Engaging", factors))
    diagnostics = route_diagnostics + (_suppression_diagnostic(row, route, evaluations),)
    for candidate in ("logistic", "boosting"):
        model = fits.get((candidate, route))
        if model is None or model.pipeline is None:
            continue
        try:
            scale, base, factors = explain_score(model, row, config=config)
            margin = base + sum(item.contribution for item in factors)
            training = tuple(float(value) for value in model.pipeline.decision_function(
                feature_frame(model.periods[0], route, config)))
            band = _margin_band(margin, training, config)
        except (ValueError, RuntimeError, FloatingPointError):
            continue
        evaluation = evidence.get((candidate, route))
        observed_n = len(model.periods[0])
        return ScoreResult(**_identity(row), state="relative", route=route, origin=candidate,
            band=band, band_kind="relative", potential_revenue=_price(row),
            relative_index=margin, evaluation_id=evaluation.evaluation_id if evaluation else None,
            fingerprint=fingerprint, observed_n=observed_n, effective_support=float(observed_n),
            evidence_strength=evidence_strength(observed_n), diagnostics=diagnostics,
            explanation_scale=scale, base_value=base, factors=factors,
            next_action=recommend_action("Engaging", factors))
    return _historical_engaging(row, history, fingerprint, route, diagnostics, config)


def score_active(records, fitted, evaluations, selections, fingerprint,
                 input_diagnostics=(), config=DEFAULT_CONFIG):
    records = tuple(dict(row) for row in _records(records))
    history = _history(records)
    diagnostics_by_id = {}
    for item in input_diagnostics:
        copied = _copy_diagnostic(item)
        if copied.get("opportunity_id"):
            diagnostics_by_id.setdefault(copied["opportunity_id"], []).append(copied)
    results = []
    for row in records:
        if row.get("deal_stage") not in ("Engaging", "Prospecting"):
            continue
        if not row.get("eligible_active"):
            issues = tuple(diagnostics_by_id.get(row.get("opportunity_id"), ())) or (
                diagnostic("unsupported_active", "Oportunidade ativa sem dados suficientes",
                    "Corrija os campos indicados no cadastro", opportunity_id=row.get("opportunity_id"),
                    scope="row"),)
            results.append(_insufficient(row, fingerprint, issues))
        elif row["deal_stage"] == "Prospecting":
            results.append(score_prospecting(row, history, fingerprint, config))
        else:
            results.append(_score_engaging(row, history, fitted, evaluations, selections,
                                            fingerprint, config))
    return tuple(results)


def rank_stage(scores, stage):
    if stage not in ("Engaging", "Prospecting"):
        raise ValueError("Unknown active stage")
    band_rank = {"alta": 0, "media": 1, "baixa": 2, None: 3}
    def key(item):
        if item.state == "calibrated":
            return (0, band_rank[item.band], -(item.expected_revenue or 0), item.opportunity_id)
        if item.state == "relative":
            partition = (item.route or "", item.origin or "", item.explanation_scale or "")
            return (1, partition, band_rank[item.band], -(item.relative_index or 0),
                    -(item.potential_revenue or 0), item.opportunity_id)
        return (2, item.opportunity_id)
    return tuple(sorted((item for item in scores if item.stage == stage), key=key))
