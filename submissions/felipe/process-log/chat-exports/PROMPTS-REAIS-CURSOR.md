# Prompts reais — sessão Cursor (Challenge 001)

_Export no espírito “screenshot de conversa”: pedido humano → resposta/resumo → julgamento._

---

### Pedido 1 — Produto

**Felipe:** Filtro de datas global no Command Center.

**Agente:** Implementou `periodo_inicio/fim` no bundle, `FilterBar`, `applyFilters`, gráfico de uso alinhado; regenerou pipeline e build.

**Julgamento:** Validado no dashboard local (127.0.0.1:8765).

---

### Pedido 2 — Setup Windows

**Felipe:** `start.bat` do zero; remover ps1/sh.

**Agente:** Batch com pip, Kaggle opcional, pipeline, npm build, verify, pytest, serve; corrigiu erro CMD (parênteses em `echo`).

**Julgamento:** Teste local → mensagem “Pronto” + HTTP 200 no bundle.

---

### Pedido 3 — Docs

**Felipe:** Unificar LEIA-ME e README; menos arquivos, mais qualidade.

**Agente:** `METODOLOGIA.md` + `ENTREGA-E-PR.md`; removeu duplicatas; atualizou `verify_submission.py`.

---

### Pedido 4 — Entrega G4

**Felipe:** Process log completo (guia submission); ler CONTRIBUTING; commitar pronto para rodar.

**Agente:** PROCESS-LOG expandido; CSVs + dist no PR; fork `mental-loop`; PR #198.

---

### Pedido 5 — UI

**Felipe:** Suavizar quadrado branco no hover do gráfico de barras.

**Agente:** Cursor do tooltip Recharts (dourado + blur CSS).

---

### Pedido 6 — Meta CE

**Felipe:** Por que nota 8,5 e não 10?

**Agente:** Gap objetivo: evidência visual de chat + `.pytest_cache` no repo → correção neste commit.

---

_Evidência adicional: histórico git na branch `submission/felipe-santiago` (somente `submissions/felipe/`)._
