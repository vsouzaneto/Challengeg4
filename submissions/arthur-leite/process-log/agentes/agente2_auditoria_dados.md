# Agente 2: auditoria de dados e números

**Papel:** auditor de dados independente e adversarial, somente leitura no projeto.
**Data:** 2026-10-14. **Commit auditado:** `ae391b0`. O working tree tinha apenas `solution/03-prototipo/app.py` modificado pelo Agente 1, que não foi auditado aqui.
**Método:** recalculei tudo do zero a partir dos CSVs, com código próprio e sem importar os scripts do projeto. A única exceção é o `motor_triagem.joblib`, carregado só para comparar os limiares com os da minha reimplementação. Depois rodei os scripts oficiais e comparei as saídas com o git. Nenhuma API de LLM foi chamada. Os pareceres anteriores (fase 1, 3 e 5) foram lidos para evitar repetição, mas nenhum número deles foi aceito sem recálculo.

---

## 1. Integridade dos dados

| Item | Resultado | Veredito |
|---|---|---|
| DS1 `customer_support_tickets.csv` | 3.945.533 bytes; SHA-256 `b06a9cde…9dd4d4`… (completo: `b06a9cde84da65db388bd964d75f88ee1eed96607cf75d0c35f09c3f11bf8bea`); 8.469 registros (29.808 linhas físicas por causa de quebras de linha dentro dos textos), 17 colunas, 8.469 Ticket IDs únicos | CONFERE |
| DS2 `all_tickets_processed_improved_v3.csv` | 14.568.920 bytes; SHA-256 `044fdace33fa564e1e60453f2941dafc95539c99878b0d32746950394b9dd4d4`; 47.837 registros + cabeçalho; 2 colunas; 0 nulos; 0 textos duplicados | CONFERE |
| Origem Kaggle | Os dois arquivos são **byte a byte idênticos** às cópias do cache do `kagglehub` (`~/.cache/kagglehub/datasets/suraj520/customer-support-ticket-dataset/versions/1/` e `.../adisongoh/it-service-ticket-classification-dataset/versions/1/`), ou seja, versão 1 dos dois datasets citados. Sem rede, não consegui comparar com o servidor do Kaggle | CONFERE (versão 1 via cache do kagglehub) |
| `data/` versionado? | Não: `.gitignore` da submissão ignora `data/`. O avaliador baixa com `baixar_dados.py` | ok |
| Respostas do LLM | Os 4 `.jsonl` de `benchmark/outputs/llm_respostas/` são idênticos aos de `data/cache/` (`cmp`) | CONFERE |

## 2. Reprodução dos scripts oficiais

Rodados a partir de `submissions/arthur-leite`:

| Script | Código de saída | `git diff` da saída |
|---|---|---|
| `solution/01-diagnostico/01_auditoria_dados.py` | 0 | `auditoria.md` idêntico |
| `solution/01-diagnostico/02_modelo_desperdicio.py` | 0 | `modelo_desperdicio.md` idêntico |
| `solution/03-prototipo/benchmark/avaliar_motor.py` | 0 | `motor_final.md` idêntico |
| `solution/03-prototipo/benchmark/benchmark.py` (extra) | 0 | `benchmark.md` mudou **só nos tempos de treino** (30 s → 29 s; 6 s → 9 s). `faixas.json` e `curva_*.csv` ficaram idênticos. Restaurei com `git checkout -- …/benchmark.md` |

Estado final do working tree: só `app.py` modificado, pelo Agente 1.

Observação: `02_modelo_desperdicio.py` e `avaliar_motor.py` usam o `data/cache/motor_triagem.joblib` quando ele existe. Para confirmar que esse cache não estava velho, retreinei o motor com código próprio. Os limiares deram iguais até a 4ª casa (Hardware 0,7836; Miscellaneous 0,7504; demais 0,7085; sugere 0,3543), e todas as métricas do motor bateram (seção 3.2).

---

## 3. Recálculo independente: número por número

### 3.1 Auditoria do DS1

