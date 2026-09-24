# Desafio 004 — Estratégia Social Media → Módulo **Mídia**

Fonte: `challenges/marketing-004-social/README.md` (lido na íntegra; a pasta do desafio só contém esse arquivo).

## O que eles pedem

**Área:** Marketing · **Tipo:** Análise + Estratégia · **Tempo sugerido:** 4–6 h

**Contexto:** a empresa investe em conteúdo **orgânico e patrocinado** (Instagram, TikTok, YouTube), com criadores e influenciadores de vários tamanhos. O Head de Marketing tem 52 mil posts e quer saber *"o que gera engajamento de verdade, se vale patrocinar influenciadores, e qual deveria ser a estratégia"*, e diz que *"uma ferramenta pra acompanhar no dia a dia, melhor ainda"*.

### 1. Análise de performance (obrigatório)
- **O que gera engajamento?** Por plataforma, tipo de conteúdo, categoria e tamanho de criador, **indo além do óbvio**.
- **Patrocínio funciona?** Orgânico × patrocinado em engajamento, alcance e **custo implícito**. Em que condições vale? Com que tipo de influenciador?
- **Qual audiência engaja mais?** Diferenças por plataforma, tipo e categoria.
- **O que NÃO funciona?**

### 2. Estratégia recomendada (obrigatório)
- **Onde concentrar:** plataforma, tipo, **frequência**, faixa de criador.
- **Política de patrocínio:** patrocinar ou não, em que condições, com que perfil e com qual **limite mínimo de seguidores/engajamento**.
- **O que parar de fazer.**
- **Quick wins** para esta semana.

### 3. Algo a mais (diferencial)
Modelo preditivo de engajamento, **dashboard para o time acompanhar**, gerador de recomendações de conteúdo, análise de **combinações de hashtags**, clustering de audiência.

### 4. Process log (obrigatório)

## Critérios de qualidade (checklist de aceite)
- [ ] Vai além de "engajamento médio por plataforma" (*"é a tabela 1, não a conclusão"*)
- [ ] Insights acionáveis: o Head sabe o que fazer na **segunda-feira**
- [ ] Comparação orgânico × patrocinado **justa**, controlando **tamanho do criador, plataforma e categoria**
- [ ] Recomendações **priorizadas** (nada de lista de 20 ideias sem ordem)
- [ ] Executivo não-técnico entende **em 5 minutos**

## Dicas deles (viram requisitos)
- **Segmentar antes** de analisar (plataforma, período, categoria).
- Ser específico: *"vídeos de 30–60 s em Tech, criadores de 10K–50K, geram 3,2x mais shares"*.
- *"Engagement rate isolado mente"*: contextualizar com alcance, plataforma e tamanho do criador.
- Toda recomendação diz **o quê, para quem, quando e com que evidência**.
- Cuidado com o **viés de sobrevivência**: quantos posts tiveram engajamento zero?

## Dados
Ver [`../04-datasets.md`](../04-datasets.md): cerca de 52 mil posts com plataforma (YouTube, TikTok, Instagram, Bilibili, RedNote), conteúdo, métricas, criador, audiência, patrocínio e data.

## Plano do módulo (sozinho)
1. **Perfil + qualidade:** distribuição de métricas (caudas longas), posts com engajamento zero, conferir se o engagement rate informado bate com a fórmula.
2. **Métricas justas:** engajamento **relativo ao criador e à plataforma** (ex.: comparar com a mediana da mesma faixa de seguidores na mesma plataforma), e não a média crua.
3. **Drivers de engajamento:** plataforma × tipo × categoria × faixa de criador × duração × hashtags × dia/horário, com tamanho de amostra mostrado.
4. **Orgânico × patrocinado controlado:** comparação **dentro do mesmo estrato** (plataforma + categoria + faixa de seguidores) e efeito por tipo de divulgação (disclosure).
5. **Audiência:** idade, gênero e local por plataforma/categoria; clusters.
6. **O que não funciona** + viés de sobrevivência.
7. **Estratégia priorizada:** onde concentrar, política de patrocínio com limites numéricos, parar de fazer, quick wins.
8. **Painel de acompanhamento** + (diferencial) modelo preditivo de engajamento avaliado honestamente.

## O que o módulo exporta / recebe
- **Exporta para Leads** 🔵: perfil de audiência que engaja.
- **Recebe do Churn** 🔵: perfil dos segmentos que cancelam/ficam (público de campanha).
- **Recebe de Leads** 🔵: setores e produtos que mais fecham.
