from pathlib import Path

import pandas as pd

from src.dataset2_diagnostics import Dataset2Diagnostics


def test_dataset2_groups_and_operational_boundary(tmp_path: Path):
    raw = tmp_path / "raw"
    raw.mkdir()
    pd.DataFrame(
        {
            "Document": [
                "reset password reset password please",
                "laptop screen issue",
                "new starter account access",
                "storage quota full",
            ],
            "Topic_group": ["Access", "Hardware", "Access", "Storage"],
        }
    ).to_csv(raw / "dataset2.csv", index=False)

    result = Dataset2Diagnostics(raw).run()

    assert result["status"] == "ready"
    assert result["rows"] == 4
    assert result["topic_groups"]["count"] == 3
    assert result["topic_groups"]["rows"][0]["label"] == "Access"
    assert result["topic_groups"]["rows"][0]["count"] == 2
    assert result["status_availability"]["available"] is False
    assert "cross_dataset_gate" not in result


def test_document_quality_detects_internal_repetition_without_mutating_source(tmp_path: Path):
    raw = tmp_path / "raw"
    raw.mkdir()
    path = raw / "dataset2.csv"
    original = pd.DataFrame(
        {
            "Document": ["reset password reset password", "simple hardware issue"],
            "Topic_group": ["Access", "Hardware"],
        }
    )
    original.to_csv(path, index=False)

    result = Dataset2Diagnostics(raw).run()
    quality = result["document_quality"]

    assert quality["exact_duplicate_documents"] == 0
    assert quality["documents_with_repeated_bigrams"] >= 1
    assert quality["source_mutation_allowed"] is False
    pd.testing.assert_frame_equal(pd.read_csv(path), original)
