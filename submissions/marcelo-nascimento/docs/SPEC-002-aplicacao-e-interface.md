# SPEC-002 — Aplicação e Interface

**Status:** Aprovada para implementação  
**Data:** 2026-09-24  
**Dependências:**

- `AGENTS.md`
- `ADR-001-arquitetura-do-sistema.md`
- `SPEC-001-scoring-engine.md`

---

# 1. Objetivo

Esta SPEC define os requisitos funcionais e visuais da aplicação de Lead Scoring.

A interface deve permitir que o vendedor responda rapidamente à pergunta:

> Em quais oportunidades devo focar agora?

O score calculado conforme `SPEC-001` será o principal elemento de priorização.

A aplicação terá quatro áreas principais:

1. Dashboard;
2. Listagem;
3. Relatórios;
4. Usuários.

Além dessas áreas, haverá uma tela pública de Login.
Instalar e utilizar React Router

---

# 2. Princípios da interface

A interface deve ser:

- mobile-first;
- responsiva;
- objetiva;
- orientada à priorização comercial;
- visualmente consistente;
- adequada para leitura rápida;
- funcional em desktop, tablet e celular.

O score deve possuir destaque visual, mas nunca aparecer sem contexto suficiente para que o usuário possa entender a oportunidade.

A aplicação deve evitar excesso de informação visual.

---

# 3. Sistema visual

A aplicação utilizará tema escuro.

A paleta obrigatória é:

| UI Layer | Nome | Hex | Aplicação |
|---|---|---|---|
| Canvas Base | Void Black | `#09090F` | Background principal |
| Surface Layer | Charcoal Deep Blue | `#12121E` | Cards, tabelas, métricas e superfícies |
| Primary Text | Cool Silver-White | `#E2E8F0` | Textos principais e métricas |
| Accent / Focus | Holographic Teal | `#06D6A0` | Hot Leads, scores altos, foco positivo |
| Secondary Accent | Iridescent Violet | `#8B5CF6` | Navegação, filtros e badges |
| Muted Action | Deep Slate | `#334155` | Bordas, estados inativos e informações secundárias |

Essas cores constituem a identidade visual base da aplicação.

---

# 4. Variáveis visuais

A paleta deve ser centralizada em CSS para evitar valores duplicados arbitrariamente pelos componentes.

Exemplo conceitual:

```css id="y2id5r"
:root {
    --color-canvas: #09090F;
    --color-surface: #12121E;
    --color-text-primary: #E2E8F0;
    --color-accent: #06D6A0;
    --color-secondary: #8B5CF6;
    --color-muted: #334155;
}
```

O agente pode criar variáveis derivadas quando necessárias para:

- hover;
- transparência;
- estados de interação;
- textos secundários;
- backgrounds auxiliares.

Essas variações devem permanecer visualmente coerentes com a paleta principal.

Não introduzir outra cor de destaque principal sem necessidade funcional.

---

# 5. Tipografia

A fonte principal será:

```text id="glwyx1"
Roboto
```

carregada através do Google Fonts.

Roboto deve ser utilizada como fonte padrão da aplicação.

---

# 6. Bootstrap

Bootstrap deve ser carregado através do CDN oficial.

Bootstrap será utilizado principalmente para:

- grid responsivo;
- utilities;
- formulários;
- tabelas;
- dropdowns;
- modais;
- componentes estruturais;
- comportamento responsivo.

A identidade visual não deve ser simplesmente o tema padrão do Bootstrap.

CSS próprio deverá aplicar a paleta definida nesta SPEC.

Não instalar Bootstrap através de NPM.

---

# 7. Font Awesome

Font Awesome deve ser carregado através do CDN oficial.

Os ícones da aplicação devem utilizar Font Awesome.

Não utilizar emojis como substitutos de ícones da interface.

---

# 8. Estrutura geral

Após autenticação, a aplicação terá a seguinte estrutura:

