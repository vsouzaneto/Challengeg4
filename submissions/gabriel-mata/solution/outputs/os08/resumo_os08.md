# OS-08 — Ferramenta (núcleo)

## Arquivo entregue

| item | valor |
|------|-------|
| arquivo | `solution/tool/decisor.html` |
| tamanho | **2,87 MB** (2.867.242 bytes) |
| meta da OS | até 6 MB |
| dependência externa | PapaParse 5.4.1 (cdnjs), só no upload de CSV |
| base embutida | "base do desafio", 52.214 posts, de 29/05/2023 a 28/05/2025 |

Arquivos de origem: `solution/tool/src/template.html`, `solution/tool/src/engine.js`,
`solution/tool/src/ui.js`, `solution/tool/build_tool.py`, `solution/tool/validar_engine.mjs`.

O validador roda com `node validar_engine.mjs` dentro de `solution/tool/` e termina com
código 0. Saída completa reproduzida abaixo.

---

## 10a — Engine (JavaScript) contra as saídas do Python

Análise de referência: 52.214 posts, margem 10%, k = 111 em desempenho e k = 109 em público.

### 10a.1 — Lift e IC 95% por valor de variável (métrica `taxa`)

| variavel | segmento | n | lift engine | lift python | dif lift | dif IC95 |
|------------|------------|-------|-------------|-------------|----------|----------|
| plataforma | Bilibili | 10598 | 1.000153 | 1.000153 | 1.48e-7 | 5.95e-6 |
| plataforma | Instagram | 10423 | 0.999688 | 0.999688 | 3.79e-7 | 2.23e-5 |
| plataforma | RedNote | 10402 | 1.000216 | 1.000216 | 4.17e-7 | 4.43e-6 |
| plataforma | TikTok | 10296 | 1.000028 | 1.000028 | 2.92e-7 | 1.17e-5 |
| plataforma | YouTube | 10495 | 0.999913 | 0.999913 | 1.23e-7 | 1.73e-5 |
| formato | image | 10303 | 0.999923 | 0.999923 | 3.17e-7 | 3.79e-5 |
| formato | mixed | 5213 | 1.000428 | 1.000428 | 4.41e-7 | 3.34e-5 |
| formato | text | 5198 | 1.000485 | 1.000485 | 3.20e-7 | 4.11e-5 |
| formato | video | 31500 | 0.999874 | 0.999874 | 2.38e-7 | 8.09e-6 |
| categoria | beauty | 21023 | 1.000005 | 1.000005 | 1.10e-7 | 1.68e-5 |
| categoria | lifestyle | 20761 | 1.000123 | 1.000123 | 5.25e-8 | 1.65e-5 |
| categoria | tech | 10430 | 0.999745 | 0.999745 | 4.15e-7 | 3.24e-5 |
| faixa | até 50K | 2564 | 1.000106 | 1.000106 | 4.15e-7 | 3.06e-5 |
| faixa | 50–100K | 2597 | 1.000339 | 1.000339 | 1.69e-7 | 8.40e-6 |
| faixa | 100–500K | 21024 | 1.000046 | 1.000046 | 3.14e-7 | 1.34e-5 |
| faixa | 500K–1M | 26029 | 0.999918 | 0.999918 | 3.03e-7 | 2.87e-5 |
| idade | 13-18 | 7852 | 0.999684 | 0.999684 | 3.55e-7 | 1.63e-5 |
| idade | 19-25 | 18276 | 1.000236 | 1.000236 | 4.57e-7 | 2.71e-5 |
| idade | 26-35 | 15700 | 0.999920 | 0.999920 | 3.36e-7 | 3.43e-5 |
| idade | 36-50 | 7736 | 0.999815 | 0.999815 | 1.36e-8 | 2.12e-5 |
| idade | 50+ | 2650 | 1.000319 | 1.000319 | 3.12e-7 | 4.69e-5 |
| genero | female | 20743 | 0.999997 | 0.999997 | 2.66e-7 | 1.62e-5 |
| genero | male | 20987 | 1.000006 | 1.000006 | 3.87e-7 | 3.12e-5 |
| genero | non-binary | 5249 | 0.999977 | 0.999977 | 4.34e-8 | 1.69e-5 |
| genero | unknown | 5235 | 1.000010 | 1.000010 | 4.38e-7 | 3.62e-5 |
| pais | Brazil | 6505 | 1.000320 | 1.000320 | 4.12e-7 | 1.40e-5 |
| pais | China | 6648 | 1.000063 | 1.000063 | 4.08e-7 | 7.05e-5 |
| pais | Germany | 6497 | 0.999668 | 0.999668 | 1.58e-7 | 3.48e-5 |
| pais | India | 6484 | 0.999430 | 0.999430 | 6.64e-8 | 2.02e-5 |
| pais | Japan | 6553 | 0.999999 | 0.999999 | 5.94e-8 | 2.26e-5 |
| pais | Russia | 6459 | 0.999982 | 0.999982 | 2.02e-7 | 5.87e-5 |
| pais | UK | 6570 | 1.000495 | 1.000495 | 1.13e-7 | 2.62e-5 |
| pais | USA | 6498 | 1.000033 | 1.000033 | 2.70e-7 | 7.80e-6 |

