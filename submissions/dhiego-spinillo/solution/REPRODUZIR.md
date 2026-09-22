# Reproduzir a auditoria

Execute a partir de `submissions/dhiego-spinillo/`. Requer Python 3 com biblioteca padrão, `curl` e acesso aos downloads públicos.

```bash
curl -L --fail 'https://www.kaggle.com/api/v1/datasets/download/suraj520/customer-support-ticket-dataset' -o /tmp/g4-support-dataset1.zip
curl -L --fail 'https://www.kaggle.com/api/v1/datasets/download/adisongoh/it-service-ticket-classification-dataset' -o /tmp/g4-support-dataset2.zip
python3 solution/auditar_datasets.py /tmp/g4-support-dataset1.zip /tmp/g4-support-dataset2.zip > /tmp/g4-auditoria-reproduzida.json
```

Comparar o resultado com `solution/reports/auditoria-datasets.json`. A data embutida no script identifica a auditoria de referência de 15/09/2026; não é um relógio da nova execução. Os endpoints podem mudar de versão: conferir `sha256_csv` antes de esperar números idênticos.

O script não imprime nomes, emails ou mensagens individuais. Não redistribuímos os CSVs neste pacote. Ele verifica os arquivos, não treina um modelo nem mede economia operacional.

## Exploração orientada às perguntas de CX

```bash
python3 solution/explorar_cx.py /tmp/g4-support-dataset1.zip /tmp/g4-support-dataset2.zip > /tmp/g4-exploracao-cx.json
```

Comparar com `solution/reports/exploracao-cx.json`. Este segundo script inclui uma amostra reprodutível de 20 resoluções para inspeção, sem nomes, emails ou descrições completas. Os rótulos de busca literal não são classificações de sentimento/urgência. A leitura interpretativa está em `solution/analise-preliminar-cx.md`.

## Universos utilizáveis por pergunta

```bash
python3 solution/auditar_coortes.py /tmp/g4-support-dataset1.zip /tmp/g4-support-dataset2.zip > /tmp/g4-coortes-qualidade.json
```

Comparar com `solution/reports/coortes-qualidade.json`. Executar mantendo `explorar_cx.py` no mesmo diretório do script, pois ele fornece o leitor de ZIPs. Não altera os arquivos de origem nem exporta dados pessoais; produz contagens de filtros independentes e comparações de sensibilidade. Interpretação em `solution/qualidade-por-pergunta.md`.

## Exemplos para compreensão e recap

```bash
python3 solution/inspecionar_contexto.py /tmp/g4-support-dataset1.zip /tmp/g4-support-dataset2.zip > /tmp/g4-contexto-e-recap.json
```

Comparar com `solution/reports/contexto-e-recap.json`. Mantém o leitor `explorar_cx.py` no mesmo diretório. Inclui textos de cinco exemplos selecionados das bases públicas, sem campos de nome/email de cliente. A seleção é intencional; não é benchmark. Não chama LLM nem implementa recap. Interpretação em `solution/contexto-e-recap.md`.

## Análise visual v1

```bash
python3 solution/renderizar_analise_visual.py
```

Abrir `solution/visual/index.html` no navegador. A geração incorpora os quatro relatórios versionados, o template e o logo local. Não baixa os datasets nem chama IA. Para refletir uma nova auditoria, revisar e atualizar primeiro os relatórios em `solution/reports/`. As interpretações e os recaps de exemplo estão no template e exigem revisão se os dados mudarem.

O HTML contém dados, estilos, scripts e logo; fontes remotas têm alternativas locais. Os links de evidência dependem da estrutura de arquivos do pacote. A página no GitHub exibe código: baixar o pacote e abrir o HTML, ou servir localmente com `python3 -m http.server 8765 --bind 127.0.0.1` e acessar `http://127.0.0.1:8765/solution/visual/index.html`.

## Verificar acesso ao Jev (opcional; uma chamada à API)

