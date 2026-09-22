"""Verificação de desenvolvimento, não benchmark nem verdade humana independente."""
import asyncio
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from service_flow import scenarios, extract_signals, connect_context, decide, PROMPT, MODEL


async def main():
    semaphore = asyncio.Semaphore(2)
    expected = {'reset':'self_service','failed':'prepared','leave':'prepared',
                'incident':'human','disabled':'human','unavailable':'human','thread':'prepared'}
    async def run(s):
        async with semaphore:
            signals = await extract_signals(s['text'])
            plan = decide(signals, connect_context(s))
            return {'scenario': s['id'], 'dataset_row': s['row'],
                    'text_sha256': hashlib.sha256(s['text'].encode()).hexdigest(),
                    'expected_development_lane': expected[s['id']],
                    'signals': signals, 'plan': plan,
                    'matches_development_expectation': plan['lane'] == expected[s['id']]}
    results = await asyncio.gather(*(run(s) for s in scenarios()))
    report = {'at': datetime.now(timezone.utc).isoformat(), 'model_requested': MODEL,
              'prompt_sha256': hashlib.sha256(PROMPT.encode()).hexdigest(),
              'scope': 'Sete cenários conhecidos usados no desenvolvimento, com contextos fictícios. Expectativas definidas por Codex; não é avaliação independente de elegibilidade ou qualidade operacional.',
              'results': results}
    target = Path(__file__).resolve().parent/'reports/fluxos-desenvolvimento.json'
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    for r in results:
        print(r['scenario'],r['signals']['source'],r['plan']['lane'], 'draft',bool(r['plan']['draft']))
    print('Relatório:',target)


if __name__ == '__main__': asyncio.run(main())
