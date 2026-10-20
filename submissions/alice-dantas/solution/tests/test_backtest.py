import importlib.util

import numpy as np
import pandas as pd
import pytest

from leadscorer import codes, data, policy, triage
from leadscorer.errors import PolicyError

from conftest import PIPELINE, opp, skip_without_real_csvs, write_raw

spec =importlib.util.spec_from_file_location("backtest", policy.SOLUTION_DIR / "scripts" / "backtest.py")
backtest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backtest)

LEGIT = [(name, ranker) for name, ranker, leak in backtest.RANKERS + backtest.LIMITS if not leak]
TRAP = next(ranker for _, ranker, leak in backtest.RANKERS if leak)
CUT = "2017-06-01"  # 213 dias antes do AS_OF da fixture; T + 90 d = 213 − 90 = 123 dias antes


def load_cut(tmp_path, extra, as_of=CUT):
    raw = write_raw(tmp_path / "raw", sales_pipeline=PIPELINE + extra)
    return backtest.build_cut(data.load(raw).opportunities, backtest.close_values(raw), as_of)


@pytest.fixture
def cut(tmp_path):
    # Abertas em 2017-06-01: quatro que fecham depois do corte e uma que nunca fecha.
    crossing = [
        opp("B1", "Ana Alfa", "GTX Basic", "Won", engaged=250, closed=150),      # ganha na janela
        opp("B2", "Bruno Beta", "MG Special", "Lost", engaged=240, closed=180),
        opp("B3", "Ana Alfa", "GTXPro", "Won", engaged=230, closed=40),          # ganha depois da janela
        opp("B4", "Bruno Beta", "GTX Plus Pro", "Lost", engaged=220, closed=150),
        opp("Z1", "Ana Alfa", "GTX Plus Pro", "Engaging", engaged=260),          # nunca fecha
    ]
    built = load_cut(tmp_path, crossing)
    assert built.outcome["won"].nunique() == 2
    return built


def test_population_is_every_engaged_deal_still_open_at_the_cut(cut):
    # W1 fechou antes; E050 e as demais abertas engajaram depois; P1 (Prospecting) não tem data.
    assert list(cut.features["opportunity_id"]) == ["B1", "B2", "B3", "B4", "Z1"]
    assert list(cut.outcome["no_outcome"]) == [False, False, False, False, True]


def test_outcome_is_a_win_inside_the_horizon(cut):
    outcome = cut.outcome.set_index(cut.features["opportunity_id"])
    assert outcome.loc["B1", "won"] == 1 and outcome.loc["B1", "won_value"] == 100
    assert outcome.loc["B3", "won"] == 0 and outcome.loc["B3", "won_value"] == 0  # ganhou depois de 90 d
    assert outcome.loc["Z1", "won"] == 0


def test_horizon_must_end_inside_the_data(tmp_path):
    with pytest.raises(PolicyError, match="último fechamento"):
        load_cut(tmp_path, [], as_of="2017-10-15")


def test_legit_rankers_only_see_what_was_known(cut):  # ADR-001, validação 4
    assert not {"close_date", "close_value", "deal_stage", "won"} & set(cut.features.columns)
    assert set(cut.train.columns) == {"product", "won", "cycle_days"}


def test_outcome_changes_never_move_legit_rankers(cut):
    before = {name: ranker(cut) for name, ranker in LEGIT}
    flipped = cut.outcome.assign(won=1 - cut.outcome["won"],
                                 close_date=cut.outcome["close_date"] + pd.Timedelta(days=31),
                                 won_value=cut.outcome["won_value"] * 9,
                                 no_outcome=~cut.outcome["no_outcome"])
    changed = backtest.Cut(cut.as_of, cut.ctx, cut.train, cut.features, flipped)
    for name, ranker in LEGIT:
        assert np.array_equal(ranker(changed), before[name]), name
    assert not np.array_equal(TRAP(changed), TRAP(cut))  # só a armadilha depende do desfecho


def hand_cut(ages, prices, won_limit, limit):
    as_of = pd.Timestamp("2017-06-30")
    features = pd.DataFrame({
        "opportunity_id": [f"O{i}" for i in range(len(ages))], "sales_agent": "Ana Alfa",
        "product": "GTX Basic", "sales_price": prices,
        "engage_date": [as_of - pd.Timedelta(days=a) for a in ages]})
    ctx = triage.Context(as_of=as_of, won_cycle_limit_days=won_limit, cycle_limit_days=limit,
                         won_cycle_median_days=min(won_limit, 57))
    return backtest.Cut(as_of, ctx, pd.DataFrame(), features, pd.DataFrame())


