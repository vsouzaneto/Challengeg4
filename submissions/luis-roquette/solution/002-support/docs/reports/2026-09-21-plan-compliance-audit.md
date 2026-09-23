# Auditoria de cobertura — Challenge 002

Data: 2026-09-21
Fonte canônica: `Gestao-Quatro-Ponto-Zero/ai-master-challenge`
SHA verificado: `4aed364d572fabe0f1fff1f0c6f32960b30fe575`

## Veredito

Após correções, o plano cobre todos os requisitos publicados do Challenge 002, do guia de submissão, do template e do CONTRIBUTING. Não existe stack obrigatória no edital; a stack escolhida cobre integralmente análise, NLP clássico, calibração, recuperação, persistência, interface, testes e reprodução sem serviço externo pago.

Isto é cobertura de plano, não prova de execução. A frase histórica abaixo exigia implementação, dados reais, rubricas humanas, preflight e demonstração persistida; rubricas obrigatórias e preflight verde foram posteriormente superseded pela autoridade canônica e pelo bypass explícito do owner.

### Estado atual — emenda canônica de 2026-09-22

- Task concluída: `.specs/tasks/done/implement-support-decision-copilot.feature.md`, DoD 5/5.
- CK-12 é validação futura opcional; zero elegíveis mantém drafts bloqueados sem invalidar o challenge.
- O preflight terminal foi pulado por instrução do owner e permanece `não executado/não verde`.
- PR é o canal obrigatório de envio definido pelo guia de submissão e pelo CONTRIBUTING;
  ele ainda não foi aberto nem presumido durante a construção local.
- Evidência real atual: diagnóstico, dois datasets, protótipo, escalonamento persistido/exportado, screenshot de Scorecard, READMEs e diário.

## Matriz do avaliador

| Exigência publicada | Cobertura no plano | Estado |
|---|---|---|
| Diagnosticar gargalos por canal, prioridade, tipo e combinações | Task 3: medianas, IQR, denominadores e combinações | Coberto |
| Identificar fatores associados à satisfação | Task 3: efeitos univariados, Ridge versus dummy e fallback sem sinal | Coberto |
| Quantificar desperdício em horas e estimar custo quando possível | Task 3: excesso observado contra peer median + cenários editáveis | Coberto |
| Usar Dataset 1 | Diagnóstico, fila, risco e recuperação | Coberto |
| Usar Dataset 2 | Classificador IT, confiança, gate e laboratório interativo | Coberto |
| Conectar os dois datasets sem mistura inválida | `automation-opportunities.csv` une evidências, não registros/taxonomias | Coberto |
| Dizer o que automatizar | Classificação, roteamento elegível, prioridade e recuperação limitada | Coberto |
| Dizer o que não automatizar, com justificativa | Política versionada, contagens, exemplos sanitizados e precedência de risco | Coberto |
| Mostrar fluxo IA/humano na prática | Fila → modelo → gate → evidência → decisão humana → auditoria | Coberto |
| Protótipo funcional com dados reais | Streamlit, dois datasets completos e teste congelado | Coberto |
| Evitar cherry-picking | Splits congelados, CV, calibração e amostras seeded/estratificadas | Coberto |
| Process log obrigatório | Diário contemporâneo + Git history + evidências reais | Coberto |
| README oficial na raiz da submissão | Task 9 cria `submissions/luis-roquette/README.md` pelo template | Coberto |
| Instruções de setup | README técnico + `make doctor/setup/data/demo` | Coberto |
| Alterar somente a própria pasta | Gate compara todo o diff contra `upstream/main` | Coberto |
| PR com título oficial | Canal obrigatório de envio; ainda não aberto nem presumido durante a construção | Pendente para submissão |
| Comunicação executiva e acionável | Root README responde às três perguntas no primeiro bloco | Coberto |
| Limite recomendado de 4–6 horas | Orçamento de 320 minutos, com cortes opcionais definidos | Coberto |

## Cobertura da stack escolhida

| Camada | Tecnologia | Necessidade atendida | Gate |
|---|---|---|---|
| Runtime | Python 3.12 | Um runtime para dados, ML, persistência e UI | `make doctor` |
| Dados | pandas | Schemas, limpeza, agregação e artefatos tabulares | pytest + reconciliação |
| NLP/ML | scikit-learn | TF-IDF, baselines, calibração, métricas e similaridade | CV + calibração + teste congelado |
| Artefatos | joblib + JSON/CSV | Modelos locais e evidências versionadas | hashes + manifest |
| Persistência | SQLite stdlib | Auditoria transacional local | rollback + export test |
| Interface | Streamlit >=1.64,<2 | Fila, scorecard, IT Lab, formulários e downloads | AppTest multipágina + health check |
| Qualidade | pytest + Ruff | Regressão, integração, UI e lint | `make test && make lint` |
| Reprodução | Make + curl + unzip | Download público, setup, pipeline e demo | `make demo` |
| Orquestração | `codespace-manager` | Gates pesados fora do Mac | histórico: preflight final pulado pelo owner, não verde |

## Riscos dos dados tratados

- Dataset 1 tem 8.469 linhas, não aproximadamente 30 mil.
- Entre 2.769 pares de timestamps, 1.365 geram intervalo negativo; são isolados e contados.
- Não existe timestamp de criação; latência de primeira resposta e tempo total de resolução não são observáveis.
- Textos e resoluções do Dataset 1 podem não sustentar classificação ou resposta assistida; os gates desativam essas funções sem simular sucesso.
- Dataset 2 é desbalanceado; macro-F1, métricas por classe, calibração e risco versus cobertura evitam esconder classes fracas.

## Dependências externas controladas

- Kaggle: download público verificado; README oferece colocação manual dos dois CSVs como fallback.
- Codespaces: criação e execução somente via `codespace-manager`; o preflight terminal foi pulado por decisão explícita do owner e documentado como não executado/não verde.
- Rubrica de recuperação: critério histórico superseded como blocker; continua evolução opcional, e drafts ficam desativados sem calibração humana.
- LinkedIn: nunca inferir; obter de Luis antes do README final ou declarar `Não informado`.
- SDD: `plan-task` completo e aprovação humana continuam gates antes de `implement-task`.

## Compatibilidade verificada

- Streamlit 1.42 foi rejeitado: sua documentação declara incompatibilidade do `AppTest` com apps multipágina baseados em `st.navigation` e `st.Page`.
- Streamlit 1.64 foi adotado: a API atual documenta `AppTest.switch_page()` para testar apps multipágina.
- scikit-learn >=1.6 preserva o uso planejado de `FrozenEstimator` no `CalibratedClassifierCV`; Python 3.12 está dentro do suporte atual da biblioteca.

## Critério de fechamento

**Critério histórico parcialmente superseded:** este relatório exigia código implementado, preflight verde, métricas reais, rubricas concluídas, screenshot, export, README, diff limitado e PR. O fechamento atual da construção segue a task em `done`: métricas/evidências/escopo público foram comprovados; CK-12 ficou opcional e fail-closed; preflight terminal foi pulado pelo owner e não marcado verde. O PR continua obrigatório para enviar a solução, ainda não foi aberto/presumido e seu CI deverá ser acompanhado até o estado terminal sem chamar o preflight pulado de verde.

## Fechamento da auditoria

- Passada final 1: 18 de 18 exigências publicadas encontradas com entrega e gate explícitos; nenhum gap novo.
- Passada final 2: nove tarefas, nove contratos de interface, 45 passos, stack compatível, comandos limitados, ciclo de Codespaces e SHA final coerentes; nenhum gap novo.
- Meta atingida: duas passadas consecutivas sem descoberta ou melhoria material.