| Número | Documento(s) | Valor citado | Meu recálculo | Veredito |
|---|---|---|---|---|
| Registros DS1 | todos | 8.469 | 8.469 | CONFERE |
| Janela de tempo | auditoria, README, relatório, log | 27 h | 27,03 h (31/05/2023 21:53 a 02/06/2023 00:55) | CONFERE |
| Resolução antes da 1ª resposta | auditoria, README, relatório, log | 49% (1.365 de 2.769) | 1.365/2.769 = 49,3% (2 empates) | CONFERE |
| CSAT uniforme | auditoria, README, log | 553/549/580/543/544; p = 0,80 | χ² = 1,666; p = 0,797 | CONFERE |
| Status equiprováveis | auditoria, README, log | p = 0,33; 67% não fechados | χ² = 2,23; p = 0,328; 67,3% | CONFERE |
| Pares associados | auditoria, README, relatório | 0 de 21 | 0 de 21 (menor p = 0,078) | CONFERE |
| V de Cramér corrigido, máximo | auditoria, log 1.1 | 0,021 | 0,0213 (sem correção: 0,0722) | CONFERE |
| V máx. 0,072 | PROCESS_LOG Fase 1 (texto histórico) | 0,072 | é o V **sem** correção; o próprio log corrige isso na 1.1 | CONFERE (histórico) |
| ρ Ticket ID × FRT | auditoria | 0,14; p < 0,001 | 0,1419; p = 8,5×10⁻²⁷ | CONFERE |
| Classificador na descrição | auditoria, README | 6,4% × 6,8%; 19,5% × 20,7%; 24,9% × 25,9% | Mesmo protocolo (CV de 5 dobras sem embaralhar): números iguais. Com dobras embaralhadas: 5,9% / 19,8% / 25,0%. A conclusão (abaixo do chute) se mantém | CONFERE |
| Poder estatístico | auditoria, README, log | 0,21 ponto (~692 por grupo, DP 1,41) | DP 1,407; 692,25 por grupo; MDE 0,2119 | CONFERE |
| Idem | relatório | "0,2 ponto" | 0,21 | CONFERE (arredondamento) |
| CSAT: 10 testes, Bonferroni 0,005, 2 p < 0,05 | auditoria, README | idem | Reproduzido pelo script (Kruskal 0,699/0,807/0,629/0,278/0,667/0,625; Spearman 0,254/0,832/0,035/0,041) | CONFERE |
| Combinações canal × prioridade × tipo | auditoria, README, relatório, log | 80 | 80 | CONFERE |
| 3 "piores" | auditoria | Email·Medium·Product inquiry 3,4 h (−0,6 a 7,5; n = 21); Chat·Low·Billing 3,3 h (1,1 a 5,4; n = 35); Chat·High·Refund 3,0 h (−0,3 a 6,2; n = 41) | 3,418 (IC −0,64 a 7,48; 21); 3,256 (35); 2,975 (41) | CONFERE |
| 3 "melhores" | auditoria | Email·Critical·Product −4,1 h (40); Social·Medium·Cancellation −3,4 h (25); Chat·Medium·Technical −3,2 h (30) | −4,135 (40); −3,419 (25); −3,248 (30) | CONFERE |
| Gap pior − melhor | auditoria, README, relatório, log | 7,6 h | 7,553 h | CONFERE |
| Gap médio sob acaso | auditoria, README, relatório, log | 8,1 h | 8,14 h (5.000 permutações, semente própria) | CONFERE |
| Permutação | auditoria, README, relatório, log | p = 0,68 | p = 0,686 | CONFERE |
| Kruskal-Wallis entre as 80 combinações | auditoria | p = 0,37 | p = 0,372 | CONFERE |
| Mediana de "duração" Critical × Low | PROCESS_LOG Fase 1 | 6,0 h × 7,1 h | Com sinal: 0,35 h × 0,35 h; em módulo: 6,55 × 6,98 h; mod 24: 11,3 × 11,7 h. **Nenhuma leitura reproduz 6,0 × 7,1** | **DIVERGE** (não reproduzível) |

### 3.2 Motor de triagem (DS2, teste de 9.568 tickets)

Reimplementação própria: TF-IDF com 1-2 gramas, `min_df=2` e `sublinear_tf`; regressão logística com C = 5; 20% de teste (seed 42) e validação de 12,5% do restante (seed 42); limiar por classe na validação (precisão ≥ 95% quando a classe tem ≥ 150 casos previstos, nunca abaixo do global); faixa de sugestão com top-2 ≥ 90%; trava de similaridade de cosseno < 0,20 com o vizinho de treino mais próximo; trava de cobertura de vocabulário < 50%.

