# Atalhos para reproduzir a entrega do zero (rodar dentro de submissions/rafael). Requer Python 3.14.
PY := .venv/bin/python
DOCKER ?= $(shell command -v docker || command -v podman)
IMAGE := g4-social
NOTEBOOK_BUILDERS := $(wildcard solution/notebooks/build/build_*.py)

.PHONY: all setup data test report notebooks site verify verify-full docker-build docker-run docker-verify

all: setup data test report notebooks   ## tudo, menos subir o site

setup:                                   ## ambiente virtual + dependências fixadas + pacotes locais
	python3.14 -m venv .venv
	.venv/bin/pip install -q -r requirements.lock
	.venv/bin/pip install -q -e .

data:                                    ## baixa o CSV do Kaggle e confere o sha256
	bash solution/scripts/get_data.sh data/raw

test:                                    ## testes automatizados (efeitos plantados + rotas do site)
	$(PY) -m pytest -q

report:                                  ## regenera docs/respostas.md (4 perguntas + estratégia + fila de testes)
	$(PY) solution/cli/answer_questions.py --out docs/respostas.md --figures docs/figures

notebooks:                               ## regenera e executa os 14 notebooks
	for b in $(NOTEBOOK_BUILDERS); do \
		name=$$(basename $$b .py | sed 's/^build_//'); \
		$(PY) $$b solution/notebooks/$$name.ipynb || exit 1; \
		.venv/bin/jupyter nbconvert --to notebook --execute --inplace solution/notebooks/$$name.ipynb || exit 1; \
	done

site:                                    ## sobe o site em http://127.0.0.1:8000 (1ª vez treina tudo, ~5 min)
	.venv/bin/social-web

verify:                                  ## checagem rápida: Python, bibliotecas fixadas, sha256 do CSV, modelos e resultados = referência
	$(PY) -W ignore solution/reproducibility/verify.py

verify-full:                             ## checagem completa: retreina do zero (~5 min) e roda os testes
	$(PY) -W ignore solution/reproducibility/verify.py --retrain --tests

docker-build:                            ## imagem com tudo: instala, confere o CSV, treina e verifica (falha se divergir)
	$(DOCKER) build $(if $(wildcard data/raw/social_media_dataset.csv),,--secret id=kaggle,src=$(HOME)/.kaggle/kaggle.json) -t $(IMAGE) .

docker-run:                              ## sobe o site da imagem em http://127.0.0.1:8000
	$(DOCKER) run --rm -p 8000:8000 $(IMAGE)

docker-verify:                           ## retreino do zero + testes dentro do container
	$(DOCKER) run --rm $(IMAGE) python -W ignore solution/reproducibility/verify.py --retrain --tests
