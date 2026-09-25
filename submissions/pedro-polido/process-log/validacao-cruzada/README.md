# Validação cruzada: segunda opinião do Claude Chat sobre o Dataset 1

O Pedro pediu uma segunda opinião ao Claude Chat (claude.ai), com o CSV anexado e o contexto do desafio, sem mostrar
os achados desta entrega: "veja se encontra os desvios nesse dataset, minha outra IA encontrou alguns quero ver se
bate". A resposta está abaixo, sem edição. Em seguida, cada afirmação dela foi recalculada a partir do CSV por
[`solution/pipeline/06_validacao_cruzada.py`](../../solution/pipeline/06_validacao_cruzada.py). Os números da tabela
saem de [`verificacao.json`](verificacao.json), gerado pelo script; nenhum foi copiado da resposta dela.

**Resultado:** 19 afirmações; **16 confirmam**, **2 divergem**, 1 não é verificável
com o arquivo. Duas das confirmações eram **pontos que a análise principal não tinha**. Entraram na revisão (Etapa 1) e
estão listados na seção "O que mudou".

Prints da conversa no Claude Chat: [o pedido e o início da resposta](prints/01-pedido-e-inicio-da-resposta.png) ·
[os desvios 1 a 6](prints/02-desvios-1-a-6.png). O trecho visível nos prints é idêntico ao texto abaixo.

## O texto recebido

> Pólido, encontrei os desvios, e eles são mais graves do que "alguns problemas de qualidade". Este dataset é sintético e aleatório. Não há sinal operacional real para diagnosticar. Os dois anexos são o mesmo arquivo (hash MD5 idêntico).
> Desvios encontrados
> 1. Volume diferente do enunciado. São 8.469 tickets, não os ~30.000 prometidos. Qualquer projeção anual precisa ser escalada e isso tem que ficar explícito.
> 2. Tempos não são durações. "First Response Time" e "Time to Resolution" são datas e horas, não intervalos.
> 
> * Todas as primeiras respostas caem numa janela de cerca de 27 horas (31/05 a 02/06/2023). As compras vão de 2020 a 2021, então a "primeira resposta" chega de 1,5 a 3 anos depois da compra.
> * Se você calcular resolução menos primeira resposta, 49,3% dos tickets fechados dão tempo negativo, ou seja, foram resolvidos antes de serem respondidos. A média é −0,06 h e o intervalo vai de −23h a +23h. Isso é ruído uniforme.
> 
> 3. Dados ausentes seguem uma regra fixa, não são faltas reais.
> 
> * Open: sem primeira resposta, sem resolução, sem CSAT (2.819)
> * Pending: com primeira resposta, sem o resto (2.881)
> * Closed: tudo preenchido (2.769)
> 
> O CSAT só existe para os 33% fechados. Não dá para medir se a satisfação "caiu", porque não há série temporal.
> 4. As descrições são texto de template.
> 
> * 100% das descrições contêm o placeholder literal `{product_purchased}`, que nunca foi substituído pelo produto.
> * Há lixo de geração no meio do texto, como `<StringProperty Name=...>`, `[16:43:25]Gnome:` e `'{error_message}'`.
> * 392 descrições são duplicatas exatas.
> 
> 5. As resoluções são frases sem sentido geradas pelo Faker, com média de 5,5 palavras. Exemplos: "Offer investment fish." e "Window range building see answer job boy." Não servem para treinar respostas sugeridas.
> 6. Tipo e assunto do ticket são independentes (qui-quadrado p=0,98). "Refund request" como assunto aparece em proporções iguais nos tipos Technical issue, Billing e os demais. Um classificador treinado nesses rótulos só aprende ruído. Detalhe: o enunciado cita 3 tipos, mas o dataset tem 5.
> 7. Dados de cliente inconsistentes. 139 e-mails se repetem, e em todos eles o nome é diferente. Com isso não dá para fazer histórico de cliente nem detectar duplicatas por cliente.
> 8. Nenhuma variável tem efeito estatístico.
> 
> * Todas as categorias têm distribuição quase perfeitamente uniforme (canal, prioridade, tipo, gênero, CSAT de 1 a 5).
> * No teste Kruskal-Wallis, o CSAT não varia por canal, prioridade, tipo, assunto, gênero nem produto (todos p > 0,27). O mesmo vale para o tempo de resolução.
> * A correlação entre tempo e CSAT é ρ=0,02 (p=0,25).
> * A pior combinação aparente é Phone + High + Refund, com CSAT 2,29 e n=31. Mas quando embaralhei o CSAT aleatoriamente 200 vezes, a variação entre combinações foi a mesma (desvio 0,241 real contra 0,243 aleatório). Os "piores gargalos" são puro acaso.
> 
> O que isso significa para o challenge
> Se a sua outra IA apontou gargalos específicos, como "telefone + crítico demora mais" ou "tempo de resposta derruba o CSAT", isso não se sustenta: são diferenças da ordem de ±0,5h dentro de um ruído de ±23h. Por outro lado, se ela encontrou os tempos negativos, o placeholder e as resoluções sem sentido, então bate com o que encontrei.
> Eu acho que a resposta mais forte para o Diretor é justamente esta: "os dados não suportam o diagnóstico pedido, e aqui está a prova." Isso demonstra rigor analítico em vez de inventar insight. Sugiro:
> 
> * Diagnóstico: apresentar a auditoria acima e usar a estrutura dos dados (tempos, CSAT, status) só como demonstração de método, deixando claro que é ilustrativo.
> * Desperdício em horas e custo: só como cenário hipotético, com premissas declaradas (por exemplo, TMA e custo/hora do agente). O dataset não permite medir.
> * Automação: o Dataset 2 (IT Service Tickets, 48k) é onde está o texto real e rotulado. É ele que sustenta o protótipo de classificação e roteamento.
> * O que não automatizar: argumentar com base nos tipos de ticket (cancelamento, reembolso, crítico), não em evidência estatística deste arquivo.
> 
> Cole aqui o que a outra IA encontrou e eu comparo item por item. Se quiser, também sigo para o diagnóstico completo e o protótipo com o Dataset 2 (você precisaria anexá-lo).

