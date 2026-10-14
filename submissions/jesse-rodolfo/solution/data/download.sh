#!/usr/bin/env bash
# Baixa os dois datasets do Kaggle para solution/data/raw/
# Requisitos: pip install kaggle, e o arquivo ~/.kaggle/kaggle.json com sua API key
# (Kaggle > Settings > API > Create New Token)
set -e
cd "$(dirname "$0")"
mkdir -p raw
kaggle datasets download -d suraj520/customer-support-ticket-dataset -p raw --unzip
kaggle datasets download -d adisongoh/it-service-ticket-classification-dataset -p raw --unzip
echo "Arquivos em raw/:"
ls -la raw/
