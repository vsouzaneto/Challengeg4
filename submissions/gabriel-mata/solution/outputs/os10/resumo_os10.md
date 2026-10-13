# OS-10 — Ferramenta didática (decisor.html)

Reescrita de tudo que aparece na tela e tema claro/escuro. O motor (`engine.js`) não foi
tocado: as mudanças ficaram em `src/template.html` e `src/ui.js`, e o arquivo final foi
regerado com `build_tool.py`.

- Arquivo gerado: `solution/tool/decisor.html` — 2,93 MB (meta: até 6 MB).
- Scripts usados: `solution/tool/build_tool.py` e `solution/analysis/os10_navegador.py`.
- Saídas desta OS: `validacao_motor.txt`, `validacoes_navegador.txt`, `texto_tela.txt`
  e as 4 capturas de tela.

## Validação 1 — motor intacto

`node solution/tool/validar_engine.mjs` e `node solution/tool/validar_os09.mjs`
(log completo em `validacao_motor.txt`).

| verificação | resultado |
|---|---|
| patrocínio na base do desafio | Barrado, efeito 0,999874, IC equiv. [0,99951; 1,00024] |
| segmentos positivos / negativos | 0 / 0 (220 sem efeito, 0 inconclusivos) |
| público | nenhum comprovado (109 segmentos) |
| recorte "últimos 90 dias" | 6.403 posts, k = 93, 24 estratos, efeito 0,999796 |
| base com efeito conhecido | vídeo +19,63% funciona; imagem −14,73%, texto −13,35%, misto −13,30% não funciona |
| teste A/B | dp 0,024461 → 30 posts por versão |
| `validar_os09.mjs` | todas as checagens passaram |
| `validar_engine.mjs` | 1 checagem fora do esperado (a mesma da OS-09) |

Os números são exatamente os da OS-09. A única checagem vermelha é a mesma de antes:
"Lift por valor de variável (taxa)", dif 1,91e-4 contra tolerância 1e-6, no script da
OS-08, cuja referência é anterior à redefinição de lift feita na OS-09. Nada mudou nela.

## Validação 2 — varredura de linguagem

Script percorre a barra superior, Diagnóstico e Planejar campanha com "Como calculamos"
fechado, os outros recolhíveis abertos, uma ideia avaliada e um mês calculado. O texto
conferido está salvo em `texto_tela.txt`.

| tela | caracteres | palavras proibidas | frases com mais de 25 palavras |
|---|---|---|---|
| barra superior | 275 | 0 | 0 |
| Diagnóstico | 4.008 | 0 | 0 |
| Planejar campanha | 1.933 | 0 | 0 |

Lista conferida: IC, intervalo de confiança, Bonferroni, segmento, recorte, estrato,
índice, lift, variância, desvio, margem relevante, teste A/B, base, combinações, k, n.

## Validação 3 — base com efeito conhecido

Arquivo `os09/fixtures/base_efeito_conhecido.csv` (6.000 posts, likes de vídeo × 1,3)
carregado pelo botão "Carregar meus dados".

- Barra superior: `Dados: base_efeito_conhecido.csv · 6.000 posts · 29/05/2023 a 19/08/2023`
- Frase principal: "Neste histórico, Vídeo, Vídeo com influenciadores de 500 mil a 1 milhão
  de seguidores, Vídeo sobre beleza trouxeram mais resultado."
- Linha "Onde e como postar": **Priorize: Vídeo**, Vídeo com influenciadores de 500 mil a
  1 milhão de seguidores, Vídeo sobre beleza. **Evite: Imagem, Texto, Misto.**

As duas frases exigidas pela OS aparecem: `Priorize: Vídeo` e `Evite: Imagem, Texto, Misto`.

## Validação 4 — Planejar campanha

| checagem | resultado |
|---|---|
| botão com tudo em "Qualquer" | travado, com a dica "Escolha pelo menos uma opção." |
| exemplo "Vídeo no TikTok" | preenche rede = TikTok e formato = video, destrava o botão |
| exemplo "Post pago no Instagram" | preenche rede = Instagram e pagar = sim |
| exemplo "Imagem sobre tecnologia" | preenche formato = image e tema = tech |
| "Mais opções" | abre 4 campos e vira "Menos opções"; clicando de novo, fecha |

Mês com 30 posts orgânicos + 10 pagos a R$ 2.000:

| | Seu plano | Se todos fossem sem pagar | conta à mão |
|---|---|---|---|
| Posts no mês | 40 | 40 | 40 |
| Visualizações | 404 mil | 404 mil | 404.011,33 e 404.005,94 |
| Interações | 80 mil | 80 mil | 80.412,34 e 80.413,89 |
| Investimento | R$ 20.000 | R$ 0 | 10 × 2.000 = 20.000 |

A conta à mão vem de `os09/d_referencia_simulador.csv` (pandas): total do mês = 40 × média
por post; "se todos fossem sem pagar" = total menos o ganho do patrocínio em 10 posts.
Os valores batem depois do arredondamento da tela.

## Validação 5 — tema

Capturas a 1.440 px, com todos os recolhíveis abertos e a aba Planejar já usada:

| arquivo | tamanho | tema | pior contraste de texto |
|---|---|---|---|
| `captura_diagnostico_claro_1440.png` | 1440×3143 | claro | 5,32:1 |
| `captura_planejar_claro_1440.png` | 1440×1473 | claro | 5,44:1 |
| `captura_diagnostico_escuro_1440.png` | 1440×3143 | escuro | 5,70:1 |
| `captura_planejar_escuro_1440.png` | 1440×1473 | escuro | 4,60:1 |

Nenhum texto abaixo de 4,5:1 nos dois temas. As quatro imagens foram abertas e conferidas
uma a uma. A escolha sobrevive ao recarregar: `localStorage["decisor-tema"] = "escuro"` e,
depois do reload, `data-tema=escuro`, rádio "Escuro" marcado e fundo `rgb(18, 20, 23)`.

Na primeira rodada, o botão principal no tema escuro ficou em 3,6:1 (texto branco sobre
`#E5584A`). Corrigido com o token `--destaque-texto`, que fica branco no claro e escuro no
escuro; o botão passou a 4,6:1. Era a única cor fixa que sobrava no CSS.

## Validação 6 — ajuda "?"

Quatro botões no Diagnóstico e dois em Planejar ao abrir (quatro depois de avaliar a ideia
e calcular o mês).

| ação | resultado |
|---|---|
| clique | abre o balão e marca `aria-expanded=true` |
| Esc | fecha |
| foco + Enter | abre (foco fica no próprio botão) |
| clique fora | fecha |

Frases conferidas na tela, uma por termo:

- Interações: "Tudo que as pessoas fazem no post: curtir, comentar e compartilhar."
- Sem pagar (orgânico): "Post que você publica sem pagar ninguém para divulgar."
- Pago (patrocinado): "Post em que você paga um influenciador para publicar."
- Pessoas alcançadas (visualizações): "Quantas vezes o post foi visto."

## Conferência extra — barras de patrocínio

As barras da seção "Vale a pena pagar influenciador?" mostram média por post, número que o
motor não devolve. O `ui.js` repete a separação em grupos comparáveis do motor e tira a
média crua. Conferido contra a mesma conta em pandas:

| | tela | pandas |
|---|---|---|
| posts usados | 49.487 | 49.487 (141 grupos) |
| interações sem pagar | cerca de 2.010 por post | 2.010,4 |
| interações pago | cerca de 2.010 por post | 2.010,3 |
| visualizações sem pagar | cerca de 10 mil por post | 10.100,3 |
| visualizações pago | cerca de 10 mil por post | 10.100,8 |

## Pontos suspeitos ou problemas encontrados

1. `validar_engine.mjs` continua com 1 checagem fora do esperado ("Lift por valor de
   variável (taxa)", dif 1,91e-4). É herança da OS-08 e não foi tocada nesta OS, que é de
   texto, interface e tema.
2. A cor `#B7791F` da tabela de tokens da OS dá 3,64:1 sobre fundo branco e reprovaria no
   mínimo de 4,5:1 pedido na parte 5. O tema claro manteve `#8C5A0A` para "Ainda não dá
   para saber". Conflito entre duas exigências da própria OS; escolhi o contraste.
3. As barras usam média crua por post e a frase ao lado usa o efeito calculado pelo motor,
   que trabalha com valores normalizados. Nesta base a diferença é invisível (ambas dizem
   "praticamente igual"), mas em outra base a barra e a frase podem não parecer idênticas.
4. O nome embutido pelo `build_tool.py` é "base do desafio" e a palavra "base" é proibida
   na tela. Como o `build_tool.py` não entra no escopo desta OS, o `ui.js` troca esse nome
   por "exemplo do desafio" na hora de exibir. Se o nome embutido mudar, a troca não pega.
5. Estados que a OS não descreve e que precisei preencher: frase principal quando nada se
   destaca e o patrocínio também não compensa; "Pagar influenciador?" quando o resultado é
   inconclusivo; as respostas "Sim." dos quatro testes de confiança; a linha de "Ainda não
   dá para saber" quando o motor não informa quantos posts faltam (uso 100 menos o que
   existe); "Para quem falar?" quando o arquivo não tem colunas de público.
6. A seção "Não faz diferença" e a "Ainda não dá para saber" listam apenas as escolhas de
   rede, formato, tema e tamanho de influenciador. As de público aparecem só em "Para quem
   falar?", que mostra o que funcionou melhor e pior — sem efeito e inconclusivo de público
   não são listados em lugar nenhum.
7. Na base com efeito conhecido, a frase principal lista três vencedores muito parecidos
   entre si ("Vídeo", "Vídeo com influenciadores de 500 mil a 1 milhão", "Vídeo sobre
   beleza"), o que deixa a frase repetitiva. É o formato pedido pela OS (até três nomes).
8. A base do desafio continua com o comportamento estranho já apontado na OS-03: os cinco
   testes de confiança dão quase tudo "Não", e a tela mostra o selo "Atenção" com o texto
   pedido pela OS. Nenhum número foi alterado.
