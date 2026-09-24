# SPEC-001 — Scoring Engine

**Status:** Aprovada para implementação  
**Data:** 2026-09-24  
**Dependência:** `ADR-001-arquitetura-do-sistema.md`

---

# 1. Objetivo

Esta SPEC define o comportamento do motor de Lead Scoring.

O sistema deve atribuir a cada oportunidade um score entre `0` e `100`, representando a força das evidências históricas de aderência entre:

- cliente;
- produto;
- setor;
- perfil da empresa;
- comportamento comercial observado.

O objetivo do score é permitir que o vendedor priorize oportunidades com maior evidência histórica de fit.

O motor deve produzir:

1. score final;
2. pontuação individual de cada fator;
3. dados utilizados para justificar cada fator;
4. justificativa textual compreensível.

---

# 2. Princípio fundamental

O score começa obrigatoriamente em:

```text
0
```

Não existe score base.

Não existe score neutro.

Não existe pontuação inicial.

Não existe compensação por ausência de dados.

Formalmente:

```text
score =
    account_product_points
  + sector_product_points
  + company_profile_points
  + financial_fit_points
```

com:

```text
0 <= score <= 100
```

Cada fator adiciona pontos somente quando existe evidência mensurável.

Se nenhum fator possuir evidência:

```text
score = 0
```

---

# 3. Escala

A pontuação máxima será distribuída da seguinte forma:

| Fator | Máximo |
|---|---:|
| Produto × cliente | 35 |
| Produto × setor | 30 |
| Perfil da empresa × produto | 20 |
| Compatibilidade financeira | 15 |
| **Total** | **100** |

Os pesos são fixos.

A ausência de dados em um fator não redistribui seu peso para os demais.

---

# 4. Dados utilizados

O cálculo utilizará as seguintes entidades.

## 4.1 Opportunity

Dados da oportunidade:

- `opportunity_id`
- `product`
- `account`
- `deal_stage`
- `engage_date`
- `close_date`
- `close_value`

## 4.2 Account

Dados disponíveis do cliente:

- `account`
- `sector`
- `year_established`
- `revenue`
- `employees`
- `office_location`
- `subsidiary_of`

## 4.3 Product

Dados disponíveis do produto:

- `product`
- `series`
- `sales_price`

## 4.4 Histórico comercial

Para cálculo de evidências históricas serão consideradas apenas oportunidades encerradas com:

```text
deal_stage = Won
```

ou:

```text
deal_stage = Lost
```

Oportunidades em:

```text
Prospecting
Engaging
```

não são evidência histórica de sucesso ou fracasso e não entram nas taxas utilizadas pelo scorer.

---

# 5. Prevenção de vazamento de dados

Ao calcular o score de uma oportunidade, a própria oportunidade não pode participar do histórico utilizado para calculá-la.

Quando houver uma data de referência disponível, somente oportunidades encerradas antes dessa data poderão ser consideradas.

Formalmente:

```text
historical.close_date < reference_date
```

Para oportunidades abertas, a data de referência será a data atual do cálculo.

Para testes históricos ou backtests, deverá ser possível fornecer explicitamente uma `reference_date`.

Isso impede que informações futuras influenciem artificialmente o score.

---

# 6. Normalização

Os dados devem ser normalizados antes de chegar ao Scoring Engine.

## 6.1 Strings

Valores textuais utilizados como identificadores devem:

- remover espaços externos;
- tratar aliases conhecidos;
- preservar o identificador canônico utilizado pela aplicação.

## 6.2 Produtos

Existe nos dados fornecidos a inconsistência conhecida:

```text
GTXPro
```

que representa:

```text
GTX Pro
```

O valor deve ser normalizado para o produto canônico:

```text
GTX Pro
```

O histórico não pode considerar esses valores como produtos diferentes.

## 6.3 Setores

Valores de setor também devem ser normalizados antes da agregação.

A normalização deve tratar diferenças representacionais conhecidas sem criar classificações novas arbitrariamente.

## 6.4 Valores ausentes

Strings vazias, valores inválidos e `NULL` devem ser tratados como ausência de informação.

O scorer não deve inventar valores para substituir dados ausentes.

---

# 7. Função de confiança histórica

Taxa de vitória pura não é suficiente.

Por exemplo:

```text
1 vitória / 1 oportunidade = 100%
```

não deve possuir a mesma força de evidência que:

```text
100 vitórias / 100 oportunidades = 100%
```

Será utilizado um ajuste determinístico de confiança.

Para:

