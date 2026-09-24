# Auditoria do Dataset: Challenge 004

> Auditoria reproduzível dos bytes adquiridos do Kaggle. O objetivo é determinar quais decisões os dados autorizam e quais devem ser bloqueadas.

## Veredito executivo

**Status:** `SUITABLE_FOR_PROTOTYPE_NOT_FOR_BUSINESS_INFERENCE`

O dataset serve como fixture para demonstrar um sistema analítico, mas não valida uma estratégia real de social media. A fonte congelada o declara simulado, as entidades de creator são instáveis e as relações lineares marginais observadas são próximas de zero. Isso não prova independência geral e não substitui análise condicional nem dados reais.

## Proveniência congelada

- Commit do brief: `4aed364d572fabe0f1fff1f0c6f32960b30fe575`
- SHA-256 do brief: `1a8d1879d8e2ffed9a5cd51b524663da237b2fc4133892e27de9bff29c9c3f87`
- SHA-256 da metadata Kaggle: `9f8e2fd522d039c76f509f41e23cdf5ab5c85969c732e630ec130ada7e88e2fd`
- Versão Kaggle: 1
- Licença reportada: MIT
- Metadata declara simulação: True
- Brief menciona engagement rate: True

## Identidade e vínculo dos dados

- ZIP: `ce78ea3352fe1ae6093e6f5d48b506ad591c6e6ca90fbab6ac91866a8c34202e` (8047768 bytes)
- CSV: `693a2df6e609d1c099f3430d9a5b894b224fe12b2420c0d93e6defe90d15f18e` (23290049 bytes)
- ZIP: 1 membro, CRC válido=True, nome seguro=True
- Hash do membro igual ao CSV: True
- Expansão ZIP: 2,8940×, teto 100,0000×
- Linhas: 52214
- Colunas: 27
- Duplicatas exatas: 0
- Coluna `engagement_rate`: ausente

## Achados bloqueadores

### F-001 | critical-for-inference

O data card da fonte descreve explicitamente o dataset como simulado.

**Implicação:** Não apresentar os achados como performance observada do G4, verdade causal ou ROI de produção.

### F-002 | high

Todo creator_id está associado a múltiplos creator_name e a contagem de seguidores varia drasticamente dentro do mesmo creator_id.

**Implicação:** Bloquear análise longitudinal por creator e recomendações específicas de creators.

### F-003 | high

As correlações lineares marginais analisadas estão próximas de zero e os spreads de médias entre grupos são muito pequenos.

**Implicação:** Não interpretar isso como independência geral. Tratar rankings marginais como evidência insuficiente e investigar relações condicionais apenas como exploração da fixture sintética.

### F-004 | high

A comparação bruta e a comparação estratificada não detectam diferença média entre patrocinado e orgânico; os ICs ficam dentro de uma SESOI ilustrativa de ±0,5% da média orgânica.

**Implicação:** A SESOI precisa de validação de negócio. O resultado não autoriza causalidade, ROI ou política de patrocínio, mas autoriza registrar ausência de diferença detectável na fixture.

### F-005 | medium

O brief do repositório menciona engagement rate, mas o CSV não contém a coluna engagement_rate.

**Implicação:** Definir explicitamente qualquer métrica de engajamento derivada e não chamá-la de ROI financeiro.

### F-006 | medium

Milhares de valores de content_url são reutilizados entre creators diferentes.

**Implicação:** Não tratar content_url como identificador estável de post e não acessar as URLs geradas.

## Missingness e consistência

- Hashtags ausentes: 8743 (16,7446%)
- Texto de comentários ausente: 8688 (16,6392%)
- Inconsistências de disclosure: 0

## Integridade da entidade creator

- Creator IDs: 5000
- Creator IDs associados a múltiplos nomes: 5000
- Mediana de nomes distintos por creator ID: 10,0000
- Mediana da amplitude de seguidores dentro do mesmo creator ID: 842.331,5000
- URLs reutilizadas entre creators diferentes: 6074

Conclusão: `creator_id` não representa uma entidade estável. Análises longitudinais ou recomendações por creator ficam bloqueadas.

## Estrutura temporal

- Início: 2023-05-29T00:15:00
- Fim: 2025-05-28T11:08:00
- Ordenação monotônica: True
- Mediana do intervalo: 14,0000 minutos
- Intervalos de zero minuto: 1309

## Spreads entre grupos

