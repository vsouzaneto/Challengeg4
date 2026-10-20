# solution/ — código da entrega

Tudo que roda está aqui. Os caminhos abaixo são relativos a `submissions/rafael/`, de onde os comandos devem ser executados. Como rodar (Docker ou venv) está no [README principal](../README.md#como-rodar).

## Fluxo

```
data/raw/*.csv ──► social_insights (análises e modelos) ──► social_web/state.py ──► solution/models/ (cache)
      ▲                    │                                        │
scripts/get_data.sh        ├──► cli/ (relatório e previsões)        └──► social_web/server.py (site + API)
 (sha256)                  └──► notebooks/ (análise passo a passo)
                                                    reproducibility/verify.py confere tudo contra reference.json
```

## Pastas

| Pasta | Papel | Entra na imagem Docker? |
|---|---|---|
| `src/social_insights/` | biblioteca de análise: carga e features, testes estatísticos, modelos, estratégia e auditorias | sim |
| `src/social_web/` | site FastAPI: páginas (Jinja2), painel Explorar, Simular post, API documentada em `/docs` | sim |
| `cli/` | linha de comando: `answer_questions.py` (relatório Markdown), `predict_engagement.py`, `predict_views.py`, `predict_hit.py` | sim |
| `scripts/` | `get_data.sh`: baixa o CSV do Kaggle e confere o sha256 | sim |
| `reproducibility/` | `verify.py` (checagem de reprodutibilidade) e `reference.json` (resultados de referência) | sim |
| `tests/` | pytest com efeitos plantados: cada método precisa achar o efeito plantado e ficar quieto no ruído | sim |
| `notebooks/` | 14 notebooks executados; `notebooks/build/` gera cada um a partir de Python | não |
| `models/` | modelos treinados e conteúdo do site (gerados por `social-web --build-only`, fora do git) | gerado no build |

## Módulos de `social_insights`

| Grupo | Módulos |
|---|---|
| Dados | `data` (CSV → features comuns), `cleaning` (qualidade; o que se sabe antes × depois de postar) |
| Perguntas e estratégia | `questions` (as 4 perguntas do desafio), `strategy` (onde focar, patrocínio, o que parar, quick wins), `audits` (disclosure, fit, mercado, duração, poder) |
| Exploração | `exploration`, `attribute_scan`, `focus`, `audience`, `top_performers`, `discovery` (bolsões), `creators`, `clustering`, `nlp` |
| Modelos | `engagement_model`, `views_forecast`, `hit_probability` (chance de top 5%), `modeling` e `drivers` (comparações e SHAP) |
| Método | `validation` (efeito plantado como controle positivo), `plots` (estilo dos gráficos) |
| Site | `site_export` (monta o conteúdo do site; todo número e frase vem das funções acima) |

## Reprodutibilidade

- **Fixado:** Python 3.14 (imagem `python:3.14.3-slim`), todos os pacotes na versão exata em `requirements.lock` (inclusive as dependências indiretas; `requirements.txt` lista só as diretas), `SEED = 42` em todo modelo, sha256 do CSV em `scripts/get_data.sh`.
- **Verificado:** `reproducibility/verify.py` compara o conteúdo inteiro do site e a resposta do simulador para 4 posts de teste com `reference.json`. Números aceitam diferença relativa de até 1e-6; textos têm de ser idênticos. O build Docker roda essa checagem e falha se algo divergir.
- **Mudou a análise de propósito?** Rode `python solution/reproducibility/verify.py --write-reference` e faça commit do novo `reference.json` junto com a mudança.
