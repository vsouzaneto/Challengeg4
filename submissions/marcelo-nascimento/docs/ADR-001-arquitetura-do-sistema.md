# ADR-001 — Arquitetura do Sistema

**Status:** Aceita  
**Data:** 2026-09-24  
**Decisão:** Arquitetura inicial da aplicação de Lead Scoring

---

## 1. Contexto

O sistema tem como objetivo auxiliar vendedores na priorização de oportunidades comerciais.

A aplicação deve apresentar o pipeline de vendas, atribuir um score de `0` a `100` para cada oportunidade e explicar os fatores responsáveis pela pontuação.

A principal pergunta que o produto deve responder é:

> Em quais oportunidades o vendedor deve focar agora?

O score deve representar evidências de aderência entre o **cliente e o produto**, utilizando os dados disponíveis e o histórico comercial.

Além do scoring, a aplicação deve fornecer:

- autenticação;
- visualização do pipeline;
- listagem e detalhamento dos scores;
- justificativas;
- filtros;
- relatórios visuais.

O projeto já possui ambiente Docker executando frontend, backend e PostgreSQL.

Por se tratar de uma aplicação pequena, a arquitetura deve permanecer simples e evitar componentes cuja complexidade operacional não seja justificada pelos requisitos atuais.

---

# 2. Decisão

Será utilizada uma arquitetura web com frontend e backend separados, utilizando:

### Frontend

- React;
- Vite.

### Backend

- Node.js.

### Persistência

- PostgreSQL.

### Infraestrutura

O ambiente Docker existente será mantido, contendo:

```text
Frontend
Backend
PostgreSQL
```

Os caminhos são:

```text
solution/frontend para Frontend
solution/backend para Backend
```

Não serão adicionados outros bancos de dados, sistemas de cache, filas, mecanismos de busca ou serviços externos enquanto não houver requisito que os justifique.

---

# 3. Arquitetura lógica

A aplicação seguirá, conceitualmente, o fluxo:

```text
┌─────────────────────────┐
│         React           │
│        Frontend         │
└────────────┬────────────┘
             │
             │ HTTP / API
             ▼
┌─────────────────────────┐
│         Node.js         │
│          API            │
├─────────────────────────┤
│ Serviços / Regras       │
│ de Negócio              │
├─────────────────────────┤
│ Scoring Engine          │
│ Explanation Builder     │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│       PostgreSQL        │
└─────────────────────────┘
```

O frontend não acessará diretamente o PostgreSQL.

Toda interação com os dados e regras de negócio será realizada através do backend.

---

# 4. Responsabilidades do frontend

O frontend será responsável por:

- autenticação e manutenção da sessão do usuário;
- apresentação do pipeline;
- apresentação dos scores;
- ordenação e filtros disponíveis ao usuário;
- detalhamento das justificativas;
- dashboards;
- gráficos e relatórios;
- interação com a API.

O frontend não será responsável por:

- calcular scores;
- reproduzir fórmulas de scoring;
- inferir justificativas;
- consultar diretamente o banco;
- duplicar regras de negócio existentes no backend.

O score recebido da API será tratado como resultado da regra de negócio do backend.

---

# 5. Responsabilidades do backend

O backend será responsável por:

- autenticação;
- acesso ao PostgreSQL;
- disponibilização da API;
- consultas do pipeline;
- normalização necessária dos dados;
- cálculo dos scores;
- geração das justificativas;
- agregações necessárias para relatórios;
- aplicação das regras de negócio.

As regras de negócio não devem depender de componentes de interface.

---

# 6. Scoring Engine

O cálculo do Lead Score será implementado como um componente isolado da camada HTTP.

Conceitualmente:

```text
Opportunity
     +
Account
     +
Product
     +
Historical Data
     │
     ▼
Feature Calculator
     │
     ▼
Scoring Engine
     │
     ▼
Score Result
```

O motor deve receber os dados necessários para o cálculo e produzir um resultado estruturado.

Ele não deve:

- conhecer componentes React;
- produzir HTML;
- depender de Bootstrap;
- conhecer rotas ou componentes visuais;
- utilizar estado da interface.

Isso permite que o cálculo seja testado independentemente da API e da interface.

A fórmula exata será definida em `SPEC-001-scoring-engine.md`.

---

# 7. Modelo do score

O score estará sempre no intervalo:

```text
0 <= score <= 100
```

A pontuação será construída exclusivamente através de evidências relacionadas à oportunidade.

Não haverá score base.

Conceitualmente:

```text
score =
    product_account_fit
  + product_sector_fit
  + company_profile_fit
  + financial_fit
```

A distribuição inicial máxima definida para os fatores é:

