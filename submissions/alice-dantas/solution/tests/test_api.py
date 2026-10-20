import json
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from api.main import WEB_ORIGIN, create_app
from leadscorer import codes, data, intelligence, policy, views
from leadscorer.__main__ import main
from leadscorer.errors import DataError

from conftest import write_raw


def roundtrip(payload):
    return json.loads(json.dumps(payload))


def pipeline_url(seller, **params):
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"/api/sellers/{quote(seller)}/pipeline" + (f"?{query}" if query else "")


@pytest.fixture
def client(raw_dir):
    return TestClient(create_app(raw_dir))


def test_sellers_are_alphabetical_and_carry_no_metric(client):  # AC-2.9
    sellers = client.get("/api/sellers").json()["sellers"]
    names = [s["name"] for s in sellers]
    assert names == sorted(names) and "Carla Gama" in names
    assert all(set(s) == {"name", "manager", "office"} for s in sellers)


def test_seller_pipeline_is_the_core_payload(client, raw_dir, capsys):  # AC-2.8
    response = client.get(pipeline_url("Ana Alfa"))
    assert response.status_code == 200
    assert response.json() == roundtrip(views.seller_pipeline(data.load(raw_dir), "Ana Alfa"))
    assert main(["--raw", str(raw_dir), "list", "--seller", "Ana Alfa", "--json"]) == 0
    assert json.loads(capsys.readouterr().out) == response.json()


def test_seller_without_open_deals_is_200(client):  # AC-2.5
    body = client.get(pipeline_url("Carla Gama")).json()
    assert body["summary"]["total"] == 0 and body["empty"] == {"code": codes.NO_OPEN_FOR_SELLER, "params": {}}


def test_unknown_seller_is_404(client):  # AC-2.6
    response = client.get(pipeline_url("Fulano"))
    assert response.status_code == 404 and "Fulano" in response.json()["detail"]


def test_invalid_as_of_is_422_with_message(client):  # AC-1.8
    response = client.get(pipeline_url("Ana Alfa", as_of="31/12/2017"))
    assert response.status_code == 422
    assert "AAAA-MM-DD" in response.json()["detail"] and "2017-12-31" in response.json()["detail"]


def test_missing_csv_is_503_with_cli_message_and_recovers(tmp_path):  # AC-1.2
    raw = write_raw(tmp_path / "raw")
    (raw / "products.csv").unlink()
    with pytest.raises(DataError) as error:
        data.load(raw)
    client = TestClient(create_app(raw))
    for url in ("/api/sellers", pipeline_url("Ana Alfa"), "/api/meta", "/api/intelligence",
                "/api/intelligence/deals?outcome=won"):
        response = client.get(url)
        assert response.status_code == 503 and response.json()["detail"] == str(error.value)
    write_raw(raw)  # os arquivos aparecem: a API responde sem reiniciar
    assert client.get("/api/sellers").status_code == 200


def test_filters_never_fail(client):  # AC-2.10
    by_manager = client.get("/api/pipeline?manager=Mara%20Um").json()
    assert by_manager["summary"]["total"] == 9 and by_manager["empty"] is None
    for query in ("manager=Ninguem", "manager=Mara%20Um&office=East", "office=Marte"):
        response = client.get(f"/api/pipeline?{query}")
        assert response.status_code == 200
        body = response.json()
        assert body["summary"]["total"] == 0 and body["empty"] == {"code": codes.NO_OPEN_FOR_FILTER, "params": {}}


