# Crítica da entrega — Challenge 004 (Social Media)

Revisão feita em 2026-10-19 contra `challenges/marketing-004-social/README.md`, `submission-guide.md`, `templates/submission-template.md` e `instructions/*.md`.
Estado revisado: branch `submission/rafael` @ `8d7597e`, com 3 notebooks modificados e o site (`solution/site/`, `site_export.py`) fora do git.

## Veredito

**O rigor técnico é alto; como entrega, ainda não está pronta.** A análise está correta, foi verificada e é reproduzível, e está bem acima do baseline de LLM. Mas faltam dois itens obrigatórios (README no formato do template e um process log narrativo). O executivo também não consegue tirar a decisão em 5 minutos. E parte das recomendações "para esta semana" (teto de 10 mil seguidores, texto como formato padrão, "evitar US$ 109 mi") sai das **premissas de custo**, não dos dados. Se o Head de Marketing aplicar isso no mundo real, pode sair caro.

| Critério | Status | Resumo |
|---|---|---|
| Análise de performance (obrigatório) | ✅ atende | 4 perguntas respondidas com teste, tamanho de efeito, FDR e MDE |
| Estratégia (obrigatório) | ⚠️ parcial | Existe, mas depende de premissas e se contradiz com os bolsões |
| Diferencial | ⚠️ parcial | 4 CLIs + site; os CLIs devolvem a média e o site está quebrado |
| Process log (obrigatório) | ❌ insuficiente | Só git + DEVELOPMENT_PROCESS; falta narrativa e evidência de IA |
| README no template | ❌ ausente | Não existe `submissions/rafael/README.md` |
| Reprodutibilidade | ✅ boa, com lacunas | Testes e relatório reproduzem; faltam download, comando único e commit limpo |
| Veracidade dos números | ✅ confirmada | 14 de 15 números batem num recálculo independente (abaixo) |
| Comparação orgânico × patrocinado justa | ✅ atende | 269 estratos + regressão com controles |
| Priorização | ❌ fraca | Dezenas de itens sem uma ordem única |
| Comunicação executiva (5 min) | ❌ não atende | `docs/respostas.md` tem tabelas cruas (p, ε², `nan`, `1.01e+04`) |
| ROI / valor para o time | ⚠️ parcial | O ROI em US$ é um artefato das premissas e falta ROI da própria entrega |

---

## 1. Veracidade — recálculo independente

O script abaixo lê o CSV bruto sem importar o pacote da submissão (`verify.py` e `verify2.py` no scratchpad da revisão; a lógica está resumida aqui).
CSV usado: 52.214 linhas, 23.290.049 bytes, sha256 `693a2df6e609d1c099f3430d9a5b894b224fe12b2420c0d93e6defe90d15f18e`.

| Afirmação na entrega | Recalculado | Status |
|---|---|---|
| 52.214 posts, 27 colunas | 52.214 × 27 | ✅ |
| Views ~10.100, desvio 100, variância/média 0,99 (Poisson) | 10.100,3 · 100,0 · 0,991 | ✅ |
| Likes/shares/comments Poisson (var/média ≈ 1) | 1,003 · 0,999 · 0,993 | ✅ |
| ρ seguidores × views = 0,005 (p = 0,29) | 0,0046 (p = 0,290) | ✅ |
| Seguidores ~ Uniforme(0, 1M), KS p = 0,87 | KS p = 0,865 | ✅ |
| Kruskal engajamento: plataforma 0,362 · formato 0,223 · categoria 0,288 · patrocínio 0,879 | idênticos | ✅ |
| Engajamento médio 19,9% | 0,1991 | ✅ |
| Nenhum post com engajamento zero | mínimo 0,179; 0 posts com 0 likes | ✅ |
| 22.314 patrocinados; 22.122 acima de 10.050 seguidores; "só 1%" dentro | 22.314 · 22.122 · 0,86% | ✅ |
| Gasto implícito ~US$ 111,5 mi; excedente ~US$ 109,3 mi | 111,55 mi · 109,31 mi (diferença de 0,03% no método) | ✅ |
| Datas 2023-05-29 → 2025-05-28 | idem | ✅ |
| Treino até 2024-12-31 = 41.771 posts | 41.794 pelo meu corte (diferença de 23, provavelmente hora/fuso) | ≈ |
| Creator tem ~10 follower_counts | média 10,4 | ✅ |
| TikTok · beauty · espanhol: 451 posts, 10,0% no top 5% de likes | 451 · 9,98% (base observada 5,17%) | ✅ |
| "2,02x" nesse segmento | 1,93x sobre a taxa observada; ~2,0x sobre 5% nominal | ⚠️ explicitar a base |

