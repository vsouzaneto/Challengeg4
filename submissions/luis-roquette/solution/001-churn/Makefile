PYTHON := .venv/bin/python

.PHONY: setup test reproduce app check

setup:
	@test -x $(PYTHON) || { \
		if command -v python3.12 >/dev/null; then python3.12 -m venv .venv; \
		elif command -v uv >/dev/null; then uv venv --python 3.12 .venv; \
		else echo "Python 3.12 ou uv é obrigatório" >&2; exit 1; fi; \
	}
	@$(PYTHON) -m pip --version >/dev/null 2>&1 || $(PYTHON) -m ensurepip --upgrade
	$(PYTHON) -m pip install --only-binary=:all: -e '.[dev]'

test:
	$(PYTHON) -m pytest -q

reproduce: test
	RAVENSTACK_TEST_STATUS=passed $(PYTHON) -m ravenstack_churn.cli reproduce --raw-dir data/raw --output-dir artifacts

app:
	RAVENSTACK_ARTIFACT_DIR=artifacts $(PYTHON) -m streamlit run app.py

check:
	$(PYTHON) -m ruff check src tests app.py
	$(PYTHON) -m ruff format --check src tests app.py
	$(PYTHON) -m pytest -q
	run_dir=$$(mktemp -d /tmp/ravenstack-check.XXXXXX); \
	trap 'rm -rf "$$run_dir"' EXIT; \
	RAVENSTACK_TEST_STATUS=passed $(PYTHON) -m ravenstack_churn.cli reproduce --raw-dir data/raw --output-dir "$$run_dir" && \
	$(PYTHON) -m ravenstack_churn.cli compare --reference-dir artifacts --candidate-dir "$$run_dir"
