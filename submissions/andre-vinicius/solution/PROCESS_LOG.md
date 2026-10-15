# Process log — case 003

Registro do uso de IA no desenvolvimento do Foco. Tem duas partes: a **narrativa** das decisões (seção 1) e o registro por tarefa, agente e teste (seções 2 a 5). Resultados de teste e de avaliação aparecem com a origem; o que não foi executado numa rodada é dito como não executado. Os hashes citados descrevem o histórico local de desenvolvimento, que não acompanha este PR para evitar expor arquivos internos de versões antigas.

## 1. Narrativa das decisões

1. **Decomposição.** Partimos da decisão do vendedor na segunda-feira: avançar conversas recentes, revisar negócios parados e qualificar primeiro contato. Definimos uma tela utilizável e documentação curta, em vez de começar por um modelo sem interface. Criamos um repositório separado para a entrega, sem arquivos dos sistemas de gestão pessoais.
2. **Auditoria do dataset.** O assistente obteve o ZIP público indicado no brief, contou os registros, conferiu chaves, datas e campos vazios. Detectou a grafia `GTXPro` no pipeline versus `GTX Pro` no catálogo e 1.425 oportunidades abertas sem conta. Ajustamos a junção e garantimos que conta ausente não elimina uma ação.
3. **Hipótese testada e rejeitada.** Primeiro codificamos afinidade histórica suavizada por produto e setor. A avaliação cronológica resultou em AUC 0,4854 e taxa Won no quartil superior de 63,45%, abaixo dos 64,84% gerais do teste. Seria enganoso vendê-la como probabilidade preditiva. Substituímos essa hipótese por uma regra operacional transparente e explicamos a limitação na própria tela.
4. **Produto e iteração.** O assistente construiu um servidor local em Python padrão e uma interface web com filas, filtros, detalhes e próximo passo. O índice usa apenas estágio aberto, tempo de engajamento, presença da conta e preço de catálogo. Documentamos que preço é proxy de impacto, nunca valor esperado. O usuário definiu a exigência de uma entrega externa isolada; mantivemos os dados e materiais pessoais fora dos arquivos versionados.
5. **Verificação.** Revisamos os critérios do [brief oficial](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/challenges/build-003-lead-scorer/README.md) e do [guia de submissão](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/submission-guide.md). Os testes verificam leitura de dados reais, normalização, negócios abertos, ordem determinística, conta ausente, resposta HTTP e ausência de vazamento de `close_value`/`close_date` na prioridade. A aplicação permanece protótipo: não afirmamos ganho comercial sem piloto.
6. **Exploração de interface.** Um mock visual fornecido pelo usuário orientou a Mesa comercial: comparação à esquerda e explicação da oportunidade à direita. Mantivemos também Fila de decisão e Visão por filas para comparar hierarquias, com tema claro/escuro/automático e detalhe separado no celular. As três telas usam exatamente o mesmo payload e regra de prioridade.
7. **Documentação e usabilidade.** Após a leitura do produto pelo usuário, a página Método passou a usar a mesma navegação e o mesmo tema do Foco. Criamos especificações, plano de testes, guia de operação e roteiro de evoluções, acessíveis por Documentação na interface. A largura de lista e detalhe ganhou ajuste manual no desktop. Ideias de notas, movimentos de cartões e painéis por pessoa/região foram registradas como propostas, sem simular persistência ou dados que o case não possui.
8. **QA na cópia isolada.** Acrescentamos testes de combinação de filtros, busca, data de engajamento ausente e desempate. A data de referência histórica foi fixada em 31/12/2017 para impedir que alterações em datas de fechamento mudem o ranking.
9. **Painéis e feedback de uso.** A interface ganhou páginas por gerente e vendedor, painel de preços e mapa ilustrativo com as três regiões existentes nos dados. A pedido do usuário, os cartões passaram a funcionar como identificação visual com avatares ilustrados e ação “Acessar detalhes”. O vínculo vendedor–gerente ficou visível nos detalhes. O mapa passou a exigir a escolha da região antes de mostrar seus vendedores e amplia a região escolhida.
10. **Duas experiências no mesmo produto.** O feedback distinguiu uso operacional de narrativa de construção. A navegação “Usar Foco” apresenta a rotina e explica a prioridade em termos comerciais; “Construção do case” reúne problema, dados, decisões, verificações e limites.
11. **Evoluções registradas sem simular dados.** Gestão compartilhada de pessoas, tarefas por status, preços negociados, agenda semanal e mapa geográfico real precisam de fonte, permissões e modelo de dados. Permanecem no roteiro; a base histórica do case não contém esses campos.
12. **Documentação completa (13/10/2026).** Uma primeira tentativa de documentação, feita por um modelo local, foi recusada (só trazia avisos de pendência e estava no repositório errado) e refeita do zero neste repositório. Nesta passagem cada afirmação foi conferida contra o código e os testes: foram acrescentadas a especificação de negócio com rastreabilidade regra → código → teste, a especificação funcional com todas as telas e endereços, a técnica com o contrato da API e a aritmética exata do índice, o plano de testes com inventário e resultados, e o ciclo de mudança. A leitura destacou três fatos que a documentação anterior não registrava de forma explícita: o índice só assume valores em degraus de 10 e seu teto de 100 não é alcançado (máximos 95, 80 e 55); `Engaging` sem data de engajamento entra em Avançar; e o mapa só comporta as três regiões do dataset. Foi acrescentado `tests/test_rules.py` para fixar as fronteiras da regra.

