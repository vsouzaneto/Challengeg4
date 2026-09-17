# Resultados técnicos verificados — artefatos v1

**Escopo:** preparação dos dois CSVs, classificador avaliado, embeddings, índice, agrupamento e projeção. Os resultados descrevem uma execução local do protótipo; não demonstram desempenho operacional em produção, economia realizada ou validação integral da interface.  
**Referências:** [dados e métricas](03-dados-e-metricas.md), [arquitetura](01-arquitetura-compartilhada.md), [check executável](../tests/test_data_pipeline.py).

## 1. Estado verificado

| Entrega | Resultado |
|---|---|
| Catálogo canônico | `catalog.sqlite3` com 56.306 registros sanitizados, 8.469 DS1 e 47.837 DS2, IDs únicos e fontes separadas |
| Predições históricas | tabela `catalog_predictions` no mesmo SQLite, com 47.837 inferências DS2 e versão do modelo |
| Arquivos originais | Hashes recalculados iguais aos registrados na auditoria e no manifesto |
| Campos pessoais | Nome, e-mail, idade e gênero não são copiados para o catálogo |
| Texto derivado | Máscaras para nomes completos conhecidos, e-mails, URLs e sequências numéricas longas; cobertura limitada a essas regras |
| Diagnóstico | CSAT, contagens e cobertura reproduzíveis; FRT/TTR e esforço continuam indisponíveis |
| Classificação | TF-IDF + regressão logística treinados no DS2; calibração sigmoide na validação; avaliação no teste separado |
| Semântica | Encoder multilíngue real aplicado a todos os registros; embeddings 384D normalizados; FAISS com busca exata por cosseno |
| Geometria | PCA + HDBSCAN para agrupamento; UMAP 2D para exibição, independente do agrupamento |
| Integridade | Check executável passou, incluindo hashes, classificação, partições, embeddings, índice, coordenadas e vizinhos |

Comando de verificação a partir da pasta `solution/`:

```sh
.venv/bin/python tests/test_data_pipeline.py
```

Saída registrada:

```text
OK: source/artifact hashes, privacy patterns, metrics, classifier, split leakage, embeddings, FAISS, geometry and neighbors
```

Essa verificação usa artefatos já produzidos; não repete treinamento ou embeddings. Foi ampliada após a primeira execução para conferir hashes das fontes/artefatos, recarga e inferência do classificador, coerência do índice FAISS e soma dos membros de clusters. A execução ampliada também passou.

## 2. Classificador: protocolo e resultados

Modelo: `tfidf-logreg-calibrated-v1`, salvo em `artifacts/v1/classifier.joblib`; o relatório estruturado fica em `artifacts/v1/model_metrics.json` após a preparação local. A execução foi registrada em `2026-09-16T02:50:08Z`.

| Partição | Registros | Uso |
|---|---:|---|
| Treino | 33.485 | Ajuste do vocabulário TF-IDF e regressão logística |
| Validação | 7.176 | Calibração sigmoide de probabilidades, com estimador de treino congelado |
| Teste | 7.176 | Avaliação final; sem ajuste do vocabulário, calibrador ou limiar |

A divisão 70/15/15 foi estratificada por grupos de texto sanitizado, normalizado com NFC, whitespace e `casefold()`, com seed 42. Os IDs ficam em `artifacts/v1/split_ids.json` após a preparação. O check confirmou ausência de interseção de IDs e de textos normalizados entre as três partições. Semelhança aproximada entre textos não foi auditada; isso limita a alegação de generalização.

Configuração: TF-IDF de unigramas/bigramas, `min_df=2`, `max_df=0.995`, até 60.000 features, `sublinear_tf=True`; regressão logística `C=4`, `max_iter=500`. Não houve procura de hiperparâmetros baseada no teste. O classificador reconhece os oito `Topic_group` do DS2, não os cinco tipos do DS1.

| Métrica no teste | Classificador | Baseline: sempre `Hardware` |
|---|---:|---:|
| Acurácia | 86,11% — 6.179/7.176 | 28,46% |
| Macro F1 | 0,8600 | 0,0554 |

| Categoria | Suporte no teste | F1 |
|---|---:|---:|
| Access | 1.069 | 0,8913 |
| Administrative rights | 264 | 0,7874 |
| HR Support | 1.638 | 0,8635 |
| Hardware | 2.042 | 0,8547 |
| Internal Project | 318 | 0,8492 |
| Miscellaneous | 1.059 | 0,8312 |
| Purchase | 370 | 0,9147 |
| Storage | 416 | 0,8883 |

Calibração avaliada no teste: log loss 0,4163; Brier multiclasses 0,2122, calculado como a média da soma dos erros quadráticos das oito probabilidades por registro. O relatório também contém bins de confiança/acerto e matriz de confusão. Calibração aplicada não significa probabilidades perfeitas: por exemplo, no bin 0,9–1,0, confiança média foi 0,9469 e acerto observado 0,9895.

