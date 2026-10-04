#!/usr/bin/env bash
# Baixa os datasets do Kaggle (download público, sem credenciais) para analysis/data/.
# O Dataset 1 já está versionado em app/data/raw/ (é usado pelo seed do app).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p data && cd data
curl -sL -o ds2.zip https://www.kaggle.com/api/v1/datasets/download/adisongoh/it-service-ticket-classification-dataset
unzip -o -q ds2.zip && rm ds2.zip
ls -la
