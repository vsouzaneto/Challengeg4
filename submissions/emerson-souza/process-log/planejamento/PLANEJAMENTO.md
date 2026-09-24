# G4 Analise: documento de regras do projeto

> **Este é o documento de referência.** Antes de qualquer passo, conferir aqui. Decisão nova ou mudança só entra com aprovação do Emerson e fica registrada no fim (Registro de mudanças).
> Status: ✅ decidido · 🟡 em discussão

---

## 1. O que é o sistema ✅
- **G4 Analise:** programa com **janela própria no computador**, como um software (ideia do Emerson).
- **Sozinho:** crio uma sessão, escolho **Churn, Suporte, Leads ou Mídia**, carrego os dados e o sistema entrega **o que o desafio correspondente pede**.
- **Cooperativo:** o resultado de uma análise pode ser usado por outra ferramenta com os mesmos dados. Exemplo-âncora: contas que o Churn indica que precisam de suporte melhor → a análise de Suporte roda nessas contas.
- Aceita os dados do desafio (1 clique) ou dados de outra empresa (De/Para de colunas).

## 2. Como vai ser entregue ✅
O desafio **não pede `.exe`**. Ele pede *"instruções de setup"* e avalia *"dá pra rodar seguindo as instruções?"*. O avaliador roda **na máquina dele**, que pode ser Windows, Mac ou Linux.

| Forma | Papel | Como |
|---|---|---|
| **1. Código-fonte** | **Obrigatória**: roda em qualquer computador | Um comando de início (`python iniciar.py`) que confere a versão do Python, cria o venv, instala as dependências e abre o sistema |
| **2. `.exe` Windows** | **Plus** | Gerado no Windows e publicado na Release do fork |

### Janela própria em qualquer computador
- Windows: a janela funciona direto.
- Mac/Linux: a janela pode exigir componentes do sistema. **Regra:** se a janela não abrir, o sistema abre **automaticamente no navegador**, com aviso. Nunca pode "não abrir".

### E se o avaliador tiver outra versão do Python?
- **Versões suportadas:** Python **3.11 a 3.14** ✅ (testado de verdade em 3.11, 3.12, 3.13 e 3.14.7). **A 3.10 saiu:** as versões atuais de numpy, pandas e streamlit exigem 3.11+, e a própria 3.10 encerra o suporte em out/2026. No 3.10, o `iniciar.py` mostra a mensagem clara (testado).
- **Dependências com versões fixas** em `requirements.txt`, escolhidas entre as que funcionam em todas essas versões → todo mundo instala exatamente a mesma coisa.
- **`iniciar.py` confere a versão** antes de tudo. Se estiver fora da faixa, mostra uma mensagem clara dizendo qual versão instalar e onde, em vez de um erro técnico.
- **venv obrigatório:** isola o projeto, não mexe no Python da máquina e **não precisa de administrador**.
- As instruções também trazem os comandos manuais (criar o venv e `pip install`), para quem preferir.

## 3. Tecnologias (derivadas das necessidades dos 4 desafios) ✅
Critério: o desafio sugere Python → **uma linguagem só**. Cada biblioteca entra **porque uma regra da seção 4 precisa dela**.

| Necessidade | Biblioteca | Desafios | Observação |
|---|---|---|---|
| Ler e cruzar tabelas (CSV/Excel) | pandas, numpy, openpyxl | 001–004 | |
| Testes estatísticos, intervalos de confiança | scipy | 001, 002, 004 | Mann-Whitney, qui-quadrado, Kruskal, bootstrap |
| Score, validação cruzada, classificador de texto | scikit-learn | 001, 002, 003 | TF-IDF + regressão logística já testado (86,6%) |
| Gráficos na tela | plotly | 001–004 | |
| Gráficos no PDF | matplotlib | Relatórios | Plotly → PDF exige navegador embutido; matplotlib é estável |
| PDF | reportlab | Relatórios | |
| Telas | streamlit | 001–004 | |
| Janela própria | pywebview | Núcleo | No Windows usa o Edge WebView2 (já vem no Windows 10/11); se falhar → navegador |
| Sessões | sqlite3 (vem com o Python) | Núcleo | |
| IA generativa (opcional) | anthropic (API) · Ollama local via HTTP (sem biblioteca extra) | 002, núcleo | O sistema funciona sem IA |
| Integração com o agente do G4 OS | mcp 1.30.0 (protocolo MCP, servidor local "stdio") | todos | Aprovada pelo Emerson em 24/09. Versão 1.x (a 2.x mudou a interface) |
| Testes automáticos | pytest | Desenvolvimento | Prova que os obrigatórios funcionam |
| Executável (plus) | pyinstaller | Entrega | |
| **Fora** | sentence-transformers / torch | — | +2 GB e risco com Python novo; o TF-IDF já passa de 86%. A comparação com outras abordagens fica no process log |

