# Registro de etapa — M1: ingestão e qualidade

- Data/hora: 20/10/2026 (data da sessão; horário não registrado pelo ambiente)
- Módulo e objetivo: M1 — validar os CSVs reais, preservar os originais, normalizar o alias de produto e fazer os left joins many-to-one.
- Ferramenta/modelo efetivamente utilizado: Codex via ferramentas locais; edição por patch.
- Prompt enviado (texto ou caminho da evidência): instruções do usuário e `prompts/01-M1-ingestao.md`.
- Resultado produzido / arquivos alterados: `src/__init__.py`, `src/ingest.py` e `tests/test_ingest.py`. Foi preparado este registro.
- Comandos de verificação realmente executados:
  - listagem dos arquivos do projeto e dos CSVs em `data/raw`;
  - leitura dos documentos obrigatórios e de `docs/EDA_BASELINE.json`;
  - leitura dos cabeçalhos e primeiras linhas dos quatro CSVs;
  - `python --version` e `python -c "import pandas, pytest; ..."`;
  - `Get-Command py,python3,pip,pytest`.
  - validação independente com `Import-Csv`/PowerShell das contagens do pipeline e do alias.
- Saídas observadas e link de evidência: os CSVs existem; `sales_pipeline.csv` tem 8.800 registros no arquivo; o baseline declara 8.800 IDs e 2.089 abertos; o alias bruto `GTXPro` está presente. Na verificação inicial, os comandos Python falharam porque `python` não estava disponível no PATH; posteriormente o Python foi instalado e o ambiente virtual do projeto foi criado.
- Verificação independente observada: 8.800 linhas, 8.800 IDs distintos, 2.089 abertos, 1.425 contas ausentes, 500 Prospecting sem `engage_date`, 1.480 linhas `GTXPro` e zero produtos sem correspondência após considerar o alias.
- Erro identificado e correção: durante a verificação, a ferramenta `git` também não foi encontrada no PATH; isso impede consultar status Git nesta sessão, mas não é necessário para a implementação do M1. A ingestão inclui diagnóstico de datas inválidas, valores de fechamento não numéricos, chaves duplicadas, chaves ausentes e falhas de correspondência.
- Decisão humana e aprovação: nenhuma política de scoring foi aprovada ou alterada. O trabalho permaneceu restrito ao M1.
- Pendências / limitações: a execução dos testes foi realizada após a instalação do ambiente virtual; não avançar ao M2 sem revisão humana do resultado já registrado.
