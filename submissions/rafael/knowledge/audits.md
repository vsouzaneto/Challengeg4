# Auditorias (compliance, fit, mercado, duração, poder) — achados e como usar

Fonte: `solution/src/social_insights/audits.py` · notebook: `solution/notebooks/14_auditorias.ipynb` (build: `notebooks/build/build_14_auditorias.py`) · testes: `solution/tests/test_audits.py` · 2026-10-19 · 52.214 posts.
Origem: lacunas de `description-gaps.md`. São análises de **composição**: valem mesmo com engajamento = ruído.

## Achados
| # | Auditoria | Manchete | Números-chave |
|---|---|---|---|
| 1 | Disclosure | Quase metade dos patrocínios tem risco regulatório alto | 47,2% implícito (risco alto) · 17,2% explícito só no vídeo (médio) · 35,6% explícito no texto (baixo) · só 2,3% com #ad visível no texto, igual aos orgânicos (2,1%) → rótulo não auditável · tipo/local sem efeito no engajamento (q ≥ 0,25) |
| 2 | Fit patrocinador × nicho | 60% dos patrocínios estão fora do nicho do creator | 39,9% no nicho · mix uniforme (~16,7% por célula) · no mesmo estrato, fit não muda engajamento nem views (q = 0,99) |
| 3 | Coerência de mercado | Só 22% dos posts estão no idioma do mercado e numa plataforma disponível lá | 12,6% em plataforma bloqueada (YouTube/Instagram/TikTok na China, TikTok na Índia, Instagram na Rússia) · Brasil, Alemanha e Rússia: 0 posts no próprio idioma · coerentes = incoerentes (q = 0,93) |
| 4 | Duração por formato | O tamanho não importa, nem medido na unidade certa | 29,7% dos posts (imagem/misto) têm "duração" sem unidade · vídeo (s) e texto (palavras): \|ρ\| ≤ 0,018, MDE 0,016–0,039 · as crenças/bolsões com `length_bin` misturam unidades |
| 5 | Poder por subgrupo | Todo "sem efeito" é conclusivo para efeitos ≥ 5% | MDE máximo 0,32% (nano, n = 454, engajamento) · 0 comparações inconclusivas |

## Mensagens para o site
1. "Quase metade dos posts patrocinados não se identifica claramente como publicidade, e isso é risco legal em todos os mercados da base. Exigir #publi/#ad no texto não custa engajamento."
2. "O campo de disclosure da base não aparece no texto do post. Com os seus dados, a ferramenta verifica o rótulo no próprio post."
3. "6 em cada 10 patrocínios estão fora do nicho do creator (ex.: games em beleza)."
4. "Só 22% dos posts falam a língua da audiência numa rede que ela consegue abrir. Brasil, Alemanha e Rússia não têm conteúdo no idioma local."
5. "Duração só tem sentido em vídeo (segundos) e texto (palavras), e em nenhum dos dois ela muda o resultado."
6. "Nossos testes veriam diferenças de até 0,3%. Então, quando dizemos 'não há diferença', não é falta de dados."

**Gráficos sugeridos:** barras empilhadas de risco por mercado; tabela/heatmap nicho × patrocinador; barras de % coerente por mercado; dispersão n × MDE.

## Como utilizar
```python
import sys; sys.path.insert(0, "solution/src")
from social_insights import data, audits
df = data.load_posts()
a = audits.disclosure_audit(df)   # também: sponsor_fit, market_coherence, length_by_format, subgroup_power
a.verdict; a.evidence; a.details  # frase executiva, tabela principal, tabelas de apoio
audits.audit_all(df)              # as 5
audits.disclosure_risk(df); audits.has_ad_marker(df); audits.sponsor_fits(df); audits.market_coherence_flags(df)  # por post
```
- **Regras editáveis:** `AD_RULES`, `RISK_LEVELS`, `AD_MARKERS`, `SPONSOR_FIT`, `MARKET_LANGUAGES`, `UNAVAILABLE_PLATFORMS`, `LENGTH_BINS_BY_FORMAT`, `RELEVANT_EFFECT` (5%). Elas vêm do conhecimento de mercado, não são parecer jurídico.
- **Qualidade:** `test_audits.py` verifica as regras por post e que cada auditoria fica quieta no ruído e detecta efeitos plantados (custo do disclosure implícito, uplift no nicho, coerência, duração do vídeo, grupos pequenos inconclusivos).

## Premissa sobre datas
`post_date` não tem fuso. **Assume-se horário normalizado** (o mesmo relógio para todos os mercados). A aplicação deve mostrar um aviso onde houver horário.
