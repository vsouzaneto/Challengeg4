"""Gera os resumos que o Radar lê (solution/app/resumos/). Roda local, com o CSV do Kaggle.

Uso, na pasta da submissão:
    python solution/gerar_resumos.py
"""
import shutil
from pathlib import Path

from src.dados import CAMINHO_PADRAO, carregar
from src.metricas import adicionar_metricas
from src.resumos import resumo_celulas, resumo_laudo, resumo_semanas, resumo_semanas_grupos

PASTA_SOLUCAO = Path(__file__).resolve().parent
PASTA_SAIDA = PASTA_SOLUCAO / "app" / "resumos"
SIMULACAO = PASTA_SOLUCAO / "resultados" / "validacao_metodo_resumo.csv"


def main(caminho_csv=CAMINHO_PADRAO, pasta_saida=PASTA_SAIDA, simulacao=SIMULACAO):
    df = adicionar_metricas(carregar(caminho_csv))
    pasta_saida = Path(pasta_saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)
    resumos = {
        "laudo.csv": resumo_laudo(df),
        "celulas.csv": resumo_celulas(df),
        "semanas.csv": resumo_semanas(df),
        "semanas_grupos.csv": resumo_semanas_grupos(df),
    }
    for nome, tabela in resumos.items():
        tabela.to_csv(pasta_saida / nome, index=False)
    shutil.copyfile(simulacao, pasta_saida / "simulacao.csv")
    return {nome: len(tabela) for nome, tabela in resumos.items()}


if __name__ == "__main__":
    for nome, linhas in main().items():
        print(f"{nome}: {linhas} linhas")
