# Endurecimento do assistente contra prompt injection — 13/10/2026

Autorizei corrigir os caminhos críticos apontados na revisão de segurança, preservando o acesso da conta Raven para a banca e sem abrir PR. O assistente usa GPT-6 Luna e consultas de negócio tipadas; a chave OpenAI e a chave privilegiada do Supabase permanecem somente no servidor.

## Risco observado

O catálogo de setor/país/plano, derivado de dados importados, era concatenado às `instructions` da Responses API. Mensagens anteriores com papel `assistant` voltavam ao modelo. Textos livres das funções `clarify_question` e `unsupported_question` podiam ser exibidos e persistidos; a consulta factual ainda enviava o resultado ao modelo para uma explicação separada. Um teste isolado com resposta sintética comprovou que uma mensagem com link e pedido de credenciais passava pelo caminho de saída e reaparecia no histórico. Isso não foi um teste de indução contra o modelo real nem demonstrou acesso indevido ao banco.

## Mudanças e limites

- As instruções do servidor são fixas. Contexto e catálogo passam como dados em mensagem de usuário separada; categorias são limitadas, e valores com URLs, controles ou instruções comuns são omitidos do catálogo enviado.
- O histórico encaminhado ao modelo contém apenas perguntas anteriores do usuário, sem reutilizar respostas livres do assistente. O histórico armazenado e visível na interface permanece intacto; seguimentos que dependam exclusivamente da formulação de uma resposta anterior podem pedir esclarecimento.
- As funções de esclarecimento/limitação apenas selecionam frases fixas do servidor. Suas mensagens livres não são exibidas nem enviadas como instruções em turnos futuros.
- A resposta factual e os valores continuam vindo da consulta SQL tipada. A segunda chamada para explicação livre foi retirada; o cartão mantém definição e ressalvas do banco. Categorias com indícios de conteúdo hostil recebem rótulo neutro na resposta.
- A autorização por sessão JWT, membership/permissão atual, limites por usuário/workspace e consultas de leitura existentes não foram afrouxados. Prompt injection ainda pode tentar influenciar a escolha de um filtro válido pelo modelo; versão, recorte e evidência seguem visíveis para conferência.
- O valor padrão de `assistant.executions.prompt_version` passa a `1.1.0` para novas execuções; registros anteriores conservam `1.0.0`.

## Verificação

Testes locais adversariais cobrem catálogo malicioso, histórico contaminado, phishing nas mensagens livres, categoria hostil e preservação do cálculo SQL. Os testes do domínio, os 47 casos da interface/adaptadores, TypeScript, sintaxe do pacote Edge e três guardas HTTP anônimos foram conferidos. Não foram criadas identidades fictícias nem importados dados de ataque no Supabase compartilhado. Os testes simulados não constituem prova de que o modelo nunca seguirá uma instrução adversarial.

A implantação publicou `challenge-assistant` ACTIVE v7, SHA256 `8f0b5c1f22d4015822d080b96544e8367c89a67f9d2211d2aa3b46b2d4e24b71`, com `verify_jwt=true`; o site frontend não foi modificado. A conta Raven permanece administradora conforme minha decisão. Não houve alteração de crédito, expiração de token ou gestão de usuários nesta rodada.