## Afirmação por afirmação

| # | Afirmação da segunda opinião | Recalculado no CSV | Veredito | Já estava na análise principal? |
|---|---|---|---|---|
| 1 | Os dois anexos são o mesmo arquivo (MD5 idêntico) | MD5 da cópia usada aqui: 3597b88e44038ae8bcc716b208e6e7c1<br>Só há uma cópia no repositório local; o hash fica registrado para quem quiser comparar. | — não verificável | — |
| 2 | 8.469 tickets, não ~30.000 | 8.469 registros; 29.807 linhas físicas sem o cabeçalho (descrições com quebra de linha)<br>Explica o '30 mil': é a contagem de linhas do arquivo, não de tickets. | ✅ confirma | Sim: auditoria, cartão 1 (29.808 linhas físicas × 8.469 registros) |
| 3 | Todas as primeiras respostas caem numa janela de ~27 h (31/05 a 02/06/2023) | 31/05/2023 21:55 a 02/06/2023 00:54 = 27,0 h | ✅ confirma | Sim: auditoria, cartão 4 |
| 4 | Compras de 2020 a 2021; a primeira resposta chega 1,5 a 3 anos depois | compras de 01/01/2020 a 30/12/2021; intervalo de 1,42 a 3,41 anos | ✅ confirma | Sim: auditoria, cartão 4 (compras de 2020 a 2021); o intervalo em anos, não |
| 5 | 49,3% dos fechados com tempo negativo; média −0,06 h; de −23 h a +23 h | 49,3% negativos; média -0,06 h; de -23,2 a 23,5 h | ✅ confirma | Sim: auditoria, cartão 5 |
| 6 | A diferença é ruído uniforme | KS contra uniforme p = 3.55e-46 (rejeita); KS contra triangular p = 0,200; curtose em excesso -0,50 (uniforme −1,2; triangular −0,6)<br>É ruído, mas triangular: o formato da diferença entre dois horários uniformes independentes. A conclusão (sem sinal operacional) não muda; a palavra 'uniforme' é que está errada. | ❌ diverge | Sim, com a forma correta (triangular). A análise principal cometeu o mesmo erro antes e o corrigiu (log técnico, erros 6 e 7) |
| 7 | Ausências seguem regra fixa por status (Open 2.819, Pending 2.881, Closed 2.769); CSAT só nos fechados (33%) | Closed: 2.769 (1ª resp. 100%, resolução 100%, CSAT 100%); Open: 2.819 (1ª resp. 0%, resolução 0%, CSAT 0%); Pending Customer Response: 2.881 (1ª resp. 100%, resolução 0%, CSAT 0%); CSAT em 32,7% dos tickets | ✅ confirma | Sim: revisão, Etapa 1 (nulos por status) |
| 8 | 100% das descrições contêm {product_purchased} | 100,0% das descrições | ✅ confirma | Sim: auditoria, cartão 2 (156 nomes de variável diferentes) |
| 9 | Há lixo de geração: <StringProperty ...>, [16:43:25]Gnome:, '{error_message}' | <StringProperty: 1 descrições; [hh:mm:ss]Nome:: 35 descrições; {error_message}: 472 descrições | ✅ confirma | Parcial: {error_message} vazio sim (revisão 2.1); os outros dois, não |
| 10 | 392 descrições são duplicatas exatas | 439 tickets em 47 grupos de texto idêntico = 392 cópias além da 1ª<br>Novo: a auditoria só procurava registros repetidos em todas as colunas (zero). | ✅ confirma | **Não.** Só comparava registros inteiros (zero) e pares parecidos (≥ 0,8) |
| 11 | Resoluções são frases sem sentido do Faker, com média de 5,5 palavras | média de 5,49 palavras em 2.769 resoluções (fechados) | ✅ confirma | Sim: auditoria, cartão 6 |
| 12 | Tipo e assunto são independentes (qui-quadrado p = 0,98) | p = 0,981; 'Refund request' vai de 6,1% a 7,4% dos tickets de cada tipo | ✅ confirma | Sim: auditoria, cartão 8 (V de Cramér 0,034) |
| 13 | O enunciado cita 3 tipos; o dataset tem 5 | 5 tipos no CSV: Billing inquiry, Cancellation request, Product inquiry, Refund request, Technical issue; o enunciado lista Technical issue, Billing inquiry, Product inquiry<br>Novo: a auditoria não comparava os tipos do CSV com os do enunciado. | ✅ confirma | **Não** |
| 14 | 139 e-mails se repetem, todos com nome diferente | 139 e-mails repetidos; em 139 deles cada ocorrência tem um nome diferente | ✅ confirma | Sim: revisão, 2.1 descartadas |
| 15 | Todas as categorias são quase perfeitamente uniformes (canal, prioridade, tipo, gênero, CSAT) | Ticket Channel: p = 0,718; Ticket Priority: p = 0,205; Ticket Type: p = 0,115; Customer Gender: p = 0,007; Customer Satisfaction Rating: p = 0,797<br>Quatro das cinco são compatíveis com uniforme; rejeita em: Customer Gender (Male 2.896, Female 2.887, Other 2.686). | ❌ diverge | Sim, sem gênero. A análise principal cometeu o mesmo erro antes e o corrigiu (log técnico, erro 2) |
| 16 | CSAT não varia por canal, prioridade, tipo, assunto, gênero nem produto (todos p > 0,27) | p de 0,278 a 0,807 | ✅ confirma | Sim, por outros testes: auditoria, cartão 9 (modelo com todas as variáveis ≈ acaso) e detector (0 de 149 segmentos) |
| 17 | O mesmo vale para o tempo de resolução | p de 0,381 a 0,919 | ✅ confirma | Sim, por outro método: detector de gargalos (Welch + Benjamini-Hochberg), 0 de 149 segmentos |
| 18 | Correlação entre tempo e CSAT ρ = 0,02 (p = 0,25) | ρ = 0,022 (p = 0,254) | ✅ confirma | Implícito no cartão 9 |
| 19 | Pior combinação Phone + High + Refund (CSAT 2,29, n = 31); embaralhando 200 vezes, a variação é a mesma (0,241 × 0,243) | pior: Phone + High + Refund request com CSAT 2,29 (n = 31); desvio entre combinações 0,241 real × 0,240 embaralhado (percentil 58 do real) | ✅ confirma | Sim, com outro método: detector validado por curva de poder, 0 gargalos reais |

