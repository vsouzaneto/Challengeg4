"""CLI: chance (%) of a planned post landing in the top 5% of its media type — views, likes and comments.

Shows the same post as video / image / text / mixed so formats can be compared before posting.
Usage (from submissions/rafael):
  .venv/bin/python solution/cli/predict_hit.py --platform TikTok --content_category beauty --language Spanish --hour 19
  .venv/bin/python solution/cli/predict_hit.py --content_type video --platform YouTube --content_category tech
  .venv/bin/python solution/cli/predict_hit.py --retrain
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from social_insights import data, hit_probability as hp  # noqa: E402
from social_insights.views_forecast import add_creator_history  # noqa: E402

MODEL_PATH = Path(__file__).parent / "models" / "hit_predictor.joblib"


def load_or_train(df: pd.DataFrame, retrain: bool) -> hp.HitPredictor:
    import joblib
    if MODEL_PATH.exists() and not retrain:
        return joblib.load(MODEL_PATH)
    predictor = hp.HitPredictor.train(df)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(predictor, MODEL_PATH)
    return predictor


def planned_posts(df: pd.DataFrame, args: dict) -> pd.DataFrame:
    """Typical post (mode/median) overridden by the CLI arguments; one row per media type unless --content_type is given."""
    history = add_creator_history(df)
    typical = {c: history[c].astype(str).mode()[0] for c in hp.CATEGORICAL} | {c: float(history[c].median()) for c in hp.NUMERIC}
    post = typical | {k: v for k, v in args.items() if v is not None and k != "content_type"}
    if post.get("hour") is not None:
        post["daypart"] = pd.cut([post["hour"]], [-1, 5, 11, 17, 24], labels=["madrugada", "manhã", "tarde", "noite"])[0]
    types = [args["content_type"]] if args.get("content_type") else sorted(df["content_type"].unique())
    return pd.DataFrame([post | {"content_type": t} for t in types])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--retrain", action="store_true")
    parser.add_argument("--content_type", help="video / image / text / mixed (omitido = compara todos)")
    for col in hp.CATEGORICAL:
        parser.add_argument(f"--{col}")
    for col in ["content_length", "caption_words", "n_hashtags", "follower_count", "hour"]:
        parser.add_argument(f"--{col}", type=float)
    args = vars(parser.parse_args())
    df = data.load_posts()
    predictor = load_or_train(df, args.pop("retrain"))
    result = predictor.predict(planned_posts(df, args))
    table = result.pivot_table(index="formato", columns="métrica", values="chance top 5% (%)").round(1)
    signal = result.pivot_table(index="formato", columns="métrica", values="sinal do segmento (%)").round(1)
    print("Chance de cair no top 5% do formato (%):\n", table.to_string(), "\n")
    interval = result.pivot_table(index="formato", columns="métrica", values="segmento IC90 (%)", aggfunc="first")
    print("Sinal histórico do segmento (plataforma × categoria × idioma) (%):\n", signal.to_string(), "\n")
    print("Intervalo de 90% do sinal do segmento (%):\n", interval.to_string(), "\n")
    print("Modelos usados:", ", ".join(sorted(set(result["modelo"]))))
    if set(result["modelo"]) == {"taxa base"}:
        print("Aviso: nenhum modelo superou a taxa base após correção. A chance oficial é a taxa histórica (5%); "
              "o sinal do segmento é uma pista, com intervalo largo.")


if __name__ == "__main__":
    main()
