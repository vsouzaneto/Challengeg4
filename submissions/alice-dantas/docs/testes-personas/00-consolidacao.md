# Rankio — Consolidação da avaliação multiagente (Challenge 003)

Data da execução: 17/10/2026 · App: `localhost:3000` (web) + `localhost:8000` (API), dados auditados, `as_of` 31/12/2017.
Nenhum arquivo do projeto foi alterado. Relatos individuais em `01` a `06` desta pasta, gravados sem edição. Os registros brutos das sessões dos agentes estão em `tasks/<id>.output` na pasta de sessão (a_c501…, a90a…, a530…, a2df…, a21b…, a986…).

## 0. Como a avaliação foi feita e o que ela vale

| Item | O que foi feito |
| --- | --- |
| Personas | 6 agentes independentes, um por vez, cada um em aba própria do navegador embutido, sem ver o relato dos outros. O estado do navegador (`localStorage`, que guarda o último vendedor) foi limpo entre as sessões. |
| O que receberam | Papel, contexto, missão, a fala da Head de RevOps e o endereço. Nenhuma explicação de telas, regras, números, documentos ou código. Foram proibidos de ler arquivos, usar shell, chamar a API, inspecionar a página por script ou pesquisar. |
| Identidades dadas (contexto, não roteiro) | Boris Faz (iniciante, East, 57 abertas, 7 Focar) · Kary Hendrixson (experiente, West, 103 abertas, 14 Focar) · Darcel Schlecht (sobrecarregado, Central, 194 abertas, **0 Focar**) · Melvin Marxen (gerente, Central) · Head de RevOps (sem vendedor) · Diretor comercial (sem vendedor). Escolhi Darcel de propósito para exercitar o cenário D. |
| Cenário F | Pergunta feita após o relatório, via mensagem, sem alternativas, pedindo resposta de memória. Respostas gravadas na íntegra. |
| Conferências do coordenador (só leitura) | (1) A ordem dentro de empates é por ID (ex.: Darcel, 6 empatadas em 5.482: IDs 5NGPM4C3, 7TFHGN6O, I3KQNE9V… com idades 148, 158, 165…). (2) "9 baixo no grupo, 8 linhas na página 4" não é erro: a 9ª está no fim da página 3. (3) O clique em "Resultados" que o agente 2 disse não funcionar abriu na primeira tentativa comigo e nos agentes 4, 5 e 6: **não reproduzido**. |

**Limites que o leitor precisa ter em mente**
- São seis personas simuladas pelo mesmo modelo. Não são evidência de usuários reais, e a rodada de compreensão com 3 a 5 pessoas não técnicas (prevista no PRD) continua pendente.
- O alerta do briefing sobre excesso de cooperação não se confirmou: os seis fecharam em "resolve parcialmente", com críticas específicas. Mas eu os orientei a não serem gentis, o que pode ter empurrado para o lado crítico. Por isso dou mais peso ao que **vários agentes encontraram de forma independente** e ao que foi **verificável** (IDs, números, ordem).
- Os relatos de ações são autodeclarados (de 73 a 139 chamadas de ferramenta por agente). Não houve captura de vídeo ou trilha de cliques; os arquivos `.output` são o registro mais próximo disso.
- Lentidão percebida (tela cinza em Equipe, URL que muda antes do conteúdo, cliques repetidos) apareceu em 4 relatos, mas não medi nada, e o servidor local pode estar em modo de desenvolvimento. **Não verificado.**

## 1. Veredito individual

| # | Persona | Veredito | Frase-síntese observada |
| --- | --- | --- | --- |
| 1 | Vendedor iniciante (Boris) | Resolve parcialmente | "Ajuda a organizar a segunda-feira e a limpar a carteira; não substitui saber qual cliente está quente." |
| 2 | Vendedor experiente (Kary) | Resolve parcialmente | "A ordem dentro dos grupos é só preço de catálogo, o que eu já faria sozinho." |
| 3 | Sobrecarregado (Darcel) | Resolve parcialmente | "Para mim, vendedor com 83 negócios velhos empatados, ela reduziu pouco o esforço." |
| 4 | Gerente (Melvin) | Resolve parcialmente | "Não me diz qual vendedor precisa de orientação; entrega carga de carteira, não desempenho." |
| 5 | Head de RevOps | Resolve parcialmente · **aprovaria piloto controlado, com condições** | "Sem as condições 1 e 2 eu não conseguiria dizer, ao fim do piloto, se ajudou nem se foi usada." |
| 6 | Diretor comercial | Resolve parcialmente · adotaria só em piloto | "Organiza e expõe o problema; ainda não prova que o vendedor vai vender mais." |

