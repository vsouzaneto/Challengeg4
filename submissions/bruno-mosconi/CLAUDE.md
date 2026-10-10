@AGENTS.md

# Específico do Claude Code

O `AGENTS.md` acima vale integralmente. Aqui ficam só os pontos que dependem do Claude Code.

**Primeiro passo:** a revisão completa do `AGENTS.md`, seção 8. Nada do material de partida é confiável até ser revisado.

## Papéis

A conversa principal é o **orquestrador**. Ela planeja, implementa todo o código e a documentação factual, roda os comandos e decide o que fazer com as revisões. As partes narrativas do process log são escritas pelo Bruno.

| Agente | Modelo | Acionar quando | Escreve? |
|---|---|---|---|
| `critico` | Opus 5.5 | revisão inicial (regras, plano, lógica do score); antes dos incrementos 1, 2 e 4; mudança de escopo; banca simulada no fim | não |
| `revisor` | Opus 5.5 | revisão inicial (código, segurança, documentação); fim de cada incremento de código; antes do deploy; antes do PR; dependência nova | não |
| `testador-de-uso` | Sonnet 5.5 | depois de cada incremento de interface; antes do deploy; contra a URL publicada | não edita; só roda os scripts de teste e de prints |

## Regras para revisões

- Passe a cada agente as entradas que o arquivo dele pede, incluindo as saídas de comando. Crítico e revisor não rodam comandos.
- **Concordância entre agentes não é prova.** Antes de corrigir um achado grave, reproduza-o: teste que falha, comando ou print. Se não reproduzir, registre por quê e siga.
- **No máximo 2 rodadas** de cada agente por gatilho. Se ainda houver divergência, leve ao usuário com as evidências.
- Achado sem evidência é descartado.

## Interface: skill `frontend-design` + briefing

A skill oficial `frontend-design` está instalada no nível do usuário (`/plugin install frontend-design@claude-plugins-official`). Use-a em toda tarefa de interface.

A própria skill manda seguir o briefing do projeto quando ele fixa uma direção: "the brief's own words always win". O briefing é este (D41; o protótipo que o aplica, aprovado na D44, está em `process-log/prototipos/rodada-3/`):

- **Produto:** ferramenta que o vendedor abre na segunda de manhã para saber por onde começar, e que o gestor abre para ver onde a equipe travou. Estilo do apple.com: limpo, elegante, caprichado em cada componente. Animação liberada, sempre com propósito; nada de enfeite.
- **Hierarquia:** um protagonista por tela. O que decide ganha tamanho, peso e posição; o resto recua.
  - **Vendedor:** o negócio nº 1 é o herói (produto, empresa, potencial grande, score, prazo, o que fazer e uma frase de motivo). Os nº 2 a 5 vêm menores. O resto fica recolhido em "Ver todos". A saudação é uma linha pequena, com ação e urgência, sem soma de dinheiro.
  - **Gestor:** o protagonista é uma frase com o principal problema da equipe e quem concentra o valor frio. Depois vem a lista de vendedores.
  - A frase de motivo aparece só no herói e no painel, nunca em toda linha.
- **Estrutura:**
  - no computador: lista à esquerda e detalhe à direita, com prévia na equipe;
  - no celular: uma coluna, uma folha que sobe e a barra de abas embaixo;
  - a data sempre visível, num controle segmentado.
- **Cor:** valores do apple.com, conferidos no CSS publicado:
  - fundo branco `#ffffff`; o `#f5f5f7` só em detalhes pequenos (trilha, campo, controle), nunca como fundo de página ou de área;
  - texto `#1d1d1f` e `#6e6e73`; o `#86868b` só em marca, ícone e texto desabilitado, porque não passa no AA como texto;
  - azul só para ação e link: botão `#0071e3`, link `#0066cc`;
  - temperatura sempre com ícone e texto: quente em laranja, esfriando em âmbar, frio em cinza com floco de neve. O frio não é azul, porque azul quer dizer "clicável";
  - modo escuro selecionado, não invertido: fundo `#000000`, superfícies `#1d1d1f`, texto `#f5f5f7`, links `#2997ff`;
  - a paleta passa no validador da skill `dataviz` nos dois modos, e todo texto atinge AA.
