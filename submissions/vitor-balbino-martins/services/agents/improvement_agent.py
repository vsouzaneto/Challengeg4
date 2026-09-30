from services.agents.openai_agent import OpenAIAgent


class ImprovementAgent:
    def run(self, context: dict) -> dict:
        return OpenAIAgent(
            "Você é o agente líder de melhoria contínua. Consolide todas as métricas, "
            "clusters, satisfação, gargalos, desperdício e evidências textuais. "
            "Não invente dados. Retorne JSON com: resumo, prioridades (lista), "
            "esteira (lista de objetos com categoria, problema, evidencia, impacto, "
            "acao, prioridade, ganho_estimado e fontes), quick_wins e riscos. "
            "Organize a esteira por ordem de impacto operacional."
        ).run(context)