Todos concluíram a navegação sem ajuda e chegaram ao painel "Por que está aqui". Nenhum ficou travado na jornada principal.

## 2. Matriz de aderência às dores do desafio

Gravidade: **Alta** = compromete o objetivo central; **Média** = reduz confiança ou exige esforço; **Baixa** = acabamento.

| Dor ou tarefa | Stakeholders | Resultado observado | Evidências | Problema encontrado | Gravidade |
| --- | --- | --- | --- | --- | --- |
| 1. Esforço em negócios que não vão fechar | Todos | **Parcial.** O Rankio separa e expõe as abertas antigas (1.291 de 2.089, 62%) e dá a ação "confirme no CRM". Não reduz o esforço: transfere a checagem, uma a uma, para o CRM. | Relatos 1, 2, 3, 5, 6 (cenário B). Nenhum agente tomou "Confirmar" como perdida, mas 5 de 6 a leram como "provavelmente morta ou esquecida". Boris ficou em dúvida se estava "largando dinheiro grande" (GTX Plus Pro 5.482, 147 d). | A lista de Confirmar é grande (83, 56, 213, 1.291) e quase sem critério para escolher qual checar primeiro além do preço. Darcel precisou separar "com cliente" na mão. | **Alta** |
| 2. Boas oportunidades que esfriam | Vendedores, gerente | **Parcial.** Acompanhar (141) sinaliza "veja o último avanço". Sem atividade, não há sinal de esfriamento. | Boris e Kary (e a Head) notaram que 12 d e 102 d, ou 14 d e 87 d, ficam no mesmo bloco, sem diferença de ordem. Boris puxaria PSMWYTMB (102 d, a 4 dias do limite) "por julgamento meu". | A idade aparece, mas não ordena nem destaca a proximidade do limite. Nada mostra último contato. | **Alta** |
| 3. Clareza sobre onde focar | Todos | **Resolvido na navegação**, parcial na decisão. Os seis acharam a primeira ação em cerca de 1 minuto (cartão "Seu próximo passo" + abas). | 6/6 chegaram ao painel sem orientação. Em carteiras sem Focar (Darcel, Anna, equipe do Melvin) a resposta foi "comece por Confirmar/Acompanhar", sem alvo claro. Para Anna, o cartão destacou B08R55ET (valor 55) por ser a única de Acompanhar. | 10 dos 27 vendedores com abertas têm Focar vazio. Empates grandes (6 em Darcel, 11 em Anna na aba Confirmar; 24 GTX Plus Pro a 5.482 só em Focar na empresa) viram fila sem critério visível. | Média |
| 4. Dependência da intuição | Vendedores | **Parcial / não demonstrado.** Ajuda quem começa (Boris). Para quem tem experiência, a ordem coincide com o que já se faria (preço de catálogo). | Os três vendedores reordenaram a lista por critério próprio: Boris (idade perto do limite), Kary (mais jovens e com cliente), Darcel (só quem tem cliente). A Evidência mostra a regra 4,6 pp acima de "só valor de tabela" e, sem as que nunca fecham, 1,0 pp **abaixo**. | O feeling ainda preenche as lacunas centrais (cliente, estágio, contato). Não há prova de que a lista supere o julgamento do vendedor; o backtest compara com outra ordem mecânica. | **Alta** |
| 5. Dificuldade para entender recomendações | Todos | **Resolvido para o "porquê"**, com ruído de linguagem. 6/6 explicaram grupo e posição corretamente e apontaram o que a ferramenta não vê. | Cenário F (seção 4). Dúvidas recorrentes: "Engajada em" (6/6), "Idade" (tooltip não lido por 2), "valor de tabela", "faixa provável", "margem de erro", "acaso", "ticket (mix de produto)". Anna filtrada mostrou "-30,3%" e "138,7%" na decomposição, ilegível para a Head. | Jargão persiste na Inteligência e na Evidência, apesar do critério AC-6.9. O nome "Confirmar" levou Darcel a ler "confirmar a venda" no início. | Média |
| 6. Visibilidade gerencial | Gerente, Head, Diretor | **Parcial.** Distribuição do pipeline e higiene: sim (Equipe, filtros ligados, caminho até a oportunidade). Desempenho e atenção por vendedor: não. | Melvin foi de Equipe → Por oportunidade → PYQ3VX08 → painel; filtros de gerente e escritório funcionaram. Sem meta, período, atividade, exportação. A Head não achou como saber se vendedores usam a ferramenta. | A decisão de não ordenar pessoas é coerente com a estatística, mas deixa sem resposta "quem precisa de orientação". Nenhuma telemetria de uso. | Média |

