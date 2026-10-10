# Fonte dos dados

- **Dataset:** CRM Sales Predictive Analytics, de agungpambudi, no Kaggle (versão 1): https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics
- **Licença:** CC0 (domínio público), conforme o enunciado do desafio.
- **Arquivos:** `accounts.csv`, `products.csv`, `sales_pipeline.csv`, `sales_teams.csv` e `metadata.csv`, sem nenhuma alteração.
- **Integridade:** o arquivo `SHA256SUMS` traz o hash de cada um. Para conferir, rode, nesta pasta, `shasum -a 256 -c SHA256SUMS` (macOS) ou `sha256sum -c SHA256SUMS` (Linux). O teste `src/core/data.test.ts` faz a mesma conferência a cada `npm run check`.
- **Origem conferida em 09/10/2026:** os 5 arquivos são idênticos byte a byte aos do zip baixado do Kaggle (`archive.zip`, arquivos datados de 14/04/2024). O zip não é versionado. Detalhes em `../../process-log/01-revisao-inicial.md` (P3).

As correções, como "GTXPro" → "GTX Pro", são feitas na leitura, no código. Os arquivos originais não são alterados.
