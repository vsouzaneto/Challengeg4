import pandas as pd
import pytest

from src.dados import carregar

CSV_MINIMO = """id,post_date,views
1,5/29/23 12:15 AM,100
2,12/1/24 3:05 PM,200
"""


def test_carregar_converte_data_com_am_pm(tmp_path):
    arquivo = tmp_path / "posts.csv"
    arquivo.write_text(CSV_MINIMO)

    df = carregar(arquivo)

    assert df["post_date"].tolist() == [
        pd.Timestamp("2023-05-29 00:15"),
        pd.Timestamp("2024-12-01 15:05"),
    ]


def test_carregar_sem_arquivo_diz_onde_baixar(tmp_path):
    with pytest.raises(FileNotFoundError, match="(?i)kaggle"):
        carregar(tmp_path / "nao_existe.csv")
