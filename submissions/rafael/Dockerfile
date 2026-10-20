# Reproducible image: pinned Python + libraries, verified CSV, models trained at build time and checked against the reference.
# Build (from submissions/rafael), with the CSV in data/raw/ or a Kaggle token passed as a secret:
#   docker build -t g4-social .                                                  # CSV already in data/raw/
#   docker build --secret id=kaggle,src=$HOME/.kaggle/kaggle.json -t g4-social .  # downloads the CSV
# Run:     docker run --rm -p 8000:8000 g4-social
# Verify:  docker run --rm g4-social python solution/reproducibility/verify.py --retrain --tests
FROM python:3.14.3-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1 \
    MPLBACKEND=Agg PYTHONHASHSEED=0
# curl: dataset download · libgomp1: OpenMP runtime used by LightGBM/XGBoost
RUN apt-get update && apt-get install -y --no-install-recommends curl libgomp1 && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 app

WORKDIR /app
# requirements.lock pins every package (direct and transitive) to the versions of the tested environment.
COPY requirements.txt requirements.lock ./
RUN pip install -r requirements.lock

# Only what runs goes into the image: packaging/test config and solution/ (code, CLIs, tests, verifier). Docs and notebooks stay out.
COPY pyproject.toml pytest.ini ./
COPY solution/src solution/src
COPY solution/cli solution/cli
COPY solution/scripts solution/scripts
COPY solution/reproducibility solution/reproducibility
COPY solution/tests solution/tests
RUN pip install --no-deps -e .

# Data: copy the CSV from the build context if present, otherwise download it with the Kaggle secret (never stored in the image).
RUN --mount=type=bind,target=/context --mount=type=secret,id=kaggle,target=/root/.kaggle/kaggle.json \
    mkdir -p data/raw && if [ -f /context/data/raw/social_media_dataset.csv ]; \
    then cp /context/data/raw/social_media_dataset.csv data/raw/; else bash solution/scripts/get_data.sh data/raw; fi

# Train every model into solution/models and fail the build if any result differs from the reference (the CSV sha256 is checked too).
RUN social-web --build-only && python -W ignore solution/reproducibility/verify.py && chown -R app:app /app

USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=90s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4)"
CMD ["social-web", "--host", "0.0.0.0", "--port", "8000"]
