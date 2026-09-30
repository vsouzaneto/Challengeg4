from services.agents.improvement_agent import ImprovementAgent
from services.report_service import SupportReportService


class ImprovementService:
    @classmethod
    def generate(cls, dataset="customer_support_tickets.csv", chunk_size=250, hourly_cost=None):
        report = SupportReportService.generate(dataset, chunk_size, hourly_cost)
        context = {"dataset": dataset, "metrics": report["metrics"], "audit": report["audit"], "consolidation": report["consolidation"]}
        result = ImprovementAgent().run(context)
        if not result.get("esteira"):
            metrics = report["metrics"]
            result["esteira"] = [
                {"categoria": "Operação", "problema": "Combinações com maior tempo de resolução", "evidencia": metrics.get("worst_combinations", []), "impacto": f"{metrics.get('waste', {}).get('recoverable_hours', 0):.1f} horas acima do benchmark", "acao": "Priorizar automação de triagem e roteamento", "prioridade": "alta", "fontes": report["audit"].get("sources", [])},
                {"categoria": "Satisfação", "problema": "Tempo de resposta associado à experiência do cliente", "evidencia": metrics.get("correlations_with_satisfaction", {}), "impacto": f"Satisfação média: {metrics.get('avg_satisfaction', '—')}", "acao": "Criar resposta assistida e alertas de SLA", "prioridade": "media", "fontes": report["audit"].get("sources", [])},
                {"categoria": "Automação", "problema": "Tickets repetitivos por canal, prioridade e tipo", "evidencia": metrics.get("channels", {}), "impacto": f"{metrics.get('ticket_count', 0)} tickets disponíveis para pré-triagem", "acao": "Classificar automaticamente e encaminhar para o time adequado", "prioridade": "baixa", "fontes": report["audit"].get("sources", [])},
            ]
        return {"dataset": dataset, "report": report, "improvement": result}
