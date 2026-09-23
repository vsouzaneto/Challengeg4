import pandas as pd

from ravenstack_churn.modeling import (
    MODEL_FEATURES,
    apply_model_gate,
    evaluate_model,
    stable_account_split,
)


def test_accounts_never_cross_train_and_test(model_panel) -> None:
    split = stable_account_split(model_panel["account_id"])
    grouped = (
        pd.DataFrame({"account_id": model_panel.account_id, "split": split})
        .groupby("account_id")
        .split.nunique()
    )
    assert grouped.max() == 1


def test_failed_model_gate_returns_no_scores() -> None:
    evaluation, scores = apply_model_gate(
        average_precision_gain=0.01,
        lift_at_20pct=1.10,
        brier_score=0.20,
        baseline_brier_score=0.22,
    )
    assert evaluation["publish_model"] is False
    assert scores is None


def test_model_features_exclude_post_churn_sources() -> None:
    forbidden = {"churn_flag", "churn_date", "reason_code", "feedback_text", "refund_amount_usd"}
    assert forbidden.isdisjoint(MODEL_FEATURES)


def test_evaluate_model_respects_publication_gate(model_panel) -> None:
    model_panel.loc[0, "days_to_annual_renewal"] = pd.NA
    evaluation, scores = evaluate_model(model_panel)
    assert isinstance(evaluation["publish_model"], bool)
    if not evaluation["publish_model"]:
        assert scores is None