```text id="aw31ew"
┌──────────────────────────────────────────┐
│ Sidebar │                                │
│         │          Conteúdo              │
│         │                                │
│         │                                │
└──────────────────────────────────────────┘
```

Em dispositivos móveis, a sidebar deve poder ser recolhida/aberta.

O conteúdo principal deve ocupar o espaço disponível.

---

# 9. Navegação

O menu principal será uma sidebar.

Itens obrigatórios:

| Item | Ícone Font Awesome |
|---|---|
| Dashboard | `fa-gauge-high` |
| Listagem | `fa-list` |
| Relatórios | `fa-chart-line` |
| Usuários | `fa-users` |

Na parte inferior ou área apropriada da sidebar deve existir ação para:

```text id="0ocuzh"
Sair
```

utilizando ícone correspondente do Font Awesome.

---

# 10. Sidebar desktop

Em telas com espaço suficiente, a sidebar deve permanecer visível.

Ela deve apresentar:

- ícone;
- nome da seção;
- indicação clara da seção ativa.

A seção ativa deve utilizar o **Iridescent Violet (`#8B5CF6`)** como principal indicador visual.

A sidebar deve utilizar o tema escuro definido pela aplicação.

---

# 11. Sidebar mobile

A aplicação deve ser desenvolvida mobile-first.

Em telas pequenas:

- a sidebar não deve consumir permanentemente largura significativa;
- deve existir controle claro para abrir o menu;
- o menu deve aparecer sobre ou ao lado do conteúdo;
- selecionar uma opção deve fechar o menu quando apropriado;
- o usuário deve conseguir retornar ao conteúdo sem dificuldade.

Os mesmos itens e ícones utilizados no desktop devem permanecer disponíveis.

---

# 12. Login

A tela de login será pública.

Ela deve conter:

- identificação visual da aplicação;
- campo de usuário/e-mail conforme modelo de autenticação implementado;
- senha;
- botão de login;
- mensagem de erro para credenciais inválidas.

Não haverá:

- cadastro público;
- seleção de tipo de usuário;
- escolha de role.

Após autenticação válida:

```text id="0cl1lm"
Login → Dashboard
```

Usuários não autenticados não devem acessar as telas internas.

---

# 13. Dashboard

O Dashboard será a visão inicial após login.

Sua função é fornecer uma leitura rápida do estado atual do pipeline e destacar as oportunidades que merecem atenção.

O Dashboard não deve tentar substituir a Listagem completa.

---

# 14. Métricas principais

O Dashboard deve apresentar cards com pelo menos:

- oportunidades abertas;
- Hot Leads;
- score médio das oportunidades abertas;
- valor total do pipeline aberto.

Oportunidades abertas são aquelas em:

```text id="mq9ehx"
Prospecting
Engaging
```

O cálculo das métricas deve ser realizado a partir dos dados retornados pelo backend.

---

# 15. Hot Leads

Para fins de interface:

```text id="72hqum"
score >= 75
```

será considerado:

```text id="5lvqax"
Hot Lead
```

Essa classificação é exclusivamente uma convenção de apresentação e priorização.

Ela não modifica a fórmula definida na `SPEC-001`.

Hot Leads devem utilizar o **Holographic Teal (`#06D6A0`)** como destaque.

O sistema não deve afirmar que Hot Lead significa determinada probabilidade de fechamento.

---

# 16. Oportunidades prioritárias

O Dashboard deve possuir uma seção de oportunidades prioritárias.

Por padrão, apresentar oportunidades abertas ordenadas por:

```text id="sn95ve"
score DESC
```

Cada item deve apresentar pelo menos:

- cliente;
- produto;
- estágio;
- score;
- indicação visual quando for Hot Lead.

A interface deve permitir navegar da oportunidade para seus detalhes.

---

# 17. Distribuição dos scores

O Dashboard deve possuir visualização resumida da distribuição dos scores das oportunidades abertas.

Faixas de apresentação:

```text id="gzstfz"
0–24
25–49
50–74
75–100
```

Essas faixas são utilizadas apenas para visualização e agrupamento.

Não alteram a matemática do score.

---

# 18. Listagem

A tela de Listagem é a principal ferramenta operacional do vendedor.

Ela deve permitir visualizar, ordenar, pesquisar e filtrar as oportunidades.

Em desktop, deve priorizar formato tabular.

Em dispositivos móveis, a apresentação pode adaptar-se para cards ou outra representação responsiva que preserve as mesmas informações essenciais.

---

# 19. Dados da Listagem

Cada oportunidade deve apresentar pelo menos:

- cliente;
- produto;
- estágio;
- vendedor responsável;
- score;
- indicação de Hot Lead;
- ação para visualizar detalhes.

Quando o cliente não estiver disponível, a interface deve indicar claramente a ausência do dado em vez de inventar um nome.

---

# 20. Ordenação

A ordenação padrão será:

```text id="nbd4ug"
score DESC
```

O usuário deve poder ordenar pelo menos por:

- score;
- cliente;
- produto;
- estágio.

A ordenação deve ser visualmente identificável.

---

# 21. Pesquisa

A Listagem deve possuir busca textual.

A busca deve permitir localizar oportunidades pelo menos por:

- cliente;
- produto.

A busca deve funcionar em conjunto com os filtros ativos.

---

# 22. Filtros

A Listagem deve possuir filtros para:

- estágio;
- produto;
- setor;
- vendedor;
- faixa de score.

Faixas de score:

```text id="g33pf9"
0–24
25–49
50–74
75–100
```

Filtros ativos devem ser visualmente identificáveis.

O **Iridescent Violet (`#8B5CF6`)** pode ser utilizado para indicar filtros ativos.

Deve existir forma simples de limpar os filtros.

---

# 23. Paginação

A Listagem deve possuir paginação.

Não carregar obrigatoriamente todas as oportunidades para o navegador para então realizar paginação exclusivamente no frontend.

A API deve permitir recuperar os dados necessários de forma paginada.

A paginação deve preservar:

- filtros;
- pesquisa;
- ordenação.

---

# 24. Detalhamento da oportunidade

Ao selecionar uma oportunidade, o usuário deve conseguir visualizar os detalhes do score.

O detalhamento pode ser implementado como:

- página;
- painel;
- drawer;
- modal.

A escolha exata é decisão de implementação, desde que funcione adequadamente em mobile e desktop.

---

# 25. Conteúdo do detalhamento

O detalhamento deve apresentar:

### Oportunidade

- cliente;
- produto;
- estágio;
- vendedor;
- datas disponíveis;
- valor disponível.

### Score

O score deve possuir forte destaque visual.

Exemplo:

```text id="v5skjr"
82 / 100
```

Se:

```text id="kvivhm"
score >= 75
```

o destaque principal deve utilizar Holographic Teal.

---

# 26. Breakdown do score

O detalhamento deve apresentar os quatro fatores definidos na `SPEC-001`:

```text id="t26oz1"
Produto × cliente
Produto × setor
Perfil da empresa
Compatibilidade financeira
```

Exemplo:

```text id="pz72a2"
Produto × cliente          29.4 / 35
Produto × setor            24.2 / 30
Perfil da empresa          17.0 / 20
Compatibilidade financeira 11.5 / 15
```

O usuário deve conseguir compreender visualmente quanto cada fator contribuiu para o resultado.

Barras de progresso ou representação equivalente podem ser utilizadas.

---

# 27. Justificativa

A justificativa produzida pelo backend deve ser apresentada junto ao score.

Exemplo:

```text id="ym50ax"
Há forte histórico de sucesso deste produto com o cliente e boa aderência ao setor. O porte da empresa também é semelhante ao perfil dos compradores históricos.
```

O frontend não deve gerar sua própria justificativa.

---

# 28. Evidências

