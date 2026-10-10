# Protótipo da rodada 3 (D41, aprovado na D44)

**Aprovado na D44**, com ajustes que vão direto para o app: o estado vazio usa ícone e texto em vez da imagem (os arquivos `vazio-*` ficam só como registro), e a paleta foi aprovada com o frio em cinza.

Um protótipo único, de alta fidelidade, com dados reais de 31/12/2017: Zane Levy e a equipe da Summer Sewald. Foi feito para o Bruno aprovar antes do código de produção. Não é código de produção.

A rodada 2 foi reprovada na D41: a usabilidade melhorou, mas o visual ainda parecia um painel genérico feito por IA. Esta rodada segue a direção do Bruno: o estilo do apple.com, um protagonista por tela, um termômetro como assinatura visual, ícones, imagens e movimento com propósito.

## Como abrir

As fontes e os dados não carregam por `file://`. Na pasta `process-log/prototipos`:

```sh
python3 -m http.server 8765
```

Depois abra `http://127.0.0.1:8765/rodada-3/index.html`. O endereço aceita:

| Opção | Efeito |
|---|---|
| `#entrada`, `#semana`, `#equipe`, `#como-funciona` | tela |
| `?tema=escuro` ou `?tema=claro` | força o modo (sem isso, segue o sistema) |
| `?fonte=onest` | mostra a fonte de quem não usa aparelho Apple |
| `?vendedor=Kary%20Hendrixson` | outra pessoa da equipe |
| `?abertura=1` | repete a animação de primeira abertura (para gravar) |

Prints e vídeos: `node rodada-3/capturar.mjs` e `node rodada-3/capturar.mjs video`, com o servidor no ar. O script usa o Playwright instalado em `solution/`.

## Telas

| Tela | Protagonista | O resto |
|---|---|---|
| Entrada | "Quem é você?" e a imagem do quente ao frio | lista de pessoas da equipe |
| Minha semana | o negócio nº 1: produto, empresa, potencial, score, prazo e o que fazer | nº 2 a 5 menores; "Ver todos os 31" recolhido; termômetro à direita (embaixo, no celular) |
| Painel do negócio | a conta (preço × chance = potencial) e a frase do motivo | score com a posição, régua, o que fazer |
| Minha equipe | "US$ 718 mil frios na equipe. Kary concentra US$ 229 mil." | vendedores com um termômetro mínimo cada; prévia à direita |
| Como funciona | a regra em uma frase e a chance por idade | o resto entra no incremento 5 |
| Estados vazios | o que fazer agora | aba Prospecção do Zane (0), Carl Lin (sem negócio) |

A saudação é uma linha pequena: "Bom dia, Zane. **Comece por estes 5.** 1 esfria e 1 fica frio nesta semana." Ela conta só os prazos de até 7 dias, sem soma de dinheiro. O dinheiro aparece no negócio em destaque.

## O que veio do apple.com

Os valores foram conferidos no CSS publicado do apple.com em 09/10/2026 (`globalheader.css`, `main.built.css`, `ac-localnav.built.css`), não de memória.

| No apple.com | Aqui |
|---|---|
| Texto `#1d1d1f`, `#6e6e73`, `#86868b`; fundo `#ffffff`; `#f5f5f7` em detalhes | igual. O `#86868b` tem 3,62:1 no branco, abaixo do AA para texto: fica só em marcas, ícones de seta e texto desabilitado. O texto de apoio usa `#6e6e73` (5,07:1) |
| Botão `#0071e3` (`#0077ed` ao passar o mouse, `#006edb` ao pressionar), link `#0066cc`, link no escuro `#2997ff` | igual, e o azul só aparece em ação e link |
| Barra global de 44 px (48 px no celular), translúcida, `saturate(180%) blur(20px)` | igual |
| Corpo de 17 px com `-0.022em`; subtítulo de 19 a 21 px; títulos de 28, 40 e 48 px, peso 600 | mesma escala, com o mesmo espaçamento entre letras |
| Botão em pílula (`border-radius: 980px`), 17 px | igual, com área de toque de 44 px |
| Curva `cubic-bezier(.25,.1,.3,1)` | usada em toda transição |
| Anel de foco azul translúcido | `outline: 4px solid rgba(0,125,250,.6)` |
| Escuro: fundo `#000`, superfícies `#1d1d1f`, texto `#f5f5f7` | igual, com tons próprios para as marcas (validados à parte), não uma inversão |

