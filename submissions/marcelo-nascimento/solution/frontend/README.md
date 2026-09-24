# Lead Scorer

Frontend React/Vite da aplicação de Lead Scoring. A regra de scoring, as justificativas e a autenticação são implementadas exclusivamente no backend Node.js.

## Execução

A partir da pasta `solution`:

```bash
cd solution
docker compose up --build
```

Serviços:

- interface: `http://localhost:5173`
- API: `http://localhost:3000/api`
- health check: `http://localhost:3000/api/health`

Usuário inicial exigido pela SPEC-002:

```text
admin@leadscore.local
lead@teste55
```

Altere a senha inicial após o primeiro acesso. O seed é identificado por uma chave estável e não é recriado quando o e-mail ou a senha são alterados.

## Validação

```bash
cd solution/backend
npm ci
npm test
npm run typecheck
npm run build

cd ../frontend
npm ci
npm run lint
npm run build
```

O frontend recebe score, fatores, evidências e justificativa pela API. O score representa a força relativa das evidências históricas de aderência e não é uma probabilidade de fechamento.
