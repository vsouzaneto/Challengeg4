# Revisão de RevOps — o que a ferramenta pode prometer e o que o time faz com ela na segunda-feira

**Autor:** revops-engineer (agente) · **Revisão humana pendente:** Bernardo Couto · **Data:** 2026-09-23
**Insumos lidos:** brief (`../../challenges/build-003-lead-scorer/README.md`), `docs/scoring-logic.md`, `docs/specs/scoring-spec.md`, `docs/figures/10_backtest.md`, `docs/figures/11_diagnostics.md`, `docs/design/ux-spec.md`, `docs/data-quality-report.md`, `process-log/decisions.md` (entradas de 2026-09-23 13:45 e seguintes).
**Números novos neste documento** foram produzidos por consultas de leitura com pandas sobre `solution/data/raw/` (comandos reproduzíveis na seção 7). Tudo o mais cita o arquivo e a seção de origem.

---

## 0. Resumo executivo para a Head de RevOps (cinco frases)

1. A ferramenta **não prevê quem vai fechar** — testamos agente, produto, setor, conta, idade, carga e um modelo estatístico em dois cortes no passado e nenhum acertou mais que escolher ao acaso (`docs/scoring-logic.md`, "Backtest"; AUC-ROC 0,44–0,53) — e é exatamente por isso que ela é útil: ela ordena os deals por **valor esperado × momento do ciclo** e tira do caminho o que já está morto, em vez de vender uma probabilidade que os dados do CRM não sustentam.
2. O achado que mais vale dinheiro não é o score: **1.291 dos 1.589 deals em Engaging (81%) passaram de 138 dias, o ciclo mais longo já fechado na história da empresa**, e carregam **R$ 3,19 milhões nominais** — 4,6× o valor dos 298 deals vivos (R$ 0,69 mi) — e zero desses 679 deals que já estavam nessa situação nos cortes de backtest fechou depois (`docs/scoring-logic.md`, "A fila de zumbis, em dinheiro"; `docs/figures/11_diagnostics.md`, "Fila de zumbis").
3. Na prática, o vendedor mediano abre a ferramenta e encontra **12 deals vivos para trabalhar e 44 parados para confirmar ou encerrar** (verificado nesta revisão, seção 7); seis dos 27 vendedores com pipeline **não têm nenhum deal vivo** — a primeira quinzena de uso é um sprint de limpeza de CRM, não de venda, e o forecast oficial deve sair só dos deals vivos.
4. Focar no top 20% por score captura **1,8× a receita** do aleatório (37,7% e 35,9% vs 20,4% e 20,6%), abaixo de "ordenar por preço" (50,5% / 45,9%) — diferença que é o preço de a ferramenta dizer **quando** agir em vez de entregar uma lista de GTK 500 (`docs/figures/10_backtest.md`, coluna "receita top 20%").
5. Recomendo aprovar a versão 1 com o posicionamento "valor × momento + higiene do pipeline", **não** aprovar o reason code de fim de trimestre com números (os traços do padrão parecem artefato do dataset, seção 3b), e rodar um piloto de 8 semanas com grupo de controle medindo receita fechada em deals vivos, zumbis resolvidos e conta preenchida (seção 2.3) — porque a única prova que importa é a que virá do uso, não do backtest.

---

## 1. Validação dos textos dos reason codes

Fontes validadas: tabela de `docs/design/ux-spec.md` §9 ("Templates dos reason codes") e tabela de `docs/scoring-logic.md` ("Reason codes"). Ainda não existe `text_pt` gerado no pipeline (`solution/pipeline/analysis/rules.py` emite só `code, direction, weight, n, value`), então esta é a redação a implementar.

Critério único: o texto muda a decisão do vendedor **sem prometer previsão que o backtest refutou**. Regra de bolso: onde a direção é `i` (informativo, peso zero — `docs/specs/scoring-spec.md` §3.1), o texto **não pode** soar como "isso faz o deal fechar mais". Placeholders `{}` preservados.

**Achado transversal (bloqueante):** `ux-spec.md` §9 dá direção `+ / −` para `AGENT_TRACK_RECORD`, `AGENT_PRODUCT_FIT`, `SECTOR_FIT`, `ACCOUNT_SIZE`, `ACCOUNT_HISTORY` e `AGENT_OVERLOAD`, e sugere ações do tipo "Mantenha o ritmo" / "Peça apoio do manager". A spec de scoring (`scoring-spec.md` §0 e §3.1) e o backtest (`10_backtest.md`, "Variantes") dizem que todos são informativos, peso zero. O drawer da ux-spec (§4.1) ainda mostra "▲ +9 pts Você fecha 74% dos GTX Pro" e "▲ +3 pts Setor tecnologia" — isso é **exatamente** a promessa que refutamos. A tabela abaixo corrige a direção; o application-engineer deve renderizar esses códigos com ℹ e sem cor de sinal (a própria ux-spec §4.2 já prevê isso para `i`).

