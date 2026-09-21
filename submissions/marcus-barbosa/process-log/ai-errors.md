# Erros da IA e correções

| # | Data | O que a IA fez/propôs | Como foi detectado | Causa raiz | Correção |
|---|---|---|---|---|---|
| 1 | 2026-09-21 | Ao commitar o código de base, a IA usou `git add -f` na pasta inteira (necessário porque `submissions/` está no `.gitignore` da raiz) e arrastou `.pytest_cache/` e `__pycache__/` para o commit | Lendo o `git status` antes do commit seguinte: 7 arquivos de cache estavam versionados | `git add -f` ignora TODAS as regras de ignore, inclusive o `.gitignore` da própria pasta; a IA assumiu que o `.gitignore` interno bastaria | `git rm -r --cached` dos caches e amend do commit local (não empurrado); daqui em diante o add usa pathspec de exclusão (`:!**/__pycache__`, `:!**/.pytest_cache`, `:!solution/data/raw`) e o `git ls-files` é conferido antes de cada commit |
