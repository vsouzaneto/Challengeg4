# Docs site (MkDocs Material)

```bash
uv sync
uv run mkdocs serve -a 0.0.0.0:8001   # http://localhost:8001
uv run mkdocs build --strict
```

Fonte única: os `.md` em `docs/`, `process-log/` e os READMEs da submissão e de `solution/`, expostos
por symlinks em `docs/` (`docs → ../../../docs`, `process-log → ../../../process-log`) e por
`include-markdown` nas páginas Início e Como rodar. Nenhum conteúdo é duplicado à mão. Chat exports
ficam fora do site (`exclude_docs`). A imagem Docker (`Dockerfile`, contexto = raiz da submissão)
copia só esses caminhos — uma página nova que inclua arquivo fora deles quebra o build da imagem.
