# Revisão guiada — três tickets antes de fechar a solução

**Objetivo:** tornar concreto o trabalho do atendente e julgar onde a assistência é útil. Esta seleção intencional vem da avaliação já executada; não é nova amostra representativa nem prova de impacto. Nenhuma nova chamada de IA foi feita para produzir este roteiro.

**Participação do candidato:** avaliar um caso por vez. Codex apresenta pedido, saída real, limites e uma pergunta operacional. Respostas ficam registradas como julgamento do candidato, sem serem confundidas com medição de tempo ou referência de qualidade de toda a base.

**Estado:** três casos discutidos; decisões do candidato registradas. Revisão qualitativa de três exemplos, sem medição de utilidade/tempo ou aprovação geral do produto.

[Registros reunidos, com saídas completas](../solution/reports/revisao-guiada.json). As posições no CSV começam em 1, sem cabeçalho; não são IDs de tickets fornecidos pela base.

## 1. Outlook: quando a ajuda acrescenta trabalho

**D2, registro 45.057; conjunto de teste já avaliado.**

### Original completo

> outlook issue hi working reinstalled issue solved best regards

### Saída efetivamente registrada

- Categoria sugerida: **Administrative rights**; rótulo da base: **Administrative rights**.
- Score: **99,61%**. Não é probabilidade calibrada de acerto operacional.
- Original: **9 palavras em inglês**. Recap: **92 palavras em português**, contando itens, incertezas e próximo passo, sem repetir citações. Os idiomas diferem; essa contagem descreve extensão, não mede esforço.
- [Geração original](../solution/reports/recap-evaluation/generate-45057.json) · [Parecer automatizado](../solution/reports/recap-evaluation/judge-45057.json).

### Leitura de Codex para discussão

Há menção a problema no Outlook, reinstalação e afirmação de resolução. O texto não permite atribuir quem confirmou, quando ou qual é o estado atual do atendimento. Também não menciona necessidade de privilégios administrativos.

**Trabalho possível do atendente:** consultar o registro atual e verificar se resta alguma ação ou confirmação necessária. Perguntar novamente ao cliente pode ser necessário em um fluxo; em outro, criaria contato desnecessário. O fragmento não resolve essa escolha.

**Limite da classificação:** acertar o rótulo `Administrative rights` desta base não comprova que essa categoria seja adequada operacionalmente. Score alto é preferência do modelo, não verificação de sentido.

**Limite do recap:** a geração pede detalhes do problema e confirmação atual; o revisor automatizado aprovou seus critérios. Ainda assim, aprovação de fidelidade não demonstra utilidade: a recomendação pode acrescentar perguntas desnecessárias.

**Pergunta ao candidato:** conferir o registro e perguntar só se necessário, seguir a coleta de detalhes sugerida ou recuperar a conversa completa antes de escolher um próximo passo?

### Decisão do candidato — caso 1

> Conferir o registro atual; só perguntar ao cliente se faltar confirmação necessária.

**Consequência para o fluxo proposto:** priorizar conferência do registro atual. Contato com o cliente depende de faltar confirmação necessária; menção a resolução no fragmento não autoriza encerramento automático. Essa decisão corrige o próximo passo proposto pelo recap neste exemplo. Não implica aprovação da categoria `Administrative rights` nem de toda a geração.

**Estado da implementação:** feedback registrado; prompt e comportamento do aplicativo ainda não alterados. Fechar o recorte após os três casos.

## 2. Férias: preservar tentativas sem reconstruir uma história incerta

**D2, registro 34.887; conjunto de teste já avaliado.**

### Original completo

