<!-- Gerado por solution/analysis/05_report.py a partir de docs/templates/diagnostico.md.tmpl. Não edite à mão. -->

# Diagnóstico operacional

O Diretor de Operações fez três perguntas: **onde o fluxo trava**, **o que impacta a satisfação** e **quanto estamos desperdiçando**. Este documento responde a cada uma separando três tipos de afirmação:

- **Observado:** contagem feita direto no arquivo.
- **Limitação:** o que os dados não permitem afirmar.
- **Cenário estimado:** conta com premissas explícitas, que precisam ser validadas antes de virar decisão.

## Antes dos números: o que a auditoria encontrou

O Dataset 1 (métricas operacionais, 8.469 tickets) tem padrão de dado sintético. Os pontos que mais afetam o diagnóstico:

- **Distribuições uniformes:** Tipo, prioridade, canal, status e nota de CSAT têm frequências estatisticamente iguais (qui-quadrado, menor p = 0,11).
- **Tempos inválidos:** Os campos são timestamps (não durações), todos numa janela de 27h, sem horário de abertura. Em 49,3% dos fechados (1.365 de 2.769) a resolução é anterior à 1ª resposta.
- **Satisfação:** Kruskal-Wallis (tipo, prioridade, canal, gênero, produto) e Spearman (duração, idade) nos 2.769 tickets fechados: menor p = 0,25.
- **Texto:** Placeholder literal {product_purchased} em 100,0% das descrições; resoluções são frases aleatórias. TF-IDF + regressão logística (validação cruzada de 5 folds, vetorizador ajustado dentro de cada fold) acerta o tipo em 18,7%, contra 20,7% chutando a classe mais comum.

Por isso **não apontamos um "canal gargalo" nem um "driver de satisfação"**. Com estes dados, isso seria apresentar ruído como insight. O que entregamos é o que o arquivo sustenta, somado a uma metodologia pronta para rodar sobre os dados reais da operação.

## 1. Onde o fluxo trava?

**Observado (descritivo):**
- 67,3% dos registros não estão fechados. 33,3% abertos e 34,0% aguardando o cliente. Contagem descritiva: sem datas de abertura não dá para medir envelhecimento da fila.
- 100% dos tickets abertos não têm registro de primeira resposta.
- 34,0% dos tickets aguardam resposta do cliente.

**Testes por segmento:**
- Não detectamos associação entre status e canal (p = 0,77).
- Não detectamos associação entre status e prioridade (p = 0,23).
- Não detectamos associação entre status e tipo (p = 0,34).
- Não detectamos associação entre status e canal × prioridade (p = 0,50).

**Leitura:** o status dos tickets não difere de forma detectável entre canais, prioridades ou tipos, e o painel mostra cada segmento com intervalo de confiança. O arquivo não tem data de abertura nem tempos consistentes, então **não é possível medir onde o fluxo trava em tempo**. O primeiro passo com dados reais é registrar abertura, primeira resposta e resolução por ticket e repetir estes mesmos testes.

## 2. O que impacta a satisfação?

**Testes realizados** (tickets fechados, que são os únicos com nota):

| Variável | Teste | p | ε² | Diferença não detectável até |
|---|---|---|---|---|
| canal | Kruskal-Wallis | 0,28 | 0,0014 | ±0,15 ponto |
| prioridade | Kruskal-Wallis | 0,63 | 0,0006 | ±0,15 ponto |
| tipo | Kruskal-Wallis | 0,70 | 0,0008 | ±0,17 ponto |
| gênero | Kruskal-Wallis | 0,63 | 0,0003 | ±0,13 ponto |

Médias por canal com IC 95%: Phone 2,95 (IC 2,85–3,06); Email 2,96 (IC 2,86–3,07); Social media 2,97 (IC 2,87–3,07); Chat 3,08 (IC 2,98–3,19).

**Leitura:** não detectamos associação nos testes realizados. Isso **não prova** que canal, prioridade ou tipo não importam numa operação real. Diz apenas que, com este volume, diferenças do tamanho indicado na última coluna não se distinguem do acaso.

## 3. Quanto estamos desperdiçando?

**Cenário estimado**, não medição. Estimativa para 30.000 tickets/ano. Combina referências medidas no teste do roteamento com premissas a validar; não é medição da operação. Economias já descontam conferência, revisão e erros residuais.

Para 30.000 tickets/ano, as etapas analisadas somam cerca de **6.986 h/ano**. Delas, **2.514 h/ano são recuperáveis** (≈ 1,4 agente em tempo integral; ≈ R$ 113.152/ano a R$ 45/h).

