# Process Log — Challenge 002

## 2026-10-06 — Estrutura inicial

### Decisão 01 — Auditoria integrada ao produto
A auditoria de dados não ficará isolada em notebook. O painel possui uma camada `Data Quality & Audit` que lê os datasets reais e expõe schema, cobertura, duplicidades, cardinalidade e inconsistências temporais.

### Decisão 02 — Não inventar `Created At`
O Dataset 1 não fornece data observável de abertura do ticket. O histórico será mantido com essa limitação explícita. O protótipo novo registrará `created_at` no momento real de entrada.

### Decisão 03 — Separar evidência e projeção
- OBSERVED: medido diretamente nos datasets.
- DERIVED: calculado apenas sobre evidência observada.
- PROJECTED: extrapolado explicitamente para a escala de ~30.000 tickets/ano fornecida pelo briefing.

### Decisão 04 — Validar timestamps antes de calcular SLA
`First Response Time` e `Time to Resolution` são descritos no briefing como tempos, porém aparecem no dataset como timestamps. O sistema não tratará esses campos como duração até que a relação temporal seja matematicamente validada.

## 2026-10-06 — Dados reais carregados

### Iteração 05 — Erro da IA no download e correção
A primeira instrução gerada pela IA apontou `data/raw/` diretamente como `output_dir` do `kagglehub`. O diretório já continha `.gitkeep`, e o `kagglehub` recusou o download com `FileExistsError`. A execução humana expôs o erro. A estratégia foi corrigida para staging isolado em `data/_downloads/dataset1` e `dataset2`, copiando depois apenas os CSVs para `data/raw/`.

### Evidência 06 — Tamanho real dos datasets
- Dataset 1: 8.469 registros e 17 colunas.
- Dataset 2: 47.837 registros e 2 colunas (`Document`, `Topic_group`) em 8 classes.
- O briefing informa ~30.000 registros para o Dataset 1, mas o arquivo fornecido contém 8.469. Os ~30.000 serão tratados como contexto operacional anual, não como tamanho da amostra.

### Evidência 07 — Campos temporais não suportam SLA bruto
Nos 2.769 tickets com `First Response Time` e `Time to Resolution` comparáveis, 1.365 (49,3%) possuem resolução anterior à primeira resposta. Em 100% dos 2.769 pares, o componente de segundos é idêntico entre os dois timestamps. Isso reforça que os campos foram gerados de forma sintética e não representam uma cronologia operacional confiável.

### Decisão 08 — Diagnóstico parcial antes de qualquer inferência de horas
O painel passa a calcular imediatamente o que é defensável: mix por status, tipo, canal e prioridade; cobertura e distribuição de CSAT; e testes de associação de CSAT por dimensões categóricas. Horas desperdiçadas e custo permanecem bloqueados até existir uma regra temporal comprovada ou uma premissa explicitamente parametrizada.

### Uso de IA
A IA foi usada para decompor o challenge, implementar a auditoria, propor testes estatísticos e automatizar a leitura dos datasets. O processo humano rejeitou inferências cronológicas sem evidência, identificou a falha do comando de download e manteve separado o que é observado, derivado e projetado.


### Iteração 09 — Correção de bug no cálculo de tickets não resolvidos
A primeira versão de `OperationalDiagnostics._waste_analysis()` aplicava o operador `~` ao inteiro resultante de `sum()` por precedência de operadores, produzindo `-2770`. A execução humana expôs a impossibilidade lógica do valor. A expressão foi corrigida para inverter a máscara booleana antes da soma: `(~status.eq("Closed")).sum()`. Para a amostra atual, o valor defensável é 5.700 tickets não fechados (67,30%).

### Evidência 10 — Canal, prioridade e tipo não explicam CSAT na amostra fechada
Nos 2.769 tickets com avaliação, os testes Kruskal-Wallis não encontraram associação estatisticamente significativa a 5% para canal (`p=0,27845447`), prioridade (`p=0,62869901`) ou tipo (`p=0,69925067`). As diferenças de média também são pequenas (spreads de 0,1309; 0,0941; 0,0945 em escala 1–5). A próxima etapa é testar assunto, produto, idade e sinal textual antes de concluir que o CSAT é essencialmente não explicado pelos campos estruturados disponíveis.

### Decisão 11 — Base parcial e normalização de escala
Os 8.469 tickets são tratados como 100% da base efetivamente fornecida e são o único denominador do diagnóstico. Os ~30.000 tickets/ano permanecem como contexto externo do briefing. A relação 8.469 / 30.000 = 28,23% é exibida apenas como normalização de escala, equivalente a aproximadamente 103 dias de volume médio se a operação anual fosse distribuída uniformemente. Esse valor não é apresentado como período cronológico observado. Projeções anuais ficam separadas e só serão usadas em cenários de impacto/ROI com premissas explícitas.

### Decisão 12 — Separar dados originais, análise cruzada e protótipo
A UI ganhou um `Dataset Explorer` somente leitura. Dataset 1 e Dataset 2 são exibidos diretamente a partir dos CSVs originais, com busca, filtros e paginação, sem correção ou enriquecimento dos registros. O `Cross-Dataset Analysis` fica separado e explicitamente marcado como `NOT VALIDATED` até que um modelo treinado no Dataset 2 seja testado semanticamente no Dataset 1. O `Prototype` permanece reservado para o fluxo redesenhado e para campos/decisões que não existem nos dados históricos originais.

### Decisão 13 — Não fingir join relacional entre os datasets
Os datasets não compartilham uma chave observável. Portanto não haverá `join` artificial por ID, cliente ou data. O único cruzamento candidato é semântico: `Document → Topic_group` do Dataset 2 como fonte supervisionada e `Ticket Subject + Ticket Description` do Dataset 1 como alvo. A validade desse cruzamento será decidida por desempenho, confiança e coerência de taxonomia antes de entrar no diagnóstico.

