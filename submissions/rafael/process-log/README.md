# Process log — como usei IA

Período: 18/10/2026 17:45 → 19/10/2026 · 33 prompts com conteúdo ([`prompts.md`](prompts.md)) · 3 sessões de trabalho (1 principal + 2 paralelas de checagem) · histórico completo em `git log` · 39 decisões registradas com motivo e alternativa descartada em [`../DEVELOPMENT_PROCESS.md`](../DEVELOPMENT_PROCESS.md).

## Ferramentas

| Ferramenta | Para que usei |
|---|---|
| **Claude Code** (Opus, terminal) | Toda a execução: download do dataset, EDA, testes estatísticos, modelos, pacote Python + testes, site FastAPI, documentação |
| Sessões paralelas do Claude Code | Checagem independente: (1) conferir a descrição oficial do Kaggle contra os dados e as conclusões; (2) revisão crítica da entrega contra os requisitos do desafio |
| Outra IA (chat) | Montar um plano de ação de análise ([`knowledge/action-plan.md`](../knowledge/action-plan.md)) quando a primeira rodada não trouxe resultado |
| Jupyter + pytest | Verificação: 14 notebooks executados e 131 testes com efeitos plantados |

## Como decompus o problema antes de pedir código

1. **Regras antes do código.** O primeiro prompt criou [`instructions/`](../instructions/): o que entregar (DELIVER), o que gera valor (VALUES), padrão de código (CODE) e estilo (GENERAL). Todos os prompts seguintes foram executados sob essas regras: nenhum número escrito à mão, correção para muitos testes, decisões registradas.
2. **Entender os dados antes da estratégia.** Pedi uma EDA em notebook para ler colunas e valores pessoalmente, antes de qualquer conclusão.
3. **Duas frentes, como o time opera:** análise geral e análise por plataforma, com as mesmas funções.
4. **Perguntas do desafio → funções.** Cada pergunta obrigatória virou uma função que gera o veredito a partir dos números (`questions.py`, `strategy.py`). Assim o texto se reescreve sozinho com os dados reais da empresa.
5. **Só então o produto:** site com servidor, em linguagem para leigos, com previsão e painel.
6. **Checagens independentes no fim:** a descrição do dataset contra as conclusões e a entrega contra os requisitos, cada uma em sessão separada para não herdar o viés da sessão principal.

## Workflow (iterações)

| # | Etapa | O que eu pedi | O que mudou por causa disso |
|---|---|---|---|
| 1 | Setup | Fork, regras em `instructions/`, achados em `knowledge/` | Estrutura que serviu de memória entre sessões |
| 2 | EDA | Notebook para eu entender colunas, valores e ligações | Descoberta central: **as métricas são sorteadas** (Poisson independentes; views ~10.100 ± 100 em todos os posts) |
| 3 | Insights gerais × por plataforma | Clusterização, NLP de comentários, público por tipo de post | Nada sobreviveu à correção estatística → controle positivo (+2% plantado) para provar que o método enxerga efeitos quando eles existem |
| 4 | Plano de outra IA | Correlações, faixas, top 10%, RF/XGBoost/CatBoost, SHAP | SHAP comparado com modelo de alvo embaralhado, para não vender ruído como "fator" |
| 5 | Perguntas e estratégia em funções | As 4 perguntas + as 4 decisões | Regra "entre opções equivalentes, vence a mais barata"; premissas de custo como parâmetros |
| 6 | Modelo de engajamento | Testar abordagens supervisionadas | 14 modelos no mesmo protocolo; o previsor só adota um modelo que bata a média |
| 7 | "Parece que os dados não trazem insight" | Foco em 4 relações com views | Efeito mínimo detectável (MDE): "não há efeito" passou a ser **comprovado**, não falta de dados |
| 8 | Varredura completa | Todos os atributos × views, likes, comentários | 96 combinações, 0 efeitos reais |
| 9 | Previsão antes de postar | Só o que se sabe antes de publicar | Inventário antes × depois, histórico do creator sem vazamento, validação temporal |
| 10 | Duração × views | Histograma, e minha leitura de "mais picos entre 20–150 s" | Contagem ≠ taxa: mais picos porque há mais vídeos nessa faixa; a chance por vídeo é igual |
| 11 | Bolsões e top 1% | Tratar variações como insights e buscar mais, por plataforma | Níveis de evidência (confirmado / se repetiu nos 2 anos / pista). Achado: TikTok · beauty · espanhol |
| 12 | Chance de top 5% | Previsor por formato e métrica | Chance oficial = taxa base quando nenhum modelo passa na correção |
| 13 | Site | Completo, com servidor, para leigos, com painel estilo Power BI | FastAPI + 8 páginas; depois: resumo primeiro e detalhes sob demanda, painel mais simples, "Simular post", identidade G4 |
| 14 | Creator × views | Minha hipótese: "quem posta" deveria importar | Os "campeões" são sorte (8,8% continuam no top vs. 10% do acaso) |
| 15 | Checagem 1 (paralela) | Descrição do Kaggle × dados × conclusões | 8 resultados enganosos encontrados (E1–E8) → auditorias de disclosure, fit, mercado, duração e poder |
| 16 | Checagem 2 (paralela) | Revisão crítica contra os requisitos | Contradições e recomendações que vinham das premissas → classes "robusta × depende de premissa" e fila de testes |