## O que veio de cada referência anterior

| Referência (rodada 2 e `docs/benchmark-ux.md`) | O que ficou | O que saiu |
|---|---|---|
| Variação B, "Mesa" | no computador: lista à esquerda, detalhe à direita, prévia na equipe | o detalhe sempre aberto ocupando a coluna: agora o termômetro fica lá e o painel desliza por cima quando você abre um negócio |
| Variação A, "Agenda" | no celular: uma coluna e a folha que sobe | a coluna estreita no computador (metade da tela vazia) |
| Direção de arte da rodada 2 | "uma pergunta por tela", "todo número tem contexto", a conta no painel, o vocabulário | fundo cinza, cartões com borda fina, verde como cor de ação, frio em azul, a barra da carteira no topo do vendedor |
| Stripe | poucos números grandes e alinhados, algarismos tabulares, cor só para status | o padrão "número grande com rótulo pequeno embaixo": o potencial do herói vem numa frase ("US$ 2.577 de potencial") |
| Linear | poucas variáveis geram os dois temas | — |
| Salesforce, Dynamics | score de 0 a 100 com o motivo ao lado; frase de coorte (Dynamics) | faixas Alta, Média e Baixa (contradizem a D28) |
| Pipedrive, Agendor | o negócio parado marcado no próprio cartão, pelos dias | a cor vermelha: frio é cinza com floco de neve |
| Attio | resumo no topo da ficha, ações logo abaixo do nome | — |

## Decisões desta rodada

**Paleta térmica.** Validada com o script da skill `dataviz` nos dois modos. A saída completa está em `paleta.txt`.

| | Claro (marca, texto) | Escuro (marca, texto) |
|---|---|---|
| Quente, chama | `#e35400`, `#b64400` (5,50:1) | `#b84300`, `#ff9a5c` (8,04:1) |
| Esfriando, termômetro | `#d9a400`, `#8a5a00` (5,93:1) | `#c78500`, `#f5c451` (10,34:1) |
| Frio, floco de neve | `#86868b`, `#6e6e73` (5,07:1) | `#86868b`, `#a1a1a6` (6,54:1) |

- Passam nos dois modos: luminosidade, separação para daltonismo (ΔE 11,4 no claro e 12,8 no escuro) e visão normal (17,8 e 15,5).
- "Falha" de propósito: o croma do frio. O cinza é a decisão do Bruno (no apple.com, azul quer dizer "clicável"), e o validador lê qualquer cinza como "sem cor". O frio nunca aparece sem o floco de neve e o texto.
- Aviso no claro: o âmbar tem 2,27:1 contra o branco. O validador exige rótulo visível, e o termômetro tem os rótulos das zonas, com ícone e texto, e a legenda com os valores.
- Até chegar aqui, 13 trios montados à mão foram reprovados, 4 no claro e 9 no escuro. Em 12 deles, laranja e âmbar se confundiam para daltônicos (ΔE de 0,5 a 6,0). Os trios aprovados saíram de uma busca automática com o próprio validador; o script ficou fora do repositório.

**Fonte.** `-apple-system, BlinkMacSystemFont, "Onest"`. Em aparelhos Apple, aparece a SF Pro do sistema, sem empacotá-la (a licença não permite). Nos demais, a Onest, empacotada (SIL OFL 1.1, licença em `../fontes/`). O print `vendedor-1280-claro-onest.png` mostra a Onest.

**Ícones.** Phosphor Icons 2.1.1, peso Light, licença MIT (`icones/LICENSE-phosphor.txt`). É a família aberta mais próxima dos SF Symbols: traço fino, pontas arredondadas, desenho geométrico. Foram usados 10 ícones, todos com função:

| Ícone | Uso |
|---|---|
| `fire` | quente |
| `thermometer-simple` | esfriando |
| `snowflake` | frio |
| `calendar-check` | Minha semana (barra de abas do celular) |
| `users-three` | Minha equipe (barra de abas do celular) |
| `info` | Como funciona (barra de abas do celular) |
| `caret-right` | linha que abre um detalhe |
| `caret-left` | voltar para a equipe |
| `caret-down` | "Ver todos" |
| `x` | fechar o painel |