## Onde ela erra

1. **"Ruído uniforme."** A diferença entre resolução e 1ª resposta não é uniforme: o KS rejeita a uniforme e não
   rejeita a triangular, e a curtose bate com a triangular, que é o formato da diferença entre dois horários uniformes
   independentes. Continua sendo ruído, então a conclusão dela (não há gargalo mensurável) se mantém. A análise
   principal cometeu o mesmo erro numa versão anterior e o corrigiu ([log técnico](../README.md), erros 6 e 7).
2. **"Todas as categorias são quase perfeitamente uniformes", incluindo gênero.** Canal, prioridade, tipo e nota são
   compatíveis com a uniforme; gênero não é (p = 0,007, com "Other" abaixo dos outros dois). Não muda nada na
   operação, mas a afirmação não se sustenta como escrita. É o mesmo erro que a análise principal cometeu e
   corrigiu ([log técnico](../README.md), erro 2).

## O que mudou por causa dela

- **Descrições idênticas.** A checagem de "registros repetidos" comparava todas as colunas e deu zero. Faltou
  comparar só o texto: 392 descrições são cópia exata de outra. Nenhum dos 47 grupos repete e-mail ou assunto, então
  é texto de template reaproveitado, não o mesmo pedido reenviado. Entrou na revisão, Etapa 1, linha "Texto idêntico".
- **Tipos do enunciado.** O brief lista 3 tipos e o CSV tem 5. Os dois que o brief não cita, *Refund request* e
  *Cancellation request*, somam 3.447 tickets (40,7%) e são justamente os que a política manda para uma pessoa
  (revisão 2.2). Entrou na revisão, Etapa 1, linha "6. Tipos".
- Os dois itens também entraram na lista de erros da Etapa 1, com a origem declarada.

## Onde as duas análises concordam no que fazer

As recomendações dela no fim do texto batem com o que a entrega já faz: o diagnóstico é a auditoria; horas e custo
aparecem só como cenário com premissas declaradas (revisão, Etapa 3); a automação se apoia no Dataset 2 (texto real e
rotulado); e o "não automatizar" se argumenta pelo tipo de pedido (reembolso, cancelamento, perda de dados), não por
estatística deste arquivo.

## Como reproduzir

```bash
cd solution/pipeline
python 06_validacao_cruzada.py
```
