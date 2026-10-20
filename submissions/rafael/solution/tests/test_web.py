"""Tests for the web app: explorer aggregations, prediction service and every page/API route (synthetic data, light models)."""
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from social_web import explore, predict, server
from social_web.state import load_state
from test_questions import make_posts


@pytest.fixture(scope="module")
def client(tmp_path_factory) -> TestClient:
    df = make_posts()
    df["creator_id"] = "c" + (df.index % 400).astype(str)
    df["creator_name"] = "n" + (df.index % 900).astype(str)
    df["content_url"] = np.where(df.index % 2 == 0, "https://a.com/", "http://b.org/")
    state = load_state(df=df, cache_dir=tmp_path_factory.mktemp("cache"), light=True)
    return TestClient(server.create_app(state))


@pytest.fixture
def posts() -> pd.DataFrame:
    return explore.prepare(make_posts())


def test_filters_and_kpis(posts):
    sub = explore.apply_filters(posts, {"platform": ["TikTok"], "content_type": ["video", "image"]})
    assert set(sub.platform) == {"TikTok"} and set(sub.content_type) <= {"video", "image"}
    cards = {c["id"]: c for c in explore.kpis(sub, posts)}
    assert cards["posts"]["valor"] == len(sub) and abs(cards["top5_views"]["total"] - 5) < 1


def test_breakdown_flags_real_difference(posts):
    posts.loc[posts.platform == "TikTok", "views"] += 300
    rows = {r["grupo"]: r for r in explore.breakdown(posts, "platform", "views")}
    assert rows["TikTok"]["diferente"] and rows["TikTok"]["vs_resto"] > 2
    assert all(r["vs_resto"] < 0 for g, r in rows.items() if g != "TikTok")  # everyone else sits below a boosted rest


def test_breakdown_natural_order(posts):
    assert [r["grupo"] for r in explore.breakdown(posts, "daypart", "views")] == ["madrugada", "manhã", "tarde", "noite"]


def test_explore_rejects_unknown_dimension(posts):
    with pytest.raises(ValueError):
        explore.explore(posts, dimension="nope")


def test_pocket_matching():
    row = {"platform": "TikTok", "content_category": "beauty", "language": "Spanish", "content_length": 200}
    assert predict.pocket_matches({"plataforma": "TikTok", "condicoes": {"content_category": "beauty", "language": "Spanish"}}, row)
    assert predict.pocket_matches({"plataforma": "todas", "condicoes": {"content_length": [174, 316]}}, row)
    assert not predict.pocket_matches({"plataforma": "YouTube", "condicoes": {"content_category": "beauty"}}, row)


@pytest.mark.parametrize("path", ["/", "/perguntas", "/estrategia", "/descobertas", "/explorar", "/simular", "/audiencia", "/auditorias", "/metodo"])
def test_pages_render(client, path):
    res = client.get(path)
    assert res.status_code == 200 and "G4 Marketing" in res.text and "{{" not in res.text


def test_api_explore_and_options(client):
    opts = client.get("/api/options").json()
    assert "platform" in opts["filtros"] and "views" in opts["metricas"]
    res = client.post("/api/explore", json={"filtros": {"platform": ["TikTok"]}, "dimensao": "content_type", "metrica": "top5_likes"})
    body = res.json()
    assert res.status_code == 200 and body["posts"] > 0 and body["breakdown"] and body["matriz"]["linhas"] == ["TikTok"]
    assert client.post("/api/explore", json={"dimensao": "nope"}).status_code == 422


def test_api_predict(client):
    res = client.post("/api/predict", json={"platform": "YouTube", "content_type": "image", "hour": 8, "is_sponsored": True})
    body = res.json()
    assert res.status_code == 200
    assert {c["metrica"] for c in body["chances"]} == {"views", "likes", "comments_count"}
    assert len(body["por_formato"]) == 3 * len({c["formato"] for c in body["por_formato"]}) and body["resumo"] and body["post"]["sponsor_category"] != "Not sponsors"
    assert client.post("/api/predict", json={"hour": 30}).status_code == 422


def test_timeseries_drops_partial_months(posts):
    posts = posts.copy()
    posts.loc[posts.index[:5], "month"] = "2020-01"  # a sparse edge month
    assert "2020-01" not in [r["mes"] for r in explore.timeseries(posts, "views")]


def test_cross_filtering_keeps_own_dimension(posts):
    result = explore.explore(posts, {"platform": ["TikTok"]}, charts=["platform", "content_type"])
    assert len(result["graficos"]["platform"]) == posts.platform.nunique()  # own filter ignored: all options visible
    assert result["posts"] == (posts.platform == "TikTok").sum()


def test_headline_reports_real_difference(posts):
    assert explore.explore(posts)["resumo"]["tipo"] == "nenhum"
    posts.loc[posts.content_type == "video", "views"] += 300
    summary = explore.explore(posts)["resumo"]
    assert summary["tipo"] == "destaque" and summary["dimensao"] == "content_type" and summary["vs_media"] > 0


