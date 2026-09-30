from services.agents.openai_agent import OpenAIAgent


class TicketExtractionAgent:
    def run(self, context: dict) -> dict:
        return OpenAIAgent(
            "Você é um agente de extração. Identifique os principais problemas e palavras-chave, "
            "e liste os canais, prioridades e tipos de ticket mais relevantes. "
            "Retorne: principais_problemas, palavras_chave, canais, prioridades, tipos_ticket."
        ).run(context)
