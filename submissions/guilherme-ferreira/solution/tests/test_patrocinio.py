import pandas as pd

from src.patrocinio import marcar_fit


def test_marcar_fit_usa_o_mapa_de_patrocinador_para_categoria():
    df = pd.DataFrame(
        {
            "is_sponsored": [True, True, True, True, False],
            "sponsor_category": ["cosmetics", "cosmetics", "fashion", "gaming", "Not sponsors"],
            "content_category": ["beauty", "tech", "lifestyle", "beauty", "beauty"],
        }
    )

    fit = marcar_fit(df)

    assert fit.tolist()[:4] == [True, False, True, False]
    assert pd.isna(fit.iloc[4])  # post orgânico não tem fit nem falta de fit
