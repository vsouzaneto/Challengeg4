# Reprodução e validação da entrega

## Objetivo

Este roteiro demonstra que a entrega pode ser avaliada em duas rotas:

1. **Avaliação imediata:** abre o PDF e executa o Streamlit com os exports Gold já versionados, sem baixar os CSVs brutos.
2. **Reprodução completa:** obtém a versão fixada do Kaggle, valida tamanho, linhas e SHA-256, reconstrói Raw → Stage → Gold no DuckDB, executa os testes e regenera o PDF.

O teste final em ambiente limpo seguirá exatamente este documento. Sua execução foi adiada pelo autor para a etapa final; o estado atual é **procedimento preparado, validação limpa pendente**.

## Pré-requisitos

- Git.
- Python 3.11 ou 3.12.
- Acesso à internet para a rota automática do Kaggle, ou uma pasta local contendo os cinco CSVs da versão 1.
- Aproximadamente 500 MB livres para ambiente virtual, dependências, CSVs e DuckDB.

O dataset esperado é `rivalytics/saas-subscription-and-churn-analytics-dataset/versions/1`. O arquivo `data/manifest.v1.json` fixa versão, tamanho, quantidade de linhas e hash de cada CSV.

## Resultados de referência

Uma reprodução correta deve produzir:

| Controle | Esperado |
|---|---:|
| Tabelas de origem | 5 |
| Linhas Raw | 33.100 |
| Linhas Stage elegíveis | 12.577 |
| Linhas Stage em quarentena | 20.523 |
| Contas | 500 |
| Eventos de churn válidos no grão da ocorrência | 600 |
| Uso temporalmente elegível | 5.554 de 25.000 — 22,22% |
| Tickets temporalmente elegíveis | 923 de 2.000 — 46,15% |
| Snapshot marcado como churn | 110 contas |
| Contas com ao menos uma ocorrência histórica | 352 |
| Concordância cadastro × histórico | 188 contas — 37,6% |
| PDF | 9 páginas A4 em orientação paisagem |

Os totais `elegíveis` e `quarentena` são somas das cinco tabelas Stage. Eles não significam que 38% da empresa é confiável para qualquer pergunta: cada métrica usa seu próprio universo em `artifacts/data/analysis_scope.csv`.

## Rota A — avaliação imediata, sem download

### 1. Entrar na pasta da submissão

```bash
cd submissions/adailton-montinegro
```

### 2. Criar um ambiente isolado

macOS ou Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Executar os testes independentes da fonte completa

```bash
pytest -q
```

Resultado esperado antes de baixar os dados: `4 passed, 1 skipped`. O teste da auditoria exata do Kaggle v1 é ignorado somente porque `RAVENSTACK_SOURCE_DIR` ainda não foi informado.

### 4. Abrir o Streamlit com os Gold versionados

```bash
streamlit run solution/app.py
```

Abrir `http://localhost:8501`. O app deve mostrar seis páginas:

1. Capa.
2. Qualidade e gate.
3. One-page executivo.
4. Diagnóstico.
5. Triagem de risco.
6. Plano de ação.

As páginas 3 a 6 permanecem bloqueadas até o reconhecimento explícito do gate na página de qualidade.

### 5. Abrir o artefato estático

O PDF pronto está em:

```text
output/pdf/ravenstack-churn-diagnostic.pdf
```

Ele deve possuir 9 páginas e começar pelo diagnóstico executivo, seguido da auditoria, do gate de parada e da continuação demonstrativa.

## Rota B — reprodução completa com a versão fixada

### 1. Baixar, validar e reconstruir

Com acesso à internet:

```bash
python scripts/build.py
```

O processo usa `kagglehub`, baixa somente quando a cópia Raw está ausente, valida o manifesto e constrói `data/warehouse/ravenstack.duckdb`.

Saída esperada:

```text
Build concluído: .../data/warehouse/ravenstack.duckdb
Raw=33100 | elegíveis=12577 | quarentena=20523 | corte=2024-12-31
Gold revisável: .../artifacts/data
```

### 2. Alternativa sem download automático

Se o ambiente bloquear o Kaggle, baixar manualmente a versão 1 e apontar a pasta que contém exatamente os cinco CSVs:

```bash
python scripts/build.py --source-dir "/caminho/absoluto/para/os-csvs"
```

O pipeline copia os arquivos byte a byte para `data/raw/` e rejeita qualquer arquivo cujo tamanho, total de linhas ou SHA-256 difira do manifesto.

### 3. Executar a suíte completa

macOS ou Linux:

```bash
export RAVENSTACK_SOURCE_DIR="$PWD/data/raw"
pytest -q
```

Windows PowerShell:

```powershell
$env:RAVENSTACK_SOURCE_DIR = "$PWD\data\raw"
pytest -q
```

Resultado esperado: `5 passed`.

Os testes cobrem:

