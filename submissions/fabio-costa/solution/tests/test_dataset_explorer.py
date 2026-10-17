from pathlib import Path

import pandas as pd

from src.dataset_explorer import DatasetExplorer


def build_data(raw: Path) -> None:
    pd.DataFrame(
        [
            {
                "Ticket ID": 1,
                "Ticket Description": "Device does not turn on",
                "Ticket Subject": "Hardware setup",
                "Ticket Type": "Technical issue",
                "Ticket Priority": "High",
                "Ticket Channel": "Email",
                "Ticket Status": "Open",
            },
            {
                "Ticket ID": 2,
                "Ticket Description": "Need refund",
                "Ticket Subject": "Refund",
                "Ticket Type": "Refund request",
                "Ticket Priority": "Low",
                "Ticket Channel": "Chat",
                "Ticket Status": "Closed",
            },
        ]
    ).to_csv(raw / "customer_support_tickets.csv", index=False)

    pd.DataFrame(
        [
            {"Document": "laptop display failure", "Topic_group": "Hardware"},
            {"Document": "password reset needed", "Topic_group": "Access"},
        ]
    ).to_csv(raw / "all_tickets_processed_improved_v3.csv", index=False)


def test_summary_keeps_datasets_separate(tmp_path: Path):
    build_data(tmp_path)
    data = DatasetExplorer(tmp_path).summary()
    assert data["status"] == "ready"
    assert data["datasets"]["dataset1"]["rows"] == 2
    assert data["datasets"]["dataset2"]["rows"] == 2
    assert data["dataset_roles"]["dataset1"]["relationship"] == "operational"
    assert data["dataset_roles"]["dataset2"]["relationship"] == "independent_training_corpus"
    assert "cross_dataset" not in data


def test_rows_are_original_and_filterable(tmp_path: Path):
    build_data(tmp_path)
    result = DatasetExplorer(tmp_path).rows(
        "dataset1", page=1, page_size=25, filter_field="Ticket Type", filter_value="Refund request"
    )
    assert result["status"] == "ready"
    assert result["pagination"]["total_rows"] == 1
    assert result["rows"][0]["Ticket ID"] == 2
    assert result["rows"][0]["Ticket Description"] == "Need refund"
