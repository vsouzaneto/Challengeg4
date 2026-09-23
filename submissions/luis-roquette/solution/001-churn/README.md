# RavenStack: diagnóstico reproduzível de churn

Pipeline Python 3.12 que cruza as cinco tabelas do Challenge 001, testa as alegações do CEO, avalia seis causas candidatas e publica relatório, dashboard e fila operacional a partir do mesmo conjunto canônico de artefatos.

## Resposta ao CEO

A fonte autoritativa é [ceo_answer.json](artifacts/ceo_answer.json), reproduzida no início do [relatório](artifacts/report.md) e do dashboard sem recalcular conclusões. Ela sempre responde na mesma ordem:

1. `what_changed`: evolução histórica do churn, denominador, unidade e incerteza;
2. `where`: recortes descritivos elegíveis, sem transformar concentração em causa;
3. `strongest_mechanism`: mecanismo sustentado, empate ou hipótese inconclusiva;
4. `unknowns`: cobertura, contradições e testes que os dados ainda não permitem fechar;
5. `next_actions`: validação ou proposta de intervenção proporcional à evidência.

O resultado numérico vigente deve ser lido no `analysis_id` validado, não copiado deste README. Fatos permanecem publicados mesmo quando nenhum mecanismo passa os gates. Nesse caso, `selected_mechanism_id=null`, a fila acionável fica vazia e a watchlist serve somente para validação — nunca autoriza contato.

A leitura executiva começa por **Resposta curta**, inclui churn e MRR perdido observado, confronta agregado com a coorte que churnará e separa tickets respondidos da base inteira. Quando nenhuma causa é sustentada, o sistema declara **Causa ainda não demonstrada**, evita falsa concentração por segmento e propõe três validações: integridade dos dados, uso prospectivo e satisfação representativa. Rótulos de confiança vêm do nível de evidência canônico; não são estimados pelo dashboard.

## Reproduzir

Requer Python 3.12. Se `python3.12` não estiver disponível, `make setup` usa `uv` quando instalado.

```bash
cd submissions/luis-roquette/solution/001-churn
make setup
make reproduce
make check
make app
```

O dashboard abre em `http://localhost:8501`. Hospedagem pública é opcional; a reprodução local é a entrega autoritativa.

## Arquitetura

```text
5 CSVs imutáveis
      ↓ contratos + qualidade
painéis observed/strict por conta e cutoff
      ↓ histórico + motivos + coortes + 6 hipóteses + gates
AnalysisResult único
      ↓ resposta canônica + 14 payloads + checksums
relatório · dashboard somente leitura · filas · manifesto
```

`make check` executa Ruff, formatação e pytest; só então reproduz em diretório temporário e compara conteúdo e parâmetros com os artefatos canônicos. A reprodução e a comparação pertencem à mesma receita fail-fast: falha na primeira impede a segunda. Só timestamp UTC e SHA de origem podem variar.

Publicação pressupõe **um escritor e o app parado**. Cada arquivo usa substituição atômica e o manifesto é escrito por último, mas o diretório inteiro não é transacional. Valide o conjunto antes de iniciar o app. Leitura concorrente, hot reload e múltiplos escritores exigiriam snapshots imutáveis e estão fora deste escopo.

## Estrutura

- `src/ravenstack_churn/`: contratos, painel temporal, diagnóstico, modelo e publicação.
- `tests/`: testes de dados, vazamento, gates, consistência, Markdown e dashboard.
- `artifacts/`: saídas canônicas protegidas por `run_manifest.json`.
- `app.py`: Streamlit somente leitura; nunca recalcula a análise.
- `.specs/` e `docs/superpowers/plans/`: SPEC e plano SDD executado.

## Artefatos