| Código | Dir. correta | Template atual (fonte) | Veredito | Texto final proposto (voz do vendedor) |
|---|---|---|---|---|
| `PRODUCT_BASE_RATE` | i | "{product} fecha em {rate}% dos casos (média geral: {global}%)." (ux-spec §9) | **Manter**, com o `n` | "{product} fecha em {rate}% dos casos ({n} deals no histórico; média geral {global}%)." — versão de `scoring-logic.md` já traz o `n`; adotar essa. |
| `AGENT_TRACK_RECORD` | i | "Você fecha {rate}% dos seus deals ({n} fechados; média do time: {team}%)." + ação "Mantenha o ritmo" / "Peça apoio do manager" (ux-spec §9) | **Reescrever** — ux-spec dá direção +/− e ação que trata como sinal; superestima previsão | "Você fecha {rate}% dos seus deals ({n} fechados; time: {team}%). Isso não muda a ordem da sua fila — no passado não previu o fechamento." Sem ação sugerida. |
| `AGENT_PRODUCT_FIT` | i | "Você fecha {rate}% dos {product} (média do time: {team}%)." + "Use seu roteiro" / "Envolva quem fecha mais" (ux-spec §9) | **Reescrever** — mesma razão; e o texto deve avisar amostra pequena quando `n < 30` (`scoring-spec.md` §3.1) | "Você fecha {rate}% dos {product} ({n} deals{, amostra pequena})." Quando `n < 30`, acrescentar literalmente ", amostra pequena". Sem ação. |
| `SECTOR_FIT` | i | "Setor {sector}: fecha {rate}% (média {global}%)." (ux-spec §9) | **Manter texto, trocar direção para i** | "Setor {sector}: {rate}% de fechamento ({n} deals; média {global}%)." Só aparece com conta (`scoring-spec.md` §3.1). |
| `ACCOUNT_SIZE` | i | "Conta com {employees} funcionários e receita de {revenue}: porte acima/abaixo da média dos fechamentos." (ux-spec §9) | **Reescrever** — "porte acima da média dos fechamentos" insinua que porte fecha mais; refutado (H-conta, `scoring-logic.md` linha 1 do resumo) | "Conta com {employees} funcionários e receita de US$ {revenue}. Serve para preparar a conversa; o porte não previu fechamento no histórico." |
| `ACCOUNT_HISTORY` | i | "{won} ganhos e {lost} perdidos nesta conta; último em {date}." + "Retome o contato que já conhece" / "Entenda por que perdeu antes." (ux-spec §9) | **Manter texto, trocar direção para i, manter as duas ações** — a ação aqui é preparação de conversa, não previsão; é o único informativo cuja ação recomendo manter | "{won} ganhos e {lost} perdidos nesta conta; último em {date}." Ação: "Retome o contato que já conhece." / "Veja no CRM por que perdeu antes." |
| `ACCOUNT_UNKNOWN` | i | "Conta não informada no CRM: estimativa menos confiável ({pct}% dos deals abertos estão assim)." + "Registre a conta no CRM antes do próximo contato." (ux-spec §9) | **Reescrever de leve** — "{pct}% dos deals abertos estão assim" (68%) normaliza o problema em vez de resolver; e "estimativa menos confiável" é verdade só de contexto, não de acerto (`scoring-logic.md`, Limitações 3) | "Sem conta no CRM: não sabemos setor, porte nem histórico. Registre a conta antes do próximo contato — leva 1 minuto e libera confiança alta." Manter `{pct}` só na visão do manager (é problema do time, não do deal). |
| `SURVIVAL_POSITIVE` | i (ux-spec diz +) | "{days} dias em Engaging: deals que passam de {threshold} dias fecham em {rate}%." + "Proponha data de fechamento esta semana." (ux-spec §9) | **Reescrever** — direção errada e o texto lê como "quanto mais velho, melhor", que em corte temporal não se sustenta (`crm-dataset`, "Estágios e desfecho": AUC-ROC 0,50). O que é útil é a **contagem regressiva** para 138 | "{days} dias em Engaging. Deals que chegaram aqui fecharam em {rate}% dos casos — mas nenhum deal fechou depois de {max} dias: faltam {remaining}." Ação: "Proponha data de fechamento esta semana." Quando `days ≤ 120`, omitir a frase da contagem. |
| `ZOMBIE_RISK` | − | Dois textos na ux-spec §9: "{days} dias em Engaging: acima de {pct}% dos deals que fecharam ({threshold}). Risco de esfriar." e crítico ">138: acima do ciclo máximo observado ({max}). Confirme se o deal ainda existe." + ação "Ligar hoje" | **Reescrever e unificar** — o primeiro texto (100–138 d) não corresponde a nenhuma regra (`scoring-spec.md` §3.1 só define zumbi > 138); a ação "Ligar hoje" em 81% do pipeline é o erro que a seção 3c evita. "Zumbi" não deve aparecer para o vendedor | "{days} dias em Engaging: nenhum deal na história fechou depois de {max}. Este deal saiu da sua fila de trabalho e está na fila 'Confirmar ou encerrar'." Ação: "Confirme com o cliente se a oportunidade existe; se não, encerre no CRM." (sem "hoje"). |
| `HIGH_TICKET` | + | "{product} tem ticket alto (R$ {price}): cada fechamento vale {mult}× a média." + "Priorize mesmo com probabilidade média." (ux-spec §9) | **Reescrever** — "{mult}× a média" pede uma média que o vendedor não tem na cabeça; e a versão de `scoring-logic.md` ("preço 5.482 × 1,00 de razão histórica × 64%") é fórmula, não frase | "Ticket alto: R$ {ev} esperados se fechar (preço de tabela R$ {price}; {product} fecha em {rate}% dos casos)." Ação: "Vale a semana mesmo com chance mediana." |
| `LOW_TICKET` | − | "{product} tem ticket baixo (R$ {price}): valor esperado limitado." + "Resolva rápido; não gaste mais de um contato." (ux-spec §9) | **Manter**, ajustando a ação — "não gaste mais de um contato" é decisão do vendedor, não da ferramenta | "Ticket baixo: {product} vale R$ {price}. Feche rápido ou deixe para depois dos deals maiores." Ação: "Resolva em um contato." |
| `PROSPECTING_NO_TIMELINE` | i | "Em Prospecting, sem data de engajamento: não dá para medir urgência." + "Qualifique e mova para Engaging, ou descarte." (ux-spec §9) | **Manter texto; reescrever a ação** — "ou descarte" é a ferramenta sugerindo desqualificar (proibido, seção 3d) | "Em Prospecting, sem data de primeiro contato: não dá para medir urgência; a posição na fila vem só do valor." Ação: "Registre o primeiro contato no CRM ao fazê-lo." |
| `AGENT_OVERLOAD` | i (ux-spec diz −) | "Você tem {n} deals abertos (mediana do time: {median}): menos tempo por deal." + "Descarte os frios para abrir agenda." (ux-spec §9) | **Reescrever** — direção errada; a ação manda descartar (proibido); e com 81% de zumbis a carga é quase toda deal morto — o número honesto é o de vivos | "Você tem {n} deals abertos, {zombies} deles parados há mais de {max} dias (time: mediana {median}). Encerrar os parados libera agenda e forecast." Ação: "Combine com seu manager um horário fixo para a fila 'Confirmar ou encerrar'." |
| `MODEL_CONTRIBUTION` | ± | "Modelo estatístico {ajusta} a estimativa das regras em {delta} pontos." (ux-spec §9) | **Não exibir na v1** — peso zero, modo sombra (`scoring-spec.md` §5). Mostrar "modelo confirma (+0)" faz o vendedor acreditar que existe um modelo decidindo | Quando `BLEND_MODEL_WEIGHT > 0`: "Ajuste do modelo: {delta} pontos ({sinal}). Veja em Qualidade por que ele foi ativado." Até lá, filtrar no backend ou na UI. |
| `QUARTER_END_WINDOW` (proposto) | i | "Faltam {days} dias para o fim do trimestre: 49% dos Won fecham em mês de fim de trimestre (Lost: 20%)." (`scoring-logic.md`, "Proposta de adição ao enum") | **Não aprovar com estes números** — ver seção 3b | Se o tech-lead quiser o código mesmo assim: "Faltam {days} dias para o fim do trimestre." Só isso, sem percentuais, e só quando `days ≤ 14`. |

