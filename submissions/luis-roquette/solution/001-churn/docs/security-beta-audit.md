# Auditoria de segurança — beta local

**Data:** 22/09/2026

**Escopo:** `solution/001-churn` no commit `0a47106`

**Parecer:** apto para beta local, sem bloqueio crítico conhecido.

## Critério

Este beta é um dashboard Streamlit local, estático e somente leitura. Ele não possui login, cadastro, envio de email, API própria, banco de dados, senha, sessão de aplicação, escrita de registros ou chamada paga. A segurança deve acompanhar o risco real: controles inexistentes para superfícies inexistentes não serão simulados.

Um controle passa a ser obrigatório quando a superfície correspondente for criada. Publicação na internet, dados reais, autenticação, escrita, banco ou integrações reabrem esta auditoria.

## Evidências verificadas

- Processo escutando somente em `127.0.0.1:8503`; não exposto à rede local.
- App valida schema, checksums, referências e `analysis_id` antes de renderizar; falha fecha a interface.
- Valores dinâmicos inseridos nos blocos HTML passam por `html.escape`; os demais usos de HTML são templates estáticos.
- Busca no código e no histórico não encontrou padrões de chave, token, senha ou chave privada; GitHub Secret Scanning e Push Protection estão ativos, com zero alertas abertos.
- Consulta OSV das seis dependências fixadas retornou zero vulnerabilidades conhecidas; Dependabot Alerts do repositório está desativado.

## Parecer item a item

| Item solicitado | Beta local | Parecer atual | Gatilho para implementação |
|---|---|---|---|
| Rate limit no login | Não aplicável | Não existe login nem endpoint de autenticação. | Antes de criar login próprio; preferir OIDC gerenciado. |
| CAPTCHA e normalização de email no cadastro | Não aplicável | Não existe cadastro nem coleta de email. | Quando houver cadastro público sujeito a abuso. |
| Rate limit no email e proteção contra aliases | Não aplicável | O sistema não envia email. Bloquear aliases de forma geral também rejeitaria usuários legítimos. | Quando existir envio transacional; limitar por conta, destino normalizado, IP e janela. |
| Gerar segredo e chave API do frontend | Proibido | Segredo no frontend não é segredo. O app não chama API protegida. | Criar segredo apenas no servidor quando uma integração real exigir; frontend recebe somente identificador público. |
| WAF e detecção avançada de bot no Cloudflare | Futuro | Não há domínio público nem origem exposta. | Antes de self-hosting público com endpoints abusáveis. |
| Logs de auditoria | Futuro | Não existem login, mutações ou ações privilegiadas. Diário de engenharia não substitui log de segurança. | Ao adicionar autenticação, escrita, download sensível ou ação administrativa. |
| Backup de todo o sistema | Atendido no beta | Código, dados estáticos e artefatos estão no GitHub; branch remota coincide com o commit auditado. Artefatos são reproduzíveis a partir dos CSVs com checksums. | Dados mutáveis exigirão backup versionado, retenção, restauração testada e cópia fora do provedor primário. |
| Sentry em todos os projetos | Dispensável agora | Adicionaria dependência e telemetria externa a um app local sem operação contínua. | Antes de um beta público persistente, com revisão de dados enviados e alertas úteis. |
| Alertas de custo | Não aplicável | O app não chama APIs pagas, banco ou infraestrutura elástica. | Ao ativar serviço faturável; definir orçamento e alerta antes da primeira chamada. |
| Ocultar chaves de API | Atendido | Não há chaves no projeto. Se surgirem, usar segredo do provedor ou variável de ambiente, nunca Git. | Na primeira integração externa. |
| Remover segredos do histórico Git | Atendido | Nenhum padrão foi encontrado e o Secret Scanning reporta zero alertas. Não se reescreve histórico sem incidente real. | Se houver alerta: revogar/rotacionar primeiro; reescrever histórico somente após avaliar impacto. |
| Usar chave pública para o banco | Não aplicável | Não existe banco. Chave pública não substitui autorização. | Ao adotar banco; cliente recebe apenas chave publicável e toda autorização continua no servidor/RLS. |
| Ativar Row-Level Security | Não aplicável | Não existe banco nem usuário. | Antes da primeira tabela acessível pelo cliente. |
| Criptografar dados sensíveis | Não aplicável no dataset atual | Dataset público e sintético do desafio; não há credencial ou PII real declarada. Transporte local não sai da máquina. | Dados reais exigem minimização, TLS e criptografia em repouso gerenciada pelo provedor. |
| Autenticação no lado do servidor | Não aplicável | Não existe área privada nem backend mutável. | Obrigatório antes de expor dados reais ou ações protegidas; UI nunca decide autorização. |
| Restringir acesso aos registros | Não aplicável no dataset atual | Os registros publicados pertencem ao dataset público e sintético. | Dados reais exigem autorização por usuário/tenant e negação por padrão. |
| Impedir adulteração de campos | Atendido para leitura | Não existe formulário de escrita; artefatos adulterados falham por checksum. | Toda futura mutação deve ignorar campos protegidos do cliente e aplicar allowlist no servidor. |
| Proteger cookies de sessão | Não aplicável | O app não cria login nem cookie de sessão próprio. | Com autenticação: HTTPS, `Secure`, `HttpOnly`, `SameSite` e rotação de sessão, preferencialmente pelo IdP/plataforma. |
| Armazenar senhas com hash | Não aplicável | Nenhuma senha é coletada ou armazenada. | Se autenticação local se tornar inevitável; preferir IdP. Nunca criar armazenamento caseiro de senha. |