```text
W = número de oportunidades Won
N = número total de oportunidades Won + Lost
K = constante de confiança
```

definir:

```text
confidence_adjusted_rate =
    (W / N) × (N / (N + K))
```

Simplificando:

```text
confidence_adjusted_rate =
    W / (N + K)
```

Quando:

```text
N = 0
```

o resultado é:

```text
0
```

Essa função não adiciona um prior ou score base.

Ela apenas reduz a força de evidências baseadas em amostras pequenas.

---

# 8. Fator 1 — Produto × cliente

**Máximo: 35 pontos**

Este é o fator de maior peso.

Ele mede o histórico comercial entre o cliente e:

1. o produto específico;
2. a família (`series`) à qual o produto pertence.

---

## 8.1 Evidência do produto exato

Buscar oportunidades históricas encerradas envolvendo:

```text
account = oportunidade.account
product = oportunidade.product
```

Calcular:

```text
exact_fit =
    exact_wins / (exact_total + 3)
```

onde:

```text
exact_total = exact_wins + exact_losses
```

A constante de confiança para produto exato será:

```text
K = 3
```

---

## 8.2 Evidência da família do produto

Buscar oportunidades históricas do mesmo cliente envolvendo produtos pertencentes à mesma `series`.

O próprio produto sendo avaliado deve ser excluído dessa segunda agregação para evitar contar a mesma evidência duas vezes.

Calcular:

```text
series_fit =
    series_wins / (series_total + 5)
```

A constante de confiança para família será:

```text
K = 5
```

---

## 8.3 Combinação

Produto exato representa evidência mais específica e recebe peso maior.

```text
account_product_fit =
    (0.70 × exact_fit)
  + (0.30 × series_fit)
```

Então:

```text
account_product_points =
    35 × account_product_fit
```

Limites:

```text
0 <= account_product_points <= 35
```

---

## 8.4 Ausência de histórico

Se não existir histórico do produto nem da família para o cliente:

```text
account_product_points = 0
```

Não utilizar média global para preencher essa ausência.

---

# 9. Fator 2 — Produto × setor

**Máximo: 30 pontos**

Este fator mede o comportamento histórico do produto dentro do setor ao qual o cliente pertence.

Exemplo conceitual:

```text
Produto: GTX Pro
Setor: Technology

Won: 80
Lost: 20
```

A evidência é compartilhada entre empresas pertencentes ao mesmo setor.

---

## 9.1 Cálculo

Selecionar oportunidades encerradas onde:

```text
product = oportunidade.product
account.sector = oportunidade.account.sector
```

Definir:

```text
W = sector_product_wins
N = sector_product_wins + sector_product_losses
```

Aplicar:

```text
sector_product_fit =
    W / (N + 10)
```

A constante de confiança será:

```text
K = 10
```

Então:

```text
sector_product_points =
    30 × sector_product_fit
```

---

## 9.2 Setor desconhecido

Se a conta não possuir setor:

```text
sector_product_points = 0
```

Se não houver histórico daquele produto naquele setor:

```text
sector_product_points = 0
```

---

# 10. Fator 3 — Perfil da empresa × produto

**Máximo: 20 pontos**

Este fator mede quanto o porte da empresa se aproxima do perfil observado das empresas que tiveram sucesso comercial com o produto.

Serão utilizadas:

- quantidade de funcionários;
- receita anual.

O ano de fundação não fará parte da versão inicial da fórmula.

Ele permanece disponível para análise futura, mas não há justificativa suficiente para assumir que empresas mais antigas ou mais novas possuem melhor fit.

---

# 11. População de referência do perfil

Para cada produto, selecionar as contas associadas a oportunidades:

```text
deal_stage = Won
```

para aquele produto.

O objetivo é construir um perfil dos clientes que efetivamente tiveram sucesso comercial com o produto.

Para evitar que várias vendas para a mesma empresa façam uma única conta dominar o perfil, cada conta deve aparecer **uma única vez** na população utilizada para calcular o perfil.

---

# 12. Perfil de funcionários

Calcular a mediana do número de funcionários das empresas que tiveram oportunidades `Won` para o produto:

```text
median_employees
```

Comparar com:

```text
account.employees
```

através de uma razão simétrica:

```text
employee_similarity =
    min(account.employees, median_employees)
    /
    max(account.employees, median_employees)
```

O resultado estará entre:

```text
0 e 1
```

Exemplo:

```text
mediana histórica = 1000
cliente = 800

similaridade = 800 / 1000 = 0.80
```