| Número | Documento(s) | Valor citado | Meu recálculo | Veredito |
|---|---|---|---|---|
| Divisão treino / validação / teste | benchmark, relatório | 33.485 / 4.784 / 9.568 | idem; 0 textos repetidos entre treino e teste | CONFERE |
| Faixa automática | motor_final, README, proposta, relatório, modelo_desperdicio, log | 65,5% com 96,4% de acerto | 65,51% · 96,38% (n = 6.268) | CONFERE |
| IC95% da faixa automática | motor_final, README, proposta, relatório | 95,9 a 96,8% | bootstrap 95,90–96,83%; Wilson 95,89–96,81% | CONFERE |
| Top-2 na faixa automática | motor_final | 99,4% | 99,38% | CONFERE |
| Faixa de sugestão | todos | 23,3%; top-1 63,4%; top-2 91,0% | 23,27% · 63,43% · 90,97% | CONFERE |
| Idem | relatório | "91%" | 90,97% | CONFERE |
| Faixa humana | todos | 11,2% (72,4% de acerto; top-2 90,2%) | 11,22% · 72,44% · 90,22% | CONFERE |
| Decomposição da faixa humana | motor_final, README, proposta, relatório | 9,7% pela trava + 1,5% por confiança baixa | 9,70% (100% pela similaridade; a trava de vocabulário barra 0%) + 1,53% | CONFERE |
| Acerto nos barrados pela trava | motor_final, proposta, log | 78,6% ("79%") | 78,56% | CONFERE |
| Destino sem trava | motor_final | auto 55,7 / sugere 41,8 / humano 2,5% | 55,71 / 41,81 / 2,48% | CONFERE |
| Acerto na confiança baixa | motor_final | 33,6% | 33,56% | CONFERE |
| Limiares por categoria | motor_final, proposta | Hardware 0,78; Misc 0,75; demais 0,71 | 0,7836; 0,7504; 0,7085 | CONFERE |
| "cada categoria só é automatizada acima do limiar em que atinge ≥ 95% na validação" | proposta 1.1 | por categoria | **Administrative rights tem só 124 casos previstos na validação (< 150)** e usa o limiar global. Na prática, só Hardware e Miscellaneous têm limiar próprio | DIVERGE (redação imprecisa) |
| Acerto por categoria (auto) | motor_final, README, proposta, relatório | Access 97,8; Admin 96,0; HR 95,8; Hardware 95,1; IP 96,4; Misc 96,0; Purchase 99,0; Storage 97,8 | 97,83 / 95,98 / 95,79 / 95,14 / 96,44 / 96,05 / 99,02 / 97,76 | CONFERE |
| "Todas as 8 categorias ≥ 95%" | README, relatório | ≥ 95% | Vale só para a estimativa pontual. IC95% (Wilson) de Hardware: ≈ 94,0–96,1% (n = 1.563); de Admin rights: ≈ 92,7–98,0% (n = 174). Hardware tem ~40% de chance de estar abaixo da meta | CONFERE COM RESSALVA |
| Faixa A global (benchmark §3) | benchmark | 74,2% · 95,1%; sugere 24,1% | 74,15% · 95,11%; 24,08% | CONFERE |
| Fora do domínio sem travas | motor_final, README, proposta, relatório, log | 34,1% ("34%") | 34,10% | CONFERE |
| Fora do domínio com travas | motor_final, README, proposta, relatório, log | 10,8% ("11%") | 10,80% (humano 80,48%; sugere 8,71%) | CONFERE |
| Trava de 0,20 "barra 82% fora do domínio e 9,5% dos normais" | PROCESS_LOG Fase 4 | 82% / 9,5% | 80,1% do DS1 / **9,7% no teste / 10,4% na validação** | **DIVERGE** (número de versão anterior, sem indicação de base) |
| "43%" fora do domínio | PROCESS_LOG Fase 4 e docstring de `triagem.py` | 43% | Não reproduzível com o código atual. O log explica que vem de uma versão anterior (limiar global, sem igualar o pré-processamento). A docstring de `src/triagem.py` ("deixava passar 43%") continua sem essa ressalva | DIVERGE (histórico; docstring desatualizada) |

### 3.3 Benchmark