**Versões:** ✅ fixadas em `g4_analise/requirements.txt` (lock universal com marcadores por sistema: Windows, Mac, Linux). Principais: numpy 2.4.6 · pandas 3.0.6 · scipy 1.17.1 · scikit-learn 1.9.1 · plotly 7.1.0 · matplotlib 3.11.2 · reportlab 5.0.1 · streamlit 1.64.0 · pywebview 6.2.1 · anthropic 1.8.0 · openpyxl 3.1.5 · mcp 1.30.0 (instalação testada em 3.11 e 3.14). Desenvolvimento (`requirements-dev.txt`): pytest 9.1.1 · pyinstaller 6.22.3. Instalação testada em Linux (3.11–3.14) e **no Windows do Emerson (Python 3.14) sem erro** ✅.

## 4. Regras de negócio

### 4.1 Churn (001) ✅ (Emerson delegou)
Conferido nos dados em 23/09:
| Regra | Decisão | Por quê |
|---|---|---|
| Quem é cliente cancelado | `accounts.churn_flag = True` → **110 de 500 (22%)** | É o estado oficial da conta e o número de "~22%" do enunciado |
| Eventos de cancelamento | Usados para **motivo e data** | 352 contas têm eventos, 61 são reativações; 35 canceladas não têm evento; 277 com evento não estão marcadas. **Tudo isso aparece no bloco "Qualidade dos dados"**, sem esconder |
| Motivo de cada cancelada | O **último evento** da conta | Hoje: budget 22,7% · pricing 21,3% · features 20% · support 18,7% · competitor 9,3% · unknown 8% |
| Quanto se perdeu | MRR da **última assinatura** de cada conta cancelada, sem duplicar → **US$ 254.952/mês** | Somar todas as assinaturas encerradas infla o número |
| Sinais de risco | Queda de uso > 30% (recente × anterior) · erros em recurso beta · ticket escalado · 1ª resposta acima do limite · satisfação ≤ 2 · downgrade recente | Todos existem nos dados; **cada sinal é testado** (canceladas × ativas) e só entra com peso se mostrar diferença |
| Score de risco | 0–100, soma de pontos dos sinais, **pesos mostrados na tela**; faixas Alto / Médio / Baixo | Auditável e explicável para o CEO |
| Modelo preditivo | Sinal secundário, **sempre com validação cruzada**, com o resultado dito honestamente | Critério "correlação × causalidade" |
| Prioridade | **Risco × valor (MRR)** → "Salvar agora / Acompanhar / Monitorar" | *"Perder $50/mês ≠ perder $5K/mês"* |
| Impacto das ações | MRR das contas-alvo × taxa de recuperação **premissa editável** | O desafio pede impacto estimado |
| "Precisa de suporte" (ponte → Suporte) | Conta com score ≥ 30 **e** com chamado escalado, resposta lenta ou satisfação baixa no período | Liga Churn → Suporte com chave real (`account_id`) → **33 contas** com as premissas atuais (o número muda se as premissas mudarem) |
| **Ajustes feitos ao construir (conferidos nos dados)** | (a) satisfação baixa = nota **≤ 3** (a base só tem notas 3, 4 e 5; com ≤ 2 o sinal nunca acenderia); (b) resposta lenta = acima do **percentil 75 da própria base** (131 min), já que o limite fixo de 240 min nunca é atingido (máx. 180); (c) score com **pesos pelos dados** por padrão (só pontua sinal com p < 0,10), com opção de pesos de regra de negócio na tela; (d) ações ordenadas pela **força da evidência** e depois pelo impacto | Achados rodando o módulo nos dados reais |

