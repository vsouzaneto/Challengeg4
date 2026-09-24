# Revisão Cética comparativa — notebook Kaggle vs. Social Growth Decision System

> **Escopo:** revisão independente do notebook como artefato secundário. O checkpoint `22cf85409aaa3be1e4a54af50ef9a6ba13ac972e` não foi reaberto, reavaliado nem alterado. Seu parecer autoritativo continua sendo `PASS`, 10,0/10, `C0/H0/M0/L0`, limitado à validação humana e sem autorização de publicação ou experimento ao vivo (`skeptic-review.md`, linhas 3–8 e 23–25; `checkpoint-receipt.json`, chaves `authoritative_review` e `human_gate`).

## Veredito

**O notebook não revela sinal novo que invalide a tese aprovada.** Ele troca as perguntas decisórias por uma classificação preditiva de um rótulo artificial, não registra nenhuma execução e introduz acoplamento matemático e vazamentos que podem produzir desempenho aparente sem valor operacional.

Há um achado comparativo útil para uma versão futura: a definição do alvo do notebook é quase uma classificação inversa da base de seguidores. Na reprodução independente do cálculo da célula 3, a correlação entre classe e `follower_count` foi **−0,9790**; um classificador descritivo que usa apenas o quintil de seguidores reproduziu **96,19%** das classes, contra **20,00%** da classe majoritária. Isso **reforça**, não enfraquece, a tese aprovada de que feature engineering não cria evidência decisória e de que a semântica da métrica precisa ser auditada antes do modelo.

**Suficiência decisória do notebook:** `INSUFICIENTE_PARA_DECISAO`.
**Efeito sobre o checkpoint:** nenhum; a tese e os gates aprovados permanecem inalterados.

## Cético Jarvis — objeto: notebook Kaggle

**Schema Gate:** **FAIL**
**Semantic Score:** **2,7/10**
**Decision:** **REDO como evidência decisória** — não é uma decisão sobre o checkpoint.

### Schema Gate

| Checagem | Estado | Evidência |
|---|---|---|
| Artefato existe e é legível | PASS | `notebook.ipynb`, SHA-256 `bde2fc30e236f4c5c68edddd81a58747786341caea963f8081d77346801042ca`. |
| Título claro | WARN | O título existe apenas na metadata da API (`social-media-engagement-analyser`); não há célula markdown. |
| Objetivo declarado | WARN | O objetivo é apenas implícito em comentários como “Smart-Social Glass-Box pipeline” e na classificação em cinco classes (células 1 e 3). |
| Fonte/contexto identificado | WARN | A célula 2 aponta o CSV do Kaggle, mas o notebook não registra que a fonte é simulada nem seu hash/licença/limites. |
| Outputs verificáveis | FAIL | As 20 células têm `execution_count: null`; nenhuma contém output. Não há accuracy, ROC-AUC, matriz de confusão, importância ou SHAP registrados. |
| Entregável/decisão | FAIL | Há código para salvar modelo (célula 20), mas nenhum artefato salvo, conclusão ou decisão demonstrada. |
| Próximas ações | FAIL | Ausentes. |
| Riscos/limites | FAIL | Não há caveats sobre simulação, identidade, causalidade, atribuição, vazamento, validade externa ou múltiplas comparações. |
| Evidência nomeada | WARN | O CSV é nomeado, mas os resultados alegáveis não existem nos bytes do notebook. |
| Gate humano/efeito externo | N/A | O notebook só propõe gravação local; não autoriza ação externa. |

### Scorecard semântico

| Critério | Peso | Nota | Contribuição | Motivo |
|---|---:|---:|---:|---|
| Evidência | 30% | 2,5 | 0,75 | Usa o mesmo CSV, mas omite proveniência simulada e não contém execução nem resultados. |
| Clareza | 20% | 4,0 | 0,80 | Pipeline numerado e legível; pergunta de negócio, estimando e conclusão não são definidos. |
| Utilidade prática | 25% | 3,5 | 0,88 | Algumas técnicas são reaproveitáveis sob outro contrato; o modelo atual não orienta decisão válida. |
| Completude | 15% | 1,5 | 0,23 | Faltam outputs, baselines adequados, incerteza, ablações, limites e decisão. |
| Risco tratado | 10% | 0,5 | 0,05 | Vazamentos e riscos causais/deployment não são reconhecidos. |
| **Total** | **100%** |  | **2,70/10** |  |

