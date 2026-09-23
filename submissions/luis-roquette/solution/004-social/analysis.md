# Estratégia Social Media — Challenge 004

## Quatro respostas obrigatórias do challenge

### O que gera engajamento?

**NÃO EXISTE VENCEDOR SUSTENTADO; NÃO REDISTRIBUIR O MIX**

- KPI: Limiar material: 0,162 p.p.
- Comparação: 20 contextos avaliados; nenhum passou simultaneamente amostra, materialidade, estabilidade e força.
- Amostra: Base: 52.214 posts.
- Ação: Manter o mix e coletar/testar contextos comparáveis antes de priorizar.
- Melhor força disponível: C=0,996.
- Cobertura: 20 contextos com ao menos um mês comparável.
- Estabilidade: insuficiente para declarar vencedor.
- Muda se: A decisão mudaria quando: Reavaliar quando houver três meses elegíveis, efeito material, estabilidade &gt;=2/3 e força &gt;=0,40.
- Evidência: `driver-overview-0b979d404f9eb642`

### Vale patrocinar influenciadores?

**NÃO ESCALAR PATROCÍNIO AGORA**

- KPI: Cobertura comparável: 1,56%.
- Comparação: Melhor contexto comparável: YouTube / vídeo / beauty / 500.000+ (+0,097 p.p.); pior contexto comparável: Bilibili / vídeo / estilo de vida / 500.000+ (-0,136 p.p.).
- Amostra: 12 estratos elegíveis; 5.216 insuficientes; ROI observado indisponível.
- Ação: Coletar custo/conversão e testar apenas o estrato selecionado antes de ampliar investimento.
- Força do melhor contexto: C=0,280.
- Cobertura: 1,56% dos posts.
- Estabilidade: 100,0% em 4 meses.
- Muda se: A decisão mudaria somente com três meses estáveis, força suficiente e cenário financeiro abaixo do ponto de equilíbrio.
- Evidência: `sponsorship-context-39fb80b0199432e9`

### Qual deve ser a estratégia?

**EXECUTAR PROGRAMA DE 30 DIAS PARA VALIDAR YOUTUBE / VÍDEO / ESTILO DE VIDA / 100.000–499.999; PRESERVAR O MIX FORA DO TESTE**

- KPI: 4 semanas: baseline → teste → replicação/revisão → decisão humana.
- Comparação: Contexto escolhido pelo ranking multivariado; escala automática: não; gate final: não atingido.
- Amostra: Base: 52.214 posts; 4 janelas operacionais.
- Ação: Executar D1–D30 com Gestor de Social Media responsável e registrar a decisão na semana 4.
- Força herdada do driver: C=0,950.
- Cobertura: 3 meses elegíveis no contexto selecionado.
- Estabilidade herdada: 100,0%.
- Muda se: A decisão mudaria na semana 4 conforme força, materialidade, concordância temporal e guards de volume.
- Evidência: `strategy-1c37897aa175be7d`

### Qual perfil de audiência mais engaja?

**NÃO HÁ PERFIL GLOBAL COMPROVADO; DADOS INSUFICIENTES PARA ELEGER UMA AUDIÊNCIA**

- KPI: Cobertura controlada máxima por dimensão: 0,00%.
- Comparação: Idade, gênero e localização não formaram pares elegíveis dentro do mesmo contexto comparável.
- Amostra: 0/26.247 estratos elegíveis; maior célula com 23 taxas definidas.
- Ação: Coletar pares de audiência comparáveis; não inventar persona nem redistribuir verba por rótulo marginal.
- Força: não mensurável.
- Cobertura controlada máxima por dimensão: 0,00%.
- Estabilidade: não mensurável.
- Muda se: A decisão mudaria quando dois rótulos no mesmo contexto tiverem ao menos 30 taxas e cinco creators por braço.
- Evidência: `audience-overview-17f51703b8f049dc`

## Estratégia de conteúdo — 30 dias