13. **Segundo redesign (14/10/2026, branch `codex/g4-003-redesign-02`).** A página de metodologia passou a mostrar as filas, a aritmética do índice, os campos que não pontuam e os limites de uso em linguagem simples. Rótulos de navegação e textos da carteira foram alinhados com essa explicação; a regra em `scoring.py` não foi alterada. A revisão fina dos botões e textos apontados pelo autor depende da lista solicitada nesta rodada. Com os CSVs públicos baixados pelo script do projeto (SHA-256 conferido), passaram 21 testes Python e 7 Node; `sync_docs.py --check` conferiu as nove cópias. O navegador de automação não estava disponível nesta rodada, por isso não foram produzidas capturas novas de desktop ou celular.

14. **Ajuste da navegação lateral (14/10/2026).** Após o retorno do autor sobre “botões laterais, ícones e etc.”, os quatro destinos da barra lateral ganharam ícones vetoriais distintos e rótulos visíveis no celular. O atalho Preços passou a aparecer junto aos demais painéis no desktop. A página de metodologia e a regra de pontuação permanecem como descritas na etapa anterior. Com os CSVs públicos baixados pelo script do projeto (hash conferido), passaram 21 testes Python e 7 Node; `sync_docs.py --check` conferiu nove cópias. Capturas novas não foram possíveis porque o navegador de controle visual estava indisponível; as imagens antigas não são apresentadas como resultado deste ajuste.

15. **Revisão visual e repetição dos testes (14/10/2026).** A branch anterior ao segundo redesign (`193a83f`) e a versão atual foram abertas com os mesmos CSVs públicos e capturadas em desktop (1440 × 900) e largura de celular (390 × 844). Os oito arquivos em [`evidence/`](evidence/README.md) mostram Oportunidades e Metodologia antes/depois. Os destinos principais ficaram legíveis no celular, sem rolagem horizontal; não foi feito teste em aparelho físico. O ZIP da base conferiu com o SHA-256 esperado. A suíte completa passou com 21 testes Python; 7 testes Node passaram; `sync_docs.py --check` conferiu nove documentos. Uma primeira execução Python sofreu interrupção transitória da conexão HTTP durante a leitura de `/api/deals`; o teste isolado e a suíte completa passaram na repetição.

16. **Ícones coloridos e botões finais (14/10/2026).** Após o autor confirmar que gostou da versão colorida, a navegação voltou a usar ícones coloridos. Os botões Fila, Mesa e Kanban ganharam rótulos curtos no celular e áreas de toque maiores; Filtrar e as abas dos painéis receberam o mesmo tratamento. As capturas finais estão em [`evidence/final-oportunidades-desktop.png`](evidence/final-oportunidades-desktop.png) e [`evidence/final-oportunidades-celular.png`](evidence/final-oportunidades-celular.png). A suíte passou com 21 testes Python e 7 Node, e a sincronização de nove documentos foi conferida. Não houve teste em aparelho físico. A entrega e sua publicação dependem da aprovação do autor.

## 2. Quem fez o quê, por tarefa