O limiar de revisão `0,75` foi fixado como política experimental antes da avaliação; não foi escolhido para otimizar o teste. Nesse limiar:

- 4.686/7.176 registros superam o limiar: cobertura de 65,30%.
- 4.523/4.686 estão corretos: acurácia condicional de 96,52%.
- 2.490/7.176 ficam abaixo: 34,70% requerem revisão por esse critério.

**96,52% não é a acurácia global do modelo.** Superar o limiar também não elimina regras de revisão por risco, contexto sensível, idioma não avaliado ou falta de evidência. As previsões pré-computadas do corpus completo ficam na tabela `catalog_predictions` do SQLite e incluem exemplos de treino e validação; seus acertos não devem ser agregados como nova avaliação independente.

## 3. Encoder, índice e agrupamentos

Encoder: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Revisão fixada: `e8f8c211226b894fcb81acc59f3b34ba3efd5f42`. O modelo foi baixado para o cache local dentro do challenge e executado em MPS. Dimensão: 384; normalização L2; limite de entrada configurado pelo modelo: 128 tokens. Textos longos podem ser truncados nessa janela, uma limitação da representação.

Índice: `FAISS IndexFlatIP`. Como os vetores são normalizados, produto interno corresponde a cosseno. O índice e os embeddings cobrem todos os registros, inclusive os que não recebem cluster. A busca não equivale a detecção comprovada de duplicata.

| Espaço | Registros | Clusters estáveis | Em clusters | Ruído `-1` | Ruído |
|---|---:|---:|---:|---:|---:|
| `ds1-semantic-v1` | 8.469 | 33 | 4.178 | 4.291 | 50,67% |
| `ds2-semantic-v1` | 47.837 | 27 | 7.197 | 40.640 | 84,96% |

HDBSCAN usa o espaço PCA de 32 componentes, distância euclidiana, `min_samples=8`; `min_cluster_size=35` no DS1 e 80 no DS2. PCA preservou 74,57% e 59,57% da variância, respectivamente. Esses parâmetros identificam grupos densos exploratórios; não foram selecionados contra uma avaliação humana de relevância.

**A cobertura de cluster é limitada, especialmente no DS2.** Os 40.640 registros de ruído não formam uma comunidade coerente. A interface precisa identificá-los como “Sem cluster estável”, preservando a busca por vizinhos; não transformar o rótulo `-1` em incidente, categoria ou oportunidade homogênea. Nenhum resultado de agrupamento comprova causa comum.

UMAP foi ajustado aos embeddings com `n_neighbors=20`, `min_dist=0.2`, 120 épocas, métrica cosseno, seed 42 e duas dimensões. Coordenadas persistidas e transformador estão disponíveis por fonte. A distância no plano é somente uma projeção; os scores apresentados devem vir dos vetores/índice originais. A hierarquia calculada é clusters → tickets; subclusters não foram inventados.

Arquivos por fonte: `embeddings.npy`, `index.faiss`, `coordinates.npy`, `clusters.npy`, `cluster_probabilities.npy`, `map_ids.json`, `neighbors.json`, `clusterer.joblib`, `projector.joblib` e `semantic.json`. Todos os vetores, coordenadas e IDs passaram nas verificações de dimensão, cardinalidade, normalização e valores finitos. A lista de vizinhos exclui o próprio registro; replay também precisa excluir sua referência histórica original, conforme contrato do backend.

## 4. Tempos medidos e ambiente

| Etapa | Tempo registrado | O que inclui / limite |
|---|---:|---|
| Treino, calibração e avaliação do classificador | 8,07 s | Até construção do relatório; não inclui toda a serialização nem predição final do corpus completo |
| Predição em lote no teste | 0,0237 ms/registro | Média de um lote de 7.176; não é latência de requisição individual nem pipeline completo |
| Espaço semântico DS1 | 33,77 s | Embeddings, índice, clusters, UMAP e preparação de metadados; download/carga inicial do encoder fora dessa medida |
| Espaço semântico DS2 | 131,72 s | Mesma delimitação do DS1 |

Esses números descrevem uma execução local, sem ensaio de carga ou SLA. Não comparar diretamente inferência em lote com latência end-to-end do Ticket Lab.

| Dependência registrada | Versão |
|---|---|
| scikit-learn | 1.9.1 |
| sentence-transformers | 5.7.0 |
| torch | 2.14.0 |
| faiss-cpu | 1.15.0 |
| umap-learn | 0.5.12 |
| hdbscan | 0.8.44 |

As demais versões estão em [requirements.lock.txt](../requirements.lock.txt). Resultados numéricos podem variar com hardware e versões; hashes abaixo identificam os bytes desta execução, sem prometer regeneração binariamente idêntica.

## 5. Hashes e procedência

SHA-256 de artefatos conferidos nesta verificação:

