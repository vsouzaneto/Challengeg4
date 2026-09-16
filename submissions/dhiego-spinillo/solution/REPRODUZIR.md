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