### Outros textos da UI que superestimam previsão (fora da tabela de reason codes)

| Onde (`ux-spec.md`) | Texto atual | Problema | Proposta |
|---|---|---|---|
| §4.1 cabeçalho do drawer; §8 `deal.pWin` | "Prob. de fechar 71 %" / `Prob. de fechar ${p} %` | `p_win` é a taxa do **produto** (60–65%), igual para todo deal do mesmo produto (`scoring-spec.md` §0). Chamar de "probabilidade de fechar" **este** deal é a única mentira que o resto do projeto se esforça para não contar. Em zumbi mostraria "31%", que é convenção (`scoring-logic.md`, Limitações 7) | "Fecham {p}% dos {product}" (taxa do produto). Em zumbi: "Sem histórico de fechamento nesta idade" no lugar do número. |
| §3.3 tile 1; §8 `queue.tiles.hot` e `tierHint.A` | "deals quentes para agir esta semana" / "Quente: agir esta semana" | "Quente" = alta chance. A não é chance, é valor × dentro do ciclo × confiança | Tile: "{n} deals para trabalhar esta semana". Tier A: "Vale a semana: bom valor, dentro do ciclo, dados completos". |
| §3.3 tile 3; §8 `queue.tiles.stale` | "{n} deals parados há +100 dias" | Para o vendedor mediano isso mostra ~50 de 60 deals — número que não muda decisão. E mistura "esfriando" (101–138) com "morto" (> 138) | Dois números: "{n} esfriando (101–138 dias)" e "{n} para confirmar ou encerrar (+138 dias) · R$ {v} mil". |
| §5.1 tile "em risco (parados há +100 dias)" e §5.3 definição | "Em risco = valor esperado dos deals com mais de 100 dias" | Com 81% acima de 138, "em risco" vira quase o pipeline inteiro e some a distinção que importa para o manager | "Esfriando = 101–138 dias (R$ X). Parados = mais de 138 dias, nunca houve fechamento (R$ Y nominais, fora do forecast)." |
| §6.1 bloco 1 "A ferramenta vence o feeling?" e frase `quality.wins` | Barras de "quantos dos 10 primeiros fecharam" com a frase de vitória como primeira opção | Os números reais são **6,3 de 10 para o scorer vs 6,6 do aleatório** (`10_backtest.md`, P@10 2017-06-30: 0,627 vs 0,660). A frase de empate (`quality.ties`) tem de ser o padrão e dizer o que a tela responde de verdade | Título: "Ela acerta mais quem vai fechar?" Resposta fixa: "Não. Nenhum critério acerta mais que o acaso (6,3 vs 6,6 de 10). O ganho está em valor, momento e limpeza — blocos 3 e 4." |
| §6.1 bloco 4 "Receita capturada" e `quality.revenue` | "capturado {top}% da receita (aleatório: {rnd}%)" | Omite que "maior preço primeiro" faz 50,5%. Omissão que a Head vai descobrir sozinha e perder confiança | "…capturaria {top}% (aleatório {rnd}%; ordenar só por preço {price}%). A diferença para o preço é o custo de dizer quando agir e de tirar os parados." |
| §8 `confidence.hint.media` | "Conta não informada ou histórico pequeno." | OK. Mas `hint.baixa` = "Prospecting sem data ou quase sem histórico" omite o caso mais comum (zumbi; 1.629 baixas, `10_backtest.md` "Confiança") | `baixa`: "Deal parado há mais de 138 dias, ou Prospecting sem conta, ou histórico pequeno." |
| §4.2 ação `discard` | "Descartar remove o deal da sua fila, não do CRM." | Correto e honesto. Mas é o oposto do que o sprint de limpeza precisa (encerrar **no CRM**). Ver lacuna 2 da seção 4 | Renomear para "Ocultar da minha fila" e adicionar ação "Encerrado no CRM" (registro, sem integração na v1). |

---

