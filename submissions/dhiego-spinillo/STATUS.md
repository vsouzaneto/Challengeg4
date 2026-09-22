# Estado atual

**21/09/2026 — três caminhos executáveis com adaptadores simulados; valor decomposto por processo. Commits locais; sem push ou PR.**

## O que está pronto

- Auditoria dos dois datasets, análise visual e relatórios reproduzíveis.
- Classificador local: 86% de concordância com os rótulos em 800 tickets reservados; Jev: 45,25%. Sensibilidade e limites documentados.
- Pareceres reais de Claude, Grok e Codex e confronto das decisões.
- Classificação, confirmação/correção humana, persistência e exportação.
- Três casos discutidos com Dhiego; [decisões registradas](docs/revisao-guiada-tres-tickets.md).
- Ficha de contexto: outros tickets, sistema e notas internas, com estado declarado pelo atendente. Relato de possível incidente separado da categoria e apoiado em trecho literal.
- Próximo passo e rascunho editável por regras, condicionados às conferências. Cópia disponível, sem envio automático.
- 204 testes passam localmente e no Docker, incluindo os novos caminhos e preservação de registros antigos.

- Resumo executivo visual e em Markdown; simulação econômica editável, com fonte salarial e três cenários.
- Mapa de oportunidades reproduzível e proposta de três caminhos: autosserviço, atendimento preparado e investigação humana.

## Limites

Não há integração de produção. Em `/fluxos`, três adaptadores consultam registros fictícios automaticamente; em `/classificador`, a ficha anterior continua recebendo declarações do atendente. Contas, notas e resultados dos sistemas demonstrativos não pertencem aos clientes dos textos. O recap via LLM continua experimental e desligado por padrão: 15/16 saídas estruturalmente válidas e fidelidade aprovada pelo revisor automatizado em 6/15. Nenhum ganho operacional foi medido.

## Próximos passos

1. Revisar `/fluxos`: recuperar acesso → concluir no provedor simulado → informar falha → aprovar resposta; comparar com investigação. Consultar `/valor` para a contribuição de cada processo.
2. Revisar o pacote e a descrição do PR para submissão. A revisão qualitativa dos três casos não é aprovação automática da implementação final.
3. Publicar a submissão após o fechamento com o candidato; nada enviado até este registro.

A calculadora arbitrária foi retirada. A hipótese de reduzir perguntas repetidas e encaminhamentos incompletos exige medir também o esforço adicional da ficha; [piloto proposto](docs/piloto-operacional.md).

Meta pessoal declarada na retomada: concluir hoje. Prazo oficial desconhecido. Preparação começou em 15/09; não atribuir total fictício de 4–6 horas. Chaves permanecem locais e ignoradas pelo Git.

Atualização 21/09: a nova calculadora em `/economia` inclui custos, adoção, tempo líquido e conversão em despesa evitada; não recupera a conta arbitrária anterior. [ADR 0007](docs/decisions/0007-autonomia-por-procedimento-e-cenarios-economicos.md). Esse era o estado da ADR 0007. A ADR 0008 abaixo implementa o fluxo em ambiente simulado; integrações de produção continuam pendentes.

## Incremento após a crítica de valor

- `/fluxos`: IA extrai sinais com citações; regras escolhem autosserviço, preparação ou investigação. Estados e trilha persistidos, conclusão simulada e tratamento de falha.
- `/valor`: contribuições por processo, sucesso/falha e antes/depois; não presume ganho na investigação.
- Verificação com IA: sete cenários conhecidos, seis extrações aceitas e um fallback; sete rotas esperadas. Não é benchmark independente.
- Integração real, elegibilidade e impacto operacional continuam pendentes. O reset isolado não sustenta o investimento nas premissas usadas; preparação de contexto é a principal hipótese de valor.
