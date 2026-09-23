# Pesquisa técnica — Challenge 002

Data: 2026-09-21

## Regra Zero

### Interface local

| Candidato | Prova consultada | Adequação | Decisão |
|---|---|---|---|
| Streamlit | Documentação oficial de `st.navigation`, formulários, tabelas e `st.download_button`; projetos de suporte no GitHub; relatos de prototipagem no Reddit | Um processo Python, componentes nativos suficientes e execução local simples | **Escolhido para reprodução mínima** |
| Gradio Blocks | Documentação oficial de layouts, estado, tabelas e downloads | Excelente para demos centradas em inferência, menos natural para fila operacional multipágina e scorecard | Não escolhido |
| Plotly Dash | Documentação oficial de callbacks, DataTable e downloads | Flexível, mas exige mais callbacks e estado para o mesmo MVP | Não escolhido |

O Reddit foi tratado como evidência de uso, não como autoridade técnica. Os relatos convergem em dois pontos úteis: Streamlit acelera protótipos internos e perde adequação quando layout, estado granular ou escala viram requisitos de produto. Esses limites são aceitáveis porque o challenge exige um protótipo local, sem autenticação, deploy ou multiusuário.

### Classificação, confiança e recuperação

| Necessidade | Candidatos | Escolha inicial |
|---|---|---|
| Classificação de texto | `DummyClassifier`; TF-IDF + `MultinomialNB`; TF-IDF + `LogisticRegression`; TF-IDF + `LinearSVC` | Comparar os quatro por CV; escolher por macro-F1 e simplicidade, sem escolher pelo teste congelado |
| Calibração | Probabilidade nativa; sigmoid; isotonic | Calibração sigmoid em conjunto separado; isotonic somente se houver amostra suficiente por classe e ganho medido |
| Recuperação | TF-IDF + similaridade cosseno; BM25; embeddings locais | TF-IDF + cosseno como baseline auditável e sem modelo externo |
| Persistência | JSONL; CSV; SQLite | SQLite da biblioteca padrão para gravação transacional e exportação CSV |

### Inspeção reproduzível dos datasets

Downloads públicos consultados pela API do Kaggle, sem credenciais:

```bash
curl -fL -o d1.zip \
  https://www.kaggle.com/api/v1/datasets/download/suraj520/customer-support-ticket-dataset
curl -fL -o d2.zip \
  https://www.kaggle.com/api/v1/datasets/download/adisongoh/it-service-ticket-classification-dataset
```

Resultados observados:

- Dataset 1: 8.469 linhas e 17 colunas, não aproximadamente 30 mil linhas.
- Dataset 1: 5.700 resoluções, tempos de resolução e avaliações estão ausentes; correspondem aos tickets não fechados.
- Dataset 1: `First Response Time` e `Time to Resolution` são timestamps, mas não existe timestamp de criação do ticket. Portanto, atraso até a primeira resposta e tempo total até a resolução não são observáveis diretamente.
- Dataset 1: o único intervalo operacional derivável é `Time to Resolution - First Response Time` para tickets fechados; deve ser chamado de **intervalo pós-primeira-resposta**, não de tempo total de resolução.
- Dataset 2: 47.837 linhas, colunas `Document` e `Topic_group`, com oito classes e forte desbalanceamento.

Essas limitações alteram o plano: o diagnóstico não atribuirá causalidade, não inventará duração de primeira resposta e apresentará denominadores explícitos. A estimativa de desperdício será um cenário editável aplicado ao intervalo observável, nunca um custo histórico alegado.

## Fontes

- Streamlit, multipage apps: https://docs.streamlit.io/develop/concepts/multipage-apps/overview
- Streamlit, forms: https://docs.streamlit.io/develop/concepts/architecture/forms
- Streamlit, dataframes: https://docs.streamlit.io/develop/concepts/design/dataframes
- Streamlit, downloads: https://docs.streamlit.io/develop/api-reference/widgets/st.download_button
- Gradio Blocks: https://www.gradio.app/docs/gradio/blocks
- Plotly Dash fundamentals: https://dash.plotly.com/basic-callbacks
- scikit-learn, probability calibration: https://scikit-learn.org/stable/modules/calibration.html
- scikit-learn, text classification example: https://scikit-learn.org/stable/auto_examples/model_selection/plot_grid_search_text_feature_extraction.html
- GitHub, Streamlit: https://github.com/streamlit/streamlit
- Reddit, Streamlit for an internal dashboard: https://www.reddit.com/r/ExperiencedDevs/comments/16k3x6e/streamlit_instead_of_real_frontend/
- Reddit, Streamlit limitations: https://www.reddit.com/r/dataengineering/comments/1bu341y/what_do_you_not_like_about_streamlit/

## Prova mínima reproduzida

O gate foi reproduzido em Codespace gerenciado com Python 3.12. O lock comprovado contém
Streamlit 1.64.0, pandas 2.3.3, scikit-learn 1.9.1, joblib 1.6.0, pytest 8.4.2 e
Ruff 0.16.8. A prova sintética executou duas páginas, edição em formulário, transação
SQLite, releitura por uma nova conexão e disponibilização dos mesmos bytes do CSV
persistido no botão de download.

`make doctor`, Ruff e os três testes focais concluíram com status 0; o servidor respondeu
`ok` no endpoint de saúde e encerrou deliberadamente com status 0. `make reproduce`
retornou status 2 com correção explícita porque esse pipeline pertence a step posterior.
A prova não usa dados pessoais, não chama API paga e não sustenta alegação de desempenho
operacional.