## 2. A segunda-feira de manhã, por persona

Números de base (verificados na seção 7, snapshot 2017-12-31): 27 vendedores com deals abertos; por vendedor, mediana de **12 deals vivos** (0–31), **44 parados** (19–83) e **0 em Prospecting** (75% dos vendedores têm 0; os 500 Prospecting se concentram em poucos — máximo 111 num só vendedor). Seis vendedores não têm nenhum deal vivo.

### 2.1 Vendedor — "em quais deals eu ligo hoje, e por quê?"

A lista que ele vê é "valor × momento": os deals vivos ordenados por quanto valem se fecharem e por estarem na janela em que deals daquele produto costumam fechar (`scoring-spec.md` §3.3–3.4). Ele **não** está vendo "os que têm mais chance". O texto de abertura da fila deve dizer isso uma vez, em uma linha, e nunca mais: "Ordem: valor esperado e momento do ciclo. Deals parados há mais de 138 dias estão em outra fila."

O que ele faz, em 12 minutos:

1. **Lê os 5 primeiros da fila "Trabalhar"** (mediana 12 deals; top 10 já é a lista inteira para a maioria). Para cada um, uma pergunta: "qual é o próximo passo concreto e quando?" A `next_action` de `scoring-spec.md` §3.7 ("Ligar esta semana e propor data de fechamento") é boa porque pede **data**, não "follow-up".
2. **Trata primeiro os que estão entre 121 e 138 dias** — 188 deals em todo o time estão na faixa 91–138 (`data-quality-report.md`, "Idade dos deals abertos"). O texto "faltam {remaining} dias para o ciclo máximo já visto: fechar ou desistir esta semana" é o único lugar onde a ferramenta muda decisão por **tempo**, e é honesto: não diz que vai fechar, diz que a janela acaba.
3. **Reserva 15 minutos por dia para a fila "Confirmar ou encerrar"** (mediana 44 deals): 5 por dia, começando pelos de maior valor e, em empate, pelos mais novos (`scoring-spec.md` §4). Em nove dias úteis a fila dele está zerada. Sem isso, ele nunca vai saber se os R$ 109 mil nominais medianos que carrega existem.
4. **Registra o que fez** (Contatado / Reunião / Proposta / Conta corrigida / Encerrado no CRM). É o que vai calibrar o fator 0,5 dos parados (`scoring-spec.md` §4) e é a única fonte de dado de atividade que a empresa terá (lacuna 1, seção 4).

Para os **seis vendedores sem deal vivo**: a fila "Trabalhar" mostra o estado vazio com copy específica — não a de `ux-spec.md` §7 ("Nenhum deal aberto neste recorte"), que soa a erro. Proposta: "Nenhum deal dentro do ciclo. Seus {n} deals abertos passaram de 138 dias: comece pela fila 'Confirmar ou encerrar' e registre novas oportunidades no CRM." Para esses seis a ferramenta é, honestamente, uma ferramenta de limpeza e prospecção nesta quinzena.

**O que vence o feeling aqui** (a exigência do brief e de `.claude/agents/revops-engineer.md`): o feeling não sabe que nenhum deal fechou depois de 138 dias, e o feeling tende a ligar para quem respondeu por último, não para o GTX Plus Pro de 127 dias com R$ 3.537 esperados que fecha em 11 dias ou nunca (`scoring-logic.md`, exemplo `059K86LU`).

### 2.2 Manager — "quem tem deal grande esfriando? onde o time perde tempo?"

A resposta honesta para "onde o time perde tempo" é o próprio pipeline: por manager, os parados somam de R$ 282 mil (Dustin Brinkmann, 190 deals) a R$ 842 mil (Celia Rouche, 257) — `docs/figures/11_diagnostics.md`, "Por manager". Nenhuma técnica de venda recupera isso; um sprint de limpeza recupera o forecast e a agenda.

**Sprint de limpeza de CRM — desenho operacional**

| Item | Definição |
|---|---|
| **Dono** | O manager. O vendedor executa; o manager acompanha o progresso na tela Time e desempata casos "não sei". A Head patrocina e comunica o **porquê** para o time antes de começar (evita leitura punitiva). |
| **Escopo** | Os 1.291 deals em Engaging com mais de 138 dias no snapshot (`scoring-spec.md` §4). Ordem dentro da fila: valor nominal desc, empate pelo mais novo. **Primeira onda:** os 561 deals entre 139 e 180 dias (R$ 1,25 mi nominais; verificado na seção 7) — são os mais prováveis de ainda existirem. Segunda onda: os 730 acima de 180 dias (R$ 1,94 mi). |
| **Cadência** | Sprint de **2 semanas**. Meta por vendedor: 5 deals/dia úteis (a mediana de 44 fecha em 9 dias). Check-in de 10 minutos na reunião de pipeline de segunda 10h: "quantos confirmados, quantos encerrados, quantos sem resposta ainda". Sem ranking entre vendedores — a tabela do Time já é ordenada por valor parado, não por pessoa (`ux-spec.md` §5.2). |
| **Critério: confirmar (mantém aberto)** | Contato bilateral com o cliente nos últimos 30 dias **documentado no CRM** (e-mail, reunião ou ligação com registro) **e** um próximo passo com data. Se confirmar: o vendedor registra "Confirmado" e o deal volta para "Trabalhar" com a data do contato como novo marco (lacuna 3, seção 4 — hoje não existe campo para isso). |
| **Critério: encerrar como Lost** | Qualquer um: (a) cliente disse não ou comprou de outro; (b) duas tentativas de contato em 10 dias úteis sem resposta; (c) contato do cliente não existe mais na empresa e não há substituto; (d) deal duplicado de outro aberto ou já fechado com a mesma conta e produto. Motivo de Lost registrado em uma das quatro letras — vira dado. |
| **Critério: "não sei"** | Vai para o manager na segunda. Se em 2 semanas ninguém consegue dizer se o deal existe, ele não existe: encerrar em (b). |
| **Efeito esperado no forecast** | Pipeline Engaging cai de 1.589 para ~300–400 deals; o valor "aberto" cai de R$ 3,88 mi para ~R$ 0,7–1,0 mi nominais. **Nada disso é receita perdida** — pelo histórico, zero desses deals fecharia (0 de 679 nos cortes; `scoring-logic.md`, "Regras duras"). Tudo que for confirmado na primeira onda é upside que hoje está invisível. **Aviso à Head:** marcar 1.291 deals como Lost derruba o win rate acumulado de 63% para **53%** (4.238 / 8.002; verificado na seção 7) — reportar essa coorte separada, como "limpeza de dezembro", e não deixar que entre na meta de conversão do trimestre. Quem não avisar isso antes vai ter o sprint sabotado. |
| **Efeito esperado na agenda** | Vendedor mediano passa de 56 deals "abertos" para ~12–20. É a única forma de o "mais tempo por deal" acontecer de verdade. |