| Número | Documento(s) | Valor citado | Meu recálculo | Veredito |
|---|---|---|---|---|
| A no teste completo | benchmark, README, proposta, log | 86,0%; F1m 0,860 | 0,8603; 0,8597 | CONFERE |
| A na amostra de 400 | benchmark, README, proposta, relatório | 85,0% (F1m 0,864) | 0,850 | CONFERE |
| B (MiniLM + regressão logística) | benchmark, log | 80,8%; F1m 0,813 | 0,8077; 0,8130 | CONFERE |
| B na amostra | proposta | 78,2% | 0,7825 | CONFERE |
| kNN-5 | benchmark, README, proposta, log | 73,3% (F1m 0,724) | 0,7325; 0,7235 | CONFERE, com ressalva metodológica (§4.5) |
| Relatório: "73%" | relatório | 73% | 73,25% | CONFERE |
| LLM zero-shot | todos | 44,0% (F1m 0,412) | 0,4400; 0,4117 (IC95% 39,0–48,8%) | CONFERE |
| LLM few-shot | benchmark, proposta | 48,0% (F1m 0,490) | 0,4800; 0,4902 | CONFERE |
| LLM RAG | benchmark, README, proposta, log | 76,9% (n = 399) | 0,7694 (307/399) | CONFERE |
| Relatório: "77%" | relatório | 77% | 76,9% | CONFERE |
| 3.8-flash few-shot | todos | 53,5% (n = 200) | 0,5350 (IC95% 46,5–60,0%) | CONFERE |
| Relatório: "54%" | relatório | 54% | 53,5% | CONFERE (arredondamento para cima; ok) |
| McNemar A × RAG | benchmark, README, proposta, relatório, log | 53 × 21; p = 0,0003 | 53 × 21; binomial exato p = 2,56×10⁻⁴ | CONFERE |
| McNemar A × 3.8-flash | benchmark | 70 × 7; p < 10⁻¹³ | 70 × 7; p = 3,5×10⁻¹⁴ | CONFERE |
| "Um id não voltou na resposta de um lote (399/400)" | benchmark | id não voltou | O arquivo tem **400 ids únicos**. O LLM devolveu **973 no lugar de 9735** (id truncado), com a categoria certa de 9735 (HR Support). O id 973 não está no teste e foi descartado | DIVERGE (descrição imprecisa) |
| "inventou um id (973, inexistente)" | PROCESS_LOG 5.1 | inexistente | **O id 973 existe no DS2** (linha 973, "Internal Project", fora do teste). É truncamento de 9735 | **DIVERGE** |
| "1 em 1.400 respostas" | README, log | 1/1.400 | 1 id fora do teste em 1.400 linhas | CONFERE |
| Corrigindo o id truncado | — | — | RAG passaria a 308/400 = 77,0% (sem impacto) | — |
| Latência de A | PROCESS_LOG Fase 3 | 0,04 ms | benchmark.md: 0,06 ms (medida de relógio, varia por máquina) | DIVERGE (baixa; entre documentos) |
| Termos de "Administrative rights" | proposta, log | outlook, upgrade, install, windows | top-5 dos coeficientes: outlook, upgrade, **issues**, install, windows | CONFERE |
| Termos de "Miscellaneous" | proposta | change, approval, groups | change, approval, approve, add, groups | CONFERE |
| "Administrative rights é, na prática, instalação de software" | relatório, log | — | upgrade aparece em 37,7% dos tickets da categoria, outlook em 28,2%, windows em 25,5%, install em 14,5% (contra < 2,5% nas demais) | CONFERE COM RESSALVA ("na prática" generaliza demais) |
| Distribuição de classes | log 0.5, auditoria | Hardware 13.617 (28,5%) × Admin 1.760 (3,7%) | idem | CONFERE |

### 3.4 Política

