# OS-09 — Decisor de Campanha: correções, como usar, planejar campanha e design

Ferramenta regerada em `solution/tool/decisor.html` (2,91 MB) a partir de
`solution/tool/src/template.html` + `engine.js` + `ui.js` via
`solution/tool/build_tool.py`. O `decisor.html` não foi editado à mão.

Scripts de checagem:

- `solution/tool/validar_os09.mjs` — roda o `engine.js` no Node e compara com o pandas.
- `solution/analysis/os09_navegador.py` — abre o `decisor.html` no Chrome (Playwright).
  Modos: `briefing6000`, `template`, `simulador`, `ideias`, `capturas`, `acessibilidade`.

---

## Validação 1 — itens 0.5.1 a 0.5.3

Saída de `node solution/tool/validar_os09.mjs`: **todas as checagens passaram**.

### 0.5.1 — lift e erro padrão contra o pandas (base do desafio, 52.214 posts)

Referência em `a_referencia_lift_ep.csv`.

| item | maior diferença | tolerância | ok |
|---|---|---|---|
| lift (segmentos simples) | 3,75e-14 | 1e-6 | sim |
| erro padrão (segmentos simples) | 9,30e-15 | 1e-6 | sim |

### 0.5.2 — base com efeito conhecido (6.000 posts, `fixtures/base_efeito_conhecido.csv`)

Carregada no navegador: 6.000 posts, 0 descartados, k = 93. Referência em
`b_referencia_efeito_conhecido.csv`.

| formato | n | lift do engine | lift esperado | veredito | esperado | dif vs Python |
|---|---|---|---|---|---|---|
| video | 3.659 | +19,63% | +19,6% | funciona | funciona | 4,44e-15 |
| image | 1.122 | −14,73% | −14,7% | nao_funciona | nao_funciona | 5,55e-16 |
| text | 610 | −13,35% | −13,3% | nao_funciona | nao_funciona | 3,44e-15 |
| mixed | 609 | −13,30% | −13,3% | nao_funciona | nao_funciona | 1,33e-15 |

Briefing lido na tela com essa base:

> **Plataforma, formato, categoria, faixa de creator** — Priorize: Vídeo (+19,6%);
> Vídeo + Creators 500K–1M seguidores (+11,1%); Vídeo + Beleza (+10,1%).
> Evite: Imagem (−14,7%); Texto (−13,3%); Misto (−13,3%).

Contém "Priorize: Vídeo" e "Evite: Imagem", com Texto e Misto na lista do "Evite".

### 0.5.3 — vereditos da base do desafio não mudaram

| item | esperado | obtido | ok | detalhe |
|---|---|---|---|---|
| patrocínio | Barrado | Barrado | sim | efeito 0,999874; IC equiv. [0,99951; 1,00024] |
| nenhum positivo | 0 | 0 | sim | 220 sem efeito comprovado |
| nenhum negativo | 0 | 0 | sim | 0 inconclusivos |
| público | nenhum comprovado | nenhum comprovado | sim | 109 segmentos de público |

Teste A/B: dp do índice 0,024461 → 1 post por versão calculado, **30 usados** (piso da OS).

---

## Validação 2 — template de ponta a ponta

`os09_navegador.py template`.

1. Botão "Baixar template" na aba Como usar gerou `template_decisor.csv` com
   cabeçalho + 3 linhas de exemplo (1 orgânica, 2 patrocinadas):

   | plataforma | formato | patrocinado | custo |
   |---|---|---|---|
   | Instagram | video | não | 0 |
   | TikTok | video | sim | 3500 |
   | YouTube | mixed | sim | 2800 |

2. As 17 colunas saem na ordem da OS e o cabeçalho é idêntico ao do arquivo preenchido:

   `post_date, platform, content_type, content_category, follower_count, is_sponsored,
   views, likes, shares, comments_count, audience_age_distribution,
   audience_gender_distribution, audience_location, hashtags, clicks, conversions, cost`

3. `fixtures/template_preenchido.csv` (2.000 primeiras linhas da base + `clicks`,
   `conversions` e `cost` fictícios com seed 42) carregado na ferramenta:
   **2.000 posts · 29/05/2023 a 25/06/2023**. Tudo roda, inclusive as métricas novas.

Bloco "Vale patrocinar?" com o arquivo preenchido:

| métrica | veredito | n |
|---|---|---|
| Engajamento | Inconclusivo | 62 |
| Alcance | Inconclusivo | 62 |
| **Conversão** | Inconclusivo | 62 |

Tabela de custos (mediana, sem veredito), 865 posts patrocinados, R$ 2.393.945 pagos:

| Indicador | Mediana · faixa (p10–p90) | Posts |
|---|---|---|
| Custo por interação | R$ 1,39 · R$ 0,48–2,26 | 865 |
| Custo por conversão | R$ 946,00 · R$ 294,13–2.407,90 | 817 |