### 4.2 Suporte (002) ✅ (conferida nos dados em 23/09)
| Regra | Proposta | Base nos dados |
|---|---|---|
| Duração do atendimento (DS1) | Resolução − 1ª resposta, **só quando positiva** → 1.402 tickets com duração válida (mediana 6,4 h); o restante aparece como excluído | Aprovado pelo Emerson |
| Onde trava | Mediana e percentil 90 da duração por canal, prioridade, tipo e **combinações** (mínimo de 30 tickets por grupo), com intervalo de confiança | Medianas quase iguais (Critical 6,0 h · Low 7,1 h; canais 6,0–6,5 h) → a conclusão provável é "não há gargalo estatístico", dito com números |
| Backlog | Volume parado por status (Open 2.819 · Pending 2.881) por canal/prioridade/tipo | É o gargalo que os dados mostram de verdade (67% não resolvidos) |
| O que impacta a satisfação | Teste estatístico por variável + tamanho do efeito; só "impacta" se passar no teste | Médias de 2,93 a 3,08 → "nenhuma variável muda a satisfação", dito com números |
| Desperdício | Horas acima da meta (SLA editável: Critical 4 h · High 8 h · Medium 24 h · Low 48 h) × R$ 45/h (editável) + custo do backlog | |
| Classificador (DS2) | Texto → categoria + confiança. Modelo base: TF-IDF + regressão logística | **Testado:** 86,6% de acurácia em 9.568 tickets nunca vistos (F1 médio 0,87) |
| Faixas de automação | Confiança **≥ 0,85 → automático** · **0,60–0,85 → IA sugere, humano confirma** · **< 0,60 → humano** | **Testado:** ≥ 0,85 cobre 57% dos tickets com 98% de acerto; ≥ 0,60 cobre 80% com 93,8% |
| O que NÃO automatizar | Prioridade Critical · Cancellation request · Refund request (DS1: envolvem dinheiro ou perda de cliente) · categorias de erro mais alto no DS2 (Administrative rights, F1 0,79: acesso e permissão = risco de segurança) · qualquer ticket abaixo de 0,60 | Exemplos reais serão tirados dos arquivos |
| Uso dos 2 datasets | DS1 = onde está o tempo e o volume; DS2 = prova que a classificação automática funciona e quanto dela é segura → **ROI** = volume do DS1 × parcela automatizável (DS2) × tempo economizado (premissa) | O desafio exige o cruzamento |
| Respostas sugeridas | **Não** usar as resoluções do DS1 (são texto aleatório). Só via LLM opcional, sempre revisadas por humano | Achado nos dados |
| Ponte Churn → Suporte ✅ | Tickets RavenStack das contas "precisa de suporte" → gargalos e desperdício (sem classificador, porque não têm texto). O plano da conta entra como "produto"; a 1ª resposta (minutos) vira horas | Construída: 33 contas → 155 chamados |
| Ponte Suporte → Churn 🟡 | Clientes (e-mail) com satisfação ≤ 2, ticket reaberto/pendente ou Cancellation request → lista de risco | 149 e-mails repetidos permitem ver recorrência |