| Número | Documento(s) | Valor citado | Meu recálculo (regex próprio, DS2 inteiro) | Veredito |
|---|---|---|---|---|
| Segurança | README, proposta, relatório, `politica.py` | 0,7% (339) | 0,71% (339) | CONFERE |
| Saúde / afastamento | idem | 2,0% (934) | 1,95% (934) | CONFERE |
| Desligamento | idem | 2,3% (1.080) | 2,26% (1.080) | CONFERE |
| Aprovação financeira | idem | 10,4% (4.987) | 10,42% (4.987) | CONFERE |
| Privilégio | idem | 13,0% (6.222) | 13,01% (6.222) | CONFERE no número, mas veja §4.2 |
| Urgência | idem | 7,7% (3.682) | 7,70% (3.682) | CONFERE |
| Ao menos uma regra | README, proposta, relatório, log | 27,7% | 27,66% | CONFERE |
| Bloqueiam rascunho / escalados | log, `politica.py` | 2,7% / 8,1% | 2,66% / 8,11% | CONFERE |
| No teste | motor_final, proposta | 27,9%; 2,7%; 7,9%; contagens 1265/1009/710/216/194/70 | 27,87%; 2,75%; 7,88%; idem | CONFERE |
| Segurança por categoria | proposta, relatório, log | Hardware 41%, Admin 19%, Access 17% | 41,3 / 18,6 / 16,8% | CONFERE |
| % das decisões de roteamento com humano | proposta | 34,5% | 23,27 + 11,22 = 34,49% | CONFERE |
| Exemplo #36521 | proposta | "suspicious sent monday… block following domains", rótulo Hardware; segurança | Texto e rótulo conferem; aciona só `seguranca`; o motor o roteia para Hardware no automático (0,84) | CONFERE |
| Exemplo #5461 | proposta | "leaver mobile phone…", Hardware; desligamento | Confere; aciona só `desligamento`; motor: Hardware, automático (0,98) | CONFERE |
| Exemplo #31874 | proposta | "maternity leaver form…", HR Support; saúde | Confere, mas também aciona **desligamento** ("leaver"), que a proposta não menciona. "Maternity leaver" é licença, não desligamento: é um falso positivo dentro do próprio exemplo | CONFERE COM RESSALVA |
| Exemplo #8682 | proposta | "new purchase po…", Purchase; aprovação humana | Confere (aciona `aprovacao_financeira` por "po"). Também aciona **privilégio**, só por causa da assinatura "kind regards **administrator**", o que a proposta não menciona. O texto pede registro de recebimento, não aprovação | CONFERE COM RESSALVA |
| "# = linha do CSV" | proposta | linha do CSV | O número é o **índice 0-based do pandas**. A linha física 36521 do CSV é outro ticket ("conference call for us is not working…"); o ticket #36521 está na linha 36523 | **DIVERGE** |
| Os 4 exemplos estão no teste? | — | — | Não: os 4 estão em treino/validação. Servem para ilustrar a política, mas a predição do motor sobre eles é dentro da amostra | ressalva |

### 3.5 ROI

| Número | Documento(s) | Valor citado | Meu recálculo | Veredito |
|---|---|---|---|---|
| Custo/hora | modelo_desperdicio, relatório ("R$ 38") | R$ 38,24 | 6.959 / (42 × 52 / 12) = 38,236 | CONFERE |
| FTE | modelo_desperdicio | 1.747 h | 42 × 52 × 0,8 = 1.747,2 | CONFERE |
| Horas hoje | modelo_desperdicio, README ("~1.500 h") | 750 / 1.500 / 2.500 | idem | CONFERE |
| Horas com IA | modelo_desperdicio | 198 / 282 / 394 | 198 / 282 / 394 | CONFERE |
| Tempo liberado | todos | 552 / 1.218 / 2.106 h ("~1.200; 550 a 2.100") | 552 / 1.218 / 2.106 | CONFERE |
| FTE | todos | 0,3 / 0,7 / 1,2 | 0,32 / 0,70 / 1,21 | CONFERE |
| R$/ano | modelo_desperdicio; relatório e proposta ("21/47/81 mil") | 21.105 / 46.563 / 80.508 | 21.105 / 46.563 / 80.508 | CONFERE |
| Nota: 10 s = 0,17 min | `roi.py` | 0,17 | Com 10 s exatos: 553 / 1.219 / 2.107 h; R$ 21.147 / 46.605 / 80.549. Diferença ≤ 1 h; já apontada pelo juiz da fase 3 | irrelevante |
| Premissa de 3 min = "84%" do resultado | PROCESS_LOG 3.1 | 84% | Número da v1 (com retrabalho). Na v2 a triagem é 100% do número, e o próprio documento passa a dizer "o resultado depende quase só" dela | histórico; ok |

### 3.6 Outras afirmações em documentos

| Afirmação | Documento | Veredito |
|---|---|---|
| "plano de instrumentação (30 dias)" × instrumentação na "semana 0" | relatório | Diverge entre seções do mesmo relatório; a proposta concilia ("≈ 30 dias" ao fim do piloto). Baixa |
| "Ruído de rótulo 15 a 25% (ex.: pedido de acesso a fila rotulado como `Storage`)" | auditoria.md, README, relatório | A faixa vem de uma leitura manual de **32 tickets** pelo juiz (5 duvidosos + 3 ambíguos). Com n = 32, o IC95% de 8/32 vai de ~11% a ~43%. Apresentar como "estimado de 15 a 25%" dá uma precisão que a amostra não tem. O exemplo citado ("acesso a fila → Storage") não aparece na lista de exemplos do parecer da fase 1. NÃO VERIFICÁVEL / ressalva |
| Formato numérico do `motor_final.md` §2 | motor_final | A coluna "Limiar" usa ponto ("0.71"), enquanto o resto do documento está em pt-BR. Baixa |
| "A: … custo zero, 0,04 ms" | log Fase 3 | ver 3.3 |

---

## 4. Problemas metodológicos que os pareceres anteriores não pegaram