Os SVGs ficam em `icones/`; o `icones.js` é gerado a partir deles.

**Score.** Anel monocromático (a cor do texto), em que a parte preenchida é o próprio score: 98 preenche 98% do anel. Ele não usa as cores de temperatura para não competir com elas.

**Termômetro.** Cada ponto é um negócio em andamento:
- posição = idade, de 0 a 138 dias em 70% da largura; os frios ficam numa zona comprimida até 440 dias;
- tamanho = potencial; os frios têm potencial 0 e ficam no tamanho mínimo;
- cor, ícone e rótulo da zona = temperatura;
- os 5 primeiros aparecem cheios e numerados, e os demais, atenuados;
- os pontos se arrumam num enxame determinístico, sem sorteio;
- passar o mouse mostra o negócio, e clicar abre o painel;
- na equipe, cada vendedor tem a versão mínima, sem rótulos.

## Movimento

Tudo usa só `transform` e `opacity`, respeita "reduzir movimento" (nesse caso não há animação nenhuma) e pode ser interrompido.

| Momento | O que acontece | Duração |
|---|---|---|
| Primeira abertura (uma vez por sessão) | o herói sobe 24 px e aparece; os nº 2 a 5 entram em cascata de 40 ms; os pontos saem do zero e deslizam até a idade; o potencial conta até o valor | até 600 ms no total |
| Troca de data | cartões e pontos saem de onde estavam (FLIP); de 30/09 para 31/12, os pontos andam para a direita; o seletor desliza | 280 ms |
| Abrir o painel | mola amortecida (cerca de 2% de passagem), da direita no computador e de baixo no celular | 280 ms |
| Passar o mouse num cartão | sobe 2 px e a sombra aparece | 220 ms |
| Pressionar | o cartão encolhe para 98,5% e o botão para 97% | 150 ms |
| Ações repetitivas (trocar de aba, abrir a lista) | sem animação | — |

## Imagens (Krea, modelo Google Nano Banana Pro)

Um estilo só: vidro fosco iluminado por dentro, fotografado em estúdio, sobre fundo liso. É a temperatura como luz: laranja quando quente, cinza quando frio. A primeira imagem serviu de referência para as outras. Cada uma tem versão clara e escura, porque uma foto de fundo branco vira um retângulo aceso no modo escuro.

Pós-processamento: ajuste de níveis, porque o fundo gerado era cinza (240) e não branco puro (no escuro, de 3 a 15 em vez de 0). Depois, `cwebp -q 86 -sharp_yuv`. As 6 imagens somam 60 KB.

| Arquivo | Onde | Texto alternativo |
|---|---|---|
| `imagens/entrada-{claro,escuro}.webp` (16:9) | tela de entrada | "Uma barra de vidro fosco iluminada por dentro, laranja numa ponta e cinza fria na outra." |
| `imagens/vazio-{claro,escuro}.webp` (1:1) | estados vazios | "Um bloco de vidro fosco cinza, parado, sobre um fundo liso." |
| `imagens/como-funciona-{claro,escuro}.webp` (21:9) | topo do "Como funciona" | "Sete placas de vidro fosco em fila, do laranja quente, à esquerda, ao cinza frio, à direita." |

Prompts, exatamente como enviados:

1. **Entrada, claro** (job `80c0a0a0-60c2-48d6-8400-9e60926d4849`, 16:9, 2K):
   > Minimal studio product photograph on a pure white seamless background. A single long, thin horizontal bar of frosted glass floats slightly above the surface, centered, occupying the middle third of the frame. Light passes through it: the left end glows with a soft warm orange, which gradually cools through amber into a neutral, pale cool grey at the right end. Matte, precise, calm. Soft diffused top light, a faint long shadow beneath the bar. Generous negative space. Photographic realism, high-end consumer electronics advertising aesthetic. No text, no people, no logos, no bubbles, no bokeh, no lens flare, no sparkles, no neon glow, no vignette.

2. **Vazio, claro** (job `46bc33cd-c0d6-41ac-ab76-771e8b862dd5`, 1:1, 1K, referência: imagem 1):
   > Same visual style, material and lighting as the reference image: minimal studio product photograph on a pure white seamless background. A single small, short block of frosted glass rests on the surface, centered, small in the frame. It is entirely neutral pale cool grey, with no warm light at all: quiet, still, empty. Soft diffused top light, a faint soft shadow beneath it. Very generous negative space. Photographic realism, high-end consumer electronics advertising aesthetic. No text, no people, no logos, no bubbles, no bokeh, no lens flare, no sparkles, no glow, no vignette.

