# Estado atual

**22/09/2026 — retomada concluída: lote integral, documentação alinhada e sete novas screenshots locais. Pacote pronto para revisão final do candidato; sem publicação.**

## Fechamento vigente

- **47.837 tickets classificados** com o modelo local congelado. 1.114 divergências com rótulos; 305 acima do limiar. Treino, validação, teste e excluídos separados. [Relatório integral](solution/reports/full-population/report.md).
- As 1.192 previsões históricas foram reproduzidas exatamente. Desempenho original: **Local 86% × Jev 45,25% em 800 tickets**. A concordância global inclui treino e não mede generalização.
- **219 testes passaram localmente e no Docker.** As verificações cobrem integridade do lote, fluxos e sinais assistivos de temperatura/urgência.
- **Protótipo somente local, sem VPS**, conforme instrução reiterada por Dhiego. Sete novas capturas, com roteiro, em [evidências finais](process-log/evidencias/entrega-local-2026-09-22/README.md). Esta rodada usa regras/classificador local, sem chamadas pagas; capturas anteriores com IA real e mobile preservadas.
- README, roteiro, PR e roadmap alinhados ao estado atual. [Respostas ao diretor, matriz e demonstração de dez minutos](docs/entrega.md).

## Próximo passo vigente

Revisar o pacote com Dhiego e fechar a submissão. Depois desse fechamento, fork/push/PR pelo canal oficial. Nenhuma ação pública foi realizada. Não ampliar funcionalidades para encerrar o case.

**Limites mantidos:** sistemas fictícios; extração restrita exercitada somente em sete cenários conhecidos; sem avaliação semântica independente nova, sentimento validado ou ganho operacional medido. ROI continua hipótese. A evidência técnica sustenta um protótipo, não implantação de produção.

---

## Histórico do checkpoint anterior — superado pela retomada acima

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

## Pausa solicitada — 22/09/2026

Dhiego encerrou a sessão para cuidar da bebê e pediu retomada amanhã. Não iniciar novos lotes ou chamadas pagas durante a pausa. Última implementação: commit `b2d92d9`, três caminhos executáveis, 204 testes passando localmente e no Docker, capturas e economics por processo. Sem push, PR ou publicação externa.

### Última verificação concluída

Na revisão de prontidão, uma instância Docker temporária, com chave OpenRouter vazia e banco descartável, carregou o modelo incluído e concluiu o autosserviço por regras. Os registros da demonstração existente não foram alterados por essa verificação.

### Retomar daqui

1. Dhiego perguntou se devemos processar todos os tickets para expor resultados. Foi anunciada a rodada local dos **47.837 textos do D2**, mas **ela ainda não foi executada nem seu script implementado**. Preservar artefato/split congelados; separar distribuição da base inteira de desempenho em treino, validação e teste. Os 800 tickets reservados continuam sendo a avaliação original, não uma avaliação nova após desenvolvimento.
2. Não tratar classificação, palavras-chave ou contexto fictício como taxa de resolução autônoma. A avaliação dos fluxos novos ainda se limita a sete cenários conhecidos; discutir/definir amostra nova e referência semântica antes de alegar generalização. Nenhuma rodada de LLM sobre a base inteira foi iniciada.
3. Fechar a revisão de entrega: README ainda contém o roteiro antigo da ficha manual como instrução principal; descrição do PR diz genericamente que todas as decisões são humanas; roadmap e algumas recomendações precisam refletir os três caminhos atuais. Esses ajustes foram identificados, mas ainda não realizados.
4. Consolidar resposta às perguntas do diretor, matriz do que funciona/foi avaliado/é simulado e roteiro curto de demonstração. Comparar somente com os feedbacks de candidatos já trazidos por Dhiego, sem pesquisar outras soluções.
5. Revisão final com Dhiego e, ao fechar a entrega, fork/push/PR conforme instruções oficiais. Manter commits locais até então. Não ampliar funcionalidades antes de resolver evidência e clareza do pacote.

Nenhum resultado da rodada completa deve ser anunciado como existente. ROI continua hipótese, não saving medido. Prazo oficial desconhecido; não reconstruir esforço fictício de 4–6 horas.