Referências do Python: `solution/outputs/os02/nivel1.csv` e `solution/outputs/os02/plataforma.csv`.
33 segmentos conferidos.

### 10a.2 — Patrocínio (comparação estratificada)

| item | engine | python | dif | fonte |
|---------------------------|----------|----------|---------|--------------|
| efeito patrocínio — taxa | 0.999874 | 0.999877 | 3.17e-6 | os03 bloco1 |
| efeito patrocínio — views | 1.000053 | 1.000054 | 5.74e-7 | os06 item 1b |
| estratos existentes | 240 | 240 | 0.00e+0 | os03 bloco1 |
| estratos usados | 141 | 141 | 0.00e+0 | os03 bloco1 |
| posts usados | 49487 | 49487 | 0.00e+0 | os03 bloco1 |
| patrocinados usados | 21174 | 21174 | 0.00e+0 | os03 bloco1 |
| orgânicos usados | 28313 | 28313 | 0.00e+0 | os03 bloco1 |

### Resumo das tolerâncias

| item | dif | tolerância | ok |
|-----------------------------------|---------|------------|-----|
| Lift por valor de variável (taxa) | 4.57e-7 | 0.000001 | sim |
| Limites do IC 95% sem correção | 7.05e-5 | 0.001 | sim |
| Efeito do patrocínio em taxa | 3.17e-6 | 0.001 | sim |
| Efeito do patrocínio em views | 5.74e-7 | 0.001 | sim |
| Estratos existentes | 0.00e+0 | 0 | sim |
| Estratos usados | 0.00e+0 | 0 | sim |
| Posts usados | 0.00e+0 | 0 | sim |
| Patrocinados usados | 0.00e+0 | 0 | sim |
| Orgânicos usados | 0.00e+0 | 0 | sim |

**Todas as checagens passaram** (`validar_engine.mjs` saiu com código 0).

---

## 10b — Vereditos esperados nesta base

| item | esperado | obtido | ok | detalhe |
|-----------------|---------------------------|---------------------------|-----|---------|
| patrocínio | Barrado | Barrado | sim | efeito 0.999874, IC de equivalência [0,99951; 1,00024] dentro de [0,90; 1,10] |
| nenhum positivo | 0 | 0 | sim | 220 segmentos "Sem efeito comprovado" |
| nenhum negativo | 0 | 0 | sim | 0 inconclusivos |
| público | Nenhum público comprovado | Nenhum público comprovado | sim | 109 segmentos de público avaliados |
| saúde da base | com alertas | com alertas | sim | 4 alertas: alcance × seguidores, likes × alcance, posts virais, posts fracassados |

---

## 10c — Verificação visual

Capturas na pasta desta OS, feitas no Chrome 154 headless sobre o `decisor.html` servido
em `127.0.0.1`:

- `captura_1280px.png` — 1280 px de largura (desktop)
- `captura_375px.png` — 375 px de largura (celular)

Em 1280 px e em 375 px: topo fixo com nome da base, contagem de posts e período; barra de
abas; "Saúde da base (4 alertas)"; briefing; seções recolhidas "Sem efeito comprovado (220)"
e "Inconclusivo (0)"; "Como calculamos" recolhido. Sem transbordo horizontal nas duas
larguras. Os campos de data "De"/"Até" aparecem só quando o filtro de período está em
"Período personalizado".

## 10d — Filtro "Últimos 90 dias"