**O que o manager faz com "deal grande esfriando":** filtra a fila do time por 101–138 dias e valor esperado. São poucos (188 no time todo); ele consegue perguntar de cada um na segunda. Para GTK 500 (R$ 26.768 de tabela, só 25 fechados no histórico) o manager entra pessoalmente: 14 GTK 500 estão parados há mais de 138 dias, R$ 375 mil nominais (verificado na seção 7) — se um só existir, paga o sprint.

### 2.3 Head de RevOps — "posso confiar nisso mais do que no feeling? quanto do pipeline cobre?"

**O que concluir:** (1) cobertura 100% dos 2.089 abertos, sem descartar ninguém; (2) a ferramenta **não** substitui julgamento sobre "vai fechar" — os dados do CRM não têm o que decide um deal (interações, proposta, concorrência, decisor; `scoring-logic.md`, Limitações 1); (3) ela substitui, sim, a ausência de qualquer critério sobre **valor e tempo**, e expõe um problema de higiene de R$ 3,19 mi que nenhum dashboard atual mostra; (4) 68% dos deals abertos sem conta é problema de processo comercial, não de dado — e sem conta não há nada para a ferramenta aprender no futuro.

**Piloto com grupo de controle (8 semanas — um ciclo mediano de Won são 57 dias, `crm-dataset`)**

| Elemento | Desenho |
|---|---|
| Unidade | Vendedor (27 ativos). Sorteio **dentro de cada manager** (estratificado): metade dos vendedores de cada time usa a ferramenta, metade continua no feeling. Evita que a diferença entre managers (R$ 282 mil vs R$ 842 mil parados) contamine o resultado. |
| Fase 0 (semanas 1–2) | Sprint de limpeza **para todos** — tratamento e controle. Motivo: a limpeza é a intervenção de maior efeito e deve acontecer independentemente do piloto; se só o tratamento limpar, o piloto mede a limpeza, não a ferramenta. O controle limpa por lista exportada, sem a UI. |
| Fase 1 (semanas 3–8) | Tratamento trabalha pela fila; controle trabalha como sempre. Ninguém vê o ranking do outro. |
| **Métrica primária** | **Receita fechada por vendedor-semana em deals que estavam vivos (≤ 138 d) no início da fase 1**, valor de fechamento real. Comparar médias tratamento vs controle com intervalo por bootstrap. |
| Secundárias | (a) **Tempo até o primeiro contato registrado** nos deals que a ferramenta marca como "fechar ou desistir" (121–138 d); (b) **% de deals abertos com conta preenchida** (base 32%); (c) **% da fila de parados resolvida** (confirmado ou encerrado) ao fim da fase 0; (d) **erro de forecast**: |forecast declarado − fechado| / fechado, por time, antes e depois. |
| Guardrails | (e) Uso: logins e ações registradas por vendedor-semana — sem uso não há efeito para medir; (f) nenhum ranking público de vendedores durante o piloto; (g) taxa de Lost "sem resposta" (critério b) para detectar limpeza por atacado sem contato. |
| Leitura honesta | Com 13–14 vendedores por braço só se detecta efeito grande na receita; a Head deve tratar a métrica primária como **direcional** e decidir o rollout principalmente pelas secundárias (b), (c) e (d) e pelo uso (e). Dizer isso antes evita "o piloto não provou nada" depois. |

---

## 3. Julgamento sobre as quatro decisões abertas

### 3a. Peso da urgência 40 vs ordenar para maximizar receita

**Recomendação: manter 25 / 35 / 40.** Justificativa:

1. A métrica "receita no top 20%" só conta deals **com desfecho** — por construção, nenhum deal morto entra nela, então ela não vê o benefício de demover os parados (`docs/scoring-logic.md`, "Leitura sem eufemismo"). Comparar 0,38 com 0,51 é comparar uma lista que resolve dois problemas com uma que resolve um.
2. Com 25/50/25 a correlação com preço vai a 0,93 (`docs/figures/11_diagnostics.md`, "Grade de pesos") — é uma lista de preços, e o brief é explícito: "precisa ter lógica de scoring/priorização (não é só ordenar por valor)" (`README.md` do challenge, "Requisitos mínimos").
3. Ordenar por preço concentra o time em GTK 500: 25 fechados no histórico, taxa 61% (`scoring-logic.md`, exemplo `A04V2WB3`) — quem monta a semana só com GTK 500 vai passar semanas sem fechar nada e abandonar a ferramenta.
4. **A visão "maximizar receita" já existe de graça**: a ordenação secundária por valor esperado da fila (`ux-spec.md` §3.3, `sort=value`). Quem quiser a lista de preços clica nela, com o aviso "a prioridade continua no badge".