## Comparação das perguntas

| Tema | Social Growth Decision System aprovado | Notebook Kaggle | Julgamento |
|---|---|---|---|
| Engajamento | “O que gera engajamento?” com razões das somas por 1.000 visualizações e bloqueio de vencedores (`evidence/decision-map.json`, `DEC-ENGAGEMENT-001`; `evidence/claim-evidence-map.json`, `CLM-ENGAGEMENT-001`). | Prediz quintis de `(likes + 2×shares + 0,5×comments) / followers` (célula 3). | **Estimandos diferentes.** O notebook não responde ao mecanismo nem à decisão; classifica um rótulo arbitrário. |
| Patrocínio | Pergunta incrementalidade, separa taxa bruta de componentes ajustados e bloqueia ROI/causalidade (`DEC-SPONSOR-001`; `reports/dataset-audit.md`, “Patrocinado versus orgânico”). | Compara média da classe ordinal por `is_sponsored` e depois por tercil de seguidores (células 17 e 19). | Não estima efeito, ROI ou causalidade. “Controlled by Creator Size” é linguagem excessiva para uma estratificação grosseira e sintética. |
| Audiência | Quantifica amplitudes pequenas e bloqueia segmentação (`DEC-AUDIENCE-001`). | Usa rótulos de audiência como one-hot no classificador (células 6–7). | Importância preditiva, mesmo se existisse, não autorizaria segmentação. |
| Criador | Demonstra identidade instável e bloqueia recomendação (`CLM-IDENTITY-001`; auditoria F-002). | Faz split por `creator_id` e chama o processo de “creator-level split” (célula 8). | O grupo não representa criador estável; o split não cumpre o que o título promete. |
| Tempo/frequência | Declara frequência não estimável e período sem vencedor (`strategy_matrix`). | Extrai hora, dia da semana e fim de semana e plota média da classe por hora (células 5 e 16). | Sem desenho causal, conta estável ou outputs, não qualifica a conclusão aprovada. |
| Texto/hashtags | Testa 970 termos com Welch e correção de Holm, mantendo caráter exploratório (`docs/prototype-scope.md`, “Hashtags”). | TF-IDF, TextBlob e contagem de vírgulas; inclui texto de comentários (células 4, 5 e 9). | Não há teste de hipótese, correção de multiplicidade ou garantia de disponibilidade no momento da decisão. |

## Evidência comparativa reproduzida

O CSV do diretório de auditoria tem SHA-256 `693a2df6e609d1c099f3430d9a5b894b224fe12b2420c0d93e6defe90d15f18e`, idêntico ao CSV congelado no checkpoint (`checkpoint-receipt.json`, `artifacts.data/extracted/social_media_dataset.csv`). Portanto, as diferenças abaixo são de método, não de amostra.

1. **Alvo dominado pelo denominador.** Reproduzindo literalmente a célula 3 nas 52.214 linhas:
   - classes balanceadas por construção: 10.442–10.443 linhas por classe;
   - correlação classe × seguidores: **−0,9790**;
   - correlação classe × numerador composto: **0,0311**;
   - no menor quintil de seguidores, **99,04%** das linhas caem na classe 4; no maior, **96,32%** caem na classe 0;
   - quintil de seguidores sozinho reproduz **96,19%** dos rótulos no conjunto completo.

2. **Patrocínio continua sem separação útil, mesmo no estimando arbitrário do notebook.** A média da classe foi **2,00010** no orgânico e **1,99987** no patrocinado. Na razão composta por seguidores, a diferença patrocinado − orgânico foi **0,000252** (aproximadamente **0,0252 ponto percentual**), IC 95% de Welch aproximado **[−0,0922; 0,1426] ponto percentual**. Isso não contradiz o sistema aprovado, que usa outro estimando e reporta, nos componentes ajustados, ICs contendo zero (`evidence/dataset-audit.json`, `/adjusted_sponsorship_effects`).

3. **O suposto agrupamento por criador é semanticamente inválido.** Todos os **5.000** `creator_id` aparecem com múltiplos nomes (mediana 10) e em todas as cinco plataformas. Além disso, **6.309** nomes mapeiam para mais de um ID. Esses números confirmam F-002 e tornam a célula 8 incapaz de garantir independência por pessoa/conta.

