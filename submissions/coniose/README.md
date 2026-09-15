# Submissão — Julio Cesar de Freitas — Challenge 001

## Sobre mim

- **Nome:** Julio Cesar de Freitas
- **LinkedIn:** https://www.linkedin.com/in/coniose/
- **Challenge escolhido:** 001 — Diagnóstico de Churn

---

## Executive Summary

Cruzei as 5 tabelas da RavenStack e testei as causas óbvias de churn (uso, suporte, preço) antes de aceitar qualquer uma — nenhuma se sustenta. O achado central: o churn não é problema de carteira madura, é de onboarding, e piora a cada safra de entrada — 15,6% das contas que entraram no 1º semestre de 2023 cancelaram nos primeiros 90 dias; da safra mais recente (2º semestre de 2024), **60,8%** (p=1,6×10⁻¹⁰, sobrevive a controle de composição por indústria/canal/plano). Rodei uma segunda sessão de IA especificamente para auditar a primeira análise, e ela invalidou dois achados que eu tinha aceitado rápido demais (um deles, um gráfico inteiro, retirei do relatório); mais tarde, revisando a posição competitiva contra outras submissões públicas do mesmo desafio, verifiquei e reproduzi de forma independente o achado de safra, que se tornou a manchete — a sequência completa e honesta está no process log. DevTools e o canal de aquisição por evento seguem como pistas secundárias, mais fracas. A recomendação principal: reconciliar os dois números de churn que a própria empresa tem hoje, instituir checkpoints nos primeiros 90 dias de conta, e dentro dessa janela, priorizar por MRR — não por taxa de risco individual, que os dados não sustentam.

---

## Solução

A entrega tem 3 camadas, pensadas pra 3 públicos diferentes — está detalhado na abordagem abaixo.

### Abordagem

Comecei entendendo a estrutura das 5 tabelas antes de qualquer teste (é a própria dica do README do desafio). Cruzei `accounts` × `subscriptions` × `feature_usage` × `support_tickets` × `churn_events` via um join de dois saltos (`feature_usage` só tem `subscription_id`; subo pra `account_id` via `subscriptions`). Testei as hipóteses óbvias primeiro (uso, suporte, preço, plano) — nenhuma se sustentou — e só depois fui pra segmentação e concentração de receita.

A decisão mais importante do processo foi separar **quem constrói** de **quem audita**: depois da primeira versão da análise, rodei uma sessão de IA dedicada e instruída explicitamente a atacar o que já tínhamos (seleção pós-hoc, paradoxo de Simpson, comparação múltipla), em paralelo com uma segunda sessão pensando só na tradução pra linguagem de negócio. Detalhes completos no [process log](./process-log/PROCESS_LOG.md).

### Resultados / Findings

