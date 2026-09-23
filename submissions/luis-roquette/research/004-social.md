# Pesquisa obrigatória — Challenge 004: Social Media

**Data:** 21/09/2026
**Decisão:** usar **Streamlit 1.64 + Pandas + SQLite da biblioteca padrão** em um monólito web local.

## 1. Problema pesquisado

Construir, em 4–6 horas, um cockpit local que importe manualmente o CSV do desafio, compare posts patrocinados e orgânicos em grupos equivalentes, detecte desvios acionáveis, explique a evidência, registre a decisão humana e exporte uma síntese executiva.

Consultas principais:

- `Python local CSV analytics dashboard upload download table charts Streamlit Dash Panel`
- `GitHub social media engagement dashboard Streamlit CSV sponsorship analytics`
- `Reddit Streamlit vs Dash dashboard framework internal analytics`
- inspeção do dataset e dos repositórios pelas APIs públicas de Kaggle e GitHub

## 2. Dataset validado

Fonte: [Social Media Sponsorship & Engagement Dataset](https://www.kaggle.com/datasets/omenkj/social-media-sponsorship-and-engagement-dataset), licença MIT, versão atualizada em 28/05/2025.

- Arquivo único: `social_media_dataset.csv`, 23.290.049 bytes.
- Dimensão real: **52.214 linhas e 27 colunas**.
- Período: 29/05/2023 a 28/05/2025.
- Plataformas: Bilibili, YouTube, Instagram, RedNote e TikTok.
- Patrocínio: 22.314 posts patrocinados e 29.900 orgânicos.
- Métricas disponíveis: views, likes, shares, comments e follower count.
- Contextos disponíveis: plataforma, tipo, categoria, idioma, data, creator, disclosure, patrocinador e audiência.
- O arquivo não possui coluna física `engagement_rate`; qualquer taxa será derivada, com fórmula, denominador e unidade explícitos.
- Apesar do nome, `audience_age_distribution` e `audience_gender_distribution` contêm rótulos categóricos, não percentuais. Idade, gênero e localização só podem ser usados como segmentos observados; não sustentam personas ou distribuição individual inferida.
- O snapshot inspecionado não contém zeros nas cinco métricas numéricas. O produto deve registrar essa limitação de representatividade e continuar aceitando/preservando zeros em outros arquivos válidos e nas fixtures.
- Ausências observadas: 8.743 hashtags e 8.688 textos de comentário vazios; não são campos obrigatórios para a análise principal.
- Restrição crítica: não há investimento, receita ou conversão. Portanto, o produto não deve calcular ROI financeiro.

## 3. Frameworks avaliados

Metadados consultados em 21/09/2026.

| Candidato | Licença / atividade | Prova relevante | Decisão |
|---|---|---|---|
| [Streamlit](https://github.com/streamlit/streamlit) | Apache-2.0; 45.807 estrelas; release 1.64.0 em 15/09/2026; testes e CI ativos | [`st.file_uploader`](https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader), [`st.download_button`](https://docs.streamlit.io/develop/api-reference/widgets/st.download_button), tabelas e gráficos no mesmo processo Python | **Escolhido:** cobre o fluxo inteiro com o menor código e sem frontend separado |
| [Dash](https://github.com/plotly/dash) | MIT; 24.423 estrelas; release 4.4.1 em 21/07/2026; testes ativos | [`dcc.Upload`](https://dash.plotly.com/dash-core-components/upload) funciona, mas o estado depende de callbacks; DataTable foi descontinuada em favor de `dash-ag-grid` | Rejeitado: mais callbacks e uma dependência adicional para uma tabela rica |
| [Panel](https://github.com/holoviz/panel) | BSD-3-Clause; 5.775 estrelas; release 1.9.4 em 17/08/2026; testes ativos | [`FileInput`](https://panel.holoviz.org/reference/widgets/FileInput.html), [`Tabulator`](https://panel.holoviz.org/reference/widgets/Tabulator.html) e templates atendem ao caso | Rejeitado: viável, porém menos direto para o prazo e com menor base de adoção observada |

Evidência de comunidade: na discussão [Dashboard Framework, r/quant](https://www.reddit.com/r/quant/comments/1d1eovf/dashboard_framework/), usuários descrevem Streamlit como rápido e adequado a ferramentas internas/read-only, e Dash como mais apropriado quando a interação e o estado ficam complexos. O MVP tem estado persistente pequeno e explícito em SQLite, então a principal limitação relatada do Streamlit não bloqueia o caso.

## 4. Soluções prontas avaliadas

| Repositório | Licença / sinais de manutenção | O que pode ser reaproveitado | Limite e decisão |
|---|---|---|---|
| [social-media-engagement-analyzer](https://github.com/Karthik-0917/social-media-engagement-analyzer) | MIT; atualizado em 09/09/2026; testes, validação e CI Python 3.11–3.13 | Padrões de validação de schema, métricas não negativas e testes | É o precedente mais próximo, mas usa outro schema, DuckDB e múltiplas páginas. Reusar conceitos com atribuição; não copiar a arquitetura |
| [Social-Media-Engagement-Dashboard](https://github.com/Vikash0Chaudhary/Social-Media-Engagement-Dashboard) | MIT; atualizado em 15/06/2026; sem testes ou releases | Confirma que Streamlit + Pandas + Plotly entrega um dashboard mínimo | Apenas médias e KPIs descritivos; não controla contexto nem valida robustamente. Rejeitado como base |
| [marketing-campaign-performance-dashboard](https://github.com/girishshenoy16/marketing-campaign-performance-dashboard) | MIT; atualizado em 13/08/2026; sem testes ou releases | Referência visual para síntese executiva | HTML estático e métricas de ROI sobre outro dataset. Rejeitado como base técnica |

Também foram descartados resultados semelhantes sem licença explícita: sem licença, não há permissão clara para reutilização de código.

## 5. Reprodução do candidato escolhido

Spike executado em ambiente temporário com Python 3.14.2, `streamlit==1.64.0` e `pandas==2.3.3`.

Fluxo reproduzido:

1. iniciar servidor Streamlit local;
2. enviar CSV pelo navegador;
3. validar colunas obrigatórias;
4. persistir hash e contagem da importação em SQLite;
5. renderizar KPI, gráfico e tabela;
6. renderizar o controle de download do CSV de evidências.

Resultados:

- health check: `ok`;
- verificação Playwright: `UI_CHECK=PASS` para upload e renderização; o spike não comprovou a conclusão de um download no navegador;
- persistência: uma importação com quatro registros;
- evidência visual: [`streamlit-proof.png`](../process-log/evidence/004/framework-research/streamlit-proof.png).

## 6. Decisão e limites

O framework será **Streamlit**. Pandas fará leitura, validação e agregações; Plotly só será usado se um gráfico nativo não cobrir a interação necessária; SQLite guardará apenas metadados, decisões e resultados. Esta é a menor pilha que atende upload, análise, drill-down, feedback e exportação no prazo.

Ficam fora do MVP: API própria, frontend separado, autenticação, cloud, DuckDB, ML, LLM, ingestão automática, previsão, clusters de persona, análise semântica de comentários e ROI financeiro.

Limite conhecido: o estado de sessão do Streamlit reinicia quando a conexão WebSocket é perdida. Estado operacional que precise sobreviver a sessões será gravado explicitamente em SQLite; o CSV bruto continuará fora do banco, conforme decisão registrada.
