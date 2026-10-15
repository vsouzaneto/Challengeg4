# Como o Foco foi desenvolvido com o Demiurgo

Este registro descreve o **case G4 003**. A fonte da sequência de tarefas é a exportação de evidências do projeto `g4-ai-master` no Demiurgo, consultada em 13/10/2026 (a versão anterior deste texto era de 10/10/2026). Código, testes e capturas estão neste repositório. Estados das tarefas podem mudar depois desta data.

## O papel de cada parte

| Parte | Função no case | Onde verificar |
| --- | --- | --- |
| autor | Escolhe o case, define o que deve funcionar, experimenta a interface, corrige o rumo e aprova entregas. | Decisões e feedback registrados nas tarefas G4 e no `PROCESS_LOG.md`. |
| Demiurgo | Guarda tarefas, objetivos, frentes, critérios de aceite, rodadas, revisões e decisões. | Tarefas `G4-RECON-01`, `G4-ESFORCO-01`, `G4-003-PAINEIS-01` e `G4-003-REDESIGN-01`. |
| Agentes | Produzem uma frente definida ou revisam o trabalho de outra frente. Codex implementou os painéis e o redesign; Claude Code fez o reconhecimento do desafio, revisou as duas entregas de interface e escreveu esta documentação; um modelo local recebeu o primeiro rascunho de documentação, que foi recusado. | Evidência de cada tarefa no quadro; veredito de revisão em `G4-003-PAINEIS-01` e `G4-003-REDESIGN-01`; histórico de `G4-003-DOCS-01`. |
| Repositório G4 | Guarda o aplicativo, especificações, testes, decisões e imagens desta entrega. | `static/`, `docs/`, `tests/` e capturas. O histórico local anterior não acompanha esta submissão. |

O Demiurgo é o ambiente de desenvolvimento que organizou tarefas, agentes, revisões e decisões deste case. O Foco é o produto entregue. O aplicativo não depende do Demiurgo para exibir a carteira. Esta página descreve o processo sem expor dados ou funcionamento interno de outros projetos.

## Sequência observada

| Etapa | Registro no Demiurgo | Resultado verificável |
| --- | --- | --- |
| Entender o desafio | `G4-RECON-01`, concluída | Leitura das opções e regras antes da escolha. A tarefa registra revisão cruzada e aprovação do autor. |
| Comparar esforço | `G4-ESFORCO-01`, concluída | Estimativas por case para apoiar a escolha. O autor escolheu o 003 como foco. |
| Construir o produto inicial | Registro de processo e commits do G4 | Auditoria da base, teste de hipótese preditiva, regra operacional explicável, interface e testes. |
| Ampliar a experiência | `G4-003-PAINEIS-01`, concluída | Painéis, Kanban, anotações locais e histórico do vendedor. Codex entregou, Claude Code revisou e autor aprovou. |
| Refinar a navegação | `G4-003-REDESIGN-01`, concluída | Subpáginas Gerente, Vendedor e Mapa de regiões, cartões de identificação com avatar ilustrado e mapa ilustrativo. Codex entregou, Claude Code revisou (Node 7/7 reexecutado; scoring.py sem mudança) e autor aprovou em 10/10/2026. |
| Documentação completa | `G4-003-DOCS-01`, concluída após a consulta | Especificações de negócio, funcional e técnica, plano de testes, operação e registro de processo, conferidos contra o código; revisão do Codex aprovada em 13/10. |
| Vitrine e segundo redesign | `G4-VITRINE-01` e `G4-003-REDESIGN-02`, em preparação final em 14/10 | A vitrine pública mostra tarefas e Kanban do G4. O segundo redesign acrescenta metodologia, ícones coloridos e botões revisados; a publicação depende da aprovação do autor. |

## O ciclo de trabalho mostrado pelo case

1. **Definir a decisão e o aceite.** A tarefa registra o problema, o responsável, as frentes e as condições para considerar a entrega pronta.
2. **Trabalhar em cópia isolada.** A mudança é feita em branch ou cópia própria, mantendo o aplicativo principal utilizável enquanto o diff é examinado.
3. **Confrontar a solução com dados e testes.** No Foco, `audit.py` confere a base, `evaluate.py` documenta a hipótese preditiva rejeitada, os testes Python verificam dados e API, e os testes Node verificam filtros, painéis e anotações.
4. **Revisar e corrigir.** A tarefa de painéis teve revisão cruzada. Uma rodada inicial da documentação foi devolvida porque o rascunho não trazia afirmações verificáveis sobre o G4 e estava no lugar errado; o material foi refeito no repositório do case.
5. **Submeter à decisão humana.** O autor aprovou a tarefa de painéis e continuou a orientar o design. A aprovação de uma tarefa no Demiurgo e a integração local do código são registros diferentes.
6. **Registrar limites e próxima evolução.** Dados históricos fictícios, notas apenas no navegador e mapa sem coordenadas reais aparecem no produto e na documentação. Recursos de CRM compartilhado permanecem no roteiro.

## Evidências para reproduzir

- `PROCESS_LOG.md`: decisões e correções desde a primeira hipótese.
- `docs/data-audit.md`: contagens, qualidade da base e avaliação histórica.
- `docs/business-spec.md`, `docs/functional-spec.md` e `docs/technical-spec.md`: negócio, telas e implementação, com rastreabilidade das regras para os testes.
- `docs/test-plan.md`: comandos, resultados e capturas da rodada.
- `docs/operations.md`: como executar e conferir uma atualização.
- `docs/product-roadmap.md`: estado atual e hipóteses futuras.

A última execução completa registrada (10/10/2026, tarefa de redesign) teve **10 testes Python com os CSVs reais e 7 testes Node** passando. Em 13/10/2026 os 7 testes Node foram reexecutados e passaram; Python não pôde ser executado naquela rodada. Os 11 testes de `tests/test_rules.py` foram escritos depois e ainda aguardam execução. Detalhes e saídas em [plano de testes](test-plan.md). Capturas mostram a interface em desktop e largura reduzida; a conexão pelo celular foi validada em 09/10/2026 e a interação detalhada ainda não foi inspecionada. Nenhum ganho comercial foi medido.

## O que se pode reaproveitar

O método serve como exemplo de organização para outras aplicações: transformar uma ideia em decisão observável, dividir a implementação, guardar evidência, revisar com outra perspectiva e obter aprovação humana. Cada uso pessoal ou corporativo precisa definir seus próprios dados, permissões, riscos e critérios de sucesso. O código e as informações de outros projetos não fazem parte desta entrega do G4.