| recorte | posts | k | estratos | efeito patroc. | funciona / não funciona / sem efeito / inconclusivo |
|-----------------|-------|-----|----------|----------------|------|
| Toda a base | 52214 | 111 | 141 | 0.999874 | 0 / 0 / 220 / 0 |
| Últimos 90 dias | 6403 | 93 | 24 | 0.999796 | 0 / 0 / 173 / 0 |

Janela aplicada: 28/02/2025 a 28/05/2025 (contada a partir da data mais recente da base).

Conferido também na interface: o topo passa de "52.214 posts · 29/05/2023 a 28/05/2025"
para "6.403 posts · 28/02/2025 a 28/05/2025" e aparece o aviso "Recalculado para 6.403 posts".
No filtro de plataformas, desmarcar Bilibili leva a base a 41.616 posts com o rótulo
"4 selecionadas", e remarcar volta a 52.214.

---

## Pontos suspeitos ou problemas encontrados

1. **Os 4 testes de saúde da base disparam alerta.** Correlação log(seguidores) × log(views)
   = 0,005644; correlação likes × views = 0,000761; variância ÷ média de views = 0,990585;
   0,0% dos posts abaixo de 10% da mediana de views. Numa base real esperaria-se correlação
   positiva nos dois primeiros e cauda de fracassos no último. Reportado, não alterado.

2. **Todos os 220 segmentos caem em "Sem efeito comprovado", nenhum inconclusivo.** Não é
   erro de regra: o desvio-padrão do índice é ~0,0245, então ep ≈ 2,4e-4 e o IC de
   equivalência de um segmento típico fica em [0,99953; 1,00032] (exemplo: formato `image`,
   n = 10.303, lift 0,999923, dp 0,024560, ep 0,000242) — muito dentro de [0,90; 1,10]. Com
   essa variância, a margem de 10% é larguíssima para o tamanho da amostra.

3. **O dimensionamento de A/B do briefing dá "pelo menos 1 post por versão".** A fórmula da
   OS com dp = 0,024461 e margem de 20% resulta em n_necessário = 0,1173, arredondado para 1
   (piso da própria ferramenta). É o que a fórmula entrega nesta base de variância quase nula.
   Reportado, não alterado.

4. **A faixa "acima de 1M" fica vazia.** Nenhum post da base tem mais de 1M de seguidores,
   então o rótulo existe mas não gera segmento. O maior `follower_count` cai em 500K–1M.

5. **Fórmula de patrocínio diferente da usada na OS-03.** A OS-08 pede média ponderada das
   **diferenças de índice** (`efeito = 1 + Σ w·d`); a OS-03 usou média ponderada das **razões
   de valores brutos**. Implementei o que a OS-08 escreve. As duas concordam em 3,17e-6 (taxa)
   e 5,74e-7 (views), bem dentro da tolerância de 0,001 — daí as diferenças não nulas na
   tabela 10a.2, que não são erro de cálculo.

6. **Ambiguidade do "(n ≥ 100)" na tabela de blocos, resolvida pela convenção do projeto.**
   Valores isolados de cada variável entram sem mínimo; só os pares exigem n ≥ 100 — é o que
   `solution/analysis/os02_benchmark.py` faz (nível 1 com min_n = 0, nível 2 com min_n = 100).
   A regra 1 do veredito (n < 100 → "poucos posts") continua valendo como a OS escreve.

7. **A coluna `hashtags` é aceita no upload mas não é embutida.** Ela é opcional na seção 2 e
   nenhum bloco de análise da OS-08 a usa, então não entra no JSON do `decisor.html`. CSVs que
   a tragam não dão erro.

8. **Três checagens de texto na interface falharam e eram artefato do teste, não da tela.**
   As buscas por "Sem efeito comprovado (N)", "k = … em desempenho" e "… de … estratos
   entraram" não achavam nada via `innerText`, porque (a) `innerText` ignora o conteúdo de
   `<details>` fechado, onde ficam o k e os estratos, e (b) as contagens são dois `<span>`
   vizinhos, sem espaço antes do parêntese. Relendo por `textContent` com os `<details>`
   abertos, os três textos estão lá: "Sem efeito comprovado(220)", "k = 111 em desempenho e
   k = 109 em público", "141 de 240 estratos entraram". Nenhuma correção foi feita no produto.

9. **Fora do escopo desta OS (previsto):** as abas "Como usar" e "Planejar campanha" existem
   na barra, mas o conteúdo delas é da OS-09.
