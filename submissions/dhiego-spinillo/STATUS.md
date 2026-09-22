# Estado atual

**21/09/2026 — protótipo funcional em revisão com Dhiego. Commits locais; sem push ou PR.**

## Concluído

- Auditoria dos dois datasets e análise visual lida pelo candidato.
- Comparação no mesmo teste reservado: classificador local 86%, Jev 45,25% (800 tickets). Sensibilidade e revisão de protocolo registradas.
- Revisões reais de Claude, Grok e Codex; [confronto](process-log/revisao-2026-09-21/decisoes.md).
- FastAPI/Jinja/JavaScript/SQLite/Docker funcionando localmente: classificação, política de confirmação humana, registro do motivo e exportação.
- Recap integrado e avaliado: 15/16 saídas estruturalmente válidas; fidelidade aprovada pelo revisor automatizado em 6/15. Experimental, desligado por padrão na interface e na API.
- 122 testes passam; Docker construído e executado localmente.

## Revisão em andamento

Dhiego está explorando o aplicativo. Questionou o destaque de uma economia simulada de 8,33 horas/mês. A calculadora foi retirada: as premissas eram arbitrárias e o resultado não justificava a intervenção. Ganhar a comparação técnica não demonstra redução de sobrecarga.

**Lacuna principal:** validar relevância operacional do recorte e utilidade para o atendente. Não há ganho de tempo medido, referência humana de qualidade do recap nem piloto na operação. A substituição da calculadora por um plano de medição não resolve essa lacuna por si só.

## Próximos passos

1. Concluir a [revisão guiada de três tickets](docs/revisao-guiada-tres-tickets.md): caso 1 discutido (conferir registro e perguntar ao cliente somente se faltar confirmação necessária); caso 2 em apresentação; caso 3 preparado.
2. Delimitar a recomendação à evidência disponível; revisar o recorte se necessário.
3. Fechar evidências visuais, pacote reproduzível e descrição do PR.
4. Submeter somente após o fechamento da entrega. Nenhuma aprovação final do candidato foi presumida.

Meta pessoal declarada na retomada: concluir hoje. Prazo oficial segue desconhecido. Preparação começou em 15/09; não atribuir retrospectivamente um total fictício de 4–6 horas. Chaves permanecem locais e ignoradas pelo Git.
