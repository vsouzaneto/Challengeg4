# Submissão — Luis Fernando Roquette — Challenge 002

## Sobre mim

- **Nome:** Luis Fernando Roquette
- **LinkedIn:** [linkedin.com/in/luisroquette](https://br.linkedin.com/in/luisroquette)
- **Challenge escolhido:** 002 — Redesign de Suporte

---

## Executive Summary

Construí um Support Decision Copilot que une diagnóstico operacional, classificação, gate de risco e decisão humana auditável. A análise de 8.469 tickets encontrou 1.404 intervalos válidos e um proxy histórico de 4.047,83 horas acima das medianas dos grupos. A evidência não sustentou automação autônoma de respostas nem uma relação confiável entre tempo e satisfação. Recomendo operar primeiro como copiloto conservador, com revisão humana e piloto shadow.

---

## Solução

### Abordagem

Separei Customer Support e IT em domínios independentes, sanitizei dados antes do modelo, congelei splits e thresholds e conectei diagnóstico, fila, precedentes, SQLite e exportação sem enviar mensagens externas.

### Resultados / Findings

- Customer obteve macro-F1 de 13,94% e 0% de cobertura segura; automação bloqueada.
- IT obteve macro-F1 de 83,51%, mas risco seletivo acima do teto; uso apenas em shadow.
- A população elegível para validação de rascunhos foi zero, portanto nenhum rascunho foi fabricado.
- [Diagnóstico, arquitetura e setup](README.md).

### Recomendações

1. Usar classificação e roteamento somente como apoio humano.
2. Validar primeiro o grupo Refund request / High.
3. Coletar timestamps completos e executar piloto shadow antes de qualquer automação externa.

### Limitações

O dataset não mede criação do ticket nem resolução total. Custos não estão presentes, a sanitização reduz cobertura e associação não prova causalidade.

---

## Process Log — Como usei IA

### Ferramentas usadas

| Ferramenta | Para que usou |
|---|---|
| OpenAI Codex | Descoberta socrática, SDD, implementação e revisão |
| Git/GitHub CLI | Worktree, histórico, diff e entrega remota |
| GitHub Codespaces | Testes e preflight reproduzíveis em Python 3.12 |

### Workflow

1. Transformei o briefing em critérios verificáveis antes de escolher tecnologia.
2. Comparei alternativas e congelei a menor arquitetura útil.
3. Implementei em ciclos de planejamento, revisão, execução e teste.

### Onde a IA errou e como corrigi

A normalização inicial permitia divergência após quebras de linha e o primeiro manifesto omitia a dependência do modelo Customer. Movi a validação para depois da normalização e corrigi o grafo do manifesto com regressões específicas.

### O que eu adicionei que a IA sozinha não faria

Exigi falha segura: capacidade sem evidência fica desativada e documentada, nunca substituída por dado sintético, geração livre ou alegação de economia.

---

## Evidências

- [x] [Diário contemporâneo](../../process-log/002-support.md)
- [x] [Pesquisa técnica](../../research/002-support.md)
- [x] [Screenshot real](evidence/screenshot.png)
- [x] [Export persistido](evidence/decisions-demo.csv)
- [x] [Métricas e hashes](evidence/metrics.json)

---

_Submissão enviada em: 22/09/2026_
