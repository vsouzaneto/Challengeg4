import pandas as pd

from leadscorer.brief import MAX_ITEMS, seller_brief
from leadscorer.manager import agent_table, manager_must_acts, revops_findings, team_table
from leadscorer.scoring import score_pipeline
from tests.test_scoring import _big_pipeline, _cal


def _scored():
    df = _big_pipeline(n=120, seed=3)
    scored, cal = score_pipeline(df, pd.Timestamp("2017-12-31"), _cal())
    return df, scored


def test_seller_brief_budget_and_order():
    df, scored = _scored()
    b = seller_brief(scored[scored["sales_agent"] == "A"])
    assert 0 < len(b["itens"]) <= MAX_ITEMS
    tipos = [i["tipo"] for i in b["itens"]]
    ordem = ["Focar agora", "Primeiras duas semanas", "Confirmar se está vivo", "Cadastrar conta", "Qualificar ou descartar", "Manter follow-up"]
    primeiros = [t for t in tipos if t != "Qualificar ou descartar"]
    assert [ordem.index(t) for t in primeiros] == sorted(ordem.index(t) for t in primeiros)
    assert len({i["deal"] for i in b["itens"]}) == len(b["itens"])
    assert all("porque" in i and i["acao"] for i in b["itens"])


def test_agent_table_and_findings():
    df, scored = _scored()
    agents = agent_table(scored, df, pd.Timestamp("2017-12-31"))
    assert set(agents.index) == set(scored["sales_agent"].unique())
    assert (agents["abertos"] == scored.groupby("sales_agent").size().reindex(agents.index)).all()
    f = revops_findings(scored, agents)
    assert f["deals_abertos"] == len(scored)
    assert 0 <= f["pct_sem_conta"] <= 100
    t = team_table(agents)
    assert t["abertos"].sum() == len(scored)


def test_manager_must_acts_are_grounded():
    df, scored = _scored()
    agents = agent_table(scored, df, pd.Timestamp("2017-12-31"))
    acts = manager_must_acts(agents, scored)
    assert len(acts) <= 5
    for a in acts:
        assert a["quem"] in agents.index and a["porque"] and a["acao"]
