from pathlib import Path

import pandas as pd

from src.cross_analysis import CrossAnalysis


def _write_dataset(
    raw_dir: Path,
) -> None:
    rows = [
        {
            "Ticket ID": 1,
            "Ticket Status": "Open",
            "First Response Time": None,
            "Time to Resolution": None,
            "Customer Satisfaction Rating": None,
            "Ticket Channel": "Chat",
            "Ticket Priority": "High",
            "Ticket Type": "Refund request",
            "Product Purchased": "Product A",
            "Ticket Subject": "Issue X",
        },
        {
            "Ticket ID": 2,
            "Ticket Status": "Pending Customer Response",
            "First Response Time": "2026-01-01 10:00:00",
            "Time to Resolution": None,
            "Customer Satisfaction Rating": None,
            "Ticket Channel": "Chat",
            "Ticket Priority": "High",
            "Ticket Type": "Refund request",
            "Product Purchased": "Product A",
            "Ticket Subject": "Issue Y",
        },
        {
            "Ticket ID": 3,
            "Ticket Status": "Pending Customer Response",
            "First Response Time": "2026-01-01 11:00:00",
            "Time to Resolution": None,
            "Customer Satisfaction Rating": None,
            "Ticket Channel": "Phone",
            "Ticket Priority": "Low",
            "Ticket Type": "Technical issue",
            "Product Purchased": "Product B",
            "Ticket Subject": "Issue X",
        },
        {
            "Ticket ID": 4,
            "Ticket Status": "Closed",
            "First Response Time": "2026-01-02 10:00:00",
            "Time to Resolution": "2026-01-02 14:00:00",
            "Customer Satisfaction Rating": 2,
            "Ticket Channel": "Email",
            "Ticket Priority": "Medium",
            "Ticket Type": "Refund request",
            "Product Purchased": "Product A",
            "Ticket Subject": "Issue X",
        },
        {
            "Ticket ID": 5,
            "Ticket Status": "Closed",
            "First Response Time": "2026-01-02 11:00:00",
            "Time to Resolution": "2026-01-02 13:00:00",
            "Customer Satisfaction Rating": 5,
            "Ticket Channel": "Email",
            "Ticket Priority": "Medium",
            "Ticket Type": "Technical issue",
            "Product Purchased": "Product B",
            "Ticket Subject": "Issue X",
        },
        {
            "Ticket ID": 6,
            "Ticket Status": "Closed",
            "First Response Time": "2026-01-02 15:00:00",
            "Time to Resolution": "2026-01-02 14:00:00",
            "Customer Satisfaction Rating": 1,
            "Ticket Channel": "Phone",
            "Ticket Priority": "High",
            "Ticket Type": "Cancellation request",
            "Product Purchased": "Product A",
            "Ticket Subject": "Issue Y",
        },
    ]

    pd.DataFrame(
        rows
    ).to_csv(
        raw_dir
        / "customer_support_tickets.csv",
        index=False,
    )


def test_open_pending_pairwise_ticket_count(
    tmp_path,
):
    _write_dataset(
        tmp_path
    )

    result = CrossAnalysis(
        tmp_path
    ).analyze(
        scope="open_pending",
        dimension_a="channel",
        dimension_b="ticket_type",
        metric="ticket_count",
    )

    assert result["status"] == "ready"
    assert result["scope"]["tickets"] == 3
    assert (
        result["summary"]["observed_combinations"]
        == 2
    )

    top = (
        result["summary"]["top_volume"]
    )

    assert top["dimension_a_value"] == "Chat"
    assert (
        top["dimension_b_value"]
        == "Refund request"
    )
    assert top["tickets"] == 2


def test_open_pending_commercial_loss(
    tmp_path,
):
    _write_dataset(
        tmp_path
    )

    result = CrossAnalysis(
        tmp_path
    ).analyze(
        scope="open_pending",
        dimension_a="channel",
        dimension_b="priority",
        metric="commercial_loss",
    )

    assert result["status"] == "ready"
    assert (
        result["metric"]["total_value"]
        == 2
    )


def test_closed_csat_metrics(
    tmp_path,
):
    _write_dataset(
        tmp_path
    )

    result = CrossAnalysis(
        tmp_path
    ).analyze(
        scope="closed",
        dimension_a="product",
        dimension_b="subject",
        metric="rating_1_3",
    )

    assert result["status"] == "ready"
    assert result["scope"]["tickets"] == 3
    assert (
        result["metric"]["total_value"]
        == 2
    )


def test_solution_time_excludes_negative_intervals(
    tmp_path,
):
    _write_dataset(
        tmp_path
    )

    result = CrossAnalysis(
        tmp_path
    ).analyze(
        scope="closed",
        dimension_a="channel",
        dimension_b="ticket_type",
        metric="solution_time",
    )

    assert result["status"] == "ready"

    assert (
        result["metric"]["valid_count"]
        == 2
    )

    assert (
        result["metric"]["total_value"]
        == 3.0
    )


def test_same_dimension_is_rejected(
    tmp_path,
):
    _write_dataset(
        tmp_path
    )

    result = CrossAnalysis(
        tmp_path
    ).analyze(
        scope="open_pending",
        dimension_a="channel",
        dimension_b="channel",
        metric="ticket_count",
    )

    assert result["status"] == "error"
    assert result["code"] == "same_dimension"
