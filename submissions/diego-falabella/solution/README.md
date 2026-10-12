# Setup

## Ferramenta (sem instalação)
Abra `dashboard/index.html` no navegador (duplo clique). Já vem com o dataset do challenge pré-processado.
Para analisar outro export, use "Choose File" e selecione um CSV com as colunas
`platform, content_type, content_category, is_sponsored, follower_count, views, likes, shares, comments_count` (+ opcional `creator_id`).
Tudo roda localmente no navegador.

## Reproduzir a auditoria
```bash
pip install -r analysis/requirements.txt
# baixe social_media_dataset.csv do Kaggle (não está no repositório — 23 MB, licença MIT)
python analysis/run_audit.py caminho/para/social_media_dataset.csv --out analysis/outputs
```
Saída: `summary.json`, `segments.csv`, 5 figuras SVG e o veredito no terminal (≈1 min).

## Reconstruir o dashboard com outro dataset embutido
```bash
python dashboard/build_dashboard.py caminho/para/social_media_dataset.csv
```

## Testar a ferramenta nos dois cenários
```bash
pip install playwright && playwright install chromium
cd dashboard && python test_dashboard.py
```