**Conclusão:** nenhum número inventado. A regra "todo número vem de código" (GENERAL.md) foi cumprida. O problema não está nos números, e sim no que se conclui deles (seções 3 e 4).

## 2. Reprodutibilidade

**O que funciona (verificado):**
- `pytest`: **57 passed em 25 s**. Os testes usam efeitos plantados, ou seja, verificam que o método detecta sinal quando ele existe.
- `answer_questions.py` regenera `docs/respostas.md` **idêntico** (diff vazio) em 9 s.
- `requirements.txt` com versões fixadas, seeds fixas, pacote `social_insights` separado dos notebooks, que são gerados por scripts em `notebooks/build/`.

**Lacunas:**
| # | Problema | Impacto | Correção |
|---|---|---|---|
| R1 | Nenhum script de download do dataset (exige login no Kaggle) e nenhum checksum | O avaliador não sabe se usou o mesmo arquivo | `scripts/get_data.sh` com Kaggle API + sha256 acima no README |
| R2 | Nenhum comando único para "rodar tudo" (CODE.md exige) | Notebooks, relatório, modelos e site rodam em passos separados | `make all` ou `run_all.sh`: dados → testes → relatório → notebooks → site |
| R3 | Python 3.14 obrigatório (os pins só compilam no 3.14, ver `knowledge/environment.md`) e isso não está documentado no setup | O setup falha em 3.11/3.12, que é o padrão de muita gente | Declarar a versão no README e, se possível, oferecer pins compatíveis com 3.11+ |
| R4 | `solution/site/build_site.py` lê `template.html`, que **não existe**; `site_export.py` e o site estão fora do git (o `.gitignore` raiz ignora `submissions/`) | Diferencial quebrado; se o commit for parcial, o PR fica com código morto | Terminar e commitar com `git add -f` arquivo a arquivo, ou remover |
| R5 | 3 notebooks modificados sem commit (−51 linhas) | Estado do PR ≠ estado revisado | Reexecutar `build_*.py`, conferir e commitar |
| R6 | Lixo local: `catboost_info/` (2 lugares), `.ipynb_checkpoints/` com cópia de 23 MB do CSV | Risco de entrar no PR com `git add -f <pasta>` | Adicionar ao `.gitignore` local e apagar |
| R7 | Modelos (`solution/models/`) não versionados; o 1º uso dos CLIs treina (25–75 s) | Ok, mas surpreende | Avisar no README |

Os 12 notebooks não foram reexecutados nesta revisão.

## 3. Requisitos do desafio, item a item

### 3.1 Análise de performance ✅
- **O que gera engajamento:** cobre plataforma, formato, categoria, porte e combinações (450 segmentos, FDR, MDE). Supera o baseline: é exatamente o que um LLM erra ao chamar 0,07% de "insight".
- **Patrocínio funciona:** a comparação é justa (estratificação em 269 estratos + regressão), com custo implícito, condições e tipo de influenciador. Atende ao critério "a comparação é justa?".
- **Audiência:** 36 testes por plataforma, formato e categoria, mais personas. ✅
- **O que não funciona:** 11 crenças testadas. Bom formato executivo.
- **Survivorship bias:** tratado (não há posts com engajamento zero nem cauda longa). ✅
- **Lacuna:** o brief diz que a empresa investe em **Instagram, TikTok e YouTube**. A análise trata Bilibili e RedNote com o mesmo peso. Recomendo dar destaque às 3 plataformas do brief e citar as outras 2 só como dado do dataset.

### 3.2 Estratégia ⚠️
| Item pedido | O que foi entregue | Problema |
|---|---|---|
| Onde concentrar (plataforma, formato, frequência, faixa de creator) | "Nenhuma vence → escolha pelo custo"; formato = **texto**; creator = **nano**; frequência = capacidade | "Texto" vem só do custo **assumido** (US$ 50 vs. 300). Recomendar texto como padrão no TikTok/YouTube não faz sentido operacional. A frequência mede o volume diário do dataset inteiro (~14 posts/dia de 5 mil creators), não a cadência de uma marca |
| Política de patrocínio + threshold | Teto de **10.050 seguidores**; contratos por CPM/CPE; grupo de controle | O threshold é uma **identidade das premissas**: CPE-alvo × interações médias ÷ custo por seguidor = 0,05 × 2.010 ÷ 0,01 = 10.050. Ele não vem de um efeito observado, e sim da premissa de US$ 10/mil seguidores somada a views planas. Com dados reais (views crescem com seguidores), o teto muda ou some |
| O que parar | Patrocínio acima do teto (~US$ 109 mi), formatos caros (~US$ 8,9 mi), 11 rotinas | Os valores em US$ são premissa × 22 mil posts de 5 mil creators fictícios. **Não é o gasto da empresa.** Na tabela de quick wins aparecem como "evita ~US$ 109.335.722", com precisão de dólar |
| Quick wins | 6 ações com esforço, impacto e dono | Bom formato. Mas os itens 1, 2 e 4 aplicam as conclusões "dependentes de premissa" no mundo real nesta semana |