| Semana | Janela | Responsável | Ação | Métrica | Cadência | Gate |
|---:|---|---|---|---|---|---|
| 1 | D1–D7 | Gestor de Social Media | Congelar o contexto e registrar o baseline orgânico comparável | ERv mediano, visualizações e interações por post | manter o mix corrente fora do teste | 30 taxas definidas e cinco creators em alvo e comparador |
| 2 | D8–D14 | Gestor de Social Media | Testar o melhor candidato elegível sem alterar o mix fora do experimento | Delta de ERv contra pares da mesma plataforma e faixa | coletar cadência comparável sem inventar quantidade | Efeito acima da materialidade e guards não negativos |
| 3 | D15–D21 | Gestor de Social Media | Replicar uma vez se o sinal persistir; revisar se divergir | Concordância entre duas janelas e concentração por creator | coletar sem número inventado | Duas janelas concordantes e força sem queda |
| 4 | D22–D30 | Gestor de Social Media | Manter, revisar ou coletar; não escalar | Confiança, materialidade, visualizações e interações | manter até decisão humana registrada | C&gt;=0,70, efeito material, duas janelas concordantes e guards não negativos |

Preservar o mix fora dos testes; nenhuma publicação ou verba é executada automaticamente.

## Decisão para segunda-feira

Fila única: o top 3 abaixo vem de `result[recommendations]`, na mesma ordem do HTML e do início do CSV; o CSV preserva a fila completa `result[all_recommendations]`, incluindo as demais ações decidíveis na UI. São propostas para decisão humana; não executam gasto, publicação ou interrupção.

1. YouTube / video / lifestyle / 500,000+ / 2025-04: Testar o padrão em escala limitada e coletar evidência antes de ampliar esforço ou investimento. Prioridade 0.424558; impacto 1; força 0.3; atualidade 0.0141519; ΔERv +0.0270584 p.p.; data representativa 2025-04-15T19:41:00. Responsável: Gestor de Social Media; execução: próximos 7 dias; revisão: 7 dias após o teste; métrica: ERv, views e interações por post. Evidência: sponsorship-fec1a70afd70ad88. Frequência: Testar 1 posts por creator por semana ISO completa; status test; unidade posts_per_creator_per_complete_iso_week; mês 2025-04; regra complete_iso_weeks_within_calendar_month_and_scope; método median_observed_posts_per_creator_week; 18 creator-semanas, 18 creators; 3 semanas completas disponíveis, 3 semanas observadas; janela 2025-04-07T00:00:00 a 2025-04-27T00:00:00; ação test_observed_cadence; mínimo de 2 semanas completas observadas. Limite: frequência observada é hipótese de teste, não efeito causal; ausência de linha não equivale a zero.
2. RedNote / video / beauty / 500,000+ / 2025-03: Testar o padrão em escala limitada e coletar evidência antes de ampliar esforço ou investimento. Prioridade 0.0190582; impacto 1; força 0.29; atualidade 0.000657178; ΔERv -0.0628742 p.p.; data representativa 2025-03-15T02:43:30. Responsável: Gestor de Social Media; execução: próximos 7 dias; revisão: 7 dias após o teste; métrica: ERv, views e interações por post. Evidência: sponsorship-0d364864017b2146. Frequência: Testar 1 posts por creator por semana ISO completa; status test; unidade posts_per_creator_per_complete_iso_week; mês 2025-03; regra complete_iso_weeks_within_calendar_month_and_scope; método median_observed_posts_per_creator_week; 27 creator-semanas, 27 creators; 4 semanas completas disponíveis, 4 semanas observadas; janela 2025-03-03T00:00:00 a 2025-03-30T00:00:00; ação test_observed_cadence; mínimo de 2 semanas completas observadas. Limite: frequência observada é hipótese de teste, não efeito causal; ausência de linha não equivale a zero.
3. YouTube / video / beauty / 500,000+ / 2024-12: Testar o padrão em escala limitada e coletar evidência antes de ampliar esforço ou investimento. Prioridade 2.93375e-06; impacto 1; força 0.3; atualidade 9.77916e-08; ΔERv +0.111229 p.p.; data representativa 2024-12-16T02:14:00. Responsável: Gestor de Social Media; execução: próximos 7 dias; revisão: 7 dias após o teste; métrica: ERv, views e interações por post. Evidência: sponsorship-aae70c7cbea56355. Frequência: Testar 1 posts por creator por semana ISO completa; status test; unidade posts_per_creator_per_complete_iso_week; mês 2024-12; regra complete_iso_weeks_within_calendar_month_and_scope; método median_observed_posts_per_creator_week; 28 creator-semanas, 28 creators; 4 semanas completas disponíveis, 4 semanas observadas; janela 2024-12-02T00:00:00 a 2024-12-29T00:00:00; ação test_observed_cadence; mínimo de 2 semanas completas observadas. Limite: frequência observada é hipótese de teste, não efeito causal; ausência de linha não equivale a zero.

