SHELL := /bin/sh

PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
VENV := .venv
BIN := $(VENV)/bin
CUSTOMER_CSV := data/raw/customer_support_tickets.csv
IT_CSV := data/raw/all_tickets_processed_improved_v3.csv
CUSTOMER_URL := https://www.kaggle.com/api/v1/datasets/download/suraj520/customer-support-ticket-dataset
IT_URL := https://www.kaggle.com/api/v1/datasets/download/adisongoh/it-service-ticket-classification-dataset

.PHONY: doctor bootstrap-lock setup data test lint reproduce app demo

doctor:
	@status=0; \
	for command in "$(PYTHON)" make curl unzip; do \
		command -v "$$command" >/dev/null 2>&1 || { echo "ERRO: $$command ausente; instale-o e repita make doctor."; status=1; }; \
	done; \
	if command -v "$(PYTHON)" >/dev/null 2>&1; then \
		"$(PYTHON)" -c 'import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)' || { echo "ERRO: use Python 3.12 (PYTHON=/caminho/python3.12)."; status=1; }; \
	fi; \
	test -f requirements.lock || { echo "ERRO: requirements.lock ausente; execute make bootstrap-lock no ambiente Python 3.12."; status=1; }; \
	mkdir -p data/runtime 2>/dev/null && test -w data/runtime || { echo "ERRO: data/runtime não é gravável; corrija as permissões."; status=1; }; \
	if test ! -s "$(CUSTOMER_CSV)" || test ! -s "$(IT_CSV)"; then \
		echo "ERRO: fontes ausentes. Execute make data ou baixe os ZIPs: extraia customer_support_tickets.csv e mova para $(CUSTOMER_CSV); extraia all_tickets_processed_improved_v3.csv e mova para $(IT_CSV)."; status=1; \
	else \
		echo "OK: fontes locais preparadas; conectividade externa não é necessária."; \
	fi; \
	if test "$$status" -eq 0; then \
		echo "OK: Python 3.12, lock, ferramentas, fontes e diretório gravável verificados."; \
	else \
		exit "$$status"; \
	fi
	@"$(BIN)/python" -c 'import importlib.metadata as m; from pathlib import Path; rows=[line.split("==") for line in Path("requirements.lock").read_text().splitlines() if "==" in line]; assert all(m.version(name)==version for name,version in rows), "Dependências divergentes; execute make setup"' || { echo "ERRO: ambiente/lock incompatível; execute make setup."; exit 2; }

bootstrap-lock:
	@test ! -e requirements.lock || { echo "ERRO: requirements.lock já existe; não sobrescrito."; exit 2; }
	@"$(PYTHON)" -c 'import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)' || { echo "ERRO: bootstrap-lock exige Python 3.12."; exit 2; }
	"$(PYTHON)" -m venv "$(VENV)"
	"$(BIN)/python" -m pip install --upgrade pip
	"$(BIN)/python" -m pip install 'setuptools==84.0.0'
	"$(BIN)/python" -m pip install --no-build-isolation -e '.[dev]'
	"$(BIN)/python" -m pip freeze --exclude-editable > requirements.lock

setup:
	@test -f requirements.lock || { echo "ERRO: requirements.lock ausente; execute make bootstrap-lock."; exit 2; }
	@"$(PYTHON)" -c 'import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)' || { echo "ERRO: setup exige Python 3.12."; exit 2; }
	"$(PYTHON)" -m venv "$(VENV)"
	"$(BIN)/python" -m pip install -r requirements.lock
	"$(BIN)/python" -m pip install --no-build-isolation --no-deps -e .

data:
	@mkdir -p data/raw
	@if test ! -s "$(CUSTOMER_CSV)"; then \
		tmp="$$(mktemp -d)"; trap 'rm -rf "$$tmp"' EXIT INT TERM; \
		curl -fL "$(CUSTOMER_URL)" -o "$$tmp/customer.zip" && \
		unzip -j "$$tmp/customer.zip" 'customer_support_tickets.csv' -d data/raw || \
		{ echo "ERRO: baixe o ZIP $(CUSTOMER_URL), extraia customer_support_tickets.csv e mova para $(CUSTOMER_CSV)."; exit 2; }; \
	fi
	@if test ! -s "$(IT_CSV)"; then \
		tmp="$$(mktemp -d)"; trap 'rm -rf "$$tmp"' EXIT INT TERM; \
		curl -fL "$(IT_URL)" -o "$$tmp/it.zip" && \
		unzip -j "$$tmp/it.zip" 'all_tickets_processed_improved_v3.csv' -d data/raw || \
		{ echo "ERRO: baixe o ZIP $(IT_URL), extraia all_tickets_processed_improved_v3.csv e mova para $(IT_CSV)."; exit 2; }; \
	fi
	@test -s "$(CUSTOMER_CSV)" && test -s "$(IT_CSV)" || { echo "ERRO: CSV esperado ausente ou vazio em data/raw."; exit 2; }

test:
	"$(BIN)/pytest" -q

lint:
	"$(BIN)/ruff" check .

reproduce:
	"$(BIN)/python" scripts/reproduce.py --customer "$(CUSTOMER_CSV)" --it "$(IT_CSV)" --output artifacts

app:
	@test -x "$(BIN)/streamlit" || { echo "ERRO: ambiente ausente; execute make setup."; exit 2; }
	"$(BIN)/streamlit" run app.py

demo: doctor app
