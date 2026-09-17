# Support Intelligence

Um sistema local de Inteligência de Suporte com seis lentes: diagnóstico, estratégia de automação, laboratório de tickets, Copilot, rede semântica e centro de comando. A rota **O Início** orienta a demonstração para pessoas não técnicas. A documentação-base foi concluída antes do início da implementação, conforme solicitado.

- [Documentação, spec de onboarding e seis specs das lentes](docs/00-indice.md).
- [Plano — 10 sprints, 40 fases + onboarding e checkpoints](docs/02-plano-de-implementacao.md).
- [Dados e limitações](docs/03-dados-e-metricas.md).
- [Validação e roteiro executivo](docs/05-validacao-demo-processo.md).
- [Resultados técnicos medidos](docs/06-resultados-tecnicos.md).

## Executar localmente

Pré-requisitos: Python 3.12, Node.js compatível com o Vite e pnpm 10. Executar a partir deste diretório. O ambiente desta entrega já está preparado em `.venv`; `artifacts/v1/catalog.sqlite3` é a fonte sanitizada dos tickets e os demais artefatos são índices/modelos derivados.

```sh
.venv/bin/python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Abrir [Support Intelligence local](http://127.0.0.1:8000). O mesmo processo entrega a aplicação e a API local.

Para reproduzir em outro ambiente, com os dois CSVs e assets originais presentes:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python scripts/prepare_data.py
.venv/bin/python scripts/train.py
.venv/bin/python scripts/build_semantic.py
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend run build
.venv/bin/python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

A primeira preparação semântica baixa um encoder público; consultas posteriores usam o modelo local. O lock registra as versões verificadas no macOS Apple Silicon/Python 3.12; outro sistema pode exigir verificação de compatibilidade de wheels. Não é necessária chave de LLM. O cache do encoder fica em `.cache/huggingface/` dentro deste diretório. Não compartilhar essa pasta nem o estado de sessões como parte de uma publicação de código.

## Verificar

```sh
.venv/bin/python tests/test_data_pipeline.py
.venv/bin/python tests/test_backend.py
pnpm --dir frontend test
pnpm --dir frontend run build
```

Com o servidor local ativo:

```sh
.venv/bin/python tests/test_integration.py
```

O teste integrado cria sessões de verificação, incluindo replay, entrada manual e feedback. Preserva essas sessões e os originais. A variável opcional `SUPPORT_BASE_URL` seleciona outro endereço local para a verificação.

## O que os dados permitem afirmar

DS1 tem 8.469 registros; DS2 tem 47.837. Seus IDs, taxonomias e espaços semânticos permanecem separados. DS1 tem CSAT/resolução em 2.769 registros fechados, mas não tem data de abertura. Os campos de resposta e resolução são timestamps e contêm inversões; **não é possível calcular TTR/FRT confiáveis** com esses arquivos. Ausências aparecem como indisponíveis.

O classificador IT foi avaliado em 7.176 registros separados do treino: acurácia 86,1% e Macro F1 0,860. Isso não é uma validação de operação de produção, de prioridade ou de português. Confidence, cosseno de similaridade e associação a cluster são medidas diferentes. Duplicata e incidente são candidatos à investigação, nunca conclusões automáticas.

O Graph representa embeddings, vizinhanças e agrupamentos exploratórios. Não representa a rede neural do classificador. Tickets sem cluster continuam pertencendo ao corpus e devem permanecer acessíveis. O replay usa conteúdo efetivamente presente nos arquivos, com ordem/chegadas simuladas e label persistente. Ele não mede tempo real de atendimento nem resolve tickets.

O Copilot recupera resoluções do DS1 e produz um rascunho extractivo para revisão. Essas resoluções são genéricas/templateadas e não constituem uma base de conhecimento validada. DS2 não contém resoluções; o produto não inventa ligação entre as fontes. Aceitar/editar/rejeitar registra feedback local, sem enviar mensagem ao cliente.

ROI representa cenários com premissas editáveis de esforço, adoção e custo. Tempo decorrido não é trabalho humano recuperado. Não há salário nem benefício realizado inferido dos CSVs.

## Estado e conservação

`runtime/` guarda sessões SQLite; Reset cria outra sessão preservando a anterior. Os CSVs, o README original e os assets G4 permanecem imutáveis. `.venv/`, `.cache/`, `runtime/`, artefatos derivados e build estão ignorados no Git. Os scripts e manifestos permitem reproduzir os derivados.

O ambiente usa um processo único. Para publicar, hospede o frontend estático na Vercel e o backend em um host Python com volume persistente; veja a instrução curta em [operação e deploy](docs/07-operacao-e-deploy.md). Integração com atendimento de produção, envio de respostas, múltiplos operadores, drift estatístico, autenticação/rate limiting e publicação pública exigem trabalho adicional. O [plano](docs/02-plano-de-implementacao.md) e a [auditoria final](docs/08-auditoria-final.md) mantêm checkpoints verificados e pendentes.