Atualidade = 2^(−idade em dias/7), ancorada na data de referência do dataset. Em grupos agregados, a data representativa é a mediana das datas do grupo-alvo (posts patrocinados na comparação de patrocínio). Um escopo de dois anos pode produzir scores muito pequenos: isso preserva a regra de recência e não demonstra uma oportunidade atual. A ordem é prioridade decrescente, |ΔERv| decrescente, data representativa decrescente e evidence_id crescente, após deduplicação contextual.

Força limitada (<0,40) exige coleta/teste, sem ampliação de investimento. As janelas de execução/revisão são propostas futuras, não datas de performance observada.

## O que os dados permitem afirmar

Método 2.5.0. Escopo efetivo: 2023-05-29T00:00:00 a 2025-05-28T00:00:00; referência 2025-05-28T11:08:00; filtros {}. 52214 posts-alvo de 52214 linhas na fonte.

Cobertura parcial: patrocínio 1.56% dos posts, 12 estratos elegíveis, 5216 insuficientes. Benchmarks: 0 níveis tentados; 0 alvos sem referência elegível; alertas post a post desativados. 0 avisos de qualidade; detalhes e motivos completos no CSV.


### Decisões recentes desta fonte

- Nenhuma decisão registrada nesta fonte.

52214 posts; 5000 creators; 527376193 views; 104966242 interações. Mediana ERv: 19.8992%; ERv ponderado: 19.9035%. Proporção de posts com zero interação: 0; taxas indefinidas: 0. Evidência: `summary-4db863a89a4913eb`.

ERv = 100 × (likes + shares + comments_count) / views; views=0 deixa a taxa indefinida e preserva volume. A mediana usa taxas por post; a taxa ponderada usa totais apenas onde views>0. Views não são alcance único; interações não são pessoas únicas.

## Plataforma, conteúdo, categoria, creators, audiência e tempo

As tabelas descrevem cada recorte; não criam uma segunda fila de prioridades. Diferenças pequenas de taxa, sem comparação controlada, não justificam redistribuir o mix. Idade, gênero e localização são rótulos de posts, não percentuais ou personas. Estas marginais não identificam vencedores: a análise condicionada e sua cobertura aparecem abaixo. Bilibili e RedNote permanecem no escopo junto a Instagram, TikTok e YouTube.

### Plataforma

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| Bilibili | 10598 | 4540 | 107039049 | 21307767 | 19.9046 | `dimension-db4866916a8180c3` |
| Instagram | 10423 | 4510 | 105275939 | 20946950 | 19.889 | `dimension-8f2a64052001aba6` |
| RedNote | 10402 | 4514 | 105068336 | 20916853 | 19.901 | `dimension-42f4e8494a2da229` |
| TikTok | 10296 | 4494 | 103995686 | 20699400 | 19.9019 | `dimension-be489b32aa8ce1d3` |
| YouTube | 10495 | 4540 | 105997183 | 21095272 | 19.9001 | `dimension-37e5690238949930` |

