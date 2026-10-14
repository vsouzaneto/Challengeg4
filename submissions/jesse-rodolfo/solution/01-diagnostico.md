# Diagnóstico operacional

**Para o diretor:** a operação perde de 1.042 a 11.400 horas de agente por ano; no caso base são 3.950 horas, o equivalente a 2,5 agentes em tempo integral, e o maior item recuperável é cobrar o cliente parado (1.700 h/ano), alvo do piloto "Lembrete de cliente parado".

1. Não existe registro de quando o ticket abre, então nenhum tempo de resposta ou de resolução pode ser medido.
2. O que dá para ver é a fila: 67% não fechados (33% abertos e 34% esperando o cliente).
3. Nada do que a operação registra explica a nota do cliente.
4. Recomendação 1: padronizar a entrada e registrar cinco campos antes de automatizar.

Números de `solution/analise/02_diagnostico.py` sobre o dataset 1 (8.469 tickets, não os 30 mil do brief). O dataset 1 é sintético e seus campos de tempo não medem duração; a prova e os testes estatísticos estão em `docs/auditoria-dados.md`.

## 1. Onde o fluxo trava

| Status | Tickets | % |
|---|---|---|
| Esperando o cliente | 2.881 | 34,0 |
| Aberto, sem nenhuma resposta | 2.819 | 33,3 |
| Fechado | 2.769 | 32,7 |

67% não fechados (33% abertos e 34% esperando o cliente). São duas esperas diferentes: os abertos não têm carimbo de resposta, ninguém falou com o cliente; os pendentes já foram respondidos e pararam do lado de fora da empresa.

Prioridade, canal e tipo não mudam a chance de o ticket estar fechado. Critical fecha 34,1%, Low 31,2%, diferença dentro do acaso. Entre as 80 combinações de canal, prioridade e tipo, o fechamento vai de 19,4% a 43,4%, mas embaralhando o status o acaso sozinho produz a mesma amplitude. Apontar "a pior combinação" seria apontar ruído. Quais combinações têm o pior tempo de resolução não dá para responder: não existe tempo de resolução.

## 2. O que impacta satisfação

A nota só existe nos 2.769 fechados (33%), distribuída por igual de 1 a 5, média 2,99. Nenhuma variável tem efeito distinguível do acaso: prioridade, canal, tipo, assunto, produto, gênero, idade. Um modelo com todas juntas acerta 20,0% das notas, abaixo dos 20,9% de chutar sempre a mais comum.

Ou a nota depende do que não é registrado (tempo até a primeira resposta, número de contatos, problema que voltou), ou a pesquisa cobre uma amostra enviesada (só fechados). Nos dois casos a ação é a mesma: registrar antes de concluir.

## 3. Quanto estamos desperdiçando

Horas de agente por ano sobre os 30 mil tickets do brief. Cada premissa pode ser trocada pelo número do diretor.

| Premissa | Baixo | Base | Alto | Origem |
|---|---|---|---|---|
| Triagem por ticket | 20 s | 30 s | 3 min | Medida: 5 tickets aleatórios cronometrados, média 19,9 s (piso); base com 10 s para ler texto original; teto para texto real com contexto |
| % roteado para a fila errada | 10% | 20% | 30% | Premissa não medida, a confirmar na primeira semana do piloto |
| Minutos por repasse | 5 | 10 | 15 | Premissa não medida, a confirmar na primeira semana do piloto |
| % que passa por "esperando o cliente" | 25% | 34% | 45% | Base: foto do backlog do dataset 1 |
| Cobranças por ticket pendente | 1 | 2 | 3 | Premissa não medida, a confirmar na primeira semana do piloto |
| Minutos por cobrança | 3 | 5 | 8 | Premissa não medida, a confirmar na primeira semana do piloto |
| % reaberto | 5% | 10% | 15% | Premissa, sem campo para medir |
| Minutos por reabertura | 10 | 20 | 30 | Premissa, sem campo para medir |
| Custo da hora | R$ 30 | R$ 50 | R$ 70 | Operação de atendimento do Jessé (venda, não suporte): R$ 29 a 37 com fixo mais comissão, R$ 56 a 74 só comissão |
| Horas produtivas por agente/ano | 1.600 | 1.600 | 1.600 | Conservador para CLT de 44 h, descontando férias e feriados |