**Contradições internas (alta prioridade):**
1. Estratégia: "retirar 'melhor horário' do checklist" (horário sem efeito). Bolsões: "postar antes do meio-dia no YouTube para comentários" (replicado).
2. Tese central: "o dataset é ruído Poisson; qualquer insight é falso". Bolsões: "**priorizar** beauty em espanhol no TikTok".
3. Notebook 09: janelas escolhidas depois de ver o gráfico são hipótese. Notebooks 10/11: 13 + 24 bolsões "replicados" viram fila de A/B. A taxa de replicação fica no nível do acaso (3–8% vs. ~5% esperado), o que a própria entrega reconhece.

O executivo recebe as duas mensagens e não sabe qual vale.

**Sobre TikTok · beauty · espanhol:** o número é real (45 hits em 451 posts, binomial p ≈ 4e-5, q global 0,035). Ainda assim, deve ser apresentado como hipótese, não como prioridade:
- não aparece nas outras plataformas (4,5–5,5%) nem nas outras métricas do TikTok (views 4,7%, shares 4,4%);
- a média sobe só 0,4%. Um deslocamento desse tamanho explicaria ~6,5% de hits, não 10%. O que sobra vem de uma variância um pouco maior (desvio 42,6 vs. 38,9; Levene p = 0,045);
- num gerador declaradamente aleatório, 1 descoberta em 14,7 mil testes é a hipótese que exige mais prova.
→ Rebaixar para "teste A/B nº 1", com critério de sucesso definido.

### 3.3 Diferencial ⚠️
- **A favor:** previsores honestos (adotam modelo só se ele bate o baseline, com correção), controle positivo, validação temporal, histórico do creator sem vazamento. É acima do que um LLM entrega.
- **Contra (visão do time de marketing):**
  - Com estes dados, os 3 previsores devolvem sempre **10.100 views / 19,9% / 5%**. O uso diário hoje é zero; o valor é **potencial**, condicionado a dados reais.
  - São CLIs Python. O time de social media não roda `.venv/bin/python predict_hit.py --platform ...`. O dashboard/site, que resolveria isso, está quebrado (R4).
  - "Rodar com dados reais" pede o esquema do Kaggle. Exportações reais (Meta Business Suite, TikTok Studio, YouTube Studio) não trazem `is_sponsored`, `audience_*` nem `disclosure_type` por post nesse formato. Falta um **mapeamento de colunas** das exportações reais para o esquema, e a indicação de quais colunas são opcionais.

### 3.4 Process log ❌ (risco de desclassificação)
O guia exige: ferramentas e por quê, decomposição antes do prompt, **onde a IA errou e como você corrigiu**, o que o humano adicionou, nº de iterações.

| Exigência | Onde está hoje | Lacuna |
|---|---|---|
| Ferramentas | Implícito (Claude Code) | Nenhuma tabela de ferramentas |
| Decomposição | `instructions/`, `action-plan.md` | Bom material, mas espalhado |
| Erros da IA | Implícitos em DEVELOPMENT_PROCESS (Hopkins falso positivo, R² de treino, p cru, contagem de picos × taxa) | Não estão apresentados como "a IA sugeriu X, eu percebi Y, corrigi com Z" |
| Contribuição humana | Pedidos do usuário citados ("pedido do usuário") | Não há uma seção explícita |
| Evidências | 21 commits + `probe_eda.py` | Sem export de chat ou screenshots; `process-log/` só tem o probe |

Os commits vão das 17:47 de 18/10 às 00:54 de 19/10 (~7 h), fora o site. Isso passa um pouco do budget de 4–6 h, o que não é penalidade, mas reforça a necessidade de priorizar.

### 3.5 README / template ❌
Falta `submissions/rafael/README.md` com: sobre mim, executive summary (3–5 frases), abordagem, resultados, recomendações priorizadas, limitações, process log e evidências. Sem esse arquivo, o avaliador não encontra a porta de entrada da entrega.

## 4. Clareza e valor para o time de marketing