### Formato

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| image | 10303 | 4475 | 104071566 | 20712300 | 19.9007 | `dimension-03f5c13251606d48` |
| mixed | 5213 | 3327 | 52652595 | 10484160 | 19.9038 | `dimension-89abb2efebdf2dea` |
| text | 5198 | 3329 | 52490501 | 10452520 | 19.9122 | `dimension-7b73352995cd7c96` |
| video | 31500 | 4999 | 318161531 | 63317262 | 19.8955 | `dimension-9ce37ec4da9be6c2` |

### Categoria

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| beauty | 21023 | 4977 | 212331201 | 42261477 | 19.8996 | `dimension-c398f3594f1f6a85` |
| lifestyle | 20761 | 4969 | 209686263 | 41740052 | 19.9013 | `dimension-8a6230fbcf4ef4e1` |
| tech | 10430 | 4523 | 105358729 | 20964713 | 19.8954 | `dimension-897abf32c37be492` |

### Faixa de seguidores

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| 0–9,999 | 454 | 436 | 4581119 | 911451 | 19.8765 | `dimension-ac03ed3755f1a080` |
| 10,000–49,999 | 2110 | 1758 | 21313743 | 4243070 | 19.9009 | `dimension-a0e65a1830049f48` |
| 100,000–499,999 | 21025 | 4982 | 212345820 | 42266183 | 19.904 | `dimension-4f83fa145bf9ff9f` |
| 50,000–99,999 | 2596 | 2091 | 26215136 | 5219513 | 19.91 | `dimension-4b7f149265feebb9` |
| 500,000+ | 26029 | 4994 | 262920375 | 52326025 | 19.8936 | `dimension-a2bd874b5316cb15` |

### Idade

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| 13-18 | 7852 | 4056 | 79321127 | 15782684 | 19.8956 | `dimension-035e59912cdebec2` |
| 19-25 | 18276 | 4947 | 184595589 | 36749614 | 19.9009 | `dimension-3423edec0a56a8e1` |
| 26-35 | 15700 | 4866 | 158563615 | 31557172 | 19.9001 | `dimension-9118a25c440ee066` |
| 36-50 | 7736 | 4072 | 78130652 | 15547930 | 19.8989 | `dimension-f2033ceb07e99b6d` |
| 50+ | 2650 | 2073 | 26765210 | 5328842 | 19.8989 | `dimension-b8bc31000a807e0c` |

### Gênero

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| female | 20743 | 4979 | 209503458 | 41698343 | 19.8944 | `dimension-088bdb09f810fb3a` |
| male | 20987 | 4977 | 211972319 | 42190194 | 19.9003 | `dimension-1d8c183647937d20` |
| non-binary | 5249 | 3353 | 53019133 | 10552457 | 19.9067 | `dimension-7651828e318d5b39` |
| unknown | 5235 | 3364 | 52881283 | 10525248 | 19.905 | `dimension-e7cbbe567efc1d9d` |

### Localização

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| Brazil | 6505 | 3724 | 65693721 | 13079528 | 19.9015 | `dimension-663b3fa135a48698` |
| China | 6648 | 3818 | 67156444 | 13367265 | 19.9036 | `dimension-9856da985acb8523` |
| Germany | 6497 | 3734 | 65632058 | 13058763 | 19.8976 | `dimension-844f90e2bbf03c05` |
| India | 6484 | 3780 | 65500057 | 13029391 | 19.8872 | `dimension-1cb1bf882628c63b` |
| Japan | 6553 | 3738 | 66182343 | 13172600 | 19.8964 | `dimension-c715c6b76f92a0b7` |
| Russia | 6459 | 3757 | 65229927 | 12982754 | 19.8982 | `dimension-3985361d4c3c1fee` |
| UK | 6570 | 3796 | 66354996 | 13213549 | 19.9048 | `dimension-68d07956a70a0f0e` |
| USA | 6498 | 3726 | 65626647 | 13062392 | 19.9035 | `dimension-3b8878af12cbf165` |

