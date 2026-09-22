# Como subir localhost e os labs no Databricks

Dois caminhos. O token Databricks fica só no ambiente — nunca no git, no README ou no chat.

| Alvo | URL |
| --- | --- |
| Institucional (Single-SPA) | http://localhost:3020/ |
| Chatbot (também em `/sdk/chatbot`) | http://localhost:3030/ |
| Painéis (também em `/sdk/dashboards`) | http://localhost:3010/ |

Requisitos: Node 18+, npm, Python 3. Os apps de 3010 e 3030 já precisam do `.env` local (veja os `.env.example` de cada pasta). Não copie segredo para este arquivo.

---

## 1. Localhost (3020 / 3030 / 3010)

Na raiz do repositório:

```bash
make local
```

Windows (PowerShell), se não tiver `make`:

```powershell
.\scripts\up-local.ps1
```

Git Bash / macOS / Linux, se não tiver `make`:

```bash
bash scripts/up-local.sh
```

O script instala `node_modules` se faltar, sobe o Flask dos painéis (5050), o Vite em 3010, o chatbot em 3030 (API 3031) e o Next em 3020.

Abra http://localhost:3020/ — Chatbot e Dashboards no menu carregam os outros dois via Single-SPA.

Para parar: feche as janelas (Windows) ou Ctrl+C (bash).

### Comandos manuais (se preferir três terminais)

```bash
# terminal A — painéis
cd src/monorepos/aibi-dashboards-external-embedding/backend
python app.py

cd src/monorepos/aibi-dashboards-external-embedding/frontend
npm install
npm run dev
```

```bash
# terminal B — chats
cd src/monorepos/e2e-chatbot-app-next
npm install
# Windows PowerShell:
$env:CHAT_APP_PORT="3031"; $env:PORT="3030"; $env:BACKEND_URL="http://localhost:3031"; npm run dev
# bash:
CHAT_APP_PORT=3031 PORT=3030 BACKEND_URL=http://localhost:3031 npm run dev
```

```bash
# terminal C — institucional
cd src/frontend
npm install
npx next dev -p 3020
```

---

## 2. Databricks (upload + execução)

Na sessão do terminal (valores só no ambiente):

```powershell
$env:DATABRICKS_HOST="https://SEU-WORKSPACE.cloud.databricks.com"
$env:DATABRICKS_TOKEN="SEU-PAT"
$env:DATABRICKS_USER="seu-email@dominio.com"
```

```bash
export DATABRICKS_HOST="https://SEU-WORKSPACE.cloud.databricks.com"
export DATABRICKS_TOKEN="SEU-PAT"
export DATABRICKS_USER="seu-email@dominio.com"
```

Enviar os quatro packs (`notebook-data-001-churn`, `notebook-process-002-support`, `notebook-build-003-lead-scorer`, `notebook-marketing-004-social`) para `/Users/$DATABRICKS_USER/ai-master-challenge/`:

```bash
make databricks
```

ou:

```bash
python scripts/databricks_labs.py upload
```

Arquivo maior que 9 MB é pulado (o CSV do lab 004). Coloque-o num Volume e use o widget `data_path`, como no README do pack.

Disparar os jobs Lab 01 → 04 (IDs do workspace já provisionado; em outra conta, defina `DATABRICKS_JOB_001` … `DATABRICKS_JOB_004`):

```bash
make databricks-run
```

ou:

```bash
python scripts/databricks_labs.py run
```

Upload e run juntos:

```bash
make databricks-all
```

Sem job: no Workspace, abra cada `01_LAB_importando_dados` e **Run All**, depois 02, 03 e 04. Widgets: `catalog_name=workspace` e o `schema_name` do pack (`ravenstack`, `supportiq`, `crm`, `social`).

---

## Conferência

```bash
make check
```

```bash
python scripts/databricks_labs.py check
python -m unittest scripts/test_databricks_labs.py
```

---

## Makefile

| Alvo | Faz |
| --- | --- |
| `make local` | Sobe 3010, 3020 e 3030 |
| `make databricks` | Upload dos 4 labs |
| `make databricks-run` | Run now dos 4 jobs |
| `make databricks-all` | Upload + run |
| `make check` | Pastas + testes do script |
