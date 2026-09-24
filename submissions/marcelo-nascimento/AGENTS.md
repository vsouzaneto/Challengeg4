AGENTS.md

1. Objetivo

Este repositório contém uma aplicação de Lead Scoring para Vendas.

O objetivo do sistema é permitir que vendedores visualizem o pipeline comercial priorizado por um score de 0 a 100, indicando quais oportunidades apresentam maior aderência entre cliente e produto.

Para cada oportunidade, o sistema deve fornecer:

* score de 0 a 100;
* justificativa do score;
* decomposição dos fatores que contribuíram para o score.

O sistema também deve disponibilizar visualizações e relatórios que permitam compreender e comparar as oportunidades do pipeline.

⸻

2. Fonte de verdade

A implementação deve seguir a documentação existente no repositório.

Ordem de autoridade:

1. AGENTS.md
2. ADRs em /docs
3. SPECS em /docs
4. ROADMAP.md
5. Código existente

As responsabilidades são:

* AGENTS.md: regras globais e restrições do projeto;
* ADR: decisões arquiteturais;
* SPECS: comportamento esperado do sistema;
* ROADMAP: ordem e dependências da implementação.

Em caso de conflito entre documentos, prevalece o documento de maior autoridade.

O agente não deve reinterpretar requisitos explícitos para facilitar a implementação.

⸻

3. Stack obrigatória

Frontend

* React
* Vite
* JavaScript/TypeScript conforme definido pelo projeto existente
* Bootstrap via CDN oficial
* Font Awesome via CDN oficial
* Roboto via Google Fonts

Backend

* Node.js

Banco de dados

* PostgreSQL

Infraestrutura

O projeto já possui Docker configurado e executando:

* frontend;
* backend;
* PostgreSQL.

A infraestrutura existente deve ser preservada, salvo quando uma alteração for necessária para atender às SPECS ou ADRs.

Não adicionar frameworks, bancos de dados, serviços ou componentes de infraestrutura sem necessidade técnica justificada.

⸻

4. Princípios de implementação

A implementação deve privilegiar:

* simplicidade;
* legibilidade;
* baixo acoplamento;
* separação clara de responsabilidades;
* comportamento determinístico;
* testabilidade;
* rastreabilidade do cálculo do score.

Este é um sistema pequeno.

Não criar abstrações, serviços, camadas ou infraestrutura antecipadamente para necessidades que não existem nas SPECS.

Evitar overengineering.

⸻

5. Arquitetura

A aplicação deve manter separação entre:

Frontend
    ↓
API Node.js
    ↓
Serviços / regras de negócio
    ↓
PostgreSQL

A regra de Lead Scoring pertence ao backend.

O frontend nunca deve calcular ou reconstruir o score.

O frontend recebe da API o resultado calculado e é responsável apenas por sua apresentação e interação com o usuário.

A arquitetura detalhada é definida pela ADR correspondente.

⸻

6. Lead Scoring

O Lead Scoring é uma regra de negócio central do sistema.

O score deve estar sempre no intervalo:

0 <= score <= 100

Invariante fundamental

O score começa em 0. Não existe score base.

São proibidos:

* score inicial diferente de zero;
* baseline;
* score neutro;
* constante adicionada ao cálculo;
* pontuação automática apenas pela existência da oportunidade;
* compensação de pontos pela ausência de dados.

O score deve ser exclusivamente resultado das evidências encontradas para a relação entre cliente e produto.

Conceitualmente:

score = soma das evidências obtidas

Ausência de evidência contribui com:

0 pontos

e não com um valor neutro ou intermediário.

A fórmula, fatores, pesos, tratamento estatístico e demais regras são definidos em SPEC-001.

O agente não pode alterar pesos, fórmula ou interpretação do score sem alteração explícita da SPEC.

⸻

7. Explicabilidade

Todo score deve ser explicável.

O backend deve ser capaz de informar:

* score final;
* fatores considerados;
* contribuição de cada fator;
* justificativa correspondente.

A justificativa deve ser derivada deterministicamente dos mesmos dados utilizados no cálculo.

Não utilizar LLM para gerar, alterar ou interpretar o score.

O vendedor deve conseguir entender por que uma oportunidade recebeu determinada pontuação.

⸻

8. Dados incompletos

Dados ausentes são uma condição válida do sistema.

A ausência de uma informação:

* não deve causar falha no cálculo;
* não deve gerar dados artificiais;
* não deve receber pontuação compensatória;
* não deve ser interpretada automaticamente como evidência positiva ou negativa.