3. **Como funciona, claro** (job `c912a0c3-6865-41f7-89f4-61cd1d6f1c66`, 21:9, 2K, referência: imagem 1):
   > Same visual style, material and lighting as the reference image: minimal studio product photograph on a pure white seamless background. A row of seven thin vertical frosted glass slabs standing upright on the surface, evenly spaced from left to right, like a measured scale. The leftmost slabs are lit from within by a soft warm orange, the middle ones by amber, and the rightmost ones are neutral pale cool grey. Calm, precise, matte. Soft diffused top light, faint soft shadows. Generous negative space above and below. Photographic realism, high-end consumer electronics advertising aesthetic. No text, no numbers, no people, no logos, no bubbles, no bokeh, no lens flare, no sparkles, no neon glow, no vignette.

4. **Entrada, escuro** (job `5c1a9c27-f0c6-4181-8ccd-9cf221ab9641`, 16:9, 2K, referência: imagem 1):
   > Recreate the reference image exactly, same composition, object, material and colors, but on a pure black seamless background instead of white: the frosted glass bar keeps its warm orange to amber to cool grey light, softly lit, with a very faint reflection beneath it. Dark studio, calm. No text, no people, no logos, no bubbles, no bokeh, no lens flare, no sparkles, no neon glow.

5. **Vazio, escuro** (job `cc50446a-1e4a-44c1-9e1a-695eb7d2d490`, 1:1, 1K, referência: imagem 2):
   > Recreate the reference image exactly, same composition, object, material and colors, but on a pure black seamless background instead of white: the small frosted glass block stays neutral pale cool grey, softly lit from above, quiet and still. Dark studio, calm, very generous negative space. No text, no people, no logos, no bubbles, no bokeh, no lens flare, no sparkles, no glow.

6. **Como funciona, escuro** (job `42ca5e4f-8d44-4df9-8ad0-81c89345e3ef`, 21:9, 2K, referência: imagem 3):
   > Recreate the reference image exactly, same composition, seven slabs, material and colors, but on a pure black seamless background instead of white: the frosted glass slabs keep their warm orange to amber to cool grey light from left to right, softly lit, faint reflections beneath. Dark studio, calm. No text, no numbers, no people, no logos, no bubbles, no bokeh, no lens flare, no sparkles, no neon glow.

Nenhuma geração foi descartada: as 6 saíram na primeira tentativa. Avaliação do orquestrador: a da entrada e a do "Como funciona" fogem da estética típica de IA (sem brilho, sem bolha, sem pessoa). A do estado vazio é a mais fraca: um bloco cinza correto, mas pouco expressivo. Cabe ao Bruno dizer se alguma parece genérica.

## Prints e vídeos

- `prints/` (WebP): telas em 1280 e 390 px, nos modos claro e escuro. Inclui vendedor, painel aberto, gestor e, no celular, a tela rolada. Só no claro: entrada, "Como funciona", estado vazio, lista completa e o print com a Onest.
- `videos/movimentos-1280.webm` e `videos/movimentos-390.webm`: primeira abertura; troca de 31/12 para 30/09 e de volta (os pontos andam); passar o mouse; abrir e fechar o painel. No computador, também a troca entre negócios com o painel aberto e a prévia da equipe.

## Limites do protótipo

- Só a equipe da Summer Sewald. No app, a entrada lista as 35 pessoas, agrupadas por regional.
- A folha do celular fecha pelo botão, pelo fundo ou pela tecla Esc; arrastar para baixo fica para o código de produção.
- Na troca de data, quando o negócio nº 1 muda, o herói novo aparece por opacidade enquanto os cartões se movem; por 280 ms, os dois movimentos se sobrepõem.
- A linha do vendedor na equipe é um botão que contém o termômetro mínimo (um `div`). O navegador aceita, mas no código de produção ele vira um elemento de frase.
- Textos e contas vêm de `../proto.js` e `../dados.js` (rodada 2, gerados pelo núcleo com `node scripts/prototipos.ts`). A tabela do "Como funciona" usa os valores do AGENTS §7 em 31/12/2017, arredondados.
