# Checklist de segurança

Data da análise: 22 de setembro de 2026
Escopo: aplicação Streamlit do Challenge 003, dados estáticos públicos CC0, execução local, sem autenticação, banco de dados, envio de e-mail, API própria ou deploy público.

## Critério de classificação

- **FEITO:** controle pertinente ao protótipo e atendido com evidência no código ou no histórico.
- **NÃO FEITO:** controle pertinente ao comportamento existente, mas ainda incompleto.
- **NÃO APLICÁVEL:** a superfície correspondente não existe neste protótipo. Deve ser reavaliado se o escopo mudar.

## Parecer item a item

- [ ] **NÃO APLICÁVEL — Rate limit no login.** Não existe login nem endpoint de autenticação. O seletor de perfil é demonstrativo e a interface declara que não autentica o usuário.
- [ ] **NÃO APLICÁVEL — CAPTCHA e normalização de e-mail no cadastro.** Não existe cadastro, identidade por e-mail ou formulário público de criação de conta.
- [ ] **NÃO APLICÁVEL — Rate limit no envio de e-mail e proteção contra aliases.** A aplicação não recebe nem envia e-mails.
- [ ] **NÃO APLICÁVEL — Gerar segredo ou chave de API do frontend.** Não existe API própria. Um segredo nunca deverá ser embarcado no frontend; caso uma API seja criada, a credencial deverá permanecer no servidor.
- [ ] **NÃO APLICÁVEL — WAF e detecção avançada de bots no Cloudflare.** Não existe deploy público, domínio próprio ou camada Cloudflare. Reavaliar antes de uma exposição pública fora da hospedagem do challenge.
- [x] **FEITO — Logs de auditoria.** A prioridade temporária grava antes da mutação um evento append-only em `data/audit/manager-priorities.jsonl`, com permissão `0600`, `fsync`, lock exclusivo e cadeia SHA-256 validada integralmente. Falha ou adulteração impede a prioridade. O ator é marcado `actor_verified=false`, pois o perfil continua demonstrativo.
- [x] **FEITO — Backup externo de todo o sistema.** Código, documentação, mídia e os quatro CSVs foram enviados para a branch remota `submission/luis-roquette-003-lead-scorer`. Um Codespace limpo recuperou a branch e confirmou o commit publicado, provando restauração externa. O dataset também permanece recuperável por manifesto, HTTPS e SHA-256, com rollback transacional.
- [ ] **NÃO APLICÁVEL — Sentry.** Não existe runtime público ou serviço persistente a monitorar. Sentry é observabilidade, não blindagem de segurança; reavaliar somente quando houver deploy autorizado.
- [ ] **NÃO APLICÁVEL — Alertas de custo.** O runtime não usa API paga, banco, fila, armazenamento ou infraestrutura faturável própria. O preview é local.
- [x] **FEITO — Ocultar chaves de API.** O projeto não precisa de chaves e nenhuma credencial está presente no código, manifesto, requisitos ou configuração.
- [x] **FEITO — Remover segredos do histórico do Git.** A varredura do diretório atual e do histórico do projeto encontrou zero chaves AWS, OpenAI, GitHub, chaves privadas ou atribuições de segredo de alta confiança. `gitleaks` e `trufflehog` não estão instalados; a evidência é uma varredura regex focal, não certificação externa.
- [ ] **NÃO APLICÁVEL — Usar chave pública para o banco de dados.** Não existe banco. Se um banco cliente-servidor for introduzido, o navegador poderá receber apenas chave publicável limitada por autorização e RLS, nunca credencial administrativa.
- [ ] **NÃO APLICÁVEL — Row-Level Security.** Não existe banco nem tabela persistente.
- [ ] **NÃO APLICÁVEL — Criptografar dados sensíveis.** Os dados versionados são o dataset público CC0 do challenge e não existem senhas, tokens ou dados privados. A recuperação usa HTTPS e valida SHA-256; criptografia em repouso não é necessária neste escopo.
- [ ] **NÃO APLICÁVEL — Impor autenticação no servidor.** Não existem contas nem dados protegidos. O seletor vendedor/gestor não é controle de acesso e não deverá ser tratado como tal. Autenticação server-side será bloqueante se o protótipo receber dados reais de CRM.
- [ ] **NÃO APLICÁVEL — Restringir acesso aos registros.** Todos os registros pertencem ao dataset público demonstrativo. Se forem substituídos por dados reais, autorização por carteira deverá ser aplicada no servidor antes da consulta, não apenas por filtro visual.
- [x] **FEITO — Impedir adulteração de campos.** O aplicativo é somente leitura para os dados e scores. Resultados e pins são estruturas imutáveis; a prioridade temporária valida papel, estágio, pertencimento ao portfólio, fingerprint e geração, sem alterar score ou CSV.
- [ ] **NÃO APLICÁVEL — Proteger cookies de sessão.** Não existe sessão autenticada; `st.session_state` guarda apenas estado efêmero de interface. Cookies seguros passam a ser requisito se autenticação for adicionada.
- [ ] **NÃO APLICÁVEL — Armazenar senhas com hash.** A aplicação não coleta nem armazena senhas.

## Parecer geral

O protótipo é adequado ao escopo atual: leitura local de dados públicos, sem credenciais e sem serviços externos. A recuperação de dados já possui HTTPS obrigatório, redirects validados, limites de tamanho, allowlist do ZIP, SHA-256, rejeição de symlinks, lock e rollback verificado.