| Etapa | Horas/ano (hoje) | Recuperável/ano | Como foi calculado |
|---|---|---|---|
| Triagem manual (ler, classificar, rotear) | 1.500 | 816 | Só nos tickets roteados automaticamente, descontando a conferência rápida que continua existindo. |
| Retrabalho por roteamento errado | 1.125 | 486 | Nos automáticos, a taxa de erro manual é trocada pelo erro medido do roteamento; o restante continua manual. Fica negativo se o erro automático superar o manual. |
| Follow-up de tickets aguardando o cliente | 1.361 | 816 | Lembretes e fechamento por inatividade. Cenário sem evidência nos dados: validar em piloto. |
| Redação de respostas | 3.000 | 396 | Economia líquida (já descontada a revisão) apenas nos tickets elegíveis a rascunho: exclui casos só-humanos e escalações. |

**Onde está o maior desperdício recuperável:** triagem (816 h) e follow-up de pendências (816 h). Ambos são automações baratas e mensuráveis. O rascunho de resposta com IA generativa rende menos (396 h), porque a economia é líquida da revisão humana e não se aplica a casos só-humanos nem a escalações.

**Sensibilidade:** mesmo com roteamento automático bem abaixo do medido e economia de rascunho menor, o cenário ainda recupera 1.652 h/ano.

| Roteamento automático | Economia líquida com rascunho | Horas recuperáveis/ano |
|---|---|---|
| 30,0% | 15% | 1.652 |
| 30,0% | 25% | 1.810 |
| 50,0% | 15% | 2.051 |
| 50,0% | 25% | 2.209 |
| 65,3% | 15% | 2.356 |
| 65,3% | 25% | 2.514 |

### Premissas

Todas são editáveis na calculadora do protótipo. O tipo indica a origem de cada uma: **medido** no Dataset 1, **referência** medida no teste do roteamento (Dataset 2, TI interna) ou **premissa** a validar.

| Premissa | Valor | Tipo | Fonte / como validar |
|---|---|---|---|
| Volume anual de tickets | 30000 tickets/ano | premissa | Enunciado do desafio (o arquivo tem 8.469 tickets). |
| Custo carregado por hora de agente | 45 R$/h | premissa | Validar com RH/financeiro. |
| Triagem manual por ticket | 3 min | premissa | Validar cronometrando ~50 triagens. |
| Conferência residual por ticket roteado automaticamente | 0,5 min | premissa | O agente ainda bate o olho na categoria ao abrir o ticket. |
| Tickets roteados automaticamente | 0,6531 fração | referencia | Medido no teste (7176 tickets de TI interna) com a política completa da API. Pressupõe re-treino com o histórico da operação. |
| Acerto nos roteados automaticamente | 0,9492 fração | referencia | Medido no teste; IC 95% 94,3%–95,6%. |
| Roteamento errado na triagem manual | 0,15 fração | premissa | Medir por reatribuições no helpdesk. |
| Retrabalho por ticket mal roteado | 15 min | premissa | Inclui reler, reatribuir e retomar o contexto. |
| Tickets aguardando o cliente | 0,3402 fração | medido | Contagem do Dataset 1 (mix sintético). |
| Follow-ups manuais por ticket pendente | 2 follow-ups | premissa | Validar no histórico do helpdesk. |
| Tempo por follow-up | 4 min | premissa | Validar no histórico do helpdesk. |
| Follow-ups automatizáveis (líquido) | 0,6 fração | premissa | Sem evidência nos dados; parte dos clientes exige contato humano. Validar em piloto. |
| Redação de uma resposta | 6 min | premissa | Validar cronometrando respostas. |
| Economia líquida com rascunho (já descontada a revisão) | 0,25 fração | premissa | Conservadora; o agente lê, ajusta e aprova. Validar em piloto A/B. |
| Casos só-humanos (reembolso e cancelamento) | 0,407 fração | medido | Contagem do Dataset 1 (mix sintético). |
| Tickets escalados por sinal de risco | 0,0654 fração | referencia | Medido no teste com a política da API. Pode sobrepor-se aos casos só-humanos (desconto conservador). |

## Limitações

- O Dataset 1 tem padrão de dado sintético (distribuições uniformes, placeholders no texto, resoluções aleatórias).
- Tempos de resposta/resolução não são utilizáveis (49% das resoluções antes da 1ª resposta; sem data de abertura). Não medimos gargalo de tempo por canal ou prioridade.
- Não detectar associação não prova ausência de efeito: diferenças pequenas podem não ser detectáveis com este volume.
- O roteamento foi medido em tickets de TI interna (Dataset 2). Aplicado aos tickets do Dataset 1 ele quase não roteia automaticamente (o guarda de domínio barra o texto). Em produção, re-treinar com o histórico da operação.
- Minutos por tarefa, taxa de roteamento errado, custo/hora e automação de follow-up são premissas a validar, não medições.

## Próximos passos para transformar o cenário em medição

1. Exportar do helpdesk real: abertura, primeira resposta, resolução, reatribuições e CSAT por ticket.
2. Rodar `02_diagnostico.py` sobre esse export. Os testes e a calculadora já estão prontos.
3. Cronometrar cerca de 50 triagens e 50 respostas para substituir as premissas de minutos.
4. Fazer um piloto de 4 semanas com roteamento automático em modo sombra (sugere sem aplicar) para medir cobertura e acerto no domínio da operação.