- **[`solution/DIAGNOSTICO.md`](./solution/DIAGNOSTICO.md)** — o deliverable principal, para o CEO fictício da RavenStack. Zero jargão estatístico; cada número é rastreável até uma das 5 tabelas.
- **[`solution/dashboard.html`](./solution/dashboard.html)** ([versão ao vivo](https://claude.ai/artifact/Vfrjf56P6w8Vp1HkRLNY3j)) — anexo técnico: todos os testes estatísticos, incluindo a seção de auditoria (regressão logística com as 28 covariáveis de uma vez, contagem de quantos testes formais foram rodados no total).
- **[`solution/painel_retencao.html`](./solution/painel_retencao.html)** ([versão ao vivo](https://claude.ai/artifact/44PuoTrXZ5Vm1TYm3r618G)) — protótipo funcional, o diferencial: 3 filas com lógicas diferentes — **fila preventiva de onboarding** (as 68 contas hoje dentro da janela crítica de 90 dias, ordenadas por MRR — a prioridade nº 1), fila de risco transparente (score = participação no MRR × churn do segmento) para as 500 contas, e um painel de memória de caso para as 100 maiores, com registro de ação persistente e compartilhado (o time de CS poderia abrir e usar amanhã).
- **[`solution/analysis/`](./solution/analysis/)** — código-fonte completo: `build_report_data.py` gera `report_data.json` do zero a partir dos 5 CSVs do [dataset no Kaggle](https://www.kaggle.com/datasets/rivalytics/saas-subscription-and-churn-analytics-dataset), incluindo `onboarding_cohort_deterioration` (a análise de safra); os 4 `audit_checks_*.py` são os scripts que a sessão de auditoria deixou, reproduzíveis (`python analysis/audit_checks_1_devtools_lookelsewhere.py` etc.).

**Achado central:** churn nos primeiros 90 dias sobe de 15,6% para 60,8% entre a safra mais antiga e a mais recente (χ²=48,6, p=1,6×10⁻¹⁰), e sobrevive a controle de composição por indústria/canal/plano (OR=2,08 por safra, p=1,5×10⁻¹⁰). É ordens de magnitude mais forte que qualquer outro achado deste relatório — inclusive o de que o conjunto completo de tudo que a RavenStack mede hoje, olhado de forma agregada (28 fatores ao mesmo tempo), não explica por que uma conta cancela (p=0,15, pseudo-R²=0,07). As duas coisas juntas são a resposta: a causa não está numa foto estática da carteira, está na trajetória dos primeiros 90 dias — seções 2 e 3 do `DIAGNOSTICO.md`.

### Recomendações

Priorizadas, com dono e prazo, na seção 7 do `DIAGNOSTICO.md`. As três primeiras:
1. Reconciliar os dois números de churn (110 contas marcadas vs. 352 com evento no log) antes de qualquer outra decisão — sem isso nenhuma métrica de retenção é confiável.
2. Instituir checkpoints de onboarding nos dias 14, 30, 60 e 90 — é a janela onde a safra mais recente cancela 4× mais que a de 2023.
3. Não usar satisfação e volume de uso, isoladamente, como indicador de retenção — nenhum dos dois separa quem cancela de quem fica na carteira agregada.

### Limitações

- O achado de safra de onboarding tem confiança estatística muito alta; **DevTools e o canal de evento continuam sendo pistas, não fato provado** — a amostra é pequena o suficiente para que uma seleção visual infle a confiança (testado e corrigido via permutação, ver `DIAGNOSTICO.md` seção 8).
- A causa da deterioração de safra ainda não está explicada — o padrão temporal é sólido, mas os dados não dizem se é perfil de cliente, onboarding ou produto.
- Não sei se a RavenStack real atende setores fora de tecnologia — as 500 contas desta base são inteiramente de 5 verticais de tech.
- Testei manualmente o registro de ação do painel após publicar — grava e persiste no banco compartilhado do artefato (dois registros de autores diferentes já salvos, em contas distintas, confirmando que o compartilhamento entre viewers funciona).

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

Ver a lista completa de 16 passos no process log. Resumo: estrutura → primeira análise → dashboard → **eu mesmo aceitei um achado (DevTools) sem testar seleção pós-hoc** → pedi analogia com manutenção preditiva → mais cortes (feature, ticket, MRR) → **eu mesmo descobri a primeira autocorreção** cruzando MRR com tenure → auditoria externa dedicada + estratégia de entrega em paralelo → reescrita completa do código com as correções → decisão de negócio (fila de risco vs. memória de caso) → 3 documentos finais → teste manual do painel → **revisão da posição competitiva contra outras submissões públicas do desafio** → verificação na fonte de um achado forte de outro candidato (safra de onboarding) → reprodução independente com metodologia própria → reformulação do `DIAGNOSTICO.md` com esse achado como manchete.

### Onde a IA errou e como corrigi

Cinco casos concretos, com número antes/depois, na seção correspondente do process log — resumidos aqui:
1. Aceitei (e a IA reforçou) um `p=0,013` sem correção de seleção pós-hoc — corrigido pra `p=0,046`/`0,157`.
2. Um gráfico com legenda factualmente falsa sobre trajetória de uso — retirado do relatório.
3. `reason_code` calculado sobre 77,5% de contas que não estavam de fato canceladas — recalculado.
4. Correção de Bonferroni aplicada em só metade de um teste espelhado — estendida.
5. Um bug de uma linha que inflou o MRR em 9× — percebido porque o número não bateu com a ordem de grandeza esperada.

### O que eu adicionei que a IA sozinha não faria

A decisão de rodar uma auditoria adversarial dedicada (a IA não se auto-desconfia por padrão); a pergunta que gerou a primeira autocorreção (cruzar MRR com tenure); a recusa de perseguir um modelo preditivo com AUC artificialmente alto; a virada de hipótese de negócio — de "os maiores clientes são o problema" para "o espaço estatístico está no volume, não na concentração" — que definiu a arquitetura dos produtos; e, ao ver um achado forte de outro candidato (safra de onboarding), a decisão de perguntar explicitamente se usar isso feria as regras do desafio, verificar com metodologia própria, e só então reformular a tese — em vez de simplesmente incorporar ou simplesmente ignorar.

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