Seção "Conversão por segmento" presente (0 acima, 0 abaixo).

Com a base do desafio (sem `conversions` nem `cost`), o bloco mostra a frase da OS:
"Adicione conversões e custo ao arquivo para avaliar patrocínios com objetivo de venda."

---

## Validação 3 — simulador conferido na mão

Cenário: 30 orgânicos + 10 patrocinados por mês, R$ 2.000 por post patrocinado,
base do desafio inteira. Esperado recalculado em pandas (`d_referencia_simulador.csv`).

| Indicador | Esperado (Python) | Exibido na ferramenta | ok |
|---|---|---|---|
| Alcance no mês | 404.011,33 · 403.977,01–404.045,65 | 404.011 · 403.977–404.046 | sim |
| Interações no mês | 80.412,34 · 80.396,93–80.427,74 | 80.412 · 80.397–80.428 | sim |
| Investimento no mês | 20.000,00 | R$ 20.000 | sim |
| Ganho do patrocínio (alcance) | 5,396 · −12,461–23,253 | 5 · −12 a 23 | sim |
| Ganho do patrocínio (interações) | −1,550 · −9,569–6,469 | −2 · −10 a 6 | sim |
| Custo por interação adicional | indefinido (ganho ≤ 0) | — | sim |

As diferenças são só de arredondamento para inteiro na tela.

Como os dois ganhos têm IC que inclui zero, aparece a frase da OS:
"R$ 20.000 em patrocínio não compram alcance nem engajamento adicional em relação ao
orgânico." Também aparece o aviso fixo de saturação.

O briefing ganhou a seção **Plano de volume** depois de simular, com os mesmos números,
e ela entra no "Copiar briefing" e no "Imprimir briefing".

---

## Validação 4 — três ideias testadas

`os09_navegador.py ideias`, base do desafio, margem 10%.

| ideia | veredito | n de posts parecidos |
|---|---|---|
| TikTok + vídeo + tech | Barrada como diferencial | 1.228 de 52.214 |
| qualquer + patrocinado | Barrada como diferencial | 22.314 de 52.214 |
| TikTok + imagem + tech + 500K–1M + 19-25 anos | Inconclusivo | 98 de 52.214 |

Frases exibidas:

- 1 e 2: "Rende igual ao resto. Escolha por custo ou marca, não por desempenho."
  Na ideia 2, por ser patrocinada e o patrocínio estar Barrado, entra também
  "O orgânico entrega o mesmo resultado."
- 3: "Teste antes. São necessários ~30 posts por versão (cerca de 32 semanas no seu
  volume atual)."

A terceira combinação foi escolhida por ter menos de 100 posts (98).

---

## Validação 5 — capturas e conferência contra a Parte 4

`os09_navegador.py capturas`. Sete capturas de página inteira em `solution/outputs/os09/`:

| arquivo | aba | largura |
|---|---|---|
| `captura_diagnostico_1280.png` | Diagnóstico | 1.280 |
| `captura_como-usar_1280.png` | Como usar | 1.280 |
| `captura_planejar_1280.png` | Planejar campanha | 1.280 |
| `captura_diagnostico_1440.png` | Diagnóstico | 1.440 |
| `captura_como-usar_1440.png` | Como usar | 1.440 |
| `captura_planejar_1440.png` | Planejar campanha | 1.440 |
| `captura_planejar_usada_1440.png` | Planejar depois de avaliar uma ideia e simular | 1.440 |

Medidas lidas do DOM nas capturas:

| item | Parte 4 pede | medido |
|---|---|---|
| largura máxima do conteúdo | 1.120 px | 1120 px |
| corpo | 15 / 1,55 | 15px / 23,25px |
| fonte | Public Sans | "Public Sans", system-ui, … |
| números | tabular-nums | tabular-nums |
| título do briefing | 32 / 700 | 32px / 700 |
| títulos de seção | 24 / 600 | 24px / 600 |
| borda das seções | 1px #DCDFE3 | 1px rgb(220,223,227) |
| sombra das seções | nenhuma | none |
| cantos arredondados | 6px só em botão/campo/selo | botão 6px, seção 0px |
| altura dos campos | 40px | 40px |
| borda superior de destaque | 3px, só no briefing | 3px rgb(192,57,43) |

Nenhuma regra `@media` de celular sobrou: só restam `prefers-reduced-motion` e `print`.

### O que estava fora da Parte 4 e foi corrigido olhando as capturas