Quando um fator não puder ser calculado por falta de dados, sua contribuição será 0, conforme definido pela SPEC de scoring.

⸻

9. Normalização dos dados

Dados externos devem ser normalizados antes de serem utilizados pelas regras de negócio.

Diferenças de representação não devem criar entidades distintas quando representam o mesmo objeto.

Exemplo conhecido nos dados fornecidos:

GTX Pro
GTXPro

representam o mesmo produto.

A estratégia definitiva de importação e normalização será definida na SPEC correspondente.

⸻

10. Autenticação e usuários

O sistema possui autenticação.

Existe apenas uma classe de usuário.

Não implementar:

* roles;
* hierarquia de usuários;
* ACL;
* RBAC;
* permissões diferenciadas;
* sistema administrativo separado,

a menos que uma SPEC futura introduza explicitamente essa necessidade.

⸻

11. Interface

A interface deve priorizar a decisão comercial:

“Em quais oportunidades devo focar agora?”

A visualização do pipeline deve tornar simples identificar:

* oportunidades com maior score;
* cliente;
* produto;
* estágio da oportunidade;
* score;
* justificativa;
* fatores relevantes.

O sistema também deve possuir relatórios visuais relacionados aos scores e ao pipeline.

Detalhes de telas, filtros e relatórios pertencem à SPEC de aplicação e interface.

⸻

12. Dependências visuais

Bootstrap deve ser carregado através do CDN oficial.

Font Awesome deve ser carregado através do CDN oficial.

Roboto deve ser carregado através do Google Fonts.

Não instalar esses recursos como dependências locais do projeto sem alteração explícita da documentação.

⸻

13. Banco de dados

PostgreSQL é o único banco de dados da aplicação.

Não introduzir:

* MySQL;
* SQLite;
* MongoDB;
* Redis;
* Elasticsearch;
* outro mecanismo de persistência,

sem decisão arquitetural explícita.

Mudanças de schema devem ser reproduzíveis.

Não depender de alterações manuais realizadas diretamente no banco.

⸻

14. API

O frontend deve consumir o backend através da API da aplicação.

As respostas relacionadas ao scoring devem fornecer dados estruturados suficientes para que o frontend apresente tanto o score quanto sua explicação.

Regras de negócio não devem depender da representação visual utilizada pelo frontend.

⸻

15. Testes

As regras de scoring devem possuir testes automatizados.

Os testes devem verificar pelo menos:

* cálculo dos fatores;
* composição do score final;
* limites de 0 e 100;
* ausência de score base;
* comportamento com dados incompletos;
* normalização relevante para o cálculo;
* geração das justificativas.

Um teste não deve apenas verificar o score final quando for possível verificar também suas contribuições individuais.

⸻

16. Regras para o agente implementador

Antes de implementar uma etapa:

1. ler este AGENTS.md;
2. consultar a ADR aplicável;
3. consultar a SPEC aplicável;
4. verificar a posição da tarefa no ROADMAP.md;
5. inspecionar o código existente antes de modificá-lo.

Durante a implementação:

* preservar decisões existentes;
* realizar mudanças pequenas e rastreáveis;
* não duplicar regras de negócio;
* não criar funcionalidades não solicitadas;
* não substituir tecnologia definida pela documentação;
* não alterar contratos documentados silenciosamente.

Quando houver ambiguidade relevante, conflito ou decisão arquitetural não coberta pela documentação, o agente deve interromper a decisão naquele ponto e solicitar esclarecimento, em vez de inventar um requisito.

⸻

17. Critério de conclusão

Uma tarefa só pode ser considerada concluída quando:

* atende à SPEC correspondente;
* respeita as ADRs;
* respeita este AGENTS.md;
* não quebra funcionalidades existentes;
* possui os testes aplicáveis;
* integra-se corretamente ao restante da aplicação;
* não deixa comportamento conhecido apenas na implementação quando deveria estar documentado.

“Funciona localmente” não é, isoladamente, critério suficiente de conclusão.

⸻

18. Regra final

A documentação define o contrato do sistema.

O agente implementador possui autonomia para decidir como implementar detalhes locais não especificados.

Essa autonomia não inclui alterar:

* requisitos;
* regras de negócio;
* arquitetura documentada;
* stack;
* contratos;
* fórmula de scoring.

Quando uma decisão ultrapassar esses limites, ela deve ser tratada como uma decisão de projeto e não como um detalhe de implementação.