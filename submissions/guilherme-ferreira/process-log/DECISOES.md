# Decisões

As decisões humanas desta entrega: o que a IA perguntou ou propôs, o que eu escolhi, quando e onde está a prova.

**Como este arquivo foi feito.** O plano previa que eu escrevesse este arquivo com as minhas palavras. No fechamento, aprovei usar a lista que a IA montou a partir das perguntas e respostas registradas nos transcripts, sem reescrevê-la ("1. pode manter", S1 21:44). A seção E, com as outras decisões dessa mesma mensagem, a IA acrescentou depois. As citações são literais, com os erros de digitação originais. Em cada pergunta, a IA explicou as opções antes de perguntar; as explicações estão nos transcripts, no horário indicado.

Horários de Brasília, 25/09/2026. "S0" é a sessão de pesquisa e "S1" a de execução ([`evidencias/transcripts/`](evidencias/transcripts/)).

## A. O que decidi por conta própria, sem opção sugerida

| Quando | O que eu disse | O que isso decidiu |
|---|---|---|
| S0 13:31 | "analisa os PR dos outros canditados" | Usar as reviews públicas do avaliador como critério de qualidade |
| S0 13:49 | "Cria a estratégia para o 004 Social. QUer uma abordagem com todos os pontos de sucesso do outros candidatos, quero um log melhor e mais claro para pessoas fora do contexto de tecnologia analisarem." | O desafio 004 e um process log para quem não é da área técnica |
| S0 13:51 | "me mostra" e "não começa ainda", enviadas enquanto a IA criava a branch e as pastas da entrega | Pedi para ver o plano e segurei o início da execução |
| S0 13:56 | "reavalia o plano com fable e veja as falhas." | Revisão do plano por outro modelo, que achou 9 falhas |
| S0 13:58 | "sim, mas antes, usa as skills de mkt que temos aqui com base nesse escopo e crie o plano." | Frameworks de marketing como base da estratégia |
| S0 14:09 | "3. pode fazer de acordo como teste." | Deploy do Radar no escopo, tratado como teste |
| S1 15:01 | "https://g4business.com quando criar a aplicação, usa esse site com base de UX" | O visual do Radar |
| S1 15:07 | "prints serão da aplicação somente. Segue ai." | Prints só da aplicação (e seguir em automático, na seção B) |
| S1 15:44 e 16:33 | Mandei os prints das minhas respostas | Entregar também os prints das decisões |
| S1 19:35 | "aprovado, executa na sessão" | Execução do plano do Radar nesta sessão, com revisão final independente |
| S1 20:22 | "coloca select box. Assim ficou uma merda." (com print da tela) | Reprovei o filtro de seleção múltipla do mapa ao ver a tela |
| S1 20:26 | "Coloca um check box para selecionar mais de um" | Filtro com checkboxes |
| S1 21:05 | "pega no vout no meu cv e coloca meu gitpages também" | LinkedIn do meu CV e o portfólio no GitHub Pages no README |

## B. Onde não segui a recomendação da IA

| Quando | Pergunta | A IA recomendava | Eu escolhi |
|---|---|---|---|
| S0 14:09 | Limiar de efeito prático: 5% ou 10%? | 5% | "2. o mais agressivo possível.": 10% |
| S1 15:07 | A sessão tinha voltado ao modo automático; a IA parou antes de editar | Voltar ao manual, se a mudança não tivesse sido de propósito (o plano pedia aprovação manual) | "Segue ai.": segui em modo automático |
| S1 16:44 | Como tratar a marca G4 no Radar público? | Visual do G4, sem logo | Visual e logo do G4, com rodapé de protótipo |
| S1 21:05 | Como fazer o baseline? | Rodar numa IA de outro fornecedor | Claude sem contexto |

## C. Onde aceitei a recomendação da IA

