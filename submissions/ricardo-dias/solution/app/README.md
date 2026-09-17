# Suporte Inteligente — protótipo (Next.js)

Interface e API do Challenge 002: diagnóstico, triagem de tickets com política de roteamento, evidências do modelo e proposta de automação.

**Publicado:** https://g4-challenge-002-ricardo-barao.vercel.app · Visão geral da submissão: [`../../README.md`](../../README.md)

## Rodar localmente

Requisitos: Node 24.

```bash
npm install
npm run dev          # http://localhost:3000
```

Não precisa de Kaggle nem de Python: o modelo e os relatórios já estão versionados em `data/`.

## Scripts

| Comando | O que faz |
|---|---|
| `npm run dev` | Servidor de desenvolvimento |
| `npm test` | Vitest: paridade TypeScript × scikit-learn no conjunto de teste, formato do modelo, cada ramo da política de roteamento, validação das APIs, bloqueio de rascunho no servidor, calculadora e componentes da UI |
| `npm run lint` | ESLint |
| `npm run build` | Build de produção (inclui checagem de tipos) |
| `npm run eval:routing` | Mede o roteamento completo com as funções da API e grava `data/routing_eval.json` (requer os artefatos de `../analysis/artifacts`) |

Para regenerar tudo a partir dos CSVs (análise → modelo → avaliação → diagnóstico → docs → testes): `bash ../pipeline.sh`.

## Variáveis de ambiente

Todas são opcionais. Sem nenhuma delas, a classificação, o roteamento e a avaliação em lote funcionam normalmente.

| Variável | Efeito |
|---|---|
| `DRAFTS_ENABLED=true` | Liga o rascunho de resposta com LLM. Sem ela, `/api/draft` responde 503 (como no link público, para não gerar custo) |
| `AI_GATEWAY_API_KEY` | Credencial do Vercel AI Gateway, exigida junto com `DRAFTS_ENABLED=true` fora da Vercel |
| `DRAFT_MODEL` | Modelo do rascunho (padrão: `anthropic/claude-haiku-4.5`) |

## Estrutura

```
app/                 páginas: / (diagnóstico), /triagem, /modelo, /proposta
app/api/classify     POST { text } ou { texts: [...] } → categoria, confiança, rota e motivo
app/api/sample       GET ?n= → tickets aleatórios do conjunto de TESTE
app/api/draft        POST { text } → rascunho em streaming; política reaplicada no servidor
components/          UI (e testes de UI em components/__tests__)
lib/classifier.ts    inferência TF-IDF + regressão logística e política de roteamento (decideRoute)
lib/policy-rules.json regras escritas à mão (termos de escalação, categorias sempre humanas)
lib/model-schema.ts  validação do model.json (versão e formato) ao carregar
lib/validation.ts    limites e mensagens de erro das APIs (400/413, sem cortes silenciosos)
lib/waste.ts         calculadora do cenário (espelho do Python, com teste de igualdade)
data/                artefatos gerados pela análise; não editar à mão
tests/               testes de backend
```

## Garantias que os testes verificam

- A inferência em TypeScript reproduz rótulo e confiança do scikit-learn em todo o conjunto de teste.
- A política da API concorda 100% com a réplica usada para escolher os limiares.
- Um ticket escalado nunca aciona o provedor de LLM, mesmo se o cliente forjar a categoria.
- Chamada unitária e em lote retornam o mesmo resultado para o mesmo texto.
- Entradas inválidas ou acima do limite são recusadas com mensagem clara, nunca truncadas.

## Deploy

Vercel, com Root Directory em `solution/app`. O `vercel.json` fixa o framework Next.js (sem ele, um projeto criado pela CLI pode ficar com o preset "Other" e responder 404). Os JSONs lidos em tempo de execução entram no bundle via `outputFileTracingIncludes` (`next.config.ts`).

> `AGENTS.md` e `CLAUDE.md` nesta pasta são gerados pelo próprio Next.js 16 com orientações para agentes de código.