---

# 13. Perfil de receita

Calcular:

```text
median_revenue
```

das contas que tiveram oportunidades `Won` para o produto.

Então:

```text
revenue_similarity =
    min(account.revenue, median_revenue)
    /
    max(account.revenue, median_revenue)
```

Resultado:

```text
0 <= revenue_similarity <= 1
```

---

# 14. Combinação do perfil

Quando ambos os valores estiverem disponíveis:

```text
company_profile_fit =
    (employee_similarity + revenue_similarity) / 2
```

Então:

```text
company_profile_points =
    20 × company_profile_fit
```

---

# 15. Perfil com dados incompletos

Este fator possui duas evidências internas independentes, cada uma valendo no máximo 10 pontos.

Portanto, sua forma equivalente de cálculo é:

```text
company_profile_points =
    (10 × employee_similarity)
  + (10 × revenue_similarity)
```

Se `employees` estiver ausente:

```text
employee contribution = 0
```

Se `revenue` estiver ausente:

```text
revenue contribution = 0
```

Se ambos estiverem ausentes:

```text
company_profile_points = 0
```

Os pontos não são redistribuídos.

---

# 16. Fator 4 — Compatibilidade financeira

**Máximo: 15 pontos**

Este fator mede especificamente a compatibilidade entre o porte financeiro da empresa e o produto.

Apesar de `revenue` também participar do perfil da empresa, este fator responde a uma pergunta diferente:

> Empresas com capacidade financeira semelhante historicamente compram este produto?

O preço unitário do produto não deve ser simplesmente dividido pela receita anual da empresa.

Os dados possuem unidades diferentes:

```text
accounts.revenue = milhões de USD / ano
products.sales_price = preço unitário sugerido
```

e o dataset não informa quantidade esperada de unidades ou orçamento disponível.

Portanto, criar arbitrariamente uma relação:

```text
sales_price / revenue
```

seria uma regra sem sustentação nos dados.

---

# 17. Faixa financeira histórica

Para cada produto, utilizar as receitas das contas que tiveram oportunidades:

```text
deal_stage = Won
```

Calcular:

```text
Q1 = primeiro quartil da receita
Q2 = mediana da receita
Q3 = terceiro quartil da receita
```

O intervalo:

```text
Q1 <= account.revenue <= Q3
```

representa a faixa financeira central observada entre compradores históricos daquele produto.

---

# 18. Cálculo da compatibilidade financeira

Se:

```text
Q1 <= revenue <= Q3
```

então:

```text
financial_fit = 1
```

Fora da faixa, a similaridade deve diminuir proporcionalmente em relação ao limite mais próximo.

Para receita abaixo de `Q1`:

```text
financial_fit =
    revenue / Q1
```

Para receita acima de `Q3`:

```text
financial_fit =
    Q3 / revenue
```

Sempre limitar:

```text
0 <= financial_fit <= 1
```

Então:

```text
financial_fit_points =
    15 × financial_fit
```

---

# 19. Ausência de informação financeira

Se:

```text
account.revenue = NULL
```

então:

```text
financial_fit_points = 0
```

Se não houver histórico suficiente de compradores do produto para calcular os quartis:

```text
financial_fit_points = 0
```

Para esta versão, são necessárias pelo menos:

```text
4 contas distintas
```

com receita válida e oportunidade `Won` para calcular a faixa financeira.

---

# 20. Score final

Após calcular os quatro fatores:

```text
raw_score =
    account_product_points
  + sector_product_points
  + company_profile_points
  + financial_fit_points
```

Aplicar proteção:

```text
score = min(100, max(0, raw_score))
```

O valor apresentado ao usuário será:

```text
round(score)
```

O backend deve preservar os valores internos com precisão suficiente para permitir auditoria.

Os fatores podem ser retornados com uma casa decimal.

---

# 21. Exemplo

Considere uma oportunidade hipotética cujo cálculo produziu:

```text
Produto × cliente:
27.4 / 35

Produto × setor:
21.8 / 30

Perfil da empresa:
16.2 / 20

Compatibilidade financeira:
13.1 / 15
```

Então:

```text
raw_score =
27.4 + 21.8 + 16.2 + 13.1

raw_score = 78.5
```

Resultado apresentado:

```text
score = 79
```

Não existe nenhuma operação como:

```text
50 + fatores
```

ou:

```text
20 + fatores
```

O resultado é exclusivamente a soma das evidências.

---

# 22. Resultado do Scoring Engine

