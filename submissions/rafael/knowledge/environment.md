# Ambiente

- Repo clonado de `Gestao-Quatro-Ponto-Zero/ai-master-challenge`; remote renomeado para `upstream`; branch `submission/rafael`.
- Fork: `origin` = git@github.com:RafaelCostaF/ai-master-challenge.git (SSH; HTTPS falha sem TTY). `gh` não instalado.
- Python 3.14; `.venv` com `requirements.txt` (versões fixadas pelo pip freeze; as versões antigas não compilam no 3.14).
- Kaggle: `~/.kaggle/kaggle.json` (chmod 600); download via API com curl.
- Root `.gitignore` ignora `submissions/` e não pode ser alterado → sempre `git add -f submissions/rafael/<arquivo>` (o `.gitignore` local ainda vale para não usar `-f` em dados).
- `git add -f <pasta>` também adiciona arquivos ignorados (`__pycache__`, dados) → adicionar arquivo por arquivo ou conferir `git status` antes do commit.
- Background/timeout: `pkill -f <padrão>` pode matar o próprio shell da ferramenta (o padrão casa com o comando) → usar `kill <pid>`. `RidgeCV` em TF-IDF esparso de 52K linhas trava (GCV denso) → Ridge com `solver="sparse_cg"` + `max_features`.

## Reprodutibilidade (2026-10-19)
- **Organização:** todo código fica em `solution/` (`src/`, `cli/`, `scripts/`, `reproducibility/`, `tests/`, `notebooks/`); na raiz ficam só configuração (`Dockerfile`, `Makefile`, `pyproject.toml`, `requirements.txt`, `pytest.ini`) e documentação. Mapa em `solution/README.md`.
- **`Dockerfile`** (`python:3.14.3-slim` + `libgomp1` + `requirements.lock`):
  - copia só o que roda (`solution/src`, `cli`, `scripts`, `reproducibility`, `tests` e a configuração), sem docs nem notebooks;
  - o CSV vem do contexto por bind mount, ou é baixado com `--secret id=kaggle,...` (o token não fica na imagem);
  - treina tudo no build (`social-web --build-only`) e roda a checagem no build, que falha se algo divergir;
  - roda como usuário `app` (sem root), com healthcheck em `/api/health`.
- **`solution/reproducibility/verify.py`**: confere Python 3.14, todos os pacotes do `requirements.lock` na versão exata (e se `requirements.txt` concorda com o lock), o sha256 do CSV, os modelos em `solution/models/` e se o payload inteiro do site + a resposta do simulador para 4 posts de teste batem com `solution/reproducibility/reference.json`. Números com tolerância relativa de 1e-6, textos idênticos; só `meta.gerado_em` é ignorado. Opções: `--retrain` (retreina do zero numa pasta temporária) · `--tests` (pytest) · `--write-reference` (regrava a referência depois de mudar a análise de propósito).
- **`requirements.lock`** (`pip freeze` do ambiente testado): `requirements.txt` só fixava as 23 dependências diretas, e o container já tinha resolvido 4 indiretas diferentes do venv, uma delas pré-release (`wrapt 2.5.2rc1`). O lock fixa todos os pacotes. Para regenerar: `.venv/bin/pip freeze --exclude-editable`, mantendo o comentário da 1ª linha.
- **CatBoost** com `allow_writing_files=False`: não cria mais `catboost_info/` na pasta onde roda (não muda resultado; a checagem confirma).
- **Quando o build falha na checagem:** alguma mudança de código alterou números ou textos. Se foi intencional, rode `verify.py --write-reference` e faça commit da nova referência junto com a mudança.
- Docker instalado nesta máquina (pacotes do Fedora: `moby-engine` 29.8.2, `docker-cli`, `docker-buildx`). O usuário está no grupo `docker`, mas isso só vale em sessão nova; até lá, usar `sg docker -c "docker …"`. Não há `make`. O `podman` funciona com o mesmo Dockerfile, mas no rootless `localhost` (IPv6) não chega na porta publicada (usar `127.0.0.1`).
- Site no container `g4-social`: `docker run -d --name g4-social -p 8000:8000 g4-social`; para parar: `docker stop g4-social && docker rm g4-social`.
