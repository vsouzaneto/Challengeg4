# Registro de etapa — M2: análise reproduzível

- Data/hora: 20/10/2026 (data da sessão; horário não registrado pelo ambiente)
- Módulo e objetivo: M2 — recalcular a EDA com corte declarado, separar abertos/fechados, distinguir médias Won das médias de todos os fechados e classificar sinais.
- Ferramenta/modelo efetivamente utilizado: Codex via ferramentas locais; edição por patch.
- Prompt enviado (texto ou caminho da evidência): instruções do usuário e `prompts/02-M2-analise.md`.
- Resultado produzido / arquivos alterados: `src/analyze.py`, `tests/test_analyze.py` e `outputs/m2_eda.json`. A função `run_analysis` gerou o relatório derivado no diretório de outputs.
- Comandos de verificação realmente executados:
  - leitura de `prompts/02-M2-analise.md` e dos arquivos do M1;
  - tentativa inicial de `python -m pytest -q`;
  - `.\\.venv\\Scripts\\python.exe -m pytest -q`;
  - `.\\.venv\\Scripts\\python.exe -c "from src.analyze import run_analysis; report = run_analysis(); ..."`;
  - validação independente das contagens com `Import-Csv`/PowerShell.
- Saídas observadas: a tentativa inicial falhou porque `python` ainda não estava disponível. Depois, o ambiente virtual foi criado, as dependências foram instaladas e o pytest terminou com `6 passed in 2.43s`. A execução gerou `outputs/m2_eda.json` e reportou 8.800 linhas, 8.800 IDs, 2.089 abertos, 6.711 fechados, 4.238 Won e win rate de `0.6315005215318135`.
- Erro identificado e correção: a instalação direta em `AppData\\Roaming\\Python` falhou por `WinError 5`. A correção foi usar `.venv` dentro do projeto, sem alterar os CSVs originais.
- Decisão humana e aprovação: nenhuma política de scoring foi aprovada. M3 não foi iniciado.
- Pendências / limitações: revisar e aprovar a proposta de política antes de iniciar M3. O score ainda não existe e nenhum ganho comercial foi validado.

## Proposta preliminar para aprovação antes do M3

Esta é uma proposta, não uma política aprovada:

- Base: somente oportunidades abertas (`Engaging` e `Prospecting`), com referência em `2017-12-31`.
- Fator principal candidato: estágio, tratado como heurística de maturidade comercial, não como taxa histórica de conversão.
- Contexto sem peso inicial: idade desde `engage_date`, produto/preço de catálogo, conta, setor, porte, região e vendedor.
- Fallbacks: missing gera aviso e contribuição neutra; conta ausente não reduz o score; produto desconhecido não recebe preço inventado.
- Proibição: não usar `close_value`, `close_date`, duração final ou qualquer resultado futuro do próprio deal aberto.
- Ordenação candidata: score decrescente; preço de catálogo apenas como desempate; `opportunity_id` como desempate final estável.
- Ainda pendentes: base numérica, pesos, faixas, clipping, versão da política e exemplos. Esses itens precisam de aprovação humana antes do M3.
