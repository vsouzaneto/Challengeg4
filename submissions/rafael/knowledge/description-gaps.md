# Descrição do Kaggle × dados × entrega — lacunas e resultados enganosos

Script: `process-log/probe_description_gaps.py` · saída: `process-log/probe_description_gaps_output.txt` · 2026-10-19.

## Resultados enganosos (corrigir)
| # | Onde | Problema | Evidência |
|---|---|---|---|
| E1 | "Disclosure explícito: sem perda de engajamento e sem risco regulatório" (estratégia, quick win 3) | Os rótulos de disclosure não aparecem no conteúdo. A comparação é só explícito × implícito, e os dois rótulos são aleatórios. Não dá para concluir nada sobre compliance | Posts com disclosure "em hashtags" têm #ad/#sponsored em 0,23% dos casos, igual aos orgânicos (0,21%) |
| E2 | Descrição: patrocinado pode ter disclosure `none` | 0 patrocinados com `none`. A análise de "patrocínio oculto", que é o maior risco de transparência, não é possível | 11.784 explícitos · 10.530 implícitos · 0 none |
| E3 | "Conteúdo curto (<60) engaja mais"; bolsões "duração 180–360 s"; `LENGTH_BINS` | `content_length` é segundos (vídeo) **ou** palavras (texto), e as faixas misturam as duas unidades. Imagem também tem "duração" | Mesma distribuição 10–599 nos 4 formatos (mediana 173–175) |
| E4 | Insights de horário | **Decisão (2026-10-19): assumir horário normalizado.** `post_date` não tem fuso; manter só um aviso na aplicação | `5/29/23 12:15 AM` |
| E5 | "Hoje só 1% dos patrocinados está abaixo do teto"; perfil "nano" | Isso descreve o gerador (seguidores ~ Uniforme(0, 1M)), não um portfólio real: 90% dos posts são macro/mega. (O poder em nano é suficiente: MDE 0,32%, ver `audits.md`) | nano 0,9% · mega 49,9% |
| E6 | Teto de 10.050 seguidores | Além de vir das premissas de custo, usa 20% de engajamento por view, uma taxa irreal (o mercado fica em 1–6%). Com taxa real, o teto cai ainda mais | 2.010 interações / 10.100 views |
| E7 | "Concentrar em 1–2 plataformas onde está o cliente-alvo" | A audiência por plataforma é uniforme (Bilibili/RedNote com 12% de público EUA/Brasil), e o idioma é independente do país. O dataset não responde a essa pergunta | ~12,5% em cada célula |
| E8 | Sentimento de comentários | `comments_text` tem de 0 a 5 frases Faker, e `comments_count` ≥ 140. A amostra não representa os comentários | mín. de comments_count = 140 |

## Análises que faltavam → feitas em `audits.md` (exceto o item 5, descartado pela premissa de horário normalizado)
1. **Auditoria de disclosure por regime regulatório** (`audience_location`: FTC/EUA, ASA/UK, Alemanha, ASCI/Índia). É composição, não depende de efeito em engajamento: 47% dos patrocinados são implícitos e 33% divulgam só no vídeo. Junto, uma regra de validação: o rótulo precisa ser verificável no texto (#ad).
2. **Fit patrocinador × nicho** (`sponsor_category` × `content_category`). Aqui é uniforme (~1/6), e 60% dos patrocínios ficam fora do nicho (mapa em `SPONSOR_FIT`). Com dados reais, é um critério de seleção de creator.
3. **Coerência idioma × país da audiência × plataforma** como checagem de qualidade/segmentação para dados reais.
4. **Análise de duração por formato e com a unidade certa** (segundos só para vídeo, palavras só para texto).
5. **Hora local da audiência** (converter `post_date` pelo fuso de `audience_location`) antes de qualquer recomendação de horário.
6. **MDE por subgrupo** (principalmente nano e formatos pequenos) ao lado de cada "equivalente".
