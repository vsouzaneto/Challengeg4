"""G5: custo implícito do patrocínio e tamanho dos testes do próximo ciclo.

O arquivo não tem custo (DQ-12). Em vez de inventar um fee, calculamos o teto do que um patrocínio
poderia valer usando o MELHOR cenário estatístico do G3 (limite superior do IC 95%).
O valor por interação é um parâmetro, não um dado; a tabela mostra vários valores.

Uso: uv run python src/analysis/implied_cost.py  (depois de run_inference.py)
"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.decision.rules import engagement_value_ceiling, sample_size_per_arm  # noqa: E402

TABLES = ROOT / "outputs" / "tables"
VALUE_PER_INTERACTION_BRL = [0.10, 0.50, 1.00, 5.00]  # parâmetros ilustrativos, sem fonte no arquivo
REAL_WORLD_SD_PP = [2.0, 5.0, 10.0]  # desvio da taxa de engajamento por post; o do arquivo é ~0,49
POSTS_PER_CONTRACT = 10
# Faixas de preço por post/Reels no Brasil, pesquisa de mercado trazida por Douglas em 2026-09-16
# (jmonline.com.br, vocenohype.com.br, influee.co, stan.store). Parâmetro externo, não dado do arquivo.
MARKET_FEES_BRL = {"micro (10–100 mil)": (500, 3_000), "grande (> 500 mil)": (15_000, 100_000)}
MARKET_FEES_SOURCE = ("pesquisa de mercado do Douglas em 2026-09-16: jmonline.com.br, vocenohype.com.br, "
                      "influee.co, stan.store; faixa por post/Reels no Brasil, varia por nicho, formato e uso de imagem")
UNIT_MARGINS_BRL = [20, 50, 100]  # margem de contribuição por venda: parâmetro do negócio


def main() -> None:
    adjusted = pd.read_csv(TABLES / "inf-sponsorship-adjusted.csv").set_index("desfecho")
    er = adjusted.loc["taxa de engajamento (p.p.)"]
    views = adjusted.loc["views (guardrail)"]
    base_views = views.media_organico

    extra_interactions_per_post = base_views * er.ic95_sup / 100
    rows = [{"valor_por_interacao_brl": v,
             "interacoes_extras_por_post_melhor_caso": extra_interactions_per_post,
             "views_extras_por_post_melhor_caso": views.ic95_sup,
             "teto_de_valor_por_post_brl": engagement_value_ceiling(base_views, er.ic95_sup, v),
             f"teto_por_contrato_{POSTS_PER_CONTRACT}_posts_brl": engagement_value_ceiling(
                 base_views, er.ic95_sup, v, POSTS_PER_CONTRACT)}
            for v in VALUE_PER_INTERACTION_BRL]
    implied = pd.DataFrame(rows)
    implied.to_csv(TABLES / "str-implied-cost.csv", index=False)

    best_case_value = engagement_value_ceiling(base_views, er.ic95_sup, max(VALUE_PER_INTERACTION_BRL))
    market = pd.DataFrame([
        {"perfil": perfil, "fee_min_brl": lo, "fee_max_brl": hi,
         "fee_sobre_teto_engajamento_min_x": lo / best_case_value,
         "fee_sobre_teto_engajamento_max_x": hi / best_case_value,
         # Não depende de nenhum valor escolhido para a interação: quanto cada interação extra
         # precisaria valer para o engajamento pagar sozinho o fee de um post.
         "valor_por_interacao_para_empatar_fee_min_brl": lo / extra_interactions_per_post,
         "valor_por_interacao_para_empatar_fee_max_brl": hi / extra_interactions_per_post,
         **{f"vendas_para_pagar_margem_{m}_brl": f"{lo / m:,.0f}–{hi / m:,.0f}" for m in UNIT_MARGINS_BRL},
         "fonte": MARKET_FEES_SOURCE}
        for perfil, (lo, hi) in MARKET_FEES_BRL.items()])
    market.to_csv(TABLES / "str-market-fees.csv", index=False)

    sizing = pd.DataFrame([{"desvio_padrao_pp": sd, "regua_pp": 1.0,
                            "posts_por_braco": sample_size_per_arm(sd, 1.0),
                            "posts_por_braco_regua_2pp": sample_size_per_arm(sd, 2.0)}
                           for sd in REAL_WORLD_SD_PP])
    sizing.to_csv(TABLES / "str-test-sizing.csv", index=False)

    with pd.option_context("display.width", 200):
        print(implied.round(3).to_string(index=False))
        print()
        print(market.round(0).to_string(index=False))
        print()
        print(sizing.to_string(index=False))


if __name__ == "__main__":
    main()
