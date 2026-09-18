from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app" / "streamlit_app.py")


def run_app() -> AppTest:
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    assert not at.exception, at.exception
    return at


def test_app_loads_and_flags_challenge_file():
    at = run_app()
    assert any("NÃO APTO" in e.value for e in at.error)
    assert len(at.tabs) == 4


def test_every_dimension_renders_without_error():
    at = run_app()
    select = at.selectbox[0]
    for option in select.options:
        select.set_value(option).run()
        assert not at.exception, (option, at.exception)


def test_incomplete_contract_is_blocked():
    at = run_app()
    at.button[0].click().run()  # formulário vazio
    assert any("BLOQUEADO" in e.value for e in at.error)


def test_example_experiment_gets_a_decision():
    at = run_app()
    assert any("Sugestão" in m.value for m in at.markdown)


def test_file_checked_in_tab_1_feeds_the_panel():
    at = run_app()
    at.radio[0].set_value("Exemplo sintético bem instrumentado (fictício)").run()
    assert not at.exception, at.exception
    base = at.radio[1]
    assert len(base.options) == 2
    base.set_value(base.options[1]).run()
    assert not at.exception, at.exception
    posts_metric = next(m for m in at.metric if m.label == "Posts no filtro")
    assert posts_metric.value != "52.214"  # o painel saiu do arquivo do challenge
    assert len(at.tabs) == 4  # as abas 3 e 4 continuam de pé