**4.1 A trava de domínio foi calibrada olhando o conjunto de teste, não só o DS1.** O log registra "limiar de 0,20: barra 82% fora do domínio e 9,5% dos normais". Não existe código de calibração no repositório, e o README admite só o lado fora do domínio ("escolhido com os mesmos dados usados para avaliá-lo"). Para a validação, o número é 10,4%. Para o teste, 9,7%. Nenhum dos dois é 9,5%, então não dá para saber qual conjunto foi usado. A sensibilidade é muito alta: com limiar 0,15, só 36% do DS1 é barrado (e 1,3% do teste); com 0,20, 80% e 9,7%; com 0,25, 96% e 23%. Os números oficiais (65,5% automático, 11,2% humano, 34% → 11%) dependem de um hiperparâmetro escolhido a olho, possivelmente com o teste. Recomendação: declarar que a trava foi escolhida por inspeção e mostrar essa tabela de sensibilidade, ou recalibrar só na validação.

**4.2 A regra de "privilégio" é, em metade dos casos, a assinatura "administrator", e quase não cobre a categoria que deveria proteger.**
- Dos 6.222 tickets que acionam a regra (os 13,0% citados), **3.130 (50%)** contêm só a palavra "administrator", em geral numa assinatura ("kind regards administrator"). Desses, 1.971 são Purchase. Por isso Purchase responde por 32% dos alertas de privilégio.
- A regra dispara em apenas **4,5%** dos tickets rotulados "Administrative rights".
- Consequência: "Privilégio de acesso 13,0%" e "27,7% dos tickets têm uma ação que exige humano" medem **acionamento de palavra-chave**, e não a quantidade de ações sensíveis. O controle de "concessão de privilégio exige aprovação" deixa passar ~95% da categoria de direitos administrativos.
- Isso é mais grave que os "falsos alarmes que custam segundos" que os documentos admitem.
- Na regra de desligamento, há falso positivo parecido: "maternity leaver" (licença-maternidade) aparece em 122 tickets, 11% dos 1.080 alertas, e está inclusive no exemplo #31874.
- Recomendação: tirar "administrator" do padrão (ou ignorar a assinatura), medir a cobertura da regra por categoria e qualificar o 27,7% como "aciona alerta".

**4.3 Identificadores dos exemplos.** "# = linha do CSV" está errado: o número é o índice 0-based. Um avaliador que abrir o CSV na linha 36521 encontra outro ticket. Trocar para "índice da linha (0-based) no CSV" ou somar 2.

**4.4 O episódio do id do LLM está descrito de três jeitos, e nenhum é exato.** O benchmark diz "não voltou"; o log diz "inventou… inexistente"; o README diz "inventou". O que aconteceu: o LLM truncou 9735 para 973, e 973 existe no DS2 (é um ticket de treino). O impacto numérico é nulo (77,0% contra 76,9%), mas é uma afirmação factual errada num documento cujo diferencial é o rigor. Também mostra que a checagem de integridade deveria cruzar os ids com a **amostra**, e não só com o teste.

**4.5 O kNN-5 de referência fica um pouco subestimado pelo desempate.** `Series.mode()[0]` desempata em **ordem alfabética**. Com desempate pelo vizinho mais próximo (o padrão usual), o kNN-5 sobe de 73,3% para **76,0%**, praticamente igual ao LLM com RAG (76,9%). Isso **reforça** a frase do log ("o LLM com RAG pouco acrescenta ao próprio histórico"). Mas os documentos que mostram "RAG 76,9% > kNN 73,3%" sugerem um ganho do LLM de 3,6 pontos que é, em boa parte, efeito do desempate.

**4.6 "Todas as categorias ≥ 95%" é uma estimativa pontual.** Hardware tem 95,1% com n = 1.563 (IC ≈ 94,0–96,1%) e Admin rights tem 96,0% com n = 174 (IC ≈ 92,7–98,0%). O limiar de Hardware foi escolhido para encostar em 95% na validação. É honesto dizer "Hardware no limite" (o README e o relatório já dizem), mas a meta de ≥ 95% por categoria não está demonstrada com confiança estatística. Além disso, Admin rights, Internal Project (188 casos) e as demais usam o limiar global, e não um limiar próprio (ver 3.2).

