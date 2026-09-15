# Submissão — Julio Cesar de Freitas — Challenge 001

## Sobre mim

- **Nome:** Julio Cesar de Freitas
- **LinkedIn:** https://www.linkedin.com/in/coniose/
- **Challenge escolhido:** 001 — Diagnóstico de Churn

---

## Executive Summary

Cruzei as 5 tabelas da RavenStack e testei as causas óbvias de churn (uso, suporte, preço) antes de aceitar qualquer uma — nenhuma se sustenta. Rodei uma segunda sessão de IA especificamente para auditar a primeira, e ela invalidou dois achados que eu tinha aceitado rápido demais (um deles, um gráfico inteiro, retirei do relatório). O que sobrevive: DevTools com o dobro do churn do resto da carteira, o canal de aquisição por evento decidindo o destino da conta antes da venda fechar, e 56% de toda a receita em risco concentrada em 100 contas nomeadas. A recomendação principal não é um modelo preditivo — é reconciliar os dois números de churn que a própria empresa tem hoje, e priorizar por MRR em risco, não por taxa.

---

## Solução

A entrega tem 3 camadas, pensadas pra 3 públicos diferentes — está detalhado na abordagem abaixo.

### Abordagem

Comecei entendendo a estrutura das 5 tabelas antes de qualquer teste (é a própria dica do README do desafio). Cruzei `accounts` × `subscriptions` × `feature_usage` × `support_tickets` × `churn_events` via um join de dois saltos (`feature_usage` só tem `subscription_id`; subo pra `account_id` via `subscriptions`). Testei as hipóteses óbvias primeiro (uso, suporte, preço, plano) — nenhuma se sustentou — e só depois fui pra segmentação e concentração de receita.

A decisão mais importante do processo foi separar **quem constrói** de **quem audita**: depois da primeira versão da análise, rodei uma sessão de IA dedicada e instruída explicitamente a atacar o que já tínhamos (seleção pós-hoc, paradoxo de Simpson, comparação múltipla), em paralelo com uma segunda sessão pensando só na tradução pra linguagem de negócio. Detalhes completos no [process log](./process-log/PROCESS_LOG.md).

### Resultados / Findings