### 4.3 Leads (003) ✅
| Regra | Proposta | Base nos dados |
|---|---|---|
| Normalização | "GTXPro" → "GTX Pro"; "technolgy" → "technology" | Achado |
| "Hoje" | 31/12/2017 (último dado) | |
| Deals avaliados | Abertos: Engaging (1.589) + Prospecting (500) | |
| Score 0–100 | Soma de fatores com pesos vindos do histórico Won × Lost: **taxa de ganho do vendedor** (55–70%) · produto · setor e porte da conta (se houver conta) · **tempo parado** comparado ao ciclo típico de um Won (mediana 57 dias) · valor esperado (preço × chance) | Vendedor é o fator com maior diferença |
| Proibido | Usar a duração do ciclo como fator positivo (vazamento: só se conhece depois de fechar) | Achado |
| Sem conta | Score calculado sem os fatores de conta, com aviso | 1.425 deals |
| Explicação | 3 principais motivos em frase (ex.: "+12: vendedor com 70% de ganho") | Exigido |
| Faixas | Quente / Morno / Frio + próxima ação sugerida | |
| Validação | O score separa Won × Lost no histórico? (medido em dados separados) | Critério "faz sentido" |
| Filtros | Vendedor, manager, região | Bônus citado pelo desafio |
| **Ajustes feitos ao construir (conferidos nos dados, 24/09)** | (a) **nenhum fator é comprovado**: vendedor 55–70% p = 0,26; produto p = 0,37; setor p = 0,97; porte p = 0,10 → entram com **suavização** (100 deals virtuais na média) e marcados como indício, com opção de desligar; (b) **tempo**: o que entra é a chance dos deals que *chegaram à mesma idade* (sem vazamento); (c) **parado** = aberto há mais que o maior ciclo já fechado (138 dias) → **62% dos abertos** (1.291 deals), −20 pontos (hipótese editável) e lista própria de requalificação; (d) **score = chance de ganhar (%)**, e a **ordem das listas = valor esperado** (chance × preço), para o valor não virar pontos misturados no score; (e) **faixas** relativas: Quente = terço de maior score dos deals vivos; (f) **validação** por foto do passado: AUC 0,50 → a base não permite prever ganho × perda, e o sistema diz isso | Achados rodando o módulo nos dados reais |

### 4.4 Mídia (004) ✅
| Regra | Proposta | Base nos dados |
|---|---|---|
| Engajamento | (curtidas + compartilhamentos + comentários) ÷ views, mais cada métrica separada | Não existe coluna pronta |
| Comparação justa | Sempre **dentro do mesmo estrato**: plataforma + categoria + faixa de seguidores (<10K · 10–50K · 50–100K · 100–500K · 500K–1M) | Exigido pelo desafio |
| "Funciona" | Só se o teste estatístico der diferença **e** o efeito for relevante (mínimo editável) | Patrocinado × orgânico: p = 0,80; plataformas: p = 0,36 → sem diferença |
| Custo implícito | Premissa editável: custo por mil seguidores do criador | Não existe custo no dataset |
| Política de patrocínio | Se não há ganho de engajamento, **o limite de seguidores é o mais barato que entrega o mesmo resultado** | Views iguais para 1K ou 1M de seguidores |
| Frequência de postagem | Analisada, com a limitação dita: cada criador tem ~10 posts em 2 anos, sem variação para medir | Achado |
| O que não funciona / parar | Pagar mais por criador grande, por plataforma ou por formato sem diferença comprovada | |
| Teste de sanidade | Numa **cópia** dos dados, injetar um efeito conhecido e mostrar que a ferramenta o encontra (rotulado como teste) | Prova que "sem diferença" é conclusão, não defeito |
| Inconsistências a mostrar | O mesmo criador aparece com seguidores diferentes em cada post e em várias plataformas | Achado |
| **Conferido ao construir (24/09)** | 15 dimensões testadas, todas "sem diferença" (maior diferença 0,13%); das 49 combinações, 4 parecem vencedoras num teste comum e nenhuma passa na correção de Bonferroni; patrocínio × orgânico dentro de 75 estratos: −0,01% (p = 0,77); views variam só 1% (base sintética); zero posts sem interação (viés de sobrevivência); teste de sanidade acha +9,6% quando injeta +10%; modelo preditivo R² ≈ 0 | Rodando o módulo nos dados reais |

## 4.5 Padrão de TODO módulo de análise ✅ (pedido do Emerson)
Cada módulo entrega uma **análise completa**, e não só dados:
1. **Resumo executivo em texto:** o que está acontecendo, em linguagem de gestor, com os números.
2. **Diagnóstico com gráficos:** cada gráfico com a frase do que ele mostra e o tamanho da amostra.
3. **Explicação do método:** como cada número foi calculado (regras da seção 4) e o nível de confiança.
4. **Listas acionáveis:** contas, tickets, deals ou posts específicos, com o motivo e exportáveis.
5. **Recomendações priorizadas:** o quê, para quem, impacto estimado e evidência (ou "decisão por custo, sem evidência").
6. **Interações:** filtros, premissas editáveis (custo/hora, SLA, limites) que recalculam na hora, e simulação de cenário.
7. **Qualidade dos dados e limitações:** o que o dado não permite afirmar.
8. **Relatório para baixar** (PDF + Markdown) e ajuda "como ler esta tela".

