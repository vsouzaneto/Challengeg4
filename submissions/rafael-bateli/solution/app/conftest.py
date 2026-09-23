import sys
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parent
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))


@pytest.fixture(autouse=True)
def local_isolado(tmp_path, monkeypatch):
    """Eventos e logs de cada teste vão para uma pasta temporária."""
    monkeypatch.setenv("LOCAL_DIR", str(tmp_path / "local"))
    yield tmp_path / "local"
