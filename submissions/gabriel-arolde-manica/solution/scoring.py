import pandas as pd


def calculate_product_win_rates(pipeline):
    """
    Historical win rate by product using closed opportunities.
    """

    closed = pipeline[
        pipeline["deal_stage"].isin(["Won", "Lost"])
    ].copy()

    if closed.empty:
        return {}

    closed["won"] = (
        closed["deal_stage"] == "Won"
    ).astype(int)

    return (
        closed
        .groupby("product")["won"]
        .mean()
        .to_dict()
    )


def calculate_score(
    deal,
    product_win_rates,
    reference_date
):
    """
    Calculate a 0-100 commercial priority score.

    This is a prioritization score, NOT a probability
    of winning the opportunity.
    """

    score = 0
    reasons = []
    risk_flags = []

    # ==========================================
    # 1. SALES STAGE — MAX 35
    # ==========================================

    stage = deal.get("deal_stage")

    if stage == "Engaging":
        score += 35
        reasons.append("+35: oportunidade em Engaging")

    elif stage == "Prospecting":
        score += 15
        reasons.append("+15: oportunidade em Prospecting")

    # ==========================================
    # 2. PIPELINE AGE — MAX 25
    # ==========================================

    engage_date = pd.to_datetime(
        deal.get("engage_date"),
        errors="coerce"
    )

    if stage == "Engaging" and pd.notna(engage_date):

        days = (
            pd.Timestamp(reference_date) - engage_date
        ).days

        if days <= 30:
            age_score = 5
            reasons.append(
                f"+5: Engaging há {days} dias"
            )

        elif days <= 90:
            age_score = 10
            reasons.append(
                f"+10: Engaging há {days} dias"
            )

        elif days <= 180:
            age_score = 17
            reasons.append(
                f"+17: Engaging há {days} dias"
            )

            risk_flags.append(
                "Pipeline envelhecido"
            )

        elif days <= 270:
            age_score = 21
            reasons.append(
                f"+21: Engaging há {days} dias"
            )

            risk_flags.append(
                "Pipeline muito envelhecido"
            )

        else:
            age_score = 25
            reasons.append(
                f"+25: Engaging há {days} dias"
            )

            risk_flags.append(
                "Possível estagnação no pipeline"
            )

        score += age_score

    elif stage == "Prospecting":

        risk_flags.append(
            "Ainda não entrou em Engaging"
        )

    # ==========================================
    # 3. PRODUCT SIGNAL — MAX 15
    # ==========================================

    product = deal.get("product")

    product_rate = product_win_rates.get(product)

    if product_rate is not None:

        if product_rate >= 0.64:
            product_score = 15

        elif product_rate >= 0.62:
            product_score = 10

        else:
            product_score = 5

        score += product_score

        reasons.append(
            f"+{product_score}: win rate histórico "
            f"do produto {product_rate:.1%}"
        )

    # ==========================================
    # 4. ACCOUNT SIZE — MAX 15
    # ==========================================

    revenue = deal.get("revenue")

    if pd.notna(revenue):

        if revenue >= 3000:
            score += 15
            reasons.append(
                "+15: conta de grande porte"
            )

        elif revenue >= 1000:
            score += 10
            reasons.append(
                "+10: conta de porte médio"
            )

        else:
            score += 5
            reasons.append(
                "+5: conta de menor porte"
            )

    else:

        risk_flags.append(
            "Dados de receita da conta ausentes"
        )

    # ==========================================
    # 5. DATA QUALITY — MAX 10
    # ==========================================

    account = deal.get("account")

    if pd.notna(account):

        score += 10
        reasons.append(
            "+10: conta identificada"
        )

    else:

        risk_flags.append(
            "Conta não identificada"
        )

    # ==========================================
    # FINAL SCORE
    # ==========================================

    return {
        "score": min(score, 100),
        "reasons": reasons,
        "risk_flags": risk_flags
    }
