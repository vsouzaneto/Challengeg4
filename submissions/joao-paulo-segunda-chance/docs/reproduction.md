# Reprodução e roteiro da banca

Estado em 13/10/2026. Concluí a aceitação completa do login e a revisão visual em navegador/celular em 13/10/2026. A etapa de usuários atualizou o banco de acesso e os adaptadores de usuários/assistente, preservando os contratos e fatos de negócio. [Guia de usuários](user_management.md). Os números do diagnóstico escrito referem-se à base original, corte 31/12/2024; o painel calcula a versão e o recorte ativos.

## Leitura e demonstração (aproximadamente 8 minutos)

1. Entrar com conta já provisionada. Mostrar perfil, referência histórica e versão ativa. Para o roteiro completo, usar uma conta administradora ou com todas as permissões descritas no guia.
2. Na visão executiva, separar flag cadastral, cancelamentos e exposição contratual. Mostrar as três prioridades e os limites de uso/satisfação.
3. Em “Investigar por exposição”, abrir uma das contas com flag sem cancelamento. Conferir contratos, eventos e tickets, incluindo nota ausente e elegibilidade. Não inferir data ou motivo ausentes.
4. Abrir o formulário de decisão e calcular uma prévia de conta ou segmento. Mostrar responsável, prazo e evidência congelada; cancelar a demonstração se não houver intenção de gravar.
5. No assistente, perguntar pelo MRR contratual de um setor. Conferir definição, corte e versão. “Explorar contas deste recorte” abre a população exploratória, não promete reproduzir ocorrências da métrica. Reabrir o histórico para mostrar persistência.
6. Em Dados/qualidade, explicar a prévia, os 89 resultados e o versionamento. Não publicar outro arquivo somente para a apresentação. Encerrar com as três ações do diagnóstico e as limitações.

Não há modelo preditivo nem promessa de receita recuperada. PR da segunda chance continua separado da PR #66 e aguarda autorização específica.

## Testes locais, sem gravação no ambiente compartilhado

Partir da pasta `submissions/joao-paulo-segunda-chance`. Requer Python 3.12 e Node 22.13 ou superior. Os comandos abaixo não publicam versão nem gravam decisões.

```sh
python -m pip install -r requirements-audit.txt
python -m unittest discover -s tests -v
python scripts/audit_data.py --data-dir /caminho/fontes --output-dir /caminho/relatorios
CHALLENGE_DATA_DIR=/caminho/fontes CHALLENGE_AUDIT_REPORT=/caminho/relatorios/audit_results.json node --test web/tests/*.test.mjs
cd web/frontend
npm ci
npm run check
npm run test:ui
npm run build
```

São necessárias as cinco fontes exatas do manifesto para comparar os 89 resultados. Sem elas o teste de referência pode ser ignorado; não registrar esse skip como equivalência aprovada. Não versionar os CSVs, relatórios por conta, senhas ou chaves privilegiadas. `npm run dev` inicia o frontend portátil para validação manual; ele aponta ao backend dedicado, portanto operações de escrita na interface são reais.

## Instalação em outro ambiente

1. Seguir a ordem das migrações e carga inicial em [foundation_status.md](foundation_status.md).
2. Aplicar as migrações web, escopos, autenticação e assistente na ordem de [web/README.md](../web/README.md). Aplicar também a migração de [gestão de usuários](user_management.md). Gerar os quatro pacotes pelos scripts canônicos e implantar com verificação JWT.
3. Configurar Supabase Auth, contas e memberships protegidos conforme [authentication.md](authentication.md); configurar o Secret OpenAI no servidor conforme [assistant.md](assistant.md). Não reutilizar identidades ou segredos do ambiente original.
4. Ajustar URL/chave pública do frontend para o próprio projeto. A chave privilegiada permanece exclusivamente no backend. Vite é a distribuição portátil; o site usa Vinext com as mesmas telas, estilos e adaptadores.
5. Validar login/perfis, erros, escrita, refresh e logout no novo ambiente. Minha aceitação no ambiente original não se transfere automaticamente à nova instalação.

Migrações não são um script indiscriminado de reset. Os testes SQL têm pré-condições e alguns representam fases anteriores à ativação. Ler cada arquivo antes de executá-lo; fixtures locais isoladas não devem ser aplicadas no projeto compartilhado.

## Verificações HTTP e limites

`python web/tests/http_auth.py --guards-only --legacy-blocks` e `python web/tests/http_assistant.py` verificam bloqueios anônimos atuais sem escrever dados de negócio. `http_auth.py --email EMAIL --expect-role administrator` (ou `super_admin`/`user`) solicita senha localmente por getpass; não transmitir senha no chat ou Git.

`python web/tests/http_users.py` verifica quatro bloqueios sem autenticação válida. O guia de usuários inclui o teste SQL em banco local isolado; suas fixtures nunca devem ser aplicadas no ambiente compartilhado. Cadastro e redefinição reais ainda precisam de validação com uma conta legítima.

Os scripts `http_import.py`, `http_decisions.py`, `http_scopes.py` e `http_smoke.py` documentam a fase anterior ao login; não constituem uma suíte autenticada atual. Seus modos de publicação/escrita não fazem parte da rotina acima. Happy DOM usa APIs simuladas: comprova comportamento dos componentes, não aparência no navegador, latência real ou integração com o modelo. A revisão visual em desktop/celular foi concluída em 13/10/2026 e está registrada no [process log](../process-log/documentation_review_2026-10-13.md).
