"""Executa a camada de scoring e imprime resultados, sem exportar arquivos."""

import json
import sys
from data import load_data
from scoring import score_open_opportunities


def main():
    # Preserva acentos também quando a saída é capturada no Windows.
    sys.stdout.reconfigure(encoding="utf-8")
    dataset = load_data()
    result = score_open_opportunities(dataset)
    print(json.dumps({
        "reference_date": result.reference_date.isoformat(),
        "open_opportunities": len(result.opportunities),
        "closed_opportunities": len(dataset.closed_opportunities),
        "historical_count": result.historical_count,
        "historical_win_rate": result.historical_win_rate,
        "confidence_counts": result.confidence_counts,
        "watchlist_price_threshold": result.watchlist_price_threshold,
        "watchlist_count": sum(row["watchlist"] for row in result.opportunities),
        "notice": "Priority Score é posição relativa, não probabilidade de fechamento. Historical Fit não é probabilidade calibrada.",
        "top_10": result.opportunities[:10],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
