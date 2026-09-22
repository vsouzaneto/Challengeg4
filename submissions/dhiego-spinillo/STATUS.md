# Estado atual

**21/09/2026 — ficha de investigação e rascunhos implementados. Revisão final e preparação da submissão. Commits locais; sem push ou PR.**

## O que está pronto

- Auditoria dos dois datasets, análise visual e relatórios reproduzíveis.
- Classificador local: 86% de concordância com os rótulos em 800 tickets reservados; Jev: 45,25%. Sensibilidade e limites documentados.
- Pareceres reais de Claude, Grok e Codex e confronto das decisões.
- Classificação, confirmação/correção humana, persistência e exportação.
- Três casos discutidos com Dhiego; [decisões registradas](docs/revisao-guiada-tres-tickets.md).
- Ficha de contexto: outros tickets, sistema e notas internas, com estado declarado pelo atendente. Relato de possível incidente separado da categoria e apoiado em trecho literal.
- Próximo passo e rascunho editável por regras, condicionados às conferências. Cópia disponível, sem envio automático.
- 147 testes passam localmente e no Docker, incluindo os novos caminhos e preservação de registros antigos.

## Limites

Não há integração com sistemas, outros chamados, notas ou logs. As conferências são declarações do atendente; nos exemplos, estados preenchidos são simulação explícita. O recap via LLM continua experimental e desligado por padrão: 15/16 saídas estruturalmente válidas e fidelidade aprovada pelo revisor automatizado em 6/15. Nenhum ganho operacional foi medido.

## Próximos passos

1. Apresentar o percurso final no aplicativo: classificar → registrar conferências → preparar orientação/rascunho → revisar e registrar.
2. Revisar o pacote e a descrição do PR para submissão. A revisão qualitativa dos três casos não é aprovação automática da implementação final.
3. Publicar a submissão após o fechamento com o candidato; nada enviado até este registro.

A calculadora arbitrária foi retirada. A hipótese de reduzir perguntas repetidas e encaminhamentos incompletos exige medir também o esforço adicional da ficha; [piloto proposto](docs/piloto-operacional.md).

Meta pessoal declarada na retomada: concluir hoje. Prazo oficial desconhecido. Preparação começou em 15/09; não atribuir total fictício de 4–6 horas. Chaves permanecem locais e ignoradas pelo Git.