Quando disponibilizadas pela API, evidências adicionais podem ser exibidas no detalhamento.

Exemplo:

```text id="1uobze"
Produto × setor

34 oportunidades Won
9 oportunidades Lost
43 oportunidades históricas analisadas
```

O objetivo é permitir que o usuário compreenda de onde veio a avaliação.

Não é necessário expor fórmulas matemáticas ao vendedor.

---

# 29. Relatórios

A tela de Relatórios deve fornecer visão analítica do pipeline e dos scores.

Os relatórios devem utilizar gráficos e métricas visuais.

O backend deve fornecer as agregações necessárias.

O frontend é responsável pela representação.

---

# 30. Relatórios obrigatórios

A primeira versão deve apresentar pelo menos:

### Distribuição de scores

Quantidade de oportunidades por faixa:

```text id="v1tw8c"
0–24
25–49
50–74
75–100
```

### Score médio por produto

Permitir comparar a aderência observada das oportunidades por produto.

### Score médio por setor

Permitir comparar as oportunidades agrupadas por setor.

### Pipeline por estágio

Apresentar quantidade de oportunidades em:

```text id="5igofn"
Prospecting
Engaging
Won
Lost
```

### Conversão histórica por produto

Utilizar negócios encerrados para apresentar:

```text id="d4cc0p"
Won
Lost
taxa histórica
```

A taxa histórica deve ser apresentada como dado histórico e não como previsão de oportunidades abertas.

---

# 31. Filtros dos relatórios

Quando aplicável, os relatórios devem permitir filtros por:

- produto;
- setor;
- vendedor;
- estágio.

Os filtros devem seguir o mesmo padrão visual da Listagem.

---

# 32. Gráficos

A biblioteca utilizada para gráficos pode ser escolhida pelo agente implementador, desde que:

- seja compatível com React;
- não introduza dependência excessiva;
- suporte responsividade;
- permita adequação à paleta visual;
- seja utilizada apenas para visualização.

Os gráficos devem respeitar o tema escuro.

Labels e valores precisam possuir contraste adequado.

---

# 33. Usuários

A tela de Usuários será responsável pelo gerenciamento dos usuários capazes de acessar a aplicação.

Todos os usuários pertencem à mesma classe.

Não existem roles.

---

# 34. Listagem de usuários

A tela deve apresentar pelo menos:

- nome;
- e-mail/identificador utilizado no login;
- status;
- ações disponíveis.

Status:

```text id="l70af7"
Ativo
Inativo
```

---

# 35. Criação de usuário

Deve ser possível criar usuário informando:

- nome;
- e-mail/identificador;
- senha inicial.

Não deve existir campo para selecionar role ou nível de permissão.

---

# 36. Edição de usuário

Deve ser possível alterar:

- nome;
- e-mail/identificador;
- status.

Também deve existir mecanismo para definir nova senha quando necessário.

Senhas nunca devem ser exibidas na interface.

---

# 37. Desativação

Usuários devem poder ser desativados.

Usuário inativo não poderá autenticar-se.

Quando possível, preferir desativação à exclusão física do registro.

---

# 38. Segurança das senhas

Senhas nunca devem ser armazenadas em texto puro.

O backend deve utilizar hash adequado para armazenamento de credenciais.

A interface nunca deve receber o hash da senha.

Criar usuário padrão admin@leadscore.local com a senha lead@teste55

---

# 39. Estados de carregamento

Operações assíncronas devem possuir indicação visual de carregamento.

Isso inclui pelo menos:

- autenticação;
- carregamento do Dashboard;
- Listagem;
- aplicação de filtros que dependam da API;
- relatórios;
- gerenciamento de usuários.

A interface não deve aparentar estar congelada durante chamadas ao backend.

---

# 40. Estado vazio

Listas e relatórios sem resultados devem apresentar estado vazio compreensível.

Exemplo:

