# Dados RavenStack (Kaggle)

**Dataset:** [SaaS Subscription & Churn Analytics](https://www.kaggle.com/datasets/rivalytics/saas-subscription-and-churn-analytics-dataset) (MIT)

## Download

**Windows:** na pasta `submissions/felipe`, rode `start.bat` — ele tenta baixar automaticamente se os CSVs não estiverem aqui.

Manual:

```bash
python -m pip install kaggle
python -m kaggle auth login   # ou KAGGLE_API_TOKEN
python -m kaggle datasets download -d rivalytics/saas-subscription-and-churn-analytics-dataset -p . --unzip
```

Arquivos esperados:

- `ravenstack_accounts.csv`
- `ravenstack_subscriptions.csv`
- `ravenstack_feature_usage.csv`
- `ravenstack_support_tickets.csv`
- `ravenstack_churn_events.csv`

Os CSVs **não** devem ir para o git em forks que respeitam `.gitignore`; mantenha localmente e documente o hash/tamanho em `solution/outputs/data_manifest.json` (gerado pelo pipeline).
