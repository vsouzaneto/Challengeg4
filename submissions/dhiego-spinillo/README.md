# Submissão — Dhiego Spinillo — Challenge 002

**Rascunho em análise — 15/09/2026. Ainda não submetido.**

## Sobre mim

- **Nome:** Dhiego Spinillo.
- **LinkedIn:** a confirmar antes da submissão.
- **Challenge escolhido:** 002 — Redesign de Suporte.

## Executive Summary

A análise começou verificando se os dois datasets permitem responder às perguntas do diretor. O primeiro contém 8.469 tickets, não oferece abertura do chamado e apresenta resolução anterior à primeira resposta em 1.365 dos 2.769 pares disponíveis. Esses limites impedem usar os campos temporais como duração operacional confiável. A direção em discussão é avaliar classificação de texto no segundo dataset e aplicar uma política explícita de encaminhamento, com revisão humana. O protótipo, o treinamento e a avaliação do modelo ainda não foram realizados.

## Solução

### Abordagem

Entender o problema → auditar os dados → discutir conclusões e limites → escolher intervenção → construir e avaliar. Nesta fase, o candidato está questionando a análise e definindo o recorte com apoio de IA.

### Resultados / Findings

- [Diagnóstico inicial](solution/diagnostico-inicial.md).
- [Exploração preliminar de CX: urgência, atrito, canais e qualidade da resposta](solution/analise-preliminar-cx.md).
- [Auditoria reproduzível e downloads](solution/REPRODUZIR.md).
- [Resultado da auditoria](solution/reports/auditoria-datasets.json).

### Recomendações

Instrumentar os eventos ausentes antes de afirmar onde se perde tempo. Testar a hipótese de triagem com avaliação separada das regras de encaminhamento. Manter indicadores e política em código explícito. Essas recomendações ainda serão discutidas antes de fechar o plano de implementação.

### Limitações

Nenhum ganho operacional, economia, redução de churn ou desempenho de classificador foi medido. Os dois datasets têm domínios distintos e não serão unidos sem relação válida. Dados de satisfação cobrem apenas parte da base. A solução técnica continua proposta.

## Process Log — Como usei IA

### Ferramentas usadas

| Ferramenta | Para que foi usada |
|---|---|
| Claude | Produção do plano inicial fornecido pelo candidato. |
| Codex | Revisão crítica, auditoria dos CSVs, discussão de alternativas e organização dos registros. |

### Workflow

1. Dhiego solicitou uma crítica do plano inicial à luz do desafio e de sua experiência.
2. Codex verificou os arquivos e produziu a auditoria; os achados não são atribuídos a uma descoberta manual do candidato.
3. Dhiego questionou escopo, uso de IA, critérios operacionais e priorização; essas intervenções alteraram o plano.
4. Dhiego definiu análise e discussão em 15/09; construção prevista para 16/09, após definição do recorte.

### Onde a IA errou e como corrigi

O plano inicial propunha métricas de duração que os dados não sustentam e uma aproximação de economia que confundia tempo decorrido com trabalho ativo. A revisão com Codex levantou essas falhas e o script confirmou os limites dos arquivos. O próprio plano de execução de Codex foi revisto após Dhiego questionar a prioridade da interface, o uso indiscriminado de IA e a expansão do escopo. Ver [registro de iterações](process-log/README.md).

### O que eu adicionei que a IA sozinha não faria

Contribuições efetivamente registradas: exigir distinção entre regras e IA, trazer dimensões operacionais de sentimento/reincidência/acompanhamento, decidir mantê-las como propostas futuras dependentes de dados e separar entendimento de implementação. Não é uma alegação de exclusividade dessas ideias; é o registro das intervenções do candidato nesta execução.

## Evidências

- [Process log](process-log/README.md).
- [Trechos selecionados das intervenções do candidato](process-log/evidencias/trechos-da-conversa.md).
- [Trechos do plano inicial revisado](process-log/evidencias/plano-inicial.md).
- [ADRs](docs/decisions/0001-fronteira-entre-regras-e-ia.md), [roadmap](ROADMAP.md) e [estado atual](STATUS.md).
- Capturas do aplicativo e resultados do modelo: pendentes de implementação.

**Submissão enviada em:** ainda não enviada.