Configurar `TYPESAFE_API_KEY` no ambiente ou no `.env` local da submissão, ignorado pelo Git. Não incluir a chave em comandos versionados ou relatórios. Requer acesso à API TypeSafe; a chamada pode consumir créditos.

```bash
python3 solution/verificar_jev.py
```

O script usa a biblioteca padrão, preserva validação TLS e, se o Python não localizar certificados padrão, procura o bundle do sistema em `/etc/ssl/cert.pem`. Envia um texto sintético curto com três categorias, sem ler/enviar o D2. Cada execução bem-sucedida atualiza `solution/reports/jev-conexao.json` com data, entrada, modelo retornado, resultado, tokens e tempo total de uma chamada. Não há retentativa automática nem registro de cabeçalhos de autenticação. `jev-latest` é um alias mutável; o relatório registra a versão efetivamente retornada.

É uma verificação de conexão/formato. Não mede acurácia, calibração ou latência típica e não deve ser incluída como resultado de teste do dataset.


## Aplicativo e ficha de investigação

Setup e Docker estão no [README](../README.md). A ficha usa `solution/investigation.py`: não faz chamadas de rede, não consulta fontes externas e não chama LLM. `POST /api/plan` prepara orientação a partir de conferências declaradas; `POST /api/review` recalcula a regra e registra categoria, contexto e rascunho editado. A exportação omite original, trecho do relato e rascunho.

Os três casos de `reports/revisao-guiada.json` são uma seleção da avaliação de recap já executada, acompanhada das decisões do candidato. Servem ao desenvolvimento; reapresentá-los na interface não é nova avaliação independente. Os testes usam banco temporário e não chamam APIs pagas.

## Experimentos já executados

A comparação está documentada em [comparacao.md](comparacao.md), com scripts, artefatos e protocolo. A avaliação separada de recap está em [avaliacao-recap.md](avaliacao-recap.md). Relatórios e respostas arquivadas permitem examinar os resultados sem usar credenciais. Não apagar ou sobrescrever essas rodadas para reapresentar novos resultados como se fossem o mesmo experimento.

## Classificação integral, sem novo treino

Com as dependências do aplicativo instaladas e o D2 baixado como no início deste guia:

```bash
.venv/bin/python solution/classificar_base_completa.py /tmp/g4-support-dataset2.zip --output /tmp/g4-d2-integral
```

Comparar com [relatório integral](reports/full-population/report.md) e seus arquivos. O script verifica hashes do CSV/modelo, exclusividade e cobertura das partições e reprodução das 1.192 previsões históricas. Não chama API, não altera o modelo e não reescolhe o limiar. O CSV comprimido exporta somente linha, partição, rótulo, sugestão e score. Timestamp e tempo de inferência variam por execução. O número da linha começa em 1, excluindo o cabeçalho. Os 47.837 registros não são um novo teste: 45.790 participaram do treino.

## Oportunidades e cenários econômicos

`python solution/mapear_oportunidades.py data/dataset2.zip > solution/reports/oportunidades.json` reproduz as buscas integrais. Contagens de menções não são elegibilidade. Acesse `/resumo` para síntese e `/economia` para calcular hipóteses sem chamada a IA. `PYTHONPATH=solution pytest -q solution/tests` inclui limites e fórmulas financeiras.

## Três caminhos executáveis

Acesse `/fluxos`, escolha um dos sete cenários e processe. Com IA ligada, somente o texto é enviado ao OpenRouter; desligada, aparecem regras lexicais explicitamente. Os adaptadores consultam fixtures locais e não acessam clientes reais. O autosserviço permite solicitar, concluir no provedor simulado e reportar falha; respostas preparadas podem ser editadas/aprovadas; investigação permanece em aberto. Cada execução possui registros isolados no SQLite persistente. Não inserir senhas reais.

`python solution/avaliar_fluxos.py` executa sete chamadas de desenvolvimento com a chave configurada e grava `solution/reports/fluxos-desenvolvimento.json`. Não é benchmark independente; reexecutar consome API e substitui o relatório. `/valor` calcula contribuições por processo sem chamadas a IA.