## Onde a IA errou e como corrigi

| Erro da IA | Como percebi | Correção |
|---|---|---|
| Usou a estatística de Hopkins para dizer que "há clusters" (0,88–0,94) | Ela dá ~0,9 até numa nuvem gaussiana única | Nulo por permutação de colunas; ganho de silhueta ≈ 0 |
| Correlação likes/seguidor × seguidores de −0,999 lida como achado | O mesmo valor aparece com likes embaralhados | Registrado como artefato de razão (denominador compartilhado) |
| Ranking de SHAP e R² de treino (~0,1) se apresentavam como "fatores" | Comparação com o modelo de alvo embaralhado e com o R² de validação (≤ 0) | Toda importância é mostrada ao lado do controle; o previsor só adota um modelo que bata a média |
| ~22 segmentos com p < 0,05 viraram candidatos a insight | É exatamente o número esperado por acaso em 450 testes | Correção FDR obrigatória em toda bateria, inclusive global entre plataformas |
| "Disclosure explícito: compliance sem perda de engajamento" | Checagem 1: o rótulo não aparece no texto do post (#ad em 2,3%, igual aos orgânicos) | Auditoria de disclosure; a ação passou a ser "rótulo verificável no texto" |
| Faixas de "duração" misturando segundos (vídeo) e palavras (texto); imagem com duração | Checagem 1, com a descrição oficial | Duração só por formato e na unidade certa; aviso no site |
| "**Priorizar** beauty em espanhol no TikTok" e "tirar horário do checklist" ao lado de "postar cedo no YouTube" | Checagem 2: contradição com a própria tese de que os dados são ruído | Fila de testes com nº de posts por grupo; o horário no YouTube virou desempate de agenda (A/B exigiria ~17 mil posts) |
| Teto de 10.050 seguidores e "evita US$ 109 mi" apresentados como achados | Checagem 2: o teto é uma conta das premissas de custo, não um efeito medido | Fórmula + tabela de sensibilidade; US$ só como ordem de grandeza; a ação robusta é pagar por resultado |
| Site estático apontando para um template inexistente | Checagem 2 | Substituído pelo app com servidor e testes de rota |
| Operacionais: `git add -f` levou `__pycache__`; `pkill -f` derrubou o próprio shell; `RidgeCV` travou em TF-IDF esparso; versões antigas não compilavam no Python 3.14 | Erros na execução | Registrados em [`knowledge/environment.md`](../knowledge/environment.md) e corrigidos (commit `c280d77`, Ridge com `sparse_cg`, versões fixadas) |

## O que eu adicionei que a IA sozinha não faria

- **Desconfiar antes de concluir.** Exigi entender os dados por conta própria (EDA) antes da estratégia. Foi isso que revelou que o dataset é simulado e mudou toda a entrega: provar o que não funciona, com rigor, em vez de inventar insight.
- **Hipóteses de negócio que a IA não levantou:** separar por plataforma (é como o time opera), "quem posta importa?", "o que se sabe antes de postar?", chance de virar destaque por formato.
- **Contestar a IA com o gráfico** ("entre 20 e 150 s parece ter mais picos"). Forçou a distinguir contagem de taxa e a registrar a janela > 480 s como hipótese escolhida a posteriori.
- **Equilíbrio entre rigor e utilidade.** Pedi que as variações virassem insights, mas com nível de evidência. Isso gerou a fila de testes em vez de "nada a reportar".
- **Checagem cruzada em sessões separadas** (descrição do dataset e revisão crítica), que encontraram os erros mais graves da sessão principal.
- **Produto para o público certo:** site para leigos, resumo primeiro e detalhes sob demanda, painel simples, "Simular post", horário tratado como relógio único (decisão minha, em vez de inventar fuso).

## Evidências

| Evidência | Onde |
|---|---|
| Prompts do autor, em ordem | [`prompts.md`](prompts.md) |
| Conversas exportadas das 3 sessões (principal + 2 checagens) | [`../evidencias/`](../evidencias/) |
| Decisões e alternativas descartadas | [`../DEVELOPMENT_PROCESS.md`](../DEVELOPMENT_PROCESS.md) |
| Revisão crítica e status das correções | [`../review/critica-entrega.md`](../review/critica-entrega.md) |
| Scripts de sondagem e saídas | [`probe_eda.py`](probe_eda.py) · [`probe_description_gaps.py`](probe_description_gaps.py) (+ `_output.txt`) |
| Achados por tema | [`../knowledge/`](../knowledge/) |
| Evolução do código | `git log --oneline` na branch `submission/rafael` |