**Discordo de um ponto da metodologia:** `scoring-methodology` diz "peso ajustável pelo manager". Na v1, **não expor ajuste de pesos** na UI. Seis managers com seis ordenações diferentes destroem a comparabilidade da tela Time e transformam toda reunião de pipeline em discussão sobre pesos. Pesos ficam em `weights.py`, versionados; mudança é decisão de RevOps com backtest, não botão.

### 3b. `QUARTER_END_WINDOW` — comportamento real ou artefato?

**Recomendação: não aprovar como reason code por deal com números; no máximo um lembrete de calendário sem percentuais, e só depois da Head validar com o negócio.**

O que verifiquei além dos documentos (comandos na seção 7):

| Traço esperado se fosse "esforço de fim de trimestre" real | O que o dado mostra |
|---|---|
| Fechamentos Won concentrados nos últimos dias do mês de fim de trimestre | **Não.** 19,2% dos Won de mar/jun/set/dez caem nos últimos 5 dias — igual aos 19,0% dos outros meses; a distribuição por semana do mês é idêntica. |
| Volume total de fechamentos sobe no fim do trimestre | **Não.** Fechamentos por mês variam de 566 a 805 sem padrão trimestral; o Won de mar/jun/set/dez fica em 503–531, contra 279–446 nos outros meses, mas… |
| … o Lost cai proporcionalmente? | O que muda é o **Lost**: 110–140 nos meses de fim de trimestre vs 287–367 nos demais; abr/jul/out concentram Lost com **ciclo mediano de 7 dias** (vs 76 nos meses de fim de trimestre). |
| Win rate mensal | 78–83% em mar/jun/set/dez; 49–57% nos outros nove meses (`11_diagnostics.md`, "Efeito fim de trimestre"). |

Leitura: não é "deal fecha mais no fim do trimestre"; é "**Lost quase não é registrado em mês de fim de trimestre**, e aparece no mês seguinte como deal curto". Há duas explicações e nenhuma vira ação por deal: (i) comportamento real de **segurar o Lost** para proteger o forecast do trimestre — que é um problema de processo a corrigir, não um sinal a explorar; (ii) artefato de um dataset possivelmente sintético (Kaggle), que gera datas de fechamento com regra de calendário — hipótese que `scoring-logic.md` (Limitações 6) já levanta e que a uniformidade dentro do mês reforça. Há ainda um problema prático: o snapshot **é** 31/12 — último dia de trimestre — então o código dispararia em todos os deals ou em nenhum na demonstração.

Como a UI deve tratar, se o tech-lead mantiver o código no enum: uma linha de contexto no topo da fila do **time** (não por deal): "Faltam {days} dias para o fim do trimestre." Sem "49% dos Won", sem "81% vs 52%" — esses números descrevem quando o Lost é registrado, não quando o vendedor deve ligar. E uma pergunta para a Head levar ao negócio: "nosso time registra Lost no mês seguinte ao fechamento do trimestre?" Se sim, isso entra no sprint de limpeza como regra: Lost se registra quando acontece.

### 3c. Como enquadrar os parados para não dizer "agir agora" em 81% do pipeline

Princípios e como a UI os cumpre:

1. **Duas filas, dois verbos.** "Trabalhar" (vivos, 298 + Prospecting) e "Confirmar ou encerrar" (1.291). O parado **nunca** aparece na fila "Trabalhar", nem em tier C/D dela — sai da lista. `scoring-spec.md` §4 já pede fila separada; o que falta na `ux-spec.md` §3 é a home mostrar a segunda fila como **aba com contador**, não como linhas ▼ misturadas (o wireframe §3.1 linha 3 mistura um deal de 121 dias com "Confirmar hoje se o deal ainda existe" — é vivo, e a ação é de zumbi).
2. **Vocabulário.** "Zumbi" fica nos documentos internos e na tela da Head. Para o vendedor: "parado há mais de 138 dias". Ninguém quer ouvir que carrega 44 zumbis; todo mundo aceita que tem 44 deals "para confirmar".
3. **Urgência administrativa, com cota.** A ação não é "ligar hoje"; é "5 por dia, começando pelo mais valioso". A fila mostra barra de progresso ("12 de 44 confirmados/encerrados") e o total nominal ("R$ 109 mil que não estão no seu forecast até você confirmar"). É o mesmo dado, virado de custo para ganho.
4. **Sem probabilidade falsa.** Não mostrar "31% de chance" (é 0,5 × taxa do produto, convenção — `scoring-logic.md`, Limitações 7). Mostrar "Sem histórico de fechamento nesta idade". Score de zumbi (≤ 49) só como ordenação dentro da fila, sem badge de tier na linha — tier C/D com hint "Frio ou parado: decidir se continua" (`ux-spec.md` §8 `tierHint.D`) até é razoável, mas o badge junto com o número induz comparação com os vivos.
5. **Ordem por chance de existir.** Valor desc e, em empate, mais novo primeiro (`scoring-spec.md` §4). Acrescentar faixas visíveis: "139–180 dias" (561 deals, R$ 1,25 mi) é a primeira onda; "acima de 300 dias" (238 deals) o vendedor pode encerrar em bloco após uma tentativa.
6. **Para o manager, a fila é dinheiro, não culpa.** Tile "R$ 842 mil parados fora do forecast" com o sprint linkado, tabela por vendedor ordenada por valor parado, coluna de carga ao lado (`ux-spec.md` §5.2) — sem coluna de posição.

### 3d. O que a ferramenta deve dizer explicitamente que NÃO faz

Para constar no README, no rodapé da tela Qualidade e na primeira abertura da fila (uma vez, dispensável):

