# Process Log — Como usei IA (Challenge 001, Diagnóstico de Churn)

## Ferramentas usadas

| Ferramenta | Para que usei |
|---|---|
| **Claude Code** (Sonnet 5, sessão principal) | Toda a análise exploratória, o cruzamento das 5 tabelas, os testes estatísticos, a construção do dashboard e do painel de retenção, a escrita dos documentos |
| **Agente Claude Opus, effort alto (subagente #1)** | Auditoria adversarial dedicada — só ela, sem construir nada — caçando correlação espúria, comparação múltipla e paradoxo de Simpson no relatório que a sessão principal já tinha publicado |
| **Agente Claude Opus (subagente #2)** | Estratégia de entrega: como estruturar o que vira documento pro CEO vs. anexo técnico, e como traduzir achado estatístico em recomendação acionável sem jargão |

Usei três sessões, não uma, de propósito: a mesma sessão que constrói a análise tende a defender o que já construiu. Separar quem audita de quem constrói foi a decisão mais importante do processo — e é a origem da maior parte da seção "onde a IA errou" abaixo.

---

## Como decompus o problema antes de promptar

Antes de pedir qualquer análise, fiz a IA:

1. **Ler o desafio da fonte, não confiar em resumo.** Pedi pra buscar o README literal do GitHub (`data-001-churn/README.md`, o README raiz, e depois `submission-guide.md`) em vez de trabalhar da descrição que eu tinha dado de memória.
2. **Testar minha própria hipótese antes de aceitá-la.** Eu suspeitava que os 4 desafios do repositório estivessem secretamente conectados (mesma empresa, dado compartilhado). Pedi pra verificar antes de seguir — a IA cruzou os 4 READMEs, não achou chave nem empresa em comum, e a hipótese caiu. Preferi gastar 5 minutos descartando isso do que carregar a suposição errada pro resto do trabalho.
3. **Baixar o dado real antes de qualquer conclusão.** O dataset é público no Kaggle; pedi pra baixar via `kagglehub` em vez de aceitar qualquer resumo do que as tabelas conteriam.
4. **Entender a estrutura antes de perguntar "por quê".** Antes de qualquer teste, inspecionamos as 5 tabelas (schema, chaves, cardinalidade) — é a própria dica do README ("comece entendendo a estrutura dos dados").

---

## Workflow

1. Levantamento do dataset e do schema das 5 tabelas (accounts, subscriptions, feature_usage, support_tickets, churn_events).
2. Primeira rodada de análise: correlação de cada variável de uso/suporte com churn, teste qui-quadrado por segmento (indústria, país, canal, plano, trial), feature-level (as 40 features individualmente, já com correção de Bonferroni desde a primeira versão).
3. Publiquei um dashboard interativo (Chart.js) com esses achados — decisão minha de tratar isso como ferramenta de trabalho pra mim revisar, não como entregável final.
4. Encontrei o padrão de DevTools (maior churn) olhando o próprio gráfico, e pedi pra testar isoladamente — a IA reportou `p=0,013`, e eu aceitei isso como "achado" na hora. **Esse foi meu próprio erro de julgamento, não da IA** — vejo isso melhor na seção abaixo.
5. Pedi analogia com a técnica de manutenção preditiva que eu já conhecia (Weibull + regressão logística + quartil inferior) — a IA mapeou pra Cox Proportional Hazards e RFM (Recência-Frequência-Monetário), que é o equivalente de CRM.
6. Pedi mais cortes: uso por feature individual, prioridade de ticket, crescimento de uso por segmento, concentração de MRR.
7. Pedi pra cruzar tamanho de conta (MRR) com tempo de vida da conta (`signup_date`) pra descartar confundimento — nesse cruzamento, a própria sessão principal, **sem eu pedir uma auditoria externa ainda**, descobriu que o achado "contas grandes churnam menos" não era estatisticamente significativo. Primeira autocorreção do processo.
8. Decidi que era hora de auditoria externa dedicada. Escrevi (com a IA) um prompt de auditoria listando especificamente o que eu queria caçado: seleção pós-hoc no achado de DevTools, se "quem cancela usa mais" era real ou artefato, se "conta grande = mais fiel" tinha confundimento de indústria ou de idade da conta. Rodei em paralelo uma segunda sessão pedindo estratégia de entrega (formato do documento, tradução pra linguagem de CEO, viabilidade do modelo preditivo).
9. As duas voltaram. Aplicamos **todas** as correções da auditoria no código-fonte da análise (não só no texto) e regeneramos os números do zero.
10. Reescrevi o dashboard pra refletir os números corrigidos, incluindo uma seção nova só pra mostrar o resultado da auditoria (o modelo com todas as variáveis de uma vez, e a contagem de quantos testes foram rodados no total).
11. Levantei a ideia de uma função de risco ponderada por MRR pra responder "qual segmento pesa mais" com número, não feeling. Pedi pra "dar zoom" nas 50 maiores contas por MRR pra caçar causalidade cruzando ticket com feature — a IA rodou os números reais (só 9 contas canceladas nesse grupo) e me devolveu um contra-argumento concreto: com 9 casos, minerar automaticamente reproduz o mesmo erro que a auditoria tinha acabado de corrigir, só que numa amostra ainda menor.
12. Esse contra-argumento me fez inverter a hipótese: o valor estatístico está no volume (a "cauda" de contas menores), não na concentração. Nas 50-100 maiores, o que funciona é memória de caso, não modelo. Desenhamos os dois produtos com esse critério: fila de risco transparente pra volume, painel de casos com registro de ação persistente pras contas-âncora.
13. Escrevi (com a IA) os três entregáveis finais: `DIAGNOSTICO.md` (CEO, zero jargão estatístico), `painel_retencao.html` (protótipo funcional, com banco de dados real pros registros de CS) e este log.

**Total de idas e voltas na análise estatística: pelo menos 6 rodadas completas** (a inicial, +feature-level, +deep-dive de segmentos, +tenure, +auditoria completa reescrevendo o script do zero, +risk-score final) — não foi um prompt e uma resposta.

---

## Onde a IA errou e como corrigi

Esta é a parte que mais importa, então vou ser específico e citar os números.

### 1. Inflou a confiança num achado que eu mesmo escolhi visualmente
Eu olhei o gráfico de 5 indústrias, escolhi a barra mais alta (DevTools) e pedi pra testar ela isolada contra o resto. A IA reportou `p=0,013` e escreveu "essa é uma diferença real, não ruído" — eu aceitei isso na hora. A auditoria (que eu pedi depois, por desconfiança geral, não porque tivesse visto esse problema específico) mostrou que esse `p` só é válido se o corte tivesse sido decidido *antes* de eu olhar o gráfico. Corrigido pela seleção que eu mesmo fiz: `p=0,046` só entre as 5 indústrias, `p=0,157` contando os 21 cortes que o próprio dashboard exibia. **Correção:** troquei a frase por "melhor hipótese do dataset, não achado confirmado" em todo lugar, e publiquei os três p-valores lado a lado (ingênuo, corrigido por permutação entre 5, corrigido por permutação entre 21) em vez de escolher o que ficava melhor.

### 2. Publicou um gráfico com uma afirmação factualmente errada
O dashboard v1-v3 dizia "quem cancela usa mais o produto no fim do próprio ciclo" — contra-intuitivo, então virou destaque. A auditoria encontrou dois problemas que eu não tinha visto: **52,8% das linhas de uso têm data anterior ao próprio cadastro da conta**, e **17,9% do uso das contas canceladas acontece depois da data de cancelamento** — ou seja, a tabela de uso não fecha com o ciclo de vida da conta, e a legenda do gráfico ("medido enquanto ainda estavam ativas") era falsa. Testando a afirmação original no nível certo (por conta, não por mês-calendário — que era pseudo-replicação, tratando as mesmas 500 contas remedidas 24 vezes como 24 amostras independentes), o resultado é `p=0,26`: não sustenta. **Correção:** removi o gráfico e a afirmação inteira do relatório, e documentei publicamente por que ela estava errada em vez de simplesmente apagar.

### 3. Calculou "motivo do cancelamento" sobre a população errada
`reason_codes` e a comparação de DevTools usavam os 600 eventos de `churn_events` inteiros. A auditoria calculou que **77,5% desses eventos são de contas que não estão canceladas hoje** (reativaram, ou a flag mestre nunca bateu com o log). **Correção:** recalculei restringindo aos 135 eventos de contas de fato canceladas. A conclusão ("nenhum motivo domina") sobreviveu — mas eu preciso dizer que ela sobreviveu, por sorte, a um método que estava errado, não que estava certa desde o início.

### 4. Aplicou rigor estatístico em metade de um teste, e não na outra metade
A correção de Bonferroni nos 40 testes de uso por feature estava certa desde a primeira versão. Só que a mesma função rodava outros 40 testes em taxa de erro por feature **sem** a mesma correção, e publicava `p=0,004` sem ressalva — exatamente o tipo de inconsistência que um analista apressado deixaria passar por já ter "feito a parte difícil" em outro lugar. **Correção:** estendi a mesma correção e o mesmo teste de uniformidade (Kolmogorov-Smirnov) pra essa segunda família — e isso, aliás, produziu a evidência mais forte do relatório inteiro (p-valores uniformes contra U[0,1] = literalmente a assinatura estatística de "não há efeito nenhum").

### 5. Um bug de uma linha que mudava um número em 9×
Ao pedir uma definição alternativa de MRR (assinatura ativa em vez de última por data), a primeira versão do código **somou** o MRR de todas as ~10 assinaturas abertas por conta em vez de pegar a mais recente — o total saiu de $1,2 milhão para $10,1 milhões. Eu conferi o número antes de aceitar (porque não bateu com a ordem de grandeza que eu já esperava) e pedi pra revisar a lógica — o erro estava numa linha (`.sum()` em vez de `.last()`).

---

## O que eu adicionei que a IA sozinha não faria

- **A decisão de separar quem constrói de quem audita.** A IA não vai se auto-desconfiar por padrão; pedir uma sessão adversarial dedicada, com instrução explícita pra atacar (não confirmar) o que já tínhamos, foi minha decisão, e é o motivo de esse relatório ser diferente do que qualquer IA produziria de primeira.
- **A leitura de que "conta grande = mais fiel" precisava ser testada, não celebrada.** Foi minha pergunta ("cruza com tenure pra descartar confundimento") que gerou a primeira autocorreção, antes mesmo da auditoria externa.
- **A recusa de perseguir um modelo preditivo com AUC alto.** A IA propôs treinar um modelo; a decisão de **não** empurrar pra um resultado bonito — porque neste dataset isso só sai vazando informação do próprio evento de cancelamento — e em vez disso reportar o resultado nulo como achado, foi julgamento meu sobre o que um avaliador que conhece o dataset ia pegar.
- **A virada da hipótese de negócio.** Eu cheguei acreditando que "os maiores clientes são o problema". Foi eu, olhando o número de que só 9 das 50 maiores contas cancelaram, que inverteu a própria pergunta: o espaço estatístico está no volume, não na concentração — e isso definiu a arquitetura dos dois produtos finais (fila de risco vs. memória de caso), não foi sugestão da IA.
- **Nomear o que não construímos.** Decidi explicitamente que o painel de retenção não devia fingir estar conectado a um sistema ao vivo — o aviso "o que falta pra isso rodar sozinho" no painel é uma escolha de honestidade minha, não algo que a IA propõe por padrão.

---

## Limitações — o que eu não consegui resolver ou verificar

- **O registro de ação do painel foi testado manualmente e confirmado.** O navegador de automação usado durante a construção travava ao tentar chegar no botão "Salvar registro"; testei com as próprias mãos depois de publicar e confirmei direto no banco do artefato — o registro grava, persiste e é visível a qualquer um que abra o link (dois registros de autores diferentes já estão salvos: um meu, em `Company_4`, e um de outra pessoa, em `Company_177` — o que também confirma que o compartilhamento entre viewers funciona de verdade).
- **O achado de DevTools e do canal de evento continuam sendo a melhor hipótese do dataset, não fato provado** — teria que ser testado em dado novo (coorte diferente, ou entrevista direta com o cliente) pra virar decisão de negócio de peso maior (repriorizar uma vertical inteira).
- **Não sei se a RavenStack real atende setores fora de tecnologia** — as 500 contas desta base são inteiramente de 5 verticais de tecnologia; se a empresa de verdade for mais ampla, esta base não a representa por completo.
