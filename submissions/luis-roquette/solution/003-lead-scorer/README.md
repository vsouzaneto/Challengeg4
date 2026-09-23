# Lead Scorer explicável

Aplicação Streamlit que prioriza oportunidades `Engaging` e `Prospecting` sem misturar as escalas. O runtime usa somente os quatro CSVs versionados e não chama APIs de IA.

## Verificação canônica

Requer Bash, acesso de instalação durante o preparo e Python 3.11 local. Em GitHub Codespaces, o script instala `uv==0.10.10`, provisiona CPython 3.11 e usa um ambiente descartável.

```bash
bash scripts/preflight.sh
```

O comando instala apenas `requirements.txt`, instala o Chromium correspondente ao Playwright, executa `pip check`, imports, todos os testes TC-01–46, a avaliação real das quatro rotas e uma jornada renderizada do app real. Qualquer gate falha com código diferente de zero. TC-47 é deliberadamente separado.

## Execução local

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m playwright install chromium
.venv/bin/python -m streamlit run app.py --browser.gatherUsageStats=false
```

Abra o endereço exibido pelo Streamlit. A tela começa no portfólio do primeiro vendedor; o contexto gestor abre a equipe e habilita filtros e prioridade temporária.

Cada prioridade temporária confirmada pelo gestor é registrada localmente em
`data/audit/manager-priorities.jsonl`. O arquivo usa permissão `0600`, append com
`fsync` e encadeamento SHA-256. O campo `actor_verified=false` deixa explícito que
o perfil é demonstrativo, não uma identidade autenticada. Se a cadeia estiver
inválida ou o append falhar, a prioridade não é aplicada.

## Recuperação explícita dos dados

```bash
.venv/bin/python data.py recover --manifest data/manifest.json --raw-dir data/raw
```

Esse comando é externo ao startup. Ele baixa a versão 1 declarada no manifesto, valida os quatro checksums e só então promove o snapshot completo. Se uma interrupção preservar o marcador transacional:

```bash
.venv/bin/python data.py recover --resume --manifest data/manifest.json --raw-dir data/raw
```

## Verificação pós-deploy — TC-47

```bash
.venv/bin/python tests/test_app.py live \
  --url 'https://APP.streamlit.app' \
  --revision 'GIT_SHA' \
  --source-digest 'SHA256_DAS_FONTES' \
  --fingerprint 'FINGERPRINT_DADOS_MODELO'
```

Os quatro argumentos são obrigatórios. O verificador exige a identidade completa renderizada e as duas visões ativas; não faz parte do preflight anterior ao deploy.

## Lógica e limites

- `Engaging`: compara regressão logística e gradient boosting nas rotas completa e sem conta. Probabilidade e receita esperada só aparecem se a rota superar os gates temporais; caso contrário, usa prioridade relativa explícita.
- `Prospecting`: usa evidência histórica suavizada e backoff até a base global. Nunca apresenta probabilidade ou receita esperada probabilística.
- Explicações reconstroem a saída real do modelo; ações vêm do playbook determinístico v1. Associação não implica causalidade nem aumento de receita.
- Protótipo de dados estáticos, sem autenticação, escrita no CRM, persistência de pins, monitoramento de drift ou retreino agendado.
- Antes de escala: piloto controlado com vendedores, captura de intervenção e desfecho, auditoria segmentada e recalibração periódica.

Evidência medida e cobertura: [docs/evaluation.md](docs/evaluation.md).
