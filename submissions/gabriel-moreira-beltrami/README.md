# Submissão — Gabriel Moreira Beltrami — Challenge 003

## Sobre mim

- **Nome:** Gabriel Moreira Beltrami
- **LinkedIn:** [gabriel-m-beltrami](https://www.linkedin.com/in/gabriel-m-beltrami)
- **Challenge escolhido:** 003 — Lead Scorer

---

## Executive Summary

Construí a **Fila de Prioridades**, uma aplicação Streamlit que organiza as 2.089 oportunidades abertas em duas filas operacionais: quem abordar em Prospecção e onde aumentar a atenção em Em negociação. A prioridade combina valor esperado de catálogo, taxa histórica de vitória suavizada e contexto da conta, e explica cada recomendação para a pessoa vendedora. A principal recomendação é concentrar esforço nos produtos premium com histórico suficiente, mas encaminhar prospects sem conta para pesquisa antes de uma abordagem comercial intensa. O app evita campos pós-desfecho e não inventa uma métrica de inatividade que os dados não suportam.

---

## Solução

O código, setup, lógica e limitações estão em [solution/README.md](solution/README.md). A aplicação inclui filtros por vendedor, gestor, região e estágio, duas filas de trabalho, seleção de lead com detalhe abaixo da tabela e exportação CSV.

### Abordagem

1. Normalizei `GTXPro` para `GTX Pro` e validei os joins entre pipeline, produtos, contas e equipes.
2. Separei 6.711 negócios fechados dos 2.089 negócios abertos e mantive `close_date`, `close_value` e resultado final fora do score.
3. Estimei `P(win | product)` com suavização Bayesiana e combinei a probabilidade com preço de catálogo, cobertura histórica e conta vinculada.
4. Testei se porte e idade da empresa justificavam aumento de prioridade. Não houve ganho útil depois de controlar por produto.
5. Transformei a análise em duas recomendações: `Engajar agora` / `Pesquisar antes` / `Nutrir` em Prospecção e `Focar agora` / `Manter ativa` / `Monitorar` em Em negociação.

### Resultados / Findings

- Há 500 oportunidades em Prospecção e 1.589 em Em negociação.
- Produtos premium representam 87,5% da receita ganha. `GTX Plus Pro` e `GTX Pro` são prioridades de maior valor com histórico amplo.
- `GTK 500` tem alto valor, mas apenas 25 negócios fechados; exige qualificação manual.
- 337 dos 500 leads em Prospecção não têm conta vinculada e entram na fila de pesquisa antes do contato de alto esforço.
- Porte e idade da empresa não receberam multiplicador de score, pois não adicionaram sinal útil fora da amostra.

### Recomendações

- Trabalhar **Priorizar prospecção** para decidir o primeiro contato e **Aumentar atenção** para negócios já ativos.
- Tratar `GTK 500` com qualificação deliberada, sem deixar preço sozinho decidir a ordem.
- Registrar `created_at`, `stage_changed_at`, `last_activity_at`, origem, descontos e atividades antes de introduzir inatividade ou um modelo causal de esforço comercial.

### Limitações

O CRM não registra criação do lead, mudança de estágio, último contato, snapshot, atividades, descontos, origem ou atribuição. A solução não mede esforço do vendedor, causalidade ou estagnação. A síntese completa está em [solution/docs/analysis-summary.md](solution/docs/analysis-summary.md).

---

## Process Log — Como usei IA

O process log detalhado está em [process-log/README.md](process-log/README.md). O histórico integral da conversa que orientou a investigação, as correções e a implementação foi incluído em [process-log/chat_history.txt](process-log/chat_history.txt).

### Ferramentas usadas

| Ferramenta | Para que usei |
| --- | --- |
| Codex | Exploração, análise, implementação, revisão e testes. |
| Agente independente | Checagem separada da hipótese de mix de produto por empresa. |
| Navegador automatizado | Verificação do app local, filtros e seleção de linhas. |

### Workflow

Inspecionei os dados, formulei e testei hipóteses de produto e perfil de empresa, construí o score, separei as duas filas operacionais, revisei explicabilidade e validei o fluxo no navegador.

### Onde a IA errou e como corrigi

- Corrigi a leitura inicial de que todos os prospects não tinham conta: 163 têm e 337 não têm.
- Limitei a escala a 0–100 e garanti uma recomendação para cada oportunidade aberta.
- Removi a ideia de estagnação porque não há timestamps suficientes.
- Corrigi a seleção persistida depois da troca de filtro, que podia apontar para uma linha inexistente.

### O que eu adicionei que a IA sozinha não faria

O julgamento comercial foi separar a decisão de iniciar conversa da decisão de aumentar atenção, e recusar uma segmentação por porte de empresa que não se sustentou fora da amostra.

---

## Evidências

- [x] Narrativa de processo e iterações: [process-log/README.md](process-log/README.md)
- [x] Histórico integral da conversa: [process-log/chat_history.txt](process-log/chat_history.txt)
- [x] Código funcional e instruções de setup: [solution/README.md](solution/README.md)
- [x] Síntese reprodutível dos dados e achados: [solution/docs/analysis-summary.md](solution/docs/analysis-summary.md)
- [x] Git history da submissão

_Submissão enviada em: 30/09/2026._
