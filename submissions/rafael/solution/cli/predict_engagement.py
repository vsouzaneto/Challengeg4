"""CLI: estimate the engagement of a planned post (trains and caches the predictor on first use).

Usage (from submissions/rafael):
  .venv/bin/python solution/cli/predict_engagement.py --platform TikTok --content_type video --content_category tech --follower_count 25000
  .venv/bin/python solution/cli/predict_engagement.py --retrain
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from social_insights import data, engagement_model as em  # noqa: E402

MODEL_PATH = Path(__file__).parent / "models" / "engagement_predictor.joblib"


def typical_post(df: pd.DataFrame) -> dict:
    """Defaults for unspecified fields: mode (categorical) or median (numeric)."""
    return {c: df[c].astype(str).mode()[0] for c in em.CATEGORICAL} | {c: float(df[c].median()) for c in em.NUMERIC}


def load_or_train(df: pd.DataFrame, retrain: bool) -> em.EngagementPredictor:
    if MODEL_PATH.exists() and not retrain:
        return em.EngagementPredictor.load(MODEL_PATH)
    summary, _ = em.compare_models(df)
    predictor = em.EngagementPredictor.train(df, summary)
    predictor.save(MODEL_PATH)
    return predictor


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--retrain", action="store_true", help="re-run the model comparison and retrain")
    for col in em.FEATURES:
        parser.add_argument(f"--{col}", type=float if col in em.NUMERIC else str)
    args = vars(parser.parse_args())

    df = data.load_posts()
    predictor = load_or_train(df, args.pop("retrain"))
    post = typical_post(df) | {k: v for k, v in args.items() if v is not None}
    result = predictor.predict(pd.DataFrame([post])).iloc[0]

    print(f"Modelo: {predictor.model_name} (R² validação {predictor.cv_r2:.4f}; supera baseline: {'sim' if predictor.beats_baseline else 'não'})")
    print(f"Engajamento estimado: {result['engajamento estimado']:.2%}  (intervalo 90%: {result['intervalo 90% inf']:.2%} – {result['intervalo 90% sup']:.2%})")
    if not predictor.beats_baseline:
        print("Aviso: nenhum modelo supera a média nestes dados. A estimativa é a média histórica, igual para qualquer post.")


if __name__ == "__main__":
    main()
