from app import _friendly_factor


def test_friendly_factor_explains_engaging_priority():
    label, reason, contribution = _friendly_factor(
        {"name": "deal_stage", "contribution": 60, "reason": "internal reason"},
        "Engaging",
    )

    assert label == "Estágio comercial"
    assert "Engaging" in reason
    assert contribution == 60


def test_friendly_factor_explains_prospecting_priority():
    label, reason, contribution = _friendly_factor(
        {"name": "deal_stage", "contribution": 30, "reason": "internal reason"},
        "Prospecting",
    )

    assert label == "Estágio comercial"
    assert "Prospecting" in reason
    assert contribution == 30