**Teste dos 5 minutos — falha hoje:**
- `docs/respostas.md` (332 linhas) mistura tabelas de pandas cruas: coluna de índice, `p_value`, `q_value`, `epsilon²`, `nan`, `1.01e+04`, `1.115e+08` e nomes em inglês (`eng_rate_views`, `follower_tier`).
- Formato numérico misturado: "10,050 seguidores" (padrão EN) ao lado de "US$ 0,05" (padrão pt-BR).
- Seções e tabelas repetidas (a tabela de crenças aparece 2 vezes; a de patrocínio também).
- A entrega soma 16 arquivos em `knowledge/`, 12 notebooks, 4 CLIs, 6 quick wins, 11 mitos, 13 + 24 hipóteses de A/B. É o caso "40 páginas onde 5 resolveriam" do guia.

**Mensagem que o Head de Marketing deveria levar (proposta):**
> "Estes dados não mostram nada que melhore engajamento ou alcance, nem plataforma, formato, creator, horário ou patrocínio. Testamos tudo com rigor e o método detecta efeitos de 2–5% quando eles existem. Então, nesta semana: (1) pare de pagar por seguidores e passe a pagar por resultado (CPM/CPE); (2) todo patrocínio novo entra com grupo de controle; (3) me passe os custos reais e as exportações das 3 plataformas, e em 2 semanas a mesma ferramenta responde com os seus dados."

**Valor real hoje, separado por robustez:**
| Vale mesmo com dados reais (robusto) | Depende das premissas/dataset (não aplicar ainda) |
|---|---|
| Pagar por resultado (CPM/CPE), não por post ou por seguidor | Teto de 10.050 seguidores |
| Grupo de controle em todo patrocínio | Texto como formato padrão |
| Corrigir para múltiplos testes antes de chamar algo de "insight" | "Evitar US$ 109 mi" / "economia de US$ 8,9 mi" |
| Disclosure explícito (custo zero de engajamento aqui + compliance) | Retirar horário do checklist (contradito no YouTube) |
| Pipeline/previsores que adotam modelo só quando ele bate a média | Priorizar beauty em espanhol no TikTok |

## 5. ROI

- **Problema:** o único "ROI" apresentado (US$ 109 mi + 8,9 mi) é premissa × volume do dataset, e o próprio `strategy-recommendations.md` alerta que não é valor contábil. Mesmo assim, ele aparece como impacto na tabela de quick wins.
- **Falta o ROI da entrega:** quanto custa adotar (horas para plugar os dados, rodar o A/B), quais decisões ela muda e qual o ganho esperado em cenários.
- **Proposta:**
  1. Trocar US$ absolutos por **fórmula + sensibilidade**: "a cada US$ 1 pago acima do CPM-alvo, X; com custo por seguidor entre US$ 5 e 20/mil, o teto fica entre A e B". O código já parametriza isso (`break_even`).
  2. ROI do A/B de patrocínio: com o MDE calculado pelo próprio `focus.mde_two_groups`, informar quantos posts pareados são necessários para detectar +5% de uplift. Assim a empresa sabe o custo do experimento antes de rodar.
  3. Métricas de sucesso em 30/60/90 dias: % de contratos por CPM/CPE, % de patrocínios com controle, CPM efetivo vs. alvo.

## 6. Plano de correção priorizado

| P | Ação | Por quê | Esforço |
|---|---|---|---|
| **P0** | Criar `README.md` no template, com executive summary de 5 frases e as 3 decisões da seção 4 | Obrigatório; porta de entrada | 1 h |
| **P0** | Process log narrativo em `process-log/README.md`: ferramentas, decomposição, **5–6 erros da IA com correção** (Hopkins, R² de treino/SHAP vs. alvo embaralhado, p cru → FDR, contagem de picos → taxa, razão por seguidor espúria, janela a posteriori), contribuição humana, iterações; anexar export/screenshots do chat | Sem isso = desclassificado | 1–2 h |
| **P0** | Resolver o site (terminar `template.html` + commit, ou remover `build_site.py`/`site_export.py`); commitar notebooks; limpar `catboost_info` e checkpoints | PR consistente | 0,5–2 h |
| **P1** | Reescrever quick wins em 2 colunas (robusto × dependente de premissa); tirar US$ 109 mi da manchete; mostrar o threshold como fórmula + sensibilidade | Evita decisão errada no mundo real | 1 h |
| **P1** | Uma página executiva (`docs/resumo-executivo.md`) com tabelas humanizadas (sem p/ε²/`nan`, números pt-BR, sem repetição); `respostas.md` vira anexo técnico | Teste dos 5 minutos | 1 h |
| **P1** | Resolver contradições: uma lista única de hipóteses de A/B (no máx. 3, com critério de sucesso e tamanho de amostra); TikTok espanhol = hipótese nº 1, não prioridade | Priorização | 0,5 h |
| **P2** | `get_data.sh` + sha256, `make all`, versão do Python no README | Reprodutibilidade | 0,5 h |
| **P2** | Mapeamento das exportações reais (Meta/TikTok/YouTube) → esquema, com colunas obrigatórias/opcionais | Ferramenta usável de verdade | 1 h |
| **P2** | Seção de ROI (seção 5) | Valor para a empresa | 0,5 h |

