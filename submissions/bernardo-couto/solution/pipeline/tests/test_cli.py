from pathlib import Path

from typer.testing import CliRunner

from lead_scorer.jobs.cli import MISSING_ARTIFACT_EXIT_CODE, app

runner = CliRunner()


def test_jobs_are_listed() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for job in ("build-features", "train", "score"):
        assert job in result.output


def test_score_without_model_exits_with_code_2(tmp_path: Path) -> None:
    result = runner.invoke(app, ["score", "--as-of", "2017-12-31", "--model", str(tmp_path / "x")])
    assert result.exit_code == MISSING_ARTIFACT_EXIT_CODE
    assert "training_manifest.json" in (result.output + (result.stderr or ""))


def test_rejects_bad_date() -> None:
    result = runner.invoke(app, ["train", "--as-of", "31/12/2017"])
    assert result.exit_code != 0
