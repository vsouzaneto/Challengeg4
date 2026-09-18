# G1: baseline, o que a IA entrega sozinha

O README do challenge avisa que o G4 já rodou o brief em vários modelos e que "parecido com o baseline não é suficiente". Antes de construir qualquer coisa, colei o brief em 5 IAs, em conversas novas, e conferi com código cada número que elas afirmaram (`src/audit/verify_baseline_claims.py` → `outputs/tables/g1-baseline-claims-check.csv`).

## Resultado em uma tabela

| IA | Teve os dados? | Conclusão central | Números conferidos | Maior problema |
|---|---|---|---|---|
| **ChatGPT** | Não | Framework: benchmark por peer group, matching de patrocínio, modelo LightGBM + SHAP, "Social Intelligence Engine" | Nenhum número; hipóteses hipotéticas ("2,4× mais shares") | Proposta de ML/SHAP para um dado sem sinal (R² teste = −0,005). A hipótese "mais seguidores → mais views" não se sustenta (r = 0,006) |
| **DeepSeek** | Parcial (37%) | "Dataset sintético, sem sinal"; código genérico | Afirmou 7.109 linhas; são 52.214 | Raciocínio sobre um arquivo truncado; o raciocínio interno vazou na resposta |
| **Grok** | Sim | "Nano/micro entregam 10–180x mais engajamento relativo; priorize P0" | ER 19,91% ✅; p = 0,80 ✅; ER/followers nano 51,7% ✅ numericamente | **Artefato vendido como insight:** interações são ~constantes (~2.010), então dividir por seguidores gera 1/x por construção. Por view, todas as faixas ficam entre 19,90% e 19,91% |
| **Claude** | Sim | "Nenhum sinal estatístico; auditar a coleta; painel com teste de significância" | ANOVA plataforma p = 0,547 ✅; formato p = 0,206 ✅; categoria p = 0,439 ✅; patrocínio p = 0,804 ✅; r = −0,002 ✅; R² ≈ 0 ✅ | Período errado (disse 01/01–09/09/2024; é 29/05/2023–28/05/2025). Amplitude entre plataformas 10x maior que a real (0,10 vs 0,0105 p.p.). Estratégia para nas 5 plataformas; sem owners, sem processo, sem custo implícito |
| **Gemini** | **Não: inventou o dataset** | "TikTok + Tech/Health + 30–60s + micro = 3,2x shares; patrocínio −15% ER; realoque 70% da verba" | Categoria "Health" não existe; a célula citada tem n = 5 e 1,02x; patrocínio −0,005% (não −15%); não existe creator >1M | **Alucinação completa com acabamento profissional** (PDF + XLSX). Copiou o exemplo "3,2x" do próprio README como se fosse achado — e o próprio "Process Log" dele admite ter *injetado* a anomalia que depois apresenta como descoberta (`gemini.md`) |

> **Mesmo modelo, resultado diferente.** O baseline do Claude.ai rodou no **Claude Opus 5**, o mesmo modelo que orquestrou esta submissão no Claude Code. A distância entre as duas entregas não vem do modelo: vem do processo (gates, régua pré-registrada, checagem numérica) e das decisões humanas registradas em `../decisions.md`.

## O que isso muda na nossa estratégia

1. **"Não há sinal" já é baseline.** O Claude sozinho chegou a essa conclusão, com ANOVA e um painel de significância. Então a honestidade estatística (o que tornou o PR #91 excepcional) **é o piso, não o diferencial**.
2. **O risco real para o Head de Marketing é o baseline do Gemini e do Grok:** respostas bonitas e confiantes que mandariam realocar 70% da verba com base em números inventados ou em artefato matemático. Nossa entrega precisa **proteger a empresa desse tipo de decisão**, e não só evitá-la no nosso próprio relatório.
3. **Nenhuma IA:**
   - explicou *por que* não há sinal (o gerador é Poisson com λ fixo: variância/média = 0,99 a 1,00 nas quatro métricas);
   - distinguiu "não detectado" de "comprovadamente irrelevante" (equivalência/TOST, poder);
   - ligou as lacunas do dado a falhas da **operação** de marketing;
   - disse **quem** faz **o quê** na segunda-feira (RACI, owners);
   - calculou o **custo implícito** pedido no brief como função de break-even;
   - respondeu a **frequência de postagem** (cada creator tem 10–11 posts: não há variação para medir);
   - recortou a estratégia para os 3 canais que a empresa usa (Instagram, TikTok, YouTube).

Esses 7 pontos viram a rubrica em `docs/differentiation-rubric.md`.