def test_old_predict_path_redirects(client):
    res = client.get("/prever", follow_redirects=False)
    assert res.status_code == 301 and res.headers["location"] == "/simular"


def test_predict_returns_status_and_improvements(client):
    body = client.post("/api/predict", json={"platform": "TikTok"}).json()
    assert {s["status"] for s in body["status"]} <= {"acima", "normal", "abaixo"}
    assert isinstance(body["melhorias"], list)


def test_nearby_best_finds_planted_language(tmp_path_factory):
    df = make_posts()
    df["creator_id"] = "c" + (df.index % 400).astype(str)
    df["creator_name"] = "n" + (df.index % 900).astype(str)
    df["content_url"] = "https://a.com/"
    boost = (df.platform == "TikTok") & (df.language == "Spanish")
    df.loc[boost, "likes"] += 120  # Spanish posts on TikTok bomb in likes
    state = load_state(df=df, cache_dir=tmp_path_factory.mktemp("planted"), light=True)
    post = {"platform": "TikTok", "content_type": "video", "content_category": "tech", "language": "English", "is_sponsored": False,
            "sponsor_category": "Not sponsors", "disclosure_type": "none", "disclosure_location": "none", "weekday": "Friday", "hour": 10,
            "follower_count": 20000, "content_length": 40, "n_hashtags": 2, "caption_words": 10, "audience_gender_distribution": "female",
            "audience_age_distribution": "19-25", "audience_location": "USA", "creator_id": None}
    suggestion = state.predictor.predict(post, goal="likes")["sugestao"]
    assert suggestion["mudancas"].get("language") == "Spanish" and suggestion["para"] > suggestion["de"]


def test_favicon_and_logo(client):
    res = client.get("/favicon.ico")
    assert res.status_code == 200 and res.headers["content-type"] == "image/x-icon" and res.content[:4] == b"\x00\x00\x01\x00"
    assert 'src="/static/img/g4-icon-192.png"' in client.get("/").text


def test_audits_page_shows_five_verdicts_and_rules(client):
    res = client.get("/auditorias")
    assert res.status_code == 200 and res.text.count('data-audit="') == 5
    assert "não parecer jurídico" in res.text and 'href="/auditorias"' in res.text


@pytest.mark.parametrize("path", ["/", "/perguntas", "/estrategia", "/descobertas", "/explorar", "/simular"])
def test_timezone_note_on_time_pages(client, path):
    assert server.TIME_NOTE in client.get(path).text


@pytest.mark.parametrize("path", ["/", "/perguntas", "/explorar", "/simular", "/auditorias"])
def test_length_note_where_duration_appears(client, path):
    assert 'data-note="duracao"' in client.get(path).text


def test_predict_flags_market_mismatch(client):
    off = client.post("/api/predict", json={"platform": "Instagram", "language": "English", "audience_location": "Russia"}).json()["mercado"]
    assert off == {"mercado": "Russia", "idioma_ok": False, "plataforma_ok": False, "idiomas": ["Russian"]}
    ok = client.post("/api/predict", json={"platform": "TikTok", "language": "English", "audience_location": "USA"}).json()["mercado"]
    assert ok["idioma_ok"] and ok["plataforma_ok"]


def test_audience_segments_api(client):
    body = client.post("/api/audience", json={"content_type": "video"}).json()
    assert body["filtros"] == {"content_type": "video"} and "erro" in body  # fixture has only 8 profiles: explain, don't cluster
    assert client.post("/api/audience", json={"platform": "Orkut"}).status_code == 422
    assert client.post("/api/audience", json={"k": 9}).status_code == 422


def test_audience_segments_cluster_profiles():
    from social_insights import audience_segments
    rng = np.random.default_rng(0)
    levels = {"audience_age_distribution": ["13-18", "19-25", "26-35"], "audience_gender_distribution": ["female", "male"],
              "audience_location": ["USA", "Brazil", "India"], "platform": ["TikTok", "YouTube"], "content_type": ["video", "image"],
              "content_category": ["beauty", "tech"], "language": ["English", "Spanish"]}
    df = pd.DataFrame({c: rng.choice(v, 6000) for c, v in levels.items()}).assign(is_sponsored=rng.random(6000) < 0.4)
    df.loc[df.audience_location == "Brazil", "language"] = "Spanish"  # planted: one country consumes a different language
    r = audience_segments.segment(df, {"content_type": "video"}, 2)
    assert r["k"] == 2 and r["perfis"] == 18 and sum(g["perfis"] for g in r["grupos"]) == len(r["mapa"]) == 18
    assert all(c["campo"] != "content_type" for c in r["colunas"])  # filtered field is constant, so it is not clustered on
    spanish = next(g for g in r["grupos"] if g["consumo"][0]["valor"] == "Spanish")
    assert spanish["traco"]["valor"] == "Brazil" and spanish["perfis"] == 6
