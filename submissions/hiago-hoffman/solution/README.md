# intento-product-starter

Template base da Intento Tech para **produtos**: SaaS, dashboards, CRM, ERP, backoffice, portais e sistemas internos.

Next.js (App Router) + TypeScript + Tailwind CSS v4 + shadcn/ui (Base UI, estilo `base-nova`). Já vem com shell de aplicação (sidebar, header), tabela de dados, formulário com validação (react-hook-form + zod), estados de loading/erro/vazio e uma tela de referência em `src/app/(app)/_reference`.

> Este repositório é **infraestrutura reutilizável**. Não coloque aqui regra de negócio, marca, dados ou telas de um cliente específico. Isso vive no repositório do produto.

## Criar um novo projeto a partir dele

No GitHub: **Use this template → Create a new repository** (privado, com o nome do produto). Ou pelo terminal:

```bash
gh repo create nome-do-produto --private --template gandahiago/intento-product-starter --clone
```

O projeto novo nasce com **histórico próprio** (não é fork). Depois:

1. Renomeie em `package.json` (`"name"`) e em `src/app/layout.tsx` (metadata).
2. Use `src/app/(app)/_reference` como modelo das primeiras telas e apague-a quando não precisar mais.
3. Siga o workflow abaixo.

## Workflow da Intento (produto)

`intento-product-design` → pesquisa quando necessária → `shadcn` (skill + MCP, já configurado em `.mcp.json`) → implementação → Preview → testes de interação → refinamento.

- Comece pela estrutura: usuários, tarefas, entidades, jornadas, permissões e estados.
- Identidade entra por **tokens** em `src/app/globals.css`; se houver `DESIGN.md`, ele é normativo.
- Não edite `src/components/ui/*` para um caso específico: use variants e composição.
- Detalhes em `CLAUDE.md`. Processo completo em `PROJECT-CREATION.md`, na pasta principal da Intento.

## Rodar localmente

```bash
npm install
npm run dev
```

Abre em http://localhost:3000.

## Deploy

Deploy independente por produto (Cloudflare Pages/Workers ou Vercel, conforme o backend). Ver `DOMAINS.md` na pasta principal da Intento.
