# Exports das conversas com IA

O projeto usou duas sessões de IA, ambas em 15/10/2026. As duas estão exportadas aqui na íntegra, na ordem em que aconteceram, sem edição de conteúdo.

| Sessão | Ferramenta | Etapas | Export |
|---|---|---|---|
| 1 | Codex | Escolha do desafio, entendimento do problema, G1 (dados), G2 (modelo) e primeira versão do G3 | [../conversa-exportada-2026-10-15.md](../conversa-exportada-2026-10-15.md) |
| 2 | Claude Code | Revisão crítica do G3, regra do prazo máximo, backtest, Lead Kanban, Dashboard, procedimento, UX, revisão de entrega, análise dos outros PRs e vídeo tutorial | [2026-10-15-claude-code-g3-a-entrega.md](2026-10-15-claude-code-g3-a-entrega.md) |

## O que está em cada export

- **Codex:** export gerado pelo próprio Codex, a pedido do candidato, com as mensagens visíveis da conversa.
- **Claude Code:** gerado a partir do log local da sessão. Traz:
  - as mensagens do candidato e as respostas da IA, com data e hora;
  - as ações executadas pela IA (comandos, arquivos lidos e editados, erros), recolhidas em blocos "Ações da IA";
  - os resumos automáticos que a ferramenta gera ao compactar conversas longas.

## O que foi omitido ou substituído

- Saídas brutas das ferramentas, raciocínio interno do modelo e instruções de sistema.
- O e-mail do candidato e caminhos locais da máquina.
- Nomes de outros projetos e clientes do candidato, trocados por `[projeto privado]`. Esses projetos serviram apenas como referência de experiência na escolha do desafio. Nenhum código ou dado deles entrou na solução.

## Como ler

Os pontos de virada estão nas mensagens do candidato:
- o pedido de análise crítica que mudou a regra do G3;
- o critério de UX ("qualquer usuário consiga interpretar");
- a retirada da comparação com a regra anterior;
- o pedido de avaliação contra o README do challenge.

As correções da IA aparecem logo depois, nas respostas e nas ações. O resumo de cada etapa está nos arquivos `2026-10-15-*.md` da pasta acima.