### Mês

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| 2023-05 | 188 | 187 | 1898818 | 377813 | 19.8931 | `dimension-9784f7880df90ed0` |
| 2023-06 | 2241 | 1811 | 22636496 | 4505008 | 19.8951 | `dimension-c82ed39e51c36df3` |
| 2023-07 | 2221 | 1831 | 22425828 | 4465405 | 19.9107 | `dimension-795114821b789be9` |
| 2023-08 | 2233 | 1837 | 22555419 | 4486031 | 19.8795 | `dimension-57e7ea68f08ba410` |
| 2023-09 | 2092 | 1741 | 21132335 | 4207344 | 19.913 | `dimension-510b20a2f063421b` |
| 2023-10 | 2186 | 1812 | 22078142 | 4393121 | 19.8941 | `dimension-c486540e8e22c784` |
| 2023-11 | 2168 | 1808 | 21897271 | 4359592 | 19.9102 | `dimension-c9e6fecdb23b3a05` |
| 2023-12 | 2177 | 1801 | 21982940 | 4377864 | 19.9073 | `dimension-0664282680ce2efe` |
| 2024-01 | 2192 | 1804 | 22140371 | 4408052 | 19.9032 | `dimension-327328a4bfe7e744` |
| 2024-02 | 2099 | 1737 | 21199664 | 4218973 | 19.8981 | `dimension-04af0689830e92cf` |
| 2024-03 | 2210 | 1792 | 22322168 | 4442533 | 19.8918 | `dimension-4c2303949336da1b` |
| 2024-04 | 2121 | 1761 | 21425517 | 4261036 | 19.8774 | `dimension-4e80928b5a36dee9` |
| 2024-05 | 2195 | 1820 | 22167277 | 4413864 | 19.9028 | `dimension-be3790a695df18e6` |
| 2024-06 | 2165 | 1786 | 21866512 | 4352679 | 19.906 | `dimension-18259a61dd43db1d` |
| 2024-07 | 2229 | 1820 | 22519508 | 4481034 | 19.8965 | `dimension-4d706ff563abb375` |
| 2024-08 | 2347 | 1916 | 23702162 | 4719291 | 19.911 | `dimension-122d594402060077` |
| 2024-09 | 2139 | 1741 | 21607668 | 4299942 | 19.8955 | `dimension-bc3cab4f24a328d0` |
| 2024-10 | 2212 | 1833 | 22348182 | 4444786 | 19.8886 | `dimension-1743a27ddf78f594` |
| 2024-11 | 2151 | 1790 | 21724203 | 4325675 | 19.8963 | `dimension-7db26bf8c60739d4` |
| 2024-12 | 2228 | 1862 | 22500047 | 4480727 | 19.9155 | `dimension-a75d44164ffcc6c4` |
| 2025-01 | 2146 | 1773 | 21672074 | 4314145 | 19.8876 | `dimension-ddade3ff24d7e106` |
| 2025-02 | 1914 | 1601 | 19332056 | 3848371 | 19.8969 | `dimension-af246c6950483572` |
| 2025-03 | 2213 | 1813 | 22351748 | 4444840 | 19.8846 | `dimension-376860cf6bf09e67` |
| 2025-04 | 2173 | 1807 | 21954870 | 4369314 | 19.901 | `dimension-d73a2b5a9d3cd9fc` |
| 2025-05 | 1974 | 1626 | 19934917 | 3968802 | 19.9019 | `dimension-663ae15cd137b500` |

## Audiência condicionada: elegibilidade, efeito e cobertura

