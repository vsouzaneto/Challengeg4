import shutil

import pytest
from streamlit.testing.v1 import AppTest

from motor import config

APP = str(config.APP / "app.py")
TELAS = ["Fila do agente", "Painel do Diretor", "Tente derrubar", "Qualidade da IA"]


@pytest.fixture
def modelo_local(modelo_d2, d1, local_isolado):
    """Copia o .pkl já treinado para a pasta isolada do teste: a tela carrega em vez de retreinar."""
    local_isolado.mkdir(parents=True, exist_ok=True)
    shutil.copy(config.APP / "dados_locais" / "modelo_d2.pkl", local_isolado / "modelo_d2.pkl")


@pytest.mark.parametrize("tela", TELAS)
def test_p12_telas_renderizam(modelo_local, tela):
    at = AppTest.from_file(APP, default_timeout=300).run()
    at.radio(key="tela").set_value(tela).run()
    assert not at.exception, at.exception


def test_p12_dataset_ausente_mostra_instrucao(tmp_path, monkeypatch):
    monkeypatch.setenv("DADOS_DIR", str(tmp_path))
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception
    assert any("Dataset ausente" in e.value for e in at.error)
    assert any("kaggle.com" in m.value for m in at.markdown)


def test_tente_derrubar_prompt_injection_vai_para_humano(modelo_local):
    at = AppTest.from_file(APP, default_timeout=300).run()
    at.radio(key="tela").set_value("Tente derrubar").run()
    at.button(key="adv_Prompt injection").click().run()
    at.button(key="triar").click().run()
    assert not at.exception
    assert any("1B" in s.value for s in at.subheader)
