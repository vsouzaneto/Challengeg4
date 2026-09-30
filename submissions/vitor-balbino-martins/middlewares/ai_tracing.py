"""Tracing local das chamadas de IA, sem envio para servidores de observabilidade."""
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from core.config import settings


def record_ai_trace(*, agent: str, model: str, prompt: str, response=None,
                    usage=None, error=None, started_at: float) -> None:
    trace = {"timestamp": datetime.now(timezone.utc).isoformat(), "agent": agent,
             "model": model, "duration_ms": round((time.time() - started_at) * 1000, 2),
             "prompt": prompt, "response": response, "usage": usage,
             "error": str(error) if error else None}
    path = Path(settings.AI_TRACE_LOG)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(trace, ensure_ascii=False, default=str) + "\n")
