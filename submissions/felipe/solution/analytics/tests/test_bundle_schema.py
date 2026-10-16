import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs"


def _bundle() -> dict:
    return json.loads((OUT / "dashboard_bundle.json").read_text(encoding="utf-8"))


def test_bundle_qualidade_dados_keys():
    q = _bundle()["qualidade_dados"]
    for k in ("contas_flag_sem_evento_churn", "pct_uso_antes_assinatura", "eventos_churn_total"):
        assert k in q


def test_bundle_recomendacao_destaque():
    r = _bundle()["recomendacao_destaque"]
    assert r["impacto_mrr_usd"] > 0
    assert "Playbook" in r["acao"] or len(r["acao"]) > 10


def test_investigacoes_sample_account():
    b = _bundle()
    cid = b["contas"][0]["conta_id"]
    inv = b["investigacoes"][cid]
    assert "suporte" in inv
    assert "eventos_churn" in inv


def test_investigacoes_cover_all_contas():
    b = _bundle()
    ids = {c["conta_id"] for c in b["contas"]}
    assert ids.issubset(set(b["investigacoes"].keys()))


def test_kpis_globais_auc():
    k = _bundle()["kpis_globais"]
    assert 0.5 < k["auc_modelo"] < 1.0


def test_filtros_periodo():
    f = _bundle()["filtros_disponiveis"]
    assert f.get("periodo_min") and f.get("periodo_max")
