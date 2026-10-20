# Data Audit — Challenge 003 | Lead Scorer

[↑ Voltar ao discovery](./discovery.md#dados) · [Hipóteses do discovery](./discovery.md#hipoteses)

> **Identificadores.** Os códigos V1 a V14 (testes), S1 a S22 (sinais) e D, M e O vêm da versão longa do discovery, preservada no histórico do git; neste documento cada um aparece com o nome.
>
> **Terminologia.** Este documento usa "envelhecido" para uma oportunidade aberta há mais tempo do que o maior ciclo fechado. O rótulo "zumbi", do plano V6, foi substituído porque a idade não prova abandono.

**Status:** Auditoria executada  
**Data:** 15/10/2026  
**Etapa:** 3 | Data Discovery (insumo para o `discovery.md`)
**Script:** [solution/scripts/audit_data.py](../solution/scripts/audit_data.py)  
**Saídas brutas:** `solution/data/processed/audit_results.json` e `audit_log.txt`

**Pergunta que este documento responde:** _quais decisões e hipóteses do Business Discovery e do Domain & Value Discovery podem ser sustentadas pelos dados disponíveis, e o que isso muda na solução?_

<a id="como-ler"></a>
## Como ler

Toda afirmação carrega uma destas etiquetas:

| Etiqueta              | Significado                                                  |
| --------------------- | ------------------------------------------------------------ |
| **[FATO MEDIDO]**     | Número calculado pelo script nesta execução. Reproduzível.   |
| **[INTERPRETAÇÃO]**   | Leitura do fato. Pode estar errada; diz o que o fato sugere. |
| **[HIPÓTESE]**        | Explicação plausível que os dados não confirmam nem refutam. |
| **[NÃO VERIFICÁVEL]** | O dataset não contém o que seria preciso para testar.        |

Nada aqui implementa scoring, dashboard ou arquitetura. Os modelos da seção 2.9 são **sondas de viabilidade**, não candidatos.

<a id="a-1"></a>
## 1. Resumo em linguagem simples

_Para quem não é técnico, mas conhece o negócio._

### O que fizemos

Abrimos os cinco arquivos do CRM e conferimos três coisas: se os dados estão íntegros, se uma tabela conversa corretamente com a outra e, principalmente, **se existe algum padrão nos dados que ajude a dizer qual oportunidade tem mais chance de fechar**. Isso foi testado simulando o passado: "se a ferramenta existisse em junho, ela teria acertado o que aconteceu depois de junho?"

### O que encontramos

1. **A estrutura está boa.** Nenhum identificador repetido, nenhuma data impossível, nenhuma venda ganha com valor zero ou negativo. As tabelas se conectam.
2. **Mas há três armadilhas.**
   - O produto "GTX Pro" está escrito "GTXPro" nas oportunidades. Quem juntar as tabelas sem perceber perde em silêncio 1.480 linhas (16,8%).
   - A empresa cliente está em branco em **68% das oportunidades abertas** e em **0% das fechadas**. Ou seja, o dado que "treina" a ferramenta é mais completo do que o dado em que ela será usada.
   - 461 oportunidades abertas são idênticas entre si (só o código muda). Não dá para saber se são duplicadas ou apenas pouco preenchidas.
3. **Sabemos o resultado de 6.711 oportunidades; 63% foram ganhas.** Outras 2.089 estão abertas (1.589 em negociação e 500 em prospecção).
4. **A surpresa principal: com os campos atuais, quase nada prevê ganhar ou perder melhor do que "chutar a média" (63%).** Vendedor, produto, setor da empresa, escritório, gerente: as diferenças entre eles são do tamanho do acaso. Nas simulações, a nota (AUC) ficou entre 0,47 e 0,57 em uma escala em que 0,5 é o mesmo que sortear. O único sinal legítimo que se repetiu é muito fraco: em qual mês do trimestre o negócio começou.
5. **O único padrão forte é uma armadilha.** Negócios fechados em março, junho, setembro e dezembro foram ganhos em ~81% dos casos; nos outros meses, ~49% a 57%. Só que o mês de fechamento só se conhece _depois_ que o negócio fecha. Usá-lo para "prever" seria usar o futuro para adivinhar o passado: o resultado parece ótimo e não vale nada na vida real.
6. **81% dos negócios "em negociação" estão abertos há mais tempo do que qualquer negócio que já fechou** (o mais longo levou 138 dias). Ou são negócios esquecidos que ninguém encerrou, ou o histórico não captura os casos longos. Isso muda o que "parado" significa e precisa ser perguntado à empresa.
7. **Dá para estimar o valor de uma oportunidade aberta.** O preço de tabela reproduz o valor fechado com ~10% de erro. Mas isso é só o preço do produto: o "valor" não traz informação além de qual produto é.

### O que os dados não permitem saber

- Quanto tempo ou esforço o vendedor gasta em cada negócio.
- Quando um negócio "esfriou" (não há registro de contatos nem de mudanças de estágio).
- Como o vendedor prioriza hoje, e portanto se o "feeling" dele já é bom.
- Custo da hora do vendedor, margem, metas, comissões.
- Quantos negócios um vendedor consegue trabalhar bem.

### O que isso muda na ferramenta

- **Não prometa "probabilidade de ganhar" como se fosse precisa.** Com estes campos, a melhor estimativa honesta para qualquer negócio aberto é próxima de 63%.
- **O que os dados sustentam hoje** é ordenar por _valor em jogo_ (preço do produto) e sinalizar _idade do negócio_ e _qualidade do cadastro_. Se isso melhora o resultado do vendedor, os dados não têm como provar.
- **Antes de construir, é preciso perguntar** à Head de RevOps: quando a empresa é preenchida, por que tantos negócios passam de 138 dias abertos e o que significa "Lost".
- **Mais dados mudariam o quadro:** registro de atividades e histórico de estágio são o que falta para medir "esfriamento", e hoje não existem.

### Termos

**Taxa de ganho:** de cada 100 negócios que terminaram, quantos foram ganhos (aqui, 63). **Ciclo:** dias entre começar a negociar e fechar. **Truncamento:** o extrato só mostra parte da história, e isso distorce o que parece ser padrão. Vazamento, backtest e AUC estão no [glossário do discovery](./discovery.md#glossario).

---

<a id="a-2"></a>
## 2. Resultados técnicos

**Premissa de data de corte.** O dataset não informa a data de extração. Adotou-se **2017-12-31** (maior `close_date`). A sensibilidade ao corte está na linha V6 da seção 2.10.

<a id="a-2-1"></a>
### 2.1 Inventário (atividade 1)

| Tabela               | Linhas | Colunas | Período / faixa                                                             | Vazios relevantes                                                                             |
| -------------------- | ------ | ------- | --------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `accounts.csv`       | 85     | 7       | `year_established` 1979–2017                                                | `subsidiary_of` 70 (82,4%)                                                                    |
| `products.csv`       | 7      | 3       | `sales_price` 55–26.768                                                     | —                                                                                             |
| `sales_teams.csv`    | 35     | 3       | 6 managers, 3 escritórios                                                   | —                                                                                             |
| `sales_pipeline.csv` | 8.800  | 8       | `engage_date` 2016-10-20 a 2017-12-27; `close_date` 2017-03-01 a 2017-12-31 | `account` 1.425 (16,2%); `engage_date` 500 (5,7%); `close_date` e `close_value` 2.089 (23,7%) |
| `metadata.csv`       | 21     | 3       | —                                                                           | —                                                                                             |

- **[FATO MEDIDO]** O `metadata.csv` declara exatamente as 21 colunas existentes nas quatro tabelas; nenhuma divergência. Nenhum token do tipo `NA`/`null`/`unknown` e nenhum espaço sobrando nos campos de dados.
- **[FATO MEDIDO]** Tipos inferidos: datas em `AAAA-MM-DD` (0 não parseáveis); `close_value` inteiro (0 não numéricos).
- **[FATO MEDIDO]** A coluna `revenue` é descrita como milhões de US$; a receita por funcionário implícita fica entre US$ 273 mil e US$ 1,18 milhão (plausível).

<a id="a-2-2"></a>
### 2.2 Granularidade, chaves e cardinalidade (atividade 2)

| Tabela           | Granularidade            | Chave            | Duplicadas / nulas |
| ---------------- | ------------------------ | ---------------- | ------------------ |
| `accounts`       | 1 linha por empresa      | `account`        | 0 / 0              |
| `products`       | 1 linha por produto      | `product`        | 0 / 0              |
| `sales_teams`    | 1 linha por vendedor     | `sales_agent`    | 0 / 0              |
| `sales_pipeline` | 1 linha por oportunidade | `opportunity_id` | 0 / 0              |

| Relacionamento                        | Cardinalidade             | Medido                                                                                                                                                                  |
| ------------------------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| pipeline → `sales_teams`              | N:1                       | 30 dos 35 vendedores têm oportunidades (110 a 747 por vendedor; mediana 278). Sem nenhuma: Carl Lin, Carol Thompson, Elizabeth Anderson, Mei-Mei Johns, Natalya Ivanova |
| pipeline → `accounts`                 | N:1 (conta pode ser nula) | 85 de 85 contas aparecem; 51 a 200 oportunidades por conta (mediana 83)                                                                                                 |
| pipeline → `products`                 | N:1                       | 7 rótulos no pipeline, mas só 6 batem com o catálogo; `GTXPro` ≠ `GTX Pro`                                                                                              |
| `sales_teams` → manager               | N:1                       | 1 manager por vendedor; 6 managers; escritórios: Central 11, East 12, West 12                                                                                           |
| `accounts.subsidiary_of` → `accounts` | N:1                       | 15 preenchidos; 0 referências órfãs                                                                                                                                     |

- **[INTERPRETAÇÃO]** `sales_pipeline` é de fato a tabela fato; as outras são dimensões. Vendedor e manager são relação de **foto atual**: não há histórico de quem era o manager em cada data.
- **[NÃO VERIFICÁVEL]** Se algum dos 5 vendedores sem oportunidades está inativo, é novo ou foi desligado.

<a id="a-2-3"></a>
### 2.3 Duplicatas, inválidos e anomalias (atividade 3)

| Verificação                                            | Resultado                                                                                                                                                                         |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Linhas 100% duplicadas                                 | **0**                                                                                                                                                                             |
| Linhas idênticas exceto `opportunity_id`               | **461** em 109 grupos (maior grupo: 28). Todas abertas: 340 Prospecting + 121 Engaging; 0 entre fechadas. 449 das 461 têm `account` nula; as 340 Prospecting não têm nenhuma data |
| `close_date` < `engage_date`                           | 0                                                                                                                                                                                 |
| Won com `close_value` ≤ 0 / Lost com `close_value` > 0 | 0 / 0                                                                                                                                                                             |
| Estágio × campos obrigatórios                          | 0 violações (ver 2.5)                                                                                                                                                             |
| Outliers (1,5×IQR)                                     | `revenue` 6/85, `employees` 8/85, `close_value` dos Won 15/4.238                                                                                                                  |
| Rótulos suspeitos                                      | `sector = technolgy` (1.058 negócios fechados); `office_location = Philipines`                                                                                                    |
| Calendário                                             | Fechamentos distribuídos por todos os dias da semana, **inclusive fim de semana (28,4%)**                                                                                         |

- **[FATO MEDIDO]** Os 461 não são prova de duplicidade: quando conta e datas estão nulas, linhas distintas ficam idênticas por construção.
- **[INTERPRETAÇÃO]** Fechamentos uniformes em sábados e domingos não é comportamento de equipe comercial real.
- **[HIPÓTESE]** O dataset é sintético ou fortemente anonimizado (também apontado como risco de representatividade no discovery). Não é verificável pelo conteúdo.

<a id="a-2-4"></a>
### 2.4 Integridade de joins (atividade 4)

| Passo                                            | Linhas        | Observação                            |
| ------------------------------------------------ | ------------- | ------------------------------------- |
| Base: `sales_pipeline`                           | 8.800         | —                                     |
| Left join por nome **exato** do produto          | 8.800         | `sales_price` nulo em **1.480**       |
| Inner join por nome exato do produto             | **7.320**     | **perde 1.480 (16,8%) em silêncio**   |
| Left join por produto **normalizado**            | 8.800         | `sales_price` nulo em 0               |
| \+ `sales_teams` por `sales_agent`               | 8.800         | `manager` nulo em 0                   |
| \+ `accounts` por `account`                      | 8.800         | `sector` nulo em 1.425 (= conta nula) |
| Inner join com `accounts`                        | 7.375         | perderia 1.425 (16,2%), todas abertas |
| Auto-junção por `account` ("histórico da conta") | 712.135 pares | **96,6× as 7.375 linhas com conta**   |

- **[FATO MEDIDO]** Todos os joins das dimensões são N:1 (validados com `validate="m:1"`): **não multiplicam linhas**. O risco de multiplicação está em auto-junções por conta.
- **[FATO MEDIDO]** Evidência de que `GTXPro` = `GTX Pro`: razão mediana `close_value`/preço nos Won de 1,0015 contra o preço de `GTX Pro`; os demais rótulos ficam entre 0,97 e 1,00 do próprio preço. O rótulo `GTX Pro` nunca aparece no pipeline.
- **[INTERPRETAÇÃO]** O mapeamento é seguro, mas é decisão de limpeza a registrar, não dado original.

<a id="a-2-5"></a>
### 2.5 Completude condicionada ao estágio (atividade 3 e V2)

| Estágio     | n     | `engage_date` | `close_date` | `close_value` | `account`      |
| ----------- | ----- | ------------- | ------------ | ------------- | -------------- |
| Prospecting | 500   | 100% nulo     | 100% nulo    | 100% nulo     | **67,4% nulo** |
| Engaging    | 1.589 | 0%            | 100% nulo    | 100% nulo     | **68,5% nulo** |
| Won         | 4.238 | 0%            | 0%           | 0%            | 0%             |
| Lost        | 2.473 | 0%            | 0%           | 0%            | 0%             |

- **[FATO MEDIDO]** Os nulos de datas e valor são **estruturais** e coerentes com o `metadata.csv` (0 violações).
- **[FATO MEDIDO]** `account` nula: 68,2% dos abertos (1.425/2.089) contra 0% dos fechados (0/6.711). Entre vendedores, 61% a 90% dos abertos têm conta nula, então não é problema de um vendedor.
- **[INTERPRETAÇÃO]** A conta aparece como preenchida **no fechamento**. A conta ausente não depende do estágio aberto (67% em Prospecting, 69% em Engaging): depende de o negócio estar aberto.
- **[HIPÓTESE]** A conta é registrada tardiamente (por exemplo, ao qualificar ou fechar). Só a empresa confirma.

<a id="a-2-6"></a>
### 2.6 Distribuições (atividade 5)

| Estágio     | n     | %     |
| ----------- | ----- | ----- |
| Won         | 4.238 | 48,2% |
| Lost        | 2.473 | 28,1% |
| Engaging    | 1.589 | 18,1% |
| Prospecting | 500   | 5,7%  |

| Produto        | Total | Won | Lost | Engaging | Prospecting | Preço de tabela | Mediana `close_value` (Won) |
| -------------- | ----- | --- | ---- | -------- | ----------- | --------------- | --------------------------- |
| GTX Basic      | 1.866 | 915 | 521  | 337      | 93          | 550             | 547                         |
| MG Special     | 1.651 | 793 | 430  | 308      | 120         | 55              | 55                          |
| GTX Pro        | 1.480 | 729 | 418  | 253      | 80          | 4.821           | 4.828                       |
| MG Advanced    | 1.412 | 654 | 430  | 242      | 86          | 3.393           | 3.382,5                     |
| GTX Plus Basic | 1.383 | 653 | 398  | 258      | 74          | 1.096           | 1.083                       |
| GTX Plus Pro   | 968   | 479 | 266  | 176      | 47          | 5.482           | 5.503                       |
| GTK 500        | 40    | 15  | 10   | 15       | 0           | 26.768          | 25.897                      |

- **[FATO MEDIDO]** Valor fechado (Won): soma 10.005.534; média 2.360,9; mediana 1.117; máximo 30.288.
- **[FATO MEDIDO]** Por vendedor: total 110–747 (mediana 278); abertos 0–194 (mediana 72).
- **[FATO MEDIDO]** Cinco contas maiores = 11,8% das linhas com conta e 12,1% do valor Won. Não há concentração extrema.
- **[FATO MEDIDO]** Volume de engajamentos por mês sobe de 7 (out/2016) a 1.198 (jul/2017) e cai a 121 (dez/2017).
- **[INTERPRETAÇÃO]** GTK 500 (40 oportunidades, 25 fechadas) é grande demais em valor e pequeno demais em amostra: qualquer análise por produto fica instável nela.

<a id="a-2-7"></a>
### 2.7 Variável-alvo, abertas × fechadas e disponibilidade (atividades 6 e 7)

**Alvo candidato:** `won = 1` se `deal_stage = Won`; `0` se `Lost`; indefinido para Prospecting/Engaging.

| Medida                                       | Valor                                    |
| -------------------------------------------- | ---------------------------------------- |
| Rotuladas                                    | 6.711 de 8.800 (76,3%)                   |
| Won / Lost                                   | 4.238 / 2.473                            |
| Taxa de ganho                                | **63,15%** (IC95% 61,99% a 64,30%)       |
| Taxa de ganho ponderada pelo preço de tabela | 62,76%                                   |
| Sem rótulo (abertas)                         | 2.089 = Engaging 1.589 + Prospecting 500 |

**Matriz de disponibilidade (treino × inferência):**

| Campo                                                 | Fechadas (treino) | Engaging  | Prospecting | Classe                                 |
| ----------------------------------------------------- | ----------------- | --------- | ----------- | -------------------------------------- |
| `sales_agent`, `product` (normalizado), `sales_price` | 100%              | 100%      | 100%        | Seguro                                 |
| `manager`, `regional_office`                          | 100%              | 100%      | 100%        | Seguro, mas é foto atual               |
| `account`, `sector`, `revenue`…                       | 100%              | **31,5%** | **32,6%**   | Condicional: nulo em 68% dos abertos   |
| `engage_date`                                         | 100%              | 100%      | **0%**      | Disponível só a partir de Engaging     |
| `close_date`                                          | 100%              | 0%        | 0%          | **Vazamento**                          |
| `close_value`                                         | 100%              | 0%        | 0%          | **Vazamento** (Lost = 0 por definição) |
| `cycle_days` (`close − engage`)                       | 100%              | 0%        | 0%          | **Vazamento**                          |

- **[FATO MEDIDO]** Abertos com todas as features estáticas (conta presente): **501 Engaging e 163 Prospecting**, ou seja, 664 dos 2.089.
- **[FATO MEDIDO]** Para os 500 Prospecting não existe nenhuma data: só vendedor, produto e (em 33%) conta.
- **[INTERPRETAÇÃO]** Só deals fechados têm rótulo. Tratar abertos como "não ganhos" seria erro (censura): são alvo de predição, nunca negativos.

<a id="a-2-8"></a>
### 2.8 Vazamento (atividade 8)

AUC de uma única variável sobre os 6.711 fechados (Won = 1):

| Variável                                        | AUC       | Disponível na inferência? | Veredito                                                                                                 |
| ----------------------------------------------- | --------- | ------------------------- | -------------------------------------------------------------------------------------------------------- |
| `close_value > 0`                               | 1,000     | Não                       | É o próprio rótulo                                                                                       |
| Fechou no 3º mês do trimestre (mar/jun/set/dez) | **0,644** | Não                       | **Vazamento** (derivado de `close_date`)                                                                 |
| `cycle_days`                                    | 0,578     | Não                       | **Vazamento**                                                                                            |
| `engage_date` (ordinal)                         | 0,464     | Sim (Engaging)            | Legítimo, sinal fraco e confundido com o recorte                                                         |
| Mês-do-trimestre do engage                      | 0,546     | Sim (Engaging)            | Legítimo, sinal pequeno                                                                                  |
| `sales_price`                                   | 0,494     | Sim                       | Sem sinal                                                                                                |
| Ordem alfabética de `opportunity_id`            | 0,512     | —                         | Sem informação, como esperado                                                                            |
| Posição da linha no CSV                         | 0,464     | —                         | **Artefato**: o arquivo está ordenado por `engage_date` (verificado) e Prospecting começa na linha 8.300 |

- **[FATO MEDIDO]** Taxa de ganho por mês do fechamento: mar 82,1%, abr 48,6%, mai 54,4%, jun 82,8%, jul 49,1%, ago 56,8%, set 79,2%, out 49,3%, nov 52,9%, dez 78,5%. Por mês-do-trimestre: 1º = 49,0% (n=1.779), 2º = 54,7% (n=2.358), **3º = 80,7% (n=2.574)**. Homogeneidade por mês rejeitada (qui-quadrado p ≈ 5×10⁻¹¹⁷).
- **[FATO MEDIDO]** O mês de fechamento explica 8,4% da variância de Won × Lost (R² ajustado 0,084), de longe o maior efeito do dataset. Entre campos conhecidos na inferência, o maior é o mês do engage (ε² 1,6%), em grande parte efeito do truncamento descrito em 2.10; o mês-do-trimestre do engage explica 0,7%. Produto, vendedor, manager, escritório, setor e conta ficam em ε² ≤ 0,07%, ou negativo.
- **[INTERPRETAÇÃO]** O único "sinal forte" do dataset é um vazamento. Um modelo ingênuo que use datas de fechamento reportaria AUC ~0,6 a 0,65 e pareceria funcionar.
- **[HIPÓTESE]** O padrão reflete comportamento de fim de trimestre (negócios empurrados e fechados como ganhos). Não é verificável aqui.
- **[INTERPRETAÇÃO]** Outro vazamento sutil: `account` nula é sinal de "aberto", não de resultado. Uma regra "conta preenchida → ganha" não vale, porque entre fechados a conta é sempre preenchida.

<a id="a-2-9"></a>
### 2.9 Viabilidade de regras, modelos e baselines (atividade 9)

**Desenho (sonda).** Para cada corte T: treino = fechados com `close_date ≤ T`; teste = negócios já engajados em T e fechados depois. Features congeladas em T. Taxas por categoria suavizadas (m = 20). IC95% do AUC por bootstrap (300 reamostras).

| Corte T    | Treino | Teste | Taxa ganho treino | Taxa ganho teste |
| ---------- | ------ | ----- | ----------------- | ---------------- |
| 2017-05-31 | 2.038  | 930   | 0,615             | 0,739            |
| 2017-06-30 | 2.679  | 970   | 0,666             | 0,628            |
| 2017-07-31 | 3.306  | 1.139 | 0,633             | 0,651            |
| 2017-08-31 | 4.091  | 893   | 0,621             | 0,713            |
| 2017-09-30 | 4.726  | 935   | 0,644             | 0,598            |

AUC no teste, por corte:

| Modelo / regra                          | 05-31   | 06-30   | 07-31   | 08-31   | 09-30   |
| --------------------------------------- | ------- | ------- | ------- | ------- | ------- |
| B0 taxa global                          | 0,500   | 0,500   | 0,500   | 0,500   | 0,500   |
| B1 taxa por produto                     | 0,504   | 0,533   | 0,498   | 0,500   | 0,495   |
| B2 taxa por vendedor                    | 0,473   | 0,507   | 0,499   | 0,529   | 0,493   |
| B3 taxa por escritório                  | 0,477   | 0,502   | 0,489   | 0,499   | 0,498   |
| B4 taxa por setor da conta              | 0,487   | 0,504   | 0,516   | 0,516   | 0,475   |
| B5 mês-do-trimestre do engage           | 0,523   | 0,507   | 0,523   | 0,561   | 0,506   |
| LR produto + vendedor + mês-trim.       | 0,491   | 0,521   | 0,517   | 0,562   | 0,503   |
| LR + setor da conta                     | 0,492   | 0,522   | 0,519   | 0,558   | 0,498   |
| Idade em T (sem treino)                 | 0,571   | 0,499   | 0,475   | 0,561   | 0,505   |
| _[VAZAMENTO] fechou no 3º mês do trim._ | _0,645_ | _0,614_ | _0,618_ | _0,650_ | _0,631_ |

- **[FATO MEDIDO]** Todos os valores legítimos ficaram entre 0,47 e 0,57. A exceção de regularidade é B5 (mês-do-trimestre do engage): acima de 0,5 nos cinco cortes (0,506 a 0,561), mas fraco. Dos 40 intervalos de confiança (8 regras × 5 cortes), **5 excluem 0,5**: B5, as duas regressões e a idade no corte 08-31, e a idade no corte 05-31. A idade muda de lado (0,475 em 07-31; 0,571 em 05-31). Com 40 intervalos a 95%, cerca de 2 excluiriam 0,5 por acaso.
- **[FATO MEDIDO]** O Brier difere da taxa global em no máximo ±0,003. Só B5 melhora (−0,001 em 05-31 e −0,003 em 08-31); nos demais cortes e modelos, iguala ou piora.
- **[FATO MEDIDO]** A taxa de ganho do teste varia de 0,598 a 0,739 entre cortes: **a janela escolhida muda a métrica tanto quanto o modelo**.
- **[FATO MEDIDO]** Em 100% dos casos, as contas do teste já apareciam no treino.
- **[INTERPRETAÇÃO]** Com os campos disponíveis, **não há evidência de lift utilizável sobre a taxa global**: o melhor caso (AUC 0,56, Brier −0,003) é pequeno e instável. Com ~900 a 1.100 casos de teste, o experimento só detecta AUC acima de ~0,55; um efeito menor poderia existir e não foi visto.
- **[INTERPRETAÇÃO]** O resultado vale para essas features, esse corte e essa técnica. Não descarta (a) features que não existem no dataset (atividade, histórico de estágio), (b) interações não testadas, (c) treino por _snapshots_ de idade.
- **[INTERPRETAÇÃO]** **Esta sonda não é o backtest final.** Aqui o teste só inclui negócios que depois fecharam (ganhos ou perdidos). O backtest do Rankio (`scripts/backtest.py`, [relatório](../solution/data/processed/backtest_report.md)) inclui também as abertas que nunca fecham na base, e nele a idade separa mais (AUC médio de 0,604 na regra servida e de 0,616 em "mais nova primeiro"). A diferença vem da população: sem as que nunca fecham, a idade não tem direção estável (acima); com elas, as mais novas ganham mais em 90 dias porque as velhas quase nunca fecham. Por isso o README descreve a idade como um sinal que depende das negociações sem desfecho, não como preditor de ganho.
- **[NÃO VERIFICÁVEL]** Comparação com o "feeling" atual: a priorização do vendedor não está registrada, então não há baseline humano para bater.

**Viabilidade por abordagem (sem escolher arquitetura):**

| Abordagem                                            | Viável com estes dados?         | Observação                             |
| ---------------------------------------------------- | ------------------------------- | -------------------------------------- |
| Ordenar por valor em jogo (preço)                    | Sim                             | Proxy validado (2.10)                  |
| Sinalizar idade vs. ciclo típico                     | Parcial                         | Idade existe só para Engaging; ver V6  |
| Sinalizar qualidade de cadastro (conta nula, rótulo) | Sim                             | Mensurável                             |
| Taxa-base por segmento (produto, etc.)               | Sim, mas sem diferença          | Todos ≈ 60% a 65%                      |
| Modelo supervisionado de P(ganho)                    | Sem lift utilizável demonstrado | AUC 0,47 a 0,57, instável entre cortes |
| Probabilidade **calibrada** por deal                 | Só como taxa-base (~63%)        | Não discrimina                         |

<a id="a-2-10"></a>
### 2.10 Testes do plano de validação (V1–V14)

| ID                                   | Status                    | Resultado medido                                                                                                    |
| ------------------------------------ | ------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| V1 Chaves e joins                    | Executado                 | Chaves únicas; joins N:1; **1.480 linhas** perdidas por `GTXPro`; auto-junção por conta explode 96,6×               |
| V2 Completude por estágio            | Executado                 | Nulos de data/valor estruturais; `account` nula só em abertos (68,2%)                                               |
| V3 Datas coerentes                   | Executado                 | 0 inversões, 0 não parseáveis; corte adotado 2017-12-31; **nenhum fechamento antes de 2017-03-01**                  |
| V4 Lost = limpeza de CRM?            | Parcial                   | Sem concentração em fim de mês (Lost 3,0%, Won 3,3%, esperado 3,3%); dispersão diária 1,27; mas fim de semana 28,4% |
| V5 Ciclo por produto e resultado     | Executado                 | Mediana Won 47–69 d; Lost 12–34 d; P90 Won 102–116 d; máximo 138 d; bimodal                                         |
| V6 Envelhecidos em Engaging          | Executado                 | **1.291 de 1.589 (81,2%)** acima de 138 d; 1.432 (90,1%) acima do P90 Won do próprio produto; com o corte no maior `engage_date` (2017-12-27), 1.238 (77,9%) |
| V7 Sinal por segmento                | Executado                 | Nenhum segmento estático se distingue do acaso (qui-quadrado p entre 0,26 e 0,97)                                   |
| V8 Vendedor domina variância?        | Executado (simples)       | Vendedor: ε² ajustado 0,0007; produto+vendedor R² aj. 0,0009                                                        |
| V9 Preço como proxy                  | Executado                 | `close_value`/preço: média 0,996, dp 0,099; 95,9% dentro de ±20%; Pearson 0,9915                                    |
| V10 Concentração/repetição de contas | Parcial                   | Top-5 = 11,8%; 100% das contas do teste estão no treino                                                             |
| V11 Carga × desfecho                 | Executado (observacional) | Ver abaixo                                                                                                          |
| V12 Supera baselines?                | Executado como sonda      | Sem lift utilizável sobre a taxa global (2.9): AUC 0,47 a 0,57                                                      |
| V13 Replay de políticas              | **Não executado**         | Exige uma política de scoring; fora do escopo desta etapa                                                           |
| V14 Estabilidade temporal            | Executado                 | Taxa de ganho por mês: 48,6% a 82,8%; por trimestre 82,1%, 61,7%, 61,4%, 60,3%                                      |

**V11 — carga × desfecho.**

- **[FATO MEDIDO]** Carga = negócios com `engage_date` abertos do mesmo vendedor na data do engage (exclui Prospecting): média 64,5, mediana 61, máximo 169.
- **[FATO MEDIDO]** Sem controle, parece haver efeito: taxa de ganho 68,3% no quartil de menor carga e 60,1% no de maior; ρ de Spearman dentro do vendedor −0,066 e −0,296 contra o ciclo dos Won.
- **[FATO MEDIDO]** Restringindo a engajados entre 2017-03-01 e 2017-08-15 (fora do truncamento inicial e com tempo para fechar), ρ cai para −0,065 (ganho) e −0,059 (ciclo). **Controlando vendedor e mês, ρ = −0,007 (p = 0,67).**
- **[INTERPRETAÇÃO]** A associação aparente entre carga e desfecho é calendário (a carga cresce com o tempo no dataset e o recorte inicial é truncado), não capacidade. **Os dados não sustentam H-002**, mas também não a refutam, porque a capacidade real é desconhecida.

**V5/V14 — truncamento à esquerda.**

- **[FATO MEDIDO]** Para cada mês de engajamento anterior a 2017-03, o ciclo mínimo observado coincide com a distância até 2017-03-01: out/2016 = 123 d (distância 122), nov = 96 (91), dez = 63 (62), jan = 36 (29), fev = 5 (1).
- **[INTERPRETAÇÃO]** Negócios engajados antes de março só aparecem se fecharam depois de 2017-03-01. A taxa de ganho desses engajamentos (73% a 82% de nov/2016 a jan/2017, contra 55% a 67% de mar a out/2017) provavelmente está inflada por seleção.
- **[NÃO VERIFICÁVEL]** A regra de extração do dataset não está documentada.

---

<a id="a-3"></a>
## 3. Hipóteses do discovery × evidência

<a id="a-3-1"></a>
### 3.1 Problemas e hipóteses (seção 1.3 do discovery)

| ID                                              | Evidência medida                                                                                                                              | Evidência ausente                                      | Interpretação                                                                                                    | Implicação para o MVP                                                               |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| **P-001** Tempo demais em deals que não fecham  | **[FATO]** 36,9% dos fechados são Lost (2.473/6.711); Lost fecham com mediana de 14 d (Won: 57 d). 81% dos Engaging passam de 138 d           | Horas/atividade por deal; definição de "desqualificar" | **[INTERP.]** Há muito negócio parado, mas o dataset não mede tempo gasto. Tempo perdido é **[NÃO VERIFICÁVEL]** | Não prometer "horas liberadas". Usar idade e valor como sinais de revisão           |
| **P-002** Boas oportunidades esfriam            | **[FATO]** Idade em T tem AUC entre 0,475 e 0,571, sem direção estável                                                                        | Log de atividade; histórico de estágio; contrafactual  | **[NÃO VERIFICÁVEL]** Esfriamento não é mensurável. Idade isolada não prevê ganho                                | Alerta de "esfriando" só pode ser baseado em idade e, sem validação, é heurística   |
| **P-003** Priorização subjetiva, sem critério   | — (afirmação do briefing)                                                                                                                     | Registro de como cada vendedor decide                  | **[NÃO VERIFICÁVEL]**                                                                                            | Entrevistas; capturar decisões do vendedor no próprio produto                       |
| **H-001** Falta critério compartilhado          | **[FATO]** Taxa de ganho por vendedor 55,0% a 70,4%; qui-quadrado p = 0,26; ε² = 0,0007                                                       | Decisões do vendedor (quais deals trabalhou)           | **[INTERP.]** As diferenças entre vendedores não se distinguem do acaso. Isso não testa "critério", só resultado | Não usar vendedor como feature nem como ranking de pessoas                          |
| **H-002** Capacidade é o gargalo                | **[FATO]** Carga média 64,5 deals abertos por vendedor; efeito da carga some ao controlar vendedor × mês (ρ = −0,007)                         | Capacidade esperada; atribuição; Prospecting sem data  | **[INTERP.]** Sem evidência de que carga prejudique o resultado; capacidade é **[NÃO VERIFICÁVEL]**              | Manter hipótese aberta; incluir visão de carga como diagnóstico, não como conclusão |
| **H-003** Incentivos mantêm deals sem chance    | **[FATO]** 1.291 Engaging acima de qualquer ciclo fechado                                                                                     | Comissão, metas, regras de status                      | **[HIPÓTESE]** Podem ser deals "envelhecidos". **[NÃO VERIFICÁVEL]** pelos dados                                       | Perguntar à empresa antes de definir limiar de desqualificação                      |
| **H-004** Vendedor não vê padrões do portfólio  | **[FATO]** Taxa de ganho por produto 60,0% a 64,8%; por conta 53,1% a 75,0%; nenhum padrão significativo                                      | O que o vendedor consulta hoje                         | **[INTERP.]** Há pouco padrão para "mostrar": os segmentos são parecidos                                         | Explicar o ranking por valor e idade, não por "padrões de ganho"                    |
| **H-005** Qualidade do CRM limita a decisão     | **[FATO]** `GTXPro` (16,8%), `account` nula em 68% dos abertos, 461 linhas indistinguíveis, rótulos com grafia errada, 5 vendedores sem deals | Regras de preenchimento por estágio                    | **[INTERP.]** **Hipótese confirmada**: o dado é utilizável, mas exige limpeza e tem lacunas estruturais          | Pipeline de normalização documentado; recusar/avisar quando faltar conta            |
| **H-006** Histórico reflete priorização passada | **[FATO]** 81% dos Engaging estão fora do suporte do histórico fechado                                                                        | Atribuição e esforço                                   | **[NÃO VERIFICÁVEL]** Viés de seleção não é testável                                                             | Tratar qualquer score como "descrição do passado", com risco de _feedback loop_     |
| **H-007** O "feeling" já é razoável             | **[FATO]** Baselines simples ficaram entre AUC 0,47 e 0,57                                                                                    | A priorização atual do vendedor                        | **[NÃO VERIFICÁVEL]** Sem baseline humano, não se mede ganho incremental                                         | Prometer só o que for testável em piloto com controle                               |
| **H-008** Valor de deal aberto indefinido       | **[FATO]** `close_value`/preço: média 0,996, 95,9% dentro de ±20%                                                                             | Desconto, margem, valor anual                          | **[INTERP.]** Preço de tabela é um bom proxy do valor fechado. Mas é função só do produto                        | Valor esperado = preço; ranking por valor reduz-se a ranking por produto            |

<a id="a-3-2"></a>
### 3.2 Decisões do mapa (HD-01 a HD-08): o que os dados sustentam

| ID    | Decisão                         | Sustentada? | Por quê                                                                                                                          |
| ----- | ------------------------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------- |
| HD-01 | Vendedor: qual deal trabalhar   | **Parcial** | Valor em jogo é mensurável. P(ganho) não discrimina além da taxa-base                                                            |
| HD-02 | Vendedor: quando desqualificar  | **Parcial**   | Há referência de ciclo (≤ 138 d), mas idade não previu perda de forma estável (AUC 0,475 a 0,571) e 81% dos abertos a excedem    |
| HD-03 | Vendedor: quando reativar       | **Não verificável**     | Não há atividade nem histórico de estágio                                                                                        |
| HD-04 | Manager: onde intervir          | **Parcial** | Visão descritiva de carteira é possível; diferenças entre vendedores são indistinguíveis do acaso, com risco de cobrança injusta |
| HD-05 | Manager: forecast               | **Não verificável**   | Taxa de ganho oscila de 48,6% a 82,8% por mês; sem forecasts históricos; probabilidade não discrimina                            |
| HD-06 | Direção: metas e capacidade     | **Não verificável**     | Sem metas, capacidade, nem forecasts                                                                                             |
| HD-07 | RevOps: baseline e retorno      | **Parcial** | Dá para congelar taxa de ganho (63,2%), ciclo e ticket, mas sem custo, margem, e com calendário instável                         |
| HD-08 | CRM: campos e regras de estágio | **Sim**     | Completude por estágio, chaves, rótulos e datas foram mensurados                                                                 |

> **Classificação canônica:** [discovery.md, seção 2](./discovery.md#hipoteses). Em versões anteriores deste documento: HD-02 "Fraca"; HD-03 e HD-06 "Não"; HD-05 "Fraca". Os motivos da coluna "Por quê" não mudaram.

---

<a id="a-4"></a>
## 4. Sinais do Decision Signals Map: previsto × medido

| Sinal                                                 | Previsto no discovery | Medido nesta auditoria                                                                  |
| ----------------------------------------------------- | --------------------- | --------------------------------------------------------------------------------------- |
| S1 Estágio                                            | ✅                    | Só 2 estágios abertos (1.589 e 500). Sem dado de transição                              |
| S2 Idade vs. ciclo                                    | 🟡                    | Derivável só para Engaging; ciclo máximo fechado 138 d; sem poder preditivo demonstrado |
| S3 Produto                                            | ✅                    | Exige normalizar `GTXPro`; taxa 60% a 65%, sem diferença significativa                  |
| S4 Valor esperado                                     | 🟡                    | **Confirmado**: preço de tabela ≈ valor fechado                                         |
| S5 Perfil da conta                                    | ✅                    | Nulo em 68% dos abertos; sem efeito mensurável                                          |
| S6 Histórico da conta                                 | 🟡                    | Conta existe só nos fechados; auto-junção explode linhas                                |
| S7 Desempenho do vendedor                             | ✅                    | Diferenças indistinguíveis do acaso                                                     |
| S9 Carga                                              | 🟡                    | Reconstruível só para Engaging; efeito some com controle de tempo                       |
| S11 Momento do ciclo                                  | 🟡                    | Efeito grande no **fechamento** (vazamento); pequeno no engage (0,7%)                   |
| S13 `close_*`, ciclo                                  | Proibido              | **Confirmado**: é o maior sinal do dataset e é vazamento                                |
| S14 Atividade / S15 Motivo de perda                   | ❌                    | **Confirmado ausente**                                                                  |
| S18 Forecasts históricos / S19 Metas / S21 Custo-hora | ❌                    | **Confirmado ausente**                                                                  |
| S12 / S22 Completude e integridade                    | ✅                    | Medidos nesta seção                                                                     |

---

<a id="a-5"></a>
## 5. O que isso muda na solução (restrições, não arquitetura)

1. **O dataset não sustenta uma promessa de "probabilidade de ganho".** A comunicação deve mostrar a taxa-base (~63%) e deixar claro que quase não discrimina entre deals.
2. **O ranking possível hoje é por valor em jogo (preço do produto) e por sinais de higiene** (idade, conta ausente). Isso é uma _regra_, e seu efeito sobre o resultado não é verificável com estes dados.
3. **Qualquer backtest deve ser temporal, com vários cortes**, e reportar o intervalo, porque a janela muda a taxa-base de 0,60 a 0,74.
4. **Congelar features na data de decisão.** `close_date`, `close_value`, ciclo, mês de fechamento e a posição da linha no arquivo estão proibidos.
5. **A base de inferência (abertos) é diferente da de treino (fechados):** conta nula em 68%, idade fora do suporte em 81% dos Engaging e Prospecting sem data. O MVP precisa tratar "não pontuável" como saída válida.
6. **Normalização obrigatória:** `GTXPro → GTX Pro`; revisão dos rótulos `technolgy` e `Philipines`; registro da decisão sobre os 461 indistinguíveis.
7. **Vendedor, manager e escritório não devem ser features nem alvo de ranking de pessoas:** não há sinal e o risco de uso indevido é alto.
8. **Prospecting só tem vendedor, produto e (em 33%) conta.** Pontuação além do valor do produto não tem base.

---

<a id="a-6"></a>
## 6. Riscos, limitações e investigações pendentes (priorizados)

| #   | Prioridade  | Risco / limitação                                                                                             | Evidência     | Investigação / mitigação                                                                                           |
| --- | ----------- | ------------------------------------------------------------------------------------------------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------ |
| 1   | **Crítico** | Sinal preditivo legítimo fraco e instável (AUC 0,47 a 0,57): um modelo pode parecer rigoroso e entregar pouco | Seção 2.9     | Obter atividade e histórico de estágio; testar _snapshots_ e interações; calibrar expectativa com a Head de RevOps |
| 2   | **Crítico** | Vazamento por data de fechamento (R² 0,084) enganaria qualquer modelo ingênuo                                 | 2.8           | Lista de features proibidas; teste automático de vazamento no pipeline                                             |
| 3   | **Alto**    | 81% dos Engaging fora do suporte do histórico (> 138 d)                                                       | 2.10 V6       | Perguntar se são envelhecidos; simular sensibilidade à data de corte                                                     |
| 4   | **Alto**    | `account` nula em 68% dos abertos e 0% dos fechados (descompasso treino × inferência)                         | 2.5           | Descobrir quando a conta é registrada; avaliar o MVP sem features de conta                                         |
| 5   | **Alto**    | Janela de extração desconhecida e truncamento à esquerda (sem fechamentos antes de 2017-03-01)                | 2.10          | Obter regra de extração; restringir análises a janelas não truncadas                                               |
| 6   | **Alto**    | Taxa de ganho instável no calendário (48,6% a 82,8% por mês)                                                  | 2.8, 2.10 V14 | Backtests em vários cortes; reportar intervalo, não ponto                                                          |
| 7   | **Médio**   | Significado de "Lost" não definido (perda real × limpeza)                                                     | V4 parcial    | Entrevista com RevOps                                                                                              |
| 8   | **Médio**   | Qualidade/identidade: `GTXPro`, rótulos, 461 indistinguíveis, 5 vendedores sem deals                          | 2.3, 2.4      | Camada de limpeza documentada e testada                                                                            |
| 9   | **Médio**   | Amostras pequenas em células (GTK 500 com 25 fechados; IC de vendedor ±4 a 10 p.p.)                           | 2.6           | Agrupar ou recusar leitura por célula com n < 30                                                                   |
| 10  | **Médio**   | Representatividade: padrões compatíveis com dado sintético (fim de semana 28,4%, sem estrutura)               | 2.3           | Declarar a limitação; não generalizar para a empresa real                                                          |
| 11  | **Médio**   | Efeito de uma ferramenta sobre o resultado não é estimável (sem baseline humano, sem controle)                | 2.9           | Desenhar piloto com grupo de controle                                                                              |
| 12  | **Baixo**   | Foto atual de manager/escritório, sem histórico                                                               | 2.2           | Aceitar como limitação                                                                                             |

**Dados que seria preciso pedir à empresa (ordem de impacto):**

1. Log de atividades (contatos, próximos passos) e histórico de mudança de estágio.
2. Quando o campo `account` é preenchido e por que 68% dos abertos não o têm.
3. Por que negócios Engaging passam de 138 dias sem fechar; existe regra de expiração?
4. Definição de Lost e de cada estágio; data e regra de extração.
5. Como os deals são atribuídos e qual a capacidade esperada por vendedor.
6. Metas, comissão, custo-hora e margem.

---

<a id="a-7"></a>
## 7. Reprodutibilidade e registro de execução

**Ambiente.** Python 3.9.6 (sistema); `.venv` em `solution/`; pandas 2.2.3, numpy 2.0.2, scipy 1.13.1, scikit-learn 1.5.2 (fixados em `solution/requirements.txt`). Seeds: 20260101.

**Como reproduzir** (a partir de `submissions/alice-dantas/solution/`):

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/audit_data.py
```

**Integridade dos dados de entrada** (SHA-256, idêntico antes e depois da execução):

| Arquivo              | SHA-256                                                            |
| -------------------- | ------------------------------------------------------------------ |
| `accounts.csv`       | `e5242324768a563fc632cddfed49a29acbbf2892b8a3c6453cc9650de9ae0358` |
| `metadata.csv`       | `22b34e498d07e3d7f322afdbf81d70a5dc0a389792944e50ca2af86a3597f0af` |
| `products.csv`       | `7c1c8cbbdb6d4c286902e1985eeb529a36366d6a43f43cd4a93c4b1da2a6eb84` |
| `sales_pipeline.csv` | `825ce8f6c32d4009548b468df3173d55a46fd73f2531f532c5459371dc52adf2` |
| `sales_teams.csv`    | `aeff1272ebe196f5a27e3fc0578aa27abf48ed9ae461aa344fb95990e5ad8bd1` |

**Execuções e correções.**

| Execução | Resultado                                | Ação                                                                                                                                            |
| -------- | ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| 1        | Exit 0                                   | Revisão da saída encontrou: sonda de vazamento usando o 1º mês do trimestre (o padrão está no 3º); carga confundida com truncamento; formatação |
| 2        | Falhou: `UnboundLocalError: first_close` | Variável usada antes de ser definida; corrigido                                                                                                 |
| 3        | Exit 0                                   | Saída revisada                                                                                                                                  |
| 4        | Exit 0                                   | Adicionado controle vendedor × mês; saída **idêntica** à execução 3 nas demais linhas (determinístico)                                          |

O `check-data` confere os quatro CSVs que o Rankio lê (`accounts`, `products`, `sales_pipeline` e `sales_teams`); o `metadata.csv` só entrou na auditoria, para conferir as colunas.

**Exploração prévia.** Antes do script, três perfis ad hoc foram rodados para decidir o que auditar. **Nenhum número deste relatório vem deles**; todos vêm do script.

**Limitações do próprio script.**

- A decomposição de variância é simples (ε² e R² linear), sem modelo misto.
- O backtest usa taxas suavizadas e regressão logística de baixa complexidade, sem ajuste fino. Não esgota o espaço de modelos.
- A data de corte (2017-12-31) é premissa.
- V13 (replay de políticas) e custo/benefício não foram executados por dependerem de scoring e de dados que não existem.
