# Submissão — Ricardo Aoyagi — Challenge 001

## Sobre mim

- **Nome:** Ricardo Aoyagi
- **LinkedIn:** https://www.linkedin.com/in/ricardo-aoyagi-09813740/
- **Challenge escolhido:** 001 — Diagnóstico de Churn (RavenStack)

---

## Executive Summary

O churn da RavenStack não subiu da forma que o número sugere. Em 24 meses nenhuma conta deixou de ser cliente: as 500 terminam 2024 com assinatura ativa. O que subiu foi a quantidade de **assinaturas encerradas**, e mais da metade disso são trocas de assinatura e compras feitas a mais e desfeitas em poucos dias. A perda real de receita é **US$ 538 mil de MRR em 24 meses, contra US$ 1,18 milhão contados hoje**. No 4º trimestre de 2024, foram 5,5% do MRR, contra 14,4% no número atual.

A perda real está concentrada em **contas Enterprise que desligam pacotes de licenças** e continuam clientes: 78% da perda por redução. O aumento do número vem de uma **mudança no ritmo de compra a partir de jul/2024**, que apareceu em todos os segmentos ao mesmo tempo.

Principal recomendação: medir o churn pela tabela de assinaturas, separando troca, compra desfeita, redução real e saída, e proteger as contas Enterprise antes de elas desligarem pacotes.

---

## Solução

| Arquivo | O que é |
|---|---|
| [`solution/relatorio.pdf`](solution/relatorio.pdf) ([.md](solution/relatorio.md)) | **Relatório de diagnóstico**: causa raiz, segmentos e contas em risco, 6 ações priorizadas com impacto estimado |
| [`solution/painel_churn_antes_depois.html`](solution/painel_churn_antes_depois.html) | **Painel interativo**: churn "antes × depois" e as 4 situações por trimestre, alternando quantidade e valor. Abre no navegador e precisa de internet para a biblioteca de gráficos |
| [`solution/escopo_automacao_cs.pdf`](solution/escopo_automacao_cs.pdf) ([.md](solution/escopo_automacao_cs.md)) | **Escopo da automação para CS**: lista diária das 7h com as assinaturas Enterprise nos primeiros 30 dias, sinais de atenção, ação esperada e registro obrigatório de motivo |
| [`docs/`](docs/README.md) | **Análises de apoio**: as 6 etapas da investigação, com planilhas com fórmulas, diagnósticos parciais e os programas que recriam tudo a partir dos CSVs. As planilhas citadas no relatório estão em `docs/analise/` |

