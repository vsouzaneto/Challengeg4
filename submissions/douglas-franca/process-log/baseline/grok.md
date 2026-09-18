# Baseline — Grok

| Campo | Valor |
|---|---|
| Data | 2026-09-16 |
| Operado por | Douglas França (conversa nova, sem contexto da submissão) |
| Entrada | Brief do Challenge 004 colado como texto, sem contexto (prints `g1-grok-01` a `03`). "Trabalhou por 6m 6s" e citou 35 fontes |
| Recebeu os dados? | A própria IA baixou o dataset via kagglehub em ambiente próprio |
| Checagem numérica | `outputs/tables/g1-baseline-claims-check.csv` |

## Resposta literal

~~~~text
Análise e Estratégia concluídas. Entreguei tudo o que o Head de Marketing pediu, com base nos ~52.214 posts do dataset real (Kaggle, licença MIT).
Arquivos gerados
Tudo em /home/workdir/artifacts/challenge004/:

























ArquivoConteúdoESTRATEGIA_SOCIAL_MEDIA.mdRelatório completo (análise + estratégia + recomendações priorizadas)dashboard_social_media.htmlDashboard interativo/estático para o time acompanhar no dia a diaprocess_log.mdLog de como a IA foi usada (obrigatório)summaries.json + model_info.jsonTabelas e resultados do modelo preditivo

Principais Findings (baseados em dados, não opinião)
1. Engagement rate é extremamente estável (~19,91% sobre views)

Diferenças entre plataformas, content type, categoria e patrocínio são estatisticamente insignificantes (ANOVA e t-tests com p > 0.20). O “o que gera engajamento” clássico quase não existe neste dataset.
2. A alavancagem real está no tamanho do creator






























TierEng Rate / FollowersRecomendaçãoNano (<10K)51,7%P0 — PriorizarMicro (10-50K)8,1%P0 — PriorizarMid (50-100K)2,8%SeletivoMacro / Mega0,81% → 0,28%Só para awareness
Nano/Micro entregam 10–180x mais engajamento relativo.
3. Patrocínio não queima (nem melhora significativamente) o engajamento

Orgânico 19,906% vs Patrocinado 19,905% (p = 0,80).

Vale a pena patrocinar especialmente Nano/Micro com bom fit de audiência e disclosure explicit. Categorias de sponsor com leve vantagem: Cosmetics e Food.
4. O que NÃO funciona

Pagar premium só por número de seguidores (Mega tem eng_rate_f baixíssimo)
Esperar “fórmula mágica” de tipo de post ou plataforma
Assumir que patrocínio destrói engajamento
Otimizar hashtags com base neste dataset (são ruído)

5. Modelo preditivo

Random Forest → R² ≈ –0.001. Confirma que o eng_rate é tão estável que quase nenhuma feature explica variação além do ruído. A decisão deve ser por seleção de creator + volume, não por “otimização de post”.

Estratégia recomendada (priorizada)
P0 (fazer esta semana)

Auditar os 100 creators com maior eng_rate_f e priorizar Nano/Micro
Manter patrocínio seletivo (não há evidência de prejuízo)
Criar scorecard simples: eng_rate_f + overlap demográfico + disclosure

P1

Aumentar proporção de Text + Mixed
Preferir sponsors Cosmetics/Food
Continuar volume em todas as 5 plataformas (diferenças irrelevantes)

P2

Observar UK/Brasil e faixa 50+ (leve edge)
Renegociar ou reduzir budget de Mega creators baseados só em followers

O relatório completo tem as tabelas, o dashboard HTML está pronto para o time usar, e o process log documenta todo o uso de IA (download via kagglehub, EDA, testes estatísticos, modelagem e síntese).
Quer que eu refine alguma parte, adicione visualizações extras ou transforme o dashboard em algo mais interativo (Streamlit etc.)?
~~~~
