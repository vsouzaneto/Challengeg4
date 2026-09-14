# ADR 0002 — Distribuição e reprodutibilidade dos dados

## Contexto

Os cinco CSVs do desafio são públicos e o repositório raiz ignora downloads de dados. Ao mesmo tempo, a aplicação Streamlit e o artefato final precisam permanecer reproduzíveis e avaliáveis.

Versionar o dataset e o banco DuckDB duplicaria fontes públicas e aumentaria o risco de divergência. Exigir preparação manual reduziria a reprodutibilidade e poderia impedir a avaliação.

## Decisão

1. Não versionar os CSVs raw nem o arquivo DuckDB gerado.
2. Versionar a URL e a versão da fonte, um manifesto com hashes SHA-256, tamanhos e contagens esperadas, além do código de bootstrap.
3. O bootstrap deve baixar o arquivo público quando os CSVs não existirem, validar sua integridade e preservar os arquivos sem alteração.
4. O pipeline deve reconstruir deterministicamente os schemas raw, stage e gold no DuckDB.
5. O Streamlit deve detectar ausência dos dados, orientar ou executar o bootstrap e nunca apresentar dados parciais como análise concluída.
6. A submissão deve incluir um artefato estático final com os principais resultados, limitações e evidências visuais, permitindo avaliação sem iniciar a aplicação.
7. Um pacote local de demonstração pode conter dados gerados, desde que não seja enviado ao GitHub antes de autorização e seja identificado como artefato reproduzível, não fonte canônica.

## Alternativas rejeitadas

- **Versionar os CSVs públicos:** duplica a fonte e contraria a intenção do `.gitignore` raiz.
- **Versionar o DuckDB:** armazena um derivado binário difícil de revisar e sujeito a ficar obsoleto.
- **Exigir download manual:** aumenta o atrito e permite versões diferentes da fonte.
- **Entregar somente o dashboard:** impede avaliação rápida quando o ambiente de execução não está disponível.

## Consequências

- O código precisa tratar rede indisponível, checksum divergente e rebuild incompleto.
- O avaliador terá uma rota reproduzível e uma rota estática para verificar a análise.
- Dados locais e banco gerado serão ignorados dentro da pasta da submissão.
- O artefato final precisará registrar a versão dos dados e o hash do manifesto usado.

## Status

Aceita pelo autor da submissão em 2026-09-12.

