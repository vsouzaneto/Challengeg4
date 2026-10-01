# Verificação da base — 30/09/2026

Ambiente observado: Windows, Node.js 22.14.0, npm 10.9.2 e Git 2.48.1. Verificações executadas em `solution/`.

| Verificação | Resultado observado |
| --- | --- |
| Instalação das versões exatas | Concluída; package-lock.json gerado; auditoria npm informou zero vulnerabilidades naquele momento |
| `npm ci --offline` | Instalação reproduzível validada pelo lockfile, usando cache local; 126 pacotes instalados |
| `npm test` | 2 arquivos, 7 testes aprovados |
| `npm run build` | Tipos do frontend, scripts e testes aprovados; build Vite concluído |
| `npm run prepare:data` | Código 1 esperado: proveniência/CSVs ainda ausentes; nenhum manifesto de dados gerado |
| `npm run evaluate` | Código 1 esperado com mensagem de avaliação não implementada; nenhuma métrica gerada |
| `npm run dev` | Servidor local iniciado em http://127.0.0.1:5173/ |
| Revisão visual no navegador integrado | Não concluída: o cliente bloqueou localhost e 127.0.0.1 com ERR_BLOCKED_BY_CLIENT |
| Git | Repositório inicializado; dependências, cache e build ignorados; sem commit ou remoto |

O sandbox inicial impediu o Node de resolver caminhos do perfil do Windows (`EPERM`); instalação e verificações foram concluídas após execução autorizada fora dessa restrição. Não foi necessário alterar proteções do navegador para entregar a base.

A primeira tentativa de `npm ci` encontrou o binding nativo do Vite em uso pelo servidor local. Após encerrar somente o processo Vite deste projeto, a reinstalação terminou e os sete testes e o build foram novamente aprovados. O servidor ficou encerrado; para abrir o app, executar `npm run dev`.

A preparação integral dos dados, o motor, a fila de missões e a avaliação histórica permanecem nos próximos marcos. Contagens e conclusões da análise anterior não foram revalidadas nesta etapa. A conversa atual é evidência disponível no chat; nenhuma exportação ou captura foi fabricada.