### Para cada dor: três perguntas

| Dor | A interface ajudou numa tarefa relacionada? | O resultado comercial foi demonstrado? | O que falta para afirmar que a dor foi resolvida |
| --- | --- | --- | --- |
| 1 | Sim: separou o que checar. | **Não.** | Piloto com controle: horas em negociações que terminaram sem venda, com e sem a lista. Resultado real das abertas antigas (a base não tem desfecho para elas). |
| 2 | Parcialmente. | **Não.** | Dado de atividade ou último contato; medir se o tempo até a primeira ação em Focar e Acompanhar cai. |
| 3 | **Sim.** | Não (clareza ≠ acerto). | Piloto: % de negócios trabalhados que estavam em Focar e a conversão deles contra o controle. |
| 4 | Parcialmente. | **Não.** | Comparar a ordem da lista com a escolha do vendedor experiente; só um piloto mede. |
| 5 | **Sim**, para o "porquê". | Só em simulação. | Teste com 3 a 5 pessoas reais não técnicas (critério do PRD: 4 de 5 explicam a posição e o limite). |
| 6 | Parcialmente. | **Não.** | Uso por vendedor, metas e período, para a gerência agir sobre pessoas. |

## 3. Problemas encontrados, priorizados, com evidência de navegação

| # | Problema | Quem viu | Evidência | Gravidade |
| --- | --- | --- | --- | --- |
| A | **Empate resolvido por ID, sem aviso.** Dentro do mesmo grupo e produto a ordem é alfabética pelo código (verificado na API: 148, 158, 165, 154, 148, 143 dias em Darcel). A tela só diz "N oportunidades de mesmo valor de tabela", mas a tabela mostra uma sequência que parece ranking. | 3, 4, 5, 6 (3 e 5 inferiram que era o código) | Darcel concluiu de início que 5NGPM4C3 "era a melhor", e depois corrigiu: "só vem primeiro por ser o primeiro código". Head: "a posição 1 ou 20 nessa fila quase não carrega informação." | **Alta** |
| B | **"Próximo passo" não é uma ação.** Em Focar é sempre "Avance primeiro as de maior valor de tabela; as do mesmo produto valem o mesmo." (regra de ordem, não passo com o cliente). Em Confirmar, o mesmo texto para todas. | 1, 2, 3, 6 | Boris: "Eu esperava algo como ligar, mandar proposta, marcar reunião." Kary: "Não me diz o que fazer em cada uma." | **Alta** |
| C | **Sem cliente em 66 a 68% das abertas** e nada que ajude a agir: nenhuma ação ("descubra o cliente no CRM antes"), nenhum filtro "com cliente". | 1, 2, 3, 4, 5, 6 | Boris 39/57, Kary 66/103, Darcel 134/194, Melvin 339/511, empresa 1.425/2.089. Darcel montou a lista de quem tem cliente "linha a linha, na mão". | **Alta** |
| D | **Idade não diferencia dentro do grupo e não mostra proximidade do limite.** | 1, 2, 3, 5, 6 | "12 d e 102 d no mesmo bloco" (Boris); "14 d e 87 d" (Kary); "21 d e 104 d empatadas" (Head, Zane Levy: 01XZ9CRY × FZWU2I30). | Média (a idade não ordena por decisão de projeto, mas a tela não ajuda a ler) |
| E | **Carteira sem filtros nem busca** (cliente, produto, faixa de dias, ID). | 2, 3, 6 | Darcel: "não achei filtro, busca nem ordenação por coluna". | Média |
| F | **Carteira sem Focar: orientação rasa.** O cartão leva ao próximo grupo mesmo quando ele traz pouca coisa (Anna → B08R55ET, valor 55). Carl Lin: só "Nenhuma oportunidade aberta para este vendedor". Melvin leu "Focar 0" como "minha equipe não tem boa oportunidade" e o Diretor esperava que Focar fosse "as melhores chances". | 3, 4, 5, 6 | Head: "não ficou claro o que priorizar entre 56 Confirmar de 5.482 cada." Diretor: "Para a Anna a resposta é só confirme no CRM." | Média |
| G | **Vocabulário.** "Engajada em" sem definição; tooltip de "Idade" difícil de achar; "faixa provável", "margem de erro", "acaso", "ticket (mix de produto)"; percentuais negativos e acima de 100% na decomposição filtrada; "Acompanhar" e "Confirmar" parecem verbos parecidos; "Confirmar" lido como "fechar a venda". | 1, 2, 3, 4, 5, 6 | Citações textuais nos relatos. | Média |
| H | **Inteligência e "Ver análises" densas para quem não é gestão.** Vendedores e gerente disseram que não era para eles; Melvin só percebeu depois que "Ver análises (14)" era o que mais lhe interessava. | 1, 2, 4 | "Inteligência e 'Ver análises' não são para mim" (Boris). | Baixa a Média |
| I | **Sem como medir uso, nem registrar o que foi feito** (ou marcar "já confirmei"); só "Copiar ID", sem link para o CRM. | 1, 2, 5, 6 | Head: "Hoje eu não teria como saber quem usa." | **Alta para o piloto**, Baixa para o desafio (a ferramenta é só leitura por decisão) |
| J | **Dados parados em 31/12/2017** e "não se atualiza sozinha". | 6 | Diretor: "para uso diário isso é um bloqueio." | Média (declarado) |
| K | **Percepção de lentidão ou de clique que não responde** (Equipe com cartões cinzas, URL muda antes do conteúdo, cliques repetidos). | 1, 2, 4, 6 | O clique em "Resultados" relatado pelo agente 2 **não se reproduziu** (agentes 4, 5, 6 e eu). | Não confirmado |
| L | **Gerente sem exportar ou imprimir**; sem meta, período ou atividade. | 4 | "Não dá para exportar nem imprimir uma lista para levar à reunião." | Média |
| M | **Detalhes de acabamento:** URL `grupo=revisar` com rótulo "Confirmar"; filtro de Escritório mostrando só "Central" após filtrar por gerente (é por desenho, mas ninguém explicou); "Completar = 0" sem dizer se é porque está tudo preenchido; tabela larga em tela estreita. | 1, 4, 5, 6 | Citações nos relatos. | Baixa |