1. **Não prevê se um deal vai fechar.** Ordena por valor esperado e momento do ciclo. Todo critério que testamos empata com o acaso nessa pergunta.
2. **Não sabe nada que não esteja no CRM**: não vê e-mails, reuniões, propostas, concorrência nem decisor. Se você falou com o cliente ontem, a ferramenta não sabe — registre.
3. **Não decide encerrar um deal.** Ela diz "nenhum deal fechou depois de 138 dias"; quem confirma e encerra é você, e o encerramento acontece no CRM, não aqui.
4. **Não avalia vendedores.** A taxa de fechamento de cada um aparece como contexto, sem peso, e nunca em ranking. Diferença de 55% a 70% entre vendedores não se sustentou fora do período em que foi medida.
5. **Não usa o valor de fechamento nem a data de fechamento** dos deals abertos — eles não existem antes do desfecho. Valor esperado vem do preço de tabela do produto.
6. **Não muda o score com base na conta** (setor, porte, histórico): 68% dos deals abertos não têm conta e, quando têm, isso não previu fechamento. A conta aparece como contexto e pede preenchimento.
7. **Não sabe se hoje é fim de trimestre** de forma útil por deal (seção 3b).
8. **Não funciona com dados de hoje**: toda idade é contada até a data de referência (31/12/2017) — `ux-spec.md` §3.4 já mostra isso; reforçar no README.

---

## 4. Lacunas de requisitos antes de um rollout real (priorizadas)

| # | Lacuna | Por que é necessária | Tipo |
|---|---|---|---|
| 1 | **Data de última atividade por deal** (último contato, reunião, proposta) no CRM ou via integração de e-mail/calendário | É o dado que decide um deal e que não existe (`scoring-logic.md`, Limitações 1). Sem ele, "parado há 150 dias" e "falei ontem" são indistinguíveis; com ele, o zumbi vira regra de inatividade, não de idade. É a única lacuna que pode fazer o score voltar a prever algo. | campo / integração |
| 2 | **Escrita de volta no CRM** para as ações da fila (confirmado, encerrado como Lost com motivo, conta preenchida) | Hoje `POST /feedback` grava num arquivo local e "Descartar" oculta da fila sem tocar o CRM (`ux-spec.md` §4.2). Sprint de limpeza sem escrita no CRM é trabalho dobrado e ninguém repete trabalho dobrado. | integração |
| 3 | **Campo "confirmado em" (data) e motivo de Lost em 4 categorias** | Permite que um parado confirmado volte à fila de trabalho com marco novo, e que a coorte de limpeza seja separada do win rate operacional (seção 2.2). O motivo de Lost em categorias é o dado que a empresa nunca teve. | campo |
| 4 | **Conta obrigatória ao criar oportunidade** (regra de CRM) | 68% sem conta não é atraso, é constante em toda idade (`data-quality-report.md`, "`account_known` é um artefato temporal"). Nenhuma ferramenta corrige isso depois; só a regra de entrada. Métrica (b) do piloto. | processo |
| 5 | **Snapshots periódicos do pipeline** (histórico de estágio por data) | Só existe um snapshot; conta e estágio do passado são anacrônicos (`data-quality-report.md`, "Limitações do dado"). Sem snapshots, nenhum backtest futuro é confiável e o PSI de `account_*` vai continuar disparando. | dado |
| 6 | **Data de engajamento obrigatória em Prospecting** ou definição do que "Prospecting" significa | 500 deals sem data alguma; urgência "desconhecida" (`scoring-spec.md` §3.3). Concentrados em poucos vendedores (máximo 111 num só) — é provável que seja lista importada, não pipeline. Validar com o negócio antes de pontuar. | campo / processo |
| 7 | **Ciclo de recalibração com o feedback** (mensal): fator dos parados, threshold 138, hazard | `ZOMBIE_P_FACTOR` é convenção (`scoring-spec.md` §2). Depois do sprint teremos, pela primeira vez, "quantos parados existiam de fato". Definir quem roda, quando, e o critério para mudar peso. | processo |
| 8 | **Autenticação e visão por perfil** (vendedor vê só a própria fila; manager o time; Head tudo) | Hoje os filtros são livres na URL (`ux-spec.md` §2). Ranking implícito de vendedores fica a um clique de qualquer um — viola o "não avalia vendedores" da seção 3d. | integração / segurança |
| 9 | **Validação com o negócio do padrão de fim de trimestre** (seção 3b) e da regra "Lost se registra quando acontece" | Se o padrão for real, é problema de processo que distorce o forecast trimestral; se for artefato, sai da lista. Uma reunião resolve. | processo |
| 10 | **Definição do forecast oficial** a partir da ferramenta: só deals vivos, valor esperado = preço × taxa do produto | Sem isso, alguém soma os R$ 3,19 mi parados ao forecast, ou os R$ 998 mil "esperados" dos zumbis (`scoring-spec.md` §4 proíbe explicitamente). | processo |

Fora da lista por decisão consciente: mais features de ML. Não há sinal nos dados atuais (`docs/figures/20_model_candidates.md`); a lacuna 1 vem antes de qualquer modelo.

---

## 5. Onde discordo do design atual (para o tech-lead desempatar)