1. **Títulos de seção a 18px.** Estavam em `h3`. Viraram `h2` (24/600) em "Vale
   patrocinar?", "O que funciona / não funciona", "Público ideal", "Resultado",
   "Mês simulado", "Testar uma ideia" e "Simulador de alcance e gasto"; os títulos
   recolhíveis (`summary`) também foram para 24/600. Os subtítulos internos
   ("Quanto custou cada resultado", "Converte mais", "Conversão") ficaram em 18px.
2. **Selos esticados nas listas.** Tinham fundo colorido ocupando 160px fixos. Nas
   listas o fundo foi removido: ficou só a barra lateral de 4px, como a Parte 4 pede.
   O selo grande do briefing e do resultado da ideia manteve o fundo.
3. **Texto de apoio alinhado à direita** na lista de "Saúde da base". Passou a ser uma
   coluna de largura fixa alinhada à esquerda.
4. **Colunas desalinhadas** entre linhas: o selo "Sem efeito comprovado" estourava os
   160px e empurrava a linha 4px. A coluna do selo passou a 176px fixos.
5. **Marcador ▸ deslocando os títulos recolhíveis** 19px à direita dos demais. O
   marcador foi para a margem, alinhando todos os títulos na mesma coluna.
6. **tabular-nums só em tabelas.** Passou para o `body`, então os números no meio do
   texto também alinham.
7. **Mediana e faixa com casas decimais diferentes** na mesma célula de custo
   ("R$ 946 · R$ 294,13–2.407,90"). Agora as duas usam 2 casas.
8. **Negativos com hífen** (`-12`) em vez do sinal de menos usado no resto da
   ferramenta. O formatador de números passou a usar "−".

---

## Validação 6 — acessibilidade básica

`os09_navegador.py acessibilidade`.

| aba | paradas de Tab | elementos focáveis | sem contorno de foco | fora da tela |
|---|---|---|---|---|
| Diagnóstico | 13 | 13 | 0 | 0 |
| Como usar | 8 | 8 | 0 | 0 |
| Planejar campanha | 21 | 21 | 0 | 0 |

Todo elemento focável é alcançado pelo Tab nas três abas e todos mostram contorno de foco.

Selos: 13 de 13 têm texto, nenhum vazio. Rótulos usados: Alerta, Barrado, Funciona,
Inconclusivo, Não funciona, Ok. Nenhum veredito depende só de cor.

Contraste mínimo medido por aba (texto contra o fundo real, exigido 4,5:1):

| aba | pior razão |
|---|---|
| Diagnóstico | 5,00:1 |
| Como usar | 5,00:1 |
| Planejar campanha | 5,44:1 |

**Correção feita:** o amarelo do "Inconclusivo"/"Alerta" era `#B7791F` e dava **3,64:1**
sobre branco, abaixo do mínimo. Passou para `#8C5A0A` (5,86:1 sobre branco; 5,45:1 sobre
o fundo claro do selo).

---

## Pontos suspeitos ou problemas encontrados

1. **A base do desafio continua sem nenhum efeito real.** Nas 220 combinações testadas,
   zero deram "Funciona" ou "Não funciona"; os 109 segmentos de público também não.
   O patrocínio fica Barrado com efeito 0,999874. O dp do índice é 0,024461, o que faz o
   cálculo do A/B pedir 1 post por versão e cair no piso de 30. Isso é consistente com os
   4 alertas de saúde da base (alcance acompanha seguidores, likes acompanham alcance,
   variação pequena demais entre posts, quase nenhum fracasso). Reportado como suspeito;
   nada foi alterado por causa disso.

2. **O "ganho do patrocínio" fica em 5 e −2** no cenário da validação 3, com IC passando
   por zero nos dois casos. É resultado direto do efeito de patrocínio ≈ 1,0000 da base.
   O custo por interação adicional sai como "—" porque o ganho não é positivo.

3. **Fora do "só adicionar funções" nas Partes 1 a 3.** A Parte 1 exigiu mexer em
   `carregarLinhas`, `montarBase` e `montarIndices` do `engine.js` para que `clicks`,
   `conversions` e `cost` fossem lidos e indexados. Sem isso as colunas novas não chegam
   ao cálculo. As funções de cálculo em si foram só acrescentadas.

4. **Índice geral na avaliação de ideia.** Quando a ideia restringe apenas a plataforma,
   a comparação usa a média geral, não a média por plataforma — senão o próprio segmento
   entraria na sua referência e o lift daria sempre 1. É a mesma exceção que o engine já
   fazia para julgar plataforma na OS-08.

5. **Primeira faixa de creator.** O `engine.js` usa "até 50K" onde o CLAUDE.md descreve
   1–10K e 10–50K separadas. Isso vem da OS-08 e não foi tocado nesta OS.

6. **As capturas são de página inteira**, não do que cabe na dobra: as abas Diagnóstico e
   Como usar passam de 2.000 px de altura e precisam de rolagem a 1.280 e a 1.440 px.