4. **Não há resultado do notebook a validar.** Há 20 células de código, zero células markdown, zero outputs e todos os contadores de execução são nulos. A metadata da API identifica autor, referência e uma data de última execução, mas os bytes entregues não preservam prova dessa execução.

## Sinais novos: o que muda e o que não muda

### Não invalida nem qualifica a tese principal

- Não há accuracy, ROC-AUC, SHAP ou gráfico materializado; logo, não existe evidência empírica nova proveniente do notebook.
- Um eventual bom score classificaria um quintil construído globalmente, não provaria crescimento, causalidade, ROI ou validade operacional.
- A aparente previsibilidade esperada decorre principalmente do uso de `follower_count` no denominador do alvo e novamente nas features.
- A comparação de patrocínio reproduz ausência de separação, não um efeito contrário ao diagnóstico aprovado.

### Qualificação útil para futura evolução, sem reabrir o checkpoint

Adicionar futuramente ao diagnóstico um teste explícito de **acoplamento matemático da métrica**: decompor numerador e denominador, medir sensibilidade a pesos e denominadores e comparar poder preditivo contra baselines de uma única variável. O resultado −0,9790/96,19% é um bom caso de teste para impedir que uma métrica derivada transforme porte em “engajamento”.

## Cálculos que merecem incorporação futura — com correções

1. **Sensibilidade da definição de engajamento.** Comparar, sem promover vencedor, componentes separados, razão por visualizações, razão por seguidores e compósitos com pesos pré-declarados. Reportar como a conclusão muda por definição. Não adotar os pesos `1/2/0,5` da célula 3 sem justificativa de negócio.
2. **Não linearidades e interações pré-declaradas.** O uso de árvore/boosting pode testar se a quase ausência de efeitos marginais esconde interações, uma limitação já reconhecida em `reports/dataset-audit.md` F-003. Exigir validação aninhada, holdout temporal, tamanho de efeito, incerteza, correção da família de hipóteses e réplica em dados reais.
3. **Ablation tests.** Comparar baseline, metadados pré-publicação, texto pré-publicação e combinação; excluir seguidores quando ele participa do rótulo e excluir qualquer variável indisponível no momento de decisão.
4. **Validação por entidade e tempo.** Só usar group split depois de estabelecer chave persistente de conta/conteúdo; adicionar corte temporal prospectivo para drift. O split da célula 8 não deve ser reutilizado com o `creator_id` atual.
5. **Explicabilidade estritamente preditiva.** SHAP pode descrever contribuição para previsão após validação do modelo; nunca deve ser traduzido como causa, alavanca ou recomendação. Incluir estabilidade entre folds e comparação com permutation importance.
6. **Interação patrocínio × porte.** A pergunta da célula 19 é pertinente como hipótese, mas deve usar contas estáveis, estimando contínuo pré-declarado, estratos com overlap, ICs, múltiplas comparações e, para causalidade, randomização/atribuição conforme `evidence/experiment-contracts.json`.

## Artefatos, leakage e claims proibidos

| Severidade | Problema | Evidência | Consequência |
|---|---|---|---|
| Crítica | **Acoplamento do alvo com feature.** `follower_count` é denominador do alvo e reaparece como `log_followers`/`is_big_creator`. | Células 3, 5 e 7; reprodução −0,9790. | Score alto pode medir a fórmula do rótulo, não conteúdo eficaz. |
| Crítica | **Leakage temporal/de deployment.** `comments_text` é concatenado ao texto preditor, embora comentários existam após publicação e o alvo inclua `comments_count`. | Célula 4; 43.526 textos não nulos distintos. | O modelo usa informação indisponível no momento de recomendar/publicar. |
| Alta | **Threshold leakage.** `qcut` é ajustado no dataset completo antes do split. | Células 3 e 8. | As fronteiras das classes incorporam validação/teste. |
| Alta | **Grupo sem identidade.** Split por `creator_id` instável. | Célula 8; `evidence/dataset-audit.json`, `/entity_integrity`. | Não prova generalização para novos criadores/contas. |
| Alta | **Sem execução auditável.** Métricas e gráficos só existem como código. | Células 11–19 sem outputs. | Nenhuma conclusão de performance pode ser aceita. |
| Alta | **Ordinalização perde magnitude.** Médias de classes 0–4 substituem a métrica contínua. | Células 16, 17 e 19. | Diferenças dentro de quintis somem; distância entre classes é tratada como uniforme sem base. |
| Média | **Pré-processamento global.** Dummies e `is_big_creator` são definidos antes do split; o target também. | Células 5–8. | Escopo de treino contaminado por estatísticas/vocabulário globais. |
| Média | **Texto multilíngue tratado como inglês.** `stop_words="english"` e TextBlob são aplicados a Chinese, Hindi, Japanese, Spanish e English. | Células 5, 6 e 9; auditoria `/categorical_counts/language`. | Features e sentimento não comparáveis entre idiomas. |
| Média | **Contagem de hashtags deslocada.** Conta vírgulas, não termos; uma hashtag recebe zero. | Célula 5. | Erro de mensuração simples e evitável. |
| Média | **SHAP não é causal.** | Célula 18. | Importância preditiva não autoriza estratégia. |
| Média | **“Controlled” indevido.** Tercis de uma medida por registro não controlam confundimento nem identidade. | Célula 19. | Rótulo do gráfico pode induzir leitura causal. |