Fonte: exportação do quadro de tarefas do projeto `g4-ai-master`, em 13/10/2026. Horários de aprovação em UTC.

| Tarefa | Frente e agente | Resultado registrado | Aprovação do autor |
| --- | --- | --- | --- |
| G4-RECON-01 — ler o repositório do desafio e fichar os 4 cases | Reconhecimento: Claude Code. Revisão cruzada: Codex (rodada 202610081609-d5d6, “aprovado”) | Fichas e regras de submissão; sem fork nem PR | 09/10/2026 03:09 |
| G4-ESFORCO-01 — esforço e plano de cada case | Esforço: Claude Code (responsável). Publicação registrada por Codex na branch `codex/g4-esforco-01`, commit `de36a8a` | Plano por case; o autor escolheu o 003 | 09/10/2026 03:32 |
| Construção do produto inicial (auditoria, hipótese, regra, interface, testes) | Codex, a pedido do autor; ver `git log` de 09/10/2026 | Commits de 09/10/2026 (`3973e3e` a `3af65a4`) e `48c08c7` | Decisões do autor ao longo do uso |
| G4-003-PAINEIS-01 — painéis, Kanban, anotações, status | Implementação: Codex (rodada 202610101514-102f). Revisão cruzada: Claude Code (rodada 202610101535-c46d, “aprovado”) | Codex: 10 testes Python, 6 Node, auditoria e avaliação passaram. Revisão: Node 6/6 reexecutado, `scoring.py` sem mudança, Python não executado | 10/10/2026 15:37 |
| G4-003-REDESIGN-01 — subpáginas Gerente, Vendedor, Mapa e “RG” com avatar | Implementação: Codex (rodada 202610101556-2a8e). Revisão cruzada: Claude Code (rodada 202610101920-176c, “aprovado”) | Codex: 10 testes Python com CSVs reais e 7 Node. Revisão: Node 7/7 reexecutado; totais 908 + 748 + 433 = 2.089 conferidos nas capturas; Python não executado | 10/10/2026 22:31 |
| G4-003-DOCS-01 — documentação completa | Documentação: Claude Code (rodada 202610130854-9a54). Revisão cruzada: Codex (rodada 202610131433-ae9e, “aprovado”) | Especificações e leitor; ver seção 7 | 13/10/2026 11:40 |
| G4-VITRINE-01 — vitrine e LinkedIn | Vitrine iniciada por Claude Code; material público simplificado para tarefas e Kanban | Rascunho em `docs/vitrine/`, sem publicação | Pendente para a versão pública |
| G4-003-REDESIGN-02 — botões, textos e metodologia no app | Codex (rodadas de 14/10/2026) | Metodologia, ícones coloridos, botões, 21 testes Python e 7 Node; capturas comparativas e finais em `evidence/` | Pendente |

## 3. Commits do repositório local de desenvolvimento

| Commit | Data | Autor do commit | Assunto |
| --- | --- | --- | --- |
| `3973e3e` | 09/10/2026 | autor | Auditoria dos dados e rejeição do sinal histórico fraco |
| `0877b69` | 09/10/2026 | autor | Dados locais e artefatos privados fora da entrega |
| `bc5c7a5` | 09/10/2026 | autor | Aplicação local explicável de priorização |
| `f9ef33c`, `e43aff8`, `3e2702f` | 09/10/2026 | autor | Exploração de design, três visões e documentação do case |
| `cd1e947`, `2d15357` | 09/10/2026 | autor | Instância opcional na rede local e registro do acesso pelo celular |
| `3af65a4`, `48c08c7` | 09/10 e 10/10/2026 | autor | Próxima iteração de experiência; QA e documentação consolidados |
| `2ed6af2`, `ca944b1` | 10/10/2026 | Codex | G4-003-PAINEIS-01 (rodadas 202610101449-89e8 e 202610101514-102f) |
| `2026ea6` | 10/10/2026 | autor | Revisão: ícone e link de Painéis em todas as barras laterais |
| `6d965c1` | 10/10/2026 | Codex | G4-003-REDESIGN-01 (rodada 202610101556-2a8e) |
| `26f3b65`, `d981caf` | 10/10/2026 | autor | Cartões de vendedor refinados; separação entre produto e construção do case |
| `0a2be16`, `15bb553` | 10/10/2026 | autor | Processo transferível e processo verificado do Demiurgo |

