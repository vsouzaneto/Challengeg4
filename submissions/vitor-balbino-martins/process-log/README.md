# Process log

## Objetivo

Construir um diagnóstico operacional de suporte e um protótipo de automação
responsável para classificação, roteamento e priorização de tickets.

## Ferramentas utilizadas

- OpenAI API para extração e consolidação dos achados operacionais.
- Python/FastAPI para a API e regras de negócio.
- PostgreSQL/PGVector e embeddings locais para o fluxo RAG.
- HTML, CSS e JavaScript sem build para o frontend.
- Tracing local em `logs/ai_traces.jsonl` para registrar modelo, latência, tokens,
  prompt, resposta e erros sem enviar dados de observabilidade a terceiros.

## Iterações e decisões

1. A camada de agentes foi migrada de Ollama para OpenAI, mantendo o contrato
   JSON utilizado pelos serviços existentes.
2. O processamento foi mantido em lotes para evitar enviar a base inteira em uma
   única chamada e para permitir cancelamento e acompanhamento do relatório.
3. O parser de auditoria foi ajustado para achatar respostas aninhadas, como
   `gargalos.combos_com_tempo_maior_resolucao` e fatores de satisfação por canal
   ou prioridade.
4. O frontend passou a preservar o relatório no `localStorage` e incorporar
   apenas campos ausentes quando uma nova resposta chega.
5. O tracing originalmente planejado com LangSmith foi substituído por registro
   local para garantir que os dados de monitoramento não sejam enviados a um
   servidor externo.

## Validações

- Endpoint de health check retornando `200`.
- Chamadas à OpenAI observadas com respostas `200`.
- Identificação e correção do caso em que a API retornava achados, mas a tela
  exibia bloco vazio por incompatibilidade de formato.
- Frontend servido por HTTP em `http://localhost:5500` para suportar ES modules.
