# ChatGPT — prompt inicial (brainstorm → PRD)

**Contexto:** colei o README do Challenge 002 no ChatGPT, dei opiniões sobre o que já conhecia de ferramentas de atendimento e conversei sobre a abordagem. Depois enviei o prompt abaixo, escrito por mim, com a visão de produto. Ao final, pedi que ele gerasse um PRD bem explicativo com as regras de negócio. O resultado está em [`../../docs/PRD.md`](../../docs/PRD.md). Li o PRD inteiro antes de começar a construir.

> o que pensei: em construir uma interface grafica parecida com zendesk + botpress. basicamente queria mesclar funcionalidades principais dos dois, como analise por uma llm de baixo valor ou gratis (gpt modelos baixos que ja dao conta ou groq) para analise de sentimentos de cada conversa. implementacao de csat para analise de como o cliente reagiu aquela experiencia, abrindo para feedbacks, dashboards interativos dos ultimos 1d, 7d, 30d, 60d e 90d, mostrando as principais perguntas (fazer um apanhado sintatico, para perguntas similares nao serem repetidas). construcao de uma knowledge base que a cada pergunta nao respondida pelo nosso agent de ia ao usuario, ficaria marcado como pendente para que esse conhecimento seja inputado no nosso KB. escalar via upstream para humano e posteriormente downstream para agent em casos de necessidade, como finalizacao de compra, recompra, churn, etc, importante o processo de human in the loop. guardrails de entrada e saida, tanto para validar input e nos proteger conta prompt injection e entradas maliciosas, quanto guardrails de saida com disclaimers para nos assegurar juridicamente e garantir que nosso sistema esteja dando boas respostas. eval com datasets robustos de entradas e saidas esperadas e analise das saidas da LLM para bater com o que é esperado e validar se faz sentido ou nao (a depender, validar com prompt engineer os direcionamentos). MCP para colocarmos tools separadas do sistema principal, tanto por uma questao de single responsability quanto para reutilizacao por N sistemas e N agents que possamos ter que se beneficiar de funcionalidades parecidas. um sistema com essa robustez ja garante que grande parte do desafio consiga ser feito!

## Como cada ideia virou produto

| Ideia do prompt | Onde está no app |
|---|---|
| Interface Zendesk + Botpress | `/inbox` (Smart Inbox em 3 colunas) + `/simulador` (emulador no console) + `/portal` (widget conversacional) |
| LLM barata (GPT mini / Groq) para sentimento | Cascata em `src/lib/ai/llm.ts` (Groq Llama 3.1 8B → 3.3 70B) sobre um tier local gratuito |
| CSAT com feedback | Widget de CSAT no portal após a resolução; dashboard CSAT × decisão do gate |
| Dashboards 1d/7d/30d/60d/90d | `/dashboard` com filtro de período e comparação com o período anterior |
| Agrupar perguntas similares | Clustering de gaps (single-linkage, cosseno ≥ 0,4) e top assuntos |
| KB que marca perguntas não respondidas como pendentes | `kb_gaps` → `/knowledge` → "Aprovar conhecimento" → artigo |
| Upstream/downstream, human in the loop | "Assumir" / escalonamento automático pelo gate; "Devolver para IA" |
| Guardrails de entrada e saída + disclaimers | `src/lib/ai/guardrails.ts` |
| Evals com datasets robustos | `/evals`, `npm run eval`, golden sets (D2 test + comportamental) |
| MCP para tools separadas | `mcp/server.ts` (7 tools) |
