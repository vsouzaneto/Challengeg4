# Decision Gate

**App no ar:** https://decision-social-doug.streamlit.app · health check: https://decision-social-doug.streamlit.app/healthz

Ferramenta do processo redesenhado (`docs/process/03-to-be.md`). Quatro abas, na ordem do ciclo:

| Aba | Etapa do processo | O que faz |
|---|---|---|
| 1 · Os dados servem? | Gate 0 | Roda as 11 regras do contrato de dados (`src/audit/health.py`). O arquivo do challenge é reprovado em 9 |
| 2 · Painel com margem de erro | Leitura | Cada grupo contra o resto, com n, IC 95%, p ajustado (BH) e veredito contra a régua de ±1 p.p. |
| 3 · Aprovar patrocínio | Gate 1 | Aponta campos faltantes, calcula as vendas para empatar e o tamanho do teste. A aprovação é humana |
| 4 · Fechar ciclo de 30 dias | Decisão | Sugere Escalar, Replicar, Iterar ou Parar pela regra pré-registrada (`src/decision/rules.py`) |

Não usa API de IA: funciona sem chave e sem custo.

## Rodar localmente
```bash
cd submissions/douglas-franca
uv sync
uv run python scripts/download_data.py      # opcional: sem ele, o app baixa o dataset ao abrir
uv run streamlit run app/streamlit_app.py
```

## Publicar (Streamlit Community Cloud)
1. Entrar em share.streamlit.io com a conta GitHub `douglasfrannca`.
2. **Create app** → repositório `douglasfrannca/ai-master-challenge`, branch `submission/douglas-franca`.
3. **Main file path:** `submissions/douglas-franca/app/streamlit_app.py`.
4. **Advanced settings:** Python 3.12. As dependências vêm de `app/requirements.txt`.
5. Health check: `https://<app>.streamlit.app/healthz` responde `{"status":"ok"}`.

## De onde vêm os dados
O dataset do challenge **não é versionado**. `src/app_data.py` usa `data/raw/` se o arquivo já foi baixado; senão baixa do Kaggle na primeira abertura (`kagglehub`, sem login, ~5 s a frio) e guarda em cache. O mesmo arquivo alimenta a análise, então o painel mostra exatamente os números dos relatórios.

## Arquivos em `assets/`
| Arquivo | Origem |
|---|---|
| `exemplo_sintetico_contrato_de_dados.csv` | **Fictício.** Mostra um arquivo instrumentado que passa no Gate 0 |
| `exemplo_sintetico_resultado_teste.csv` | **Fictício.** Resultado de um teste de dois braços para a aba 4 |