```text id="e4npl3"
Nenhuma oportunidade encontrada com os filtros selecionados.
```

Não apresentar simplesmente uma tabela vazia sem explicação.

---

# 41. Erros

Falhas de API devem possuir tratamento visual.

O usuário deve receber mensagem compreensível.

Detalhes internos como:

- stack traces;
- SQL;
- paths internos;
- mensagens técnicas sensíveis;

não devem ser exibidos na interface.

---

# 42. Responsividade

A aplicação deve ser funcional a partir de telas móveis.

Não será considerado suficiente construir primeiro uma interface desktop e apenas permitir overflow horizontal no celular.

Componentes devem ser projetados para adaptação real.

Prioridades mobile:

- navegação acessível;
- score imediatamente visível;
- identificação do cliente;
- identificação do produto;
- filtros utilizáveis;
- detalhamento legível.

---

# 43. Tabelas em mobile

Tabelas extensas não devem depender exclusivamente de scroll horizontal para funcionar.

Quando necessário, registros podem ser apresentados como cards em telas menores.

Exemplo conceitual:

```text id="ycy07j"
┌───────────────────────────────┐
│ Acme Corporation       82     │
│ GTX Pro              HOT      │
│ Engaging                       │
│                               │
│ Ver detalhes →                │
└───────────────────────────────┘
```

---

# 44. Hierarquia visual do score

Na Listagem e no Dashboard, o score deve possuir maior peso visual que informações secundárias.

Entretanto, não deve ocupar espaço desproporcional.

Hot Leads devem ser facilmente reconhecíveis sem exigir leitura detalhada.

---

# 45. Uso das cores de destaque

## Holographic Teal — `#06D6A0`

Utilizar principalmente para:

- Hot Leads;
- scores de alta prioridade;
- indicadores positivos relacionados ao score;
- foco em oportunidades prioritárias.

## Iridescent Violet — `#8B5CF6`

Utilizar principalmente para:

- navegação ativa;
- filtros ativos;
- badges de sistema;
- elementos interativos secundários.

## Deep Slate — `#334155`

Utilizar principalmente para:

- bordas;
- divisores;
- elementos inativos;
- informações de menor prioridade.

As cores de destaque não devem ser utilizadas indiscriminadamente.

---

# 46. Acessibilidade visual

A utilização da cor não deve ser o único mecanismo para transmitir informação.

Por exemplo, Hot Lead deve possuir:

- cor;
- score numérico;
- label ou indicador equivalente.

Estados ativos devem possuir indicação além de uma diferença de tonalidade difícil de perceber.

Controles interativos devem possuir estados de foco visíveis.

---

# 47. Formatação

Valores monetários devem possuir formatação consistente.

Datas devem possuir formato consistente em toda a aplicação.

Scores apresentados como prioridade devem utilizar números inteiros:

```text id="k0brzp"
82
```

Breakdown técnico pode utilizar uma casa decimal:

```text id="45zdkg"
29.4 / 35
```

---

# 48. API necessária

A implementação deverá fornecer endpoints ou contratos equivalentes capazes de atender:

```text id="ak1l4w"
Autenticação

Dashboard
    métricas
    oportunidades prioritárias
    distribuição de scores

Oportunidades
    listagem paginada
    pesquisa
    filtros
    ordenação
    detalhe
    score
    fatores
    justificativa

Relatórios
    distribuição
    produto
    setor
    estágio
    conversão histórica

Usuários
    listagem
    criação
    edição
    ativação/desativação
    alteração de senha
```

A organização exata das URLs é decisão de implementação.

---

# 49. Performance da Listagem

Filtros, paginação e ordenação devem ser suportados adequadamente pelo backend.

A interface não deve depender de baixar todo o dataset para então:

```text id="7msnd6"
filter()
sort()
paginate()
```

no navegador.

Isso mantém a arquitetura adequada caso o número de oportunidades aumente.

---

# 50. Persistência de score

