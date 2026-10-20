# PRD — Challenge 003 | Lead Scorer

**Status:** entregue em 19/10/2026 (escopo congelado em 15/10/2026 e ampliado pelas revisões 1 a 11 abaixo) · **Dona:** Maria Alice Dantas · **Base:** [architecture.md](./architecture.md) (ADR-001 a ADR-010), [data-audit.md](./data-audit.md) e [discovery.md](./discovery.md). Este PRD não reabre o discovery: reduz os seis P0 da arquitetura (F-01 a F-06) a três (P0-1 a P0-3), fixa aceite, dados, comandos e ordem de construção, e recebe o P0-4 (Revisão 5) e o P0-5 (Revisão 11). **Revisão 1** (teste de mesa, 15/10/2026): próximos passos, legenda de ordem, frase de posição e AC-2.12. **Revisão 2** (16/10/2026): contrato orientado a dados ([ADR-004](./architecture.md#adr-004)). Os critérios de texto passam a ser de código no back e de texto nos catálogos da tela e da CLI; entram os AC-4.x do contrato e o backtest com todas as abertas em cada corte. **Revisão 3** (16/10/2026): interface Rankio ([ADR-005](./architecture.md#adr-005) e [design-system.md](./design-system.md)).
- **Nova jornada:** abas por grupo, cartão "Seu próximo passo" e painel lateral.
- **Páginas novas:** Equipe, Evidência e Como funciona, com menu central.
- **Contrato v4:** `/api/evidence`, `/api/rules` e `by_seller` (AC-4.5 e AC-4.6).
- **Critérios de interface:** AC-5.x.
- **Ajustes da revisão visual (16/10/2026):** cursor de clique em todo elemento clicável; tabelas paginadas no lugar de "Mostrar mais"; filtros de gerente e escritório que se restringem; Evidência com a escolha entre linguagem de negócio e técnica, e cartão "A pergunta" com os números à esquerda e o gráfico à direita.

**Revisão 4** (16/10/2026): regra A ([ADR-006](./architecture.md#adr-006)) e contrato v5.
- **Regra:** dois limites de idade, calculados no `as_of` (L1 = piso do P90 do ciclo das ganhas, 106 d; L2 = maior ciclo fechado, 138 d), e o grupo novo Acompanhar entre Focar e Revisar.
- **Nomes na tela:** Focar, Acompanhar, Confirmar (chave `revisar`), Qualificar e Completar (chave `nao_pontuavel`); os limites aparecem como fato do histórico, nunca como prazo.
- **Explicação:** só os dois motivos que decidem; a referência de ciclo por produto e a taxa das fechadas saem (AC-3.4 e AC-3.5 retirados).
- **Evidência:** a regra servida é a referência, e a página mostra a conclusão do recorte sem as que nunca fecham.

**Revisão 5** (17/10/2026): Inteligência comercial ([ADR-007](./architecture.md#adr-007)) e contrato v6.
- **Página nova entre Equipe e Evidência:** onde o processo pode melhorar (diagnósticos com próximo passo), o que os resultados mostram (descobertas por regras fixas) e a exploração por recorte até as negociações (P0-4).
- **Descreve, não prevê:** nenhum número da página entra na lista; toda taxa leva o n, a faixa provável e o veredito de acaso; realizado e valor de tabela nunca se somam.
- **Pessoas:** vendedor, gerente e escritório em ordem alfabética, sem gráfico e sem índice por pessoa (AC-2.9 continua valendo).
- **Sem filtro de período:** o histórico tem só de março a dezembro de 2017, e o 1º trimestre só tem março (82% de ganho, um artefato de registro).

**Revisão 6** (17/10/2026): orientação de verificação, conta neutra e contexto da idade ([ADR-008](./architecture.md#adr-008)) e contrato v7. Origem: teste com seis personas simuladas (`docs/testes-personas/`), persona do vendedor iniciante.
- **"O que verificar agora" no lugar de "Próximo passo":** a base não registra atividades, estágio nem contatos, então a orientação é uma verificação no CRM com base nos dados da linha (grupo e conta registrada ou ausente), sem presumir atividade, intenção nem compromisso. O painel diz isso.
- **Conta ausente é cadastro, não qualidade:** nas 4.238 ganhas e 2.473 perdidas a conta está sempre registrada, então a base não permite saber se ela indica algo sobre o desfecho; nas abertas (31%) ela não varia com a idade, o vendedor nem o escritório. Filtro "com / sem cliente registrado" na Carteira e na Equipe, sem mudar a ordem.
- **Idade com contexto, sem urgência:** o painel e a coluna Idade mostram a idade ao lado da mediana, de L1 e de L2 das vendas ganhas, com o aviso de que isso descreve as vendas que fecharam. Nenhum semáforo, contagem para o limite nem mudança de ordem.
- **Empates sem falsa ordem:** "N oportunidades empatadas (…): sem ordem entre si"; a ordem por código não vale como ranking. O critério de desempate não mudou.
- **Vocabulário:** "Engajada em" vira "Início da negociação"; Confirmar é a verificação de que a negociação continua; o resumo mostra só os grupos com itens e diz quais estão vazios.
- **Interface:** o menu vira um botão em telas estreitas (limite ajustado na Revisão 8); o selo de data, quando a API não responde, diz "Sem conexão com os dados" e deixa tentar de novo.
- **Fora desta revisão:** a ordem da lista, os grupos e o backtest não mudam; a conclusão comercial continua a mesma: a ferramenta organiza a verificação, não prova que as oportunidades escolhidas fecham mais.

**Revisão 7** (17/10/2026): nova ordem dos grupos ([ADR-009](./architecture.md#adr-009)), carteira com busca e filtros e sugestões de negociação no painel.
- **Ordem dos grupos:** Focar → Qualificar → Acompanhar → Confirmar → Completar. É uma decisão de produto, sem prova de desfecho: o backtest não avalia a Prospecting. Grupos, limites L1 e L2, faixas e a ordem dentro do grupo não mudam; Focar vazio passa a apontar para Qualificar quando ele tem itens.
- **Tabela:** sem linha de empate e com os IDs alinhados. O painel ainda diz que a ordem entre empatadas é só pelo código.
- **Busca e filtros na Carteira e na Equipe:** busca por ID, produto, cliente (e vendedor na Equipe), e filtros de cliente (com ou sem registro), produto, faixa de valor de tabela, idade e início da negociação, todos na URL. Descrevem a lista, não mudam ordem nem grupo; sem idade ou data, a oportunidade fica de fora quando esses filtros estão ativos.
- **Sugestões de negociação:** o painel traz, por grupo, possibilidades para contextos que a base não registra ("Se já houve contato recente: …"), e a nota do painel passa a dizer que o Rankio indica possibilidades para cenários, não uma certeza de próximo passo. As sugestões não vêm dos dados da oportunidade e não preveem resultado.

**Revisão 8** (17/10/2026): carteira mais enxuta e cabeçalho que não estoura.
- **Carteira:** o bloco de textos antes da tabela (total e grupos, legenda da ordem, grupos vazios e nota sobre o cliente) sai da tela. Entra o título "Suas oportunidades", com a quantidade de abertas numa etiqueta, e a busca e os filtros na mesma linha. A ordem dos grupos continua explicada em "Como funciona", e a ausência de cliente segue visível em cada linha ("sem cliente registrado"). Cada linha da Carteira tem uma caixa de seleção no lugar do ícone de seta: marcar de 2 a 5 oportunidades da aba atual faz surgir uma barra fixa ("N selecionadas", "Priorizar", "Limpar") que abre a priorização assistida direto nas perguntas, sem a etapa de escolher; a escolha vale só na aba onde foi feita. A CLI e a Equipe mantêm a legenda e a nota. Isso substitui, na Carteira, a legenda e o aviso que o AC-2.1 e o AC-2.12 descrevem na tela.
- **Cabeçalho:** o menu de páginas vira botão abaixo de 1024 px (antes, abaixo de 768 px); entre os dois, as cinco páginas, a data e o tema não cabiam e o tema saía da tela.

**Revisão 9** (17/10/2026): linguagem da Inteligência e da Evidência e um guia dos grupos. Origem: teste com seis personas simuladas, persona do vendedor experiente (Kary).
- **Guia dos grupos:** um botão "O que significa cada grupo?" ao lado das abas abre um popover com as cinco definições, na ordem das abas. O texto é o mesmo `groupDescription` do resumo de cada grupo, então não diverge do "Como funciona".
- **Linguagem de negócio:** "faixa provável" vira "entre X e Y: onde a taxa de ganho real provavelmente está"; "margem de erro" vira "a diferença real deve ficar entre…"; "dentro do acaso" vira "pequena demais para ser confiável: poderia aparecer mesmo que os recortes fossem iguais"; "Ciclo mediano de ganho" vira "Tempo típico até ganhar"; "ticket por venda (mix de produto)" vira "receita por venda (depende dos produtos vendidos)"; "Engajada em" vira "Início da negociação" na tabela de negociações da Inteligência. A linguagem técnica da Evidência (Δ, IC95%, Val@K) não muda.
- **Guarda de vocabulário:** `copy.test.ts` passa a proibir "margem de erro", "faixa provável", "dentro do acaso", "ticket" e "mix" nos textos da Inteligência e da Evidência em linguagem de negócio.
- **Fora desta revisão:** a ordem da lista, os grupos, os limites e o backtest não mudam, nem o contrato (v7). A Kary notou que a ordem dentro de Focar é, na prática, o preço de catálogo; a Evidência já diz que a regra rende 4,6 pontos a mais que só o valor de tabela, e essa mensagem fica. Não foi reproduzida a falha de troca de aba em "Ver análises".

**Revisão 10** (17/10/2026): títulos de faixa por página e uma frase sobre Confirmar. Origem: teste com seis personas simuladas, persona do vendedor sobrecarregado (Darcel).
- **Faixa dividida em páginas:** o título de faixa mostra o total da faixa no grupo; quando a página mostra só parte dela, mostra "X de Y nesta página". Antes, "Valor de tabela baixo (9)" aparecia sobre 8 linhas, e parecia faltar uma.
- **Confirmar:** a definição do grupo ganha "Confirmar é limpar a carteira, não prever venda", pois a Darcel perguntou se as negociações velhas estão mortas ou só esquecidas, e a base não responde isso.
- **README:** "faixa provável" vira "o intervalo em que ela deve ficar", na linha da Inteligência.
- **Fora desta revisão:** a ordem dentro dos empates (por código) e a regra não mudam. Ajudar a escolher entre empatadas com perguntas de triagem fica para decisão à parte.
- **Faixas de valor ao alcance:** cada título de faixa de valor de tabela da Carteira ganha o link "ver as faixas em Como funciona", pois o Melvin só achou os limites (alto a partir de 3.000, médio de 500 a 2.999, baixo até 499) em outra tela. Só o link: os limites não entram no título porque só existem em `/api/rules`, e levá-los ao `meta` mudaria o contrato.

**Revisão 11** (18/10/2026): priorização assistida pelo vendedor ([ADR-010](./architecture.md#adr-010)). Origem: teste com seis personas simuladas, persona do vendedor sobrecarregado (Darcel): "tenho várias oportunidades empatadas, por qual começo?".
- **O que é:** uma camada **declarada pelo vendedor**, separada do scoring. Ele escolhe de 2 a 5 oportunidades empatadas (ou avalia uma só), responde 7 perguntas (interesse, momento, necessidade, urgência, orçamento, decisão e próxima ação, sempre com "Não sei") e recebe uma ordem sugerida de trabalho por **pontos de qualificação declarada (0 a 100)**, com a quebra por pergunta, o que ainda não se sabe e o que fazer agora.
- **Pontos:** pesos 20/20/15/15/15/10/5, definidos pela dona do produto (Urgência reduzida de 25 para 15 para somar 100). "Não sei" vale 0 ponto confirmado e não é um "não": a tela mostra também até onde a pontuação iria se o que se desconhece se confirmasse. Pontos iguais ficam empatados. Quem tem 4 ou mais respostas "Não sei" fica num bloco à parte, sem posição. Pesos e pontos por resposta são **hipóteses a validar**, e a tela diz isso.
- **Categoria de trabalho** (o que fazer, não ordena): compromisso a cumprir ou a organizar, definir continuidade, avançar qualificação, retomar ou reavaliar, investigar primeiro, qualificar necessidade. "Hoje" é a data dos dados; ação com data até 7 dias depois (ou anterior) conta como compromisso a cumprir.
- **Onde fica:** só no navegador (`localStorage`), sem texto livre; nada vai ao servidor nem ao CRM. Aparece no cartão "O que verificar agora" (empate no topo), no painel "Por que está aqui" e como selo discreto na Carteira, sem mudar a ordem oficial. Cada avaliação pode ser removida, com confirmação.
- **Não muda:** classificação, ordem oficial, contrato (v7), API, CLI, backtest e Evidência. Nunca mostra porcentagem, "chance" ou "melhor oportunidade".
- **Fora desta revisão:** validação com vendedores reais (protocolo na entrega de validação), persistência em backend com usuários autenticados e ordenação a partir de pontos aprendidos nos dados.

## 1. Problema e valor

- **Problema:** segundo a Head de RevOps, os vendedores escolhem no feeling quais das 2.089 oportunidades abertas trabalhar, sem critério comum e visível. O custo disso nunca foi medido.
- **Valor proposto:** uma lista única do que abrir primeiro, com o motivo de cada posição em campos verificáveis e com o que os dados não sabem. Se isso melhora o resultado, só um piloto com grupo de controle vai dizer.

## 2. Jornada de demonstração (até 2 minutos)

`as_of` = 2017-12-31. Vendedor principal: **Zane Levy**. Contraste: **Darcel Schlecht**. A resposta vem antes da lista (cartão "O que verificar agora"), os grupos são abas e a explicação abre num painel lateral. O roteiro reflete a versão entregue (revisões 6 a 11).

| Etapa | O usuário faz | Informação visível | Reação do sistema |
| --- | --- | --- | --- |
| 1. Entrada (0:00–0:20) | Abre `localhost:3000` (vai para a Carteira) e escolhe Zane Levy; na próxima visita, ele já vem escolhido | "Dados até 31/12/2017" no cabeçalho; os 35 vendedores em ordem alfabética, com busca; cartão "O que verificar agora" com a verificação de Focar e o empate do topo: `01XZ9CRY` e `FZWU2I30` (GTX Plus Pro, 5.482) | Responde em menos de 1 s; nenhum percentual de chance; o vendedor fica na URL |
| 2. Interpretação (0:20–0:50) | Lê o título "Suas oportunidades" (88 abertas) e a aba Focar | Abas Focar 13, Acompanhar 18, Confirmar 57, Qualificar 0 e Completar 0 (88 = 13 + 18 + 57 + 0 + 0), com a definição do grupo ("Abertas há até 106 dias. No histórico, 90% das vendas ganhas fecharam dentro desse tempo. É sobre o tempo aberta, não sobre a chance de fechar."), o botão "O que significa cada grupo?", busca e filtros; tabela com ID, produto, cliente, valor de tabela, início da negociação e idade, e "sem cliente registrado" em cada linha sem conta | Ordena por grupo → faixa → preço → ID; agrupa empates ("sem ordem entre si"); dentro do grupo, a idade não ordena |
| 3. Decisão (0:50–1:30) | Abre `01XZ9CRY` e segue com "Próxima" | Painel "Por que está aqui" com os dois motivos que decidiram (por que neste grupo, por que nesta posição), a idade ao lado da mediana, de L1 e de L2 das ganhas, a nota do que o sistema não vê, "O que verificar agora" e "Copiar ID" | As frases só usam campos da linha; Anterior e Próxima seguem a ordem do grupo |
| 4. Vazio e desempate (1:30–2:00) | Troca para Darcel Schlecht | Ela não tem Focar nem Acompanhar (194 = 111 Qualificar + 83 Confirmar), então a Carteira abre em Qualificar e o cartão aponta Qualificar como ponto de partida; no topo, 13 oportunidades empatadas (GTX Plus Pro, 5.482). Ela marca de 2 a 5 e abre a priorização assistida (P0-5) | O vendedor age no CRM pelo ID (a ferramenta só lê, RE-03); o estado vazio não quebra a tela; a ordem oficial não muda |

**Jornada da Head de RevOps** (Revisão 3):

| Etapa | O usuário faz | Informação visível | Reação do sistema |
| --- | --- | --- | --- |
| 5. Equipe | Abre Equipe; filtra por gerente ou escritório | Quatro cartões de números no topo, como na Inteligência (valor de tabela em aberto 4,97 mi, 35 vendedores, 4.238 vendas ganhas e taxa de ganho 63,2%), e abaixo o cartão "Carteira aberta · 2.089" com a barra e a legenda clicável por grupo (157 Focar, 500 Qualificar, 141 Acompanhar, 1.291 Confirmar e 0 Completar); abaixo disso, duas abas centralizadas: "Por vendedor" (35, em ordem alfabética, 8 sem abertas) e "Por oportunidade" (2.089, a lista com a coluna Vendedor) | Nenhum percentual calculado na tela; nenhum ranking de pessoas (a tabela abre alfabética e o gerente pode ordenar por coluna); o nome leva à carteira do vendedor; só a análise aberta fica na tela |
| 6. Inteligência (Revisão 5) | Abre Inteligência; filtra pelo botão "Filtros" (produto, vendedor, gerente, escritório, setor, cliente ou porte) e abre "Ver análises" | No corpo, só números, gráficos e tabelas, com a leitura abaixo de cada tabela: receita ganha 10,01 mi, 4.238 vendas ganhas, taxa de ganho 63,2% de 6.711 fechadas (intervalo de 62,0% a 64,3%), ciclo mediano 57 dias; à parte, a carteira aberta (2.089, 4,97 mi em valor de tabela, "não é receita"); em "Ver análises", sete diagnósticos com próximo passo (1.291 de 1.589 em andamento acima de 138 dias, 1.425 abertas sem cliente contra 0 fechadas, 500 em prospecção sem data, 5 de 35 vendedores sem oportunidade, 80,7% de ganho no último mês do trimestre contra 52,3%, entrada de 283 e 121 contra 864,6 por mês, mediana de 10 vendedores por cliente) e o que o CRM não registra; descobertas (taxa de ganho dentro do acaso em todos os recortes; 3 de 7 produtos com 83,5% da receita; diferença entre vendedores vem do volume e do mix) | Nenhum número entra na lista; "Ver negociações" abre as negociações por trás do número com o mesmo recorte; "Ver na Equipe" leva ao grupo Confirmar |
| 7. Evidência | Abre Evidência (linguagem de negócio, o padrão) e, se quiser, troca para a técnica | "Se cada vendedor trabalhasse as 10 primeiras da lista, quanto do valor vendido nos 90 dias seguintes estaria nelas?": regra atual 58,4%, só valor de tabela 53,8% ("4,6 pontos a menos que a regra atual ; a diferença real deve ficar entre 2,5 e 6,8 pontos a menos") e ordem aleatória 23,2%; sem as negociações que nunca fecharam na base, 78,1% contra 79,1%, com a conclusão "Sem elas, "Só valor de tabela" rende 1,0 ponto a mais que a regra atual…"; "O que esta evidência não mostra". Na técnica: Val@10, Δ com IC95%, P@10, Lift@10 e AUC | Os números vêm do resultado gravado do backtest e são os mesmos nas duas linguagens; a armadilha de vazamento não aparece |

## 3. Funcionalidades P0

**P0-1 · Carteira classificada.** Origem: F-03, F-04, F-05 e a guarda de F-06; RD-02 a RD-04, RD-07; ADR-001 e ADR-002.
- **Descrição:** carrega, normaliza e junta os CSVs; põe cada aberta em exatamente um grupo, com motivo.
- **Entradas:** `sales_pipeline`, `products`, `sales_teams` e `accounts` em `data/raw/`. Política: `as_of` (padrão `max(close_date)` = 2017-12-31), percentil do primeiro limite (90) e faixas de valor.
- **Saídas:** abertas com identificação, idade, faixa, grupo e motivo; `meta` (`as_of`, os dois limites, o percentil, SHA-256); relatório de reconciliação.
- **Lógica (regra A, Revisão 4):** `GTXPro` → `GTX Pro`; junções m:1 mantêm 8.800 linhas. Dois limites só com fechadas até o `as_of`: L1 = piso do P90 do ciclo das ganhas (hoje 106 d) e L2 = maior ciclo fechado (hoje 138 d). Focar = Engaging com idade ≤ L1; Acompanhar = Engaging acima de L1 e até L2; Revisar = Engaging acima de L2; Qualificar = Prospecting; Não pontuável = falta um campo necessário. Sem venda ganha até o `as_of` → erro `no_won_history`. Só campos permitidos entram; `close_date` só entra nos limites. Função pura (`triage.engaging_group`, a mesma do backtest); CSV só leitura.
- **Dados ausentes:** arquivo, coluna, rótulo ou estágio inválido → erro explícito, nunca descarte; produto vazio ou Engaging sem data → Não pontuável; conta vazia → só o aviso (AC-1.2 a 1.8).
- **Pronto quando:** AC-1.x verdes, reconciliação 8.800/2.089 publicada e saída determinística.

**P0-2 · Lista "Onde focar" por vendedor.** Origem: F-01 e F-04; RB-04, RB-06, RD-06, RE-02, Q-01; ADR-001 e ADR-003.
- **Descrição:** a carteira de um vendedor em ordem única e declarada, com resumo por estado.
- **Entradas:** saída de P0-1, `seller` e `as_of`; `manager` e `office` na API e na página Equipe.
- **Saídas:**
  - `GET /api/meta`;
  - `/api/sellers` (ordem alfabética);
  - `/api/sellers/{seller}/pipeline?as_of=` (`summary`, `ordering`, `empty` e grupos com itens, `empty` e `next_action`, em códigos; ver ADR-004);
  - `/api/pipeline?manager=&office=`, com `by_seller`;
  - `/api/rules` e `/api/evidence` (Revisão 3);
  - páginas Next.js com menu central (Carteira, Equipe, Evidência e Como funciona; ADR-005), e a Inteligência na Revisão 5 (ADR-007);
  - CLI `python -m leadscorer list`.
- **Lógica:** grupo → faixa de valor de tabela (alto ≥ 3.000; médio de 500 a 2.999; baixo < 500) → preço decrescente → ID, só para estabilidade. Dentro do grupo, a idade é coluna; mesmo grupo e produto é empate (a ordem entre eles é só pelo código, e a tabela não os destaca); vendedores nunca são ordenados. A ordem vai no payload como dado (`ordering`), e a CLI e a Equipe (na Carteira, desde a Revisão 8, só em Como funciona) escrevem acima da lista a legenda "Ordem: Focar → Qualificar → Acompanhar → Confirmar → Completar; em cada grupo, maior valor de tabela primeiro; a idade aparece, mas não muda a ordem." Faixas e percentil são política provisória (U-06).
- **Dados ausentes:** vendedor inexistente → 404; vendedor sem abertas (8), grupo vazio ou filtro vazio → mensagem própria; Focar vazio (10 vendedores, todos começam por Qualificar, ADR-009) aponta o próximo grupo com oportunidades; conta nula → "sem cliente registrado" (AC-2.4 a 2.7 e 2.10).
- **Pronto quando:** AC-2.x verdes, CLI igual à API e a jornada rodando sem intervenção.

**P0-3 · "Por que está aqui".** Origem: F-02 e a frase mínima de F-09; RB-03, RE-04, RD-01, RD-05, RJ-07.
- **Descrição:** explica cada posição com frases de modelo fixo, preenchidas com campos, e dá o próximo passo.
- **Entradas e saídas:** linha e `meta` de P0-1 → `reasons: [{code, role, params}]` e `next_action: {code, params}` na API. A tela (`copy/pt-BR.ts`) e a CLI (`cli_text.py`) escrevem as frases (ADR-004).
- **Lógica:** sem LLM. Exatamente dois motivos, os que decidiram (Revisão 4):
  - **grupo** (`role: group`): idade × L1 (`age_within_won_cycle`), idade entre L1 e L2 (`age_above_won_cycle`), idade × L2 (`age_above_cycle_limit`), estágio Prospecting ou campo ausente;
  - **ordem** (`role: order`): faixa e preço de tabela.
  - Os motivos de contexto (P90 por produto e taxa das fechadas) saíram: não decidem, e o P90 por produto seria um segundo "P90", diferente do que decide.
- **Frases da tela e da CLI:**
  - "Focar porque está aberta há X dias; 90% das vendas ganhas fecharam em até 106 dias.";
  - "Acompanhar porque está aberta há X dias: mais do que 90% das vendas ganhas levaram (106 d), sem passar da venda mais longa já fechada (138 d).";
  - "Confirmar porque está aberta há X dias, mais do que qualquer venda já fechada aqui (138 d).";
  - "Qualificar porque ainda está em prospecção" e "Completar porque falta <campo>";
  - "preço de catálogo, não valor negociado";
  - nota fixa: "O sistema só vê datas, produto e preço de tabela: não vê ligações, reuniões nem e-mails."
- **Duas frases corrigidas na Revisão 2,** porque diziam mais do que o código:
  - "ainda não tem data de engajamento" virou "ainda está em prospecção";
  - "e isso não diferencia uma da outra" saiu.
- **O que verificar agora** (Revisão 6; códigos `check_status`, `check_progress`, `confirm_still_active`, `check_prospecting` e `fix_missing_field`; os três primeiros levam `has_account`; o texto é da tela e da CLI): Focar, "Consulte no CRM o andamento da negociação com <conta>." (sem conta, "…o andamento e a conta desta negociação."). Acompanhar, "Consulte no CRM o último registro da negociação com <conta>." Confirmar, "Verifique no CRM se a negociação com <conta> continua: o tempo aberta não prova que ela terminou." Qualificar, "Em prospecção, sem data de início: verifique no CRM se já houve engajamento e registre a data quando houver." Completar, "Corrija <campo> no CRM." Na ação do grupo, que não tem conta, `has_account` é nulo e a frase é genérica ("…de cada negociação"). Focar vazio cita só o limite que importa para o grupo indicado (`has_engaging` diz se há Engaging acima de L1): "Nenhuma aberta há até 106 dias. Comece por Qualificar: …" (ou por Acompanhar), "Todas as negociações em andamento estão abertas há mais de 138 dias. Comece por Confirmar: …" ou "Nenhuma negociação em andamento. Comece por Qualificar: …". Vocabulário proibido: AC-3.8.
- **Dados ausentes:** sem idade → nenhuma idade inventada; conta nula → só o aviso do cabeçalho (AC-3.3).
- **Pronto quando:** AC-3.x verdes e 100% dos itens explicados.

**P0-4 · Inteligência comercial (Revisão 5).** Origem: F-08 (resumo descritivo), HD-04, HD-07 e HD-08; RD-06, RJ-02 e RJ-03; [ADR-007](./architecture.md#adr-007).
- **Descrição:** uma página para a Head de RevOps ver onde o processo comercial falha, o que melhorar e o que explica a receita. A Carteira continua a página principal: a Inteligência não pontua nem ordena oportunidades.
- **Entradas:** os mesmos 4 CSVs; a carga passa a trazer `close_value` e, de `accounts`, setor, receita anual e sede (fora do frame da classificação). Filtros por produto, vendedor, gerente, escritório, setor, cliente e porte do cliente (quartis da receita anual).
- **Saídas (`/api/intelligence`):** histórico das fechadas (receita, ganhas, perdidas, taxa com faixa provável, ticket, ciclos); carteira aberta com os grupos da regra (o mesmo recorte da Equipe); diagnósticos e descobertas em código e params; um recorte por dimensão com teste de acaso e decomposição da receita; mix vendedor × produto; faixas de ciclo terminadas em L1 e L2; ritmo mensal. `/api/intelligence/deals` devolve as negociações por trás de um número.
- **Lógica:** taxa = ganhas ÷ fechadas, com Wilson 95%; teste de acaso por qui-quadrado nos segmentos com pelo menos 20 fechadas, com α = 0,05 ÷ 7 dimensões; decomposição da receita em volume × taxa × ticket pela variância do log, com pelo menos 4 segmentos; diagnósticos e descobertas por regras fixas com limites em `policy.py`.
- **Dados ausentes:** abertas sem cliente saem dos recortes de setor, cliente e porte, e a página diz quantas; nenhum dado ausente vira "baixo potencial".
- **Pronto quando:** AC-6.x verdes e a etapa 6 da jornada.

**P0-5 · Priorização assistida pelo vendedor (Revisão 11).** Origem: persona do vendedor sobrecarregado (Darcel) e do iniciante (Boris): "tenho várias oportunidades empatadas, por qual começo?"; RD-06, RJ-02; [ADR-010](./architecture.md#adr-010).
- **Descrição:** o vendedor responde 7 perguntas sobre 2 a 5 oportunidades empatadas (ou sobre uma) e recebe uma ordem sugerida de trabalho por pontos de qualificação declarada, com a explicação de cada ponto. É uma camada separada do scoring: usa só o que o vendedor declara e nada do que o backtest validou.
- **Entradas:** as oportunidades empatadas da carteira (`tie_size`, mesmo grupo e produto), as respostas do vendedor e `meta.as_of` como "hoje".
- **Saídas:** pontos confirmados e potencial (0 a 100), quebra por pergunta, categoria de trabalho, lacunas, orientação e ordem; resumo e plano para copiar. Tudo calculado no navegador e guardado só nele.
- **Pronto quando:** AC-7.x verdes. O teste de compreensão com vendedores reais (README, "Para escalar") **não foi feito**: pesos e pontos seguem como hipótese.

**Fora do escopo:** F-07, F-10 a F-13, RJ-01 a RJ-07, escrita no CRM e envio por Slack ou e-mail. F-08 volta como P0-4 (Revisão 5). F-07 inclui o registro de eventos de uso (RD-08): a ferramenta não registra uso, e só a priorização assistida guarda respostas, no navegador do vendedor.

## 4. Dados, dependências, comandos e riscos

**Dados:** os quatro CSVs do Kaggle (CC0) em `solution/data/raw/`, conferidos pelo SHA-256 de [`A§7`](./data-audit.md#a-7); demonstração com Zane Levy, Darcel Schlecht (sem Focar nem Acompanhar) e Carl Lin (sem abertas). Testes unitários usam fixtures sintéticas; o e2e usa os CSVs reais e é pulado com aviso se eles faltarem.

**Oráculos:** os números e registros de AC-1.1, AC-1.8, AC-2.1, AC-2.4, AC-3.1 e AC-3.3 foram conferidos nos CSVs em 15/10/2026, por consulta fora do repositório (ver Limites em [architecture.md](./architecture.md#limites)).

**Dependências:** Python 3.9.6 com pandas 2.2.3 e numpy 2.0.2; FastAPI, pydantic, uvicorn, pytest e httpx fixados na fatia 0; scipy no backtest e no teste de acaso da Inteligência; scikit-learn só na auditoria dos dados; Node 22.12 e npm 11.5 com Next.js e lockfile; no front, TypeScript 6, zod 4, Vitest 5 (com Vite 7), jsdom 28 e `@hey-api/openapi-ts` 0.95, que gera tipos e validação do contrato. A interface (Revisão 3) acrescenta:
- Tailwind 4.3 e os componentes do shadcn, que entram pela CLI 4.21.1 via `npx`, sem virar dependência;
- Radix, `cn`, lucide, next-themes e cmdk;
- Recharts 3.10, só no gráfico da Evidência. Sem banco, sem segredo, sem LLM e sem rede em execução.

**Comandos do avaliador** (em `submissions/alice-dantas/solution/`):

```bash
# 0. Baixar o dataset no Kaggle pelo navegador e copiar os 4 CSVs para data/raw/
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m leadscorer check-data          # presença, colunas, hash e reconciliação
.venv/bin/pytest
.venv/bin/uvicorn api.main:app --port 8000
cd web && npm ci && npm run dev                    # http://localhost:3000
cd web && npm run typecheck && npm test            # testes do front, sem a API no ar
.venv/bin/python -m leadscorer list --seller "Zane Levy"   # caminho sem Node
.venv/bin/python scripts/backtest.py               # regrava a evidência servida em /api/evidence
# Se o contrato mudar: export_openapi.py, export_fixtures.py e, em web/, npm run contract
```

| Artefato | Risco | Regra |
| --- | --- | --- |
| CSVs brutos | Ficam fora do PR, mas `git add -f` os incluiria, e o [commit-flow](./commit-flow.md) não filtra `.csv` | Excluir `data/raw/*.csv` no `git add` e na etapa 5; publicar `data/raw/README.md` com link e SHA-256 |
| `outputs/` da CLI | Republica o dataset linha a linha | Fora do PR; fixtures só sintéticas |
| `audit_log.txt` | Traz caminho absoluto local (`/Users/...`) | Trocar por caminho relativo |
| Credenciais | Token do Kaggle; `.env` do Next.js | Download pelo navegador; URL da API com padrão no código |
| Artefatos locais | `.venv` (206 MB), `node_modules`, `.next`, `.pytest_cache` | Acrescentar `.next` e `.pytest_cache` ao commit-flow |

## 5. Métricas

| Testável hoje | Como | Critério |
| --- | --- | --- |
| Execução | Setup do zero pelo README | Nenhum passo fora do README |
| Funcionalidade | pytest, `npm test`, `npm run typecheck` e a jornada da seção 2 | 100% verde; jornada em até 2 min |
| Lógica | Partição, reconciliação, `as_of`, invariância, códigos e textos | Bate com os oráculos |
| Contrato | Schema tipado, snapshot e respostas sintéticas atualizados; validação no front | AC-4.1 a 4.8 |
| Interface | Contraste dos tokens, só primitivos do shadcn, navegação, Carteira, painel, Equipe, Inteligência, Evidência e Como funciona; roteiro em 375 px e nos dois temas | AC-5.1 a 5.9 |
| Inteligência | Oráculos nos CSVs, somas que fecham, mesma política da Equipe, regras de diagnóstico e descoberta, textos com números só dos params, arranjo da página | AC-6.1 a 6.12 |
| Ranking offline válido | Backtest em 7 cortes com todas as Engaging abertas em T e desfecho em 90 dias, só com o que se sabia em cada corte; AUC com IC; P@10, Lift@10 e Val@10 por vendedor, com IC por bootstrap de vendedores; sensibilidade sem as negociações que nunca fecham | Sem vazamento e reprodutível; produto e preço perto de 0,5; a vantagem da idade é reportada junto com a sensibilidade; a armadilha do mês de fechamento só funciona com o campo proibido |
| Compreensão | 3 a 5 pessoas não técnicas: "quais 3 você abre, e por quê?" | 4 de 5 explicam a posição e o limite da ferramenta (**não executado**; README, "Para escalar") |

**Só em piloto** (exige F-07 e grupo de controle, F-13): adoção semanal; % de deals trabalhados que estavam em Focar; horas economizadas e tempo para decidir o foco; conversão e valor ganho com e sem a ferramenta; % de Revisar resolvidos em 30 dias. Nenhuma dessas métricas pode ser afirmada com o dataset.

## 6. Backlog por fatias

Cada fatia termina com os seus testes verdes.

0. **Ambiente:** dependências em venv limpo e Next.js; versões fixadas; `data/raw/README.md`; ajuste do commit-flow.
1. **P0-1a:** carga e contrato (AC-1.1 a 1.5).
2. **P0-1b:** estados, guarda de campos e invariância (AC-1.6 a 1.11).
3. **P0-2a:** ordenação, legenda e CLI; o P0 já pode ser entregue sem web (AC-2.1 a 2.3 e 2.11).
4. **P0-3:** explicação no núcleo (AC-3.1 a 3.9).
5. **P0-2b:** API, com a CLI igual à API (AC-2.4 a 2.10).
6. **P0-2c:** tela e ensaio cronometrado da jornada (AC-2.12).
7. **Validação offline:** backtest, armadilha e scripts das consultas diretas (publica o que a consulta direta conferiu).
8. **Entrega:** README, process log e commit.
9. **Contrato (Revisão 2, ADR-004):**
   - schemas tipados;
   - códigos no back;
   - catálogos de texto na tela e na CLI;
   - payload sem texto (AC-4.1 a 4.4).
10. **Interface (Revisão 3, ADR-005):**
    - design system: tokens, shadcn e tema claro e escuro;
    - navegação central e Carteira com cartão, abas e painel;
    - Equipe;
    - contrato v4 (evidência, regras e resumo por vendedor);
    - Evidência e Como funciona (AC-4.5, AC-4.6 e AC-5.x).
11. **Inteligência comercial (Revisão 5, ADR-007):**
    - carga com `close_value` e atributos do cliente; recorte compartilhado com a Equipe (`views.scope`);
    - `leadscorer/intelligence.py` e as duas rotas (contrato v6);
    - página `/inteligencia` (AC-4.8 e AC-6.x).

**Decisões desta versão:** **D-1** os seis P0 da arquitetura viram três, e o backtest de F-06 vira evidência (fatia 7). **D-2** os CSVs ficam fora do PR. **D-3** as 4 a 6 h são estimativa, sem gatilho de tempo (fecha a falha 4 do PL-021). **D-4** o `as_of` mínimo é `max(close_date)`; o cenário com `as_of` 2017-12-27 (o maior `engage_date`; Focar 351) sai do aceite, porque tira da carteira deals que só fecharam depois do `as_of`. **D-5** rótulo de produto desconhecido gera erro; produto vazio vira Não pontuável. **D-6** (Revisão 2):
- o back entrega códigos, e o texto é da tela e da CLI;
- `contract_version` 3 sinaliza a saída dos campos de texto;
- as duas frases que diziam mais do que o código foram corrigidas.

**D-7** (Revisão 3):
- **Interface:** só componentes do shadcn, com tokens medidos na peça de marca e menu central, sem sidebar.
- **Dados das páginas novas:** os números de Equipe, Evidência e Como funciona vêm da API (`contract_version` 4); a tela só formata.
- **Evidência:** é o resultado gravado de `scripts/backtest.py`, sem a armadilha de vazamento.
- **Por vendedor:** a tabela abre em ordem alfabética e pode ser ordenada por qualquer coluna, só para consulta (AC-2.9).

**D-8** (Revisão 4, [ADR-006](./architecture.md#adr-006)):
- **Regra A no lugar do corte único:** as duas regras por idade dependem das negociações que nunca fecham; no pior caso, a regra A perde menos (−1,0 contra −1,5 pp), e ela tira do topo de Focar as negociações velhas e caras.
- **Prospecting continua depois das Engaging:** o backtest não o avalia, então a posição não muda.
- **Contrato v5:** back, CLI e tela mudam juntos; a explicação fica só com o que decide.

**D-9** (Revisão 5, [ADR-007](./architecture.md#adr-007)):
- **Inteligência descritiva:** diagnósticos e descobertas por regras determinísticas, em código e params; sem modelo preditivo e sem texto gerado por LLM.
- **Pessoas:** ordem alfabética, decomposição só no nível da dimensão, sem gráfico nem índice por pessoa; a matriz vendedor × produto mostra volume e mix, nunca taxa por célula.
- **Cruzamentos (Revisão 6):** abaixo da tabela de resultados, um seletor "Cruzar" troca entre seis tabelas de fechadas com a fatia de cada coluna e sem taxa por célula: o que cada vendedor vende, o que cada cliente compra, o que cada setor compra, quem cada vendedor atende (por setor) e a relação de setor e de país da sede do cliente com o escritório do vendedor. A API devolve `crosstabs` (as cinco novas) ao lado de `matrix`; clicar numa célula abre as negociações do recorte (exceto país da sede, que não é filtro da página).
- **Tabela de resultados (Revisão 6):** as colunas Ganhas e Perdidas ficam ao lado de Fechadas em todas as dimensões; cada título de coluna tem tooltip explicando o que mostra; o rodapé vira dois blocos ("A taxa de ganho muda de verdade entre…?" e "De onde vem a diferença de receita"), com o texto longo em popover. "Sem venda" passa a "Perdida(s)" nos rótulos de resultado de negociações já fechadas (nunca para abertas); setores, países de sede e escritórios aparecem em português, e a chave original segue na URL e na API.
- **O que a ordem não usa (Revisão 6):** a taxa de ganho do vendedor por produto (mediana de 30 fechadas por combinação, metade com menos de 30; a taxa da primeira metade do histórico não prevê a da segunda, correlação de 0,04) e o tempo típico de ganho do cliente (cada cliente tem de 23 a 115 ganhas, mas o ciclo varia dentro do cliente tanto quanto entre todos, desvio de 41 dias nos dois, e o ciclo típico de um cliente não se repete entre as duas metades do histórico, correlação de −0,16). Explicado em Como funciona, no cartão "O que a ordem não usa, e por quê". Os números vêm de uma análise única sobre os CSVs; não estão no payload.
- **Sem filtro de período e sem matriz de venda cruzada:** os meses não são comparáveis (fim de trimestre), e 73 de 85 clientes já compraram 6 dos 7 produtos.
- **Contrato v6:** duas rotas novas; a tela só formata.

---

## Tabela de critérios de aceite

Fixture = arquivo sintético de teste. Os demais casos rodam nos CSVs reais com `as_of` 2017-12-31, salvo indicação.

| ID | P0 | Caso | DADO | QUANDO | ENTÃO |
| --- | --- | --- | --- | --- | --- |
| AC-1.1 | P0-1 | Sucesso | os 4 CSVs com o hash auditado | `check-data` roda | 8.800 linhas após cada junção, 0 preço nulo e 2.089 abertas = 157 + 141 + 1.291 + 500 + 0; L1 = 106 d e L2 = 138 d; Focar com 69/56/32 por faixa |
| AC-1.2 | P0-1 | Arquivo ausente | sem `products.csv` em `data/raw/` | a carga roda (CLI ou API) | erro com o nome do arquivo, a pasta esperada e o passo de download; nenhuma lista parcial; API com status 503 e a mesma mensagem |
| AC-1.3 | P0-1 | Arquivo inválido | `sales_pipeline.csv` vazio, que não seja CSV ou sem a coluna `engage_date` | a carga roda | erro com o arquivo e as colunas faltantes; nenhuma lista parcial |
| AC-1.4 | P0-1 | Contrato de rótulo | fixture com o produto `GTX Ultra`; e, à parte, a carga sem o mapa de normalização | a carga roda | erro lista o rótulo e as IDs, sem descarte; sem o mapa, 1.480 não casadas, e com o mapa, 0 |
| AC-1.5 | P0-1 | Arquivo divergente | CSVs com schema válido e SHA-256 diferente do auditado | a carga roda | `meta.audited` falso; a tela e a CLI mostram o aviso "dados diferentes da versão auditada"; os oráculos deixam de ser garantidos |
| AC-1.6 | P0-1 | Campo nulo | fixture com uma Engaging sem `engage_date` e uma aberta sem `product` | a classificação roda | as duas em Não pontuável, com os motivos "sem data de engajamento" e "sem produto"; a soma dos estados é igual ao total |
| AC-1.7 | P0-1 | Campo nulo (conta) | as 1.425 abertas sem conta | a classificação roda | o estado e a ordem são iguais aos da mesma linha com conta; a conta só alimenta o aviso |
| AC-1.8 | P0-1 | Valor extremo | `as_of` 2018-01-31, 2018-03-31 e 2030-01-01; depois `2017-12-30` e `31/12/2017` | a classificação roda | Focar 84, 9 e 0 e Acompanhar 76, 25 e 0, sempre com 2.089 na partição e L1 = 106 d; os dois últimos dão erro de validação com o mínimo aceito e o formato AAAA-MM-DD |
| AC-1.9 | P0-1 | Fronteira | fixture com ganhas de 10 e 110 d (L1 = 100) e maior ciclo de 138 d; Engaging de 100, 101, 138 e 139 dias; à parte, ganhas de 10 e 115 d (P90 = 104,5) | a classificação roda | 100 d em Focar, 101 e 138 d em Acompanhar, 139 d em Revisar; com P90 = 104,5, L1 = 104 (o piso) e 105 d vai para Acompanhar |
| AC-1.10 | P0-1 | Vazamento | linhas, `opportunity_id` e `close_value` das fechadas embaralhados; uma Won extra com `close_date` > `as_of` | a classificação roda | nenhum grupo, faixa ou ordem muda; os limites continuam em 100 e 138 d (a Won futura não entra em L1) |
| AC-1.11 | P0-1 | Determinismo | a mesma entrada e a mesma política | duas execuções | saídas com o mesmo hash |
| AC-1.12 | P0-1 | Sem histórico (Revisão 4) | fixture sem nenhuma venda ganha até o `as_of` | a carga roda (API ou CLI) | 503 com `code` = `no_won_history` e o `as_of`; a CLI sai com erro e sem lista; nenhum limite inventado |
| AC-2.1 | P0-2 | Sucesso | Zane Levy | a lista é pedida | 88 = 13 + 18 + 57 + 0 + 0 em `summary`; Focar na ordem alto (4) → médio (7) → baixo (2), com `01XZ9CRY` e `FZWU2I30` empatadas no topo; na mesma faixa, preço decrescente e depois ID; `ordering` traz grupos focar → qualificar → acompanhar → revisar → nao_pontuavel, dentro do grupo faixa → preço → ID, com `age_affects_order` falso; a CLI e a Equipe escrevem a partir dele a legenda (na Carteira ela saiu na Revisão 8) "Ordem: Focar → Qualificar → Acompanhar → Confirmar → Completar; em cada grupo, maior valor de tabela primeiro; a idade aparece, mas não muda a ordem." |
| AC-2.2 | P0-2 | Ordem declarada (a idade não ordena) | deals do mesmo estado e produto, com `engage_date` embaralhada entre eles | a lista é pedida | a ordem não muda; a idade aparece como coluna em Focar, Acompanhar e Revisar |
| AC-2.3 | P0-2 | Empate | 2 ou mais deals com o mesmo estado e produto | a lista é exibida | `tie_size` > 1; a tela e a CLI os agrupam como "N oportunidades empatadas (…): sem ordem entre si" (a contagem é das linhas mostradas) |
| AC-2.4 | P0-2 | Resultado vazio (grupo) | Darcel Schlecht | a lista é pedida | grupo focar com `empty` = `start_with_group` apontando para qualificar, que tem itens (L1 = 106 e L2 = 138 no `meta`); a CLI escreve "Nenhuma aberta há até 106 dias. Comece por Qualificar: …" e a tela abre na aba Qualificar; 111 Qualificar e 83 Confirmar visíveis. Os 10 vendedores com Focar vazio começam todos por Qualificar (Revisão 7); se Qualificar também estiver vazio, o ponto de partida é o próximo grupo com itens (Acompanhar, depois Confirmar) |
| AC-2.5 | P0-2 | Resultado vazio (vendedor) | Carl Lin, sem abertas | a lista é pedida | status 200, resumo zerado e `empty.code` = `no_open_for_seller`; a tela e a CLI mostram "Nenhuma oportunidade aberta para este vendedor" |
| AC-2.6 | P0-2 | Entrada inválida | `seller=Fulano` | a API é chamada | 404 com `code` = `seller_not_found` e `params.seller`; a tela só oferece nomes de `sales_teams` |
| AC-2.7 | P0-2 | Campo nulo | linha sem conta | a lista é exibida | `account` nulo, contado em `summary.without_account`; a tela e a CLI mostram ID, produto, `engage_date` e "sem cliente registrado", e o aviso de conta, uma vez, no cabeçalho da CLI e da Equipe (na Carteira, desde a Revisão 8, só a marca em cada linha) |
| AC-2.8 | P0-2 | Contrato | qualquer vendedor e `as_of` válido | API e CLI são comparadas | itens, ordem e contagens idênticos; a soma dos 35 vendedores é 2.089; toda resposta passa pelo modelo tipado de `api/schemas.py` |
| AC-2.9 | P0-2 | Sem ranking de pessoas | `GET /api/sellers` e `by_seller` de `/api/pipeline` | a lista é pedida | ordem alfabética nos dois; nenhuma tela ou endpoint ordena vendedores por resultado; a tabela "Por vendedor" abre em ordem alfabética e o gerente pode ordenar por coluna na tela (consulta; a API e a ordem inicial não mudam, e nenhuma coluna pontua pessoas) |
| AC-2.10 | P0-2 | Filtro vazio | `manager` inexistente ou combinação sem abertas | o filtro é aplicado | lista vazia com `empty.code` = `no_open_for_filter`; nunca 500 |
| AC-2.11 | P0-2 | Valor extremo | `as_of` 2030-01-01 | a lista de qualquer vendedor é pedida | grupos focar e acompanhar vazios e todas as Engaging em Revisar |
| AC-2.12 | P0-2 | Tela (roteiro manual, fatias 6 e 10) | API e tela no ar com os CSVs auditados | a jornada da seção 2 é seguida | Aparecem: "Dados até 31/12/2017" no cabeçalho; o cartão "O que verificar agora" com o empate de `01XZ9CRY` e `FZWU2I30`; o título "Suas oportunidades" com 88 abertas e as cinco abas com contagem (13 + 18 + 57 + 0 + 0) e Focar ativa; o painel de `01XZ9CRY` com os dois motivos e o que verificar; Darcel abrindo em Qualificar, com 13 empatadas no topo; Equipe com 2.089 = 157 + 141 + 1.291 + 500 + 0 e a Evidência com 58,4% e 53,8% e a conclusão do recorte sem as que nunca fecham. A lista aparece em menos de 1 s após escolher o vendedor; nenhum erro; jornada do vendedor em até 2 min |
| AC-2.13 | P0-2 | Equipe: leitura e reunião | filtro de gerente cujo Focar é 0; aba "Por vendedor" | a Equipe é aberta | o cartão Focar diz "Nenhuma aberta há até N dias" e que isso não significa equipe sem boas oportunidades; "Copiar tabela" leva todos os vendedores do filtro, separados por tabulação, sem chamar o servidor; a tabela de oportunidades quebra linha nas colunas de texto e cabe sem rolagem horizontal em 768 px (em 375 px rola dentro do cartão, sem estourar a página) |
| AC-2.14 | P0-2 | Leitura de vazio e de decomposição | vendedor sem abertas; decomposição da receita com fatia negativa ou acima de 100% | a Carteira ou a Inteligência é aberta | a Carteira vazia diz que a base não registra abertas no nome do vendedor e manda conferir o cadastro no CRM; quando alguma fatia (fora as marcadas como desprezíveis) sai de 0 a 100%, o texto diz que os fatores se compensam e não mostra porcentagens, sem mudar o contrato |
| AC-2.15 | P0-2 | Focar não é chance; estatística em palavras | grupo Focar; indicadores e veredito de taxa de ganho da Inteligência | a Carteira ou a Inteligência é aberta | a descrição do Focar diz que é sobre o tempo aberta, não sobre a chance de fechar; a faixa da taxa de ganho diz "onde a taxa de ganho real provavelmente está"; o veredito diz que a diferença poderia (ou dificilmente poderia) aparecer se os recortes fossem iguais; o indicador de ciclo se chama "Tempo típico até ganhar"; números e contrato inalterados |
| AC-2.16 | P0-2 | Faixas de valor ao alcance | Carteira com oportunidades em faixas de valor | a lista é aberta | cada título de faixa de valor (alto, médio, baixo) traz o link "ver as faixas em Como funciona", que leva a `/como-funciona`; a faixa sem valor de tabela não tem o link; ordem, contrato e API inalterados |
| AC-3.1 | P0-3 | Explicação da prioridade | a Focar `01XZ9CRY` (GTX Plus Pro, Initech, engajada em 2017-09-18) | o painel é aberto | exatamente dois `reasons`: `age_within_won_cycle` (104 d, L1 = 106 d, 90%) e `list_price` (5.482, alto); `next_action` = `check_status` com `has_account` verdadeiro. A tela e a CLI mostram "Focar porque está aberta há 104 dias; 90% das vendas ganhas fecharam em até 106 dias.", "valor de tabela 5.482 (valor de tabela alto)" e "Consulte no CRM o andamento da negociação com Initech."; o painel traz também a idade no contexto do histórico (mediana, L1 e L2 das ganhas) e o aviso de que o sistema não registra atividades, estágio nem contatos (Revisão 6) |
| AC-3.2 | P0-3 | Acompanhar e Revisar | uma Acompanhar (`J0G6ZLYZ`, 120 d) e uma Revisar | o painel é aberto | Acompanhar: motivo `age_above_won_cycle` com a idade e os dois limites, `next_action` = `check_progress`. Revisar: `age_above_cycle_limit` com a idade e L2, `next_action` = `confirm_still_active`, texto "Verifique no CRM se a negociação … continua", sem "perdida", "encerre", "prazo" nem "parada" |
| AC-3.3 | P0-3 | Campo nulo | a Qualificar `28EJ0L9T` (GTX Plus Pro, sem cliente, sem data) | o painel é aberto | motivo `prospecting_stage` (a regra é o estágio) e o de ordem; nenhuma idade inventada; texto "Qualificar porque ainda está em prospecção"; `next_action` = `check_prospecting` |
| AC-3.4 | — | Retirado na Revisão 4 | — | — | A referência de ciclo por produto saiu da explicação ([ADR-006](./architecture.md#adr-006)): não decide, e seria um segundo "P90" |
| AC-3.5 | — | Retirado na Revisão 4 | — | — | Idem; um produto sem ganhas não muda nada, porque L1 é um número só para todos os produtos |
| AC-3.6 | P0-3 | Não pontuável | item Não pontuável da fixture | o painel é aberto | motivo `missing_field` com o campo; `next_action` = `fix_missing_field`; texto "Corrija <campo> no CRM" |
| AC-3.7 | P0-3 | Verificabilidade | os 2.089 itens | os testes comparam códigos, valores e textos | exatamente dois motivos (grupo e ordem), que citam os valores que decidiram e, sozinhos, reconstroem o grupo e a ordem (back); todo número das frases da tela e da CLI vem dos parâmetros do código ou do `meta` (front e CLI) |
| AC-3.8 | P0-3 | Vocabulário | os catálogos de texto da tela e da CLI e tudo o que eles mostram | os testes varrem os textos | nenhuma palavra começa por um termo proibido (lista única, exportada do back para a tela; inclui "prazo", "vence", "atrasad", "parad", "inativ" e "chance zero"); faixas só com "de tabela"; o payload não traz texto de tela |
| AC-3.9 | P0-3 | Resultado vazio | um grupo vazio | a tela é exibida | `empty` = `group_empty` e só a mensagem do grupo, sem painel de explicação vazio |
| AC-4.1 | Contrato | Schema | as 8 rotas | o `openapi.json` é gerado | toda resposta e todo erro têm modelo tipado, sem objeto solto; o snapshot em `web/contract/` e as respostas sintéticas em `web/tests/fixtures/` estão atualizados |
| AC-4.2 | Contrato | Resposta fora do contrato | código desconhecido, tipo errado ou campo obrigatório ausente | a tela recebe a resposta | a validação zod recusa e a tela mostra a mensagem de erro; campo novo é tolerado |
| AC-4.3 | Contrato | Cobertura de textos | todos os códigos do contrato | os testes dos catálogos rodam | cada código tem texto na tela e na CLI; um código novo sem texto quebra o `typecheck` (tela) e o `pytest` (CLI) |
| AC-4.4 | Contrato | Sem texto no payload | qualquer resposta | o payload é inspecionado | nenhum campo de texto pronto (`legend`, `label`, `explanation`, `next_step`, `empty_message`…); `meta.contract_version` = 7 |
| AC-4.5 | Contrato | Evidência | o resultado gravado do backtest (`data/processed/backtest_results.json`) | `GET /api/evidence` é chamado | as 7 estratégias em código, na ordem do relatório, sem a armadilha de vazamento; `reference` = `age_p90_then_max_cycle` (a servida); Val@10 de 0,584 (servida), 0,569 (regra anterior, delta −0,015, IC −0,027 a −0,002) e 0,538 (só valor de tabela, delta −0,046, IC −0,068 a −0,025); sem as que nunca fecham, 0,781 contra 0,791, com `without_no_outcome_verdict` = `reference_behind` (só valor de tabela, +0,010, IC +0,003 a +0,019); responde sem os CSVs; arquivo ausente, inválido ou com outro `design.served_rule` → 503 com `code` = `evidence_unavailable` |
| AC-4.6 | Contrato | Regras e resumo por vendedor | os CSVs auditados | `GET /api/rules` e `GET /api/pipeline` são chamados | `rules` traz `meta`, `ordering` e as faixas (alto a partir de 3.000; médio de 500 a 2.999; baixo até 499), iguais à política; `by_seller` traz os 35 vendedores em ordem alfabética, 8 com zero abertas, com somas iguais ao `summary` (2.089); com filtro, só os vendedores do filtro |
| AC-4.7 | Contrato | Mesma política (Revisão 4) | os CSVs auditados e as fixtures | os testes comparam as saídas | núcleo, API, CLI, carteira da equipe, detalhe e regras servem a mesma lista e o mesmo `meta`; grupos e ações do contrato saem da política; o backtest reproduz a ordem servida em cada um dos 7 cortes |
| AC-4.8 | Contrato | Inteligência (Revisão 5) | `GET /api/intelligence` e `GET /api/intelligence/deals` | as rotas são chamadas | resposta igual ao núcleo; diagnósticos e descobertas em uniões por `code`, com os mesmos códigos no núcleo, no schema e no catálogo; todo parâmetro chega como texto e é validado no núcleo; `outcome` ou `group` inválido → 422 com `code` = `invalid_parameter`; valor de filtro desconhecido → 200 com recorte vazio; `close_value` ou receita do cliente que não seja número → 503 com `code` = `data_bad_number` |
| AC-5.1 | Interface | Tokens | `web/app/globals.css` | `tokens.test.ts` roda | todo par de texto com contraste ≥ 4,5 : 1 nos temas claro e escuro; o lilás da marca `#8091FA` igual nos dois |
| AC-5.2 | Interface | Só shadcn | as composições em `app/` e `components/` (fora de `ui/`) | `design-system.test.ts` roda | nenhum `<button>`, `<table>`, `<select>`, `<input>` ou `<details>` cru, nenhuma cor literal e nenhum `style` inline; a regra de cursor de clique (botões, links, abas, opções, combobox) fica fora de `@layer`, para valer sobre os utilitários |
| AC-5.3 | Interface | Navegação | qualquer página | o cabeçalho é exibido | os 5 itens do menu central (Inteligência entre Equipe e Evidência, Revisão 5), com `aria-current="page"` na página ativa; `/` leva a `/carteira`; sem sidebar |
| AC-5.4 | Interface | Carteira | fixtures de Ana Alfa, Bruno Beta e Carla Gama | a Carteira é aberta | o cartão mostra a ação do grupo por onde começar e o primeiro bloco da ordem com o empate inteiro, nunca um ID sozinho dentro dele; aba inicial Focar, ou o grupo de `start_with_group` quando Focar está vazio (Qualificar, Acompanhar ou Confirmar, com fixtures próprias); sem abertas, só a mensagem de vazio; vendedor e aba na URL; o último vendedor volta na próxima visita |
| AC-5.5 | Interface | Painel | um item da lista | o painel é aberto | os dois motivos, agrupados por `role` (grupo e ordem), na ordem do payload; a nota do que o sistema não vê; próximo passo; Anterior e Próxima na ordem do grupo; Esc fecha |
| AC-5.6 | Interface | Equipe | fixtures da equipe e filtros | a Equipe é aberta | um número por grupo do `summary` (5), com "de N abertas" e sem percentual calculado na tela; filtros de gerente e escritório na URL e na chamada, cada um mostrando só as opções compatíveis com o outro; abaixo dos números, as abas "Por vendedor" (padrão) e "Por oportunidade", com a contagem e a escolha na URL (`?visao=oportunidades`); "Por vendedor" na ordem da API, com as colunas de grupo na ordem de `ordering.group_order` e link para a carteira; filtro sem vendedores mostra a mensagem, sem tabela vazia; tabelas paginadas (25 por página, sem "Mostrar mais"), e a tabela acompanha o item aberto no painel |
| AC-5.7 | Interface | Evidência e Como funciona | fixtures `evidence` e `rules` | as páginas são abertas | todo código de estratégia com rótulo e descrição nas duas linguagens; linguagem de negócio por padrão, sem siglas (pp, IC95%, AUC, Val@…); linguagem técnica pela URL, com as métricas completas; todo número sai do payload; a armadilha nunca aparece; aviso quando `audited_data` é falso; o veredito do recorte sem as que nunca fecham, nas duas linguagens; grupos, os dois limites e as faixas vindos de `/api/rules` |
| AC-5.9 | Interface | Mesma política (Revisão 4) | as fixtures e o código de `app/`, `components/` e `lib/` | `policy.test.ts` roda | abas, cartões e colunas seguem `ordering.group_order` e o `summary`; nenhum componente escreve uma chave de grupo à mão; todo grupo do contrato tem nome no catálogo |
| AC-5.8 | Interface | Responsivo e tema (roteiro manual) | API e tela no ar | as 5 páginas são abertas em 375 px e 1280 px | nenhuma rola na horizontal; no celular, o menu desce para a segunda linha e quebra em duas, centralizado e o gráfico some (a tabela traz os mesmos números); o tema segue o sistema por padrão, e o seletor Claro, Escuro ou Sistema guarda a escolha |
| AC-6.1 | P0-4 | KPIs reais (Revisão 5) | os CSVs auditados | a Inteligência é aberta sem filtro | receita ganha 10.005.534 ("10,01 mi"), 4.238 ganhas de 6.711 fechadas, taxa 63,2% com faixa provável 62,0–64,3%, ciclo mediano 57 dias (14 nas sem venda); carteira aberta 2.089 = 157 + 141 + 1.291 + 500 + 0 com valor de tabela 4.966.215, num cartão à parte com "não é receita" |
| AC-6.2 | P0-4 | Mesma política | qualquer filtro de gerente ou escritório e qualquer `as_of` válido | a Inteligência e a Equipe são comparadas | o `summary` das abertas, o `meta` e a `ordering` são iguais; o recorte sai de `views.scope`, o mesmo da Equipe |
| AC-6.3 | P0-4 | Somas | qualquer recorte | os testes somam | em cada dimensão, os segmentos somam o total (fechadas, ganhas, perdidas, receita e abertas, com a linha sem cliente); cada linha da matriz soma as fechadas do vendedor; as faixas de ciclo somam as fechadas e terminam em L1 e L2 do `meta`; o detalhamento tem o mesmo total do número que o abriu |
| AC-6.4 | P0-4 | Diagnósticos reais | os CSVs auditados | a página é aberta | 1.291 de 1.589 em andamento acima de 138 dias (grupo `revisar`); 1.425 de 2.089 abertas sem cliente e 0 de 6.711 fechadas; 500 de 500 em prospecção sem data; 5 de 35 vendedores sem oportunidade (Carl Lin, Carol Thompson, Elizabeth Anderson, Mei-Mei Johns e Natalya Ivanova); 80,7% de ganho no último mês do trimestre contra 52,3%; 283 e 121 novas negociações em nov e dez/2017 contra 864,6 por mês de jun a out; mediana de 10 vendedores por cliente (até 30). Cada um com próximo passo e ação |
| AC-6.5 | P0-4 | Descobertas reais | os CSVs auditados | a página é aberta | as 7 dimensões dentro do acaso (p de 0,14 a 0,97, α = 0,05 ÷ 7); 3 de 7 produtos com 83,5% da receita; decomposição entre vendedores 61,5% volume, 39,9% ticket e taxa desprezível; entre produtos, 89,6% ticket; entre portes, 76,0% volume; sem venda com mediana de 14 dias contra 57; 73 de 85 clientes com 6 dos 7 produtos (falta o GTK 500) |
| AC-6.6 | P0-4 | Pessoas | as dimensões vendedor, gerente e escritório | a tabela é exibida | ordem alfabética vinda da API, com quem tem zero; sem gráfico e sem índice por pessoa; a tabela abre alfabética e pode ser ordenada por coluna, só para consulta; a matriz vendedor × produto mostra fechadas e fatia do mix, sem taxa por célula |
| AC-6.7 | P0-4 | Filtros e recorte vazio | filtros na URL; valor inexistente | a página é aberta | cada filtro atualiza todos os números e fica na URL; filtrar por setor, cliente ou porte diz quantas abertas sem cliente saíram; valor inexistente mostra o vazio, nunca erro 500 |
| AC-6.8 | P0-4 | Detalhamento | uma linha, uma célula ou um diagnóstico | o usuário pede as negociações | o painel chama `/api/intelligence/deals` com o recorte somado à linha ou célula; abas Ganhas, Sem venda e Abertas; as abertas na ordem da regra, com o grupo e o link para a carteira do vendedor |
| AC-6.9 | P0-4 | Linguagem | o catálogo da Inteligência e as fixtures | `copy.test.ts` roda | todo código de diagnóstico, descoberta, veredito e dimensão tem texto; nenhum número fora dos params; nenhum termo proibido; sem jargão (IC, qui-quadrado, Bonferroni, Wilson, p-valor, margem de erro, faixa provável, ticket); o desfecho Lost se chama "sem venda" |
| AC-6.10 | P0-4 | Fim de trimestre | o diagnóstico `quarter_end_outcome_mix` | o texto é exibido | aparece como conferência do registro da data de fechamento, nunca como sinal ou como "melhor época para vender" (RJ-02) |
| AC-6.11 | P0-4 | Desempenho | os CSVs auditados | `/api/intelligence` é chamado | resposta em menos de 300 ms locais (cerca de 100 KB); o detalhamento das 4.238 ganhas cabe numa resposta |
| AC-6.12 | P0-4 | Arranjo da página | a Inteligência aberta | a página é exibida | os filtros ficam num botão "Filtros" (popover com os sete campos), com o recorte ativo em chips e a contagem no botão; o corpo tem só números, gráficos e tabelas, com a leitura abaixo de cada tabela; diagnósticos e descobertas ficam em "Ver análises" (painel lateral, abas Processo e Resultados, com contagem) e as definições em "Como funciona" |
| AC-7.1 | P0-5 | O núcleo não muda | a priorização assistida em uso | as respostas são salvas ou alteradas | a classificação, a ordem oficial, os contadores, `openapi.json`, as fixtures e a Evidência ficam idênticos (nenhum arquivo do back muda) |
| AC-7.2 | P0-5 | Seleção | um empate no topo do cartão | o vendedor abre "Avaliar estas oportunidades" | a lista mostra todas as empatadas (mesmo grupo, produto e valor de tabela), nada vem marcado e só avança com 2 a 5 escolhidas; a sexta fica travada até desmarcar uma |
| AC-7.3 | P0-5 | Questionário | uma oportunidade em avaliação | o vendedor responde | as 7 perguntas aparecem numa tela, cada uma com "Não sei", sem resposta pré-marcada; cada resposta é guardada na hora; dá para voltar, pular e deixar incompleta |
| AC-7.4 | P0-5 | "Não sei" não é "não" | uma resposta "Não sei" | os pontos são calculados | vale 0 ponto confirmado, é contada à parte e aumenta a faixa "até N pontos"; nunca é tratada como resposta negativa |
| AC-7.5 | P0-5 | Avaliação incompleta | uma pergunta sem resposta | o resultado é exibido | a oportunidade fica fora da ordem, listada como comparação parcial, com atalho para responder |
| AC-7.6 | P0-5 | Política determinística | as mesmas respostas e a mesma data dos dados | a avaliação roda de novo | pontos, categoria, ordem e textos são idênticos; os pesos somam 100 |
| AC-7.7 | P0-5 | Explicação | qualquer resultado | o cartão é exibido | traz os pontos, a quebra por pergunta, por que, o que ainda não se sabe, o que fazer agora e a data da avaliação, e o aviso "não é previsão de fechamento" |
| AC-7.8 | P0-5 | Empate preservado | duas avaliações com os mesmos pontos | a ordem é exibida | ficam com a mesma posição, marcadas como empate, sem desempate por ID |
| AC-7.9 | P0-5 | Quase tudo desconhecido | 4 ou mais respostas "Não sei" | o resultado é exibido | a oportunidade vai para o bloco "Investigar primeiro", sem posição e sem rótulo de qualidade |
| AC-7.10 | P0-5 | Contradição | "ainda sem contato" com ação combinada (ou com necessidade confirmada) | as respostas são dadas | a tela pergunta se houve equívoco; sem confirmação, a oportunidade fica fora da ordem como "Revisar respostas" |
| AC-7.11 | P0-5 | Ação com data | uma ação combinada com data | a categoria é decidida | até 7 dias depois da data dos dados (ou anterior), é compromisso a cumprir, e a anterior pede verificar a situação sem dizer que atrasou; depois disso, é só uma nota de compromisso futuro |
| AC-7.12 | P0-5 | Ordem manual | um resultado com 2 ou mais na ordem | o vendedor sobe ou desce uma oportunidade | a posição muda, aparece "posição escolhida por você" e a justificativa continua ligada às respostas |
| AC-7.13 | P0-5 | Sem previsão | todos os textos da priorização | a varredura roda | nenhuma porcentagem, "probabilidade", "chance" nem "melhor oportunidade", e o vocabulário proibido do AC-3.8 não aparece |
| AC-7.14 | P0-5 | Só no navegador | o fluxo completo | é executado | nenhuma chamada além das leituras da API; as respostas ficam em `localStorage` e a tela avisa os limites; se o navegador não guarda, a avaliação segue e avisa |
| AC-7.15 | P0-5 | Carteira | uma oportunidade avaliada | a Carteira é exibida | mostra o selo "Avaliada · N pontos · categoria" no cartão e na linha, sem mudar a ordem nem o grupo |
| AC-7.16 | P0-5 | Celular | a avaliação aberta em 375 px | o painel é usado | ocupa a tela toda, sem rolagem horizontal, e funciona só com teclado |
| AC-7.17 | P0-5 | Remover avaliação | uma oportunidade avaliada | o vendedor usa "Remover avaliação" no cartão de resultado ou no painel "Por que está aqui" | a tela pede confirmação; ao confirmar, as respostas daquela oportunidade (e as ordens escolhidas que a incluíam) saem do navegador e o selo some da Carteira; cancelar não apaga nada |

---

**Estado na entrega (19/10/2026).** Os cinco bloqueios do início do build:
1. **Compatibilidade da stack:** resolvido. FastAPI, pydantic e Next.js rodam em Python 3.9.6 e Node 22.12 (`pytest` 221 e `vitest` 284 verdes); o plano de contingência não foi usado.
2. **Oráculos sem script:** resolvido em parte. Os oráculos viraram testes, e `scripts/audit_data.py` e `scripts/backtest.py` estão no repositório. As "consultas diretas" (por exemplo, as 298 Engaging dentro do ciclo) seguem sem script (ver Limites em [architecture.md](./architecture.md#limites)).
3. **Commit-flow:** resolvido. O fluxo exclui `data/raw/*.csv`, `.next` e `.pytest_cache`; a CLI não gera `outputs/`, e o `audit_log.txt` não traz caminho absoluto.
4. **Política provisória (U-06):** aberto. Faixas de valor e percentil do primeiro limite seguem sem validação da Head de RevOps; são parâmetros.
5. **Teste de compreensão** (e a rodada da priorização assistida com vendedores reais): não feito.
