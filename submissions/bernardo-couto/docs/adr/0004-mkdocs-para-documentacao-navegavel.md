# ADR 0004 — MkDocs Material para documentação navegável

**Status:** aceito · **Data:** 2026-09-23

## Contexto
A documentação (setup, lógica, backtest, model card, API, design, segurança, limitações, ADRs, process log) é extensa e em Markdown. O pedido é navegação em HTML gerada do Markdown, com o Swagger incluído.

## Decisão
**MkDocs Material** (Python, mesma toolchain do projeto), com Mermaid para diagramas, `swagger-ui-tag` para embutir `openapi.json`, paleta e fontes do G4, `mkdocs build --strict`. Servido como estático pelo serviço `docs` do Compose.

## Alternativas
Docusaurus (Node; mais pesado), Sphinx (menos amigável para Markdown puro), GitHub Pages (fora do escopo de um PR de submissão).

## Consequências
Fonte única: os `.md` de `docs/`, `process-log/` e READMEs; nada duplicado à mão. Links quebrados falham o build.