def test_served_rule_splits_at_both_limits():
    cut = hand_cut(ages=[90, 91, 138, 139], prices=[550, 5482, 5482, 9999], won_limit=90, limit=138)
    assert list(backtest.served_rule(cut)) == [2e6 + 550, 1e6 + 5482, 1e6 + 5482, 9999]
    # A regra anterior põe tudo até 138 d no mesmo grupo e ordena só por preço.
    assert list(backtest.max_cycle_only(cut)) == [2e6 + 550, 2e6 + 5482, 2e6 + 5482, 9999]
    # Um limite fixo acima do maior ciclo é cortado nele.
    assert list(backtest.fixed_limit(200)(cut)) == list(backtest.max_cycle_only(cut))


def test_cut_ctx_is_the_core_context(tmp_path):
    raw = write_raw(tmp_path / "raw", sales_pipeline=PIPELINE)
    frame = data.load(raw).opportunities
    cut = backtest.build_cut(frame, backtest.close_values(raw), CUT)
    assert cut.ctx == triage.resolve_context(frame, CUT)  # só W1 (ganha, 10 d) fechou até o corte
    assert (cut.ctx.won_cycle_limit_days, cut.ctx.cycle_limit_days) == (10, 10)


def core_order_at_cut(frame, cut):
    """A lista que o núcleo serviria em T: as abertas em T viram Engaging e passam por
    triage.classify/order com o Context do corte."""
    at_t = frame[frame["opportunity_id"].isin(cut.features["opportunity_id"])].assign(
        deal_stage="Engaging", close_date=pd.NaT)
    ordered = triage.order(triage.classify(at_t, cut.ctx))
    return {seller: list(group["opportunity_id"]) for seller, group in ordered.groupby("sales_agent", sort=False)}


def backtest_order(cut):
    scores = pd.DataFrame({"seller": cut.features["sales_agent"], "id": cut.features["opportunity_id"],
                           "score": backtest.served_rule(cut)})
    return {seller: list(group.sort_values(["score", "id"], ascending=[False, True])["id"])
            for seller, group in scores.groupby("seller", sort=False)}


def test_served_ranker_reproduces_the_core_order_at_the_cut(tmp_path):
    rows = PIPELINE + [opp(f"G{age}", "Ana Alfa", product, "Won", engaged=age + 250, closed=250)
                       for age, product in ((5, "GTX Basic"), (20, "GTXPro"), (40, "MG Special"))] + [
        opp(f"O{age}", "Ana Alfa", product, "Engaging", engaged=213 + age)
        for age, product in ((3, "GTX Basic"), (15, "GTX Plus Pro"), (35, "GTXPro"), (60, "MG Special"))]
    raw = write_raw(tmp_path / "raw", sales_pipeline=rows)
    frame = data.load(raw).opportunities
    cut = backtest.build_cut(frame, backtest.close_values(raw), CUT)
    assert len(set(triage.engaging_group(backtest.age_days(cut), cut.ctx))) == 3  # os três grupos aparecem
    assert backtest_order(cut) == core_order_at_cut(frame, cut)


def test_auc_basics():
    y = np.array([0, 0, 1, 1])
    assert backtest.auc(y, np.array([1.0, 2, 3, 4])) == 1.0
    assert backtest.auc(y, np.array([4.0, 3, 2, 1])) == 0.0
    assert backtest.auc(y, np.ones(4)) == 0.5
    assert backtest.auc_ci(y, np.ones(4)) == (0.5, 0.5)


def test_top_k_counts_won_value_in_the_window_against_the_oracle(cut):
    # Ana Alfa: Z1 (5.482, nunca fecha), B3 (4.821, ganha depois de 90 d), B1 (550, ganha na janela).
    by_price = backtest.top_k(cut, backtest.table_value(cut), k=2).set_index("seller")
    assert by_price.loc["Ana Alfa", ["hits", "value", "oracle"]].tolist() == [0, 0, 100]
    assert by_price.loc["Ana Alfa", "expected_hits"] == pytest.approx(2 / 3)
    # Mais nova primeiro: B3 (17 d) e B1 (37 d) → a lista acha o único valor ganho.
    youngest = backtest.top_k(cut, backtest.youngest_first(cut), k=2).set_index("seller")
    assert youngest.loc["Ana Alfa", ["hits", "value", "oracle"]].tolist() == [1, 100, 100]
    assert list(backtest.top_k(cut, backtest.table_value(cut), k=3)["seller"]) == ["Ana Alfa"]  # Bruno tem 2


def test_list_metrics_sum_every_seller_cut():
    lists = pd.DataFrame({"seller": ["A", "B"], "hits": [3, 1], "expected_hits": [2.0, 2.0],
                          "value": [300.0, 0.0], "oracle": [400.0, 100.0]})
    assert backtest.list_metrics(lists, k=10) == {"p_at_k": 0.2, "lift_at_k": 1.0, "val_at_k": 0.6}


