# Submissão — Rafael Reis — Challenge 002

## Sobre mim

- **Nome:** Rafael Reis
- **LinkedIn:** não informado no perfil público utilizado para esta submissão
- **GitHub:** [rafaelreis-r5](https://github.com/rafaelreis-r5)
- **Challenge escolhido:** Challenge 002 — Redesign de Suporte

## Executive Summary

Construí um sistema único de Inteligência de Suporte observado por seis lentes: diagnóstico operacional, estratégia de automação, laboratório de tickets, Copilot, rede semântica e Command Center. O protótipo usa os dois datasets do desafio, mantém suas finalidades separadas e transforma classificação, busca semântica, evidências e replay em uma experiência navegável. A principal recomendação é automatizar triagem e recuperação de referências com limiar de revisão, preservando decisão humana para baixa confiança, risco e comunicação externa. As limitações dos dados — especialmente a ausência de abertura válida para FRT/TTR — aparecem como indisponibilidade explícita, nunca como métrica inventada.

## Solução

### Abordagem

Comecei pelo problema de negócio e pelos limites dos datasets. Estruturei a ideia com o Hermes, um agente de prompt, e depois usei o Codex para transformar o briefing em arquitetura, specs, sprints, contratos e implementação incremental. O Dataset 1 alimenta o diagnóstico de volume, status, CSAT e resoluções; o Dataset 2 alimenta o classificador de oito categorias. O backend usa Python/FastAPI e SQLite; o frontend usa Vite, TypeScript, Sigma.js e Graphology; a instalação do frontend usa pnpm.

Para classificação, usei TF-IDF com regressão logística e split por grupos normalizados. O teste separado alcançou 86,1% de acurácia e Macro F1 de 0,860. Para vizinhança, duplicatas e agrupamentos, usei embeddings multilíngues, FAISS, HDBSCAN e UMAP. O Graph apresenta relações semânticas reais com uma camada visual neon; ele não representa os neurônios internos do classificador.

### Resultados / Findings

- Rota **O Início** com narrativa de decisão, comando local e roteiro de ponta a ponta.
- Diagnóstico histórico com filtros por canal, prioridade, tipo, status, produto e CSAT.
- Ticket Lab com classificação, confiança, política de prioridade/rota/ação, vizinhos e candidatos a duplicata.
- Copilot extractivo com fontes históricas, limitações e feedback aceitar/editar/rejeitar; nenhuma mensagem externa é enviada.
- Graph com seleção de nó, isolamento de vizinhança, restauração, arraste individual, tabela equivalente e scores/tipos/métodos das arestas.
- Command Center com Live Replay, eventos, métricas incrementais, alertas semânticos e links para investigação.
- Dados originais preservados; DS1 e DS2 continuam em espaços separados.

Detalhes técnicos, contratos, métricas e limitações estão em [`solution/SOLUCAO.md`](solution/SOLUCAO.md) e na [documentação completa](solution/docs/00-indice.md).

### Recomendações

1. Pilote classificação, roteamento e recuperação de referências com revisão humana obrigatória para baixa confiança e casos sensíveis.
2. Use a rede semântica e os alertas como instrumentos de investigação, validando clusters, duplicatas e possíveis incidentes com o time.
3. Antes de produção, acrescente validação humana formal, autenticação, rate limiting, monitoramento, dados temporais operacionais e uma base de conhecimento validada.

### Limitações

Os CSVs não têm abertura válida para calcular FRT/TTR; CSAT cobre somente parte dos registros e as resoluções são genéricas. O benchmark do classificador é offline, feito no corpus IT em inglês, e não valida português, prioridade ou operação de produção. O replay simula chegadas e não mede atendimento real. Continuam pendentes validação humana de clusters/vizinhos, multisseleção, histórico recuperável de feedback, reconexão e duas abas, autenticação, performance formal e alguns modos avançados do Graph.

## Execução local

Dentro de `solution/`, com Python 3.12 e pnpm 10:

```sh
.venv/bin/python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Abra `http://127.0.0.1:8000/#/inicio`. Para reproduzir os artefatos em um ambiente novo, siga [`solution/SOLUCAO.md`](solution/SOLUCAO.md); ele contém preparação dos dados, treino, embeddings, build e testes.

## Process Log — Como usei IA

O histórico completo da conversa com a IA está em [`process-log/CHAT-DEV-CODEX.md`](process-log/CHAT-DEV-CODEX.md). Esse arquivo registra a linha de raciocínio, as decisões, as correções, as validações e as iterações realizadas com o Codex. O índice resumido está em [`process-log/README.md`](process-log/README.md).

### Evidências

- [x] Chat export/narrativa: [`process-log/CHAT-DEV-CODEX.md`](process-log/CHAT-DEV-CODEX.md)
- [x] Git history da implementação
- [x] Testes automatizados e smoke test documentados em [`solution/docs/05-validacao-demo-processo.md`](solution/docs/05-validacao-demo-processo.md)
- [ ] Screenshots ou gravação de tela adicionais

---

Submissão preparada em 16/09/2026.
