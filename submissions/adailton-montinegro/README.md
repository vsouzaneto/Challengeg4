# Submissão — Adailton Montinegro — Challenge 001

## Sobre mim

- **Nome:** Adailton Montinegro
- **LinkedIn:** [linkedin.com/in/adailtonmontinegro](https://www.linkedin.com/in/adailtonmontinegro/)
- **Challenge escolhido:** 001 — Diagnóstico de Churn da RavenStack

---

## Executive Summary

Cruzei e auditei as cinco fontes da RavenStack, totalizando 33.100 registros. As chaves conectam as tabelas, mas os eventos não formam um ciclo de vida temporal e financeiro coerente: somente 22,2% do uso e 46,1% dos tickets sobrevivem às regras temporais, enquanto o cadastro e o histórico de churn concordam em apenas 37,6% das contas. Por isso, a base não permite afirmar uma causa raiz de churn, calcular churn mensal ou receita perdida, nem treinar uma probabilidade individual defensável. A recomendação correta é interromper a análise decisória, corrigir os contratos de dados e, se houver urgência, coletar evidência independente com clientes, Customer Success e Suporte.

O restante da entrega é uma demonstração estatística explicitamente limitada da parcela recuperável. Ela mostra como preservar os dados brutos, colocar impossibilidades em quarentena, publicar métricas com cobertura e organizar uma fila de investigação humana sem fingir causalidade ou automação pronta para produção.

> **Mensagem para o CEO:** a RavenStack confirmou um problema de medição antes de confirmar uma causa de churn. Usar estes dados para abordar clientes, alterar canais ou comprometer investimento criaria precisão aparente sobre fatos incompatíveis.

---

## Comece por aqui

| Artefato | Para que serve |
|---|---|
| [Relatório executivo em PDF](output/pdf/ravenstack-churn-diagnostic.pdf) | Entrega canônica em 9 páginas; pode ser avaliada sem executar código. |
| [Aplicação Streamlit](solution/app.py) | Auditoria visual, análise demonstrativa, filtros e fila de triagem. |
| [Narrativa executiva](docs/EXECUTIVE-NARRATIVE.md) | Evidências, limites de inferência e plano de ação detalhado. |
| [Guia de reprodução](docs/REPRODUCIBILITY.md) | Instalação, rebuild Raw → Stage → Gold, testes e critérios de aceite. |
| [Process log](process-log/DECISION-LOG.md) | Linha do tempo do uso de IA, revisões humanas, erros e decisões. |

Para abrir o dashboard usando os exports Gold já versionados:

```bash
cd submissions/adailton-montinegro
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run solution/app.py
```

O fluxo completo, incluindo download validado da fonte, reconstrução do DuckDB, testes e regeneração do PDF, está em [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md).

---

## O que foi encontrado

### 1. Qualidade e cobertura

| Evidência | Resultado | Consequência |
|---|---:|---|
| Registros auditados | 33.100 | As cinco tabelas foram inspecionadas e cruzadas. |
| Uso temporalmente elegível | 5.554 de 25.000 — 22,2% | 19.446 registros ficam fora de análises temporais. |
| Tickets temporalmente elegíveis | 923 de 2.000 — 46,1% | 1.077 tickets são anteriores ao cadastro da conta. |
| Uso anterior ao início da assinatura | 19.142 registros — 76,6% | A telemetria não respeita a vigência contratual. |
| Assinaturas em sobreposição não explicada | 4.992 de 5.000 — 99,8% | Não existe `product_id` para distinguir contratos simultâneos. |
| Contas com sobreposição | 500 de 500 | Somar assinaturas por conta superestimaria MRR. |
| Eventos de churn que coincidem com `end_date` | 6 de 600 — 1,0% | O evento não identifica a assinatura encerrada. |
| Tickets sem nota de satisfação | 825 de 2.000 — 41,3% | A média de satisfação descreve apenas respondentes. |

Integridade referencial e `ARR = MRR × 12` estão corretos. Isso comprova consistência estrutural limitada, não validade temporal ou de negócio.

### 2. Existem três definições incompatíveis de churn

- O cadastro marca 110 de 500 contas, ou 22%, como churn no snapshot.
- O histórico contém 600 ocorrências associadas a 352 contas.
- Cadastro e histórico concordam em 188 de 500 contas, ou 37,6%.
- Há 35 contas marcadas apenas no cadastro e 277 apenas no histórico.
- As assinaturas encerradas não reconciliam com o histórico de eventos.

Essas fontes não podem ser fundidas em uma única variável-alvo sem criar um fato que os dados não contêm.

### 3. O desafio é respondido sem inventar precisão

**O que está causando o churn?** A causa de negócio não é identificável com esta fonte. A causa raiz comprovada do paradoxo executivo é a falha de medição: cadastro, assinatura, produto, suporte e churn não compartilham um ciclo de vida reconciliado.

**Quais segmentos estão mais em risco?** A base não suporta probabilidade calibrada nem ranking autônomo de clientes. O dashboard entrega uma fila de triagem para 390 contas sem flag no snapshot: 376 têm cobertura insuficiente e precisam de validação de dados; somente uma entra na faixa demonstrativa de atenção alta. Receita é usada para ordenar impacto potencial, nunca para aumentar artificialmente o risco.

**O que fazer?** Parar o uso decisório da base; corrigir instrumentação e contratos de dados; obter voz do cliente em paralelo; operar a triagem apenas em `shadow mode`; e testar intervenções com desenho controlado depois da reconstrução do baseline.

### 4. Sinais exploratórios que merecem investigação

- A intensidade média de uso por registro permanece praticamente plana nas janelas anteriores à próxima ocorrência.
- Na parcela temporalmente elegível, 6 de 40 tickets dos 14 dias anteriores foram escalados, contra 5 de 107 entre 15 e 60 dias. O sinal é exploratório e não prova causa.
- Os motivos declarados estão distribuídos entre produto e funcionalidades (19,0%), orçamento (17,3%), suporte (17,3%), não informado (15,8%), concorrente (15,3%) e preço (15,2%). Motivo declarado é hipótese para pesquisa, não sentença causal.
- Plano, indústria e canal não apresentam evidência robusta suficiente para recomendar ICP ou realocação de aquisição.

---

## Recomendação priorizada

| Prioridade | Ação concreta | Dono sugerido | Como medir |
|---|---|---|---|
| P0 | Suspender KPIs, modelos e automações baseados nas definições conflitantes. | CEO + Dados | Outputs retirados da rotina decisória. |
| P0 | Conduzir pesquisa curta, entrevistas com ativos/cancelados/reativados e revisão conjunta de casos. | CS + Suporte + Produto | Respostas, entrevistas e hipóteses registradas com fonte. |
| P1 | Definir a state machine de conta e assinatura e o contrato dos eventos de churn. | Produto + Billing + Engenharia | Estado atual reconciliado com ledger e vigência. |
| P1 | Incluir `subscription_id`, produto, datas solicitada/efetiva, reativação, invoice e pagamento. | Billing + Engenharia de Dados | Waterfall de MRR fecha por conta-produto-período. |
| P1 | Bloquear uso fora da vigência, tickets pré-cadastro e IDs duplicados na ingestão. | Engenharia de Dados | Zero novas violações e quarentena monitorada. |
| P2 | Operar a fila de triagem apenas para revisão humana em `shadow mode`. | CS Ops + Dados | Falsos positivos, overrides e outcomes futuros registrados. |
| P3 | Testar intervenções por sinal com controle ou rollout escalonado. | Produto + CS + Analytics | Uplift incremental, custo e receita reconciliada. |

A simulação financeira do dashboard é apenas um dimensionamento condicional. Converter oportunidade em ROI exige custo da ação, margem e uplift causal observado — campos inexistentes na base.

---

## Solução técnica

```text
Kaggle v1 ou diretório local
          │
          ▼
manifesto: tamanho + linhas + SHA-256
          │
          ▼
Raw imutável ──► Stage tipado + flags + quarentena
                              │
                              ▼
                     Gold + catálogo de métricas
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
        exports CSV/JSON              DuckDB local
                 │
          ┌──────┴──────┐
          ▼             ▼
      Streamlit      PDF executivo
```

### Contratos adotados

- **Raw:** cópia byte a byte dos cinco CSVs, verificada pelo manifesto.
- **Stage:** tipagem, padronização, deduplicação determinística, flags de qualidade e quarentena; nenhuma data ou status é inventado.
- **Gold:** universos analíticos, coberturas, fatos descritivos, dimensões, testes exploratórios, proxies condicionais e fila de triagem.
- **Métricas:** cada indicador é rotulado como `Observed`, `Derived`, `Conditional` ou `Unavailable`.
- **Apresentação:** Streamlit e PDF leem os mesmos 11 CSVs e um JSON publicados em `artifacts/data/`.

---

## Limitações explícitas

Com os dados atuais, não são calculáveis de forma defensável:

- saldo mensal de clientes e taxa mensal de logo churn;
- MRR perdido, expansion, contraction, GRR e NRR;
- causa raiz de negócio ou efeito causal de suporte, produto, preço ou canal;
- probabilidade individual calibrada de churn;
- ICP recomendado por aquisição;
- LTV, CAC payback e ROI de uma ação.

O índice de triagem não é modelo preditivo. O intervalo de receita por conta não é MRR reconciliado. As contagens mensais de eventos não são churn rate.

---

## Process Log — Como usei IA

### Ferramentas

| Ferramenta | Uso |
|---|---|
| GPT-5.6 Sol xHigh — Codex | Orquestrador central da investigação, implementação do pipeline, Streamlit, PDF, testes e documentação. |
| GPT-5.6 Sol xHigh — subagentes Codex | Revisões independentes de escopo, restrições do repositório e arquitetura da solução. |
| Gemini 3.8 High — Antigravity | Segunda análise e revisão adversarial dos achados e da primeira implementação. |
| DuckDB + Python | Modelagem Raw/Stage/Gold, validações e exports reproduzíveis. |
| Streamlit + Altair + Plotly | Interface executiva e exploração interativa. |
| ReportLab | Relatório PDF gerado a partir da mesma camada Gold. |
| RTK | Redução de ruído das saídas de terminal durante a construção. |

### Workflow e iterações

1. Leitura do desafio, template, guia de submissão e estrutura dos cinco arquivos.
2. Profiling independente de cada tabela e auditoria dos cruzamentos.
3. Identificação das definições incompatíveis de churn e das violações temporais.
4. Revisão humana da primeira análise, que apresentava métricas e modelo não sustentados.
5. Aprovação de uma política de verdade analítica e de um gate executivo de parada.
6. Construção do pipeline Raw → Stage → Gold com manifesto, quarentena e testes.
7. Construção e revisão visual do Streamlit em seis páginas.
8. Remoção do protótipo rejeitado e de artefatos que poderiam orientar decisões erradas.
9. Geração e inspeção página a página do PDF canônico.
10. Preparação de documentação e reprodução em ambiente limpo.

### Onde a IA errou e como foi corrigida

- A primeira abordagem aceitou definições incompatíveis de churn e tentou calcular churn rate, base ativa e MRR perdido. A auditoria mostrou que o denominador mensal e a receita encerrada não são identificáveis.
- Um Random Forest foi inicialmente chamado de modelo preditivo, apesar de target incoerente, leakage temporal, validação aleatória e pontuação na própria amostra. O modelo e os quadrantes derivados foram rejeitados e removidos.
- Correlações exploratórias de suporte, uso e canal chegaram a ser descritas como causa ou recomendação. A linguagem foi reescrita para separar fatos, associações, hipóteses e causalidade.
- Depois que a cota do Codex foi excedida, uma continuação em outra worktree abriu indevidamente a PR #119. O autor interrompeu a execução, fechou a PR, removeu a branch remota e aguardou a janela de cinco horas antes de retomar o trabalho canônico.
- A revisão visual encontrou sobreposição no topo do Streamlit, legendas técnicas, eixos que exageravam variação e cabeçalhos de PDF que não rasterizavam em algumas páginas. Todos foram corrigidos e reinspecionados.

### O que o julgamento humano adicionou

- A exigência de mostrar primeiro a qualidade da fonte e recomendar a interrupção profissional da análise.
- A decisão de continuar apenas como demonstração estatística da parcela recuperável.
- A proibição de inventar status, datas, receita, churn rate, causalidade, probabilidade ou ROI.
- A rota alternativa de curto prazo baseada em voz do cliente e revisão de CS/Suporte.
- A exigência de linguagem compreensível para um CEO, evidências rastreáveis e revisão visual antes do PDF.
- O controle explícito de Git: commits locais frequentes e nenhum envio remoto sem autorização.

### Evidências

- [Conversa completa com o Codex — export sanitizado](evidencias-manuais/conversa-codex-sanitizada.md)
- [Capturas manuais do processo](evidencias-manuais/)
- [Decision log completo](process-log/DECISION-LOG.md)
- [Política de verdade analítica](docs/adr/0001-politica-de-verdade-analitica.md)
- [Distribuição e reprodutibilidade](docs/adr/0002-distribuicao-e-reprodutibilidade-dos-dados.md)
- [Superfícies da entrega](docs/adr/0003-superficies-da-entrega.md)
- [Gate de parada](docs/adr/0004-gate-de-parada-e-analise-demonstrativa.md)
- Histórico Git com commits incrementais da análise, pipeline, aplicação, limpeza e relatório.

---

## Estado da entrega

- [x] Cinco fontes cruzadas.
- [x] Evidências quantitativas rastreáveis.
- [x] Correlação separada de causalidade.
- [x] Recomendações concretas e priorizadas.
- [x] Streamlit funcional em tema claro.
- [x] PDF executivo de 9 páginas.
- [x] Process log e histórico Git.
- [x] Pipeline e testes automatizados.
- [ ] Reprodução final em ambiente limpo — procedimento em [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md), com execução adiada pelo autor para a etapa final.

_Documentação preparada em 12 de setembro de 2026._

---

## Mapa da entrega — até o segundo nível

```text
submissions/adailton-montinegro/
├── .streamlit/
│   └── config.toml
│       Tema claro e identidade visual da aplicação.
├── artifacts/
│   └── data/
│       11 CSVs e 1 JSON da camada Gold usados pelo Streamlit e pelo PDF.
├── data/
│   ├── manifest.v1.json
│   │   Versão, tamanho, linhas e SHA-256 dos cinco arquivos de origem.
│   ├── raw/
│   │   CSVs originais gerados localmente; somente .gitkeep é versionado.
│   └── warehouse/
│       Banco DuckDB reconstruível; somente .gitkeep é versionado.
├── docs/
│   ├── EXECUTIVE-NARRATIVE.md
│   │   Diagnóstico, limites de inferência e plano de ação completo.
│   ├── REPRODUCIBILITY.md
│   │   Setup, rebuild, testes, resultados esperados e checklist de aceite.
│   └── adr/
│       Quatro decisões sobre verdade analítica, dados, entrega e gate.
├── evidencias-manuais/
│   ├── conversa-codex-sanitizada.md
│   │   Export completo e sanitizado da conversa com o Codex.
│   └── 001 a 011 — capturas do trabalho com IA
│       Orientações, inconsistências, análises paralelas, refinamentos e revisão.
├── output/
│   └── pdf/
│       Relatório executivo canônico de 9 páginas.
├── process-log/
│   └── DECISION-LOG.md
│       Linha do tempo, erros da IA, intervenções humanas e decisões.
├── scripts/
│   ├── build.py
│   │   Bootstrap, validação do manifesto e execução Raw → Stage → Gold.
│   └── build_report.py
│       Geração reprodutível do PDF a partir dos exports Gold.
├── solution/
│   ├── pages/
│   │   Seis páginas Streamlit: capa, qualidade, one-page, diagnóstico,
│   │   triagem de risco e plano de ação.
│   ├── sql/
│   │   Regras declarativas das camadas Raw, Stage e Gold.
│   ├── src/
│   │   Pacote Python de bootstrap, pipeline e testes estatísticos.
│   ├── app.py
│   │   Entrada e navegação da aplicação.
│   └── ui.py
│       Componentes visuais, carregamento dos Gold e gate.
├── tests/
│   ├── test_pipeline_contracts.py
│   │   Contratos determinísticos com fixture sintética.
│   ├── test_known_v1_audit.py
│   │   Auditoria dos números conhecidos da versão 1 do Kaggle.
│   └── conftest.py
│       Configuração da suíte.
├── CONTEXT.md
│   Glossário e semântica canônica.
├── README.md
│   Porta de entrada executiva, técnica e processual.
└── requirements.txt
    Dependências reproduzíveis da solução.
```