def test_delta_of_a_list_against_itself_is_zero():
    lists = pd.DataFrame({"seller": ["A", "B", "C"], "hits": [3, 1, 4], "expected_hits": [2.0, 2.0, 3.0],
                          "value": [300.0, 0.0, 50.0], "oracle": [400.0, 100.0, 80.0]})
    delta = backtest.delta_ci(lists, lists)
    assert all(value == 0 for value in delta.values())


@pytest.fixture(scope="module")
def real_result():
    skip_without_real_csvs()
    return backtest.run(policy.RAW_DIR)


@pytest.mark.real_data
def test_real_population_includes_deals_without_outcome(real_result):
    assert [c["n_test"] for c in real_result["cuts"]] == [1330, 1618, 1535, 1686, 2257, 2265, 2409]
    assert real_result["cuts"][-1]["share_no_outcome"] == 0.612
    assert all(c["cycle_limit_days"] == 138 for c in real_result["cuts"])
    assert [c["won_cycle_limit_days"] for c in real_result["cuts"]] == [114, 106, 105, 109, 107, 105, 107]
    assert real_result["design"]["served_rule"] == codes.SERVED_RANKER


@pytest.mark.real_data
def test_real_served_ranker_reproduces_the_core_order_at_every_cut(real_dataset):
    frame = real_dataset.opportunities
    values = backtest.close_values(policy.RAW_DIR)
    for as_of in backtest.CUTS:
        cut = backtest.build_cut(frame, values, as_of)
        assert cut.ctx == triage.resolve_context(frame, as_of)
        assert backtest_order(cut) == core_order_at_cut(frame, cut), as_of


@pytest.mark.real_data
def test_real_value_only_rankers_stay_at_chance(real_result):
    summary = {s["ranker"]: s for s in real_result["summary"]}
    for name in ("Taxa por produto", "Aleatório", "Só valor de tabela"):
        assert summary[name]["cuts_ci_above_half"] == 0, name
        assert 0.45 <= summary[name]["auc_mean"] <= 0.55, name
    trap = summary["[VAZAMENTO] fechou no 3º mês do trimestre"]
    assert trap["cuts_ci_above_half"] == len(backtest.CUTS)


@pytest.mark.real_data
def test_real_served_rule_leads_only_with_deals_without_outcome(real_result):
    summary = {s["ranker"]: s for s in real_result["summary"]}
    served, previous = summary[backtest.SERVED], summary[backtest.MAX_CYCLE]
    assert (served["auc_mean"], previous["auc_mean"]) == (0.604, 0.574)
    assert (served["val_at_k"], previous["val_at_k"], summary[backtest.LIST_PRICE]["val_at_k"]) == (0.584, 0.569, 0.538)
    assert (previous["d_val_at_k"], previous["d_val_low"], previous["d_val_high"]) == (-0.015, -0.027, -0.002)
    assert previous["d_p_high"] < 0
    # A limitação principal: sem as que nunca fecham, "só preço" fica à frente da regra servida.
    without = {s["ranker"]: s for s in real_result["without_no_outcome"]}
    assert without[backtest.SERVED]["val_at_k"] == 0.781
    price = without[backtest.LIST_PRICE]
    assert (price["val_at_k"], price["d_val_at_k"], price["d_val_low"], price["d_val_high"]) == (0.791, 0.01, 0.003, 0.019)


def test_delta_ci_is_antisymmetric():
    a = pd.DataFrame({"seller": ["A", "B", "C"], "hits": [3, 1, 4], "expected_hits": [2.0, 2.0, 3.0],
                      "value": [300.0, 0.0, 50.0], "oracle": [400.0, 100.0, 80.0]})
    b = a.assign(hits=[2, 2, 1], value=[100.0, 50.0, 70.0])
    ab, ba = backtest.delta_ci(a, b), backtest.delta_ci(b, a)
    assert ab["d_val_at_k"] == pytest.approx(-ba["d_val_at_k"])
    assert (ab["d_val_low"], ab["d_val_high"]) == pytest.approx((-ba["d_val_high"], -ba["d_val_low"]))


def test_every_strategy_has_a_stable_code():
    names = [name for name, _, _ in backtest.RANKERS + backtest.LIMITS]
    assert set(backtest.CODES) == set(names) and len(set(backtest.CODES.values())) == len(names)
    served = [backtest.CODES[name] for name, _, leak in backtest.RANKERS if not leak]
    assert served == list(codes.RANKER_CODES)  # a API serve estas, nesta ordem


@pytest.mark.real_data
def test_real_result_carries_the_codes(real_result):
    for key in ("summary", "limits", "without_no_outcome"):
        assert all(entry["code"] == backtest.CODES[entry["ranker"]] for entry in real_result[key]), key
    assert all(row["code"] == backtest.CODES[row["ranker"]] for row in real_result["rows"])


@pytest.mark.real_data
def test_real_backtest_is_deterministic(real_result):
    assert backtest.run(policy.RAW_DIR) == real_result
