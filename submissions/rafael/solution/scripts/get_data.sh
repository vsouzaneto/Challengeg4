#!/usr/bin/env bash
# Baixa o dataset do Kaggle (API pública, exige ~/.kaggle/kaggle.json) e confere o sha256 do CSV usado na análise.
set -euo pipefail

DATASET="omenkj/social-media-sponsorship-and-engagement-dataset"
CSV="social_media_dataset.csv"
SHA256="693a2df6e609d1c099f3430d9a5b894b224fe12b2420c0d93e6defe90d15f18e"
OUT_DIR="${1:-data/raw}"
CREDENTIALS="${KAGGLE_CONFIG_DIR:-$HOME/.kaggle}/kaggle.json"

[ -f "$CREDENTIALS" ] || { echo "Falta $CREDENTIALS (Kaggle → Settings → Create New Token)." >&2; exit 1; }
user=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['username'])" "$CREDENTIALS")
key=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['key'])" "$CREDENTIALS")

mkdir -p "$OUT_DIR"
zip=$(mktemp --suffix=.zip)
trap 'rm -f "$zip"' EXIT
curl -sfL -u "$user:$key" -o "$zip" "https://www.kaggle.com/api/v1/datasets/download/$DATASET"
python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extract(sys.argv[2], sys.argv[3])" "$zip" "$CSV" "$OUT_DIR"

echo "$SHA256  $OUT_DIR/$CSV" | sha256sum -c - || { echo "Aviso: o CSV mudou desde a análise; os números podem diferir." >&2; exit 2; }
