---
status: passing
canonical: true
area: ops-cx
created: 2026-09-21
last_updated: 2026-09-21
---

# SPEC-002 Redesign de Suporte (`process-002-support`)

## Comportamento visível

O candidato atua como AI Master de Suporte (~30K tickets/ano, email / chat / telefone / social). O Diretor de Operações pede **três coisas**: onde se perde tempo, o que dá para automatizar com IA, e **algo rodando** — não só PowerPoint.

O challenge testa análise + julgamento de processo + (diferencial) build.

Persona da saída: Diretor de Operações (quer horas e ROI).

## Contrato

### Entrada

Os **dois** datasets de [DATA-SOURCES.md](../architecture/DATA-SOURCES.md). Um tem métricas operacionais + texto; o outro tem 48K textos já rotulados em 8 `Topic_group`. Sem chave de join — o cruzamento é de **método** (treinar/validar classificação no #2, diagnosticar operação no #1).

### Obrigatório

1. **Diagnóstico operacional** (dataset 1)
   - Gargalos por canal × prioridade × tipo (piores TTR).
   - O que move `Customer Satisfaction Rating` (tempo, canal, tipo — com dados).
   - Desperdício em horas e, se possível, custo; maior fatia recuperável.
2. **Proposta de automação** (ambos)
   - O que automatizar (classificação, roteamento, sugestão, prioridade, duplicata — o que os dados sustentarem).
   - O que **não** automatizar, com exemplos dos dados.
   - Fluxo: ticket entra → etapas → onde IA atua → onde humano entra.

### Diferencial (não gate, mas o brief empurra)

Protótipo com dados reais: classificador com confiança, respostas por similaridade, roteador, dashboard de gargalo, etc. Cherry-pick de 3 exemplos = fraco.

### Process log

Obrigatório.

## Critérios de qualidade (aceitação)

| # | Critério | Red flag |
|---|----------|----------|
| Q1 | Ambos os datasets | Um só |
| Q2 | Diagnóstico com números | Texto genérico de “usar NLP” |
| Q3 | Automação realista | Automatizar 100% |
| Q4 | Humano insubstituível justificado | “IA resolve tudo” |
| Q5 | Protótipo (se houver) generaliza | 3 tickets escolhidos a dedo |

Especificidade esperada: métrica + método + recorte (não “classificar tickets com IA”).

## Verificação

- [ ] README ainda lista os dois Kaggle e os três blocos (diagnóstico, automação, protótipo).
- [ ] Submissão quantifica gargalo e desperdício.
- [ ] Há zona explícita de não-automação.
- [ ] Process log presente.

## Evidência

2026-09-21: `challenges/process-002-support/README.md` (Operações / CX; Diagnóstico + Automação + Build; 4–6 h).

## Notas

PII de cliente (`Customer Email`, `Customer Name`) aparece no dataset 1. Solução do candidato não deve commitar dumps identificáveis no PR se puder agregar.

Disco 2026-09-21: só o Dataset 1, **8 469** linhas (brief ~30 k). Dataset 2 **ausente** (zip = o mesmo CSV). Classificador 8 classes sem esse arquivo não tem ground truth local. ERD: [erd/process-002-support.md](../erd/process-002-support.md).

Lab Databricks (mesmo contrato de colunas): [notebook-process-002-support](../../notebook-process-002-support/README.md) — ingestão Lab 01, Assistant Lab 02, **entregável Lab 03**, análise Lab 04. Spec do pacote: [SPEC-010-lab-002-databricks.md](SPEC-010-lab-002-databricks.md). Entregável: [SPEC-014](SPEC-014-lab-03-entregaveis.md).

## Sucesso / falha

- Sucesso: “Chat × Billing × High = TTR p95 de H h; classificador 8 classes com acurácia A% no holdout do dataset 2; fila Critical continua humana; ROI ≈ Y h/mês.”
- Falha: deck “implementar chatbot” sem números nem recorte do que não automatizar.

## Migração e compatibilidade

Dois datasets distintos são invariante. Fundir num CSV só no brief = nova spec.
