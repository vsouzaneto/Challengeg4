"""Validação do método por simulação (script isolado).

Planta efeitos conhecidos (+15%, +10% e +3%) em células sorteadas de uma cópia do dado e
mostra com que frequência o método de sinal os encontra. Nenhum número da análise vem daqui.

Uso, na pasta da submissão:
    python solution/validacao_metodo_simulacao.py
"""
from pathlib import Path

from src.dados import CAMINHO_PADRAO, carregar
from src.metricas import faixa_creator
from src.simulacao import resumir_validacao, validar_metodo

DIMENSOES = ["platform", "content_category", "content_type", "faixa_creator"]
EFEITOS = [0.15, 0.10, 0.03]
PASTA_SAIDA = Path(__file__).resolve().parent / "resultados"


def main(caminho_csv=CAMINHO_PADRAO, pasta_saida=PASTA_SAIDA, repeticoes=200, semente=42):
    df = carregar(caminho_csv)
    df["faixa_creator"] = faixa_creator(df["follower_count"])
    rodadas = validar_metodo(df, EFEITOS, DIMENSOES, repeticoes=repeticoes, semente=semente)
    resumo = resumir_validacao(rodadas)

    pasta_saida = Path(pasta_saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)
    rodadas.to_csv(pasta_saida / "validacao_metodo_rodadas.csv", index=False)
    resumo.to_csv(pasta_saida / "validacao_metodo_resumo.csv", index=False)
    print(resumo.to_string(index=False))
    return resumo


if __name__ == "__main__":
    main()
