from collections.abc import Iterator
from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.repository import repository
from api.settings import settings
from tests.fixtures import write_model_dir, write_partition

LATEST = date(2017, 12, 31)
BACKTEST = date(2017, 9, 30)


@pytest.fixture(scope="session")
def artifacts(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Two partitions (struct reasons / JSON reasons) and a model dir in a temp solution/."""
    root = tmp_path_factory.mktemp("solution")
    scores = root / "data" / "gold" / "scores"
    write_partition(scores, LATEST)
    write_partition(
        scores,
        BACKTEST,
        reasons_as_json=True,
        drop_as_of_column=True,
        drop_columns=("sales_price",),  # partition written before schema 1.1.0
        model_version="test-old",
    )
    write_model_dir(root / "models")
    (root / "data" / "feedback").mkdir(parents=True)
    return root


@pytest.fixture(autouse=True)
def _point_settings(artifacts: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setattr(settings, "scores_dir", artifacts / "data" / "gold" / "scores")
    monkeypatch.setattr(settings, "models_dir", artifacts / "models")
    monkeypatch.setattr(settings, "feedback_dir", artifacts / "data" / "feedback")
    repository.reset()
    yield
    repository.reset()


@pytest.fixture
def client() -> Iterator[TestClient]:
    from api.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def empty_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """Client whose settings point to directories without any artifact."""
    monkeypatch.setattr(settings, "scores_dir", tmp_path / "scores")
    monkeypatch.setattr(settings, "models_dir", tmp_path / "models")
    monkeypatch.setattr(settings, "feedback_dir", tmp_path / "feedback")
    repository.reset()
    from api.main import app

    with TestClient(app) as c:
        yield c