| Arquivo | Conteúdo |
|---|---|
| `ceo_answer.json` | resposta canônica em cinco blocos, `analysis_id`, claims, ações e referências |
| `report.md` | a mesma resposta canônica, seguida pelas tabelas de auditoria |
| `monthly_churn.csv` | série abr/2023–nov/2024 e comparação referência versus recente |
| `reason_distribution.csv` | primeiro motivo terminal válido por período e horizonte diagnóstico |
| `event_cohort_metrics.csv` | casos e controles contemporâneos em janelas pré-evento |
| `mechanism_scorecard.csv` | seis gates e escada de evidência por mecanismo |
| `findings.csv` | seis hipóteses com efeito, intervalo, Holm, sensibilidade e gates |
| `claim_checks.csv` | uso e satisfação por coorte |
| `segment_metrics.csv` | snapshot diagnóstico por segmento; não é taxa populacional histórica |
| `account_panel.csv` | painel completo `observed` + `strict` |
| `account_queue.csv` | contas acionáveis apenas quando existe finding aceito |
| `account_watchlist.csv` | contas nomeadas para validação descritiva, sem ação autorizada |
| `quality_report.json` | schema, nulos, duplicidades e contradições |
| `model_evaluation.json` | métricas fora do tempo e motivos de recusa |
| `run_manifest.json` | ambiente, parâmetros, `analysis_id` e SHA-256 dos 14 payloads |

## Definições e gates

- **Churn histórico:** primeiro evento terminal válido, excluindo reativação; população cadastrada no início do mês; taxa de período ponderada por exposições conta-mês, não probabilidade semestral.
- **MRR:** perda no evento usa a assinatura vigente conhecida; desconhecido permanece nulo. MRR exposto é limite máximo de oportunidade, nunca receita recuperável.
- **Coortes relativas:** casos e controles contemporâneos compartilham âncora; janelas terminam antes do churn. Satisfação representa tickets respondidos e é ponderada por respostas dentro da âncora.
- **Gates:** temporalidade, comparação, amostra/cobertura, associação ajustada com Holm, robustez `observed`/`strict` e corroboração pertinente. Cada um termina em `pass`, `fail` ou `unavailable`.
- **Escada:** `confirmed_fact`, `supported_mechanism`, `plausible_hypothesis` e `rejected_claim`. Falta de dados, intervalo amplo ou falha de ajuste nunca viram refutação automática.

Uma causa só recebe `accepted` quando todos os gates passam. Mesmo assim, a leitura é observacional e não prova causalidade.

O modelo usa split estável por conta, treino até agosto de 2024 e teste de setembro a novembro. Scores só são publicados se houver ganho de average precision, lift ≥ 1,25, Brier não pior que o baseline e avaliação segmentada completa.

## Dados e limitações

Fonte: [SaaS Subscription & Churn Analytics](https://www.kaggle.com/datasets/rivalytics/saas-subscription-and-churn-analytics-dataset), por River @ Rivalytics, licença MIT. Os cinco arquivos originais são preservados e verificados por SHA-256.

As datas contraditórias limitam inferência; feedback textual é usado apenas retrospectivamente; MRR exposto é oportunidade máxima, não receita recuperável; e nenhum experimento de intervenção existe para estimar impacto causal. O dataset parece sintético e não deve orientar contato real com clientes.

## Solução de problemas

- `Python 3.12 ou uv é obrigatório`: instale um deles e repita `make setup`.
- `ravenstack_*.csv: checksum mismatch`: restaure os dados brutos oficiais e repita `make reproduce`.
- `findings.csv checksum mismatch` (ou outro artefato): não edite `artifacts/`; execute `make reproduce`.
- `Artefatos inválidos` no app: conclua `make reproduce` antes de `make app`.
- wheel ausente: confirme Python 3.12; as versões fixadas possuem wheels Linux e macOS.

## Processo

O método completo está nos diários [pré-início](../../process-log/000-pre-inicio.md), [descoberta socrática](../../process-log/001-descoberta-socratica.md), [otimização do plano](../../process-log/002-otimizacao-plano-loop.md) e [implementação em feedback looping](../../process-log/003-implementacao-feedback-looping.md).

O parecer de segurança proporcional ao beta está em [docs/security-beta-audit.md](docs/security-beta-audit.md). Ele classifica os 19 controles solicitados, registra as evidências atuais e define os gatilhos que obrigam uma nova auditoria.
