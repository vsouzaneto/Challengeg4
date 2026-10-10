# Análise de referência (Python)

Esta é a implementação em Python feita na preparação, separada da do app (TypeScript). Os números que o app usa vêm do núcleo em TypeScript (`npm run auditoria`). Na revisão inicial, os dois foram comparados e, onde divergiram, a revisão decidiu qual estava certo (CA7, D22; ver `../../process-log/01-revisao-inicial.md`, R1–R4).

## Como rodar

```sh
cd solution/analysis
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python backtest_referencia.py      # tabela de backtest de referência
python auditoria_sql.py            # 21 consultas SQL (DuckDB); grava saidas/auditoria_sql.md
python efeito_trimestre.py         # efeito de fim de trimestre
python backtest_exploratorio.py    # primeira versão do backtest, com modelo de ML
python significancia_ml.py         # revisão inicial: ML com desempate pelo ID, por vendedor e foto (N18)
python referencia_scipy.py         # revisão inicial: valores do scipy para os testes da estatística do TS (D23)
```

`significancia_ml.py` e `referencia_scipy.py` foram escritos na revisão inicial. O `referencia_scipy.py` lê `saidas/estatistica-entradas.json`, que `npm run auditoria` grava.

Os dados vêm de `../data`. Para usar outra pasta, defina a variável `CRM_DATA_DIR`.

## Arquivos

| Script | Saída em `saidas/` | O que mostra |
|---|---|---|
| `backtest_referencia.py` | `backtest_referencia.txt` | Receita capturada pelos 10 primeiros de cada vendedor, em 4 datas de 2017. É a referência do app (ver tabela abaixo). Determinístico: empate desfeito pelo ID; aleatório calculado pela esperança exata. |
| `auditoria_sql.py` | `auditoria_sql.md` | 21 consultas: contagens, chance pela idade com e sem viés de sobrevivência, ciclo máximo de 138 dias, p-valores por vendedor, gestor, regional, produto, setor e empresa. |
| `efeito_trimestre.py` | `efeito_trimestre.txt` | Taxa de ganho por mês do trimestre em que o negócio foi concluído (49,0% · 54,7% · 80,7%). |
| `backtest_exploratorio.py` | `backtest_exploratorio.txt` | Primeira versão do backtest, com gradient boosting. O modelo é determinístico (`random_state=0`, sem parada antecipada nesse tamanho), mas a ordenação não desempata pelo ID (`sort_values("sc")`), então empates podem mudar o resultado. O "valor esperado" daqui usa chance por **dia exato**, não as faixas da D5. Fica como registro. |
| `significancia_ml.py` | `ml-por-vendedor.csv` | ML e valor ponderado por dia, com desempate pelo ID e 5 sementes (dão o mesmo resultado). O teste pareado está em `npm run auditoria`: a diferença não é significativa (p de 0,74 a 0,83). |
| `referencia_scipy.py` | `../src/core/scipy-reference.json` | Referência do scipy para as funções estatísticas escritas à mão (D23). |

Resultados de referência do `backtest_referencia.py`:

| Método | Receita capturada |
|---|---|
| Valor ponderado | 44,41% |
| Situação e preço (o Python trata 90 dias como "no prazo"; com a D2, que começa "esfriando" em 90, dá 43,16%) | 43,35% |
| Preço sem parados | 40,10% |
| Só preço | 36,17% |
| Chance só com concluídos | 32,23% |
| Aleatório | 15,40% |

## Reprodutibilidade

As saídas desta pasta foram geradas na preparação; segundo a preparação, com Python 3.13. Na revisão inicial, em 09/10/2026, os scripts foram rodados de novo com Python 3.12.4 e as versões de `requirements.txt` (pandas 3.0.5, numpy 2.5.3, DuckDB 1.5.6, scipy 1.18.1, scikit-learn 1.9.1). `backtest_referencia.py` e `efeito_trimestre.py` reproduziram as saídas byte a byte. `auditoria_sql.py` mudou só a ordem de linhas empatadas, porque as consultas não têm `ORDER BY` completo. O arquivo versionado é o original.
