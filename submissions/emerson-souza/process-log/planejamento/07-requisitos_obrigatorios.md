# Requisitos: OBRIGATÓRIO primeiro, diferencial depois

**Regra do Emerson:** o foco é fazer **os obrigatórios funcionarem**. Os diferenciais entram depois, se o obrigatório estiver 100%.
Cada item tem: onde aparece no sistema + como provamos que está pronto (teste de aceite).

Legenda: 🔴 obrigatório · 🟦 diferencial · 📄 documentação

---

## 001 — Churn (módulo Retenção)

| # | Requisito do desafio | Tipo | Onde no sistema | Pronto quando… |
|---|---|---|---|---|
| 1.1 | **Causa raiz** do churn, cruzando tabelas | 🔴 | Aba "Causa raiz" | Mostra a comparação canceladas × ativas nas **5 tabelas**, com números e o teste do "paradoxo do CEO" |
| 1.2 | **Segmentos em risco**, com **contas específicas** | 🔴 | Aba "Segmentos e contas" | Tabela de taxa por segmento + lista de contas exportável |
| 1.3 | **Ações concretas, priorizadas, com impacto estimado** | 🔴 | Aba "Plano de ação" | Cada ação tem prioridade, contas-alvo e MRR protegido estimado, com premissa |
| 1.4 | Relatório legível pelo **CEO** | 🔴 | Botão "Relatório" (PDF/MD) | Um executivo entende em 5 min |
| 1.5 | Insights **verificáveis** (números) e **correlação × causalidade** | 🔴 | Todas as abas | Cada afirmação tem número + ressalva quando for correlação |
| 1.6 | Process log | 🔴📄 | `process-log/` | Rodadas registradas |
| 1.7 | Modelo preditivo que funcione | 🟦 | Aba "Modelo" | Validação cruzada, métrica honesta |
| 1.8 | Dashboard interativo | 🟦 | (o próprio painel) | Já coberto pela arquitetura |
| 1.9 | Automação para o CS | 🟦 | Cruzamento → Suporte | Lista de contas enviada para a sub-sessão de suporte |

## 002 — Suporte

| # | Requisito do desafio | Tipo | Onde no sistema | Pronto quando… |
|---|---|---|---|---|
| 2.1 | **Onde o fluxo trava** (canal × prioridade × tipo, piores combinações) | 🔴 | Aba "Gargalos" | Matriz com tempo e volume + ranking das piores combinações, **com intervalo de confiança** |
| 2.2 | **O que impacta a satisfação** | 🔴 | Aba "Satisfação" | Efeito de cada variável, com teste estatístico; conclusão honesta se não houver efeito |
| 2.3 | **Desperdício em horas (e custo)**, e onde é recuperável | 🔴 | Aba "Desperdício" | Horas acima da meta por combinação × custo/hora editável |
| 2.4 | **O que automatizar** (usando **os 2 datasets**) | 🔴 | Aba "Automação" | Lista com justificativa baseada em dados |
| 2.5 | **O que NÃO automatizar**, com exemplos dos dados | 🔴 | Aba "Automação" | Categorias + exemplos reais de tickets |
| 2.6 | **Fluxo na prática** (ticket entra → IA → humano) | 🔴 | Aba "Automação" (diagrama) | Diagrama com os limiares de confiança |
| 2.7 | Process log | 🔴📄 | `process-log/` | |
| 2.8 | **Protótipo funcional** (classificador com confiança / roteador / respostas sugeridas) | 🟦* | Aba "Testar ticket" | Acurácia/F1 **medida em conjunto de teste** do DS2; funciona com qualquer texto |
| 2.9 | ROI (horas/mês economizadas) | 🟦 | Aba "Automação" | Cálculo com premissas explícitas |

\* Tecnicamente é diferencial, mas o próprio diretor diz *"quero ver algo rodando"* e o critério pergunta *"se construiu protótipo: funciona com dados reais?"*. **Tratamos como obrigatório na prática.**

## 003 — Lead Scorer (módulo Vendas)

