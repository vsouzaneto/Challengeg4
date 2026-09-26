import numpy as np
import pandas as pd

from src.hashtags import comparar_hashtags


def posts_com_hashtags():
    """200 posts: 'alta' rende 20% a mais; 'neutra' rende igual; 'rara' aparece em poucos posts."""
    rng = np.random.default_rng(11)
    tags = ["alta"] * 60 + ["neutra,outra"] * 60 + ["rara"] * 10 + [np.nan] * 70
    engajamento = np.where(np.array(tags, dtype=object) == "alta", 0.24, 0.20) + rng.normal(0, 0.005, len(tags))
    return pd.DataFrame({"hashtags": tags, "engajamento": engajamento})


def test_comparar_hashtags_so_marca_como_sinal_a_hashtag_com_efeito():
    tabela = comparar_hashtags(posts_com_hashtags(), minimo=30).set_index("hashtag")

    assert tabela.loc["alta", "classe"] == "sinal"
    assert tabela.loc["neutra", "classe"] != "sinal"
    assert tabela.loc["neutra", "n"] == 60


def test_comparar_hashtags_ignora_hashtags_com_poucos_posts():
    tabela = comparar_hashtags(posts_com_hashtags(), minimo=30)

    assert "rara" not in set(tabela["hashtag"])
