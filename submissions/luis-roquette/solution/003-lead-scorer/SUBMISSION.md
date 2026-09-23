# Submissão — Luis Fernando Roquette — Challenge 003

## Sobre mim

- **Nome:** Luis Fernando Roquette
- **LinkedIn:** [linkedin.com/in/luisroquette](https://br.linkedin.com/in/luisroquette)
- **Challenge escolhido:** 003 — Lead Scorer

---

## Executive Summary

Construí uma aplicação Streamlit que transforma 8.800 oportunidades em filas explicáveis para vendedor e gestor. As 2.089 oportunidades ativas são separadas entre `Engaging` e `Prospecting`, sem comparar escalas incompatíveis. Quatro rotas probabilísticas falharam nos gates temporais, então o produto publica prioridade relativa em vez de falsa precisão. Recomendo um piloto controlado que registre intervenção e desfecho antes de qualquer recalibração.

---

## Solução

### Abordagem

Validei os quatro CSVs com manifesto e checksums, separei os estágios, avaliei modelos temporalmente e derivei explicações da saída real com um playbook determinístico.

### Resultados / Findings

- 8.800 oportunidades analisadas e 2.089 ativas priorizadas.
- Quatro rotas probabilísticas rejeitadas pelos gates.
- Filas acionáveis para vendedor e gestor, sem escrita no CRM ou API de IA no runtime.
- [Aplicação, preflight e execução](README.md).

### Recomendações

1. Usar a fila relativa em um piloto controlado.
2. Registrar intervenção e desfecho.
3. Publicar probabilidades somente após superar os gates temporais.

### Limitações

Os dados são estáticos e os perfis são demonstrativos. Não há autenticação, escrita no CRM, inferência causal, monitoramento de drift ou retreino agendado.

---

## Process Log — Como usei IA

### Ferramentas usadas

| Ferramenta | Para que usou |
|---|---|
| OpenAI Codex | Descoberta, implementação, testes e auditoria |
| SDD Context Engineering Kit | SPEC, plano e critérios de aceite |
| NotebookLM e Graphify | Síntese visual e rastreabilidade estrutural |

### Workflow

1. Reli o briefing até estabilizar a compreensão.
2. Conduzi seis ondas socráticas antes da SPEC.
3. Implementei, testei, lapidei a interface e auditei a entrega.

### Onde a IA errou e como corrigi

A primeira direção reduzia o problema a um dashboard com score. A revisão humana redefiniu o produto como fila de ação, bloqueou leakage, separou estágios incompatíveis e impediu probabilidades não sustentadas.

### O que eu adicionei que a IA sozinha não faria

Defini que o vendedor precisava saber onde focar, por quê e o que fazer agora; o número isolado nunca seria o produto.

---

## Evidências

- [x] [Diário contemporâneo](../../process-log/003-lead-scorer.md)
- [x] [Avaliação medida](docs/evaluation.md)
- [x] [Checklist de segurança](docs/security-checklist.md)
- [x] [Aplicação e execução reproduzível](README.md)
- [x] [Histórico Git](https://github.com/luisroquette/ai-master-challenge/commits/submission/luis-roquette-003-lead-scorer/)

---

_Submissão enviada em: 22/09/2026_
