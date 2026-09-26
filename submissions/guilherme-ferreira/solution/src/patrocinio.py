"""Patrocínio: relação entre a categoria do patrocinador e a do conteúdo."""
import pandas as pd

# Premissa declarada: categorias de conteúdo que combinam com cada categoria de patrocinador.
FIT_PATROCINIO = {
    "cosmetics": {"beauty"},
    "fashion": {"beauty", "lifestyle"},
    "electronics": {"tech"},
    "gaming": {"tech"},
    "food": {"lifestyle"},
    "travel": {"lifestyle"},
}


def marcar_fit(df) -> pd.Series:
    """True quando o conteúdo combina com o patrocinador; vazio (NA) nos posts orgânicos."""
    combina = [
        conteudo in FIT_PATROCINIO.get(patrocinador, set())
        for patrocinador, conteudo in zip(df["sponsor_category"], df["content_category"])
    ]
    return pd.Series(combina, index=df.index, dtype="boolean").where(df["is_sponsored"])