**4.7 Vazamento entre treino e teste: não encontrado.**
- 0 textos idênticos entre treino e teste.
- O vetorizador e o índice de vizinhos da trava são ajustados só no treino.
- Os exemplos few-shot e os vizinhos do RAG vêm de treino + validação (`llm_classify.py`), nunca do teste.
- Os embeddings MiniLM são pré-treinados e não usam rótulos.
- Os limiares das faixas são escolhidos na validação (auto na validação: 70,0% de cobertura, 96,1% de precisão) e medidos no teste.
- A ressalva das quase-duplicatas (~0,6 ponto) já foi feita pelo juiz da fase 3.
- Os hiperparâmetros (C = 5, 1-2 gramas, min_df = 2) não têm registro de busca. Se foram escolhidos olhando o teste, o efeito deve ser pequeno, mas não dá para verificar.

**4.8 A "duração" da tabela de piores combinações é TTR − FRT, que o próprio documento declara não ser uma duração.** A tabela existe para responder literalmente à pergunta do Diretor, e o texto deixa isso claro. Ressalva: o IC95% usa aproximação normal com n = 21 a 41 e caudas largas. Isso não muda a conclusão, porque o teste de permutação é o argumento correto.

**4.9 Afirmações causais e redação.** Não encontrei confusão entre correlação e causalidade nos números. Três afirmações são opinião, ou mais fortes que a evidência:
- "Administrative rights é, na prática, instalação de software" (ver 3.3);
- "o tempo de espera na fila errada é provavelmente o maior ganho" (declarada como "provavelmente");
- o ruído de rótulo "de 15 a 25%" (ver 3.6).

---

## 5. Resumo das divergências

