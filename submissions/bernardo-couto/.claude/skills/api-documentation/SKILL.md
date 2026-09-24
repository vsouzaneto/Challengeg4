---
name: api-documentation
description: Padrões de documentação da API (FastAPI/OpenAPI 3.1 exemplar — tags, exemplos, erros, versionamento, operation_id, exportação de openapi.json) e da documentação navegável em HTML gerada a partir de Markdown com MkDocs Material (estrutura, nav, Mermaid, inclusão do Swagger). Use ao criar/alterar endpoints, o site de docs ou tipos TS gerados do OpenAPI.
user-invocable: false
---

# API e documentação navegável

## OpenAPI exemplar (FastAPI)

- `FastAPI(title="Lead Scorer API", version="1.0.0", summary=..., description=<markdown pt-BR com contexto de negócio, como o score é calculado em 5 linhas, link para docs>, openapi_tags=[{name, description}], contact, license_info={"name": "MIT"}, servers=[...])`.
- Toda rota: `summary`, `description` (markdown), `response_model`, `responses={404: {...}, 422: {...}, 503: {...}}`, `operation_id` estável em snake_case (usado na geração de tipos TS), `tags`.
- Modelos Pydantic v2 com `Field(description=..., examples=[...])` e `model_config = ConfigDict(json_schema_extra={"examples": [...]})`. `ScoredDeal` é a fonte única do contrato.
- Erros no formato `{"error": {"code": "...", "message": "...", "hint": "..."}}`; 503 quando artefatos ausentes com `hint` contendo o comando para gerar.
- Paginação `?limit&offset` + `total`; ordenação `?sort=-priority_score`; filtros documentados com enum quando o domínio é fechado (`deal_stage`, `tier`, `regional_office`).
- Versionamento: prefixo `/api/v1`; `X-Model-Version` e `X-As-Of` como headers de resposta.
- Exportar: `python -m api.export_openapi > docs-site/docs/api/openapi.json` no build; validar com `uvx openapi-spec-validator`.
- Frontend: `npx openapi-typescript http://localhost:8000/openapi.json -o src/api/schema.d.ts`.

## Documentação navegável (MkDocs Material)

- `solution/docs-site/mkdocs.yml`: `site_name: Lead Scorer — Documentação`, tema `material` com paleta custom (navy `#001F35`, dourado `#B9915B`, fontes Manrope/Libre Baskerville via `extra_css`), `nav` explícita:
  1. Início (executive summary) · 2. Como rodar · 3. Arquitetura (Mermaid) · 4. Dados e qualidade · 5. Lógica de scoring e backtest · 6. Pipeline de ML e model card · 7. API (Swagger embutido + guia) · 8. Design e UX · 9. Segurança · 10. Limitações · 11. ADRs · 12. Process log.
- Plugins: `search`, `mermaid2` (ou `pymdownx.superfences` com `custom_fences` para mermaid), `swagger-ui-tag` para embutir `openapi.json`; `pymdownx.tabbed`, `admonition`, `tables`.
- Os `.md` de `docs/` e `process-log/` são a fonte; o site usa `docs_dir` apontando para uma pasta com symlinks ou o plugin `monorepo`/`include-markdown` — nunca duplicar conteúdo à mão.
- Diagramas **sempre em Mermaid** (fenced ```mermaid); nada de ASCII art para arquitetura.
- Servido por `mkdocs serve` em dev e como estático (nginx) no serviço `docs` do Compose; `mkdocs build --strict` no CI local (links quebrados falham).

## Checklist

- [ ] `/docs` abre com título, descrição, tags e exemplos em todas as rotas
- [ ] `openapi.json` válido e exportado
- [ ] tipos TS gerados e commitados
- [ ] `mkdocs build --strict` sem avisos
- [ ] Mermaid renderiza em todos os diagramas
