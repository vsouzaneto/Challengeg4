---
name: spark-ml-practices
description: Boas práticas do pipeline Spark / Spark ML do Lead Scorer — quando Spark se justifica (e quando não), ambiente (JDK 17/21, local[*]), camadas bronze/silver/gold em parquet particionado por as_of, Pipeline ML declarativo, validação temporal (nunca randomSplit/CrossValidator), persistência e versionamento do PipelineModel com model card, manifestos, PSI, testes com fixture Spark. Use ao escrever ou revisar qualquer código PySpark, job ou modelo.
user-invocable: false
---

# Spark ML — práticas deste projeto

## Por que Spark aqui (e o que dizer ao avaliador)

Os dados do challenge (8.800 deals) cabem em pandas. Spark **não** entra por volume; entra porque a Head pediu algo que "sempre execute a classificação": um pipeline de ML operacional, reexecutável por data (`--as-of`), com modelo versionado, que escale para o CRM inteiro sem reescrita. Regra de honestidade: a API e o web **não** dependem de Spark em runtime (a API lê o parquet com pandas/pyarrow), e a documentação declara explicitamente que Spark é decisão de arquitetura, não necessidade de escala hoje. Onde Spark só adiciona atrito (ex.: explicabilidade local), o driver faz em pandas e isso é dito.

## Ambiente

- `pyspark` 3.5.x pinado no `pyproject.toml`; Python 3.12 via uv.
- JDK **17 ou 21** (Spark 3.5 não suporta 23+). Na máquina de desenvolvimento há um Corretto 21 instalado (`/usr/libexec/java_home -v 21`); o padrão do sistema é o JDK 23, que falha. `lead_scorer/spark.py` resolve `JAVA_HOME` (env → `/usr/libexec/java_home -v 21` → `-v 17`) e aborta com instrução clara se só houver 23+.
- Sessão única via `get_spark(app_name, for_tests=False)`: `master=local[*]`, `spark.sql.shuffle.partitions=8` (4 em testes), `spark.ui.enabled=false` em testes, `spark.sql.session.timeZone=UTC`, `spark.driver.memory=2g`.
- Sem `spark-submit` obrigatório: jobs rodam com `uv run python -m lead_scorer.jobs.<job>`; `spark-submit` é opcional e documentado.

## Camadas e layout

```
data/raw/            CSV imutáveis + SHA256SUMS
data/bronze/<t>/     leitura com StructType explícito, FAILFAST, _ingested_from (sha256)
data/silver/<t>/     limpos, tipados, conformados; opportunities com flags account_known etc.
data/gold/opportunity_features/as_of=YYYY-MM-DD/   1 linha por deal aberto em as_of; só info conhecida em as_of
data/gold/history_stats/as_of=YYYY-MM-DD/          agregados com close_date <= as_of
data/gold/labels/as_of=YYYY-MM-DD/                 desfecho após as_of (avaliação); separado das features
data/gold/scores/as_of=YYYY-MM-DD/                 saída do score (ScoredDeal) + manifest.json
models/<version>/    PipelineModel salvo + model_card.md + metrics.json + feature_list.json + training_manifest.json
models/latest        arquivo texto com o nome da versão
```
Parquet com `mode("overwrite")` na partição; jobs idempotentes; `manifest.json` com parâmetros, git sha, checksums dos raw, contagens, duração.

## Pipeline ML

- `Pipeline(stages=[StringIndexer(handleInvalid="keep"), OneHotEncoder(handleInvalid="keep"), Imputer(strategy="median"), VectorAssembler(handleInvalid="keep"), StandardScaler, <estimator>])`.
- Features **somente** de `opportunity_features` (lista fechada em `ml/features.py`, testada). Nenhuma coluna de desfecho, nenhum `label` no vetor.
- Estimador padrão: `LogisticRegression(elasticNetParam, regParam, weightCol para desbalanceamento leve)`; contribuições por feature = coeficiente × valor padronizado (exatas). Alternativa: `GBTClassifier(maxDepth≤4, maxIter≤100, seed)` com `IsotonicRegression` para calibrar em holdout temporal; só se bater a LR com margem documentada.
- Seeds fixas em tudo que é estocástico; `setSeed`.
- **Proibido**: `randomSplit`, `CrossValidator`, `TrainValidationSplit` (folds aleatórios vazam o futuro). Validação = cortes temporais definidos pelo data-scientist.
- Avaliação com `BinaryClassificationEvaluator(areaUnderPR)` + métricas de negócio calculadas em pandas no driver (lift, precision@k, receita capturada, Brier, calibração).

## Explicabilidade

Saída `ScoredDeal` (ver `scoring-methodology`). `reasons` combina regras (camada 1) e contribuições do modelo (camada 2) ordenadas por |peso|, traduzidas para pt-BR na voz do vendedor. Contribuições do modelo só entram se forem exatas (LR) ou calculadas por método testado; nunca "feature importance global" apresentada como explicação local.

## Monitoramento e ciclo de vida

- `score` grava PSI por feature (treino vs. lote) no manifesto; aviso se PSI > 0,2.
- Retreino: `train --as-of <nova data>` gera nova versão; promoção = atualizar `models/latest` após comparar `metrics.json`. Exemplo de agendamento (cron/Airflow) em `docs/ml-pipeline.md`.
- Model card obrigatório: dados e janela, features, métricas por corte vs. baselines, limitações, uso pretendido, riscos (gaming, ranking de vendedores).

## Testes

- Fixture `spark` session-scoped (`conftest.py`) com config de teste; dados sintéticos pequenos + amostra dos raw.
- Igualdade de DataFrames com `chispa` (ou `assertDataFrameEqual` do PySpark 3.5).
- Testes de contrato: schema de saída; `set(features) ∩ {close_value, close_date, label} == ∅`; point-in-time; round-trip `PipelineModel.save/load`; reexecução idempotente; determinismo com seed.

## Anti-padrões

`inferSchema=True`; `collect()` em tabela inteira sem motivo; UDF Python onde expressão SQL resolve; `toPandas()` dentro de loop; `current_date()`/`current_timestamp()`; salvar modelo sem manifesto; UI importando pyspark; `spark.jars.packages` de fontes não confiáveis.
