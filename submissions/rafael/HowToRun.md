
### Como rodar

**Com Docker (recomendado).** Fixa todas as versões, confere o dataset e falha se algum resultado divergir da referência.

```bash
cd submissions/rafael
docker build -t g4-social . && docker run --rm -p 8000:8000 g4-social   # site em http://127.0.0.1:8000 (build ~10 min)
```
- Sem o CSV em `data/raw/`: `docker build --secret id=kaggle,src=$HOME/.kaggle/kaggle.json -t g4-social .`
- Checagem completa: `docker run --rm g4-social python solution/reproducibility/verify.py --retrain --tests`

**Sem Docker** (Python 3.14 e credencial do Kaggle em `~/.kaggle/kaggle.json`):

```bash
cd submissions/rafael
python3.14 -m venv .venv && .venv/bin/pip install -r requirements.lock && .venv/bin/pip install -e .
bash solution/scripts/get_data.sh                                          # baixa o CSV e confere o sha256
.venv/bin/python -m pytest -q                                              # testes (~2 min)
.venv/bin/python solution/reproducibility/verify.py                        # confere resultados com a referência
.venv/bin/python solution/cli/answer_questions.py --out docs/respostas.md  # relatório das 4 perguntas
.venv/bin/social-web                                                       # site em http://127.0.0.1:8000
```
Atalhos no [`Makefile`](Makefile).

### Organização

```
submissions/rafael/
├── README.md · DEVELOPMENT_PROCESS.md     visão geral · decisões tomadas
├── Dockerfile · Makefile                  ambiente · atalhos
├── solution/                              código: análises, site, testes, notebooks
├── docs/                                  resumo executivo, relatório e imagens
├── knowledge/                             achados por tema
├── process-log/                           como usei IA: narrativa e prompts
├── evidencias/                            conversas com a IA exportadas
├── review/                                revisão crítica da entrega
└── instructions/                          regras seguidas no projeto
```

---

