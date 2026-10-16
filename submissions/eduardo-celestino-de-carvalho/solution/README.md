# Lead Kanban — Challenge 003

Esta pasta contém o **Lead Kanban**, o tratamento reproduzível do dataset público, os experimentos e as verificações do Challenge 003.

O Lead Kanban é uma aplicação web local ([server.py](server.py) + [web/](web/)) que organiza as oportunidades abertas em três colunas: **Negociar**, **Qualificar** e **Confirmar ou encerrar**.

- **Carga dos dados:** [leadscore/data.py](leadscore/data.py). Verifica SHA-256, esquema, chaves, etapas, nulos e datas do ZIP público do Kaggle, que fica em `solution/data/` (ignorado pelo Git).
- **Regras de negócio:** [leadscore/priority.py](leadscore/priority.py).
- **Payload da interface:** [leadscore/board.py](leadscore/board.py).
- **Experimento do G2:** [experiment_model.py](experiment_model.py), [documentado aqui](../docs/07-g2-modelagem.md). A regressão logística não alimenta o sistema.

## Demo pública

[celestinoedu.github.io/ai-master-challenge](https://celestinoedu.github.io/ai-master-challenge/) é a mesma interface, servida como arquivos estáticos. Para gerá-la:

```powershell
python build_static.py --out dist   # web/ + data/board.json, sem servidor
```

Sem o servidor Python, o app lê `data/board.json`, o mesmo payload de `/api/board`.

## Rodar o Lead Kanban

Pré-requisito: **Python 3.11+**, sem bibliotecas externas, e acesso à internet na primeira execução para baixar o dataset auditado. A partir da pasta `solution/`:

```powershell
python server.py --open
```

Abra **http://localhost:8000**. O [servidor](server.py) usa apenas a biblioteca padrão. A interface é HTML, CSS e JavaScript em módulos, sem build:

| Arquivo | Responsabilidade |
|---|---|
| [web/js/terms.js](web/js/terms.js) | Vocabulário e cores, fonte única |
| [web/js/state.js](web/js/state.js) | Filtros e preferências |
| [web/js/pipeline.js](web/js/pipeline.js) | Quadro e detalhe |
| [web/js/dashboard.js](web/js/dashboard.js) | Relatório gerencial |
| [web/js/help.js](web/js/help.js) | Procedimento |
| [web/js/main.js](web/js/main.js) | Navegação e inicialização |

**Telas e funcionalidades**

- **Barra superior fixa:** Pipeline, Dashboard, filtros globais (regional, manager, vendedor, busca) e o botão **?**, que abre o procedimento completo. A tecla `?` também abre.
- **Pipeline:** guia rápido para quem chega (dispensável) e três colunas com contagem e valor potencial:
  - **Negociar** (298): `Engaging` dentro do prazo máximo de 138 dias.
  - **Qualificar** (500): `Prospecting`.
  - **Confirmar ou encerrar** (1.291): `Engaging` com prazo excedido.

  Os cartões mostram posição, valor potencial, barra de prazo, fase e progresso das ações. O detalhe traz próximas ações marcáveis, motivos, régua de prazo, conta e histórico. Há exportação em CSV.
- **Dashboard:** relatório de uma página para a gestão:
  - KPIs de valor e de "pipeline no prazo", cada um com explicação no ícone ⓘ;
  - composição por regional, manager ou vendedor;
  - rankings por vendedor;
  - a seção "Por que a fila funciona assim": 4 fatos dos dados, cada um com número, frase curta e visual simples. Os histogramas completos ficam em "Ver dados completos";
  - tabela ordenável, exportável em CSV.
- **Procedimento:** regras de negócio, fluxo de classificação, régua de prazos, ações, indicadores, funcionalidades, evidências, glossário e limites.

Os filtros, o agrupamento e as ações marcadas ficam salvos no navegador. Nada é gravado no CRM.

**Demonstração rápida:**
1. No Pipeline, veja a proporção entre Negociar e Confirmar ou encerrar.
2. Escolha "Anna Snelling" na barra: ela tem 1 negócio em Negociar, 55 para qualificar e 56 para confirmar ou encerrar.
3. Abra um cartão, marque uma ação e navegue com ← →.
4. No Dashboard, alterne entre Regional, Manager e Vendedor, veja os rankings e a seção "Por que a fila funciona assim".
5. Clique em **?** para ver o procedimento completo.

## Reproduzir o G1 — Dados

Pré-requisito: **Python 3.11+** e acesso à internet na primeira execução. A partir desta pasta `solution/`:

```powershell
python audit_data.py
python -m unittest discover -s tests -p test_data.py -v
```

O primeiro comando baixa automaticamente a versão auditada do dataset público quando não há cache, verifica o hash e imprime um relatório JSON com contagens, ausências por etapa e aliases aplicados. Para salvar o relatório localmente: `python audit_data.py --output data/quality-report.json`. O ZIP e o relatório em `data/` não devem entrar no PR. Se o arquivo público mudar, o comando para com erro e exige nova auditoria antes de usar a nova versão.

O [notebook de auditoria](notebooks/01-auditoria-crm.ipynb) permite inspecionar a exploração inicial em Jupyter; `audit_data.py` reproduz esta etapa sem bibliotecas externas de Python.

## Reproduzir o G2 — Método

É a única etapa com dependência externa (scikit-learn). A partir desta pasta:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-model.txt
.\.venv\Scripts\python.exe experiment_model.py --output experiments/g2-results.json
```

Em macOS/Linux, use `.venv/bin/python`. Sem o scikit-learn, os testes do modelo são pulados e os demais rodam normalmente.

O experimento baixa/valida o mesmo ZIP público, fixa cortes temporais e compara cinco métodos. O JSON de resultados contém somente agregados e é versionável; o ZIP e o ambiente `.venv` ficam locais. A avaliação retrospectiva usa negócios resolvidos em 30 dias, portanto **não estima a probabilidade de fechamento da carteira aberta**. O modelo testado não mostrou utilidade operacional; veja números e limites em [docs/07-g2-modelagem.md](../docs/07-g2-modelagem.md). O G1 também roda sem bibliotecas externas.

## Como o Lead Kanban decide

Atributos fixos (produto, setor, vendedor) quase não separam ganhos de perdas. O sinal que o histórico sustenta é o **tempo em `Engaging`**: perdas se decidem cedo (mediana de 14 dias) e nenhum dos 6.711 negócios concluídos fechou depois de 138 dias. Por isso:

- **Negociar:** `Engaging` dentro do prazo máximo, ordenado por valor potencial e, no empate, pelo negócio mais recente. A fase (Início, Em andamento, Perto do limite) define a ação.
- **Qualificar:** `Prospecting`, ordenado por valor potencial.
- **Confirmar ou encerrar:** `Engaging` com prazo excedido; a ação é confirmar com o cliente e atualizar a etapa no CRM.

O valor potencial é o preço de catálogo, não uma probabilidade. Conta ausente gera uma tarefa de cadastro sem mudar a ordem. A regra, a evidência e os limites estão em [docs/09-g3-revisao-fila-foco.md](../docs/09-g3-revisao-fila-foco.md). A regra anterior, de pontos de atenção, está registrada em [docs/08](../docs/08-g3-fila-comercial.md).

## Reproduzir o backtest da regra

A partir desta pasta, sem bibliotecas externas:

```powershell
python evaluate_focus.py --output experiments/g3-focus-backtest.json
```

Em cinco fins de mês de 2017, o script reconstrói os negócios em `Engaging`, usando só os fechamentos conhecidos até cada corte. Depois compara as regras pelos ganhos e pela receita nos 5 primeiros negócios de cada vendedor. O Lead Kanban somou **326 ganhos e 2,09 mi de receita**, contra **275 e 1,76 mi** do método óbvio de ordenar só pelo valor. O JSON também guarda, como registro do processo, a primeira regra do G3 e uma variante descartada. Nenhum dos 1.443 casos com prazo excedido fechou depois.

O ganho vem da idade do negócio: tirar os parados da fila (1,76 → 1,90 mi) e, no empate de valor, preferir os mais novos (→ 2,09 mi). Em `decomposition`, o JSON traz essas variantes e um bootstrap pareado: +18,5% sobre "só valor", com IC 95% de +12% a +25%.

O mesmo JSON traz dois controles de robustez (`robustness_summary`):
- **Desempate refeito com as 3 primeiras datas e conferido nas 2 últimas.** "Mais recente primeiro" vence nas duas partes; nas 2 últimas, com 670 mil, contra 502 mil do mais antigo primeiro e 493 mil de ordenar só pelo valor. As datas já tinham sido vistas, então isso não equivale a uma validação independente.
- **Prazo por percentil (p99, p95, p90) em vez do máximo.** A receita da fila quase não muda, mas 9, 35 e 86 vendas que ainda iam fechar cairiam em "Confirmar ou encerrar". Com o máximo, nenhuma.

O resultado continua exploratório; as ressalvas estão no [doc da revisão](../docs/09-g3-revisao-fila-foco.md).

## Testes

```powershell
python -m unittest discover -s tests -v
```

São 31 testes: carga e auditoria, regra das colunas e da ordem, payload da interface, ausência de vazamento e bootstrap do backtest, e intervalos de bytes do vídeo tutorial. Os testes do modelo exigem scikit-learn e são pulados sem ele.

Os arquivos brutos, ambientes locais e credenciais não entram no Pull Request; o download do dataset público é reproduzível e a fonte está creditada. A versão roda localmente sobre dados do CRM até 31/12/2017, sem conexão com um CRM ativo.