@pytest.mark.parametrize("url, core", [
    ("/api/meta", lambda d: views.meta(d, views.context(d, None))),
    ("/api/rules", lambda d: views.rules(d)),
    ("/api/pipeline", lambda d: views.team_pipeline(d)),
    ("/api/pipeline?manager=Mara%20Um", lambda d: views.team_pipeline(d, manager="Mara Um")),
    ("/api/pipeline?office=Central", lambda d: views.team_pipeline(d, office="Central")),
    (pipeline_url("Ana Alfa", as_of="2018-03-31"), lambda d: views.seller_pipeline(d, "Ana Alfa", "2018-03-31")),
    ("/api/intelligence", lambda d: intelligence.payload(d)),
    ("/api/intelligence?manager=Mara%20Um&product=GTX%20Basic",
     lambda d: intelligence.payload(d, intelligence.Filters(manager="Mara Um", product="GTX Basic"))),
    ("/api/intelligence?sector=retail&as_of=2030-01-01",
     lambda d: intelligence.payload(d, intelligence.Filters(sector="retail"), "2030-01-01")),
    ("/api/intelligence/deals?outcome=open&group=revisar", lambda d: intelligence.deals(d, outcome="open",
                                                                                         group="revisar")),
    ("/api/intelligence/deals?outcome=won&seller=Ana%20Alfa",
     lambda d: intelligence.deals(d, intelligence.Filters(seller="Ana Alfa"), "won")),
])
def test_endpoints_are_the_core_payload(client, raw_dir, url, core):  # mesma política em todas as rotas
    assert client.get(url).json() == roundtrip(core(data.load(raw_dir)))


def test_cli_explain_json_is_the_list_item(raw_dir, capsys):
    assert main(["--raw", str(raw_dir), "explain", "--id", "E101", "--json"]) == 0
    detail = json.loads(capsys.readouterr().out)
    listed = views.seller_pipeline(data.load(raw_dir), "Ana Alfa")
    item = next(e for g in listed["groups"] for e in g["items"] if e["opportunity_id"] == "E101")
    assert detail == roundtrip({"meta": listed["meta"], "seller": "Ana Alfa", "item": item})
    assert item["group"] == "acompanhar"


def test_meta_follows_as_of(client):
    assert client.get("/api/meta").json()["as_of"] == "2017-12-31"
    assert client.get("/api/meta?as_of=2030-01-01").json()["as_of"] == "2030-01-01"


def test_cors_only_for_the_web_page(client):
    allowed = client.get("/api/sellers", headers={"Origin": WEB_ORIGIN})
    other = client.get("/api/sellers", headers={"Origin": "http://exemplo.com"})
    assert allowed.headers.get("access-control-allow-origin") == WEB_ORIGIN
    assert "access-control-allow-origin" not in other.headers


@pytest.mark.real_data
def test_real_api_matches_core_for_all_35_sellers(real_dataset):  # AC-2.8
    client = TestClient(create_app(policy.RAW_DIR))
    sellers = client.get("/api/sellers").json()["sellers"]
    assert len(sellers) == 35
    total = 0
    for seller in sellers:
        body = client.get(pipeline_url(seller["name"])).json()
        assert body == roundtrip(views.seller_pipeline(real_dataset, seller["name"]))
        total += body["summary"]["total"]
    assert total == 2089
    assert client.get("/api/pipeline").json()["summary"]["total"] == 2089


@pytest.mark.real_data
def test_real_cli_json_equals_api(capsys):  # AC-2.8
    client = TestClient(create_app(policy.RAW_DIR))
    assert main(["list", "--seller", "Zane Levy", "--json", "--as-of", "2018-01-31"]) == 0
    cli = json.loads(capsys.readouterr().out)
    assert cli == client.get(pipeline_url("Zane Levy", as_of="2018-01-31")).json()


@pytest.mark.real_data
@pytest.mark.parametrize("query, filters", [
    ("", intelligence.Filters()),
    ("?office=East", intelligence.Filters(office="East")),
    ("?sector=retail", intelligence.Filters(sector="retail")),
    ("?account=Kan-code", intelligence.Filters(account="Kan-code")),
])
def test_real_intelligence_api_matches_core(real_dataset, query, filters):
    client = TestClient(create_app(policy.RAW_DIR))
    assert client.get(f"/api/intelligence{query}").json() == roundtrip(intelligence.payload(real_dataset, filters))
