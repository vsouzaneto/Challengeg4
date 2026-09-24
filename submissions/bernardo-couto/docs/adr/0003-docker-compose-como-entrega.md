# ADR 0003 — Docker Compose como forma de entrega

**Status:** aceito · **Data:** 2026-09-23

## Contexto
O avaliador vai clonar e seguir o README. A stack tem Python, Node e (para o pipeline) JVM. Cada pré-requisito no host é um ponto de falha.

## Decisão
`docker compose up` sobe `api`, `web` e `docs` com artefatos commitados (`gold/scores/as_of=2017-12-31`, `models/latest`) — sem JDK, sem chave. Perfil `pipeline` (imagem `eclipse-temurin:17` + uv) executa os jobs Spark para quem quiser reproduzir o treino e o scoring.

## Consequências
Docker vira pré-requisito único do caminho curto; imagens multi-stage, slim, não-root, com `HEALTHCHECK`; `make up|pipeline|test|docs` como atalhos. O caminho sem Docker permanece documentado (uv + npm).