### O que funcionou (também é evidência)
- **Descobribilidade:** 6/6 acharam nome → cartão → abas → painel sem instrução.
- **Honestidade das limitações:** 6/6 citaram espontaneamente que o sistema "só vê datas, produto e preço de tabela" e "não calcula chance de fechar", e disseram que isso aumentou a confiança.
- **Valor de tabela ≠ receita (cenário C):** nenhum agente confundiu os dois. O tooltip e o painel funcionaram. Ninguém tratou valor alto como chance alta; Melvin e o Diretor notaram o contrário: o GTK 500 (26.768) lidera a lista com poucas vendas históricas (cerca de 25 fechadas, faixa larga). O subponto "por que uma de menor valor aparece antes de uma maior" **não foi exercitado por nenhum agente** (fica como lacuna do teste).
- **Retratos de pipeline:** 62% parado, cadastro incompleto e vendedores sem carteira foram achados concretos que Head e Diretor transformaram em decisão.
- **Filtros de gerente e escritório (cenário E):** funcionaram e se restringiram mutuamente; a passagem da visão geral até a oportunidade funcionou.

## 4. Compreensão das recomendações (cenário F)

Respostas originais ao fim dos relatos individuais. Resumo:

| Agente | Oportunidade explicada | Grupo explicado corretamente? | Posição explicada corretamente? | Ressalva própria |
| --- | --- | --- | --- | --- |
| 1 | I5VHXAWW (Focar, 1ª) | Sim: 55 d dentro do "tempo normal" (106 d) | Sim: maior preço de catálogo | "Regra de ordenação, não razão comercial." |
| 2 | JJGRAQ2K (Focar, 1ª) | Sim, mas "não entendi esse 106 a fundo" | Sim | Ligaria antes para as mais novas (julgamento próprio) |
| 3 | 7TFHGN6O (Confirmar, 2ª) | Sim: 158 d passou de 138 d | Sim, e notou que o desempate não é explicado ("suposição minha, a ordem do código") | "O grupo não separa a Inity das outras." |
| 4 | DO6VKC2G (Confirmar, 1ª na equipe) | Sim | Sim: maior preço de catálogo (26.768) | Trataria como conferência, não previsão |
| 5 | 1FEHFRKX (Confirmar, 1ª) | Sim | Sim; inferiu ordem por código | "A posição 1 ou 20 quase não carrega informação." |
| 6 | 1LY8CAXD (Focar, 1ª do West) | Sim | Sim | Duvida da base do GTK 500; "a ferramenta não diferencia 20 d de 95 d" |

