# Como executar

## Caminho mais rápido — zero instalação

**https://winnow-flame.vercel.app/dashboard/index.html**

Mesmo código deste repositório, com deploy automático a cada push — não é uma versão
desatualizada. Só um navegador com internet, nada pra instalar.

## Caminho rápido — rodar localmente sem instalar nada de Python

Os resultados já estão versionados em `output/*.json` — não precisa rodar a análise pra ver
o protótipo. Só precisa de Python instalado (vem por padrão em qualquer Mac/Linux; no Windows,
[python.org](https://www.python.org/downloads/) ou Microsoft Store) e uma internet ativa
(o navegador carrega React/react-dom/visx do esm.sh em tempo de execução).

```bash
cd submissions/cleiton/solution
python -m http.server 8000       # no Windows pode precisar ser "py" em vez de "python"
```

Depois abra **http://localhost:8000/dashboard/index.html** no navegador. Se a porta 8000
estiver ocupada, troque por outra (`python -m http.server 8080`, por exemplo) e ajuste a URL.
Sem instalação de pacote nenhum — `http.server` é biblioteca padrão do Python.

## Caminho completo — reproduzir a análise do zero

Requisitos: Python 3.10+.

```bash
# 1. Baixe os dois datasets do Kaggle (links no README do challenge) e coloque em ../../../datasets/:
#    datasets/customer_support_tickets.csv          (Customer Support Ticket Dataset)
#    datasets/it_ticket_classification.csv          (IT Service Ticket Classification Dataset)

python -m venv .venv
.venv/Scripts/activate   # ou source .venv/bin/activate no Linux/Mac
pip install -r requirements.txt

python 01_diagnostic.py        # -> output/diagnostic.json
python 02_train_classifier.py  # -> output/model_weights.json, output/classifier_metrics.json
python 03_roi_model.py         # -> output/roi_model.json (depende do passo anterior)
```

## Protótipo interativo

`dashboard/` é uma única página React (via esm.sh, sem build step) no mesmo tema visual do meu
portfólio — Manrope + DM Mono, dark, gráficos em visx. Ela junta o diagnóstico operacional e
o protótipo num só lugar, navegável pela barra lateral com scroll-spy: seções 00-04 são o
diagnóstico (gargalos, satisfação, desperdício em horas); seção 05 é **Winnow**, a central de
triagem ao vivo (classificador, detecção de duplicata, triagem de prioridade, ciclo completo
de atendimento); seção 06 é o ROI. Lê os cinco JSONs em `output/` (diagnóstico, métricas do
classificador, pesos do modelo, ROI e o experimento de embeddings rejeitado) e roda o
classificador **inteiramente no navegador**, sem backend — qualquer texto colado no Winnow é
classificado com os mesmos pesos exportados do scikit-learn.

Precisa ser servido por HTTP (não `file://`, por causa de CORS no `fetch()` dos JSONs) e o
navegador precisa de internet para carregar React/react-dom/visx do esm.sh em tempo de
execução — não há build step nem `node_modules`. Rode a partir de `solution/`:

```bash
python -m http.server 8000
# abra http://localhost:8000/dashboard/index.html
```

Testado de ponta a ponta com Playwright (Chromium headless): os dois gráficos visx desenham
barras reais, o simulador classifica ao vivo e não há nenhum erro no console.

Versão ao vivo, completa e sempre atualizada (deploy automático a cada push):
**https://winnow-flame.vercel.app/dashboard/index.html**

Também existe uma versão estática mais antiga, sem visx e sem o Winnow completo (detecção de
duplicata, triagem de prioridade, navegação lateral), publicada num Claude Artifact:
https://claude.ai/code/artifact/1b04cec8-cbc9-4a6e-939c-256236422aba

## Experimento opcional (não faz parte do pipeline principal)

`experiments/04_embeddings_experiment.py` testa se trocar TF-IDF por embeddings pré-treinados
(sentence-transformers) melhora a acurácia — resultado real: piora em toda métrica, ver seção
"Experimento rejeitado" no dashboard. Não precisa rodar isso para reproduzir a submissão; os
resultados já estão salvos em `output/embeddings_experiment.json`. Se quiser rodar de novo,
tem dependências pesadas à parte (torch + sentence-transformers, ~500MB de download) e leva
uns 20-30 minutos em CPU:

```bash
pip install -r experiments/requirements.txt
python experiments/04_embeddings_experiment.py
```