- preservação de Raw e reconciliação `raw = elegível + quarentena`;
- chaves únicas nos fatos Gold;
- coerência do intervalo proxy de receita;
- reconciliação das contagens mensais permitidas;
- proibição de probabilidade e leakage na fila de triagem;
- contrato dos 12 exports revisáveis;
- anomalias exatas conhecidas da versão 1 do Kaggle;
- valores dos testes estatísticos usados na narrativa.

### 4. Regenerar o PDF

```bash
python scripts/build_report.py
```

Saída esperada:

```text
.../output/pdf/ravenstack-churn-diagnostic.pdf
```

O PDF usa os mesmos arquivos de `artifacts/data/` consumidos pelo Streamlit. Metadados esperados:

- título: `RavenStack - Diagnóstico de Churn`;
- autor: `Adailton Montinegro`;
- tamanho de página: A4 paisagem;
- total: 9 páginas.

### 5. Reabrir o Streamlit

```bash
streamlit run solution/app.py
```

Confirmar que os valores de capa, qualidade, one-page e triagem coincidem com o PDF e com a tabela de resultados de referência deste documento.

## Teste final em ambiente limpo

Quando o autor liberar a etapa final, a validação será executada assim:

1. Criar uma pasta temporária fora da cópia de desenvolvimento.
2. Clonar a branch da submissão sem reutilizar o ambiente virtual, o DuckDB ou os CSVs locais.
3. Conferir que todos os arquivos alterados estão dentro de `submissions/adailton-montinegro/`.
4. Criar um novo `.venv` e instalar somente `requirements.txt`.
5. Rodar `pytest -q` antes do download e confirmar `4 passed, 1 skipped`.
6. Abrir o Streamlit com os exports versionados e realizar um smoke test das seis páginas.
7. Executar `python scripts/build.py` pela rota automática do Kaggle.
8. Definir `RAVENSTACK_SOURCE_DIR` e confirmar `5 passed`.
9. Executar `python scripts/build_report.py`.
10. Validar as 9 páginas do PDF e reconciliar os números de referência.
11. Abrir novamente o Streamlit e conferir que o rebuild não alterou a narrativa nem os indicadores.
12. Registrar versões de Python e dependências, duração, resultado de cada etapa e qualquer desvio no process log.

Nenhum push ou Pull Request faz parte do teste de reprodução. O envio remoto continuará dependendo de autorização explícita do autor.

## Checklist de aceite

- [ ] Instalação concluída somente com `requirements.txt`.
- [ ] Testes sem Raw: 4 aprovados e 1 ignorado com justificativa explícita.
- [ ] Streamlit inicia sem depender do DuckDB local.
- [ ] Seis páginas carregam e o gate bloqueia a continuação demonstrativa.
- [ ] Manifesto valida os cinco CSVs da versão 1.
- [ ] Build produz 33.100 Raw, 12.577 elegíveis e 20.523 em quarentena.
- [ ] Testes com Raw: 5 aprovados.
- [ ] Os 12 exports Gold são reconstruídos.
- [ ] PDF regenerado com 9 páginas A4 paisagem.
- [ ] Números-chave coincidem entre Gold, Streamlit e PDF.
- [ ] Nenhum arquivo fora da pasta da submissão foi alterado.
- [ ] Nenhum push ou PR foi executado durante a validação.

## Falhas esperadas e recuperação

| Sintoma | Causa provável | Ação |
|---|---|---|
| Falha no download do Kaggle | Rede, autenticação ou indisponibilidade | Usar `--source-dir` com a versão 1 já baixada. |
| `Falha no contrato dos dados` | Versão ou arquivo diferente do manifesto | Obter a versão 1 correta; não editar o CSV para fazê-lo passar. |
| Raw local inválido | Download parcial ou cópia incorreta | Remover somente os cinco CSVs locais inválidos ou usar `--force-download`. |
| Porta 8501 ocupada | Outro Streamlit em execução | Rodar `streamlit run solution/app.py --server.port 8502`. |
| Páginas analíticas bloqueadas | Gate ainda não reconhecido | Ler a página de qualidade e marcar o reconhecimento consciente. |
| Teste Kaggle v1 ignorado | Variável de ambiente ausente | Definir `RAVENSTACK_SOURCE_DIR` para `data/raw`. |

## Artefatos gerados e versionados

| Caminho | Natureza | Versionado |
|---|---|---|
| `data/raw/*.csv` | Fonte pública imutável validada | Não |
| `data/warehouse/ravenstack.duckdb` | Banco derivado | Não |
| `artifacts/data/*.csv` e `*.json` | Gold revisável usado nas apresentações | Sim |
| `output/pdf/ravenstack-churn-diagnostic.pdf` | Relatório executivo canônico | Sim |

O banco e os CSVs Raw são descartáveis porque podem ser reconstruídos. Os exports Gold e o PDF são versionados para que a análise continue avaliável mesmo sem rede.
