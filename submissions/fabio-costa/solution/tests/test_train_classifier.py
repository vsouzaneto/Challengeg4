from hashlib import sha256

import numpy as np
import pytest

from src import train_classifier as training


def test_source_contract_and_group_isolation():
    before = sha256(training.SOURCE.read_bytes()).hexdigest()
    texts, labels, splits, group_count = training.prepare()
    assert len(texts) == len(labels) == 47837
    assert group_count > 0
    train, validation, test = splits
    indices = [set(x.tolist()) for x in splits]
    assert not (indices[0] & indices[1])
    assert not (indices[0] & indices[2])
    assert not (indices[1] & indices[2])
    assert sum(map(len, splits)) == len(texts)
    groups = np.array([" ".join(x.lower().split()[:6]) for x in texts])
    group_sets = [set(groups[x]) for x in splits]
    assert not (group_sets[0] & group_sets[1])
    assert not (group_sets[0] & group_sets[2])
    assert not (group_sets[1] & group_sets[2])
    assert all(set(labels[x]) == set(labels) for x in splits)
    assert sha256(training.SOURCE.read_bytes()).hexdigest() == before


def test_source_sha_mismatch_blocks(monkeypatch, tmp_path):
    source = tmp_path / "corrupt.csv"
    source.write_text("Document,Topic_group\\nhello,Access\\n")
    monkeypatch.setattr(training, "SOURCE", source)
    with pytest.raises(RuntimeError, match="DATASET_SHA_MISMATCH"):
        training.prepare()


@pytest.mark.parametrize("kind", ["LinearSVC", "LogisticRegression"])
def test_model_pipeline_fit_and_predict(kind):
    corpus = ["hardware laptop issue", "hardware laptop broken",
              "password access issue", "password access request"] * 3
    labels = ["Hardware", "Hardware", "Access", "Access"] * 3
    estimator = training.model(kind)
    estimator.fit(corpus, labels)
    predictions = estimator.predict(["hardware laptop issue", "password access request"])
    assert len(predictions) == 2
    assert set(predictions).issubset({"Hardware", "Access"})