- **[`solution/DIAGNOSTICO.md`](./solution/DIAGNOSTICO.md)** — o deliverable principal, para o CEO fictício da RavenStack. Zero jargão estatístico; cada número é rastreável até uma das 5 tabelas.
- **[`solution/dashboard.html`](./solution/dashboard.html)** ([versão ao vivo](https://claude.ai/artifact/Vfrjf56P6w8Vp1HkRLNY3j)) — anexo técnico: todos os testes estatísticos, incluindo a seção de auditoria (regressão logística com as 28 covariáveis de uma vez, contagem de quantos testes formais foram rodados no total).
- **[`solution/painel_retencao.html`](./solution/painel_retencao.html)** ([versão ao vivo](https://claude.ai/artifact/44PuoTrXZ5Vm1TYm3r618G)) — protótipo funcional, o diferencial: fila de retenção transparente (score = participação no MRR × churn do segmento) para as 500 contas, e um painel de memória de caso para as 100 maiores, com registro de ação persistente e compartilhado (o time de CS poderia abrir e usar amanhã).
- **[`solution/analysis/`](./solution/analysis/)** — código-fonte completo: `build_report_data.py` gera `report_data.json` do zero a partir dos 5 CSVs do [dataset no Kaggle](https://www.kaggle.com/datasets/rivalytics/saas-subscription-and-churn-analytics-dataset); os 4 `audit_checks_*.py` são os scripts que a sessão de auditoria deixou, reproduzíveis (`python analysis/audit_checks_1_devtools_lookelsewhere.py` etc.).

**Achado central:** o conjunto completo de tudo que a RavenStack mede hoje (28 fatores testados ao mesmo tempo) não explica por que uma conta cancela (p=0,15, pseudo-R²=0,07). Isso não é falha da análise — é a resposta, e está detalhada na seção 8 do `DIAGNOSTICO.md`.

### Recomendações

Priorizadas, com dono e prazo, na seção 6 do `DIAGNOSTICO.md`. As duas primeiras:
1. Reconciliar os dois números de churn (110 contas marcadas vs. 352 com evento no log) antes de qualquer outra decisão — sem isso nenhuma métrica de retenção é confiável.
2. Tirar satisfação e uso do "score de saúde" da conta — nenhum dos dois separa quem cancela de quem fica.

### Limitações

- O achado de DevTools e do canal de evento são a **melhor hipótese do dataset**, não fato provado — a amostra é pequena o suficiente para que uma seleção visual infle a confiança (testado e corrigido via permutação, ver `DIAGNOSTICO.md` seção 7).
- Não sei se a RavenStack real atende setores fora de tecnologia — as 500 contas desta base são inteiramente de 5 verticais de tech.
- Não confirmei com meus próprios olhos, no navegador, que o registro de ação do painel de retenção grava no banco compartilhado (a automação de teste que usei travou repetidamente numa tela específica) — testei manualmente depois de publicar. [ajustar após teste manual, se necessário]

---

## Process Log — Como usei IA

> Ver [`process-log/PROCESS_LOG.md`](./process-log/PROCESS_LOG.md) para a versão completa, com números e citações. Resumo:

### Ferramentas usadas

| Ferramenta | Para que usei |
|------------|--------------|
| Claude Code (Sonnet 5, sessão principal) | Análise exploratória, cruzamento das 5 tabelas, testes estatísticos, dashboard, painel de retenção, escrita dos documentos |
| Agente Claude Opus #1 (auditoria, effort alto) | Sessão dedicada só a atacar o relatório já publicado — seleção pós-hoc, paradoxo de Simpson, comparação múltipla |
| Agente Claude Opus #2 (estratégia de entrega) | Estrutura do documento pro CEO, tradução de achado estatístico pra recomendação acionável, viabilidade do modelo preditivo |

### Workflow

Ver a lista completa de 13 passos no process log. Resumo: estrutura → primeira análise → dashboard → **eu mesmo aceitei um achado (DevTools) sem testar seleção pós-hoc** → pedi analogia com manutenção preditiva → mais cortes (feature, ticket, MRR) → **eu mesmo descobri a primeira autocorreção** cruzando MRR com tenure → auditoria externa dedicada + estratégia de entrega em paralelo → reescrita completa do código com as correções → decisão de negócio (fila de risco vs. memória de caso) → 3 documentos finais.

### Onde a IA errou e como corrigi

Cinco casos concretos, com número antes/depois, na seção correspondente do process log — resumidos aqui:
1. Aceitei (e a IA reforçou) um `p=0,013` sem correção de seleção pós-hoc — corrigido pra `p=0,046`/`0,157`.
2. Um gráfico com legenda factualmente falsa sobre trajetória de uso — retirado do relatório.
3. `reason_code` calculado sobre 77,5% de contas que não estavam de fato canceladas — recalculado.
4. Correção de Bonferroni aplicada em só metade de um teste espelhado — estendida.
5. Um bug de uma linha que inflou o MRR em 9× — percebido porque o número não bateu com a ordem de grandeza esperada.

### O que eu adicionei que a IA sozinha não faria

A decisão de rodar uma auditoria adversarial dedicada (a IA não se auto-desconfia por padrão); a pergunta que gerou a primeira autocorreção (cruzar MRR com tenure); a recusa de perseguir um modelo preditivo com AUC artificialmente alto; e a virada de hipótese de negócio — de "os maiores clientes são o problema" para "o espaço estatístico está no volume, não na concentração" — que definiu a arquitetura dos dois produtos finais.

---

## Evidências

- [x] Narrativa escrita completa — [`process-log/PROCESS_LOG.md`](./process-log/PROCESS_LOG.md)
- [x] Chat export — sessão completa do Claude Code disponível a pedido
- [ ] Screenshots das conversas com IA
- [ ] Screen recording do workflow
- [x] Git history — este PR
- [x] Código-fonte auditável — [`solution/analysis/`](./solution/analysis/)

---

*Submissão enviada em: 2026-09-14*