Claims proibidos a partir deste notebook: “o modelo funciona”, “follower_count gera engajamento”, “SHAP identifica alavancas”, “patrocínio não funciona”, “porte controla patrocínio”, “horário ideal”, “perfil de audiência vencedor” ou qualquer mudança de verba.

## Gaps críticos

1. O notebook não contém resultados nem narrativa conclusiva.
2. O alvo é dominado por um denominador também oferecido ao modelo.
3. Há informação pós-publicação nas features.
4. O split usa uma entidade que a auditoria já provou instável.
5. O pipeline ignora simulação, incerteza, validade externa e semântica decisória.

## Correções obrigatórias antes de qualquer reaproveitamento analítico

- [ ] Definir decisão, momento da previsão, estimando e campos disponíveis nesse momento.
- [ ] Ajustar thresholds e todo pré-processamento somente no treino.
- [ ] Remover `comments_text` e qualquer variável pós-tratamento/pós-publicação.
- [ ] Eliminar o acoplamento entre denominador do alvo e features ou tratá-lo explicitamente em ablação/baseline.
- [ ] Substituir `creator_id` por chave estável validada; até lá, não alegar generalização por criador.
- [ ] Preservar outputs, versões, hashes, seeds, baseline e intervalos de incerteza.
- [ ] Tratar idiomas adequadamente e corrigir contagem de hashtags.
- [ ] Rotular SHAP como explicação preditiva, nunca causal.
- [ ] Manter qualquer modelo como exploração da fixture sintética, sem ação operacional.

## Registro de refutação — incorporado ao relatório por restrição de escopo

| Hipótese do notebook | Teste cético | Resultado | Status |
|---|---|---|---|
| Fusão texto + metadados aprende engajamento | Comparar alvo com seguidores isoladamente | −0,9790; quintil de seguidores reproduz 96,19% dos rótulos | Refutada como demonstração de valor incremental |
| Split é creator-level | Auditar cardinalidade de identidade | 100% dos IDs têm múltiplos nomes e plataformas | Refutada |
| Patrocínio difere na classe | Reproduzir média por grupo | 2,00010 vs. 1,99987 | Sem sinal material |
| Notebook demonstra performance | Inspecionar outputs e execução | Zero outputs; 20/20 contadores nulos | Não demonstrada |
| SHAP entrega explicação acionável | Verificar validade do alvo e temporalidade | Alvo acoplado + texto pós-publicação | Bloqueada |

## Próximo passo recomendado

Não alterar o checkpoint. Guardar este relatório como nota comparativa e, numa evolução futura separada, adicionar ao harness analítico um teste automático de acoplamento alvo–feature e uma especificação de experimento não linear com dados reais, chave estável e holdout temporal.

## Fontes e limites desta revisão

- Notebook/API: `notebook.ipynb` e `kaggle-api-response.json`; o JSON interno da API é igual ao notebook local.
- Dataset: `social_media_dataset.csv`, 52.214 × 27, hash idêntico ao checkpoint.
- Diagnóstico aprovado consultado em leitura: `source-checkpoint.zip::reports/dataset-audit.md`, `evidence/dataset-audit.json`, `evidence/decision-map.json`, `evidence/claim-evidence-map.json`, `evidence/experiment-contracts.json` e `docs/prototype-scope.md`.
- Os cálculos adicionais deste relatório são reproduções independentes em leitura do CSV, não outputs preservados pelo notebook e não constituem nova revisão autoritativa do checkpoint.