**Leitura honesta dessas respostas**
- **O núcleo do modelo foi entendido por 6/6**: grupo pela idade contra dois marcos do histórico; posição pelo preço de catálogo; ferramenta não vê atividade e não prevê chance.
- **Eco da interface:** todas as respostas reutilizam frases da tela ("90% das vendas ganhas fecharam em até 106 dias"). Isso não prova compreensão, e um modelo parafraseia com facilidade; pessoas reais podem se sair pior. Sinais de compreensão parcial: Kary não entendeu o 106 "a fundo"; Darcel, Head e Kary não sabiam o critério dentro do empate e inventaram um.
- **Interpretações incorretas observadas durante a jornada** (corrigidas depois): "Confirmar" como confirmar a venda (Darcel); "Focar 0" como "minha equipe não tem boa oportunidade" (Melvin); Focar como "melhores chances" (Diretor); o número destacado no cartão como "nota da oportunidade" (Head); a primeira da fila de empatadas como "a melhor" (Darcel).
- Critério do PRD (4 de 5 não técnicos explicam posição e limite): **não pode ser dado como atendido** por esta rodada. Ela só indica que o texto do painel é claro o bastante para um leitor atento.

## 5. Melhorias propostas

Não há bloqueio de navegação: abrir a carteira, entender o grupo e chegar ao painel funcionou para todos. Os P0 abaixo são onde "decidir como agir" perde substância. Nenhum exige mudar o scoring.

### P0 — Bloqueiam o passo "decidir como agir"

**P0-1. Mostrar que a ordem dentro de um empate não é ordem.**
- Problema: IDs em sequência parecem ranking.
- Persona afetada e evidência: Darcel (concluiu que 5NGPM4C3 era a melhor), Head, Kary, Diretor.
- Consequência comercial: o vendedor começa por uma negociação arbitrária e acredita que foi recomendada.
- Mudança: dentro de cada bloco de empate, marcar "mesmo valor de tabela: sem ordem entre si" e não numerar; o cartão "Seu próximo passo" passa a listar o bloco como conjunto e dizer "escolha entre elas pelo que você sabe do cliente". Fica fora do escopo mudar o critério de desempate sem evidência de backtest.
- Verificação: em fixtures de empate, nenhuma linha do bloco mostra posição individual; teste com 3 pessoas: "qual destas é a melhor?" → "não sei dizer pela ferramenta / empate".

**P0-2. Trocar o "próximo passo" repetido por uma ação que dependa do que a linha mostra.**
- Problema: Focar mostra a regra de ordenação no lugar da ação; Confirmar dá a mesma frase a 1.291 itens.
- Evidência: Boris e Kary.
- Consequência: o vendedor iniciante (a persona mais necessitada) não sabe o que fazer depois de escolher.
- Mudança: ação por fatos do registro, sem inventar dado: sem cliente → "Descubra o cliente no CRM antes de contatar"; com cliente em Confirmar → "Confirme com <cliente>…"; idade a ≤10 dias do limite → "Está a N dias do limite de 106 dias" (fato, sem a palavra "prazo", respeitando AC-3.8).
- Verificação: toda linha tem ação distinta conforme sua combinação de cliente e posição na faixa; varredura de vocabulário continua verde; teste com iniciantes: "o que você faz agora com esta?" responde com um passo concreto.

