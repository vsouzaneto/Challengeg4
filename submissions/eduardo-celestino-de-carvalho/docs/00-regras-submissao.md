# Regras do challenge e estado da entrega

Fonte: [README principal](../../../README.md), [Challenge 003](../../../challenges/build-003-lead-scorer/README.md), [Guia de Submissão](../../../submission-guide.md) e [CONTRIBUTING](../../../CONTRIBUTING.md).

## Exigências da solução

- Escolher um desafio: **003 — Lead Scorer**.
- Entregar software que execute com os dados reais das quatro tabelas públicas.
- Priorizar negócios com lógica além de ordenar por valor e explicar ao vendedor por que cada negócio recebeu seu score.
- Documentar comandos de instalação/execução, lógica do score e limitações.
- Entregar **process log obrigatório**: ferramentas de IA, etapas, iterações, verificações, erros reais e decisões do candidato. A ausência dessa evidência desclassifica a submissão.

## Regras de organização e envio

- Todos os arquivos que entrarão no PR devem ficar em `submissions/eduardo-celestino-de-carvalho/`. Não alterar arquivos fora dessa pasta no PR.
- O README da pasta segue as seções do template oficial e será completado com os resultados finais.
- O envio final exige fork, branch `submission/eduardo-celestino-de-carvalho` e um Pull Request para `main` com título `[Submission] Eduardo Celestino de Carvalho — Challenge 003`.
- O repositório só aceita envio por PR. A orientação de tempo é 4–6 horas; o README principal informa que não há prazo fixo.

## Estado local em 15/10/2026

| Item | Estado |
|---|---|
| Repositório público trazido para esta pasta de trabalho | Feito |
| Branch local `submission/eduardo-celestino-de-carvalho` | Feito |
| Pasta de submissão, hipótese e process log inicial | Feito |
| G1 — carga e auditoria reproduzíveis | Concluído; tipos, chaves, nulos, datas e aliases verificados |
| G2 — baseline e modelo | Concluído; modelo reprovado para uso operacional, resultados documentados |
| G3 — ferramenta funcional | Concluído; Lead Kanban com Pipeline, Dashboard e procedimento |
| G4/G5 — revisão de qualidade e handover final | Concluído; robustez testada, docs revisados, teste em clone limpo |
| Commits locais | Feitos com `git add -f` e lista explícita de arquivos |
| Fork, push e Pull Request | **Aguardar a decisão do candidato** |

**Detalhe do repositório:** o `.gitignore` da raiz ignora `submissions/`. Para incluir os arquivos da entrega sem modificar a raiz, é necessário usar `git add -f -- <caminhos explícitos dos arquivos>` e conferir `git diff --cached --name-only` antes de qualquer commit. **Não forçar a pasta inteira:** isso também incluiria o ZIP de dados locais, mesmo com a regra `solution/data/` no `.gitignore`. Nenhum arquivo foi enviado ao GitHub nesta etapa.

## Cuidados com a publicação futura

O PR será público. Material de outros projetos serviu apenas para avaliar competências; código, dados, nomes de clientes, credenciais e conversas privadas desses projetos não devem aparecer na solução ou nas evidências. Usar somente o dataset público indicado pelo challenge e conteúdo produzido especificamente para esta submissão.
