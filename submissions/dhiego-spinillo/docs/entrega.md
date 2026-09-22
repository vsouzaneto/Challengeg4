# Fechamento da entrega

**22/09/2026 — pacote local para revisão do candidato. Publicação pendente.**

## Mensagem ao diretor

“Os dados não permitem medir onde o tempo aumentou: falta abertura, quase metade dos pares temporais é inválida e não há histórico de transferências. Não vou transformar isso em horas desperdiçadas. Há oportunidades para preparar contexto, evitar repetição e tratar procedimentos simples. Construí três caminhos para demonstrar essa proposta e um piloto para verificar se o ganho paga o investimento.”

| Pergunta | Resposta sustentada | Evidência |
|---|---|---|
| Onde perdemos tempo? | Ainda não localizamos duração ou trabalho ativo com segurança. 2.881 pendentes e os relatos sugerem perguntas de investigação, não uma medida de desperdício. Registrar eventos, motivo da espera, transferências e trabalho ativo. | [Diagnóstico](../solution/analise-preliminar-cx.md) e [qualidade por pergunta](../solution/qualidade-por-pergunta.md). |
| O que automatizar com IA? | Sugerir categoria e extrair sinais do texto. Regras e contexto controlam procedimentos; consultas preparam atendimento. Recuperação elegível é demonstrada em provedor fictício, exceções vão para humano. | [Três caminhos](tres-velocidades.md) e [ADR 0008](decisions/0008-fluxos-executaveis-e-valor-por-processo.md). |
| Funciona e vale investir? | Software executável, comparação de categoria e evidências dos fluxos. Não há impacto operacional observado. A condição econômica do exemplo é recuperar 47,06 h/mês para pagar o primeiro ano, sob custos e conversão financeira declarados. | [Valor por processo](valor-por-processo.md), [capturas](../process-log/evidencias/fluxos-v1/README.md) e [piloto](piloto-operacional.md). |

## O que estamos entregando

| Componente | Estado e limite |
|---|---|
| Auditoria dos dois datasets | Pronta, reproduzível, com universos utilizáveis por pergunta. Bases não foram unidas. |
| Classificação Local × Jev | 86% × 45,25% no teste original de 800. Treino supervisionado local versus Jev por definições; não representa todos os usos possíveis do Jev. |
| Rodada integral do D2 | 47.837 processados, 1.114 divergências com rótulos, 305 acima do limiar. Modelo preservado; não é um novo teste independente. |
| Autosserviço | Procedimento de recuperação executável em conta fictícia, com conclusão, token, revalidação e tratamento de falha. Não é autorresposta livre de LLM. |
| Solução com aval | Contexto reunido, rascunho por regras, edição e aprovação persistidas. Não envia ao cliente. |
| Humano cuidando | Relato sensível, restrição ou fonte indisponível leva à investigação. Não presume causa nem resolução. |
| IA em mais de uma tarefa | Classificação local e extração por LLM nos fluxos. Recap separado e experimental; não é base para executar ações. |
| Temperatura, urgência e SLA | Temperatura e menção de prazo aparecem como sinais literais auditáveis para o atendente; não mudam prioridade. A demo explicita que SLA não é calculável sem eventos e política de prazo. |
| Guardrails | Contratos/citações, regras de contexto, bloqueios e estados testados. Não garantem detectar toda ambiguidade ou incidente. |
| ROI/saving | Calculadora editável por processo. Resultado é hipótese, não economia medida. Reset sozinho não sustenta o cenário de investimento. |
| Processo e reprodução | 219 testes locais e Docker, fontes/hashes, ADRs, iterações, decisões do candidato e capturas. Sem necessidade de VPS para revisar. |

## Quem decide o quê

| Decisão | Mecanismo | Por quê | Não faz |
|---|---|---|---|
| Categoria | Modelo local treinado no D2 | 86% no teste reservado; incluído localmente, sem custo por chamada. | Não executa procedimento; revisão humana obrigatória. |
| Intenção, tentativa e sinal de risco | LLM opcional com citações validadas; regras lexicais acrescentam bloqueios | Linguagem aberta exige leitura sem conceder autoridade ao modelo. | Não confirma fato, causa, prioridade ou elegibilidade. |
| Contexto, elegibilidade, token e ação | Consultas de demonstração + regras/máquina de estados | Segurança, auditoria e comportamento reproduzível. | Não depende de score ou LLM; não altera conta real. |
| Rascunho e investigação | Texto por regra + aprovação/investigação humana | Fato precisa de fonte e casos sensíveis não podem ser presumidos. | Não envia resposta livre automática ou encerra incidente. |

[Matriz completa: IA, modelo local, regras, humano, escopo e custo](onde-entra-ia.md). Temperatura e prazo entram como sinais citados, não como decisão. Nota de sentimento, prioridade, churn, SLA histórico e saving continuam fora de IA decisória: faltam rótulos, histórico confiável e eventos operacionais para validar essas decisões.

## Demonstração de aproximadamente 10 minutos

1. **2 min — `/resumo`:** explicar o problema, os limites temporais e a intervenção. Mostrar por que “aguardando cliente” pode ser dependência legítima.
2. **3 min — `/fluxos`:** pedido curto de recuperação, consulta das fontes fictícias, início/conclusão no provedor, falha com histórico e aprovação do rascunho. Mostrar a trilha.
3. **1 min — `/fluxos`:** possível incidente. Categoria não define gravidade; o caso fica aberto para investigação, sem afirmar causa.
4. **2 min — `/classificador` e [rodada integral](../solution/reports/full-population/report.md):** mostrar sugestão e revisão. Explicar 86% no teste, Jev 45,25% e por que score alto não autoriza ação.
5. **2 min — `/valor`:** mostrar quanto depende de preparação. Reduzir minutos poupados/conversão financeira e observar a sensibilidade. Fechar com a medição necessária para decidir o investimento.

Sem chave, a demonstração usa regras explicitamente. Com chave, a extração usa IA real e pode variar ou cair em fallback. As [capturas](../process-log/evidencias/fluxos-v1/README.md) e os [resultados arquivados](../solution/reports/fluxos-desenvolvimento.json) permitem examinar a execução anterior sem consumir API.

## O que falta para publicar

- Dhiego percorrer o roteiro e confirmar que consegue explicar o recorte e suas limitações. A revisão anterior de três tickets orientou o desenvolvimento; não equivale a essa revisão final.
- Depois do fechamento com o candidato: criar/usar fork, enviar a branch e abrir um único PR conforme o guia oficial. Commits permanecem locais até esse momento.

## O que permanece como evolução

A extração dos novos fluxos ainda precisa de amostra nova, selecionada antes das respostas, e referência humana para intenção, tentativas, risco e pedidos omitidos. Os sete cenários conhecidos não suprem isso. Uma avaliação futura deve congelar prompt/regras, registrar casos em que se abstém e medir erro por tipo; não atribuir estado de conta fictício à base inteira para estimar autonomia.

Integração real, autenticação, elegibilidade e redução de trabalho/recontato pertencem ao piloto. Não são requisitos para afirmar que existe um protótipo funcional, mas são necessários para recomendar implantação e anunciar retorno.

À luz apenas dos feedbacks de candidatos trazidos por Dhiego, o pacote já inclui diagnóstico honesto, protótipo, process log, commits, evidência visual e cenários financeiros. A lacuna mais relevante é a validação semântica dos novos fluxos e o ganho operacional, declarados. Não há garantia de aprovação nem necessidade de copiar o escopo de outros candidatos.