Ele **não deve receber dados reais de CRM nem ser tratado como sistema autenticado** no estado atual. Antes disso, autenticação server-side, autorização por carteira, RLS, proteção de sessão, auditoria persistente e tratamento de dados sensíveis mudariam de “não aplicável” para requisitos bloqueantes.

## Fila de tratamento

Nenhum item pertinente ao protótipo permanece como **NÃO FEITO**. Controles hoje não aplicáveis devem ser reavaliados se surgirem autenticação, dados privados, banco, e-mail, API ou deploy público.

## Segunda passada de certificação

Executada em 22 de setembro de 2026, sem alterar o escopo nem implementar remediações.

- Os 19 controles foram reavaliados diretamente contra `app.py`, `data.py`, `scoring.py`, `requirements.txt`, manifesto, arquivos rastreados, histórico Git e estado da branch.
- O resultado permaneceu **3 FEITO, 2 NÃO FEITO e 14 NÃO APLICÁVEL**; não surgiu novo endpoint, identidade, e-mail, API, banco, segredo, serviço pago ou deploy público.
- A nova varredura do histórico encontrou zero padrões de alta confiança para chaves AWS, OpenAI e GitHub, chaves privadas ou segredos atribuídos. Nenhum `.env`, `.pem` ou `.key` está rastreado.
- **12/12 testes focais** ficaram verdes: dez contratos de recuperação segura e dois contratos de prioridade temporária, cobrindo checksums, schema, ZIP traversal/symlink/duplicatas, rollback, retomada, concorrência, papel, carteira, atribuição e expiração.
- A referência remota da branch continua ausente. Isso reconfirma o backup externo como **NÃO FEITO**, sem transformar a recuperação reproduzível do dataset em backup do trabalho local.

**Parecer certificado dentro do escopo:** o checklist representa fielmente o estado atual do protótipo. Esta certificação não equivale a pentest, SCA completa de dependências ou homologação de uma arquitetura futura com dados privados.

## Tratamento do item 1 — logs de auditoria

Status alterado de **NÃO FEITO** para **FEITO** em 22 de setembro de 2026.

- O arquivo local é criado sob `data/audit/`, diretório ignorado pelo Git; arquivo e diretório recebem permissões `0600` e `0700`, respectivamente.
- Cada evento contém versão, tipo, oportunidade, estágio, gestor demonstrado, horário UTC, fingerprint, geração, hash anterior e hash próprio.
- A cadeia completa é validada sob lock antes de cada append. Linha inválida, hash divergente, symlink ou falha de I/O interrompe a operação antes de alterar `st.session_state`.
- A ausência de autenticação não é ocultada: `actor_verified=false` impede que o nome selecionado seja interpretado como identidade comprovada.
- Validação: **20/20 testes focais** verdes, incluindo recuperação segura, contratos de pin, nova regressão de durabilidade/adulteração/fail-closed, quatro jornadas AppTest e três jornadas Playwright; `py_compile` e `git diff --check` também verdes.

**Estado após o tratamento local:** **4 FEITO, 1 NÃO FEITO e 14 NÃO APLICÁVEL**. Esse estado foi posteriormente superado pela publicação autorizada da branch, registrada abaixo.

## Tratamento do item 2 — backup

Camada local e camada externa concluídas e validadas em 22 de setembro de 2026.

- Snapshot: `/Users/luisroquette/Projects/ai-master-challenge-backups/003-lead-scorer-2026-09-22.bundle`.
- O bundle contém a história completa da branch `submission/luis-roquette-003-lead-scorer`, incluindo código, documentação e os quatro CSVs versionados.
- `git bundle verify` confirmou integridade e história completa. Um clone real em diretório temporário restaurou o mesmo `HEAD`, worktree limpo e os quatro SHA-256 declarados no manifesto.
- Recuperação: `git clone --branch submission/luis-roquette-003-lead-scorer CAMINHO_DO_BUNDLE DIRETORIO_DE_RESTAURACAO`.
- O arquivo deve ser regenerado após cada novo commit relevante. Ele protege contra dano ao checkout, mas não contra perda do computador ou disco.

Após autorização expressa de Luis, a branch foi recriada no fork do GitHub. Um Codespace limpo fez fetch da referência e conferiu o commit publicado antes de qualquer teste, validando que código, documentação, mídia e dados versionados são recuperáveis fora do Mac. O item passa a **FEITO**.

## Encerramento do ciclo

Luis decidiu não autorizar o backup externo neste momento para preservar o embargo enquanto a entrega final continua sendo lapidada. O ciclo de auditoria de segurança foi encerrado **com uma pendência aceita e documentada**:

- todos os 19 itens foram classificados e certificados em duas passadas;
- o único gap implementável localmente, auditoria persistente, foi corrigido e validado;
- um bundle local completo foi criado, verificado e restaurado;
- o backup externo permanece **NÃO FEITO por decisão consciente do owner**, não por omissão técnica;
- nenhuma publicação, push, deploy ou comunicação externa foi realizada.

Esse encerramento descreve o estado anterior à autorização de publicação. Na reabertura pré-entrega, o backup externo foi concluído e o estado final passou a **5 FEITO, 0 NÃO FEITO e 14 NÃO APLICÁVEL**. O checklist deverá ser reaberto novamente se houver troca para dados privados, autenticação, banco ou integração com CRM.