Para cada rótulo de idade, gênero ou localização, comparamos pares dentro da mesma plataforma, formato, categoria, faixa de seguidores, mês-calendário e estado de patrocínio. Cada rótulo precisa de 30 taxas definidas e cinco creators. O efeito é mediana ERv do alvo menos mediana do comparador; taxa é acompanhada de volume e amostra. As demais dimensões de audiência não são controladas: associação descritiva, não efeito causal, persona ou vencedor geral. Sem dois rótulos elegíveis, a resposta é insuficiência quantificada, não uma preferência por público.

| Dimensão | Estratos elegíveis/total | Células elegíveis/total | Maior amostra de taxas por célula | Posts cobertos/total | Cobertura | Evidência |
|---|---:|---:|---:|---:|---:|---|
| audience_age_distribution | 0/8749 | 0/21644 | 19 | 0/52214 | 0% | `audience-overview-17f51703b8f049dc` |
| audience_gender_distribution | 0/8749 | 0/19024 | 23 | 0/52214 | 0% | `audience-overview-0d385d7502344cd8` |
| audience_location | 0/8749 | 0/28638 | 12 | 0/52214 | 0% | `audience-overview-45ba97ad6e7d7c2c` |

## Patrocínio e o que não funciona

12 estratos elegíveis; 5216 sem amostra/contraparte suficiente; cobertura de 1.55897% dos posts. Evidência: `sponsorship-overview-4750d8952c3f931c`.

Controle: mesma plataforma, formato, categoria, faixa de creator e mês-calendário. Cada mês exige contrapartes contemporâneas; orgânicos de um mês não são comparados a patrocinados de outro. Cada braço exige 30 taxas definidas e cinco creators; o efeito é a diferença entre medianas das medianas de ERv por creator. Cobertura baixa restringe as conclusões aos meses/contextos elegíveis; não sustenta uma política geral de patrocínio. Patrocínio é associação observacional, não causalidade. Custo implícito e retorno financeiro não podem ser calculados: faltam investimento, custo de produção, receita/conversão. Nenhum threshold de seguidores justifica desembolso sozinho.

Menor associação de ERv: Bilibili / video / lifestyle / 500,000+ / 2023-09; ΔERv -0.136225 p.p.; força 0.36; orgânicos/patrocinados: 37/38 posts, 372753/383650 views, 74407/76011 interações. Evidência: `sponsorship-9332c8416ba393aa`.

Maior associação de ERv: YouTube / video / lifestyle / 500,000+ / 2024-04; ΔERv +0.160707 p.p.; força 0.29; orgânicos/patrocinados: 34/30 posts, 343605/302197 views, 68090/60132 interações. Evidência: `sponsorship-129b2710dcf6e1e0`.

Esses extremos são achados descritivos, não prioridades adicionais nem ordens para suspender renovação. Sinal negativo isolado ou força insuficiente exige investigação; interromper investimento requer sinais concordantes, evidência forte e decisão humana. Ausência de zeros observados, quando indicada acima, limita a avaliação do fracasso: não prova inexistência de posts sem engajamento.

## Estratégia operacional e quick wins

Responsável sugerido: Gestor de Social Media. Executar nos próximos 7 dias; revisar 7 dias após cada teste. A estratégia abaixo aplica a fila inicial, sem reordená-la.

| Tema | Ação | Critério de revisão |
|---|---|---|
| Esforço e quick win | Preparar briefs dos contextos da fila na ordem exibida; anexar a evidência e registrar aceitar/rejeitar/editar. | Rever ERv, views e interações por post no mesmo contexto. |
| Público e creators | Preservar rótulos de audiência e faixa de creator do contexto; coletar se faltarem controles. Não inferir uma persona ou threshold de contratação. | Pelo menos 30 taxas e cinco creators por braço; declarar composição e concentração. |
| Frequência | Testar a mediana observada de posts/creator/semana completa indicada em cada prioridade; estado collect pede coleta antes de propor cadência. | Comparar janelas equivalentes; hipótese observacional, não frequência ótima ou efeito causal. Ausência de linha não equivale a zero. |
| Patrocínio | Obter custos reais antes de avaliar desembolso; força limitada pede coleta/teste. | ERv e volume concordantes, grupo comparável e dados financeiros. |
| Parar/revisar | Revisar repetição de padrões negativos; não parar por média global ou sinal isolado. | Interrupção exige a guarda do motor e decisão humana; sem base, coletar. |

