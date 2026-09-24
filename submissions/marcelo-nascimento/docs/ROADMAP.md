# ROADMAP — Lead Scorer

**Status:** Concluído  
**Data:** 2026-09-24  
**Conclusão:** 2026-09-24

Este roadmap define a ordem recomendada de implementação.

As regras funcionais pertencem às SPECS.  
As decisões arquiteturais pertencem à ADR.

O agente deve implementar incrementalmente e manter o sistema funcional ao final de cada etapa.

Todas as etapas e os Gates abaixo foram concluídos. O scoring permanece no backend, sob demanda e sem alteração da fórmula documentada.

---

# 1. Banco e dados

Preparar a estrutura PostgreSQL necessária para:

- usuários;
- contas;
- produtos;
- oportunidades;
- equipes/vendedores.

Implementar:

- migrations;
- importação dos dados fornecidos;
- normalização dos dados;
- alias `GTXPro → GTX Pro`;
- relacionamentos necessários.

### Gate

- [x] migrations executam corretamente;
- [x] datasets são importados;
- [x] dados podem ser consultados pelo backend;
- [x] produtos estão normalizados.

---

# 2. Scoring Engine

Implementar integralmente a `SPEC-001-scoring-engine.md`.

Ordem sugerida:

```text
normalização
    ↓
features históricas
    ↓
4 fatores
    ↓
score final
    ↓
Explanation Builder
```

Implementar os testes obrigatórios da SPEC.

### Gate

- [x] score varia entre `0` e `100`;
- [x] nenhuma evidência resulta em `0`;
- [x] quatro fatores funcionam independentemente;
- [x] dados ausentes não quebram o cálculo;
- [x] justificativa é gerada;
- [x] testes estão passando.

**Não avançar com uma implementação incorreta do scoring apenas para construir a interface.**

---

# 3. API

Criar os contratos necessários para:

- autenticação;
- dashboard;
- oportunidades;
- detalhe do score;
- relatórios;
- usuários.

Implementar paginação, pesquisa, filtros e ordenação no backend quando aplicável.

### Gate

- [x] A API fornece todos os dados necessários para a `SPEC-002` sem exigir que o frontend reproduza regras de negócio.

---

# 4. Estrutura da aplicação

Implementar:

- Login;
- autenticação;
- proteção das rotas;
- layout principal;
- sidebar responsiva;
- navegação.

Configurar visual:

```text
Roboto          → Google Fonts
Bootstrap       → CDN oficial
Font Awesome    → CDN oficial
```

Aplicar a paleta definida na `SPEC-002`.

### Gate

Usuário consegue:

```text
Login
  ↓
Dashboard
  ↓
Navegar entre as áreas
  ↓
Logout
```

- [x] Fluxo validado em desktop e mobile pela interface responsiva implementada.

---

# 5. Dashboard e Listagem

Implementar primeiro a experiência principal do produto.

### Dashboard

- métricas;
- Hot Leads;
- oportunidades prioritárias;
- distribuição de scores.

### Listagem

- oportunidades;
- score;
- pesquisa;
- filtros;
- ordenação;
- paginação;
- detalhe da oportunidade;
- breakdown dos quatro fatores;
- justificativa.

### Gate

Um vendedor consegue abrir a aplicação e responder rapidamente:

> Em quais oportunidades devo focar e por quê?

- [x] O vendedor identifica oportunidades prioritárias e compreende score, fatores e justificativa.

---

# 6. Relatórios e Usuários

Implementar:

### Relatórios

- distribuição dos scores;
- score médio por produto;
- score médio por setor;
- pipeline por estágio;
- conversão histórica por produto;
- filtros.

### Usuários

- listagem;
- criação;
- edição;
- ativação/desativação;
- redefinição de senha.

Não implementar roles.

### Gate

- [x] Todos os requisitos da `SPEC-002` estão funcionais.

---

# 7. Verificação final

Executar revisão completa contra:

```text
AGENTS.md
    ↓
ADR-001
    ↓
SPEC-001
    ↓
SPEC-002
```

Verificar:

- [x] testes;
- [x] scoring;
- [x] autenticação;
- [x] responsividade;
- [x] estados de loading;
- [x] estados vazios;
- [x] tratamento de erros;
- [x] ausência de regras duplicadas no frontend;
- [x] ausência de funcionalidades fora do escopo.

Corrigir regressões encontradas.

## Evidências da verificação final

- Backend: `26/26` testes do Scoring Engine aprovados;
- Backend: typecheck estrito, incluindo os testes, e build aprovados;
- Frontend: ESLint e build Vite aprovados;
- Docker: build da imagem e `docker compose config` aprovados;
- PostgreSQL: `85` contas, `7` produtos, `35` vendedores, `8.800` oportunidades e `2.089` oportunidades abertas importadas;
- API: autenticação, proteção de rotas, dashboard, listagem, filtros, detalhe, quatro fatores, justificativa, relatórios, usuários e logout validados;
- Segurança: senha nunca exposta, sessões revogadas, usuário inativo bloqueado, seed inicial não recriado após rotação de credencial e rate limit validado;
- Frontend: proxy `/api` e fallback SPA validados por meio do servidor Vite de produção.

---

# Definição de concluído

O projeto está concluído quando:

1. [x] os dados podem ser importados de forma reproduzível;
2. [x] o Scoring Engine atende integralmente à SPEC-001;
3. [x] a aplicação atende integralmente à SPEC-002;
4. [x] os testes obrigatórios passam;
5. [x] o vendedor consegue identificar oportunidades prioritárias e entender a justificativa do score;
6. [x] a aplicação funciona adequadamente em mobile e desktop.

Não implementar funcionalidades futuras antes desses critérios serem atendidos.