A estratégia de calcular scores sob demanda ou persistir resultados derivados pode ser escolhida conforme a implementação definida pela arquitetura existente.

Independentemente da estratégia:

- a fórmula deve permanecer única;
- frontend e relatórios devem utilizar a mesma lógica;
- não podem existir duas implementações diferentes do scorer;
- um score desatualizado não deve ser apresentado como atual silenciosamente.

---

# 51. Rotas conceituais do frontend

A aplicação deve possuir rotas equivalentes a:

```text id="yqgfp8"
/login

/dashboard
/leads
/reports
/users
```

Os nomes técnicos podem variar desde que a estrutura de navegação definida nesta SPEC seja preservada.

---

# 52. Componentes compartilhados

Elementos repetidos devem ser componentizados quando isso reduzir duplicação real.

Exemplos naturais:

```text id="as1fs8"
Sidebar
ScoreBadge
LeadCard
MetricCard
Filters
LoadingState
EmptyState
ErrorState
```

Não criar um design system complexo para uma aplicação deste porte.

---

# 53. Critérios de aceite — Login

Considerado concluído quando:

- usuário válido consegue autenticar;
- usuário inválido recebe erro;
- usuário inativo não consegue autenticar;
- usuário não autenticado não acessa áreas internas;
- logout encerra o acesso autenticado;
- senha não é armazenada em texto puro.

---

# 54. Critérios de aceite — Dashboard

Considerado concluído quando:

- apresenta as métricas definidas;
- apresenta Hot Leads;
- apresenta oportunidades prioritárias;
- apresenta distribuição de scores;
- oportunidades são priorizadas pelo score;
- dados são obtidos do backend;
- funciona em mobile e desktop.

---

# 55. Critérios de aceite — Listagem

Considerada concluída quando:

- apresenta as oportunidades;
- ordenação padrão é por score decrescente;
- possui pesquisa;
- possui filtros;
- possui paginação;
- permite acessar detalhes;
- apresenta score e Hot Lead;
- mantém usabilidade em mobile.

---

# 56. Critérios de aceite — Detalhamento

Considerado concluído quando apresenta:

- dados da oportunidade;
- score;
- quatro fatores;
- contribuição de cada fator;
- justificativa;
- evidências quando fornecidas;
- tratamento de dados ausentes.

---

# 57. Critérios de aceite — Relatórios

Considerados concluídos quando apresentam:

- distribuição dos scores;
- score médio por produto;
- score médio por setor;
- pipeline por estágio;
- conversão histórica por produto;
- filtros aplicáveis;
- visualização responsiva.

---

# 58. Critérios de aceite — Usuários

Considerado concluído quando:

- usuários podem ser listados;
- usuários podem ser criados;
- dados permitidos podem ser editados;
- senha pode ser redefinida;
- usuário pode ser ativado/desativado;
- não existem roles;
- senhas e hashes nunca são expostos.

---

# 59. Fora do escopo

Não fazem parte desta versão:

- cadastro público;
- recuperação automática de senha por e-mail;
- múltiplas roles;
- permissões diferenciadas;
- notificações;
- integração com CRM externo;
- edição manual do score;
- edição manual dos pesos;
- configuração da fórmula pela interface;
- IA generativa;
- chat;
- exportações avançadas;
- customização individual de dashboard;
- temas alternativos.

Essas funcionalidades somente devem ser implementadas mediante nova especificação.

---

# 60. Regra final

A interface existe para tornar o Lead Scoring operacional.

A prioridade visual deve seguir:

```text id="zn2hzv"
Onde focar
    ↓
Por que focar
    ↓
Contexto da oportunidade
    ↓
Análise agregada
```

O sistema não deve esconder o score em dashboards complexos nem apresentar métricas secundárias com maior destaque que a priorização das oportunidades.

A experiência deve permitir que o vendedor abra a aplicação e identifique rapidamente quais oportunidades merecem atenção e quais evidências sustentam essa priorização.