# Desafio 001 — Diagnóstico de Churn → Módulo **Retenção**

Fonte: `challenges/data-001-churn/README.md` (lido na íntegra; a pasta do desafio só contém esse arquivo).

## O que eles pedem

**Área:** Dados / Analytics · **Tipo:** Análise · **Tempo sugerido:** 4–6 h

**Contexto:** RavenStack, SaaS B2B com cerca de 500 contas. O churn subiu, o CS diz que a satisfação está ok e o produto diz que o uso cresceu. O CEO pergunta: *"algo não bate"*.

**Entregável principal: relatório de diagnóstico que responda:**
1. **O que causa o churn?** A causa raiz, não a resposta óbvia, **cruzando as tabelas**.
2. **Quais segmentos estão mais em risco?** Com dados, **identificando contas específicas**.
3. **O que fazer?** Ações concretas, priorizadas e **com impacto estimado**.

**Formato:** livre (PDF, Markdown, notebook, dashboard).

**Diferencial (opcional):** modelo preditivo que funcione, dashboard interativo, automação que o CS usaria amanhã, análise que ninguém pediu e que muda a conversa.

**Process log:** obrigatório.

## Critérios de qualidade (checklist de aceite do módulo)
- [ ] Cruzou as **5 tabelas** ("quem só olhou uma perdeu o ponto")
- [ ] Insights **verificáveis**, mostrando os números
- [ ] Recomendações **acionáveis** (nada de "melhorar a experiência do cliente")
- [ ] Distingue **correlação de causalidade**
- [ ] O **CEO não-técnico** consegue ler e agir

## Dicas deles (viram requisitos)
- Entender a estrutura dos dados **antes** de analisar.
- Cruzar **uso de features × eventos de churn**.
- Comparar **tickets de quem cancelou × quem ficou**.
- Verificar se o "uso cresceu" vale **para todos os segmentos**.
- **Pesar pelo valor**: perder US$ 50/mês ≠ perder US$ 5 mil/mês.
- Cuidado com conclusões apressadas.

## Dados
Ver [`../04-datasets.md`](../04-datasets.md): 5 CSVs (`accounts`, `subscriptions`, `feature_usage`, `support_tickets`, `churn_events`), com chaves `account_id` e `subscription_id`.

## Plano do módulo (sozinho)
1. **Perfil dos dados:** contagens, nulos, datas, ligações entre tabelas, conferência de chaves órfãs.
2. **Tabela mestra por conta:** agrega assinaturas (última MRR, plano, upgrades/downgrades), uso (total, tendência recente × anterior, erros, erros em beta), suporte (volume, 1ª resposta, resolução, escalados, satisfação) e churn (motivo, data, reativação).
3. **Números-base verificáveis:** taxa de churn, MRR perdido **sem duplicidade**, distribuição de motivos só das contas realmente canceladas.
4. **Causa raiz:** comparar canceladas × ativas em cada sinal; testar o "paradoxo do CEO" (uso agregado × uso por segmento, satisfação média × satisfação de quem saiu).
5. **Segmentos em risco:** indústria, canal de aquisição, país, plano, assentos, trial, com taxa e **contas específicas** listadas.
6. **Score de risco explicável** (regras com pesos claros) + modelo preditivo **avaliado com validação cruzada** (dizer com honestidade se o sinal é fraco).
7. **Ações priorizadas com impacto estimado** em MRR protegido.
8. **Relatório para o CEO** (PDF/Markdown) + painel.

## O que o módulo exporta para cooperar
- Lista de contas com risco, valor, sinais e motivo provável → **Suporte** (🟢), **Leads/valor** (🟢)
- Perfil dos segmentos que cancelam e que ficam → **Mídia** (🔵)
