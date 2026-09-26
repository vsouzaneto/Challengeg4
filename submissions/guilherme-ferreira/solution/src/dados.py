"""Leitura do CSV do challenge 004 com os tipos certos."""
from pathlib import Path

import pandas as pd

CAMINHO_PADRAO = Path(__file__).resolve().parents[1] / "data" / "social_media_dataset.csv"
URL_KAGGLE = "https://www.kaggle.com/datasets/omenkj/social-media-sponsorship-and-engagement-dataset"
FORMATO_DATA = "%m/%d/%y %I:%M %p"  # ex.: 5/29/23 12:15 AM


def carregar(caminho=CAMINHO_PADRAO) -> pd.DataFrame:
    """Lê o CSV e converte post_date para data e hora."""
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(
            f"CSV não encontrado em {caminho}. Baixe o dataset no Kaggle ({URL_KAGGLE}) "
            "e salve como solution/data/social_media_dataset.csv."
        )
    df = pd.read_csv(caminho)
    df["post_date"] = pd.to_datetime(df["post_date"], format=FORMATO_DATA)
    return df
