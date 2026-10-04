# AI Support OS — app

**Demo:** https://ai-support-os.vercel.app · login `demo@g4.com.br` / `g4demo2026`

Next.js 16 + TypeScript + SQLite (libsql). Inbox estilo Zendesk, portal conversacional estilo Botpress, pipeline de IA com Human in the Loop, Knowledge Gaps, evals e servidor MCP.

## Rodar localmente

```bash
npm install
npm run seed     # cria data/app.db: 8.469 tickets reais do Dataset 1 processados pelo pipeline + KB + demo + evals
npm run dev      # http://localhost:3000
```

Login demo: `demo@g4.com.br` / `g4demo2026`, ou crie uma conta em `/signup`. O portal do cliente (público) fica em `/portal`.

| Script | O que faz |
|---|---|
| `npm run seed` | (Re)cria o banco a partir de `data/raw/customer_support_tickets.csv` |
| `npm run eval` | Roda os evals (480 tickets de teste do D2 + 58 casos comportamentais). **Exit 1** se houver automação insegura |
| `npm run mcp` | Servidor MCP (stdio) com 7 tools |
| `npm run build` | `seed` + `next build` |

## Variáveis de ambiente (todas opcionais)

| Variável | Efeito |
|---|---|
| `GROQ_API_KEY` (ou `LLM_API_KEY`) | Liga a cascata LLM (Groq, OpenAI-compatible). Sem ela, tudo roda no tier local |
| `LLM_BASE_URL`, `LLM_MODEL_FAST`, `LLM_MODEL_STRONG` | Outro provider/modelos (default: Groq `llama-3.1-8b-instant` / `llama-3.3-70b-versatile`) |
| `TURSO_DATABASE_URL`, `TURSO_AUTH_TOKEN` | SQLite gerenciado (persistência real na Vercel). Sem eles, cada instância serverless teria sua própria cópia em `/tmp` |
| `SESSION_SECRET` | Chave HMAC do cookie de sessão (obrigatória em produção) |

## Deploy na Vercel

1. Importe o repositório e defina **Root Directory** = `submissions/felipe-gigante/solution/app`.
2. Mantenha o build command padrão (`npm run build`, que já roda o seed).
3. Opcional: `GROQ_API_KEY` e `TURSO_*`.

Sem Turso, o `app.db` gerado no build é copiado para `/tmp` no cold start: cadastros e tickets novos valem enquanto a instância estiver quente (ok para demo). Com Turso: crie um banco vazio, rode **uma vez** `SEED_REMOTE=1 TURSO_DATABASE_URL=... TURSO_AUTH_TOKEN=... npm run seed` e configure as duas variáveis na Vercel (com elas definidas, o build não re-semeia).

## MCP

```bash
claude mcp add support-os -- npx tsx mcp/server.ts   # dentro desta pasta
```

Tools: `knowledge.search_articles`, `knowledge.list_gaps`, `knowledge.create_gap`, `support.classify_text`, `support.triage_ticket`, `support.get_ticket`, `support.ops_metrics`.

## Estrutura

```
src/lib/ai/        pipeline.ts (orquestrador + gate) · classifier.ts · sentiment.ts · risk.ts
                   priority.ts · kb.ts · guardrails.ts · llm.ts · text.ts
src/lib/           db.ts · auth.ts · tickets.ts (HITL, feedback, CSAT) · analytics.ts · evals.ts
src/app/(app)/     dashboard · diagnostico · inbox · knowledge · evals · arquitetura
src/app/portal/    portal do cliente (público)
data/generated/    classifier.json, métricas e diagnóstico (gerados por ../analysis)
data/raw/          Dataset 1 (Kaggle, CC0)
mcp/server.ts      servidor MCP
```

## Análise e treino (Python)

```bash
cd ../analysis
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
./download_data.sh            # Dataset 2 (Kaggle, download público)
python diagnostico.py         # → app/data/generated/diagnostico.json
python train_classifier.py    # → app/data/generated/classifier*.json + golden set
```
