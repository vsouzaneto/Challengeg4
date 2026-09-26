import numpy as np
import pandas as pd

import validacao_metodo_simulacao
from src.simulacao import plantar_efeito, resumir_validacao, validar_metodo

DIMENSOES = ["plataforma", "formato"]


def dados_poisson(n_por_celula=80, semente=0):
    """9 células sem efeito nenhum, com contagens sorteadas como no dado do challenge."""
    rng = np.random.default_rng(semente)
    n = n_por_celula
    partes = [
        pd.DataFrame(
            {
                "plataforma": p,
                "formato": f,
                "views": rng.poisson(10_100, n),
                "likes": rng.poisson(1_510, n),
                "shares": rng.poisson(300, n),
                "comments_count": rng.poisson(200, n),
            }
        )
        for p in "ABC"
        for f in "xyz"
    ]
    return pd.concat(partes, ignore_index=True)


def test_plantar_efeito_multiplica_as_interacoes_so_nas_linhas_marcadas():
    df = pd.DataFrame({"likes": [100, 100], "shares": [20, 20], "comments_count": [30, 30], "views": [1000, 1000]})

    plantado = plantar_efeito(df, np.array([True, False]), 0.10)

    assert plantado.loc[0, ["likes", "shares", "comments_count", "views"]].tolist() == [110, 22, 33, 1000]
    assert plantado.loc[1, ["likes", "shares", "comments_count", "views"]].tolist() == [100, 20, 30, 1000]
    assert df.loc[0, "likes"] == 100


def test_validar_metodo_acha_efeito_grande_e_nao_chama_efeito_pequeno_de_sinal():
    rodadas = validar_metodo(dados_poisson(), efeitos=[0.5, 0.03, 0.0], dimensoes=DIMENSOES, repeticoes=5, semente=1)

    resumo = resumir_validacao(rodadas).set_index("efeito")

    assert resumo.loc[0.5, "taxa_sinal"] == 1.0
    assert resumo.loc[0.03, "taxa_sinal"] == 0.0
    assert resumo.loc[0.03, "taxa_abaixo_do_limiar"] == 1.0  # percebe o efeito, mas é pequeno demais
    assert resumo.loc[0.0, "taxa_sinal"] == 0.0
    assert rodadas["falsos_positivos"].sum() == 0


def test_script_de_validacao_grava_um_resumo_por_efeito(tmp_path):
    posts = dados_poisson(n_por_celula=40).rename(columns={"plataforma": "platform", "formato": "content_type"})
    posts["content_category"] = "beauty"
    posts["follower_count"] = 200_000
    posts["post_date"] = "5/29/23 12:15 AM"
    arquivo = tmp_path / "posts.csv"
    posts.to_csv(arquivo, index=False)

    validacao_metodo_simulacao.main(arquivo, tmp_path / "saida", repeticoes=2, semente=0)

    resumo = pd.read_csv(tmp_path / "saida" / "validacao_metodo_resumo.csv")
    assert sorted(resumo["efeito"]) == [0.03, 0.10, 0.15]