| Artefato | SHA-256 |
|---|---|
| `catalog.sqlite3` | fonte canônica sanitizada; cardinalidade, privacidade e metadados validados no check executável |
| `classifier.joblib` | `9cc5db856530fd9bd31d75c7fed1dddfa38a26b7de76f6713d8431988bf3f2f4` |
| `catalog_predictions` | 47.837 linhas de inferência histórica no SQLite, validadas no check executável |
| `split_ids.json` | `f3c57e44fc6e605afb030bdb84b9be1e7f28eb8f87ba997d2f3e605d62b870aa` |
| `model_metrics.json` | `c43d627d050b42870bea8a7bef52609ee25617a482c3c2dda8cb415d1cd91915` |
| Encoder `model.safetensors` — 470.641.600 bytes | `eaa086f0ffee582aeb45b36e34cdd1fe2d6de2bef61f8a559a1bbc9bd955917b` |
| DS1 `embeddings.npy` | `ddb4d5e5da7fafc4275beb50583d8a051b1959e1f1be4ed62bfdd9b288f6fc51` |
| DS1 `index.faiss` | `01c6e0240f48e33af8d90d226902403eda219db76447b8c9773ee8309d767f57` |
| DS2 `embeddings.npy` | `1a59cbeb9ffef353725d245f70dc80658278ed9c7dbafd2d5f5cd51e2c0265bb` |
| DS2 `index.faiss` | `87a02ca038476927dba99baa07ce2190b5e36b8ad0bcdcc961b2b488ecea0aaf` |

Os hashes de coordenadas, rótulos de cluster e mapas de IDs constam nos arquivos `artifacts/v1/ds1/semantic.json` e `artifacts/v1/ds2/semantic.json` gerados pela preparação e também foram comparados com os arquivos. Os checksums dos CSVs permanecem aqueles da [auditoria de dados](03-dados-e-metricas.md#1-inventário-verificado).

## 6. Limitações preservadas

- **Dados operacionais:** falta abertura do ticket; 1.365 dos 2.769 pares temporais têm resolução anterior à primeira resposta. Não há FRT/TTR/esforço recuperável confiável.
- **CSAT:** observado apenas em 2.769 fechados; ausência não foi imputada. Associação entre grupos não implica causalidade.
- **Domínio e idioma:** avaliação do classificador cobre rótulos IT do DS2. Não existe benchmark rotulado PT-BR nem avaliação do classificador na taxonomia DS1. Encoder multilíngue não transforma o classificador lexical em modelo avaliado para todos os idiomas.
- **Vazamento:** duplicatas exatas normalizadas foram separadas por grupos. Near-duplicates e dependências semânticas entre partições continuam sem auditoria específica.
- **Recuperação e duplicatas:** scores e vizinhos são reais, mas relevância e precisão de candidatos a duplicata ainda exigem julgamento humano. Não há métricas humanas inventadas.
- **Respostas:** DS2 não contém resolução; resoluções DS1 são históricas, com qualidade não validada e descrições templateadas. Não provam uma solução correta para novo ticket.
- **Privacidade:** máscara por padrão não garante detectar todos os nomes desconhecidos ou outros dados sensíveis em texto livre. Catálogo destinado ao protótipo local; revisão adicional antes de compartilhamento externo.
- **Operação:** clusters, modelo e replay não demonstram incidentes de produção, automação aprovada, retorno financeiro realizado ou redução de quadro. ROI permanece cenário de premissas.
- **Segurança de artefatos:** arquivos `joblib` são os gerados localmente. Não carregar serializações externas fornecidas por usuários.

## 7. Checkpoints desta entrega

- [x] DAT-01: inventário e hashes dos CSVs originais conferidos, sem modificá-los.
- [x] DAT-02: catálogo com IDs únicos, campos pessoais excluídos e máscaras testadas.
- [x] DAT-02b: catálogo e predições históricas persistidos em SQLite; o runtime lê o banco, não JSON.
- [x] DAT-03: métricas auditadas e bloqueios FRT/TTR mantidos.
- [x] ML-01: divisão por grupos persistida e sem interseção de textos normalizados.
- [x] ML-02: baseline, classificação calibrada, métricas e suporte por classe registrados.
- [x] SEM-01: embeddings reais de todo o corpus, índices, coordenadas e agrupamentos persistidos.
- [x] SEM-02: dimensões, normalização, hashes, cardinalidade e vizinhos validados.
- [x] VER-01: check executável da preparação/artefatos passou após ampliação de integridade.
- [ ] VAL-01: avaliação humana de relevância, duplicatas, agrupamentos e respostas.
- [ ] VAL-02: avaliação rotulada de entradas PT-BR, fora de domínio e near-duplicates.
- [ ] VAL-03: piloto de esforço, retrabalho, riscos e retorno operacional real.

Os itens pendentes são limites de validação; não impedem demonstrar os artefatos reais, desde que a interface preserve esses limites.
