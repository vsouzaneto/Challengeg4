.PHONY: help local databricks databricks-run databricks-all check

ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PYTHON ?= python

help:
	@echo make local            sobe 3010 + 3020 + 3030
	@echo make databricks       envia os 4 labs para o Workspace
	@echo make databricks-run   dispara os 4 jobs (Lab 01-04)
	@echo make databricks-all   upload + run
	@echo make check            confere pastas e testes do script

ifeq ($(OS),Windows_NT)
local:
	powershell -NoProfile -ExecutionPolicy Bypass -File "$(ROOT)/scripts/up-local.ps1"
else
local:
	bash "$(ROOT)/scripts/up-local.sh"
endif

databricks:
	$(PYTHON) "$(ROOT)/scripts/databricks_labs.py" upload

databricks-run:
	$(PYTHON) "$(ROOT)/scripts/databricks_labs.py" run

databricks-all:
	$(PYTHON) "$(ROOT)/scripts/databricks_labs.py" all

check:
	$(PYTHON) "$(ROOT)/scripts/databricks_labs.py" check
	$(PYTHON) -m unittest "$(ROOT)/scripts/test_databricks_labs.py"
