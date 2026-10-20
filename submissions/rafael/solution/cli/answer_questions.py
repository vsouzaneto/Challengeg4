"""CLI: answers the four Challenge 004 questions + the four strategy decisions + the test queue + the proofs behind the
executive summary, and writes a Markdown report (optionally also the summary's chart).

Usage (from submissions/rafael): .venv/bin/python solution/cli/answer_questions.py [--out docs/respostas.md] [--figures docs/figures]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from social_insights import data, exploration, plots, questions, strategy  # noqa: E402

TIER_CHART = "views_por_faixa_de_creator.png"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="Markdown file to write (prints to stdout if omitted)")
    parser.add_argument("--figures", type=Path, help="folder for the executive summary's chart (median views per creator tier)")
    args = parser.parse_args()

    df = data.load_posts()
    queue = strategy.test_queue(df)
    sections = [*questions.answer_all(df), *strategy.recommend_all(df), queue, strategy.deliverable_evidence(df, queue)]
    report = "# Respostas e estratégia — Challenge 004\n\n" + "\n\n---\n\n".join(s.to_markdown() for s in sections)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
        print(f"Relatório salvo em {args.out}")
    else:
        print(report)
    if args.figures:
        args.figures.mkdir(parents=True, exist_ok=True)
        plots.tier_views_chart(exploration.engagement_rate_by_tier(df)).savefig(args.figures / TIER_CHART, dpi=150)
        print(f"Gráfico salvo em {args.figures / TIER_CHART}")


if __name__ == "__main__":
    main()
