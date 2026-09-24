# syntax=docker/dockerfile:1.7
# Build context must be the submission root (docs-site includes ../docs, ../process-log, ../README.md).
FROM python:3.12-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /uvx /bin/
ENV UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /src/solution/docs-site
COPY solution/docs-site/pyproject.toml solution/docs-site/uv.lock ./
RUN uv sync --frozen --no-dev
COPY README.md CLAUDE.md /src/
COPY docs /src/docs
COPY process-log /src/process-log
COPY solution/README.md /src/solution/README.md
COPY solution/docs-site /src/solution/docs-site
RUN uv run mkdocs build --strict

FROM nginx:alpine AS runtime
COPY --from=build /src/solution/docs-site/site /usr/share/nginx/html
RUN printf 'server { listen 80; root /usr/share/nginx/html; index index.html; add_header X-Content-Type-Options nosniff always; add_header X-Frame-Options SAMEORIGIN always; location / { try_files $uri $uri/ $uri.html =404; } }\n' > /etc/nginx/conf.d/default.conf
EXPOSE 80
HEALTHCHECK --interval=15s --timeout=3s --retries=3 CMD wget -qO- http://127.0.0.1/ >/dev/null || exit 1
