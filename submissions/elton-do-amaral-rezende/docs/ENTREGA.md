# Entrega e revisão

A aplicação está hospedada com acesso público, sem login, autorizado pelo candidato em 01/10/2026. A publicação não envia candidatura. O [README da raiz](../README.md) segue o template oficial; o funcionamento local está no [guia de instalação e uso](SETUP.md) e foi testado em uma pasta no formato de submissão. O GitHub do candidato é [MunhozVs](https://github.com/MunhozVs/).

## Revisar o produto

A primeira visita abre Zane Levy. Para repetir a revisão original, escolher Darcel Schlecht, abrir a missão 7, conferir posição e fatores, copiar a orientação, concluir, adiar, desfazer no histórico e recarregar. Trocar de vendedor para verificar isolamento. O índice não é chance de fechamento; valores são preços de catálogo em USD. A avaliação desfavorável aparece em Como priorizamos.

## Preparação do PR oficial

Regras consultadas em 01/10/2026: [CONTRIBUTING](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/CONTRIBUTING.md), [guia](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/submission-guide.md) e [template](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/templates/submission-template.md).

Antes de enviar:

- O README está preenchido com Elton do Amaral Rezende, GitHub MunhozVs e LinkedIn, assim como solução, resultados, recomendações, limitações, uso de IA e evidências. Confirmar o prazo individual antes de enviar.
- Criar a branch no fork e colocar a solução dentro de submissions/ com a pasta do candidato. O PR deve alterar somente essa pasta e usar o título exigido pelo regulamento.
- Transportar código, CSVs, README, docs, Referencias e process-log. Preservar o .gitignore dentro da pasta da submissão. Não transportar .git, node_modules, dist, coverage, caches, .work ou artefatos gerados.
- A pasta .openai/ e o helper scripts/build-for-hosting.mjs são específicos desta hospedagem e podem ficar fora do pacote oficial. Não são necessários para executar os comandos de solution/. O identificador da hospedagem não é uma credencial.
- Confirmar a autoria Git antes do commit no fork. Os commits locais iniciais herdaram o nome de configuração “Your GitHub Username”; não reescrevemos o histórico já publicado nesta revisão.
- O avaliador pode abrir a aplicação pública sem login ou executar localmente. A verificação HTTP sem credenciais retornou 200 e o HTML da aplicação em 01/10/2026.
- Usar o diário como narrativa de processo e as capturas como evidência da aplicação. Narrativa escrita é um formato aceito pelo guia; chat-exports/ não contém exportações reais. Acrescentar conversas exportadas apenas se existirem, sem fabricar evidências.

Não foi criado ou enviado PR de recrutamento. Essas pendências pertencem à montagem da candidatura, não são placeholders no funcionamento do app.