> move vacation days time card error move vacation days dear please delete card error for thank you assistant sent wednesday december re move vacation days thanks if you one can help with next one tried add annual leave but allow submit errors out there tasks added for annual leave entries problem list for task details empty when select leave you know if common problem or thanks sent wednesday december re move vacation days hi please note your absence was only saved by you submitted per below print screen if absence only saved get deducted balance going for approval flow have submitted absence yes deducted balance but alright because if you check your balance using th balance calculation date you have below confirm everything alright further action needed your side please let know if you need further details kind regards assistant sent wednesday december re move vacation days dear have submitted absence request for days seem have decreased days balance days still remained let know if alright thanks sent friday december re move vacation days hi we have taken note days be carried over into please proceed with booking your holiday for kind regards assistant sent thursday december re move vacation days fine can you help with please regards sent december move vacation days hi planning vacation th th wondered whether you can moving annual leave days into please advice thanks lead architect

### Saída efetivamente registrada

- Categoria sugerida: **HR Support**; rótulo da base: **HR Support**.
- Score: **99,88%**. Não é probabilidade calibrada de acerto operacional.
- Original: **232 palavras em inglês**. Recap: **412 palavras em português**, contando itens, incertezas e próximo passo, sem repetir citações. Os idiomas diferem; essa contagem descreve extensão, não mede esforço.
- [Geração original](../solution/reports/recap-evaluation/generate-34887.json) · [Parecer automatizado](../solution/reports/recap-evaluation/judge-34887.json).

### Leitura de Codex para discussão

O documento reúne referências a mover dias de férias, erro ao adicionar licença anual, detalhes de tarefa vazios, saldo de dias e distinção entre solicitação salva e submetida. Datas e autoria estão incompletas; não há base segura para ordenar todos os eventos.

**Trabalho possível do atendente:** distinguir problema de saldo, submissão e erro no apontamento; consultar o estado atual antes de repetir orientações já dadas. Preservar a tentativa `tried add annual leave ... errors out ... details empty` pode evitar reiniciar o diagnóstico. Não afirmar que cada menção representa uma pendência atual.

**O que o protótipo entrega:** categoria `HR Support`, seguida de 11 itens, sete incertezas e um próximo passo. A síntese inclui as tentativas, mas também atribui ao usuário uma fala cuja autoria é incerta e sugere uma ordem de mensagens que o arquivo não estabelece.

**Objeção do avaliador automatizado:** autoria e expressão “próximo período” extrapolam o texto. Codex acrescenta uma objeção de utilidade para discussão: o atendente ainda precisa filtrar uma saída longa para localizar o problema atual. Isso não foi medido em experimento de tempo.

**Hipótese de formato mais útil, ainda não implementada/validada:** poucos tópicos sobre problema relatado, tentativas já mencionadas e pontos a conferir internamente, cada um com fonte. Não transformar toda ausência do dataset em pergunta ao cliente.

**Pergunta ao candidato:** quais informações você precisaria ver primeiro para continuar esse atendimento sem repetir trabalho, e quais dessas lacunas exigiriam consultar o sistema antes de perguntar ao cliente?

### Decisão do candidato — caso 2

Dhiego definiu a sequência:

1. Verificar se existe mais algum ticket aberto.
2. Consultar o sistema para confirmar se as férias estão lançadas.
3. Consultar notas internas do atendimento.

**Se as férias estiverem lançadas**, fazer a confirmação proposta por Dhiego:

> Verifiquei aqui e as férias foram lançadas. Tem alguma outra solicitação que precise de ajuda?

**Se não estiverem lançadas**, perguntar se houve nova tentativa, se o erro persiste e em qual etapa; solicitar evidências, como print de tela, para escalar ao time técnico.

**Consequência para o fluxo proposto:** o próximo passo depende de conferências internas e do estado real, além do texto do ticket. Consulta a outros chamados pode evitar trabalho paralelo; consulta ao sistema e às notas orienta o contato. Esses benefícios são hipóteses, sem medição nesta revisão. A fala “Verifiquei aqui” só cabe após uma consulta efetivamente realizada.

**Limites de implementação:** o protótipo atual não consulta outros tickets, sistema de férias ou notas internas. Não apresentar essas verificações como executadas, nem interpretar falta de acesso ao sistema como prova de que as férias não foram lançadas. Identificação confiável do solicitante e vínculo entre registros exigem dados que não podem ser reconstruídos dos emails inconsistentes do D1.

