# FocusScore — lógica de priorização

## Pergunta de negócio
Em vez de perguntar apenas “qual oportunidade tem maior probabilidade de ganhar?”, a solução foi orientada para:

> Em que oportunidade deve o vendedor investir o próximo minuto?

## Princípios
1. O score deve ser explicável.
2. Deve utilizar informação disponível no momento da decisão.
3. Deve evitar data leakage.
4. Deve transformar-se em comportamento dentro do CRM.
5. Não deve substituir julgamento humano sem evidência suficiente.

## Contexto considerado
- etapa comercial
- produto
- setor
- região
- dimensão da empresa
- receita potencial
- histórico comercial
- vendedor
- contexto da oportunidade

## Leakage evitado
Não utilizámos `close_date` ou `close_value` para priorizar oportunidades abertas.

## Explainability operacional
O FocusScore é traduzido para prioridade, estrelas, tags como 🔥 Prioridade Alta, 💰 Alto Valor e ⚠️ Em Risco, além de atividade recomendada e deadline.

## Stage vs Priority
**Stage** representa onde o negócio está no processo comercial.

**Priority** representa onde o vendedor deve concentrar atenção.
