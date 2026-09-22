"""Cliente mínimo; nunca registra credenciais ou cabeçalhos."""
import httpx
from triage_core import key_from_env


async def chat(messages, model='anthropic/claude-sonnet-5', max_tokens=2200, json_mode=False):
    key = key_from_env('OPENROUTER_API_KEY')
    if not key:
        raise ValueError('OPENROUTER_API_KEY não configurada')
    payload = {'model': model, 'messages': messages, 'temperature': 0, 'max_tokens': max_tokens}
    if json_mode:
        payload['response_format'] = {'type': 'json_object'}
    async with httpx.AsyncClient(timeout=150, follow_redirects=False) as client:
        response = await client.post('https://openrouter.ai/api/v1/chat/completions', json=payload,
                                     headers={'Authorization': 'Bearer ' + key})
        if response.status_code != 200:
            raise ValueError(f'OpenRouter HTTP {response.status_code}')
        body = response.json()
    choice = body['choices'][0]
    if choice.get('finish_reason') != 'stop':
        raise ValueError('Resposta incompleta; não apresentar como concluída')
    return {'model': body.get('model'), 'id': body.get('id'), 'content': choice['message']['content'],
            'usage': body.get('usage', {})}