## Controles indispensáveis do beta

1. **Manter execução local:** bind em loopback e sem publicação acidental.
2. **Manter segredos fora do Git:** Secret Scanning e Push Protection já cobrem o repositório; qualquer credencial futura deve usar o cofre do provedor.
3. **Preservar restauração:** GitHub guarda o snapshot; `make reproduce` reconstrói artefatos e `make check` verifica igualdade.
4. **Reavaliar antes de mudar o risco:** internet pública, dados reais, autenticação, banco, escrita ou API paga bloqueiam a entrega até nova auditoria.

## Lacunas aceitas no beta

- Dependabot Alerts está desativado. A consulta pontual ao OSV ficou verde, mas não substitui monitoramento contínuo. Ativar antes de hospedagem pública persistente.
- Não há Sentry nem log de auditoria persistente. Como não há operação contínua ou mutação, o custo supera o benefício nesta fase.
- GitHub é a única cópia remota documentada. Adequado para código e dados reproduzíveis do beta; inadequado para futuro dado operacional mutável.

## Recuperação

```bash
git clone https://github.com/luisroquette/ai-master-challenge.git
git checkout work/001-ceo-answer
cd submissions/luis-roquette/solution/001-churn
make setup
make reproduce
make check
make app
```

O manifesto guarda SHA dos arquivos brutos e dos 14 payloads. Se um artefato quebrar, ele deve ser reproduzido; não editado manualmente. O commit auditado permanece recuperável em `origin/work/001-ceo-answer`.

## Fontes primárias

- Streamlit: [gestão de segredos](https://docs.streamlit.io/deploy/concepts/secrets) e [autenticação OIDC](https://docs.streamlit.io/develop/concepts/connections/authentication).
- GitHub: [Secret Scanning](https://docs.github.com/en/code-security/concepts/secret-security/secret-scanning) e [remoção de dados sensíveis](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).
- Cloudflare: [rate limiting no WAF](https://developers.cloudflare.com/waf/rate-limiting-rules/).
- OSV: [banco aberto de vulnerabilidades](https://osv.dev/).

## Decisão

Nenhuma implementação adicional é indispensável para este beta local. Criar login, CAPTCHA, chaves, banco, RLS, Sentry ou WAF agora aumentaria superfície e manutenção sem reduzir risco real. A auditoria deve ser reaberta antes de qualquer publicação persistente ou troca do dataset sintético por dados reais.