### P1 — Tornam a decisão confusa, exigem esforço ou reduzem a confiança

**P1-1. Filtros na Carteira: com cliente / sem cliente, produto, busca por ID.** Evidência: Darcel, Kary, Diretor; 66 a 68% sem cliente. Consequência: horas lendo linha a linha. Verificação: em Darcel (134 de 194 sem cliente), o filtro "com cliente" mostra só as com cliente nomeado, sem leitura linha a linha.

**P1-2. Tornar a idade legível dentro do grupo, sem mudar a ordem.** Evidência: Boris, Kary, Head. Mudança: indicador visual de proximidade do limite na coluna Idade. Verificação: 12 d e 102 d visualmente distintas; a ordem e o backtest não mudam (AC-4.7 segue válido).

**P1-3. Estados vazios que conduzem.** Focar vazio hoje manda para um grupo que pode ter 1 item de valor 55 (Anna). Mudança: quando o próximo grupo traz 1 ou poucos itens triviais, o cartão resume a sequência ("1 em Acompanhar; depois 56 em Confirmar, maior valor primeiro"); Carl Lin recebe "sem oportunidades abertas na base; não é erro". Verificação: caso Anna e caso Carl Lin com texto próprio.

**P1-4. Vocabulário.** "Engajada em" → "Início da negociação" com definição visível; decompor receita sem percentuais negativos ou acima de 100% (ex.: "o ticket explica a maior parte"); trocar "faixa provável", "margem de erro" e "acaso" na Inteligência por frases de negócio, conforme o critério já escrito no AC-6.9. Esclarecer "Confirmar" com subtítulo "checar se ainda está ativa". Verificação: 4 de 5 não técnicos explicam "Confirmar" e "Engajada em".

**P1-5. (Condição de piloto) Medir uso.** Contagem de abertura de carteira e de painel por vendedor, em local da Head, sem ranquear desempenho. Evidência: Head e Diretor. Verificação: a Head vê quais dos 35 abriram a ferramenta na última semana.

**P1-6. Investigar a lentidão percebida.** 4 agentes relataram cartões cinzas e cliques que demoram. Verificar em modo de produção antes de agir; se reproduzir, tratar. Não confirmado.

### P2 — Evoluções

- Exportar ou imprimir a lista e a visão de equipe (reunião de segunda; evidência: Melvin).
- Atualização de dados e filtro de período (evidência: Diretor; "Dados até 31/12/2017").
- Medida de carga por vendedor para o gerente (ex.: % da carteira em Confirmar, sem ranking de pessoas).
- Explicar por que o filtro de Escritório mostra só as opções compatíveis; "Completar = 0" com a razão; `grupo=revisar` na URL; tabela em telas estreitas.
- Marcar "já confirmei" ou ligar ao CRM: fora do escopo (a ferramenta só lê); avaliar depois do piloto.

## 6. Requisitos observáveis x o que só a produção mostra

| Observável na aplicação (confirmado por esta rodada) | Exige acompanhamento em produção (não comprovável com agentes simulados) |
| --- | --- |
| Uso de ponta a ponta sem instrução; 35 vendedores na lista; carteira, grupos e painel "Por que está aqui" | Adoção semanal pelos 35 vendedores |
| Prioridade identificável em cerca de 1 minuto e justificativa em linguagem simples | Economia de tempo e horas deixadas de gastar em negócios sem fechamento |
| Abertas antigas separadas e com ação de checagem; honestidade sobre o que não vê | Se "Confirmar" realmente evita esforço improdutivo ou só o redistribui |
| Visão de equipe com filtros e acesso à oportunidade | Se os gerentes mudam a orientação por causa dela |
| Linguagem adequada ao leitor atento (com ressalvas, seção 3-G) | Compreensão por pessoas reais (teste com 3 a 5 ainda pendente) |
| — | Aumento de receita ou conversão com grupo de controle |

## 7. Veredito da Head de RevOps simulada