### Decisão 14 — Separar estado do fluxo de tempo de resolução
Para responder “Onde o fluxo trava?”, o painel passa a destacar `Open`, `Pending Customer Response`, `Closed + Resolution` e `Closed sem Resolution`. Esses números são estado observado do snapshot, não duração. `Closed sem Resolution` é tratado como falha de completude a investigar, não automaticamente como atendimento sem solução satisfatória.

### Decisão 15 — Cruzamento operacional antes do ranking temporal
Canal, prioridade e tipo de ticket passam a ser cruzados em todas as combinações observadas. Enquanto a cronologia histórica permanecer inválida, o ranking usa somente `taxa de não fechamento no snapshot` (Open + Pending) e exibe o ranking por tempo como bloqueado. Nenhum “pior tempo de resolução” será fabricado a partir dos timestamps inconsistentes.


### Decisão 16 — Topic_group entra no Diagnóstico, mas status por grupo permanece bloqueado
O Dataset 2 contém apenas `Document` e `Topic_group`; portanto não é possível afirmar quantos tickets Open/Pending/Closed existem por grupo diretamente nessa base. O Diagnóstico passa a mostrar a distribuição observada dos 8 Topic Groups e mantém `status por grupo` como indisponível até que um classificador validado aplique a taxonomia do Dataset 2 aos 8.469 tickets do Dataset 1. Só então será permitido cruzar `Topic_group previsto × Ticket Status × Priority × Channel × Ticket Type`.

### Decisão 17 — Preservar Document original e auditar repetição interna
A visualização do Dataset 2 revelou texto aparentemente já processado/normalizado e com repetições internas. O Dataset Explorer continuará mostrando o CSV original sem correção. Uma camada de Data Quality mede duplicatas exatas, comprimento em tokens, razão de tokens únicos, repetição de bigramas, presença de pontuação e caixa do texto. Qualquer limpeza futura será feita em cópia processada para treinamento, nunca sobre a evidência original.

## Decisão — separar relacionamento real de saída de modelo

A revisão dos schemas mostrou que o Dataset 1 e o Dataset 2 não possuem chave comum observável. O Dataset 1 contém Ticket ID, Customer Name/Email e Ticket Status; o Dataset 2 contém apenas Document e Topic_group. Portanto, nenhum Ticket Status ou cliente será atribuído ao Dataset 2 e nenhuma linha será ligada artificialmente entre as bases.

O uso do Dataset 2 fica restrito a corpus rotulado para treinar/testar classificação. Qualquer Topic_group aplicado posteriormente a um ticket do Dataset 1 será marcado como MODEL-DERIVED, nunca como dado observado.

Também foi corrigida a interpretação da unidade do Dataset 1: as 8.469 linhas são tickets, não clientes. A identidade de cliente dentro do Dataset 1 pode ser analisada por Customer Email, mantendo essa análise separada do Dataset 2.


## Decisão 09 — Dataset 2 não representa melhorias implementadas
- Evidência: o README do challenge define cada linha do Dataset 2 como `Document` (texto completo do ticket) + `Topic_group` (classe), totalizando ~48K tickets de outra organização.
- Decisão: tratar as 47.837 linhas como corpus independente de tickets rotulados para treinamento/teste de classificadores.
- Regra: não somar Dataset 2 ao volume anual de ~30K, não converter linhas em melhorias e não criar relação cliente/status com Dataset 1 sem chave observável.

## Decisão 10 — Fluxo operacional completo também no Dataset Explorer
- Motivo: a inspeção dos dados brutos precisa manter visíveis as dimensões operacionais usadas no diagnóstico.
- Implementação: Open/Pending/Closed + Channel + Priority + Ticket Type são exibidos no cabeçalho do Dataset Explorer a partir do Dataset 1, sem alteração dos CSVs.

## Decisão 18 — Dataset 2 sai do Diagnóstico Operacional
O requisito da Entrega 01 determina diagnóstico com base no Dataset 1. Como o Dataset 2 contém somente `Document` e `Topic_group`, sem cliente, canal, prioridade, status, resolução, CSAT ou tempo operacional, ele não será apresentado como evidência da fase de diagnóstico.

Esta decisão substitui a Decisão 16 quanto à localização do `Topic_group`: a distribuição do Dataset 2 passa para `Automação IA`, onde funciona como corpus de treinamento/validação. Nenhum `Topic_group` do Dataset 2 é tratado como estado operacional da empresa do case.

## Decisão 19 — Não usar o conceito visual de CROSS-DATASET
Não existe relacionamento relacional entre as bases. O termo `CROSS-DATASET` foi removido da UI para evitar a impressão de que existe um join observável. A relação entre os datasets é funcional e sequencial:
- Dataset 1 → diagnóstico operacional e definição do problema.
- Dataset 2 → treinamento/teste da classificação para a proposta de automação.
- Aplicações futuras do modelo sobre novos tickets ou sobre texto do Dataset 1 serão explicitamente marcadas como saída de modelo, não como dado original.

## Decisão 20 — Dataset Explorer separado por fase
O Dataset Explorer da fase de Diagnóstico passa a exibir somente o Dataset 1. O fluxo operacional observado (status, canais, prioridades, tipos e recorrência de clientes) foi movido para o rodapé dessa área, depois das linhas originais.

O Dataset 2 ganha seu próprio explorer dentro de `Automação IA`, junto da distribuição de `Topic_group` e da auditoria do campo `Document`. Os dois CSVs continuam preservados e exibidos em modo somente leitura.
