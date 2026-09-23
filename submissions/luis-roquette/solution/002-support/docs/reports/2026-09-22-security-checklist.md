# Check de segurança — Support Decision Copilot

Data: 2026-09-22
Escopo: código, configuração e histórico Git da solução `002-support`; deploy público
Streamlit observado. Nenhuma configuração privada do provedor foi presumida.

## Parecer geral

**Risco atual: alto para uso operacional; aceitável somente como demo pública sem dados
reais.** A solução foi construída como protótipo offline/fail-closed, não como sistema
multiusuário. O código agora bloqueia decisões e registros anônimos, mas o IdP ainda não
está configurado e o armazenamento continua efêmero e sem backup.

## Checklist

| # | Controle | Estado | Risco | Parecer |
|---:|---|---|---|---|
| 1 | Rate limit no login | Pendente no IdP | Alto | O fluxo OIDC foi preparado, mas o provedor ainda não está configurado. Rate limit deve ser aplicado no IdP e na borda, sem inventar contador local por processo. |
| 2 | CAPTCHA + normalização de e-mail no cadastro | Não aplicável hoje | — | Não existe cadastro nem e-mail de usuário. CAPTCHA só após abuso mensurável; normalização precisa preservar identidade do provedor. |
| 3 | Rate limit de e-mail e defesa contra alias | Não aplicável hoje | — | Não há envio de e-mail. Futuro limite deve usar conta, IP, destino canônico e janela temporal; alias não pode criar cota nova. |
| 4 | Segredo e chave API no frontend | Rejeitado como desenho | Crítico se feito | Frontend público não guarda segredo. Usar segredo apenas no servidor; frontend recebe somente identificador público com escopo mínimo. |
| 5 | WAF e detecção avançada de bots (Cloudflare) | Ausente | Médio | Deploy usa domínio do Streamlit; nenhum WAF/bot rule próprio foi encontrado. Avaliar proxy/domínio controlado somente após autenticação. |
| 6 | Logs de auditoria | Parcial | Alto | SQLite registra decisões sanitizadas, versões e timestamps. Faltam ator autenticado, login/falha, leitura, export, administração, IP/UA protegido, retenção e trilha imutável central. |
| 7 | Backup e recuperação | Adiado; sem estado operacional | Aceito no protótipo; crítico antes de escrita | Sem OIDC, visitantes não criam o SQLite. O CSV demonstrativo está versionado e os artefatos são reproduzíveis. Banco durável, retenção, backup automático e restore testado bloqueiam qualquer ativação operacional. |
| 8 | Sentry | Ausente | Médio | Nenhum SDK/DSN/configuração. Antes de instalar, definir redaction para não enviar texto de tickets, PII ou segredos. |
| 9 | Alertas de custo | Ausente / baixa exposição atual | Baixo | Não há API paga; treino é local no boot. Faltam alertas do provedor e limites de CPU/storage/reboot. |
| 10 | Ocultar chaves de API | Verificado por ausência | Baixo hoje | Nenhuma credencial foi encontrada. `.env`, `.env.*` e `.streamlit/secrets.toml` são ignorados; o exemplo contém somente placeholders. |
| 11 | Remover segredos do histórico Git | Nenhuma remoção necessária | Baixo hoje | A varredura restrita ao Challenge 002 encontrou somente placeholders no commit que criou o exemplo de secrets. Scanner especializado será obrigatório se uma credencial real for introduzida. |
| 12 | Chave pública para banco | Não aplicável | — | O banco é SQLite local e não usa chave. Em banco remoto, chave pública não substitui autorização; credencial privilegiada fica somente no servidor. |
| 13 | Row-Level Security | Não aplicável hoje | Crítico numa migração multiusuário | SQLite não oferece RLS e não há tenants/usuários. Banco remoto deve negar por padrão e testar políticas por organização e papel. |
| 14 | Criptografia de dados sensíveis | Parcial | Alto | A aplicação sanitiza PII e pretende não persistir dado sensível, mas o SQLite não tem criptografia de aplicação nem chave gerenciada. TLS/criptografia do provedor não foram verificados. |
| 15 | Autenticação no servidor | Implementada no código; IdP pendente | Alto até configurar | OIDC nativo valida identidade no servidor e exige allowlist exata de issuer + subject. Sem secrets, ações ficam bloqueadas. Falta cadastrar o cliente no IdP e configurar o deploy. |
| 16 | Restringir acesso aos registros | Implementado para decisões | Médio residual | Visitante anônimo não cria, lista nem exporta o SQLite. Diagnóstico e fila sanitizada continuam públicos por decisão de produto; ainda não existem papéis ou organizações. |
| 17 | Impedir adulteração de campos | Parcial forte | Médio residual | SQL parametrizado, validação fechada, UUID idempotente e schemas reduzem adulteração. Mutações anônimas foram bloqueadas; ainda falta vincular o ator ao evento imutável. |
| 18 | Proteger cookies de sessão | Não verificável / sem sessão de auth | Alto ao adicionar auth | A aplicação não emite cookie de autenticação próprio. Flags `Secure`, `HttpOnly`, `SameSite`, rotação, expiração e CSRF devem ser verificadas quando houver sessão. |
| 19 | Hash de senhas | Não aplicável | — | Não há senha local. Preferir IdP/OIDC; se senha existir, usar Argon2id com parâmetros versionados, salt automático e proteção contra credential stuffing. |

## Ordem de tratamento