**Aprovaria um piloto controlado, não um lançamento geral.** Com estas condições (dela, mais o que a consolidação acrescenta):
1. Piloto com grupo de controle: parte do time usa a lista, outra não, com métrica definida antes (valor ganho, conversão, tempo até primeira ação em Focar).
2. Ver adoção: quem abriu a carteira e o painel (P1-5).
3. Faxina prévia das 1.291 abertas acima de 138 dias: confirmar ou encerrar no CRM antes de começar. Sem isso, a lista que o vendedor vê é, em sua maior parte, "Confirmar".
4. Corrigir o cadastro: cliente obrigatório, data de engajamento, vendedores sem carteira.
5. Melhorar o desempate e o próximo passo (P0-1 e P0-2): "hoje dezenas de oportunidades empatam só por valor de catálogo".
6. Simplificar a linguagem da Inteligência (P1-4).
7. *(Acréscimo do coordenador)* Dizer ao piloto, com todas as letras, que a Evidência mostra que a regra é só 4,6 pontos melhor que ordenar por preço (e perde por 1,0 ponto sem as que nunca fecham): o piloto existe para descobrir se a regra por idade acrescenta algo.

## 8. Veredito final sobre o Challenge 003

| Requisito do desafio | Atende? | Base |
| --- | --- | --- |
| Software que roda, com dados reais | **Sim** | 6/6 usaram de ponta a ponta; números dos relatos batem com os oráculos (88 = 13+18+57 em Zane; 194 em Darcel; 2.089 na equipe) |
| Vendedor visualiza sua carteira | **Sim** | 3/3 vendedores, e também Head, gerente e Diretor |
| Identifica prioridade | **Sim**, com a ressalva dos empates | A, D |
| Entende por que | **Sim** (simulado) | Cenário F |
| Orientação comercial utilizável | **Parcial** | B, C: o próximo passo é genérico |
| Reduz a dependência do feeling | **Parcial, não demonstrado** | Dor 4 |
| Reconhece negócios que merecem revisão | **Sim** | Confirmar e Acompanhar |
| Gestor entende a equipe | **Sim** para distribuição e higiene; **não** para desempenho | Dor 6 |
| Complexidade adequada ao não técnico | **Sim** na Carteira e na Equipe; **não** na Inteligência e em partes da Evidência | G, H |

- **Atendimento aos requisitos mínimos:** sim.
- **Utilidade observada:** real para organizar a carteira e limpar o pipeline; modesta para decidir entre negócios do mesmo grupo.
- **Impacto comercial:** não comprovado. A única evidência quantitativa (Evidência) é uma simulação em dados passados, e a própria tela admite que sem as negociações que nunca fecham "só valor de tabela" rende 1,0 ponto a mais.

## 9. Pergunta final

**"Se disponibilizássemos o Rankio amanhã para os 35 vendedores, o que eles conseguiriam fazer melhor na segunda-feira de manhã, o que continuaria difícil e quais problemas precisariam ser corrigidos antes de um piloto real?"**

**Fariam melhor:** abrir o próprio nome e, em cerca de um minuto, ver a carteira em cinco grupos, saber por que cada negócio está onde está e que o sistema só enxerga datas, produto e preço de tabela. Perceberiam que a maior parte da carteira está acima do maior ciclo já fechado (62% das abertas na empresa; 82 de 103 em Kary, 44 de 57 em Boris) e que o trabalho de segunda é, antes de tudo, checar o que ainda está vivo. Gerentes veriam em minutos quem tem pipeline novo e quem só tem pipeline velho ou sem data.

**Continuaria difícil:**
- 10 dos 27 vendedores com abertas não têm nenhum Focar; nas carteiras como a de Darcel e a de Anna, a ferramenta diz "confirme no CRM" e entrega uma fila de dezenas de empates sem critério visível.
- Descobrir o cliente (66 a 68% das abertas não têm cliente) e o que fazer em cada negociação: o próximo passo é uma frase repetida.
- Para quem tem experiência, o ranking dentro do grupo coincide com o que já faria sozinho. A ferramenta não substitui o feeling; ela o reorganiza.
- Gerentes continuam sem saber quem precisa de orientação, e a Head sem saber quem usa.

**Corrigir antes do piloto:** P0-1 (empate sem falsa ordem), P0-2 (ação real no próximo passo), filtro "com cliente" (P1-1), vocabulário (P1-4), medição de uso (P1-5), e a faxina das 1.291 abertas. Mais: desenhar o piloto com controle, porque nada nesta rodada, nem a Evidência, permite afirmar que a lista melhora o resultado.
