# syntax=docker/dockerfile:1.7
# Spark 3.5 needs JDK 17/21; this image is used only by the `pipeline` Compose profile.
# Build context must be solution/.
FROM eclipse-temurin:17-jdk-jammy
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /uvx /bin/
ENV UV_LINK_MODE=copy UV_PYTHON_INSTALL_DIR=/opt/uv/python UV_PYTHON=3.12 \
    PYTHONUNBUFFERED=1 JAVA_HOME=/opt/java/openjdk UV_NO_SYNC=1
RUN apt-get update && apt-get install -y --no-install-recommends make procps \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app && useradd --system --gid app --home /app app
WORKDIR /app
COPY --chown=app:app shared/lead_scorer_contracts /app/shared/lead_scorer_contracts
COPY --chown=app:app pipeline /app/pipeline
COPY --chown=app:app Makefile /app/Makefile
RUN uv python install 3.12 && cd pipeline && uv sync --frozen --no-dev && chown -R app:app /app /opt/uv
USER app
CMD ["make", "-C", "/app", "pipeline"]
