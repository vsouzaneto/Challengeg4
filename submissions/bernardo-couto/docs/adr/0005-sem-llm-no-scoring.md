# ADR 0005 — Sem LLM (incluindo Jev) no scoring

**Status:** aceito · **Data:** 2026-09-23

## Contexto

Foi avaliado o uso de um "System One model" (Jev, da TypeSafe AI) — modelo de decisão estruturada, com saídas tipadas, probabilidades calibradas, latência de 70–500 ms e sem geração de texto — como classificador/roteador de deals. Também se considerou um LLM generalista para gerar explicações.

## Decisão

Nenhum LLM ou modelo externo participa do cálculo do score nem da geração dos reason codes. O scoring é regras transparentes + Spark ML treinado nos dados do próprio CRM; as explicações são templates determinísticos alimentados pelos números de cada deal.

## Justificativa

1. **O problema é tabular e supervisionado.** Temos 6.711 desfechos rotulados e features estruturadas. Um modelo treinado nesses dados captura o histórico da empresa; um modelo externo não é treinável nos nossos dados (não há fine-tuning declarado) e só poderia reproduzir regras que já temos.
2. **Explicabilidade exata.** Coeficientes e contribuições por feature são auditáveis e testáveis. Uma decisão vinda de API externa é uma caixa opaca com confiança, não uma explicação.
3. **Execução offline e reprodutível.** Serviço em early access (waitlist), hospedado nos EUA, exige chave de API e rede. A rubrica do G4 penaliza setup que depende de chave ou infra externa; nosso `docker compose up` roda sem nada disso.
4. **Sem sinal não estruturado.** Jev brilharia em rotear texto livre (notas de reunião, e-mails). O dataset não tem esse tipo de dado. Adotá-lo agora seria complexidade sem necessidade.
5. **Custo de manutenção.** Mais um fornecedor, mais um contrato, mais um ponto de falha, para um ganho não demonstrável no backtest.

## Consequências

- Nenhuma dependência de rede em runtime; nenhuma chave de API.
- Se o CRM passar a ter texto livre por deal (atividades, notas), reavaliar um classificador tipado (Jev ou similar) para extrair sinais estruturados que alimentem o pipeline — nunca para substituir o score.
- Documentar em `limitations.md` que "IA" nesta solução significa modelo treinado + engenharia assistida por IA, não LLM em produção.
