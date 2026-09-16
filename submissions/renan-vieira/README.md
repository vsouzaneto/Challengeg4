# Submissão — Renan Vieira — Challenge 001

## Sobre mim

- **Nome:** Renan Vieira
- **LinkedIn:** https://www.linkedin.com/in/vieira-vieira
- **Challenge escolhido:** 001 — Diagnóstico de Churn

---

## Executive Summary

O churn da RavenStack não é um problema de segmento nem de satisfação: é um problema de **ativação de clientes novos que piorou conforme a aquisição escalou**. A cohort que assinou em 2024 churna 3x mais rápido nos primeiros dois meses (48,7%) do que a cohort de 2023 (15%), e isso acontece de forma uniforme entre indústria, plano, canal, MRR e perfil de uso — nenhum desses atributos discrimina quem sai. O time de produto está certo que "uso total cresceu" (ficou estável), mas isso mascara uma queda de mais de 90% no uso por conta, porque a base de clientes triplicou sem escalar onboarding junto. A recomendação central não é uma campanha de retenção segmentada (não existe segmento de risco isolável), é consertar a ativação nos primeiros 60 dias e monitorar isso por cohort, não por score individual de conta.

---

## Solução

### Abordagem

Comecei validando a integridade das 5 tabelas (joins, duplicatas, nulos) antes de qualquer análise — isso já revelou que `accounts.churn_flag` (status atual) e `churn_events` (histórico completo, incluindo reativações) contam histórias diferentes, e usei `churn_events` como fonte de verdade para "essa conta já churnou".

Depois testei as duas afirmações contraditórias do CEO ("uso cresceu" e "satisfação ok") isoladamente, cruzando as 5 tabelas por conta. Quando a segmentação por atributo (indústria/plano/canal/MRR) não mostrou diferença, rodei uma clusterização comportamental (PCA + K-Means/GMM/K-Medoids) para testar se havia uma estrutura de risco que os cortes simples não estavam capturando. Só quando isso também não discriminou risco, testei a hipótese de cohort/tempo — que foi o que resolveu a contradição.

### Resultados / Findings

1. **"Uso cresceu" é uma ilusão de escala.** O uso total mensal ficou estável (~10-11 mil eventos/mês) entre meados de 2023 e o fim de 2024, mas a base ativa quase triplicou (92 → 250 contas). Uso por conta caiu de ~500+/mês para ~40-48/mês (queda de mais de 90%).
2. **"Satisfação ok" também é verdade, e não importa.** Satisfação média é praticamente idêntica entre quem churnou (3,98) e quem ficou (3,98). A métrica não captura o que está causando a saída.
3. **Nenhum atributo de conta discrimina risco de churn**: taxa de churn é uniforme entre indústria (67-74%), plano (68-72%), canal (60-75%) e MRR (contas que churnam têm MRR médio igual ao das que ficam, ~$20K). Uso individual nos 60 dias antes do churn também não prediz saída (queda em só 49% dos casos, quase um cara-ou-coroa). Uma clusterização comportamental (PCA + K-Means/GMM/K-Medoids, testada em k=2 a k=4) confirmou: só k=2 tem concordância robusta entre algoritmos, e os dois clusters resultantes têm taxa de churn quase idêntica (71% vs 69,7%).
4. **O sinal real é de cohort, não de perfil.** O tempo médio até o primeiro churn caiu de 6 meses (cohort 2023) para 1 mês (cohort 2024). O % de contas que churna nos primeiros 2 meses de vida saltou de 15% para 48,7% entre os dois cohorts — mesmo com a aquisição crescendo de forma constante (55→80 contas/trimestre). Isso é consistente com o achado #1: a empresa escalou aquisição sem escalar capacidade de ativação.
5. **Motivo declarado não aponta uma causa única** (features 19%, support 17%, budget 17%, unknown 16%, competitor 15%, pricing 15%), mas o motivo "unknown" é o que mais cresce (266,7% entre H1 e H2 de 2024) — a empresa está perdendo visibilidade sobre o porquê da saída à medida que o volume aumenta.
6. **Enterprise é o alerta prospectivo.** Hoje não é o segmento com maior churn em volume, mas é o que mais acelera em termos relativos (+171,7% de eventos de churn entre H1 e H2 de 2024, mais que Pro e Basic) — o segmento mais valioso está entrando na mesma trajetória de deterioração.

*(Gráfico da curva de retenção por cohort de signup, mostrando a divergência entre 2023 e 2024, está anexado como `curva_retencao_cohort.png` / disponível no notebook de análise.)*

### Recomendações

Priorizadas por causa raiz, não por sintoma:

1. **[P0] Consertar ativação nos primeiros 60 dias**, não CSAT nem pricing. É onde a deterioração está concentrada e é a única variável que realmente mudou entre cohorts. Ação concreta: mapear o fluxo de onboarding atual e identificar o que não escalou junto com a aquisição (suporte humano, conteúdo de ativação, tempo de resposta ao primeiro contato).
2. **[P0] Trocar o KPI de churn que o CEO acompanha.** Parar de olhar `churn_flag` ou contagem mensal bruta (cresce mecanicamente com o tamanho da base) e passar a acompanhar **% de churn por cohort de entrada, nos primeiros 60 dias** — é a métrica que expôs o problema real e vai mostrar se as ações de onboarding estão funcionando, mês a mês.
3. **[P1] Corrigir a captura de motivo de churn.** "Unknown" crescendo mais rápido que qualquer motivo real significa que a empresa está perdendo a capacidade de diagnosticar suas próprias perdas à medida que cresce — provavelmente processo manual de exit que não escalou.
4. **[P1] Monitorar Enterprise de forma proativa**, mesmo sem sinal de volume ainda: é o segmento de maior receita por conta e está acelerando mais rápido que os demais em termos relativos.
5. **[P2] Não construir um modelo de propensão a churn por conta.** Testamos clusterização e comparação de atributos e nenhum discrimina risco individual o suficiente para justificar o investimento — evita gastar tempo de engenharia de dados num caminho que já mostrou não funcionar aqui.

### Limitações

- O dataset é sintético e termina em 2024-12-31; os últimos ~15-30 dias têm sinais de censura (ex: 24 assinaturas com `end_date` exatamente na última data do dataset, bem acima da média diária de ~1,8), então tratei o último mês com cautela nas séries temporais.
- Não há dados operacionais externos (o que mudou no time de CS, pricing, onboarding ao longo de 2024) para confirmar a causa raiz do achado #4 além do padrão estatístico — a recomendação é uma hipótese fortemente sustentada pelos dados, não uma causa comprovada por uma fonte externa.
- Testei um score de risco por conta baseado em uso nos primeiros 30 dias e ele **não se validou** (grupo "flagado" churnou menos que o resto, 41,7% vs 62,9%, numa amostra de 47 contas) — reportado aqui porque é evidência de que os atributos de conta realmente não carregam sinal individual neste dataset, não só uma tentativa que deu errado.
- Amostra de clientes por cohort recente (2024 Q4) é pequena, então os pontos finais da curva de retenção para essa cohort têm mais ruído.

---

## Process Log — Como usei IA

> **Preencher com sua reflexão pessoal — o ponto desta seção é mostrar seu julgamento, não o do Claude.**

### Ferramentas usadas

| Ferramenta | Para que usou |
|---|---|
| Claude (chat + code execution) | Tratamento e cruzamento das 5 tabelas, testes de hipótese, clusterização (PCA/K-Means/GMM/K-Medoids), construção e validação do diferencial, redação do relatório |
| *adicionar outras que você usou* | |

### Workflow

1. Planejamento da abordagem (fases do diagnóstico) antes de tocar nos dados
2. Tratamento e validação de integridade das 5 tabelas
3. Teste das duas afirmações do CEO isoladamente, com dados
4. Segmentação por atributo → clusterização comportamental → hipótese de cohort/tempo (nessa ordem, descartando cada uma antes de ir pra próxima)
5. Construção do diferencial (monitor de cohort) e validação nos próprios dados antes de propor
6. Consolidação no relatório seguindo o template

### Onde a IA errou e como corrigi

- O script de tratamento (skill de clustering) detectou `current_mrr` como coluna "identificadora" e removeu ela junto com 7 linhas por "chave duplicada" — um falso positivo claro, já que MRR é uma variável central de negócio, não um ID. Percebi lendo os logs de execução da conversa: a leitura da IA não batia com a estrutura da tabela, que deixava claro que `current_mrr` era uma métrica de negócio recorrente, não um identificador único — por isso pedi a correção manual.
- Na Fase 2, comparei `max_mrr` (pico histórico) de quem churnou com `current_mrr` (atual) de quem ficou — colunas diferentes para grupos diferentes, o que criou uma diferença de MRR que não existia de verdade. Foi corrigido comparando a mesma métrica nos dois grupos. Fui eu quem pediu para prosseguir nessa etapa, e foi a própria IA quem identificou e sinalizou o erro antes de fechar o diagnóstico. Ao longo de toda a execução, fui lendo os logs para garantir que a IA estava seguindo o plano desenhado nas fases acima, e foi nessa checagem que o erro apareceu.
- O primeiro desenho do diferencial (flag de risco por uso baixo nos primeiros 30 dias) não se sustentou na validação — o grupo flagado churnou MENOS que o resto. Isso foi testado antes de entregar, não depois.

### O que eu adicionei que a IA sozinha não faria

Validei a definição de churn proposta pela IA (usar `churn_events` como fonte de verdade em vez do `churn_flag` estático, já que captura reativações e todo o histórico de saída), fazendo sentido dessa escolha porque ela separa "já churnou alguma vez" de "está churnado hoje", que são perguntas diferentes. Sobre k=2 vs k=4 no clustering: acompanhei o argumento de concordância entre os três algoritmos (K-Means/GMM/K-Medoids); só k=2 teve consenso robusto entre eles, então confiei nesse critério em vez de forçar mais segmentos.

---

## Evidências

- [ ] Screenshots das conversas com IA
- [ ] Screen recording do workflow
- [ ] Chat exports
- [ ] Git history (se construiu código)
- [ ] Outro: _____________

---

*Submissão enviada em: 15/09/2026*