## 5. Particularidades de cada desafio (o que NÃO pode faltar)
Cada módulo tem que cumprir o "O que entregar" do seu desafio **como está escrito**:

| Desafio | Obrigatórios, do jeito que o desafio pede | Particularidade que muda a forma de fazer |
|---|---|---|
| **001** | 1) causa raiz **cruzando as tabelas** · 2) segmentos em risco **com contas específicas** · 3) ações **priorizadas com impacto estimado** | Distinguir **correlação × causalidade**; o CEO (não técnico) tem que conseguir agir |
| **002** | 1) **Diagnóstico:** onde trava (canal/prioridade/tipo e combinações) · o que impacta a satisfação · desperdício em **horas e custo** · 2) **Automação:** o que automatizar · **o que NÃO automatizar, justificado com exemplos dos dados** · como funciona na prática (ticket → IA → humano) | **Usar os 2 datasets** · *"automatizar 100% é red flag"* · os exemplos do "não automatizar" têm que vir **dos tickets reais** (ex.: categorias como HR Support e Administrative rights no DS2; tipos Cancellation/Refund request no DS1) · o protótipo tem que funcionar com dados reais, não com 3 exemplos |
| **003** | Solução que **roda** · **dados reais** · scoring que não é só valor · vendedor entende **o porquê** · docs de **setup, lógica e limitações** | O deliverable é **software**, não documento · explicabilidade · pensar no vendedor na **segunda de manhã** |
| **004** | 1) o que gera engajamento · patrocínio funciona? · audiência que mais engaja · o que NÃO funciona · 2) onde concentrar · **política de patrocínio com limite** · o que parar · quick wins | Comparação orgânico × patrocinado **justa** (controlar criador, plataforma, categoria) · recomendações **priorizadas** · o executivo entende em 5 min |
| **Todos** | Process log · README no template · setup | Evidências de uso de IA; sem elas, é desclassificado |

## 6. Regras da junção (cooperativo) ✅
Os 4 datasets são de **4 empresas diferentes**, sem chave em comum. Por isso existem **2 jeitos** de cooperar:
- **Tipo A: outra ferramenta nos MESMOS dados.** A ferramenta de um desafio roda nos dados de outro (ex.: a ferramenta de Suporte nos tickets da RavenStack).
- **Tipo B: resultado vira perfil.** O resultado de uma análise vira um **perfil** (país, idade, gênero, setor/categoria) que filtra a análise de outra base. Não liga pessoas, liga perfis.

Selo em todo cruzamento: 🟢 dado real · 🟡 proxy (sinal indireto) · 🔵 hipótese (regra editável) · ❌ não dá.

### Matriz completa (linha = dados de origem · coluna = ferramenta que recebe)
| Dados de → | Churn | Suporte | Leads | Mídia |
|---|---|---|---|---|
| **Churn** (RavenStack) | — | 🟢 **A**: tickets da RavenStack (prioridade, 1ª resposta, resolução, satisfação, escalonamento) → gargalos, satisfação e desperdício só das contas em risco. Sem classificador (não há texto) | 🟢 **A**: contas + assinaturas → score explicável de **valor × risco** ("vale a pena manter?") e contas com histórico de upgrade e baixo risco = oportunidade de expansão | 🔵 **B**: países das contas que mais cancelam → audiência desses países no social (em comum: UK, Alemanha, EUA, Índia; 4 dos 7) → que conteúdo usar em campanha de retenção |
| **Suporte** (DS1) | 🟡 **A**: tickets "Cancellation request" (1.695) = **intenção de cancelar** → o que diferencia esses clientes (produto, canal, idade, satisfação) + lista de clientes em risco | — | 🟡 **A**: tickets "Product inquiry" (1.641) = **oportunidades de venda**, priorizadas por produto e canal | 🔵 **B**: idade e gênero de quem mais reclama ou cancela → mesma faixa de audiência no social → que conteúdo falar com esse público |
| **Leads** (CRM) | ❌ não há cancelamento no CRM. Só dá **concentração de receita** (dependência de poucas contas) 🟡 | ❌ não há tickets. Só a **fila de onboarding** (deals ganhos → lista para o suporte receber) 🟡 | — | 🔵 **B**: países (em comum: Brasil, China, Alemanha, Japão, EUA) e setores onde mais ganhamos (tecnologia/software ↔ categoria "tech") → onde concentrar conteúdo |
| **Mídia** (social) | ❌ não há clientes nem cancelamentos | ❌ não há tickets | 🔵 **B**: perfil de audiência que mais engaja (país/categoria) → fator extra, **desligado por padrão**, no score de leads | — |

