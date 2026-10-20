"""CLI: forecast the views of a planned post using only what is known before posting.

Usage (from submissions/rafael):
  .venv/bin/python solution/cli/predict_views.py --creator_id creator_586 --platform TikTok --content_type video --content_category tech --content_length 45 --is_sponsored False
  .venv/bin/python solution/cli/predict_views.py --retrain
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from social_insights import data, views_forecast as vf  # noqa: E402

MODEL_PATH = Path(__file__).parent / "models" / "views_forecaster.joblib"
CATEGORICAL = sorted({c for cats, _ in vf.BLOCKS.values() for c in cats})
NUMERIC = sorted({n for _, nums in vf.BLOCKS.values() for n in nums} - set(vf.CREATOR_HISTORY))


def load_or_train(df: pd.DataFrame, retrain: bool) -> vf.ViewsForecaster:
    if MODEL_PATH.exists() and not retrain:
        return vf.ViewsForecaster.load(MODEL_PATH)
    forecaster = vf.ViewsForecaster.train(df, vf.evaluate(df))
    forecaster.save(MODEL_PATH)
    return forecaster


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--retrain", action="store_true")
    parser.add_argument("--creator_id", help="usa o histórico deste creator (posts anteriores)")
    for col in CATEGORICAL:
        parser.add_argument(f"--{col}")
    for col in NUMERIC:
        parser.add_argument(f"--{col}", type=float)
    args = vars(parser.parse_args())

    df = data.load_posts()
    forecaster = load_or_train(df, args.pop("retrain"))
    creator = args.pop("creator_id")
    typical = {c: df[c].astype(str).mode()[0] for c in CATEGORICAL} | {c: float(df[c].median()) for c in NUMERIC}
    post = typical | (vf.creator_snapshot(df, creator) if creator else {}) | {k: v for k, v in args.items() if v is not None}
    result = forecaster.predict(pd.DataFrame([post])).iloc[0]

    print(f"Modelo: {forecaster.model_name} (supera a média histórica: {'sim' if forecaster.beats_baseline else 'não'})")
    print(f"Views previstas: {result['views previstas']:,.0f}  (intervalo 90%: {result['intervalo 90% inf']:,.0f} – {result['intervalo 90% sup']:,.0f})")
    if not forecaster.beats_baseline:
        print("Aviso: nada do que se sabe antes de postar melhora a previsão nestes dados. A estimativa é a média histórica, igual para qualquer post.")


if __name__ == "__main__":
    main()