| Fator | Pontuação máxima |
|---|---:|
| Produto × cliente | 35 |
| Produto × setor | 30 |
| Perfil da empresa × produto | 20 |
| Compatibilidade financeira | 15 |
| **Total** | **100** |

Os algoritmos utilizados para transformar evidências em pontos serão especificados na SPEC de scoring.

A ausência de evidência para determinado fator resulta em contribuição de `0` pontos para esse fator.

---

# 8. Scoring determinístico

O cálculo será determinístico.

Dado o mesmo conjunto de dados e a mesma versão das regras:

```text
score(input) = sempre o mesmo resultado
```

Não será utilizada LLM para:

- calcular score;
- determinar pesos;
- decidir evidências;
- alterar pontuação;
- interpretar ausência de dados.

Modelos generativos não fazem parte da arquitetura inicial do scoring.

---

# 9. Explicabilidade

O resultado do Scoring Engine não será apenas um número.

O contrato conceitual será:

```text
ScoreResult
├── score
├── factors[]
│   ├── factor
│   ├── points
│   ├── maxPoints
│   └── reason
└── justification
```

Exemplo conceitual:

```json
{
  "score": 78,
  "factors": [
    {
      "factor": "account_product_fit",
      "points": 30.1,
      "maxPoints": 35,
      "reason": "Forte histórico de sucesso deste produto ou família para o cliente."
    },
    {
      "factor": "sector_fit",
      "points": 21.9,
      "maxPoints": 30,
      "reason": "O produto apresenta bom histórico no setor deste cliente."
    }
  ],
  "justification": "A oportunidade apresenta forte aderência entre produto e cliente."
}
```

A estrutura definitiva será especificada na SPEC.

---

# 10. Explanation Builder

A geração da justificativa será separada do cálculo matemático do score.

Fluxo:

```text
Features
   │
   ▼
Scoring Engine
   │
   ├── score
   └── factors
          │
          ▼
  Explanation Builder
          │
          ▼
    justification
```

O `Explanation Builder` será determinístico.

Sua função será transformar os fatores calculados em explicações compreensíveis para o vendedor.

Ele não poderá modificar o score.

Isso mantém separadas:

- decisão matemática;
- explicação comercial da decisão.

---

# 11. Dados ausentes

O sistema deve funcionar com informações incompletas.

Dados ausentes não serão preenchidos artificialmente apenas para permitir o scoring.

Quando uma informação necessária para determinado fator não estiver disponível:

```text
contribuição do fator = 0
```

Os demais fatores continuam sendo calculados normalmente.

Exemplo:

```text
Produto × cliente       0 / 35
Produto × setor        24 / 30
Perfil da empresa      15 / 20
Compatibilidade        11 / 15
                       ───────
Score                  50 / 100
```

O sistema não redistribuirá os 35 pontos indisponíveis entre os demais fatores.

Portanto, os pesos máximos permanecem fixos mesmo diante de dados ausentes.

---

# 12. Normalização

Dados provenientes das fontes comerciais devem passar por normalização antes de serem utilizados pelo Scoring Engine.

O objetivo é impedir que diferenças puramente representacionais sejam interpretadas como entidades diferentes.

Existe, por exemplo, uma inconsistência conhecida:

```text
GTX Pro
GTXPro
```

Ambos representam o mesmo produto.

A normalização deve acontecer antes do cálculo do score.

O Scoring Engine deve trabalhar com entidades já identificadas e normalizadas, não implementar heurísticas textuais para descobrir produtos equivalentes durante cada cálculo.

---

# 13. Persistência

PostgreSQL será a única fonte persistente da aplicação.

O banco armazenará os dados necessários para:

- usuários;
- contas/clientes;
- produtos;
- oportunidades;
- histórico comercial;
- informações necessárias ao scoring.

A modelagem definitiva será especificada junto às necessidades funcionais das SPECS.

Alterações de schema devem ser reproduzíveis.

Não serão consideradas parte válida da arquitetura alterações manuais de banco que não possam ser recriadas no ambiente.

---

# 14. Cálculo sob demanda e dados derivados

O histórico comercial será armazenado como dado persistente.

Métricas e features derivadas desse histórico poderão ser calculadas pelo backend.

Nesta versão inicial, não será introduzida infraestrutura adicional especificamente para processamento assíncrono, filas ou pipelines analíticos.

Caso o volume de dados futuramente torne o cálculo sob demanda inadequado, poderá ser introduzida estratégia de:

- pré-cálculo;
- materialização;
- cache;
- processamento assíncrono.

Essa mudança exigirá nova decisão arquitetural.

---

# 15. API

Frontend e backend se comunicarão através de API HTTP.

