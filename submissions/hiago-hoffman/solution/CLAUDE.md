@AGENTS.md

# intento-product-starter

Starter oficial da Intento Tech para produto: SaaS, sistemas administrativos, CRM, ERP, dashboards, backoffice e portais. Next.js 16 (App Router), TypeScript, Tailwind CSS v4, shadcn/ui sobre Base UI.

É uma **fundação**, não uma aplicação. Nada aqui é específico de um produto.

## Workflow principal: `intento-product-design`

Todo trabalho de UI neste repositório é produto. Sempre comece pela skill `intento-product-design`:

`intento-product-design` → pesquisa quando necessária (`mobbin-search`) → `shadcn` (skill + MCP) → implementação → Preview → testes de interação → refinamento.

- Comece pela estrutura (usuários, tarefas, entidades, jornadas, permissões, estados), não pela tela.
- **Não aplique experimentalismo visual de landing page** em telas operacionais. Clareza, densidade e consistência vêm primeiro.
- Páginas públicas de marketing não moram aqui: use o `intento-landing-starter`.

## shadcn é fundação, não identidade visual

shadcn entrega comportamento, acessibilidade e estrutura. **A identidade é de cada produto**: cores, tipografia, radius, densidade, ícones e navegação.

- Identidade entra por **tokens** em `src/app/globals.css` (`:root` / `.dark`), nunca por classes soltas nos componentes.
- Se existir `DESIGN.md` na raiz, seus tokens são normativos: aplique-os em `globals.css` e use só eles.
- Troca de tema: `npx shadcn@latest apply <preset> --only theme,font`.
- Tokens semânticos disponíveis: os do shadcn (`primary`, `muted`, `destructive`, `border`…) + `success` e `warning` para estados.
- Nunca cores cruas (`bg-blue-500`) nem `dark:` manual; use `bg-primary`, `text-muted-foreground`, `bg-success`.

## Consulte o shadcn antes de criar componentes

Antes de escrever qualquer componente de UI comum, **consulte o registry**. Não recrie o que já existe.

1. Já instalado? Veja `src/components/ui/`.
2. Existe no registry? `npx shadcn@latest search @shadcn -q "<termo>"` (ou o MCP do shadcn).
3. Leia a doc antes de usar: `npx shadcn@latest docs <componente>`.
4. Instale só o necessário: `npx shadcn@latest add <componente>`, depois leia os arquivos gerados.

Regras:
- Base **Base UI** (`@base-ui/react`, não Radix): triggers customizados usam `render`, não `asChild`. Navegação com aparência de botão usa `<Link className={buttonVariants()}>`: `Button` renderizando `Link` vira `role="button"` e perde a semântica de link.
- Toast é o `toast` de `@/components/ui/toast` (Base UI), não `sonner`: `toast.add({ type: "success", title })`.
- Não edite `src/components/ui/*` para um caso específico; use variants, composição e tokens.
- Rótulos acessíveis em inglês dos componentes `ui` (Close, Toggle Sidebar) foram traduzidos para pt-BR. Ao adicionar ou reinstalar componentes, traduza os novos.
- Formulários: React Hook Form + Zod + `Field`/`FieldGroup` (padrão em `src/app/(app)/_reference/item-form.tsx`).

## Estados são obrigatórios

Nenhuma tela ou componente com dados está pronto só com o happy path. Implemente e teste:

- **loading**: `Skeleton` no formato do conteúdo (`loading.tsx` por rota, `DataTable loading`). Ações usam `Spinner` + `disabled` no botão.
- **empty**: `Empty` com próxima ação. Diferencie "nada ainda" (CTA de criação) de "filtro sem resultado" (limpar filtros).
- **error**: `ErrorState` com "Tentar novamente"; `error.tsx` por segmento. Falha de ação dentro de Sheet/Dialog aparece no próprio overlay (`Alert destructive`), sem perder o que o usuário digitou; fora de overlays, `toast` de erro.
- **success**: `toast` de sucesso confirmando a ação; em exclusões, ofereça desfazer.

Considere também disabled, sem permissão, textos longos, zero e muitos registros.

## Validação final no Preview (obrigatória)

Não declare nada pronto sem validar no Preview integrado (`preview_start` com `product-starter`, `.claude/launch.json`):

1. rode a aplicação e percorra a jornada do início ao fim;
2. clique, preencha formulários, envie inválido e válido;
3. provoque cada estado (loading, empty, error, success);
4. confira o console (sem erros nem warnings de hidratação);
5. teste mobile (375px) quando fizer sentido;
6. rode `npm run lint` e `npm run build`.

## Estrutura

- `src/app/layout.tsx`: documento raiz + `Providers`.
- `src/app/(app)/`: área logada. `layout.tsx` (sidebar + topbar), `loading.tsx`, `error.tsx`.
- `src/app/(app)/_reference/` + `page.tsx`: **página de referência** dos padrões. Substitua pela primeira jornada real e apague a pasta.
- `src/app/not-found.tsx`, `src/app/global-error.tsx`: 404 e falha do root layout.
- `src/components/ui/`: shadcn (gerado pelo CLI).
- `src/components/`: composições do produto: `providers.tsx` (Toaster, TooltipProvider), `app-sidebar.tsx` (navegação), `page-header.tsx`, `data-table.tsx` (tabela com estados), `error-state.tsx`.
- `src/lib/`, `src/hooks/`: utilitários e hooks compartilhados.
- Novos contextos por route group, ex.: `(auth)` para login.

## Não incluído (adicione por projeto, quando houver necessidade)

Auth, banco/ORM, dark mode toggle (`next-themes`), ordenação/paginação/seleção de tabela (`@tanstack/react-table`), testes, monitoramento de erros.

## Comandos

- `npm run dev`: Preview (`.claude/launch.json`, porta 3000)
- `npm run build` / `npm run lint`
