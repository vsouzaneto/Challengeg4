# Fila de Prioridades — Classificador de Leads

Aplicação Streamlit funcional para o Challenge 003. Ela dá ao time comercial duas filas: **quem abordar** em Prospecção e **onde aumentar a atenção** em Em negociação. A interface tem filtros por responsável, gestor, região, estágio e pontuação, além de detalhe explicável por oportunidade e exportação CSV.

## Como executar

1. Baixe `accounts.csv`, `products.csv`, `sales_teams.csv` e `sales_pipeline.csv` do dataset [CRM Sales Predictive Analytics](https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics).
2. Na raiz do fork, instale as dependências e indique onde estão os CSVs:

```powershell
python -m pip install -r submissions\gabriel-moreira-beltrami\solution\requirements.txt
$env:LEAD_SCORER_DATA_DIR = "C:\caminho\para\os\csvs"
python -m streamlit run submissions\gabriel-moreira-beltrami\solution\app.py
```

Abra a URL exibida pelo Streamlit, normalmente `http://localhost:8501`. Se os CSVs estiverem em `data/raw/` na raiz do fork, a variável de ambiente não é necessária.

## Como usar

1. Aplique os filtros no painel **Meu foco**.
2. Escolha **Priorizar prospecção** para o primeiro contato ou **Aumentar atenção** para negócios ativos.
3. Use o círculo no início de uma linha para abrir o detalhe abaixo da tabela.
4. Leia a justificativa e os componentes antes de agir; a pontuação ordena a fila, não substitui a qualificação comercial.

## Lógica de pontuação

A **pontuação de ação (0–100)** soma:

1. **Valor esperado de catálogo:** preço de catálogo × taxa histórica de vitória suavizada.
2. **Força da evidência:** cobertura de negócios fechados para o produto. Isso reduz a influência do raro `GTK 500`, que tem preço alto e pouco histórico.
3. **Contexto da conta:** uma conta vinculada recebe um pequeno bônus operacional.

Ela não usa `close_date`, `close_value` ou o resultado final para pontuar oportunidades abertas. Também exclui identidade da pessoa vendedora e porte/idade da empresa, pois esses campos não adicionaram sinal útil depois de controlar por produto.

## Limitações

O dataset não possui data de criação do lead, mudança de estágio, data de snapshot, interações, desconto, origem do lead ou momento de atribuição. Por isso não mede esforço comercial, causalidade ou inatividade. Antes de criar um alerta de espera, o CRM deve registrar `created_at`, `stage_changed_at` e `last_activity_at`.

Veja a [síntese da análise](docs/analysis-summary.md) para a estrutura dos dados e os achados que sustentam a regra.
