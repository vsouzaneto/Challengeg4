# Submissão — Luis Fernando Roquette — Challenge 001

## Sobre mim

- **Nome:** Luis Fernando Roquette
- **LinkedIn:** [linkedin.com/in/luisroquette](https://br.linkedin.com/in/luisroquette)
- **Challenge escolhido:** 001 — Diagnóstico de Churn

---

## Executive Summary

Cruzei cinco tabelas em um painel temporal reproduzível para investigar uso, satisfação e seis possíveis causas de churn. O churn recente chegou a 12,4%, mas nenhuma causa passou todos os gates de estabilidade, associação e confirmação entre fontes. O uso agregado cresceu enquanto caiu entre futuros churners, e as datas apresentam contradições materiais. Recomendo sanear a medição e validar prospectivamente uso e satisfação antes de direcionar intervenções.

---

## Solução

### Abordagem

Imobilizei os CSVs com hashes, modelei cada conta por data de corte sem vazamento, comparei cronologias `observed` e `strict` e publiquei relatório, dashboard e fila a partir do mesmo objeto canônico.

### Resultados / Findings

- Nenhuma das seis hipóteses foi confirmada com evidência suficiente.
- O uso agregado subiu, mas caiu na coorte que posteriormente churnou.
- Foram detectados eventos anteriores à assinatura ou ao cadastro, limitando inferências causais.
- [Relatório executivo](artifacts/report.md) e [instruções de execução](README.md).

### Recomendações

1. Sanear eventos fora do ciclo de vida e reproduzir as métricas.
2. Acompanhar uso e churn prospectivamente com cobertura mínima de 70%.
3. Medir satisfação fora dos tickets com amostra representativa.

### Limitações

Os dados são observacionais, contraditórios e aparentemente sintéticos. Não há histórico de intervenção para estimar efeito causal ou receita recuperável.

---

## Process Log — Como usei IA

### Ferramentas usadas

| Ferramenta | Para que usou |
|---|---|
| OpenAI Codex | Descoberta, SDD, implementação, testes e documentação |
| Pesquisa web/GitHub | Verificação de padrões, fontes e regras |
| Graphify | Auditoria estrutural e rastreabilidade da solução |

### Workflow

1. Reli o briefing até duas passadas consecutivas sem novos achados.
2. Conduzi cinco ondas socráticas antes da SPEC.
3. Implementei e revisei cada fase com testes e documentação contemporânea.

### Onde a IA errou e como corrigi

A IA propôs um teste de caminho incompatível com o `AppTest`, capturas amplas de exceção e um gate temporal impossível. Corrigi o caminho, restringi as exceções e removi a exigência conceitualmente inválida antes do fechamento.

### O que eu adicionei que a IA sozinha não faria

Defini que abstenção é melhor que causalidade instável, que toda recomendação precisa de um gate de confiança e que relatório, dashboard e CSV devem compartilhar a mesma verdade canônica.

---

## Evidências

- [x] [Diário pré-início](../../process-log/000-pre-inicio.md)
- [x] [Descoberta socrática](../../process-log/001-descoberta-socratica.md)
- [x] [Otimização do plano](../../process-log/002-otimizacao-plano-loop.md)
- [x] [Implementação em feedback loops](../../process-log/003-implementacao-feedback-looping.md)
- [x] [Histórico Git](https://github.com/luisroquette/ai-master-challenge/commits/submission/luis-roquette/)

---

_Submissão enviada em: 23/09/2026_