**Estado da implementação:** orientação registrada; prompt e aplicativo ainda não alterados. A decisão não é aprovação integral do recap gerado nem validação de ganho de tempo.

## 3. Férias e acesso a dados de outro colega: categoria não expressa risco

**D2, registro 45.725; conjunto de teste já avaliado.**

### Original completo

> annual leave days sent wednesday december re annual leave days importance high dear please check restore accesses properly seems able access data for another colleague please let know when fixed thank you administration officer sent wednesday december re annual leave days hi think mistake process using credential get access you can thanks sent wednesday december re annual leave days could you please check again make another thank you sent wednesday december re annual leave days hello please note different data than you sent can be checked again if error persists please let know be investigated by thank you administration officer sent tuesday december annual leave days hi can you please check annual leave days for more details below thank you sent tuesday december bug annual leave request hi sending you for issue we found thank you

### Saída efetivamente registrada

- Categoria sugerida: **HR Support**; rótulo da base: **HR Support**.
- Score: **99,62%**. Não é probabilidade calibrada de acerto operacional.
- Original: **136 palavras em inglês**. Recap: **204 palavras em português**, contando itens, incertezas e próximo passo, sem repetir citações. Os idiomas diferem; essa contagem descreve extensão, não mede esforço.
- [Geração original](../solution/reports/recap-evaluation/generate-45725.json) · [Parecer automatizado](../solution/reports/recap-evaluation/judge-45725.json).

### Leitura de Codex para discussão

O assunto aparente é férias, mas o texto inclui `seems able access data for another colleague` e um pedido para verificar/restaurar acessos. Isso é um relato de possível exposição de dados de outro colega, não comprovação de um incidente nem de sua causa.

**Trabalho possível do atendente:** verificar o relato e encaminhá-lo conforme o procedimento de acesso/segurança da operação. Não orientar exploração de dados alheios nem conceder acesso automaticamente.

**O que o protótipo entrega:** `HR Support`, igual ao rótulo da base, com score alto e confirmação humana. A política atual não tem uma identificação independente desse risco nem o destaca como uma dimensão separada da categoria.

**O que o recap captou:** o relato de acesso a dados de outro colega aparece no primeiro item. Porém a geração também supõe “credencial equivocada”, uma causa que o fragmento não comprova; o revisor automatizado apontou essa extrapolação.

**Hipótese de evolução, ainda não implementada/validada:** separar assunto, sinal de risco sustentado em trecho e procedimento humano. Identificação semântica pode sugerir um sinal; regra explícita define o que requer revisão especializada. Esta seleção isolada não valida detector de risco nem política completa.

**Pergunta ao candidato:** qual sinal deveria ser destacado antes da categoria, e qual ação caberia ao atendente versus ao responsável pelo sistema/acessos?

### Decisão do candidato — caso 3

Dhiego considera o assunto RH e o atendimento como investigação de possível incidente. Propôs compreender como o cliente concluiu que via dados de outra pessoa, obter print ou outra evidência e possivelmente envolver Segurança ou Engenharia para consultar logs.

Enumerou hipóteses, sem confirmar nenhuma: confusão de interpretação; problema técnico como RLS, cookie ou cache; erro de preenchimento/vínculo, por exemplo ID errado em um evento exibido no histórico. A investigação deve distinguir problema técnico de preenchimento.

**Consequência:** separar assunto, relato de incidente e causa. O rótulo RH pode permanecer correto; não basta para definir a condução. A interface deve permitir registrar o relato e apoiar investigação humana, sem diagnosticar vulnerabilidade nem afirmar consulta a logs.

## Critério para a próxima decisão

Depois da revisão do candidato: registrar utilidade percebida, danos potenciais, informações necessárias e o fluxo mínimo que valha demonstrar. Não converter três opiniões sobre exemplos em acurácia, minutos economizados, ROI ou aprovação de produção. Não reavaliar os mesmos casos após ajustes e apresentar o resultado como teste independente; qualquer ajuste usa estes casos como desenvolvimento.