| Quando | Pergunta | Escolha |
|---|---|---|
| S0 13:52 | Dependências, fork e linha Co-Authored-By | Instalar; criar o fork; manter a linha |
| S0 14:09 | Declarar no log a leitura das reviews públicas? | "1. pode declarar" |
| S1 14:50 | A sessão está em modo automático e o plano pede aprovação manual | Troquei para manual: "está manual já, mas pode tirar os prints por favor." |
| S1 14:50 | Fork, dependências e e-mail dos commits | Criar o fork; lista enxuta; e-mail noreply do GitHub |
| S1 14:56 | Captura de tela bloqueada pelo macOS | Eu tiro os prints e a IA organiza |
| S1 15:33 | A camada de alocação também sai de sorteio: como fica a tese? | Duas camadas, reescritas: "Resultado: sem sinal. Operação: sem critério." |
| S1 15:33 | O +10% da simulação vira sinal em 51,5% das rodadas | Manter e explicar que 10% é a fronteira |
| S1 15:33 | Push a cada fase? | Sim |
| S1 15:58 | Que práticas entram no "parar de fazer"? | As quatro: sem fit, divulgação fraca, sem foco, parceria de um post só |
| S1 15:58 | Mapa de fit como premissa? | Fica como está |
| S1 16:19 | Custo implícito sem faixa de creator confiável | Custo médio por post, ajustável (US$ 1.500, de 500 a 5.000) |
| S1 16:32 | Ordem das hipóteses; donos das regras; efeito mínimo | H1, H2, H3 pela nota ICE; mapa de donos proposto; 20%, que cabe em 30 dias |
| S1 16:42 | De onde o Radar lê os dados | Resumos gerados por script |
| S1 17:01 e 17:04 | Telas e abordagem do Radar | As quatro telas; app de quatro páginas com o CSS do G4 |
| S1 17:05 a 17:14 | As quatro partes do desenho, o download do logo e a especificação | Aprovei cada parte, o download e a especificação |
| S1 20:43 | Formato dos checkboxes | Caixa que abre com checkboxes |
| S1 21:05 | Formato dos transcripts; CLAUDE.md nos transcripts | Markdown e JSONL; tirar o global e manter o do projeto |

## D. Erros da IA e quem pegou

| Erro | Quem pegou | O que foi feito |
|---|---|---|
| O plano dizia que 95% dos posts eram de creators com 50 mil seguidores ou mais | O laudo do dado (seguidores sorteados a cada post) | Tirei o achado ao decidir a tese |
| "10% ou mais" no lugar de "mais de 10%" | Um teste de fronteira | Corrigido |
| O plano dizia que +10% "deve ser encontrado" | A simulação (51,5%) | Decidi manter e explicar a fronteira |
| "Nenhum grupo difere em mais de cerca de 1%" só valia para grupos grandes | A própria IA, ao revisar o laudo | A frase saiu |
| Custo por faixa de creator sobre seguidores sorteados | A própria IA, na estratégia | Escolhi a premissa única |
| Controles e tabelas ilegíveis no modo escuro; números cortados | A própria IA, conferindo a tela | Corrigido |
| Filtro vazio com texto invisível e borda vermelha | Eu, na tela (print `05-radar_07_filtro_reprovado.png`) | Pedi caixa de seleção e depois checkboxes |
| Tabela escondendo coluna no celular, ícones sumindo no modo escuro, brief quebrando com dado de outro formato, semana padrão errada | A revisão independente | Corrigido, com teste ou medição na tela |
| Baseline rodado como subagente, herdando as instruções do projeto | A própria IA | Descartado e refeito em modo seguro |

## E. Fechamento (S1 21:44)

- Usar esta lista como o DECISOES.md, em vez de escrevê-lo eu mesmo.
- Manter o README como está, incluindo as seções escritas na minha voz.
- A IA tira os prints das telas do Radar e junta ao repositório.
- À sugestão de publicar o Radar online, respondi "pode subir uma PR minha no padrão informado no teste". O Radar fica rodando local, e o PR sai no padrão do desafio.
- Não fazer a revisão da análise por uma IA de outro fornecedor, prevista no plano como opcional.
- Tirar dos transcripts a lista de pastas do meu vault do Obsidian, que só mostrava outros projetos meus.
- Incluir um resumo das skills usadas em cada etapa, com o Obsidian e o motivo de usar os grafos ([`SKILLS.md`](SKILLS.md)).
