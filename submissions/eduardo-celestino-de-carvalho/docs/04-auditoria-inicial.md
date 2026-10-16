# Primeira auditoria do dataset CRM

**Data:** 15/10/2026. **Fonte:** [CRM Sales Predictive Analytics, Kaggle](https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics). **Reprodução:** [notebook](../solution/notebooks/01-auditoria-crm.ipynb), executado do começo ao fim com biblioteca padrão do Python. O arquivo ZIP baixado é local e ignorado pelo Git. SHA-256 do ZIP usado: `74d535826330b616758ebb6bb393abf701a5126364a72fbe71003cb6a7a87a9c`.

## Estrutura conferida

| Tabela | Linhas |
|---|---:|
| `sales_pipeline.csv` | 8.800 |
| `accounts.csv` | 85 |
| `products.csv` | 7 |
| `sales_teams.csv` | 35 |

Não há `opportunity_id` duplicado. Todos os vendedores do pipeline aparecem em `sales_teams.csv`. Contas preenchidas correspondem ao cadastro; a ausência de conta, porém, é frequente nos negócios abertos.

## Desfechos e carteira aberta

| Etapa final ou atual | Negócios | Sem conta |
|---|---:|---:|
| `Won` | 4.238 | 0 |
| `Lost` | 2.473 | 0 |
| `Engaging` | 1.589 | 1.088 |
| `Prospecting` | 500 | 337 |

São **6.711 negócios concluídos** e **2.089 abertos**; 1.425 abertos (68,2%) não têm conta. Os 500 em `Prospecting` também não têm `engage_date`. Isso limita modelos dependentes de informações da conta ou de tempo desde o engajamento.

## Falha de junção detectada

O pipeline contém **1.480 linhas com `product = GTXPro`**, mas o catálogo usa **`GTX Pro`**. São 729 `Won`, 418 `Lost`, 253 `Engaging` e 80 `Prospecting`. Uma junção exata sem revisão descartaria o preço de catálogo em 16,8% das oportunidades, inclusive 333 abertas. O notebook registra a regra explícita `GTXPro → GTX Pro` e verifica que não sobram produtos sem correspondência depois dela. O CSV original é preservado.

## Cronologia e limites para o modelo

- `engage_date` aparece em 8.300 linhas, entre 20/10/2016 e 27/12/2017.
- `close_date` aparece apenas nos 6.711 negócios concluídos, entre 01/03/2017 e 31/12/2017.
- `close_date`, `close_value` e status final não devem ser entradas do modelo.
- Não há histórico de etapas, data da última interação nem resultado futuro dos negócios abertos. A próxima auditoria deve definir cortes temporais defensáveis antes do treinamento.

**Decisão nesta fase:** a hipótese preditiva permanece viável para teste, mas ainda não existe métrica de desempenho nem evidência de impacto comercial. O próximo passo é construir uma referência simples e preparar a avaliação temporal.

## Fechamento do G1 — preparação reproduzível

O módulo [leadscore/data.py](../solution/leadscore/data.py) e o comando [audit_data.py](../solution/audit_data.py) fazem download da versão auditada, verificam o SHA-256, leem as quatro tabelas, validam todas as linhas e geram um relatório JSON. A rotina não extrai arquivos do ZIP nem altera a fonte. Em execução limpa, carregou **8.800/8.800 oportunidades**, sem linhas descartadas. Campos numéricos e datas foram convertidos para tipos apropriados; IDs duplicados, chaves desconhecidas, schema inesperado, datas invertidas e desfechos em negócios abertos provocam erro explícito.

Além de `GTXPro → GTX Pro` em 1.480 oportunidades, 12 contas têm `sector = technolgy`; a grafia é normalizada explicitamente para `technology` no objeto derivado, mantendo o valor original para auditoria. Todos os vendedores e todas as contas preenchidas encontram correspondência após a preparação. O relatório detalha nulos por etapa, permitindo distinguir ausência estrutural de informação da etapa de uma falha de leitura.

O arquivo `metadata.csv`, incluído no ZIP como dicionário, esclarece que `engage_date` é a **data de entrada em Engaging**, não a criação da oportunidade; `sales_price` é **preço sugerido de catálogo**; `close_value` é **receita realizada**. Assim, `sales_price` pode ser um proxy de valor futuro, enquanto `close_value` é informação posterior ao resultado. O dataset não fornece a data de criação do negócio nem uma fotografia histórica da etapa em que ele se encontrava antes de fechar.

**Verificações:** 7 testes de contrato passaram e um download em pasta limpa reproduziu o mesmo SHA-256 e as mesmas contagens. O G1 está concluído. A definição do corte temporal e o experimento preditivo pertencem ao G2.