| # | Onde | Divergência | Gravidade |
|---|---|---|---|
| 1 | `politica.py`, proposta, README, relatório | "Privilégio 13,0%" e "27,7% exigem humano" são acionamentos de palavra-chave: 50% dos alertas de privilégio vêm só de "administrator" (assinatura), e a regra cobre só 4,5% dos tickets de Administrative rights | **média/alta** (metodológica) |
| 2 | README, relatório, log | A trava de 0,20 foi escolhida por inspeção, possivelmente olhando o teste ("9,5% dos normais"), e é muito sensível (0,15 → 36% barrados; 0,25 → 96%). Só o lado fora do domínio está declarado como otimista | média |
| 3 | proposta | "# = linha do CSV" é o índice 0-based; a linha física é # + 2 | média (o avaliador acha outro ticket) |
| 4 | log 5.1; benchmark; README | O id "973 inexistente" existe; era 9735 truncado. "Não voltou" também é impreciso | baixa/média |
| 5 | proposta, relatório, README | kNN 73,3% subestimado pelo desempate alfabético (76,0% com desempate pelo vizinho mais próximo, ≈ RAG) | baixa |
| 6 | proposta 1.1 | "cada categoria tem limiar calibrado ≥ 95% na validação": Admin rights (124 casos) e 5 outras usam o limiar global | baixa |
| 7 | log Fase 1 | Mediana de duração "6,0 h Critical × 7,1 h Low" não se reproduz | baixa |
| 8 | log Fase 4 | "82% / 9,5%" da trava × atuais 80,1% / 9,7% (teste) / 10,4% (validação) | baixa |
| 9 | `src/triagem.py` (docstring) | "deixava passar 43%": número velho, sem a ressalva do log (o atual é 34,1%) | baixa |
| 10 | log Fase 3 × benchmark | Latência 0,04 ms × 0,06 ms | baixa |
| 11 | proposta (#31874, #8682) | Os exemplos acionam regras extras não mencionadas: desligamento por "maternity leaver" e privilégio pela assinatura "administrator" | baixa |
| 12 | relatório | "Plano de instrumentação (30 dias)" × "semana 0" | baixa |
| 13 | auditoria, README, relatório | Ruído de rótulo "15–25%" estimado com n = 32 (IC real de ~11 a 43%); o exemplo "→ Storage" não é rastreável | baixa |
| 14 | motor_final | Limiares com ponto decimal ("0.71") num documento em pt-BR | cosmética |

**Todo o resto confere**, até a casa decimal publicada: DS1 inteiro, motor de triagem, benchmark, McNemar, frequências da política, os 4 exemplos (texto e rótulo) e o ROI. Os scripts oficiais reproduzem os outputs versionados byte a byte, exceto os tempos de treino do `benchmark.md`.

---

## 6. Código executado (trechos)

Scripts completos no scratchpad da sessão: `a2_ds1.py`, `a2_motor.py`, `a2_bench.py`, `a2_rag.py`, `a2_pol.py`, `a2_coef.py`, `a2_misc.py`, `a2_priv.py`.

```python
# DS1 (a2_ds1.py)
fr=pd.to_datetime(d['First Response Time']); tt=pd.to_datetime(d['Time to Resolution'])
allts=pd.concat([fr,tt]).dropna(); (allts.max()-allts.min()).total_seconds()/3600   # 27.03
dc=((tt-fr).dt.total_seconds()/3600)[d['Ticket Status']=='Closed']; (dc<0).sum()      # 1365 / 2769
stats.chisquare(csat.value_counts().sort_index().values)                              # p 0.797
def vc(a,b):  # Cramér V corrigido (Bergsma)
    t=pd.crosstab(a,b).values; chi,p,_,_=stats.chi2_contingency(t); n=t.sum(); r,k=t.shape
    phi=max(0,chi/n-(k-1)*(r-1)/(n-1)); rr=r-(r-1)**2/(n-1); kk=k-(k-1)**2/(n-1)
    return np.sqrt(phi/min(kk-1,rr-1)),p                                              # máx 0.0213; 0/21 p<.05
mde=(norm.ppf(.975)+norm.ppf(.8))*sd*np.sqrt(2/(len(cs)/4))                           # 0.2119
# permutação vetorizada (5.000 réplicas, semente 12345)
keys=f.groupby(k).ngroup().values; cnt=np.bincount(keys)
for _ in range(5000): p=rng.permutation(hv); m=np.bincount(keys,p)/cnt; sims.append(m.max()-m.min())
# gap 7.553 ; acaso 8.14 ; p 0.686 ; KW 0.372
```

```python
# Motor (a2_motor.py)
rest,te=train_test_split(d,test_size=.2,stratify=d.Topic_group,random_state=42)
tr,va=train_test_split(rest,test_size=.125,stratify=rest.Topic_group,random_state=42)
vec=TfidfVectorizer(ngram_range=(1,2),min_df=2,sublinear_tf=True); clf=LogisticRegression(C=5,max_iter=3000)
def thr(conf,ok,alvo,teto=np.inf):
    m=conf<teto; c=conf[m]; a=ok[m]; o=np.argsort(-c); pr=np.cumsum(a[o])/np.arange(1,len(c)+1)
    idx=np.where(pr>=alvo)[0]; return c[o][idx.max()] if len(idx) else min(teto,1.01)
lim[c]=max(g,thr(cv[m],okv[m],.95)) if m.sum()>=150 else g        # Hardware .7836, Misc .7504, resto .7085
sim=1-NearestNeighbors(n_neighbors=1,metric='cosine').fit(Xtr).kneighbors(Xt)[0].ravel()
band=np.where((sim<.2)|(cob<.5),'humano',np.where(ct>=L,'auto',np.where(ct>=ts,'sugere','humano')))
# auto .6551/.9638 ; sugere .2327/.6343/top2 .9097 ; humano .1122 ; trava .0970 ; conf baixa .0153
# IC bootstrap [.9590,.9683] ; DS1: auto .1080, sem travas .3410
```

```python
# Benchmark (a2_bench.py)
s400,_=train_test_split(te,train_size=400,stratify=te.Topic_group,random_state=7)
a=(pA[ids]==y).values; c=(p==y).values; b01=(a&~c).sum(); b10=(~a&c).sum()
stats.binomtest(min(b01,b10),b01+b10).pvalue        # rag: 53 x 21, p=2.56e-4
vote=[pd.Series(lab[r]).mode()[0] for r in vz]       # 0.7325 (desempate alfabético)
vote2=[next(l for l in lab[r] if l in top) ...]      # 0.7600 (desempate pelo mais próximo)
# rag: 400 ids únicos; id 973 fora do teste; 9735 ausente (973 = truncamento; 973 existe no DS2)
```

```python
# Política (a2_pol.py / a2_priv.py)
M=pd.DataFrame({k:t.str.contains(v) for k,v in R.items()})    # 339/934/1080/4987/6222/3682; any 27.66%
only_admin=t.str.contains(r'\badministrator\b') & ~t.str.contains(r'\b(admin|privileges?|rights|permissions?)\b')
only_admin.sum()                                              # 3130 de 6222 (1971 em Purchase)
ar.str.lower().map(lambda x: bool(pr.search(x))).mean()       # 0.045 dos tickets 'Administrative rights'
lines=open(csv).read().splitlines(); lines[36521-1]          # outro ticket: índice ≠ linha do CSV
```

```python
# ROI
ch=6959/(42*52/12); fte=42*52*.8
for m in [1.5,3,5]: hoje=30000*m/60; ia=30000*(a*.17+s*.5+h*m)/60  # 552/1218/2106 h; R$ 21105/46563/80508
```