**Como rodar:** o painel (`solution/painel_churn_antes_depois.html`) abre direto no navegador e precisa de internet para carregar a biblioteca de gráficos. Para recriar as planilhas, veja as instruções de setup em [`docs/README.md`](docs/README.md#como-recriar-as-planilhas) (Python 3 com pandas e openpyxl, mais os 5 CSVs do Kaggle).

### Abordagem

1. **Entender a estrutura antes de analisar.** As 5 tabelas foram carregadas e cruzadas por `account_id` e `subscription_id`. Primeiro montamos uma visão "como os dados vêm" (Excel mês a mês e um painel). [Print 1](process-log/screenshots/1.png)
2. **Testar a coerência de cada tabela.** Foram 28 regras checadas linha a linha. Só a tabela de assinaturas é coerente (valor = licenças × preço; data de fim = encerrada). As três marcações de churn (conta, evento e assinatura) só concordam em 100 das 500 contas. Por isso a tabela de assinaturas virou a base, e as outras serviram como confirmação. [Print 2](process-log/screenshots/2.png)
3. **Triangular causas.** Comparamos 22 características (segmento, plano, uso, suporte, satisfação) nas três definições de churn. Nenhuma explica o churn. O sinal é de **tempo**: primeiros 30 dias e a partir de jul/2024. [Print 3](process-log/screenshots/3.png)
4. **Abrir o "churn" em situações.** Cada assinatura encerrada foi classificada em troca, compra extra desfeita, redução real ou saída do cliente, em quantidade e em US$. Na troca, calculamos quanto voltou na assinatura nova. [Print 4](process-log/screenshots/4.png)
5. **Aprofundar onde está o dinheiro (Enterprise),** em 4 períodos: preço, licenças, features, reclamações, perfil e caso a caso das 79 reduções. [Print 5](process-log/screenshots/5.png)
6. **Cruzar uso de features e eventos de churn** a partir dessas tabelas, sem partir das assinaturas, e comparar os tickets de quem teve churn com os de quem não teve. [Print 6](process-log/screenshots/6.png)
7. **Consolidar:** contas prioritárias, perda real por trimestre, ritmo de compra por segmento e a ligação entre evento de churn e cancelamento real. [Print 7](process-log/screenshots/7.png)

### Resultados / Findings

- **O churn de hoje mistura 4 coisas** (24 meses):
  - 233 trocas: US$ 461 mil voltaram na assinatura nova;
  - 64 compras extras desfeitas: US$ 180 mil;
  - 185 reduções reais: US$ 400 mil;
  - 4 saídas de cliente: US$ 23 mil, e as quatro contas voltaram depois.
  [Print 8](process-log/screenshots/8.png)
- **Causa do aumento:** a partir de jul/2024, o intervalo típico entre compras da mesma conta caiu de 26 para 11 dias. As compras em rajada foram de 3% para 22%, e o cancelamento em até 30 dias de 0,7% para 6,1%. Aconteceu em todos os países, indústrias e canais ao mesmo tempo, o que aponta para uma mudança de processo.
  [Print 9](process-log/screenshots/9.png)
- **Causa da perda real:** contas Enterprise desligam pacotes inteiros, cerca de 25 licenças e 1/4 do que pagam, e continuam Enterprise. Não houve aumento de preço, feature nova ou piora de suporte.
  [Print 10](process-log/screenshots/10.png)
- **Por que "algo não batia" para o CEO:**
  - a satisfação só tem notas 3 a 5, e 41% dos tickets ficam sem nota; [Print 11](process-log/screenshots/11.png)
  - a tabela de uso tem o mesmo volume todo mês, e suas datas estão espalhadas ao acaso. [Print 12](process-log/screenshots/12.png)
- **Contas em risco:** 10 contas Enterprise nomeadas, com 4 prioritárias (A-13466a, A-f44180, A-8ae05d, A-69fad4). Também os contratos anuais encerrados antes de 12 meses (US$ 164 mil). [Print 13](process-log/screenshots/13.png)
- **Dados:** os eventos de churn não se ligam aos cancelamentos reais. A proximidade entre os dois é igual à de uma data sorteada (8% contra 7,6%). Além disso, 37% dos eventos não têm motivo útil. [Print 14](process-log/screenshots/14.png)

### Recomendações

1. Trocar a régua de churn pela tabela de assinaturas (imediato).
2. Programa de proteção Enterprise: as 4 contas prioritárias e as 10 da lista, mais um alerta antes de desligar um pacote. Cada 10% evitado ≈ US$ 19 mil de MRR por trimestre. Vai ao encontro da automação sugerida para CS.
3. Descobrir e corrigir o que mudou no processo de compra em jul/2024.
4. Regra para contratos anuais encerrados antes de 12 meses.
5. Motivo de cancelamento obrigatório e claro, sem vazio e sem "unknown".
6. Tornar a base coerente: alinhar sistemas e modelagem, gerar o evento de churn a partir do fim real da assinatura e validar datas.

### Limitações

- **Base fictícia:** parte das incoerências pode vir do gerador dos dados.
- **Regras da análise:** as janelas de 7 dias (troca) e 30 dias (compra extra) e a regra de rajada são escolhas da análise, não regras da empresa.
- **Sem modelo preditivo:** uso, tickets e eventos não têm sinal confiável hoje. As ações 5 e 6 são pré-requisito para um modelo.
- **O que os dados não respondem:**
  - **o que** mudou no processo de compra em jul/2024;
  - **por que** as contas Enterprise desligam pacotes.

  Isso precisa ser confirmado com a empresa e com os clientes.

---

## Process Log — Como usei IA

### Ferramentas usadas

| Ferramenta | Para que usou |
|------------|--------------|
| Claude (app Claude, modo agente, modelo configurado claude-opus-5-5) | Análise dos 5 CSVs em Python (pandas), testes de coerência, planilhas Excel com fórmulas, relatórios em Markdown e PDF, painel interativo, escopo da automação |
| Claude ligado ao computador (pasta `G4_DESAFIO`) | Leitura dos dados, gravação dos arquivos e teste de cada programa no meu computador |

**Por quê:** escolhi o Claude em modo agente, ligado à minha pasta, para que ele lesse os dados e gravasse os arquivos diretamente, sob minhas regras de autorização. Assim cada resultado virou um arquivo verificável (planilha com fórmulas e programa), e não só uma resposta no chat.

### Workflow

**Como decompus o problema antes de pedir à IA:** comecei pelas regras de trabalho e por entender a estrutura e a confiabilidade dos dados. Só depois de saber em qual tabela confiar fui atrás das causas, sempre partindo das perguntas do CEO (causa, quem está em risco, o que fazer).

1. **Regras antes de tudo:** a IA não podia criar ou editar nada sem autorização, não podia mexer nos dados originais nem usar git, e tinha de trabalhar passo a passo, esperando meu "pode seguir".
2. **Visão original dos dados:** Excel e painel guardados como base intacta.
3. **Reconciliação:** provar com exemplos que as tabelas não batem e escolher a fonte confiável.
4. **Recorte de nov/dez 2024:** padrões dos cancelamentos rápidos; troca × redução × saída; flags de upgrade/downgrade; rajadas; valores em US$; gráfico mês a mês.
5. **Enterprise em 4 períodos:** preço, licenças, features, reclamações, perfil; depois as 79 reduções caso a caso, com "gêmeas" e prazos, e o teste de janelas de rajada (7 a 30 dias).
6. **Uso e eventos de churn,** sem partir das assinaturas, e tickets de quem teve churn × quem não teve.
7. **Consolidação, relatório final e adicionais:** painel e escopo para o CS.

Cada etapa gerou planilhas com fórmulas verificáveis, um programa que as recria a partir dos CSVs e um diagnóstico parcial em .md.

**Iterações:** foram 36 mensagens minhas ao longo de um dia, em 6 etapas de análise, com cerca de 360 ações executadas pela IA e várias rodadas de correção após conferir os números.

### Onde a IA errou e como corrigi

- **Frases que contradiziam os números.** Exemplos: a direção do erro da feature_13 e a leitura da cobrança. As notas foram reescritas depois da conferência dos números.
- **Premissas corrigidas com uma base de comparação.** Exemplos:
  - "ter uma assinatura igual = troca": 48% das Enterprise ativas têm uma gêmea, então isso não prova troca;
  - "a feature_10 explica o churn": por assinatura, o uso dela é igual entre quem cancela e quem fica.
- **Afirmação de "não há diferença" revista.** A prioridade "alta" dos tickets tinha diferença confiável; a planilha recalculada mostrou, e o texto foi corrigido.
- **Erros técnicos de fórmulas e gráficos no Excel** (#VALUE!, rótulo lido como fórmula, eixos), corrigidos após recalcular e conferir cada planilha.
- **Divergência entre planilhas:** a perda real de nov/dez saiu US$ 474 mil numa e US$ 482 mil na outra. A planilha 07 ficou como referência.

### O que eu adicionei que a IA sozinha não faria

- **Pedi provas antes de qualquer conclusão.** A coerência da base foi testada antes da análise de causa.
- **Perguntei se a troca era mesmo perda** ("o valor migrado já está em ingressantes?"). Isso levou ao cálculo do MRR reposto e à separação entre churn contado e perda real.
- **Centrei a investigação no Enterprise por valor**, separada em 4 períodos, com a hipótese de preço e feature, e pedi o caso a caso das reduções: gêmeas, prazos, rajada.
- **Testei a rajada com outras janelas** (10, 14, 20, 21, 28 e 30 dias), o que levou ao achado do ritmo de compra.
- **Exigi melhorar os dados, não só analisar:** motivo de cancelamento sem vazio e sem "unknown", e alinhamento de sistemas e modelagem.
- **Ajustei a estrutura do relatório** para seguir as perguntas do CEO e defini o escopo da automação para o CS.

---

## Evidências

- [ ] Screenshots das conversas com IA
- [ ] Screen recording do workflow
- [x] Chat exports — [`process-log/chat-exports/conversa_claude_desafio_churn.txt`](process-log/chat-exports/conversa_claude_desafio_churn.txt)
- [ ] Git history (se construiu código)
- [x] Outro: planilhas Excel com fórmulas e programas Python de cada etapa, diagnósticos parciais e a memória do projeto em [`docs/`](docs/README.md) + screenshots evidenciando a abordagem e os resultados em [`process-log/screenshots/`](process-log/screenshots/) (prints 1 a 14, citados em Abordagem e Resultados).

---

_Submissão enviada em: 17/10/2026_
