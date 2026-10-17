from pathlib import Path
import pandas as pd

from src.dataset_explorer import DatasetExplorer


def test_dataset1_customers_and_no_relational_join(tmp_path: Path):
    raw = tmp_path / "raw"
    raw.mkdir()
    pd.DataFrame({
        "Ticket ID": [1, 2, 3, 4],
        "Customer Name": ["A", "A", "B", "C"],
        "Customer Email": ["a@example.com", "a@example.com", "b@example.com", "c@example.com"],
        "Ticket Description": ["x", "y", "z", "w"],
        "Ticket Subject": ["s1", "s2", "s3", "s4"],
        "Ticket Type": ["Technical issue"] * 4,
        "Ticket Priority": ["High"] * 4,
        "Ticket Channel": ["Email"] * 4,
        "Ticket Status": ["Open", "Closed", "Open", "Closed"],
    }).to_csv(raw / "d1.csv", index=False)
    pd.DataFrame({
        "Document": ["hardware issue", "access issue"],
        "Topic_group": ["Hardware", "Access"],
    }).to_csv(raw / "d2.csv", index=False)

    result = DatasetExplorer(raw).summary()
    assert result["datasets"]["dataset1"]["rows"] == 4
    assert result["customer_summary"]["unique_customer_emails"] == 3
    assert result["customer_summary"]["multi_ticket_customers"] == 1
    assert result["customer_summary"]["max_tickets_per_customer"] == 2
    assert "cross_dataset" not in result
    assert result["dataset_roles"]["dataset2"]["relationship"] == "independent_training_corpus"
    assert result["dataset_roles"]["dataset2"]["has_ticket_status"] is False
