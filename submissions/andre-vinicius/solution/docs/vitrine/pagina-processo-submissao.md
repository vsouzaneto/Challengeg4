# Process Log — Case 003 (Lead Scorer): como usei IA

> Página pronta para a pasta `submissions/<seu-nome>/process-log/` do G4 (o nome da pasta é meu). Segue o bloco "Process Log" do [template de submissão](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/templates/submission-template.md). A versão longa, com linha do tempo e evidências, é [`fluxo-completo.md`](fluxo-completo.md).

## Resumo

O case escolhido foi o **003, Lead Scorer**. A solução é um aplicativo local, o **Foco**, que organiza 2.089 oportunidades abertas em três filas (Avançar, Revisar, Qualificar), explica cada posição e sugere a próxima ação. A IA foi usada em duas camadas: **agentes construíram** (Codex e Claude Code) e **agentes revisaram uns aos outros**, com um quadro de tarefas registrando objetivo, revisão e aprovação humana de cada passo. A construção foi feita junto: eu e os agentes.

## Como trabalho: o Demiurgo

O **Demiurgo** é uma aplicação local minha que organiza as tarefas, a documentação e os testes num quadro de tarefas (Kanban). Cada tarefa tem objetivo, critério de aceite, responsável e aprovação minha. Neste desafio, os agentes que apareceram foram Claude Code, Codex e um modelo local. Só o quadro do G4 está em [`processo-no-demiurgo.md`](processo-no-demiurgo.md).

## Ferramentas usadas

| Ferramenta | Para que usei |
| --- | --- |
| **Claude Code** | Ler o repositório do desafio e montar a ficha dos quatro cases; desenhar o brief do plano de esforço; revisar o trabalho do Codex (painéis e redesign); reescrever a documentação lendo o código; integrar a documentação; montar esta vitrine. |
| **Codex** | Auditar os dados; testar e descartar a hipótese histórica; escrever a regra, o servidor e a interface; construir painéis, Kanban, mapa e cartões; revisar o levantamento do desafio e a documentação; publicar o plano de esforço. |
| **Modelo local** | Primeiro rascunho de documentação. Foi recusado em revisão (ver "Onde a IA errou"). |
| **Quadro de tarefas (Demiurgo)** | Guardar objetivo, critério de aceite, responsável, revisão cruzada e aprovação humana de cada tarefa. |

Escolha de ferramentas: nas tarefas com revisão cruzada registrada (levantamento, construção do Foco, painéis, redesign e documentação), um agente construía e **outro** revisava; ninguém revisou o próprio trabalho. Exceções, declaradas: o plano de esforço (publicado numa sessão comigo, sem revisão cruzada registrada), a integração da documentação e esta vitrine, que eu li e aprovei direto.

## Workflow

1. **Levantamento (08/10).** Claude Code leu o repositório público do G4, sem fork nem login, e produziu uma ficha por case e um resumo das regras. Codex revisou e corrigiu três pontos. Tarefa `G4-RECON-01`.
2. **Esforço e escolha (08 e 09/10).** Plano de esforço dos quatro cases (4 a 6 h cada, hipóteses feitas antes de ver os dados). O case 003 foi recomendado e **escolhido por mim**. Tarefa `G4-ESFORCO-01`.
3. **Dados antes do produto (09/10).** Auditoria do conjunto público: 8.800 negócios, 2.089 abertas, nome de produto divergente, 1.425 abertas sem conta. Primeira hipótese preditiva testada com corte cronológico e **descartada** (AUC 0,4854). Commit `3973e3e`.
4. **Primeiro produto (09/10).** Regra operacional simples e explicável, servidor local, interface com filas, filtros, motivo e próxima ação, e testes. Commit `bc5c7a5`. Tarefa `G4-LEAD-SCORER-01` (construção pelo Codex, revisão do Claude Code, minha aprovação em 10/10).
5. **Ciclos de uso com revisão (10/10).** Eu usava o app e pedia a próxima mudança: painéis, Kanban e anotações; depois subpáginas Gerente, Vendedor e Mapa de regiões com cartão de identificação. Codex construiu, Claude Code revisou, eu aprovei. Tarefas `G4-003-PAINEIS-01` e `G4-003-REDESIGN-01`.
6. **Documentação e testes (09 e 13/10).** Rascunho do modelo local recusado; documentação refeita do zero contra o código, com especificações, plano de testes e registro por tarefa. Em 13/10, uma segunda rodada tirou da documentação as duas capturas da própria página de documentação, que não mostravam o app em uso, e usou só capturas reais do aplicativo; o Codex revisou (aprovado) e eu aprovei. Tarefas `G4-003-DOCS-01` e `G4-INTEGRAR-DOCS-01` (juntar a documentação na branch de trabalho, resolvendo um conflito).
7. **Vitrine (13/10).** Esta página, a versão longa e o rascunho de divulgação. Tarefa `G4-VITRINE-01`.

## Onde a IA errou e como corrigi

