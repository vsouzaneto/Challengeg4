# Rankio — notas técnicas da solução

Para quem for dar manutenção. O setup, a lógica de priorização e as limitações estão no [README da submissão](../README.md); as decisões, em [docs/architecture.md](../docs/architecture.md); os critérios de aceite, em [docs/prd.md](../docs/prd.md).

## Camadas

| Camada | O que faz | Onde |
| --- | --- | --- |
| Núcleo Python (pandas) | Carga, normalização, grupos, ordem e motivos em código; funções puras, sem web e sem texto de tela. Política (limites, faixas, termos proibidos) em `policy.py` | `leadscorer/` |
| CLI | `check-data`, `list --seller` (texto ou `--json`) e `explain --id`; escreve os textos a partir dos códigos (`cli_text.py`) e imprime no terminal, sem gerar CSV | `python -m leadscorer` |
| API FastAPI | `GET /api/meta`, `/api/sellers`, `/api/sellers/{seller}/pipeline`, `/api/pipeline?manager=&office=`, `/api/rules`, `/api/evidence`, `/api/intelligence` e `/api/intelligence/deals`; respostas tipadas (pydantic, descritas em `/docs`); erros 404, 422 e 503 com `code`, `params` e `detail` | `api/` |
| Tela Next.js (TypeScript) | Cinco páginas (Carteira, Equipe, Inteligência, Evidência e Como funciona). Valida cada resposta contra o contrato e escreve os textos a partir dos códigos (`copy/pt-BR.ts`); a priorização assistida roda aqui (`lib/assisted/`) | `web/` |

CLI, API e tela consomem o mesmo payload, e a lista é idêntica nas três saídas (testado para os 35 vendedores). A tela não calcula número de negócio: só formata.

## Contrato entre back e front (ADR-004)

O back entrega códigos, parâmetros e números (`reasons: [{code, role, params}]`, `next_action`, `ordering`); o front decide como dizer. O schema fica em `web/contract/openapi.json`, e o front gera dele os tipos e a validação zod. Versão atual: **7**.

- **v4:** evidência, regras e resumo por vendedor.
- **v5:** regra A (ADR-006), com o grupo Acompanhar, os dois limites e só os motivos que decidem.
- **v6:** Inteligência comercial (ADR-007), com duas rotas novas.
- **v7:** nova ordem dos grupos (ADR-009), orientação de verificação e contexto da idade (ADR-008). A priorização assistida (ADR-010) não muda o contrato.

**Quando o contrato mudar** (campo ou código novo em `api/schemas.py` ou `leadscorer/codes.py`), regenere os artefatos do front; os testes dos dois lados falham se algum ficar desatualizado:

```bash
.venv/bin/python scripts/export_openapi.py     # web/contract/openapi.json
.venv/bin/python scripts/export_fixtures.py    # web/tests/fixtures/ (dados sintéticos)
cd web && npm run contract                     # web/lib/contract/ (tipos e validação zod)
.venv/bin/python scripts/backtest.py           # regrava a evidência servida em /api/evidence
```

Os primitivos do shadcn ficam em `web/components/ui/` e entram pela CLI fixada, sem que ela vire dependência: `cd web && npx shadcn@4.21.1 add <componente>`.

## Testes

- **Back (`pytest`, 221):** reconciliação das junções, partição dos grupos, invariância (embaralhar fechadas e incluir venda futura não muda nada), explicações reconstruídas a partir dos códigos, vocabulário proibido, paridade núcleo = CLI = API. Sem os CSVs, os testes que dependem dos dados reais pulam com aviso.
- **Front (`vitest`, 284 + `tsc`):** contrato contra respostas sintéticas, cobertura de textos, contraste dos tokens (AA nos dois temas), regra "só shadcn" e a política da priorização assistida. Não precisam da API nem dos CSVs.

## Desvios em relação ao plano

- A CLI imprime no terminal, sem gerar CSV.
- A tela usa Tailwind v4 e componentes do shadcn, sem ESLint, com `agentRules: false` em `next.config.mjs` para o `next dev` não criar um `AGENTS.md`. O `next-env.d.ts` é gerado pelo `next dev` e não vai para o repositório.
- O CSS de que os primitivos dependem fica copiado em `web/app/shadcn.css` (MIT), para não trazer as 34 dependências da CLI do shadcn. As dependências novas estão fixadas em versões publicadas há pelo menos 14 dias.
- Ferramentas do front escolhidas para rodar em Node 22.12: Vitest com Vite 7 fixado (o Vite 8 não trouxe o binário nativo nesta máquina), jsdom 28 e `@hey-api/openapi-ts` 0.95.
- A validação do `as_of` fica na entrada (CLI e API), e o núcleo aceita qualquer data; assim, o teste de vazamento com uma venda futura (AC-1.10) não conflita com o `as_of` mínimo.
- A API carrega os dados uma vez e calcula a lista a cada chamada (cerca de 25 ms). A evidência é o resultado gravado de `scripts/backtest.py`: não se recalcula quando os dados mudam, e a página avisa quando o resultado não veio dos CSVs auditados.