1. **`ux-spec.md` §4.1 / §8 `deal.pWin` — "Prob. de fechar {p}%"**: é a taxa do produto e deve ser rotulada assim. Bloqueante para mim; contradiz o posicionamento inteiro.
2. **`ux-spec.md` §9 — direções `+/−` e ações para `AGENT_*`, `SECTOR_FIT`, `ACCOUNT_SIZE`, `AGENT_OVERLOAD`**: devem ser `i`, sem ação, conforme `scoring-spec.md` §3.1. O drawer de exemplo (§4.1) precisa ser refeito com o caso `059K86LU` real de `scoring-logic.md`.
3. **`scoring-logic.md`, "Proposta de adição ao enum" — `QUARTER_END_WINDOW` com "49% dos Won"**: não aprovar com números (seção 3b).
4. **`ux-spec.md` §3.3 tile "parados há +100 dias" e §5 "em risco = +100 dias"**: separar esfriando (101–138) de parados (> 138); com 81% acima de 138 o tile atual não muda decisão.
5. **`ux-spec.md` §6.1 — bloco "vence o feeling" com frase de vitória como padrão**: os números reais dão empate/derrota em acerto; a tela tem de abrir dizendo isso e apontando para valor e limpeza.
6. **`scoring-methodology` — "peso ajustável pelo manager"**: não na v1 (seção 3a).
7. **`ux-spec.md` §9 — ações "descarte" em `PROSPECTING_NO_TIMELINE` e `AGENT_OVERLOAD`**: a ferramenta não sugere desqualificar (seção 3d, item 3).
8. **`ux-spec.md` §3.1 wireframe linha 3**: deal de 121 dias com ação de zumbi ("Confirmar hoje se o deal ainda existe"). Para 121–138 a ação correta é a de `scoring-spec.md` §3.7: "faltam {n} dias para o ciclo máximo: fechar ou desistir esta semana".

Concordo e reforço: fila de zumbis separada com desempate pelo mais novo (`scoring-spec.md` §4); tabela do manager por valor em risco sem posição (`ux-spec.md` §5.2); tier A barrado para confiança baixa (`scoring-spec.md` §3.6); pesos 25/35/40 (`process-log/decisions.md`, 2026-09-23 13:45).

---

## 6. O que precisa de validação humana do Bernardo

1. Aceitar a troca de "Prob. de fechar" por "Fecham {p}% dos {product}" na UI (item 1 da seção 5).
2. Decidir com o tech-lead se `QUARTER_END_WINDOW` entra no enum como lembrete sem números ou fica fora da v1.
3. Confirmar o vocabulário "Trabalhar" / "Confirmar ou encerrar" e "parado" (vendedor) vs "zumbi" (interno).
4. Confirmar que "Descartar" vira "Ocultar da minha fila" e ganha a ação "Encerrado no CRM" como registro.
5. Aprovar a redação final da tabela da seção 1 para o `machine-learning-engineer` gerar `text_pt` no pipeline (com teste de snapshot exigindo ≥ 1 dígito por texto, `scoring-spec.md` §6.11).

---

## 7. Como reproduzir os números novos deste documento

```bash
cd solution/pipeline
uv run python - <<'PY'
import pandas as pd
p = pd.read_csv("../data/raw/sales_pipeline.csv", parse_dates=["engage_date","close_date"])
pr = pd.read_csv("../data/raw/products.csv"); pr["product"] = pr["product"].replace({"GTXPro": "GTX Pro"})
p["product"] = p["product"].replace({"GTXPro": "GTX Pro"})
p = p.merge(pr[["product", "sales_price"]], on="product", how="left")
SNAP = pd.Timestamp("2017-12-31")

# Fim de trimestre: Won/Lost por mês de fechamento; dia do mês; ciclo
c = p[p.deal_stage.isin(["Won", "Lost"])].copy()
c["m"] = c.close_date.dt.to_period("M"); c["qe"] = c.close_date.dt.month.isin([3, 6, 9, 12]); c["dom"] = c.close_date.dt.day
print(c.pivot_table(index="m", columns="deal_stage", values="opportunity_id", aggfunc="count"))
won = c[c.deal_stage == "Won"]
print("Won nos últimos 5 dias: fim de tri %.3f · outros %.3f" % ((won[won.qe].dom >= 26).mean(), (won[~won.qe].dom >= 26).mean()))
lost = c[c.deal_stage == "Lost"]; lost["cyc"] = (lost.close_date - lost.engage_date).dt.days
print("ciclo mediano Lost: fim de tri", lost[lost.qe].cyc.median(), "· abr/jul/out", lost[lost.close_date.dt.month.isin([4, 7, 10])].cyc.median())

# Composição por vendedor no snapshot
o = p[p.deal_stage.isin(["Engaging", "Prospecting"])].copy()
o["d"] = (SNAP - o.engage_date).dt.days
o["cls"] = pd.cut(o.d, [-1, 138, 10_000], labels=["live", "zombie"]).astype(str).where(o.deal_stage == "Engaging", "prospecting")
g = o.groupby(["sales_agent", "cls"]).size().unstack(fill_value=0)
print(g.describe().loc[["50%", "min", "max"]]); print("vendedores sem deal vivo:", (g["live"] == 0).sum(), "de", len(g))
z = o[o.cls == "zombie"]
print("valor nominal parado por vendedor, mediana:", z.groupby("sales_agent").sales_price.sum().median())
print(z.groupby(pd.cut(z.d, [138, 180, 240, 300, 430])).sales_price.agg(["size", "sum"]))
print("GTK 500 parados:", (z["product"] == "GTK 500").sum(), z[z["product"] == "GTK 500"].sales_price.sum())
print("win rate se 1.291 virarem Lost: %.3f" % (4238 / (6711 + 1291)))
PY
```

Saída obtida em 2026-09-23: Won nos últimos 5 dias 0,192 vs 0,190; ciclo mediano Lost 76 (fim de tri) vs 7 (abr/jul/out); por vendedor mediana 12 vivos / 44 parados / 0 Prospecting; 6 de 27 sem deal vivo; R$ 108.803 parados por vendedor (mediana); 561 deals e R$ 1.254.970 na faixa 139–180 dias; 14 GTK 500 parados (R$ 374.752); win rate pós-limpeza 0,530.