| Desperdício (h/ano) | Baixo | Base | Alto | Etiqueta |
|---|---|---|---|---|
| Espera que vira trabalho: cobrar o cliente | 375 | 1.700 | 5.400 | Recuperável por automação (lembrete de cliente parado: lembrete e encerramento após prazo) |
| Movimentação: repasse entre filas | 250 | 1.000 | 2.250 | Recuperável por automação (classificação e roteamento) |
| Superprocessamento: triagem manual | 167 | 250 | 1.500 | Recuperável por automação (classificação) |
| Retrabalho: reabertura | 250 | 1.000 | 2.250 | Não recuperável até medir a causa |
| **Total** | **1.042** | **3.950** | **11.400** | |
| Agentes em tempo integral | 0,7 | 2,5 | 7,1 | |
| Custo/ano | R$ 31 mil | R$ 198 mil | R$ 798 mil | |

**Sensibilidade** (cada premissa de baixo a alto, as outras no base; total base 3.950 h):

| Premissa | Total se baixo | Total se alto | Amplitude |
|---|---|---|---|
| Cobranças por ticket pendente | 3.100 | 4.800 | 1.700 |
| Minutos por cobrança | 3.270 | 4.970 | 1.700 |
| Triagem por ticket | 3.867 | 5.200 | 1.333 |
| % roteado errado | 3.450 | 4.450 | 1.000 |
| Minutos por repasse | 3.450 | 4.450 | 1.000 |
| % que passa por pendente | 3.500 | 4.500 | 1.000 |
| % reaberto | 3.450 | 4.450 | 1.000 |
| Minutos por reabertura | 3.450 | 4.450 | 1.000 |

As duas premissas que mais mexem no total são do ciclo de cobrança, e nenhuma é medida hoje. A triagem, a única premissa medida, pesa pouco no caso base (250 h): o ganho de classificar automaticamente não está no tempo de ler, está em errar menos a fila. Na cronometragem, a triagem humana sem ajuda acertou 1 de 5 tickets contra o rótulo do dataset.

Fica fora da conta o tempo que o cliente espera sem ninguém trabalhando no ticket. Não custa hora de agente, custa satisfação, e é o que os 33% abertos sem resposta indicam.

## 4. Hipóteses do Bloco 0 contra os dados

| Hipótese (escrita antes de abrir os dados) | Resultado |
|---|---|
| O tempo se perde esperando, não resolvendo | Sustentada pela estrutura: 67% não fechados (33% abertos e 34% esperando o cliente) |
| Crítico não é resolvido mais rápido | Compatível: fecha na mesma proporção que Low; velocidade não medível |
| Telefone e rede social demoram mais | Não confirmada: fechamento igual entre canais; demora não medível |
| A nota cai pela demora na primeira resposta | Não testável: falta hora de abertura |
| Reembolso, pagamento e cancelamento custam mais | Não testável; tipo e assunto não batem entre si (60,0% dos tickets são tipo financeiro, 18,8% têm assunto financeiro) |
| Classificar por texto a IA faz bem e barato | A medir no dataset 2, Bloco 4 |

## 5. Recomendação 1: instrumentar antes de automatizar

**Passo zero, entrada estruturada:** o cliente escolhe o tipo num menu e preenche 2 ou 3 campos obrigatórios; o texto livre vira complemento. É a forma mais barata de instrumentar a entrada e reduz a triagem quase a zero nos tickets bem preenchidos (detalhe em `02-proposta-automacao.md`).

| Campo, registrado pelo sistema | O que destrava |
|---|---|
| Data e hora de abertura | Tempo até primeira resposta e até resolução por canal, prioridade e tipo |
| Data e hora de cada mudança de status | Separa espera interna (aberto sem dono) de espera externa (cliente) |
| Contador de reabertura | Taxa real de retrabalho, hoje premissa de 5% a 15% |
| Histórico de fila e responsável | Taxa real de repasse, hoje premissa de 10% a 30% |
| Resolução aplicada ligada à nota do cliente | Saber qual resposta funciona, base do aprendizado do banco de respostas; hoje Resolution é texto aleatório e nenhum se repete |

Com duas semanas desses campos, as premissas de cobrança e repasse viram medidas e a faixa de 1.042 a 11.400 horas vira um número. Sem eles, nenhuma automação tem antes e depois para comparar.
