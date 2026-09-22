# [Submission] Dhiego Spinillo — Challenge 002

Auditoria de suporte, comparação de classificadores e protótipo de triagem assistida em `submissions/dhiego-spinillo/`. Os tempos do Dataset 1 não sustentam cálculo de desperdício: não há abertura e 49,3% dos pares disponíveis estão invertidos. A entrega distingue achados, hipóteses e instrumentação necessária.

No Dataset 2, o modelo local treinado acertou 86% dos 800 rótulos reservados; Jev por definições, sem treino específico, acertou 45,25%. O limiar escolhido na validação não manteve a meta de erro no teste: todas as decisões continuam humanas. Recap foi integrado e avaliado separadamente, mas permanece experimental por fidelidade insuficiente na revisão automatizada.

O protótipo FastAPI/Jinja/SQLite/Docker classifica texto novo, registra conferências declaradas pelo atendente, separa relato de possível incidente da categoria e prepara orientação/rascunho por regras. Permite revisão, registro e exportação; não consulta sistemas externos nem envia respostas. A revisão de três casos com o candidato orientou o fluxo. Não há alegação de ganho operacional medido.

## Verificação

- 147 testes passam localmente e no Docker.
- Navegação e capturas em desktop e celular; conferências incompletas, confirmação, situação pendente e relato de incidente exercitados.
- Modelo incluído: `docker compose up --build` na pasta da submissão e abrir `http://127.0.0.1:8766`. Classificação e preparação por regras funcionam sem chave externa.
- README, process log, pareceres reais de Claude/Grok/Codex, ADRs, resultados brutos e proposta de piloto incluídos.
- Alterações restritas à pasta da submissão. Credenciais, banco local e datasets completos não fazem parte do Git.

Este arquivo prepara título e descrição; sua criação não publica o PR.