- **Tipografia:** `-apple-system, BlinkMacSystemFont`, com a Onest empacotada nos demais aparelhos. A SF Pro não é empacotada, porque a licença não permite. A escala é a do apple.com: título de 34 a 48 px, peso 600; subtítulo de 19 a 21 px; corpo de 17 px; apoio de 14 a 15 px. Algarismos tabulares nos números. Hierarquia por tamanho e peso, nunca por CAIXA ALTA, e nada de rótulo minúsculo em cinza claro para o que importa.
- **Espaço e forma:** respiro generoso. A separação vem do espaço e de uma sombra muito suave (`0 4px 12px rgba(0,0,0,.04)`), não de bordas nem de fundos cinza. Cantos de cerca de 18 px nos cartões e 28 px nos painéis grandes.
- **Componentes caprichados em todos os estados** (normal, passar o mouse, foco, pressionado, desabilitado):
  - barra de navegação fixa de 44 px, translúcida, com `saturate(180%) blur(20px)`;
  - controle segmentado;
  - botão em pílula;
  - linha de lista com área de toque de pelo menos 44 px e seta de que abre um detalhe;
  - painel lateral no computador e folha no celular;
  - anel de foco visível.
- **Termômetro:** a assinatura visual. Os negócios aparecem como pontos de 0 a 138 dias:
  - tamanho = potencial;
  - cor = temperatura;
  - marcas em 90 e 138 dias;
  - os 5 primeiros em destaque;
  - na equipe, uma versão mínima por vendedor.
- **Ícones:** só com função, de uma família de traço fino: Phosphor, peso Light. Nenhum ícone decorativo.
- **Imagens (Krea):** só na entrada, nos estados vazios e no topo do "Como funciona", com um estilo só. Proibido: pessoas, mascotes, bolhas em 3D, brilho exagerado e estética típica de imagem gerada por IA. Em WebP, com texto alternativo e o prompt registrado em `process-log/`.
- **Movimento:**
  - primeira abertura, uma vez por sessão, até 600 ms: o herói sobe, os cartões entram em cascata, os pontos deslizam e o potencial conta;
  - interações em menos de 300 ms: elevação ao passar o mouse, painel com mola e troca de data com os pontos andando e as linhas mudando de lugar;
  - sempre com desaceleração no fim, só `transform` e `opacity`, interrompível, sem animar ação repetitiva e respeitando "reduzir movimento".
- **Estados vazios** dizem o que fazer e levam à aba certa ("Atualize ou dê perda" ou "Prospecção").
- **Nada de botão que não faz nada:** o app só lê dados, então a ação principal é abrir o detalhe.
- **Evitar os vícios que a skill lista:**
  - cartões idênticos com a mesma sombra;
  - rótulo em caixa alta acima de cada título;
  - textos separados por "·";
  - fonte monoespaçada em rótulo de dado;
  - "→" no fim de botão;
  - número grande com rótulo pequeno como solução padrão.
- **Língua:** a do vendedor, com o vocabulário do `AGENTS.md`, seção 10. Moeda sempre em US$.

## Proteções ativas

- O hook `.claude/hooks/guard-pasta.mjs` bloqueia `Edit`/`Write`/`NotebookEdit` em arquivos do repositório fora desta pasta. Se ele bloquear, não tente contornar: explique ao usuário.
- O hook falha fechado: se o próprio hook quebrar, toda edição é bloqueada. Se a mensagem for `Cannot find module` ou `node: not found`, a configuração está quebrada: pare e avise o usuário.
- **Pedem confirmação:**
  - `git push`, `gh`, `vercel`;
  - instalação de pacotes;
  - `git add -f`;
  - edições em `.claude/`, `CLAUDE.md` e `AGENTS.md`.
- **Bloqueados:** `git push --force`, `gh pr merge`, `git add -A`, `git add .` e `git commit -a`.
- **Limite:** regras de Bash comparam o texto do comando, não o efeito. Por exemplo, `git -C . push` escapa da regra de `git push`. Elas protegem contra engano, não são barreira de segurança. A barreira final é rodar `sh tools/adicionar-ao-git.sh` antes de cada commit e checar o escopo antes do PR.
