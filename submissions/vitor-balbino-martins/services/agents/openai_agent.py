import json
import time

from openai import OpenAI
from core.config import settings
from middlewares.ai_tracing import record_ai_trace


class OpenAIAgent:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=settings.OPENAI_TIMEOUT_SECONDS)

    def run(self, context: dict) -> dict:
        prompt = (
            "Analise exclusivamente o contexto fornecido. Responda somente JSON válido, sem markdown.\n"
            + json.dumps(context, ensure_ascii=False, default=str)
        )
        started_at = time.time()
        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError("A API da OpenAI retornou uma resposta vazia")
            result = json.loads(content)
            record_ai_trace(agent=self.__class__.__name__, model=settings.OPENAI_MODEL,
                            prompt=prompt, response=result,
                            usage=response.usage.model_dump() if response.usage else None,
                            started_at=started_at)
            return result
        except Exception as exc:
            record_ai_trace(agent=self.__class__.__name__, model=settings.OPENAI_MODEL,
                            prompt=prompt, error=exc, started_at=started_at)
            raise
