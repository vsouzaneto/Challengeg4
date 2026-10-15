# Vitrine do processo: case 003 no desafio G4

Esta pasta reúne a história do desenvolvimento do Foco, as evidências do produto e um exemplo simples de como organizei o trabalho no Demiurgo. Serve como material para minha conferência antes da entrega ao G4 e como base para o post.

**Estado:** rascunho para eu ler e aprovar. Nada foi publicado, e fork, push e pull request continuam só comigo.

## Em uma frase: o Demiurgo

É minha aplicação local para organizar tarefas num quadro. Nesta vitrine, mostro somente as tarefas e o Kanban do G4 em [`processo-no-demiurgo.md`](processo-no-demiurgo.md). O funcionamento interno do Demiurgo não faz parte deste material.

| Arquivo | Para quê | Para quem |
| --- | --- | --- |
| [`fluxo-completo.md`](fluxo-completo.md) | O documento vitrine: sete etapas, linha do tempo, erros e correções, testes, segurança, o que se pode e não se pode afirmar | Qualquer leitor, em linguagem simples |
| [`prints-do-app.md`](prints-do-app.md) | Galeria dos prints reais do aplicativo, cada um com um exemplo de uso e a conferência feita | Quem quer ver o produto funcionando |
| [`processo-no-demiurgo.md`](processo-no-demiurgo.md) | Kanban e lista de tarefas do G4, sem outros projetos | Quem quer ver como o trabalho andou |
| [`pagina-processo-submissao.md`](pagina-processo-submissao.md) | Página curta no formato do bloco "Process Log" do template do G4, para copiar para `submissions/<seu-nome>/process-log/` | Avaliadores do G4 |
| [`img/`](img) | Quadro do G4 e captura do Kanban filtrado no G4 | Carrossel e página de processo |

## Recorte para apresentação pública

- **Tarefas e Kanban do G4.** Só entram exemplos do projeto do desafio, sem outros projetos nem conversas internas.
- **Produto e evidência.** O Foco, os testes e os limites do case são apresentados com links verificáveis.
- **Post simples.** A entrada de pedidos no Demiurgo é opcional; o foco visual são as tarefas e o quadro.

## O que esta pasta não faz

- Não altera código, testes nem documentos existentes fora desta pasta.
- Não registra estes documentos no leitor de documentação do aplicativo (`sync_docs.py`, `reader.js`, `documentation.html`): é um passo curto para depois da integração.
- Não afirma tempo gasto, ganho comercial nem poder preditivo.

## Limites conhecidos

- **Capturas finais do Foco foram tiradas em 14/10.** As telas de oportunidades no desktop e no celular estão em `evidence/final-oportunidades-desktop.png` e `evidence/final-oportunidades-celular.png`. As demais capturas do app são de rodadas anteriores.
- **A captura do Kanban é de 13/10.** Ela mostra somente o G4; a figura `quadro-g4.svg` é uma representação dos registros e não uma captura de tela. Estados posteriores não aparecem nessas imagens.
- Em 14/10, a suíte atual passou com **21 testes Python e 7 testes Node**; `sync_docs.py --check` conferiu os 9 documentos do leitor. A auditoria e a avaliação dos dados têm seus resultados e limites descritos nos documentos do produto.
- Este material ainda depende da minha aprovação para publicação.