O motor deve retornar uma estrutura equivalente a:

```json
{
  "opportunityId": "ABC123",
  "score": 79,
  "rawScore": 78.5,
  "factors": [
    {
      "id": "account_product_fit",
      "label": "Produto × cliente",
      "points": 27.4,
      "maxPoints": 35
    },
    {
      "id": "sector_product_fit",
      "label": "Produto × setor",
      "points": 21.8,
      "maxPoints": 30
    },
    {
      "id": "company_profile_fit",
      "label": "Perfil da empresa",
      "points": 16.2,
      "maxPoints": 20
    },
    {
      "id": "financial_fit",
      "label": "Compatibilidade financeira",
      "points": 13.1,
      "maxPoints": 15
    }
  ],
  "justification": "...",
  "calculatedAt": "..."
}
```

Campos adicionais de auditoria podem ser retornados pelo domínio ou armazenados internamente, desde que não alterem esse comportamento.

---

# 23. Evidências para explicação

Além dos pontos, cada fator deve disponibilizar ao `Explanation Builder` as evidências utilizadas.

Exemplo conceitual:

```json
{
  "id": "sector_product_fit",
  "points": 21.8,
  "maxPoints": 30,
  "evidence": {
    "sector": "technology",
    "won": 34,
    "lost": 9,
    "sampleSize": 43
  }
}
```

Isso permite produzir justificativas baseadas em fatos reais.

---

# 24. Explanation Builder

A justificativa será determinística.

Ela não deve utilizar LLM.

O builder receberá:

```text
score
factors
evidence
```

e produzirá texto compreensível para o vendedor.

---

# 25. Classificação dos fatores para explicação

Para fins exclusivamente textuais, calcular:

```text
factor_ratio =
    points / maxPoints
```

Classificar:

```text
factor_ratio >= 0.75
→ evidência forte

factor_ratio >= 0.50 e < 0.75
→ evidência moderada

factor_ratio > 0 e < 0.50
→ evidência fraca

factor_ratio = 0
→ sem evidência
```

Essas classificações não adicionam nem removem pontos.

Servem apenas para geração de texto.

---

# 26. Justificativa geral

A justificativa deve destacar prioritariamente os fatores que mais contribuíram para o resultado.

Exemplo:

```text
Score 82.

Há forte histórico de sucesso deste produto com o cliente e boa aderência ao setor. O porte da empresa também é semelhante ao perfil dos compradores históricos.
```

Para score baixo:

```text
Score 18.

Há pouca evidência histórica de aderência entre este cliente e o produto. O produto também apresenta baixo histórico de sucesso no setor.
```

Para ausência significativa de dados:

```text
Score 24.

O histórico disponível fornece pouca evidência para esta oportunidade. Não há histórico suficiente entre este cliente e o produto para avaliar esse fator.
```

O texto nunca deve afirmar certeza de venda.

Evitar frases como:

```text
"Esta venda será fechada."
"Este cliente vai comprar."
"Há 82% de chance de fechar."
```

O score não é uma probabilidade calibrada de fechamento.

---

# 27. Significado do score

O score significa:

> força relativa das evidências históricas disponíveis de aderência entre cliente e produto.

O score **não significa**:

> probabilidade percentual de fechamento.

Portanto:

```text
score = 80
```

não significa:

```text
80% de chance de venda
```

Essa distinção deve ser preservada na API, interface e documentação.

---

# 28. Estágio da oportunidade

`deal_stage` não adicionará pontos ao score.

Um lead em `Engaging` não recebe automaticamente mais pontos que um lead em `Prospecting`.

O objetivo do score é medir fit comercial, não reproduzir a posição atual do funil.

O estágio poderá ser utilizado pela interface para:

- filtros;
- agrupamentos;
- relatórios;

mas não faz parte da fórmula desta versão.

---

# 29. Vendedor e equipe

Os seguintes campos não fazem parte do score:

- `sales_agent`;
- `manager`;
- `regional_office`.

O score deve avaliar a oportunidade entre produto e cliente, e não a performance histórica do vendedor responsável.

Esses dados poderão ser utilizados nos relatórios.

---

# 30. Close value

`close_value` não deve participar diretamente da fórmula inicial.

Ele representa o valor observado de uma oportunidade encerrada e pode sofrer influência de:

- quantidade;
- negociação;
- descontos;
- características específicas do contrato.

Não existe informação suficiente para interpretar valores maiores como evidência de maior fit.

O campo permanece disponível para relatórios e análises futuras.

---

# 31. Requisitos de pureza do motor

