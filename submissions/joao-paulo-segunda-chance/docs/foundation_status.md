# Fundação de dados — implementação

## Estado

Estrutura aplicada no Supabase dedicado e primeira versão de dados publicada. O código desta etapa implementa persistência e processamento; ainda não é o site ou o importador web. Relatórios detalhados e IDs das fontes permanecem fora do repositório público.

## Entregue

- Cinco contextos em schemas privados: acesso, ingestão, domínio canônico, análise e operações.
- Contratos puros de fonte: tipos, obrigatoriedade e nulabilidade, sem dependência de pandas/banco.
- Preservação de bytes exatos dos CSVs em chunks privados, conferida por tamanho e SHA-256. É uma solução de bootstrap para os arquivos pequenos; Storage e binários Excel serão tratados pelo adaptador web.
- Valores originais separados da representação normalizada. Hash de registro é calculado pelo adaptador Postgres sobre JSON canônico, distinto do hash dos bytes do arquivo.
- Manifesto de cinco fontes, identidade por arquivo/linha e tabelas canônicas versionadas.
- IDs conflitantes de uso preservados na origem e no canônico; registros envolvidos são excluídos das medidas temporalmente qualificadas, sem escolha arbitrária de uma linha.
- Snapshots por data de referência, reconciliação, catálogo de qualidade e evidências vinculadas à execução.
- Receita contratual agregada antes dos cruzamentos; exclui trials e não é apresentada como perda prevista.
- Sem cobertura confirmada, queda de uso permanece indeterminada e não gera alerta automático de retenção.
- Versão atual trocada somente após conferência de fontes e snapshots. Falhas preservam publicação anterior.
- Fontes verificadas, manifestações processadas, resultados e evidências finalizados são imutáveis, incluindo troca indevida de parent IDs.
- FK garante que uma evidência não aponte para snapshot de outra execução.
- RLS por membership; usuários não se atribuem cargos. Dados brutos e funções de importação são restritos ao backend.
- Interfaces públicas de leitura com SECURITY INVOKER. Nenhuma chave privilegiada no código.
- Adaptador CLI de importação via RPC e preparação local de payloads ignorados pelo Git.

## SQL aplicado e ordem de reprodução

Aplicar em um projeto dedicado vazio, usando operador autorizado. Cada arquivo representa uma mudança aplicada; não reexecutar cegamente DDL não idempotente.

1. `db/foundation.sql` — estrutura inicial gerada dos contratos.
2. `db/normalized_records.sql` — representação normalizada e política de contratos de backend.
3. `db/ingestion_functions.sql` — carga retomável de bytes/linhas.
4. `db/immutability_hardening.sql` — validação de parents antigos e novos.
5. `db/import_api.sql` — RPCs de backend.
6. `db/promotion_idempotency.sql` — evita reexecutar inserts já materializados e cobre FKs de origem.
7. `db/lineage_indexes.sql` — índices das relações e integridade da execução da evidência.
8. `db/analysis_runtime_guards.sql` — limite de data observada e manifesto processado imutável.

O gerador `scripts/build_foundation_sql.py` reproduz a primeira migração a partir dos templates/contratos. As migrações posteriores permanecem separadas para preservar a sequência de evolução. Alterações futuras precisam de nova migração, não edição retroativa da aplicada.

## Validação

- 26 testes Python aprovados nesta etapa: domínio, contratos e auditoria com fontes sintéticas.
- SQL: existência dos schemas, RLS/grants, membership de leitor vs. não membro, negação de acesso ao raw e APIs privilegiadas.
- SQL: imutabilidade de fonte/versão, data além das fontes rejeitada e candidata incompleta impedida de substituir a publicação.
- Replay verificado em fixture sintética com rollback; publicação já concluída reapresentada sem gerar nova execução.
- Contagens e hashes das fontes reais reconciliados; divergências de churn conferidas independentemente no SQL e no auditor.
- Security Advisors: sem avisos no último retorno. Índices de FK necessários foram criados; avisos informativos de índices novos ainda não usados serão monitorados quando houver tráfego real.

Os testes SQL com fixtures fazem rollback, inclusive das identidades sintéticas de auth. O adaptador REST usa os mesmos RPCs, mas não foi chamado com uma chave privilegiada nesta sessão; a carga foi executada pela conexão autorizada de Supabase.

## Executar localmente

```bash
python -m pip install -r requirements-audit.txt
python -m unittest discover -s tests
python scripts/prepare_initial_import.py --data-dir /pasta/csv --output-dir .work/import
```

Para operação de backend, configurar `SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` em ambiente protegido e executar `scripts/import_to_supabase.py`. Nunca colocar a chave em arquivo versionado ou no navegador. O workspace existente e a data de referência são argumentos explícitos.

## Próximas fases

Interface de diagnóstico, login/provisionamento de usuários reais, upload web CSV/Excel com preview e confirmação, atualização de uma fonte mantendo manifesto completo, decisões/ações com validação de transições e mensuração. O schema de operações está preparado; o workflow de decisão ainda precisa de implementação e testes. Não há PR aberta nem solicitação de revisão.