A API deve expor recursos relacionados a:

- autenticação;
- pipeline;
- oportunidades;
- scores;
- detalhamento dos fatores;
- dados agregados necessários aos relatórios.

Os contratos específicos pertencem às SPECS.

O formato da API deve preservar a separação entre regra de negócio e apresentação.

---

# 16. Autenticação

A aplicação possuirá autenticação.

Existe apenas uma classe de usuário.

Consequentemente, a arquitetura inicial não possuirá:

- RBAC;
- múltiplas roles;
- ACL;
- níveis administrativos;
- matriz de permissões.

Um usuário autenticado pertence ao mesmo nível funcional que qualquer outro usuário autenticado.

A autenticação não deve ser confundida com autorização por papéis, que não é requisito desta versão.

---

# 17. Interface e dependências visuais

A interface utilizará React.

Os seguintes recursos serão carregados externamente:

- Bootstrap pelo CDN oficial;
- Font Awesome pelo CDN oficial;
- Roboto pelo Google Fonts.

Essas bibliotecas não devem ser instaladas como dependências locais.

Componentes React próprios poderão utilizar as classes fornecidas pelo Bootstrap.

A aplicação não adotará outro framework visual em paralelo.

---

# 18. Relatórios

Os relatórios serão produzidos a partir dos mesmos dados utilizados pela aplicação.

Agregações necessárias serão realizadas pelo backend/PostgreSQL e expostas através da API.

O frontend será responsável pela representação visual.

A definição dos relatórios obrigatórios e suas métricas pertence à `SPEC-002-aplicacao-e-interface.md`.

---

# 19. Testabilidade

A separação entre acesso a dados, cálculo e apresentação deve permitir testar o Scoring Engine sem iniciar o frontend.

Conceitualmente:

```text
fixtures / dados conhecidos
          │
          ▼
   Feature Calculator
          │
          ▼
    Scoring Engine
          │
          ▼
resultado esperado
```

Os testes devem conseguir verificar independentemente:

```text
factor(input)
score(input)
explanation(result)
```

Isso é particularmente importante porque o score é a principal regra de negócio do produto.

---

# 20. Decisões rejeitadas

## 20.1 Score base

Rejeitado.

O score deve representar apenas evidências observadas.

Adicionar uma pontuação inicial produziria uma informação sem correspondência com evidência real.

---

## 20.2 Redistribuição de pesos quando faltam dados

Rejeitada.

Redistribuir pontos faria duas oportunidades receberem escalas diferentes e dificultaria a comparação direta entre scores.

Os pesos permanecem fixos.

---

## 20.3 Scoring no frontend

Rejeitado.

Duplicaria regra de negócio e permitiria divergência entre clientes.

O cálculo pertence exclusivamente ao backend.

---

## 20.4 Uso de LLM para scoring

Rejeitado para a arquitetura inicial.

O requisito exige um score reproduzível, auditável e explicável.

O problema pode ser atendido através de regras determinísticas derivadas dos dados históricos disponíveis.

---

## 20.5 Microsserviços

Rejeitados.

O tamanho e os requisitos atuais do sistema não justificam a complexidade operacional.

O backend Node.js será uma única aplicação organizada internamente por responsabilidades.

---

## 20.6 Bancos ou serviços auxiliares

Redis, Elasticsearch, MongoDB e outras tecnologias de persistência ou cache não serão utilizados inicialmente.

PostgreSQL atende às necessidades atuais do produto.

---

# 21. Consequências

## Positivas

A arquitetura escolhida:

- mantém o sistema simples;
- centraliza regras de negócio;
- facilita testes;
- permite auditoria dos scores;
- mantém os scores comparáveis;
- evita dependência de IA generativa;
- reduz infraestrutura;
- permite evolução posterior sem antecipar complexidade.

## Limitações aceitas

O cálculo inicial poderá exigir consultas e agregações sobre o histórico comercial.

Essa abordagem é considerada adequada ao volume inicial do sistema.

Caso o volume de dados cresça significativamente, a estratégia de cálculo poderá precisar ser revisada.

---

# 22. Critério para revisão desta ADR

Uma nova ADR deverá ser criada caso seja necessário alterar decisões estruturais como:

- stack principal;
- mecanismo de persistência;
- arquitetura de frontend/backend;
- responsabilidade pelo scoring;
- natureza determinística do scoring;
- estratégia de processamento que introduza novos componentes de infraestrutura;
- introdução de IA generativa na decisão do score;
- introdução de múltiplos tipos de usuário ou modelo de autorização.

Mudanças internas que não alterem essas decisões podem ser realizadas sem nova ADR, desde que continuem compatíveis com as SPECS.