| # | Requisito do desafio | Tipo | Onde no sistema | Pronto quando… |
|---|---|---|---|---|
| 3.1 | **Roda** (não é mockup) | 🔴 | Módulo inteiro | Abre e funciona pelo painel/.exe |
| 3.2 | Usa os **dados reais** | 🔴 | | As 4 tabelas do CRM |
| 3.3 | **Lógica de scoring** (não é só ordenar por valor) | 🔴 | Aba "Pipeline priorizado" | Score 0–100 com fatores ponderados pelos dados |
| 3.4 | Vendedor entende **o porquê** do score | 🔴 | Coluna "Por quê" + detalhe do deal | Os 3 principais motivos em português, em cada deal |
| 3.5 | 📄 **Setup** (dependências, comandos) | 🔴📄 | `docs/` | Outra pessoa roda seguindo o texto |
| 3.6 | 📄 **Lógica** (critérios e por quê) | 🔴📄 | `docs/` + aba "Como o score funciona" | |
| 3.7 | 📄 **Limitações** e o que falta para escalar | 🔴📄 | `docs/` | |
| 3.8 | Process log (mostrar o "vibe coding") | 🔴📄 | `process-log/` | Com histórico de commits |
| 3.9 | Filtros **vendedor / manager / região** | 🟦 | Barra lateral do módulo | |
| 3.10 | Visão "segunda-feira de manhã" | 🟦 | Tela inicial do módulo | |

## 004 — Social Media (módulo Mídia)

| # | Requisito do desafio | Tipo | Onde no sistema | Pronto quando… |
|---|---|---|---|---|
| 4.1 | **O que gera engajamento** (plataforma, tipo, categoria, tamanho de criador), além do óbvio | 🔴 | Aba "Engajamento" | Comparações controladas com efeito + IC |
| 4.2 | **Patrocínio funciona?** Comparação **justa** (controlando criador/plataforma/categoria), custo implícito, quando vale | 🔴 | Aba "Patrocínio" | Comparação estratificada + conclusão |
| 4.3 | **Perfil de audiência** que mais engaja, por plataforma/tipo/categoria | 🔴 | Aba "Audiência" | |
| 4.4 | **O que NÃO funciona** | 🔴 | Aba "Engajamento" | |
| 4.5 | Estratégia: **onde concentrar** (plataforma, tipo, **frequência**, faixa de criador) | 🔴 | Aba "Estratégia" | Recomendações **priorizadas** |
| 4.6 | **Política de patrocínio** com **limites** (seguidores/engajamento) | 🔴 | Aba "Estratégia" | Regra numérica clara |
| 4.7 | **O que parar de fazer** | 🔴 | Aba "Estratégia" | |
| 4.8 | **Quick wins** da semana | 🔴 | Aba "Estratégia" | |
| 4.9 | Process log | 🔴📄 | | |
| 4.10 | Dashboard de acompanhamento / modelo preditivo / hashtags / clusters | 🟦 | Abas extras | |

## Requisitos comuns (da entrega)

| # | Requisito | Tipo |
|---|---|---|
| C.1 | README no formato do template (Sobre mim, Executive Summary, Solução, Process Log, Evidências) | 🔴📄 |
| C.2 | Instruções de setup (se tem código) | 🔴📄 |
| C.3 | Process log com evidências (prints, chat exports, narrativa, git) | 🔴📄 |
| C.4 | Tudo dentro de `submissions/emerson-souza/` | 🔴 |
| C.5 | PR com título no formato pedido | 🔴 |

## Requisitos do NOSSO sistema (núcleo)

| # | Requisito | Prioridade |
|---|---|---|
| N.1 | Abre em **janela própria**, como software (ideia do Emerson) | 🔴 |
| N.2 | **Sessões**: criar, escolher o módulo, salvar, reabrir, apagar | 🔴 |
| N.3 | **Entrada de dados** (CSV/Excel/JSON) + botão "usar dados do desafio" | 🔴 |
| N.4 | **De/Para** para aceitar dados de outras empresas | 🔴 (sugestão automática = 🟦) |
| N.5 | **Cruzamento Churn → Suporte** (🟢) | 🔴 (é o exemplo-âncora) |
| N.6 | Demais cruzamentos | 🟦 |
| N.7 | Selo de evidência 🟢🟡🔵 + bloco "Qualidade dos dados" | 🔴 |
| N.8 | Executável Windows + Release | 🔴 |
