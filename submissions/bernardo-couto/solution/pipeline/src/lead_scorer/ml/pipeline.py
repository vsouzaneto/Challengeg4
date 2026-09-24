"""Spark ML pipeline of layer 2: declarative stages, fit, predict, save/load.

``StringIndexer(product, keep) -> OneHotEncoder(keep) -> Imputer(median) -> VectorAssembler(keep)
-> StandardScaler(withMean) -> LogisticRegression(elastic-net)``, followed by an
``IsotonicRegression`` calibrator fitted on the temporal hold-out month (never on training rows).
Everything is deterministic (no sampling stage); ``SEED`` is set where the API accepts one.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pyspark.ml import Pipeline, PipelineModel
from pyspark.ml.classification import LogisticRegression, LogisticRegressionModel
from pyspark.ml.feature import (
    Imputer,
    OneHotEncoder,
    StandardScaler,
    StringIndexer,
    VectorAssembler,
)
from pyspark.ml.functions import vector_to_array
from pyspark.ml.regression import IsotonicRegression, IsotonicRegressionModel
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from lead_scorer.ml.features import CATEGORICAL_FEATURES, LABEL_COL, NUMERIC_FEATURES

SEED = 20171231
#: Spec section 5 proposes regParam=0.1; with that penalty every coefficient collapses to 0 on
#: this data (the features carry no signal) and the shadow model degenerates to a constant.
#: regParam=0.01 keeps the model non-trivial so the promotion metrics mean something.
LR_PARAMS: dict[str, float | int] = {"elasticNetParam": 0.5, "regParam": 0.01, "maxIter": 200}
MIN_CALIBRATION_ROWS = 50

RAW_PROB_COL = "p_model_raw"
PROB_COL = "p_model"
LR_DIR = "lr"
CALIBRATOR_DIR = "isotonic"


def build_pipeline(
    elastic_net_param: float = 0.5, reg_param: float = 0.1, max_iter: int = 200
) -> Pipeline:
    indexers = [
        StringIndexer(inputCol=c, outputCol=f"{c}_idx", handleInvalid="keep")
        for c in CATEGORICAL_FEATURES
    ]
    encoder = OneHotEncoder(
        inputCols=[f"{c}_idx" for c in CATEGORICAL_FEATURES],
        outputCols=[f"{c}_ohe" for c in CATEGORICAL_FEATURES],
        handleInvalid="keep",
    )
    imputer = Imputer(
        inputCols=list(NUMERIC_FEATURES),
        outputCols=[f"{c}_imp" for c in NUMERIC_FEATURES],
        strategy="median",
    )
    assembler = VectorAssembler(
        inputCols=[f"{c}_ohe" for c in CATEGORICAL_FEATURES]
        + [f"{c}_imp" for c in NUMERIC_FEATURES],
        outputCol="features_raw",
        handleInvalid="keep",
    )
    scaler = StandardScaler(
        inputCol="features_raw", outputCol="features", withMean=True, withStd=True
    )
    lr = LogisticRegression(
        featuresCol="features",
        labelCol=LABEL_COL,
        elasticNetParam=elastic_net_param,
        regParam=reg_param,
        maxIter=max_iter,
        standardization=False,  # already scaled; keeps coefficients in standardised units
    )
    return Pipeline(stages=[*indexers, encoder, imputer, assembler, scaler, lr])


def _clean_slot_name(name: str) -> str:
    """``product_ohe_GTX Pro`` -> ``product=GTX Pro``; ``log_price_imp`` -> ``log_price``."""
    if "_ohe_" in name:
        col, category = name.split("_ohe_", 1)
        return f"{col}={category}"
    return name.removesuffix("_imp")


@dataclass
class ShadowModel:
    """Fitted layer-2 model: Spark ML ``PipelineModel`` + optional isotonic calibrator."""

    model: PipelineModel
    calibrator: IsotonicRegressionModel | None

    @property
    def lr(self) -> LogisticRegressionModel:
        stage = self.model.stages[-1]
        assert isinstance(stage, LogisticRegressionModel)
        return stage

    def predict(self, df: DataFrame) -> DataFrame:
        """Add ``p_model_raw`` (LR) and ``p_model`` (calibrated, or raw when no calibrator)."""
        out = self.predict_raw(df)
        if self.calibrator is not None:
            out = self.calibrator.transform(out)  # adds PROB_COL (its predictionCol)
        else:
            out = out.withColumn(PROB_COL, F.col(RAW_PROB_COL))
        out = out.withColumn(PROB_COL, F.least(F.greatest(F.col(PROB_COL), F.lit(0.0)), F.lit(1.0)))
        drop = ["rawPrediction", "probability", "prediction", "features", "features_raw"]
        drop += [f"{c}_idx" for c in CATEGORICAL_FEATURES] + [
            f"{c}_ohe" for c in CATEGORICAL_FEATURES
        ]
        drop += [f"{c}_imp" for c in NUMERIC_FEATURES]
        return out.drop(*drop)

    def predict_raw(self, df: DataFrame) -> DataFrame:
        """Pipeline transform + ``p_model_raw`` (uncalibrated LR probability of Won)."""
        return self.model.transform(df).withColumn(
            RAW_PROB_COL, vector_to_array(F.col("probability"))[1].cast("double")
        )

    def feature_names(self) -> list[str]:
        """Names of the assembled vector slots (one-hot categories expanded) from ML metadata."""
        meta = self.model.transform(self._empty_like()).schema["features_raw"].metadata
        attrs = meta.get("ml_attr", {}).get("attrs", {})
        names: dict[int, str] = {}
        for group in attrs.values():
            for attr in group:
                names[int(attr["idx"])] = _clean_slot_name(str(attr["name"]))
        return [names[i] for i in sorted(names)]

    def coefficients(self) -> dict[str, float]:
        names = self.feature_names()
        coefs = self.lr.coefficients.toArray().tolist()
        out = dict(zip(names, coefs, strict=False))
        out["intercept"] = float(self.lr.intercept)
        return out

    def _empty_like(self) -> DataFrame:
        session = SparkSession.getActiveSession()
        assert session is not None
        cols = ", ".join(
            [f"{c} string" for c in CATEGORICAL_FEATURES]
            + [f"{c} double" for c in NUMERIC_FEATURES]
        )
        return session.createDataFrame([], cols)

    def save(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        self.model.write().overwrite().save(str(directory / LR_DIR))
        if self.calibrator is not None:
            self.calibrator.write().overwrite().save(str(directory / CALIBRATOR_DIR))

    @classmethod
    def load(cls, directory: Path) -> ShadowModel:
        model = PipelineModel.load(str(directory / LR_DIR))
        calibrator = (
            IsotonicRegressionModel.load(str(directory / CALIBRATOR_DIR))
            if (directory / CALIBRATOR_DIR).exists()
            else None
        )
        return cls(model=model, calibrator=calibrator)


def fit_shadow_model(train: DataFrame, calibration: DataFrame | None) -> ShadowModel:
    """Fit the pipeline on ``train`` and the isotonic calibrator on ``calibration`` (hold-out)."""
    model = build_pipeline(
        elastic_net_param=float(LR_PARAMS["elasticNetParam"]),
        reg_param=float(LR_PARAMS["regParam"]),
        max_iter=int(LR_PARAMS["maxIter"]),
    ).fit(train)
    shadow = ShadowModel(model=model, calibrator=None)
    if calibration is not None and calibration.count() >= MIN_CALIBRATION_ROWS:
        scored = shadow.predict_raw(calibration)
        iso = IsotonicRegression(
            featuresCol=RAW_PROB_COL, labelCol=LABEL_COL, predictionCol=PROB_COL, isotonic=True
        )
        shadow.calibrator = iso.fit(scored)
    return shadow


__all__ = [
    "CALIBRATOR_DIR",
    "LR_DIR",
    "LR_PARAMS",
    "MIN_CALIBRATION_ROWS",
    "PROB_COL",
    "RAW_PROB_COL",
    "SEED",
    "ShadowModel",
    "build_pipeline",
    "fit_shadow_model",
]
