from pathlib import Path

from fastapi.testclient import TestClient

from api.routers.meta import list_as_of_partitions, read_model_version


def test_meta_without_artifacts(empty_client: TestClient) -> None:
    body = empty_client.get("/api/v1/meta").json()
    assert body["artifacts_present"] is False
    assert body["as_of_available"] == []
    assert body["default_as_of"] is None
    assert body["model_version"] is None
    assert body["open_deals"] is None
    assert body["schema_version"] == "1.1.0"
    assert body["snapshot_date"] == "2017-12-31"


def test_meta_with_partitions(client: TestClient) -> None:
    body = client.get("/api/v1/meta").json()
    assert body["as_of_available"] == ["2017-09-30", "2017-12-31"]
    assert body["default_as_of"] == "2017-12-31"
    assert body["model_version"] == "test-model-v1"
    assert body["artifacts_present"] is True
    assert body["open_deals"] == 24


def test_partition_listing_ignores_garbage(tmp_path: Path) -> None:
    scores = tmp_path / "scores"
    for d in ("2017-09-30", "2017-12-31"):
        (scores / f"as_of={d}").mkdir(parents=True)
        (scores / f"as_of={d}" / "part-0.parquet").write_bytes(b"")
    (scores / "as_of=2017-06-30").mkdir()  # empty partition: ignored
    (scores / "as_of=not-a-date").mkdir()
    (scores / "as_of=not-a-date" / "x.parquet").write_bytes(b"")
    (scores / "garbage").mkdir()
    assert [d.isoformat() for d in list_as_of_partitions(scores)] == ["2017-09-30", "2017-12-31"]


def test_model_pointer_variants(tmp_path: Path) -> None:
    models = tmp_path / "models"
    (models / "v1").mkdir(parents=True)
    (models / "v1" / "metrics.json").write_text('{"model_version": "v1"}')
    assert read_model_version(tmp_path / "latest") is None
    (models / "latest").write_text("v1\n")
    assert read_model_version(models / "latest") == "v1"
    (models / "latest").unlink()
    (models / "latest").symlink_to(models / "v1", target_is_directory=True)
    assert read_model_version(models / "latest") == "v1"


def test_helpers_on_missing_paths(tmp_path: Path) -> None:
    assert list_as_of_partitions(tmp_path / "nope") == []
    assert read_model_version(tmp_path / "latest") is None
