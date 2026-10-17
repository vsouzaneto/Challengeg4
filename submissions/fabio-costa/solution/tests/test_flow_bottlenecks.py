from pathlib import Path

import pandas as pd

from src.diagnostics import OperationalDiagnostics


def test_flow_snapshot_and_combination_ranking(tmp_path: Path):
    rows = [
        {"Ticket ID": 1, "Ticket Type": "Technical issue", "Ticket Status": "Open", "Ticket Priority": "High", "Ticket Channel": "Email", "Customer Satisfaction Rating": None, "Resolution": None, "First Response Time": None, "Time to Resolution": None},
        {"Ticket ID": 2, "Ticket Type": "Technical issue", "Ticket Status": "Pending Customer Response", "Ticket Priority": "High", "Ticket Channel": "Email", "Customer Satisfaction Rating": None, "Resolution": None, "First Response Time": "2023-06-01 09:30:00", "Time to Resolution": None},
        {"Ticket ID": 3, "Ticket Type": "Technical issue", "Ticket Status": "Closed", "Ticket Priority": "High", "Ticket Channel": "Email", "Customer Satisfaction Rating": 4, "Resolution": "Reinstalled driver", "First Response Time": "2023-06-01 10:00:01", "Time to Resolution": "2023-06-01 12:00:01"},
        {"Ticket ID": 4, "Ticket Type": "Refund request", "Ticket Status": "Closed", "Ticket Priority": "Low", "Ticket Channel": "Chat", "Customer Satisfaction Rating": 3, "Resolution": None, "First Response Time": "2023-06-01 10:00:02", "Time to Resolution": "2023-06-01 09:00:02"},
    ]
    pd.DataFrame(rows).to_csv(tmp_path / "customer_support_tickets.csv", index=False)

    result = OperationalDiagnostics(tmp_path).run()
    assert result["status"] == "ready"
    flow = result["flow"]["snapshot"]
    assert flow["open"] == 1
    assert flow["pending_customer"] == 1
    assert flow["closed"] == 2
    assert flow["closed_with_resolution"] == 1
    assert flow["closed_without_resolution"] == 1
    assert flow["not_closed"] == 2
    assert flow["open_without_first_response"] == 1
    assert flow["pending_after_first_response"] == 1

    combos = result["bottleneck_combinations"]
    assert combos["resolution_time_status"] == "blocked"
    assert combos["rows"][0]["channel"] == "Email"
    assert combos["rows"][0]["priority"] == "High"
    assert combos["rows"][0]["ticket_type"] == "Technical issue"
    assert combos["rows"][0]["unresolved"] == 2
    assert combos["rows"][0]["unresolved_pct"] == 66.67

    resolution = combos["closed_resolution_time"]
    assert resolution["status"] == "derived"
    assert resolution["provenance"] == "DERIVED"
    assert resolution["valid_pairs"] == 2
    assert resolution["fast_resolution_assumption"] == 1
    assert resolution["ranked_tickets"] == 1
    assert resolution["overall_median_hours"] == 2.0

    worst = resolution["rows"][0]
    assert worst["channel"] == "Email"
    assert worst["priority"] == "High"
    assert worst["ticket_type"] == "Technical issue"
    assert worst["tickets"] == 1
    assert worst["median_hours"] == 2.0
