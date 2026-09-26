import pandas as pd

import gerar_resumos


def test_gerar_resumos_grava_os_cinco_arquivos(tmp_path, posts_minimos):
    csv = tmp_path / "posts.csv"
    posts_minimos.assign(post_date=posts_minimos["post_date"].dt.strftime("%m/%d/%y %I:%M %p")).to_csv(csv, index=False)
    simulacao = tmp_path / "simulacao.csv"
    pd.DataFrame({"efeito": [0.15], "rodadas": [2], "taxa_sinal": [1.0], "taxa_abaixo_do_limiar": [0.0],
                  "lift_medido_medio": [0.15], "falsos_positivos_por_rodada": [0.0]}).to_csv(simulacao, index=False)

    linhas = gerar_resumos.main(csv, tmp_path / "resumos", simulacao)

    assert sorted(p.name for p in (tmp_path / "resumos").iterdir()) == [
        "celulas.csv", "laudo.csv", "semanas.csv", "semanas_grupos.csv", "simulacao.csv",
    ]
    assert linhas["semanas.csv"] == 2
    assert "fit" in set(pd.read_csv(tmp_path / "resumos" / "laudo.csv")["chave"])
