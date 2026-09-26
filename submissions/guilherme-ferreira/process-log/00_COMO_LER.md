# Como ler este process log

Uma página para quem não é da área técnica: o que foi feito, em que ordem e como conferir.

## O que foi feito, em ordem

1. **Pesquisa (sessão 0, cerca de 1 hora).** Pedi à IA para ler o desafio, os PRs dos outros candidatos e as reviews públicas do avaliador, e li a síntese dela. Pedi um plano ao Claude, pedi a outro modelo que achasse as falhas dele e mandei refazer.
2. **Execução (sessão 1, cerca de 8 horas no relógio, das quais 1h40 parada por erro de conexão).** Sete fases: ambiente, laudo do dado, análise, estratégia, Radar e fechamento, mais o baseline, que ficou para o fechamento. A IA fez o trabalho braçal e parou em cada decisão que o plano marcava como minha.

## Onde está cada coisa

| Arquivo | O que tem |
|---|---|
| [`DIARIO.md`](DIARIO.md) | Uma entrada por fase: o que eu queria saber, o que pedi, o que a IA respondeu, como conferi e o que decidi |
| [`DECISOES.md`](DECISOES.md) | As decisões humanas, com as minhas palavras citadas; montado pela IA a partir dos transcripts, que aprovei usar no lugar de um texto meu |
| [`SKILLS.md`](SKILLS.md) | As skills usadas em cada etapa, o vault do Obsidian e por que uso grafos |
| [`evidencias/baseline/`](evidencias/baseline/) | O enunciado cru num Claude sem contexto, e onde a resposta dele erra |
| [`evidencias/screenshots/`](evidencias/screenshots/) | Prints das minhas respostas nas perguntas de decisão, das telas do Radar e do filtro que reprovei |
| [`evidencias/transcripts/`](evidencias/transcripts/) | As conversas inteiras com o Claude Code |

## Declarações

- **Pesquisa antes de começar.** Pedi à IA para ler o repositório, as reviews públicas do avaliador e as submissões anteriores, li a síntese dela e usei isso para definir o critério de qualidade. A sessão de pesquisa está nos transcripts.
- **Modo de aprovação.** A pesquisa rodou em modo automático: leitura, planejamento, o download e o perfil do CSV e a criação da branch e das pastas da entrega. Na execução, a criação do fork e do ambiente teve aprovação manual; depois, decidi seguir em modo automático, com a IA parando nas decisões. O avaliador já apontou o modo automático como ponto negativo em outra submissão. Preferi declarar.
- **Screenshots.** A captura de tela do macOS não funcionou para o Claude Code, porque ele não tem permissão para gravar a tela. Os prints das minhas respostas e do filtro que reprovei são meus, colados no chat e salvos pela IA. Os prints das telas do Radar foram tirados pela IA, a meu pedido, com o Chrome sem janela controlado por um script. Os transcripts mostram o resto.
- **Transcripts.** Cada sessão está em dois formatos: um Markdown legível, com pedidos, respostas e uma linha por ferramenta usada, e o registro completo em JSONL compactado. Um script removeu o meu e-mail, os caminhos da minha pasta pessoal, o meu arquivo de configuração pessoal do Claude (CLAUDE.md global), o ID da organização, a cópia do prompt de sistema do Claude Code, as imagens, os emojis que o próprio Claude Code grava, a lista de pastas do meu vault do Obsidian e os nomes dos meus outros projetos. O arquivo de instruções do projeto (CLAUDE.md do projeto) ficou, porque mostra as regras que dei à IA. Ele não faz parte da entrega.
- **Baseline.** Feito com o mesmo fornecedor de IA (Claude), em modo seguro, sem nenhum contexto meu: só o enunciado e o CSV. A primeira tentativa foi descartada, porque herdou as instruções do projeto.
- **Decisões.** O plano previa que eu escrevesse o `DECISOES.md`. No fechamento, decidi usar a lista montada pela IA a partir dos transcripts, sem reescrevê-la ("pode manter"). As minhas falas aparecem citadas literalmente.
- **O que ficou de fora.** A revisão da análise por uma IA de outro fornecedor, prevista no plano como opcional, não foi feita. O Radar não foi publicado online; roda local com um comando (README).

## Como conferir

- Todo número do README aponta para o que o gera: uma seção do notebook, o script da simulação ou os transcripts.
- Os testes automáticos rodam com `python -m pytest` (instruções no README).
- Os commits seguem a ordem em que o trabalho foi feito, um por etapa. O baseline (Fase 1) entrou no fechamento.

## Glossário

1. **Engajamento:** (likes + shares + comentários) / views.
2. **Célula:** uma combinação de plataforma, categoria e formato, como "TikTok, beauty, vídeo".
3. **Diferença:** quanto um grupo de posts rende acima ou abaixo de todos os outros.
4. **Intervalo de 95%:** a faixa onde a diferença real provavelmente está.
5. **Limiar de 10%:** a menor diferença que justifica mudar a estratégia. Foi definido antes de comparar os grupos.
6. **Correção para muitas comparações (Benjamini-Hochberg):** com centenas de comparações, algumas parecem importantes por acaso. A correção tira esses falsos achados.
7. **Sinal e ruído:** sinal é a diferença acima de 10%, confiável depois da correção e com pelo menos 30 posts. O resto é ruído.
8. **Simulação:** efeitos de tamanho conhecido plantados numa cópia do dado, para provar que o método os acharia.
9. **Efeito mínimo detectável:** o menor efeito que um teste consegue enxergar com o número de posts disponível.
10. **Baseline:** a resposta de uma IA que recebe só o enunciado, sem nenhum trabalho meu, para comparar com a entrega.