## Auditabilidade e limites

Fonte SHA-256: `693a2df6e609d1c099f3430d9a5b894b224fe12b2420c0d93e6defe90d15f18e`; método `2.5.0`. Cada evidência está em [evidence.csv](./evidence.csv), com escopo, fórmula e referências.

Regeração conjunta: `python3 analysis.py /caminho/social_media_dataset.csv --evidence evidence.csv --summary summary.html --report analysis.md`.

Linhas `recommendation` preservam `rank`, score, impacto, força, atualidade, valores originais V/I/F, denominadores P95, diferença, data representativa, ação, responsável e janelas. Impacto = média de min(V/P95_V,1), min(I/P95_I,1), min(F/P95_F,1); prioridade = 100 × impacto × força × atualidade. Scores são relativos à plataforma/tipo/unidade, não monetários. P95=0 usa máximo positivo ou zero se inexistente.

A coluna JSON `frequency_hypothesis` preserva status, valor/unidade, método, amostra de creator-semanas/creators, mês (`period_month`), regra (`coverage_rule`), semanas completas disponíveis/observadas, janela, ação, mínimo de semanas para coleta e limitação. No patrocínio mensal, entram apenas semanas ISO completas inteiramente dentro do mês e do escopo; semanas que atravessam a fronteira mensal ficam fora. Sem mês fixo, vale a cobertura completa do escopo. O valor é uma hipótese de teste no mesmo contexto da recomendação, não promessa de desempenho.

Em `source_ref`, agrupar por `evidence_id` e `reference_role` (target/comparator) e ordenar por `reference_chunk` (base 1). `source_row_id`, `source_line` e `reference_index` são arrays JSON paralelos, em blocos de até 500 entradas e 32.768 caracteres no campo de IDs, legíveis pelo limite padrão do csv.reader. O índice identifica o registro dentro da evidência (base 0); concatenar fragmentos de ID com o mesmo `reference_index`, conservando a linha física inicial (base 1). IDs acima de 4.096 caracteres são fragmentados sem perder conteúdo. Reconstituir a chave completa com `source_hash + ':' + ID`. Campos multilinha contam todas as linhas físicas; células de texto neutralizam fórmulas de planilha.

Linhas `evidence_detail` projetam estatísticas do alvo/comparador, incluindo quartis, amostra, fallback e controles removidos de benchmarks; no editorial, target=current e comparator=previous. `statistics` preserva os números completos. `quality`, `warning`, `benchmark_diagnostic` e `sponsorship_uncovered` conservam diagnósticos sem reunir milhares de contextos numa célula. Campos analíticos acima de 32.768 caracteres ficam vazios na linha-base e são reconstruídos por `analysis_field`: agrupar evidence_id/reference_role/field_name, ordenar field_chunk e concatenar json.loads(field_value); field_name tem formato record_type.campo para evitar colisões entre evidência e recomendação. O mesmo princípio vale para `history_field` no histórico, usando decision_id/outcome_id. A barreira final também limita campos/metadados de qualquer linha. Se necessário, emite `export_field`: evidence_id=export-row-N aponta para a N-ésima linha-base (base 1, excluindo export_field); agrupar por essa chave/field_name e concatenar json.loads(field_value) na ordem field_chunk. Reconstruir essa camada primeiro, depois analysis_field/history_field; campos normais não mudam. A neutralização de fórmulas é preservada no texto recomposto.

A CLI publica todo o histórico, sem alertas post a post. Ausência de período anterior igualmente longo pode impedir comparações editoriais; não se inventa tendência. O monitoramento recente pode produzir outra fila porque tem outro escopo. Não há unidade confirmada de content_length, causalidade, ROI ou resultados futuros inferidos.