## Pontos fortes a preservar
- Diagnóstico de dados sintéticos logo no início, que virou a tese da entrega. É o principal diferencial contra o baseline.
- FDR em toda bateria de testes, com correção global entre plataformas.
- Controle positivo em todas as frentes: prova que "sem efeito" não é falta de poder.
- MDE: transforma "não achei" em "não existe, e eu veria se existisse".
- Previsores que se recusam a prometer o que os dados não sustentam.
- Código testado (57 testes), relatório determinístico, decisões registradas com alternativa descartada.

---

## 7. Status das correções (2026-10-19, tarde)

Entre a revisão e esta rodada, a entrega ganhou um app web (`solution/src/social_web`), auditorias (`audits.md`) e análise de creators (`creators.md`). Com isso, os itens R4 (site quebrado) e E1 (disclosure) foram resolvidos em outra sessão. Nesta rodada:

| Item da crítica | O que mudou | Onde |
|---|---|---|
| Contradição "dataset é ruído" × "priorizar TikTok · beauty · espanhol" | Virou hipótese nº 1 da **fila de testes**: "testar antes de mudar o mix", com ~1.430 posts por grupo e as ressalvas (não aparece em outras plataformas/métricas) | `strategy.test_queue`, Início, Descobertas, `pockets-by-platform.md` |
| Contradição "tirar horário do checklist" × "postar cedo no YouTube" | Regra geral mantida (sem melhor horário). O YouTube entra como "top 1% de comentários, média igual"; A/B inviável (~17 mil posts por grupo), então vira desempate de agenda e acompanhamento | idem + `pockets-and-top1.md` |
| Teto de 10.050 seguidores apresentado como dado | Ação principal virou "pagar por resultado" (robusta). O teto ficou como regra provisória com **tabela de sensibilidade** (1.000–40.400 seguidores conforme preço e CPM-alvo) | `strategy.threshold_sensitivity`, Estratégia |
| "Evita US$ 109 mi" nos quick wins | Impacto em % ("98% do gasto implícito é excedente, pelas premissas"); US$ só como ordem de grandeza ilustrativa | `strategy.stop_doing`, `quick_wins` |
| "Texto como formato padrão" | "Nenhum formato engaja mais; usar o mais barato que a plataforma comporta, pelo custo real" (depende de premissa) | `where_to_focus` |
| Quick wins sem distinção de robustez | Coluna **Base**: 4 robustas primeiro, 2 dependentes de premissa depois | `quick_wins`, Estratégia |
| Insight novo e verdadeiro | **~134x** a mais por mil views no creator mega vs. nano **independe do valor do cachê** (só exige cachê proporcional aos seguidores), o que torna essa a base mais confiável da política de patrocínio | `strategy.tier_cost_ratio` |
| Frequência "14 posts/dia" lida como cadência da marca | Explicitado: soma de todos os creators da base | `where_to_focus` |

Verificação: `pytest` com 116 passed (+5 testes novos em `test_strategy.py`); `docs/respostas.md` regenerado (agora com a seção 5, Fila de testes); payload do site regenerado em `solution/models/site_payload.json` e as 8 páginas renderizam (200) com os dados reais.

**Material de entrega (2026-10-19, noite):**
- README no template, com executive summary, recomendações priorizadas, limitações, process log e "como rodar" → `README.md`.
- Process log narrativo (ferramentas, decomposição, 16 iterações, 10 erros da IA com correção, contribuição humana) → `process-log/README.md`. Os prompts de todas as sessões estão em `process-log/prompts.md` e as conversas exportadas em `evidencias/`.
- Resumo executivo de 1 página → `docs/resumo-executivo.md`.
- Reprodutibilidade: `scripts/get_data.sh` (Kaggle + sha256, testado) e `Makefile`; `catboost_info/` no `.gitignore`.

**Ainda em aberto:** PR e uma seção de ROI quantitativa da própria entrega.
