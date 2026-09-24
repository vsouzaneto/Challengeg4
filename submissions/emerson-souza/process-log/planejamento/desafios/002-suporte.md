# Desafio 002 — Redesign de Suporte → Módulo **Suporte**

Fonte: `challenges/process-002-support/README.md` (lido na íntegra; a pasta do desafio só contém esse arquivo).

## O que eles pedem

**Área:** Operações / CX · **Tipo:** Diagnóstico + Automação + **Build** · **Tempo sugerido:** 4–6 h

**Contexto:** cerca de 30 mil tickets por ano (email, chat, telefone, redes sociais). O time está sobrecarregado, o tempo de resolução subiu e a satisfação caiu. O Diretor de Operações pede: *"onde estamos perdendo tempo, o que dá pra automatizar com IA, e me mostre que funciona — quero ver algo rodando"*.

### 1. Diagnóstico operacional (obrigatório, com o Dataset 1)
- **Onde o fluxo trava?** Gargalos por canal, prioridade e tipo, e quais **combinações** geram os piores tempos.
- **O que impacta a satisfação?** Tempo de resposta? Canal? Tipo de problema?
- **Quanto estamos desperdiçando?** Em **horas** e, se possível, em **custo**. Onde está o maior desperdício recuperável?

### 2. Proposta de automação com IA (obrigatório, com **ambos** os datasets)
- **O que automatizar:** classificação, roteamento, respostas sugeridas, triagem de prioridade, detecção de duplicatas.
- **O que NÃO automatizar:** tickets que exigem julgamento humano, **com exemplos dos dados**.
- **Como funcionaria:** ticket entra → etapas → onde a IA atua → onde o humano intervém.

### 3. Protótipo funcional (diferencial)
Classificador (texto → categoria + confiança), respostas sugeridas por tickets similares, roteador que categoriza e prioriza, dashboard de gargalos.

### 4. Process log (obrigatório)

## Critérios de qualidade (checklist de aceite)
- [ ] Usou **os dois datasets** ("o poder está no cruzamento")
- [ ] Diagnóstico com **números concretos**
- [ ] Automação **realista** ("automatizar 100% é red flag")
- [ ] Separa onde a IA ajuda de onde o humano é insubstituível
- [ ] Protótipo funciona com **dados reais**, não com 3 exemplos escolhidos a dedo

## Dicas deles (viram requisitos)
- O Dataset 2 (48 mil textos em 8 categorias) serve para **treinar e testar** o classificador.
- Ser específico: *"8 categorias com X% de acurácia usando embeddings + zero-shot"*.
- Pensar no dia a dia do **agente de suporte**.
- Mostrar **ROI**: *"automação X economiza Y horas/mês"*.
- Saber **onde parar**.

## Dados
Ver [`../04-datasets.md`](../04-datasets.md): Dataset 1 (cerca de 30 mil tickets, com métricas + texto de descrição e resolução) e Dataset 2 (cerca de 48 mil textos de TI com `Topic_group`).

## Plano do módulo (sozinho)
1. **Perfil + limpeza:** tempos (FRT, resolução) em horas, status, tickets sem resolução, satisfação nula.
2. **Gargalos:** matriz canal × prioridade × tipo com mediana/percentis de tempo e volume; as piores combinações.
3. **Satisfação:** efeito de cada variável (comparações controladas + modelo simples interpretável), cuidando de correlação × causa.
4. **Desperdício:** horas acima de uma meta (SLA) por combinação × custo/hora **configurável** → onde está a maior economia recuperável.
5. **Classificador:** baseline (TF-IDF + modelo linear) × embeddings × zero-shot com LLM, com **acurácia/F1 por categoria num conjunto de teste separado** e matriz de confusão.
6. **Automação proposta:** fluxo com limiares de confiança (alta → automático; baixa → humano), o que **nunca** automatizar (ex.: prioridade Critical, reclamação sensível, cobrança contestada), com exemplos reais.
7. **Protótipo no painel:** colar/importar ticket → categoria + confiança + prioridade sugerida + fila + resposta sugerida por tickets similares + "vai para humano?".
8. **ROI:** horas/mês economizadas por automação, com premissas explícitas.

## O que o módulo exporta / recebe
- **Recebe do Churn** 🟢: tickets das contas em risco (sem texto → só a parte operacional).
- **Exporta para Churn** 🟡: clientes com experiência ruim de suporte.
- **Exporta para Leads** 🟡: tickets "Product inquiry" como oportunidades.
