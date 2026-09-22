---
status: passing
canonical: true
area: marketing
created: 2026-09-21
last_updated: 2026-09-21
---

# SPEC-004 Estratégia Social Media (`marketing-004-social`)

## Comportamento visível

O candidato atua como AI Master de Marketing. Há ~52K posts (orgânico + patrocinado) em Instagram, TikTok, YouTube (e outras plataformas do dataset). O Head de Marketing quer: o que gera engagement de verdade, se patrocinar vale, e uma **estratégia** — não opinião. Ferramenta de acompanhamento é diferencial.

Persona da saída: Head de Marketing (5 minutos para entender).

## Contrato

### Entrada

Um dataset cross-platform em [DATA-SOURCES.md](../architecture/DATA-SOURCES.md). Flag `is_sponsored` é o gancho de ROI. Volume declarado: ~52.000.

### Obrigatório — análise

Com dados, não achismo:

1. O que gera engagement — por plataforma, tipo, categoria, tamanho de creator. Além de “vídeo > imagem”.
2. Patrocínio funciona? Orgânico vs patrocinado em engagement, alcance, custo implícito; **em que condições** e com que perfil.
3. Perfil de audiência que mais engaja (plataforma × tipo × categoria).
4. O que **não** funciona.

Comparação orgânico vs patrocinado precisa **controlar** tamanho de creator, plataforma e categoria (critério do brief).

### Obrigatório — estratégia

1. Onde concentrar (plataforma, tipo, frequência, faixa de creator).
2. Política de patrocínio (sim/não, condições, threshold de followers/engagement).
3. O que parar.
4. Quick wins desta semana.

Recomendações **priorizadas** — não lista de 20 ideias.

### Diferencial

Modelo de engagement; dashboard; gerador de recomendações; hashtags; clustering de audiência; qualquer loop dado → decisão recorrente.

### Process log

Obrigatório.

## Critérios de qualidade (aceitação)

| # | Critério | Fora |
|---|----------|------|
| Q1 | Análise além da tabela 1 (média por plataforma) | “TikTok engaja mais” como conclusão |
| Q2 | Insights acionáveis na segunda | Framework genérico de conteúdo |
| Q3 | Orgânico vs ads com controle | Comparar médias cruas |
| Q4 | Recomendações priorizadas | Brain dump |
| Q5 | Executivo entende | Relatório só de p-value |

Cuidado declarado no brief: engagement rate isolado mente; survivorship (posts com zero engagement).

## Verificação

- [ ] README ainda pede análise + estratégia + process log.
- [ ] Submissão segmenta (plataforma / período / categoria) antes de concluir.
- [ ] “Postar mais no TikTok” (se aparecer) traz o quê / para quem / quando / evidência.
- [ ] Process log presente.

## Evidência

2026-09-21: `challenges/marketing-004-social/README.md` (Marketing; Análise + Estratégia; 4–6 h).

## Notas

Plataformas Bilibili e RedNote estão no brief. Ignorá-las sem dizer por quê é buraco analítico, não simplificação automática.

Disco 2026-09-21: 52 214 × **27** colunas. Sem `engagement_rate` (derivar). Audience é bucket, não JSON. `creator_name` ≠ 1:1 com `creator_id`. Métricas quase constantes (eng ≈ 0,199). ERD: [erd/marketing-004-social.md](../erd/marketing-004-social.md).

Lab Databricks (mesmo contrato de colunas): [notebook-marketing-004-social](../../notebook-marketing-004-social/README.md) — ingestão Lab 01, Assistant Lab 02, **entregável Lab 03**, análise Lab 04. Spec do pacote: [SPEC-012-lab-004-databricks.md](SPEC-012-lab-004-databricks.md). Entregável: [SPEC-014](SPEC-014-lab-03-entregaveis.md).

## Sucesso / falha

- Sucesso: “Vídeo 30–60s, categoria Tech, creators 10K–50K, 3,2× shares vs média da plataforma; patrocínio só acima de threshold T após controle; parar formato F na plataforma P.”
- Falha: “Vídeos performam melhor que imagens; postem mais.”

## Migração e compatibilidade

`is_sponsored` + volume ~52K + recorte cross-platform são invariantes. Trocar dataset = bump desta spec + DATA-SOURCES + ERD.
