"""CLI for the batch jobs: ``python -m lead_scorer.jobs <job> --as-of YYYY-MM-DD``.

``build-features`` (bronze -> silver -> gold), ``train`` (backtest + shadow model + model card
into ``models/<version>``) and ``score`` (``gold/scores/as_of=<date>``). Missing prerequisites
(gold partition, model pointer) exit with code 2 and a hint; a failed acceptance threshold in
``train`` exits with code 3.
"""

from __future__ import annotations

from datetime import date

import typer

from lead_scorer.config import SNAPSHOT_DATE

app = typer.Typer(
    name="lead_scorer.jobs",
    help="Lead Scorer batch jobs (PySpark). Use --as-of to pick the snapshot/backtest cut.",
    no_args_is_help=True,
    add_completion=False,
)

MISSING_ARTIFACT_EXIT_CODE = 2
ACCEPTANCE_EXIT_CODE = 3

AsOfOption = typer.Option(
    SNAPSHOT_DATE.isoformat(),
    "--as-of",
    help="Reference date (YYYY-MM-DD). Defaults to the data snapshot.",
    show_default=True,
)


def _parse_as_of(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise typer.BadParameter("expected YYYY-MM-DD") from exc


def _fail(job: str, exc: Exception, code: int) -> None:
    typer.echo(f"[{job}] {exc}", err=True)
    raise typer.Exit(code=code)


@app.command("build-features")
def build_features(as_of: str = AsOfOption) -> None:
    """Raw -> bronze -> silver -> gold/opportunity_features, history_stats, labels at --as-of."""
    from lead_scorer.jobs.build_features import run

    summary = run(_parse_as_of(as_of))
    for line in summary.lines():
        typer.echo(line)


@app.command("train")
def train(
    as_of: str = AsOfOption,
    no_strict: bool = typer.Option(
        False, "--no-strict", help="Write artifacts even if a section-7 acceptance check fails."
    ),
) -> None:
    """Backtest the rules + shadow LR on the cuts before --as-of; save models/<version>/ + card."""
    from lead_scorer.jobs.artifacts import MissingArtifactError
    from lead_scorer.jobs.train import run
    from lead_scorer.ml.evaluate import AcceptanceError

    try:
        summary = run(_parse_as_of(as_of), strict=not no_strict)
    except MissingArtifactError as exc:
        _fail("train", exc, MISSING_ARTIFACT_EXIT_CODE)
    except AcceptanceError as exc:
        _fail("train", exc, ACCEPTANCE_EXIT_CODE)
    else:
        for line in summary.lines():
            typer.echo(line)


@app.command("score")
def score(
    as_of: str = AsOfOption,
    model: str = typer.Option(
        "latest", "--model", help="models/latest, a version name or a path to models/<version>."
    ),
) -> None:
    """Score open deals at --as-of with the given model and write gold/scores/as_of=<date>."""
    from lead_scorer.jobs.artifacts import MissingArtifactError
    from lead_scorer.jobs.score import ContractViolationError, run

    try:
        summary = run(_parse_as_of(as_of), model=model)
    except MissingArtifactError as exc:
        _fail("score", exc, MISSING_ARTIFACT_EXIT_CODE)
    except ContractViolationError as exc:
        _fail("score", exc, 1)
    else:
        for line in summary.lines():
            typer.echo(line)


def main() -> None:
    app()
