import sys
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parent
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))


import pandas as pd  # noqa: E402

from motor import config  # noqa: E402


@pytest.fixture(scope="session")
def d1():
    if not config.csv_d1().exists():
        pytest.skip("Dataset 1 ausente em solution/data/")
    return pd.read_csv(config.csv_d1())


@pytest.fixture(scope="session")
def modelo_d2():
    from motor import classificador
    if not config.csv_d2().exists():
        pytest.skip("Dataset 2 ausente em solution/data/")
    m, _ = classificador.carregar_ou_treinar(caminho_pkl=config.APP / "dados_locais" / "modelo_d2.pkl")
    return m


@pytest.fixture(autouse=True)
def local_isolado(tmp_path, monkeypatch):
    """Eventos e logs de cada teste vão para uma pasta temporária."""
    monkeypatch.setenv("LOCAL_DIR", str(tmp_path / "local"))
    yield tmp_path / "local"