### Regras
- **Prioridade de construção:** 🟢 primeiro (Churn → Suporte e Churn → Leads) · depois 🟡 · 🔵 por último.
- Todo cruzamento Tipo B mostra na tela **quais valores casaram e quais não** (ex.: "4 de 7 países em comum").
- Onde a base de destino não tem sinal (Mídia), o cruzamento diz isso: *"nenhum perfil engaja mais que outro"*. Não inventa.
- ❌ aparece na tela como botão desabilitado, com o motivo (ex.: *"o CRM não tem cancelamentos"*).
- A junção **não pode enfraquecer** nenhum desafio: cada módulo cumpre sozinho 100% do seu obrigatório.

## 7. O que os dados mostraram (resumo) ✅
- **001:** inconsistências entre `churn_flag` e eventos (ver 4.1).
- **002:** DS1 com 8.469 tickets (não 30 mil); satisfação ≈ 3 em tudo; tempos são datas/horas → **duração = resolução − 1ª resposta, só quando positiva**, mostrando quantos saíram. DS2: 47.837 textos em 8 categorias.
- **003:** tem sinal (vendedor 55–70%); corrigir "GTXPro"/"technolgy"; 1.425 deals sem conta; cuidado com o vazamento de tempo.
- **004:** sem sinal (views ≈ 10.100, engajamento ≈ 0,199 em tudo) → provar com estatística, decidir pelo custo, testar a ferramenta com um efeito injetado (rotulado como teste).

## 8. Entrega ✅
- `submissions/emerson-souza/`: `README.md` (template) · `solution/` · `process-log/` (`screenshots/`, `chat-exports/`) · `docs/`.
- PR: `[Submission] Emerson Souza — Challenges 001, 002, 003 e 004`. Um PR só.
- Datasets grandes não sobem (vêm do Kaggle; o setup explica onde colocar).
- Guardar desde já: prints das conversas com IA, do sistema rodando e o diário.

## 9. Revisão dos 4 desafios: tudo contemplado?
| Desafio | Item obrigatório | Regra que cobre | Situação |
|---|---|---|---|
| 001 | Causa raiz cruzando tabelas | 4.1 sinais testados nas 5 tabelas | ✅ |
| 001 | Segmentos e contas específicas | 4.1 segmentação + lista de contas | ✅ |
| 001 | Ações priorizadas com impacto | 4.1 risco × valor + impacto por premissa | ✅ |
| 002 | Onde trava | 4.2 durações + backlog | ✅ |
| 002 | O que impacta a satisfação | 4.2 teste por variável | ✅ |
| 002 | Desperdício em horas e custo | 4.2 SLA × custo/hora | ✅ |
| 002 | O que automatizar / NÃO automatizar com exemplos | 4.2 faixas + lista de exclusão + exemplos reais | ✅ |
| 002 | Fluxo na prática | 4.2 faixas de confiança | ✅ (falta desenhar a tela) |
| 002 | Usar os 2 datasets | 4.2 ROI = DS1 × DS2 | ✅ |
| 002 | Protótipo com dados reais | Classificador testado em 9.568 tickets | ✅ |
| 003 | Roda, dados reais, score além do valor, explica o porquê | 4.3 | ✅ |
| 003 | Docs de setup, lógica e limitações | Seção 2 + docs | ✅ |
| 004 | O que gera engajamento / o que não funciona | 4.4 estratos + testes | ✅ |
| 004 | Patrocínio funciona (justo) + custo implícito | 4.4 estratos + premissa de custo | ✅ |
| 004 | Audiência que mais engaja | 4.4 mesmos testes por idade, gênero e local | ✅ |
| 004 | Onde concentrar, frequência, faixa de criador | 4.4 (frequência com limitação declarada) | ⚠️ dado insuficiente, declarado |
| 004 | Política de patrocínio com limite, parar, quick wins | 4.4 decisão por custo | ✅ |
| Todos | Process log, README, setup | Seções 2 e 8 | ✅ |