| Dimensão | Métrica | Spread % da média | Eta² |
|---|---|---:|---:|
| platform | views | 0,0099% | 0,0000 |
| platform | likes | 0,0855% | 0,0001 |
| platform | shares | 0,1178% | 0,0001 |
| platform | comments_count | 0,1894% | 0,0001 |
| content_type | views | 0,0285% | 0,0001 |
| content_type | likes | 0,0416% | 0,0000 |
| content_type | shares | 0,1450% | 0,0001 |
| content_type | comments_count | 0,2055% | 0,0001 |
| content_category | views | 0,0154% | 0,0000 |
| content_category | likes | 0,0312% | 0,0000 |
| content_category | shares | 0,0552% | 0,0000 |
| content_category | comments_count | 0,0365% | 0,0000 |
| audience_location | views | 0,0291% | 0,0001 |
| audience_location | likes | 0,1090% | 0,0001 |
| audience_location | shares | 0,1193% | 0,0000 |
| audience_location | comments_count | 0,2146% | 0,0001 |

Spreads e Eta² pequenos indicam pouca separação marginal nesta fixture. Eles não provam ausência de relações não lineares ou interações.

## Patrocinado versus orgânico

Método do IC: aproximação normal com erro-padrão de Welch. SESOI ilustrativa: ±0,5% da média orgânica; deve ser validada pelo negócio antes de uso real.

| Métrica | N patrocinado | N orgânico | Diferença | IC 95% | Cohen d | Equivalente na SESOI? |
|---|---:|---:|---:|---:|---:|---:|
| views | 22314 | 29900 | 0,2882 | [-1,4495, 2,0260] | 0,0029 | True |
| likes | 22314 | 29900 | 0,0322 | [-0,6426, 0,7070] | 0,0008 | True |
| shares | 22314 | 29900 | -0,1306 | [-0,4305, 0,1693] | -0,0075 | True |
| comments_count | 22314 | 29900 | 0,0369 | [-0,2076, 0,2813] | 0,0026 | True |

## Patrocinado versus orgânico com ajuste

Método: stratified standardization by platform, content_category and follower_band. Estratos elegíveis: 75; linhas elegíveis: 52214.

| Métrica | Diferença ajustada | IC 95% | Equivalente na SESOI? |
|---|---:|---:|---:|
| views | 0,3180 | [-1,4216, 2,0576] | True |
| likes | 0,0209 | [-0,6548, 0,6966] | True |
| shares | -0,1260 | [-0,4263, 0,1743] | True |
| comments_count | 0,0361 | [-0,2085, 0,2807] | True |

Resultado descritivo da fixture: não foi detectada diferença média relevante sob a SESOI ilustrativa, inclusive após estratificação. Isso não autoriza inferência causal, ROI ou política de patrocínio.

## Relações lineares marginais

| Relação | Correlação de Pearson |
|---|---:|
| views × likes | 0,0008 |
| views × shares | -0,0074 |
| views × comments | -0,0050 |
| followers × views | 0,0050 |
| followers × likes | -0,0031 |
| content length × views | -0,0041 |

As correlações lineares marginais estão próximas de zero. O resultado não exclui dependência não linear, interações, confundimento ou efeitos condicionais.

## Decisões autorizadas

- Demonstrar um gate reproduzível de qualidade dos dados.
- Demonstrar análise descritiva controlada sobre a fixture do challenge.
- Gerar hipóteses e experimentos para validação com dados primários reais.
- Construir um protótipo explicável com confiança explícita e estados de bloqueio.

## Decisões bloqueadas

- Afirmar efeitos causais de patrocínio ou atributos de conteúdo.
- Afirmar ROI financeiro sem custo de campanha e receita atribuível.
- Recomendar creators específicos com base em entidades instáveis.
- Apresentar rankings sintéticos como verdade operacional do G4.

## Recomendação para a submissão

Manter o Challenge 004 em duas camadas: Data Trust Gate e análise exploratória claramente rotulada da fixture. A entrega deve mostrar o sistema funcionando, bloquear recomendações sem sustentação e propor coleta de dados reais e experimentos para responder patrocínio, conteúdo, creator e audiência.

## Reprodução

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/audit_dataset.py \
  --csv data/extracted/social_media_dataset.csv \
  --archive data/raw/social-media-sponsorship-and-engagement-dataset.zip \
  --challenge-brief evidence/sources/challenge-004-README.md \
  --dataset-metadata evidence/sources/kaggle-dataset-metadata.json \
  --json-output evidence/dataset-audit.json \
  --markdown-output reports/dataset-audit.md
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -v
```