O autor de um commit **não** identifica quem produziu o trabalho: commits feitos pelo autor humano podem conter trabalho de agente, e a rodada de um agente pode ser commitada pelo acionador. Para saber quem fez o quê vale o registro da tarefa (seção 2).

## 4. Ocorrências, limitações e correções registradas

| Quando | Ocorrência | Tratamento |
| --- | --- | --- |
| 08/10/2026 | Em G4-RECON-01 o ambiente da rodada pediu aprovação para executar `node`; o documento ficou commitado e não publicado | Declarado na evidência; a revisão do Codex validou o diff e o kit |
| 10/10/2026 | Em G4-003-PAINEIS-01 e G4-003-REDESIGN-01 o ambiente não deixou escrever em `.git`; as alterações foram commitadas pelo acionador da rodada | Declarado nas evidências; commits `ca944b1` e `6d965c1` |
| 10/10/2026 | Nas duas revisões de Claude Code, Python e a pasta `data/` não estavam disponíveis | Os vereditos dizem “não executado” e confiam no registro do Codex, sem apresentá-lo como execução própria |
| 10/10/2026 | O plano de testes passou a dizer que a confirmação pelo celular estava pendente, embora o registro de 09/10 mostrasse HTTP 200 vindo de um dispositivo da rede e a abertura confirmada pelo autor | Reconciliado em 13/10/2026 a partir do histórico do git; ver [plano de testes](docs/test-plan.md) |
| Antes de 13/10/2026 | O primeiro rascunho de documentação (modelo local) foi recusado: só avisos de pendência e no repositório errado | Refeito do zero neste repositório |
| 13/10/2026 | Nesta rodada o ambiente exigiu aprovação para executar Python e baixar o dataset, que a rodada não pode pedir | Foram executados os testes Node; a suíte Python, `audit.py`, `evaluate.py` e o novo `tests/test_rules.py` ficaram **não executados**, e isso está dito no [plano de testes](docs/test-plan.md) |

## 5. Hierarquia de evidência

Para quem recebe esta submissão, a evidência reproduzível é: (1) testes versionados em `tests/` e os comandos de [operação](docs/operations.md); (2) resultados com data no [plano de testes](docs/test-plan.md); (3) capturas do produto e do quadro G4; (4) esta narrativa e a tabela de tarefas. Os hashes acima são contexto do histórico local, não links verificáveis neste PR.

## 6. Ferramentas de IA e papéis

- **OpenAI Codex:** auditoria dos dados, hipótese histórica, regra, interface, painéis, redesign, documentação inicial e verificação.
- **Claude Code:** reconhecimento do desafio, plano de esforço (publicado pelo Codex), revisões cruzadas de painéis e redesign, e esta documentação completa.
- **Demiurgo:** ambiente de desenvolvimento do autor, usado para organizar tarefas, critérios de aceite, frentes, revisões e evidências. O Foco não depende dele para rodar.
- **Modelo local:** primeiro rascunho de documentação, recusado.
- **Autor:** escolha do case, exigência de entrega isolada e sem material pessoal, uso do produto, correções de rumo, aprovação das tarefas. Fork, push e PR são feitos somente por ele.

As decisões de escopo e privacidade vieram do autor; a rejeição da hipótese histórica veio dos resultados medidos, não de preferência por uma técnica. A IA não operou de forma autônoma nem validou ganho comercial: nenhum ganho foi medido.

## 7. Revisão cruzada de documentação — 13/10/2026

Codex, rodada `202610131433-ae9e`, leu os dois commits `f8ffed0` e `85c461d` e o diff desde `15bb5533533f`, conferiu especificações contra o código e abriu as imagens do Foco. Baixou o dataset público com o hash esperado e executou 21 testes Python, 7 Node, auditoria, avaliação, sintaxe de todos os scripts e sincronização dos nove documentos. Resultados e limitação do navegador constam na seção 4.4 do [plano de testes](docs/test-plan.md).

Correções pequenas na revisão: distinguiu campos copiados para contexto dos campos usados no cálculo e identificou as imagens antigas como evidência histórica, pois algumas antecedem o layout atual. Não alterou a aplicação. Não realizou merge, push, PR nem aprovação da tarefa; a decisão humana continua pendente.