**Visual:** identidade própria ✅ [Emerson, 24/09]: visual próprio e sóbrio → barra lateral grafite (#14222E), cor principal petróleo (#0F4C5C), âmbar/tijolo/musgo para status, cantos retos (2px), fonte do sistema (Segoe UI), sem emojis (ícones de linha discretos e etiquetas de texto), cabeçalho próprio; tudo em `.streamlit/config.toml` e `app/nucleo/visual.py`. (Regra anterior "layout só no fim" foi antecipada pelo próprio Emerson.)

**Planejamento fechado.** Próximo passo: seção 10.

## 10. Ordem de construção ✅
Cada etapa só fecha quando funciona com os dados reais e está registrada no process log.
1. **Ambiente** ✅ (testado também no Windows): `g4_analise/iniciar.py` + `requirements.txt` + `requirements-dev.txt`.
2. **Núcleo** ✅ (falta abrir no Windows): janela própria (com o navegador como reserva), sessões e sub-sessões (SQLite), dados do desafio com 1 clique ou arquivos próprios (CSV/Excel/JSON), De/Para com sugestão automática, matriz de cruzamentos na tela. 14 testes automáticos passando.
3. **Churn (001)** ✅ completo no padrão 4.5 (resumo, causa raiz, segmentos e contas, plano de ação, modelo e método, qualidade, relatório PDF/MD, como ler, premissas editáveis). 23 testes passando.
4. **Suporte (002)** ✅ completo no padrão 4.5 (resumo, onde trava, satisfação, desperdício, automação com fluxo/ROI/exemplos reais, protótipo 'Testar ticket', qualidade, relatório). 32 testes passando no total.
5. **Cruzamentos 🟢:** Churn → Suporte ✅ (botão "Enviar para Suporte" cria a sub-sessão com selo 🟢). **Churn → Leads vai para o fim da etapa 6**, porque precisa da ferramenta de Leads pronta para rodar.
6. **Leads (003)** ✅ completo no padrão 4.5 (resumo, minha segunda-feira com 3 listas e filtros, visão do gestor, o que muda a chance, plano de ação, validação e método, qualidade, relatório, como ler). 45 testes passando. Ponte **Churn → Leads** ✅ como "carteira de expansão" (selo 🟡: sem vendedor e sem datas na base; histórico = as próprias contas).
7. **Mídia (004)** ✅ completo no padrão 4.5 (resumo, o que gera engajamento com combinações e hashtags, patrocínio justo com custo e política, audiência, estratégia priorizada com quick wins e o que parar, painel semanal, teste de sanidade + modelo preditivo, qualidade, relatório). 54 testes passando.
8. **Cruzamentos 🟡 e 🔵 + diferenciais** ✅. Pontes ativas (8): Churn → Suporte 🟢 · Churn → Leads 🟡 · Churn → Mídia 🔵 · Suporte → Churn 🟡 (o Churn passou a aceitar bases sem receita: valores viram contagem de clientes) · Suporte → Leads 🟡 **lista** (a base de suporte não tem vendas para o score aprender; vira CSV de oportunidades) · Suporte → Mídia 🔵 · Leads → Mídia 🔵 · Mídia → Leads 🔵. Tipo B: o perfil filtra a base de destino escolhida (dados do desafio ou uma sessão). ❌ ficam Leads → Churn/Suporte e Mídia → Churn/Suporte. Diferenciais do 004 que faltavam: **recomendar post** (engajamento esperado + se trocar formato/plataforma rende mais) e **clustering de audiência** (k-means por criador). 60 testes passando.
8a. **Correções da avaliação do Emerson (24/09)** ✅: botões "Salvar" gravam direto em Downloads\G4 Analise (o download do navegador não funciona na janela) · aba **📦 Exportar** (CSV dos dados analisados + Excel com tudo).
8c. **Integração com o G4 OS** ✅ (pedido do Emerson): `app/servidor_mcp.py` expõe o sistema ao agente do G4 OS como fonte MCP local (12 ferramentas: listar/obter/consultar só leem; criar sessão, cruzar e exportar pedem confirmação no modo Explorar; nada apaga nem executa ação no mundo). `app/servicos.py` separa a lógica da tela, então janela e agente usam o MESMO código e as MESMAS sessões. `INSTALAR_NO_G4OS.bat` (ou `python iniciar.py --g4os`) cadastra a fonte + skill no workspace do G4 OS, sem mexer no resto. Formato conferido na documentação oficial que vem dentro do G4 OS (sources.md, skills.md).
8b. **Conferência final do funcional** (todos os módulos e pontes no Windows, downloads) → só então visual (regra acima).
9. `.exe` + README + entrega.

## Revisão das anotações anteriores (23/09)
Conferi tudo o que foi anotado contra as regras acima. Correções:
- A lista de requisitos antiga marcava o **`.exe` como obrigatório** → **errado**. É um plus; o obrigatório é o código com instruções de setup.
- A lista de tecnologias antiga trazia **"Streamlit no navegador"** como opção → **descartado**. Janela própria, com o navegador só como reserva automática quando a janela não abre.
- A primeira análise falava em **~30 mil tickets** no 002 → o arquivo real tem **8.469**.
- O "não automatizar" do 002 não dizia de onde viriam os exemplos → agora é regra que venham **dos tickets reais**.
- Faltava o tratamento de **versões diferentes do Python** → seção 2.

## Registro de mudanças
| Data | Mudança | Quem |
|---|---|---|
| 24/09 | Identidade visual própria · teste real do agente no G4 OS · revisão completa (base mínima, pt-BR) | Emerson pediu · IA construiu e revisou |
| 24/09 | Integração com o G4 OS (servidor MCP + fonte + skill); biblioteca mcp 1.30.0 | Emerson pediu e aprovou a biblioteca · IA construiu |
| 24/09 | Etapa 8: pontes 🟡/🔵 e diferenciais; regra "layout só com o funcional 100%" | Emerson definiu a regra e a ordem · IA construiu |
| 24/09 | Etapa 7: módulo Mídia construído e testado · ponte Churn → Leads (opção A, 🟡) | IA construiu · Emerson escolheu a opção A e aprovou a etapa |
| 24/09 | Etapa 6: módulo Leads construído e testado; ajustes da regra 4.3 registrados | IA construiu · Emerson aprovou a etapa |
| 24/09 | Etapa 5: ponte Churn → Suporte construída e testada; Churn → Leads passa para depois do módulo Leads | IA construiu · Emerson aprovou a etapa |
| 23/09 | Nome G4 Analise · janela própria · 4 desafios · núcleo sozinho + cooperativo | Emerson |
| 23/09 | Tempos do 002 (resolução − 1ª resposta, só positivas) | Emerson aprovou |
| 23/09 | Entrega em 2 formas (código obrigatório + `.exe` plus) · Python em tudo · regras do Churn delegadas à IA | Emerson |
| 23/09 | Visual padrão por enquanto · ordem de construção | Emerson |
| 23/09 | Etapa 4 (Suporte) construída e testada | IA construiu · Emerson aprovou a etapa |
| 23/09 | Etapa 3 (Churn) construída e testada; ajustes da regra 4.1 registrados | IA construiu · Emerson aprovou a etapa |
| 23/09 | Etapa 2 (núcleo) construída e testada | IA construiu · Emerson aprovou a ordem |
| 23/09 | Etapa 1 (ambiente): faixa Python 3.11–3.14 (3.10 saiu por incompatibilidade testada), versões fixas | IA testou · Emerson |
| 23/09 | Matriz completa de cruzamentos (Tipo A e Tipo B), conferida nos campos reais | Emerson pediu · IA levantou |
| 23/09 | Propostas de regras 002–004 conferidas nos dados · revisão dos 4 desafios · bibliotecas derivadas das regras | IA propôs, Emerson aprovou |