| O que deu errado | Como percebi | O que fiz |
| --- | --- | --- |
| A primeira hipótese preditiva não separava ganhos de perdas (AUC 0,4854): o grupo "melhor" ganhou **menos** (63,45%) que a média (64,84%). | Avaliação com corte cronológico, separando ajuste e teste. | Descartei a hipótese. A fila usa regra transparente e a tela diz que o índice não é probabilidade. |
| O rascunho de documentação do modelo local falava de login, microsserviços e banco de dados que o projeto não tem, não citava arquivo nem teste algum e estava no repositório errado. | Revisão comparou com a especificação técnica do próprio projeto. | Recusado duas vezes e refeito do zero a partir do código e dos testes. |
| A página do vendedor não mostrava as vendas históricas pedidas no critério de aceite. | Revisão cruzada do diff contra o critério. | Ajuste feito em 4 minutos, com um teste novo que prova que o score não muda com os fechamentos. |
| Uma rodada começou no repositório errado. | O próprio agente parou antes de alterar qualquer coisa. | Rodada refeita no repositório certo. |
| Documentação antiga dizia "celular pendente" quando o histórico já mostrava o acesso confirmado; e não registrava que o teto de 100 do índice nunca é alcançado. | Releitura contra o histórico do git e o código. | Reconciliado e documentado. |
| A documentação trazia dois prints da própria página de documentação, que não mostravam o app. | Li a documentação e apontei. | Trocados por prints reais do aplicativo, com legenda e números conferidos. |
| O merge da documentação deu conflito em 10 arquivos com um commit feito direto na branch de trabalho. | Na tentativa de merge, depois da minha aprovação. | Desfeito sem perder nada e resolvido numa tarefa própria, mantendo o conteúdo aprovado e o fato mais recente do app. |

## O que eu adicionei que a IA sozinha não faria

- **Escolher o problema e dizer não.** Escolhi o case, exigi uma entrega isolada, sem material pessoal, e decidi qual trabalho valia a pena.
- **Usar o produto e mudar o rumo.** Os painéis, o Kanban, o mapa ilustrativo e o cartão de identificação dos vendedores vieram do uso e do feedback, não de um plano inicial. O pedido de um mapa foi "a gente cria um mapa qualquer", e o resultado foi marcado na tela como ilustrativo.
- **Aceitar um resultado negativo.** A decisão de não vender previsão onde o teste não sustentava veio do número medido.
- **Aprovar.** Nenhuma tarefa foi concluída sem aprovação humana registrada.

## Quantas iterações

Oito tarefas do G4 no quadro na data da consulta (seis concluídas, uma em andamento e uma no backlog; ver [`processo-no-demiurgo.md`](processo-no-demiurgo.md)), mais a construção do Foco, registrada em outro agrupamento. Duas versões de construção e duas de revisão nos painéis, uma de construção e uma de revisão no redesign, duas recusas de rascunho de documentação e uma reescrita. A sequência está resumida no [registro escrito](../../PROCESS_LOG.md); o histórico Git local anterior não acompanha esta submissão.

## Testes e verificação

- Python: 8 testes com os arquivos reais do desafio (`tests/test_scoring.py`) e 2 sintéticos (`tests/test_sales.py`); a documentação acrescentou 11 testes de fronteira da regra (`tests/test_rules.py`). Em 10/10, Codex registrou **10 testes Python com os arquivos reais e 7 Node passando**; em 13/10, na revisão da documentação, **21 testes Python e 7 Node**.
- Node: 7 testes (`tests/test_filters.cjs`, `tests/test_business.cjs`). Executados também em 13/10 por Claude Code: **7 de 7 passaram**.
- Auditoria e avaliação: `python audit.py` e `python evaluate.py` reproduzem as contagens e o AUC.
- O que **não** foi executado pelo agente que montou esta vitrine: a suíte Python e os scripts de auditoria (o ambiente não permitiu executar Python). Os resultados Python citados vêm das execuções do Codex, com origem.

## Evidências

- [x] **Histórico do trabalho:** sequência de decisões e iterações no [registro escrito](../../PROCESS_LOG.md). Os commits locais anteriores não acompanham este PR.
- [x] **Código e testes:** `scoring.py`, `tests/`.
- [x] **Capturas da interface:** pasta [`evidence/`](../../evidence/README.md) e [`docs/evidence/`](../evidence), com legenda e exemplo de uso em [`prints-do-app.md`](prints-do-app.md).
- [x] **O processo no quadro de tarefas, só do G4:** [`processo-no-demiurgo.md`](processo-no-demiurgo.md) (Kanban e lista de tarefas).
- [x] **Narrativa escrita:** [`PROCESS_LOG.md`](../../PROCESS_LOG.md) e [`fluxo-completo.md`](fluxo-completo.md).
- [ ] Screen recording do workflow (não gravado).
- [ ] Export das conversas com os agentes (não incluído: contêm caminhos e contexto que não fazem parte da entrega).

## Limitações

- O conjunto de dados é fictício e termina em 2017. Não há histórico de mudanças de estágio. **Não se afirma ganho comercial.**
- O índice é uma regra operacional, não uma probabilidade, e não foi validado com vendedores.
- O mapa é ilustrativo e comporta as três regiões do conjunto.
- Interação em celular real e navegação por teclado não têm inspeção detalhada registrada.
- A versão pública foi conferida em 14/10 e depende da minha aprovação antes da publicação.
- Não há captura real da tela principal (a fila) do Foco. Do Demiurgo, há só o Kanban filtrado no G4 ([`processo-no-demiurgo.md`](processo-no-demiurgo.md)).
