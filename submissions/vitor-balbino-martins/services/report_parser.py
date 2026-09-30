class ReportParser:
    @staticmethod
    def _items(value):
        """Achata grupos de achados retornados como objeto com listas internas."""
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            items = []
            for key, nested in value.items():
                if isinstance(nested, list):
                    items.extend(nested)
                elif nested not in (None, "", {}):
                    items.append({"title": key, "value": nested})
            return items or ([value] if value else [])
        return [value] if value not in (None, "") else []

    @staticmethod
    def _first(data, *keys):
        for key in keys:
            value = data.get(key)
            if value not in (None, "", [], {}):
                return value
        return []

    @staticmethod
    def parse(dataset, metrics, extractions, consolidation, sources):
        bottlenecks = ReportParser._first(
            consolidation, "gargalos", "flow_bottlenecks", "bottlenecks", "combinacoes_criticas",
        )
        bottlenecks = ReportParser._items(bottlenecks)
        if not bottlenecks:
            bottlenecks = [{
                "title": "Combinações com maior tempo de resolução",
                "evidence": metrics.get("worst_combinations", []),
                "reason": "Ordenação calculada sobre canal, prioridade e tipo de ticket.",
            }]
        satisfaction = ReportParser._first(
            consolidation, "impactos_satisfacao", "satisfaction_drivers", "satisfaction_impact", "fatores_satisfacao",
        )
        satisfaction = ReportParser._items(satisfaction)
        if not satisfaction:
            satisfaction = [{
                "title": "Variáveis associadas à satisfação",
                "evidence": metrics.get("correlations_with_satisfaction", {}),
                "reason": "Correlação de Pearson e médias de satisfação por canal, prioridade e tipo.",
            }]
        return {
            "schema_version": "1.0", "dataset": dataset,
            "findings": {
                "flow_bottlenecks": bottlenecks,
                "satisfaction_drivers": satisfaction,
                "recoverable_waste": ReportParser._first(consolidation, "desperdicio_recuperavel", "recoverable_waste") or [{"evidence": metrics.get("waste", {})}],
                "recommendations": ReportParser._first(consolidation, "recomendacoes", "recommendations"),
            },
            "evidence": metrics, "agent_extractions": extractions,
            "reasoning": consolidation.get("justificativa", consolidation.get("resumo_executivo")),
            "sources": sources,
        }
