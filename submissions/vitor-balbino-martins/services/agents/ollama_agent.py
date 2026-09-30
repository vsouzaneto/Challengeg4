import json
import httpx
from core.config import settings


class OllamaAgent:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt

    def run(self, context: dict) -> dict:
        prompt = (
            "Analise exclusivamente o contexto fornecido. Responda somente JSON válido, sem markdown.\n"
            + json.dumps(context, ensure_ascii=False, default=str)
        )
        response = httpx.post(
            f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/chat",
            json={"model": settings.OLLAMA_MODEL, "stream": False, "format": "json",
                  "messages": [{"role": "system", "content": self.system_prompt},
                               {"role": "user", "content": prompt}]},
            timeout=settings.OLLAMA_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        content = response.json()["message"]["content"]
        return json.loads(content)