1. **P0 — configurar a fronteira:** cadastrar IdP, guardar secrets e validar login real.
2. **P0 — persistência:** banco durável, backup automático, retenção e restore testado.
3. **P1 — auditoria:** ator, evento, alvo, resultado e correlação em log append-only com
   redaction e acesso restrito.
4. **P1 — observabilidade:** Sentry com scrubbing e alertas de disponibilidade/custo.
5. **P2 — borda:** rate limits, WAF/bot management, CAPTCHA somente nos fluxos que
   realmente existirem.

## Evidência examinada

- `deploy_app.py`: bootstrap público, sem autenticação ou middleware de autorização.
- `src/support_copilot/store.py`: SQLite transacional, validação, SQL parametrizado,
  idempotência e export; sem identidade, criptografia ou backup.
- `.gitignore`: `.env`, `.env.*`, `.streamlit/secrets.toml`, SQLite e runtime são ignorados.
- `.streamlit/config.toml`: somente telemetria, watcher e modo headless.
- Git atual e histórico da pasta: nenhum segredo reconhecido pelos padrões executados;
  varredura especializada ainda pendente.

## Gate para produção

Não usar dados reais nem decisões operacionais antes de configurar o IdP e fechar o P0
de persistência. O protótipo público
deve continuar limitado a dados sanitizados de demonstração. Cada correção futura exige
teste de regressão, evidência no diário e nova medição de risco residual.

## Decisão de minimalidade para a avaliação

Somente três frentes são indispensáveis no protótipo atual e foram tratadas:

1. **Fronteira fail-closed:** visitante não grava, lê decisões nem exporta estado local.
2. **Ausência de estado operacional:** sem escrita, backup não é apresentado como garantia;
   armazenamento durável e restore bloqueiam a futura ativação do OIDC.
3. **Higiene de credenciais:** nenhum segredo real foi encontrado no checkout ou no
   histórico do Challenge 002; arquivos sensíveis estão ignorados.

Os demais controles permanecem condicionais: serão implementados somente quando surgir a
superfície correspondente. Isso inclui login ativo, cadastro, e-mail, dados reais, banco
remoto, domínio próprio, API paga ou operação multiusuário. Para a avaliação pública e
somente leitura, não há outro código de segurança indispensável.

## Tratamento 01 — autenticação e autorização

- Estado: publicado em modo fail-closed; configuração do provedor deliberadamente
  adiada durante a avaliação do protótipo.
- Identidade: OIDC nativo do Streamlit, sem senha local e sem token exposto.
- Autorização: allowlist simultânea de `iss` e `sub`; e-mail/alias não concede acesso.
- Falha segura: sem IdP, segredo ou allowlist, mutações, leitura e export ficam desativados.
- Regressão: modo anônimo não cria SQLite; quatro ações ficam desabilitadas; issuer ou
  subject divergente é rejeitado.
- Evidência publicada: commit `0f98402c1108c5a65d3617a27b5edf9981ad2f58`; página
  executiva pública; fila anônima com quatro ações e dois campos desabilitados; página de
  evidências sem leitura de decisões ou export operacional.
- Validação: `50` testes locais e Ruff verdes. O preflight remoto não ficou verde porque
  o semáforo global de Codespaces permaneceu ocupado; a exceção por congestionamento foi
  registrada, sem ocultar o gate ausente.
- Risco residual: alto para uso operacional até cadastrar o cliente OIDC no IdP,
  configurar os secrets no Streamlit Cloud e preencher as allowlists de `iss` e `sub`.
- Decisão de entrega: não exigir login do avaliador. A superfície pública fica restrita a
  diagnóstico e artefatos sanitizados; escrita, leitura de decisões e export operacional
  permanecem indisponíveis. OIDC volta a ser bloqueador antes de dados reais ou operação.
- Próxima ativação: instalar `Authlib>=1.3.2`; criar o cliente no Google Identity — ou no
  Microsoft Entra ID se o ambiente corporativo usar Microsoft 365 — e armazenar todas as
  credenciais somente no cofre do provedor.

## Tratamento 02 — backup e recuperação

- Estado: conscientemente adiado enquanto o protótipo permanecer sem escrita operacional.
- Evidência: modo anônimo não cria `data/runtime/decisions.sqlite3`; o demonstrativo
  sanitizado `evidence/decisions-demo.csv` está versionado; artefatos são reproduzíveis.
- Decisão: não tratar cópia de SQLite efêmero como backup. Não existe dado operacional
  mutável no deploy atual.
- Gate obrigatório para ativar OIDC: armazenamento durável gerenciado, retenção definida,
  backup automático, runbook e teste de restauração com evidência.
- Risco residual: aceito somente para avaliação pública em modo fail-closed; crítico para
  produção, piloto com operadores ou dados reais.

## Tratamento 03 — credenciais e histórico Git

- Estado: concluído para o escopo atual; nenhuma credencial real existe no protótipo.
- Checkout: nenhum padrão conhecido de token, chave privada, credencial cloud ou JWT foi
  encontrado nos arquivos do Challenge 002.
- Histórico: o único commit candidato adicionou `.streamlit/secrets.example.toml`; todos
  os valores sensíveis são placeholders `SET_IN_STREAMLIT_CLOUD`.
- Proteção: secrets reais permanecem fora do Git por regras explícitas de ignore e devem
  existir somente no cofre do provedor.
- Decisão mínima: não instalar scanner nem reescrever histórico sem segredo confirmado.
  Scanner dedicado vira gate quando a primeira credencial real for criada.
