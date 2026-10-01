# Auditoria antes da submissão — 01/10/2026

Revisão do produto, dos testes, da reprodução local e dos arquivos versionados. O objetivo foi encontrar problemas concretos, não certificar ausência absoluta de bugs.

## Resultado

39 testes em cinco arquivos passaram. Uma pasta nova em `.work/audit-clean/submissions/revisao/` recebeu somente os arquivos versionados necessários e reproduziu `npm ci`, `prepare:data`, `evaluate`, `npm test` e `npm run build`, incluindo a verificação de tipos. Não havia dependências, dist ou JSONs gerados antes da instalação. O build de produção foi aberto em uma origem local separada dos registros do usuário.

A preparação e a avaliação geraram os mesmos hashes dos seis JSONs do projeto principal. Foram confirmadas 8.800 oportunidades, 2.089 abertas, 1.480 aliases e nenhum vínculo desconhecido. A avaliação continua com 4.726 históricos, 2.409 candidatos, 559 Won, 376 Lost e 1.474 censurados; a regra e as métricas não foram alteradas na revisão.

## Correções e verificações

- Corrigido um caso limite de consulta ao histórico: nomes como `constructor`, `toString` ou `__proto__` podiam ser confundidos com propriedades herdadas de um objeto JavaScript. A pontuação usava a média geral, mas a explicação não identificava corretamente a falta de histórico específico. Um teste reproduziu a falha antes da correção. Agora só consideramos chaves próprias do histórico.
- O cálculo H passou a ler os pesos de `SCORING_RULE.historicalWeights`, eliminando uma cópia dos mesmos números dentro do motor. Os valores e resultados foram preservados.
- Removido `DailyQueueState`, contrato antigo sem consumidores. A fila utiliza os contratos efetivos `DayState` e `SellerState`.
- Atualizado o índice do process log, que ainda descrevia somente a base sem dados. Os registros históricos de sete e 31 testes foram preservados com seu contexto; não são a contagem atual.
- Acrescentados testes para datas inexistentes, nomes especiais no histórico, catálogo sem variação, ciclo zero, avaliação vazia, poucos candidatos, carteira vazia e exportação CSV da carteira correta. Mocks de clipboard/storage nos testes simulam falhas reais dessas APIs; não substituem os CSVs nem o motor do produto.
- Mantidos os controles já testados: invariância a resultados futuros, censura, seleção sem concluir, isolamento por vendedor/dataset, lotes sem repetição, adiamento, desfazer, meta, sequência, restauração e virada do dia.

## Git, dependências e placeholders

Verificados os 74 caminhos versionados anteriores à revisão e os cinco commits existentes. Nenhum node_modules, dist, coverage, cache, .work, .env, chave privada ou arquivo gerado de execução estava versionado. A busca por padrões de tokens e chaves privadas no histórico não encontrou correspondências; isso é uma inspeção por padrões, não uma garantia universal sobre todos os formatos de segredo.

`npm audit --json` e a instalação limpa retornaram zero vulnerabilidades conhecidas. O aviso de depreciação de `whatwg-encoding` é de uma dependência transitiva de testes, sem alerta de vulnerabilidade. Não trocamos versões apenas para eliminar esse aviso.

Não foi encontrado stub de função ou funcionalidade central simulada no app. `provenance.example.json` é um exemplo identificado; a execução lê a proveniência real preenchida e os CSVs incluídos. Arquivos .gitkeep apenas reservam diretórios. A pasta chat-exports/ não contém conversas exportadas, e a documentação não diz que contém.

`.openai/hosting.json` contém o identificador do site e o diretório estático; não contém token. A configuração e o helper de hospedagem são dispensáveis no pacote oficial. O diário não foi alterado nesta auditoria.

## Navegador e evidências

No build de produção reconstruído: primeira visita com Zane, uma missão expandida e zero ações; missão 7 com seis cards acima e três abaixo; foco no título; concluir, recarregar preservando a conclusão, adiar, desfazer e desfazer pelo histórico. Os registros criados pela revisão foram revertidos. Console consultado sem erros. Em viewport de 390 px, documento/corpo não excederam a largura disponível.

Capturas reais: [desktop](../process-log/screenshots/audit-desktop.jpg) e [celular](../process-log/screenshots/audit-mobile.jpg). As capturas anteriores continuam como evidências das versões anteriores. Não existe suíte automatizada de navegador nem certificação formal de acessibilidade.

## Limitações que continuam explícitas

O score não demonstrou superioridade à referência aleatória na taxa entre negócios resolvidos; não promete probabilidade nem aumento de conversão. Há censura e proxies sem snapshots. Ações são declarações locais, sem autenticação ou atualização de CRM; abas e dispositivos não sincronizam em tempo real. Os dados de demonstração são históricos e as empresas são fictícias. O JavaScript contém os dados estáticos, aproximadamente 255 kB gzip, e gera aviso de chunk grande.

## Antes de enviar o PR

O software passou pelas verificações desta revisão. A candidatura ainda precisa ser montada no fork: perfil e README conforme o template, somente arquivos dentro da pasta do candidato e título do PR conforme as regras. O nome de autoria Git herdado nos commits locais é “Your GitHub Username”; ajustar a identidade antes do commit no fork, sem reescrever silenciosamente o histórico publicado. O link do site é privado; definir um acesso viável ao avaliador ou fornecer o setup local, sem presumir que ele verá o link.

Regras e formatos conferidos nas fontes oficiais: [Challenge 003](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/challenges/build-003-lead-scorer/README.md), [CONTRIBUTING](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/CONTRIBUTING.md), [guia de submissão](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/submission-guide.md) e [template](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/templates/submission-template.md). O guia aceita narrativa escrita como evidência de processo; o diário cumpre esse formato. Detalhes da montagem: [ENTREGA.md](ENTREGA.md).
