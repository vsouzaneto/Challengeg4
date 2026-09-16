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
