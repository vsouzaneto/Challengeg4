# Decision log

## 2026-09-12 — Preparação e contrato analítico

### Objetivo

Estruturar uma submissão reproduzível para o Challenge 001, com Streamlit e DuckDB, sem enviar alterações ao GitHub antes de autorização explícita.

### Ferramentas de IA e automação

- **GPT-5.6 Sol xHigh no Codex:** orquestração central, inspeção do repositório, auditoria dos CSVs, implementação, testes e documentação.
- **GPT-5.6 Sol xHigh em subagentes Codex:** revisões independentes e somente leitura das regras da submissão, da arquitetura enxuta e dos limites estatísticos.
- **Gemini 3.8 High no Antigravity:** segunda análise e revisão adversarial dos achados e da primeira implementação.
- **RTK:** redução do volume das saídas de terminal durante a investigação.
- **Conversa completa:** https://chatgpt.com/s/cx_6aa6002b2a088191ab20e15596113ec3
- **Capturas selecionadas:** `evidencias-manuais/`.

### Trabalho realizado

1. O repositório foi clonado localmente com o remoto denominado `upstream` para reduzir risco de push acidental.
2. As regras do challenge, do processo de submissão e do template foram lidas antes de criar código.
3. Foi identificado que `submissions/` está ignorado pelo próprio `.gitignore`, embora seja o local obrigatório da entrega.
4. Foi realizada uma auditoria exploratória dos cinco CSVs públicos.
5. Foram encontradas divergências entre as fontes de churn, assinaturas simultâneas e eventos fora das janelas temporais possíveis.
6. A política de verdade analítica foi discutida e aprovada antes da implementação.

### Onde a IA poderia ter errado

A resposta inicial poderia ter aceitado os flags de churn, somado todas as assinaturas e produzido indicadores visualmente convincentes. A inspeção dos arquivos mostrou que essa abordagem confundiria três fenômenos diferentes e criaria receita não reconciliada.

### Julgamento humano incorporado

O autor aprovou separar snapshot, eventos e assinaturas; preservar sujeira em quarentena; não inventar substituições; rotular proxies; e não chamar um score heurístico de probabilidade.

### Decisão

Adotar o contrato descrito em `docs/adr/0001-politica-de-verdade-analitica.md` antes de construir o pipeline e o dashboard.

## 2026-09-12 — Distribuição dos dados e artefato final

### Problema

Os dados precisam alimentar a aplicação e permanecer reproduzíveis, mas os CSVs públicos e o banco derivado não devem ser versionados como se fossem código da submissão.

### Recomendação da IA

Versionar apenas o downloader, o manifesto e os hashes, reconstruindo o DuckDB a partir da fonte pública.

### Complemento do autor

A política só é aceitável se os dados necessários ao Streamlit estiverem disponíveis e se houver um artefato final com a análise concluída.

### Decisão

Foi aprovada a política descrita em `docs/adr/0002-distribuicao-e-reprodutibilidade-dos-dados.md`: bootstrap automatizado, validação de integridade, rebuild determinístico e artefato estático final avaliável sem executar o app.

## 2026-09-12 — Superfícies da entrega

### Decisão avaliada

Escolher entre uma aplicação interativa, um relatório estático ou uma entrega combinada.

### Recomendação da IA

Entregar Streamlit e PDF, evitando que a avaliação dependa da execução do app e preservando a exploração detalhada.

### Decisão do autor

Formato duplo aprovado. O Streamlit será a superfície explorável; o PDF será o artefato canônico. O Markdown versionado será a fonte editável, e os dois formatos deverão consumir as mesmas métricas gold.

## 2026-09-12 — Gate profissional de parada

### Problema

A parcela recuperável permite uma análise demonstrativa, mas continuar a análise após encontrar falhas sistêmicas poderia sugerir que essa é a conduta recomendada para uma empresa real.

### Complemento do autor

Entre a auditoria e a continuação analítica, a entrega deve avisar que a decisão correta seria parar, corrigir o sistema e somente depois retomar o diagnóstico. Se houver urgência, a investigação precisa buscar evidência independente em clientes e nos times de CS e Suporte.

### Decisão

Foi aprovado o gate descrito em `docs/adr/0004-gate-de-parada-e-analise-demonstrativa.md`. O Streamlit e o PDF deverão apresentar o callout antes de qualquer conclusão sobre churn. Pesquisa de satisfação, coleta de sugestões, entrevistas e revisão operacional serão recomendadas como rota de curto prazo.

## 2026-09-12 — Revisão adversária do protótipo inicial

### Problema

O protótipo anterior publicava churn rate, base ativa, MRR perdido, quadrantes de risco e um Random Forest como se fossem fatos operacionais. A revisão cruzada mostrou que as três definições de churn não reconciliavam, a receita estava no grão da assinatura e o modelo agregava informações posteriores ao corte.