O núcleo matemático do Scoring Engine deve poder ser executado sem:

- React;
- servidor HTTP;
- acesso direto à interface;
- dependência de estado global.

Sempre que possível, as funções matemáticas devem receber dados e retornar resultados sem efeitos colaterais.

Exemplo conceitual:

```text
calculateAccountProductFit(history)
calculateSectorProductFit(history)
calculateCompanyProfile(account, buyers)
calculateFinancialFit(account, buyers)

calculateScore(features)
```

A organização exata dos arquivos é decisão de implementação, desde que preserve essa separação.

---

# 32. Consultas e agregações

O agente pode decidir se as agregações históricas serão:

- realizadas em SQL;
- realizadas no backend após consulta;
- divididas entre PostgreSQL e Node.js.

A decisão deve privilegiar:

- clareza;
- eficiência;
- testabilidade.

A fórmula documentada nesta SPEC não pode mudar em função dessa escolha.

---

# 33. Testes obrigatórios

O Scoring Engine deve possuir testes automatizados.

---

## 33.1 Score zero

Dada uma oportunidade sem qualquer evidência:

```text
account_product = 0
sector_product = 0
company_profile = 0
financial_fit = 0
```

esperado:

```text
score = 0
```

---

## 33.2 Ausência de score base

Criar explicitamente um teste que garanta:

```text
nenhuma evidência → score === 0
```

Esse teste é obrigatório e protege uma invariante do produto.

---

## 33.3 Limite superior

Nenhuma combinação pode produzir:

```text
score > 100
```

---

## 33.4 Histórico pequeno

Uma única vitória não pode produzir fit máximo.

Exemplo:

```text
W = 1
N = 1
K = 3

fit = 1 / 4
```

---

## 33.5 Histórico crescente

Mantendo a taxa de vitória equivalente, maior quantidade de evidência deve aumentar a confiança.

Por exemplo:

```text
1 Won / 1 total
```

deve possuir menor fit que:

```text
10 Won / 10 total
```

---

## 33.6 Dados ausentes

Testar independentemente ausência de:

- account;
- sector;
- revenue;
- employees;
- histórico do produto;
- histórico da série.

Nenhum desses casos deve causar falha do scorer.

---

## 33.7 Normalização

Garantir que:

```text
GTXPro
```

e:

```text
GTX Pro
```

sejam associados ao mesmo produto canônico antes do scoring.

---

## 33.8 Exclusão da própria oportunidade

Garantir que uma oportunidade sendo avaliada não possa influenciar seu próprio score histórico.

---

## 33.9 Somente negócios encerrados

Garantir que:

```text
Prospecting
Engaging
```

não sejam contabilizados como `Won` ou `Lost`.

---

## 33.10 Determinismo

Para o mesmo conjunto de dados:

```text
score(input) === score(input)
```

em execuções diferentes.

---

# 34. Critérios de aceite

A SPEC estará implementada quando:

- o backend conseguir calcular score para uma oportunidade;
- o score estiver entre 0 e 100;
- não existir score base;
- os quatro fatores estiverem implementados;
- cada fator puder retornar 0 independentemente;
- ausência de dados não causar erro;
- o histórico considerar apenas Won/Lost;
- pequenas amostras sofrerem ajuste de confiança;
- produtos estiverem normalizados;
- o resultado incluir decomposição dos fatores;
- o resultado possuir justificativa determinística;
- o score não for apresentado como probabilidade;
- os testes obrigatórios estiverem passando.

---

# 35. Fora do escopo desta SPEC

Não fazem parte desta SPEC:

- telas;
- layout;
- dashboard;
- gráficos;
- filtros visuais;
- autenticação;
- gerenciamento de usuários;
- aparência da aplicação;
- relatórios de vendedores;
- definição do fluxo de navegação.

Esses requisitos pertencem à `SPEC-002-aplicacao-e-interface.md`.

---

# 36. Possíveis evoluções futuras

Não implementar nesta versão, mas a arquitetura deve permitir futura avaliação de:

- recalibração dos pesos baseada em dados;
- novos fatores;
- comportamento temporal;
- recência do histórico;
- localização geográfica;
- relacionamento entre matriz e subsidiária;
- performance por família de produtos;
- modelos estatísticos supervisionados;
- avaliação offline do poder preditivo do score;
- comparação entre score e conversão real.

Essas possibilidades não constituem requisitos atuais.

Qualquer alteração da fórmula deverá ser documentada antes de ser incorporada ao produto.