### Erros identificados

- target inconsistente entre snapshot, ledger e assinaturas;
- leakage por histórico de churn e refunds;
- validação aleatória em vez de temporal;
- treinamento e pontuação sobre as mesmas 500 contas;
- score chamado de probabilidade sem calibração;
- quadrantes cuja separação de churn era parcialmente tautológica;
- soma de assinaturas simultâneas tratada como MRR por conta;
- recomendações de canal e suporte descritas com linguagem causal sem desenho causal.

### Decisão

Rejeitar o modelo e os outputs derivados, preservar o histórico Git como evidência da correção e reconstruir a entrega a partir da política de verdade analítica. O commit `ce8712e` removeu os artefatos rejeitados da versão corrente.

## 2026-09-12 — Pipeline Raw, Stage e Gold

### Implementação

O commit `9a1cd8c` introduziu:

1. manifesto da versão 1 do Kaggle com tamanho, linhas e SHA-256;
2. bootstrap automático ou por diretório local;
3. Raw imutável em DuckDB;
4. Stage tipado com flags, deduplicação e quarentena;
5. Gold com universos, coberturas, fatos descritivos, dimensões, proxies e triagem;
6. catálogo de métricas com estados de confiabilidade;
7. 12 exports CSV/JSON revisáveis;
8. testes sintéticos e auditoria das anomalias exatas da fonte.

### Resultado validado

- 33.100 linhas Raw;
- 12.577 registros Stage elegíveis;
- 20.523 registros Stage em quarentena;
- 5 testes aprovados quando a fonte completa é fornecida.

## 2026-09-12 — Dashboard executivo revisado com o autor

### Processo

O commit `b443e65` construiu seis páginas Streamlit sobre os exports Gold. O autor revisou visualmente cada superfície e pediu ajustes de linguagem e legibilidade.

### Ajustes orientados pelo autor

- tema claro e correção da sobreposição do topo;
- header curto, data e autoria na navegação;
- legendas de qualidade traduzidas para decisão de negócio;
- gate obrigatório antes das páginas demonstrativas;
- nomenclatura semântica nos cards e tabelas;
- rótulos na linha do tempo e escalas que não exageram variação;
- dispersão em quadrantes com leitura e recomendação;
- score identificado como índice de triagem, nunca probabilidade;
- simulação explicada como dimensionamento condicional, não ROI.

### Resultado

O dashboard passou a separar claramente auditoria, recomendação profissional de parada e continuação demonstrativa.

## 2026-09-12 — Incidente de governança entre agentes

Depois que a cota do Codex foi excedida, o autor tentou continuar a análise com outro agente em uma worktree separada. O agente interpretou incorretamente o estado e a autorização da tarefa, criou um commit e abriu indevidamente a Pull Request #119. O autor interrompeu a execução, fechou a PR, removeu a branch remota e aguardou a janela de cinco horas para retomar no ambiente canônico.

A cópia canônica foi então auditada: o trabalho válido permaneceu local, o remoto foi mantido somente como `upstream` e nenhuma nova submissão foi enviada.

Esse incidente reforçou um requisito operacional da entrega: IA não amplia autoridade. Commits locais são permitidos para preservar o processo; push, PR e comunicação externa exigem autorização humana explícita.

## 2026-09-12 — Relatório executivo canônico

### Implementação

O commit `8e27815` adicionou um gerador ReportLab e um PDF de nove páginas consumindo os mesmos exports Gold do Streamlit.

### Validação

- inspeção visual das nove páginas em resolução original;
- correção do momento de desenho dos cabeçalhos e rodapés;
- 28 verificações numéricas, estruturais e de renderização aprovadas;
- metadados, tamanho A4 paisagem e ausência de páginas vazias confirmados;
- números-chave reconciliados com `artifacts/data`.

### Decisão

O PDF é o artefato canônico para leitura executiva; o Streamlit é a superfície de exploração. Nenhum dos dois recalcula métricas de forma independente.

## 2026-09-12 — Documentação e reprodução

### Problema

O README ainda descrevia o protótipo rejeitado e apontava para arquivos removidos. Além disso, o procedimento de reconstrução não estava consolidado em uma sequência testável por um avaliador.

### Ação preparada

- substituir o README por uma porta de entrada coerente com a análise final;
- declarar a dependência de geração do PDF;
- documentar avaliação imediata e reprodução completa;
- definir resultados esperados, critérios de aceite e recuperação de falhas;
- executar o roteiro em um clone limpo posteriormente, na etapa final definida pelo autor.

### Estado

Documentação preparada para revisão humana. A reprodução limpa foi adiada pelo autor; nenhum envio remoto será realizado antes de autorização explícita.
